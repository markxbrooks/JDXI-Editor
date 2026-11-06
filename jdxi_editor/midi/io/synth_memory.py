"""
jdxi_editor.midi.io.synth_memory
What the editor knows of the JD-Xi's parameter memory, byte by byte.

Every DT1 (data set) that passes through the MIDI helper is recorded: replies
from the JD-Xi and the parameter changes the editor sends. A patch can then
be saved as the synth's own bytes, i.e. raw MIDI values, rather than from the
editor's controls, whose display units (ms, fractions, ±63) differ per widget
and lose precision.

Roland addresses and sizes are 7-bit per byte; they are kept as linear
offsets so a section can cross a byte boundary (Effect 1 is 145 bytes from
18 00 02 00, ending at 18 00 03 10).

Example:
    >>> memory = SynthMemory()
    >>> memory.record_dt1(bytes.fromhex("F0 41 10 00 00 00 0E 12 19 42 00 00 01 02 22 F7"))
    True
    >>> memory.read(bytes.fromhex("19 42 00 00"), 2)
    b'\\x01\\x02'
    >>> memory.read(bytes.fromhex("19 42 00 00"), 3) is None   # third byte unknown
    True
"""

from __future__ import annotations

import threading
from typing import Optional, Sequence

from jdxi_editor.midi.io.request_queue import DT1_COMMAND, ROLAND_ID, SYSEX_START

JDXI_DT1_HEADER = bytes([0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, DT1_COMMAND])
SYSEX_END = 0xF7


def address_to_linear(address: Sequence[int]) -> int:
    """4 bytes of 7 bits -> linear offset."""
    value = 0
    for byte in address:
        value = (value << 7) | (int(byte) & 0x7F)
    return value


def linear_to_address(value: int) -> bytes:
    """Linear offset -> 4 bytes of 7 bits."""
    return bytes((value >> shift) & 0x7F for shift in (21, 14, 7, 0))


def roland_checksum(data: Sequence[int]) -> int:
    return (128 - sum(data) % 128) % 128


def build_dt1(address: Sequence[int], data: Sequence[int]) -> bytes:
    """A JD-Xi DT1 message writing *data* at *address*."""
    body = bytes(address) + bytes(data)
    return JDXI_DT1_HEADER + body + bytes([roland_checksum(body), SYSEX_END])


class SynthMemory:
    """Thread-safe byte map of the JD-Xi's memory, filled from DT1 messages."""

    # A DT1 with at least this many data bytes is a section dump (a reply or a
    # loaded patch); its start and length mark a section. Parameter changes
    # are 1-4 bytes.
    SECTION_MIN_BYTES = 8

    def __init__(self) -> None:
        self._bytes: dict[int, int] = {}
        self._sections: dict[int, int] = {}  # linear start -> size in bytes
        self._lock = threading.Lock()

    def record_dt1(self, message: Sequence[int]) -> bool:
        """
        Record a DT1 message (with or without F0/F7); returns False if it is not one.

        Layout without F0: 41, device, model×4, 12, address×4, data…, checksum[, F7]
        """
        data = list(message)
        if data and data[0] == SYSEX_START:
            data = data[1:]
        if data and data[-1] == SYSEX_END:
            data = data[:-1]
        if len(data) < 13 or data[0] != ROLAND_ID or data[6] != DT1_COMMAND:
            return False
        start = address_to_linear(data[7:11])
        values = data[11:-1]  # drop the checksum
        with self._lock:
            for offset, value in enumerate(values):
                self._bytes[start + offset] = int(value) & 0x7F
            if len(values) >= self.SECTION_MIN_BYTES:
                self._sections[start] = max(self._sections.get(start, 0), len(values))
        return True

    def sections(self) -> list[tuple[bytes, int]]:
        """(address, size) of every section seen as a whole, in address order."""
        with self._lock:
            return [
                (linear_to_address(start), size)
                for start, size in sorted(self._sections.items())
            ]

    def read(self, address: Sequence[int], size: int) -> Optional[bytes]:
        """The *size* bytes from *address*, or None if any of them is unknown."""
        start = address_to_linear(address)
        with self._lock:
            try:
                return bytes(self._bytes[start + i] for i in range(size))
            except KeyError:
                return None

    def section_dt1(self, address: Sequence[int], size: int) -> Optional[bytes]:
        """The section as one DT1 message, as the JD-Xi would send it, or None."""
        data = self.read(address, size)
        return None if data is None else build_dt1(address, data)

    def clear(self) -> None:
        with self._lock:
            self._bytes.clear()
            self._sections.clear()
