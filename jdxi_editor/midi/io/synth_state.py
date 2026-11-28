"""
What the JD-Xi holds, kept apart from what the editor shows.

    confirmed (LCS)  bytes read back from the JD-Xi (its replies): the only
                     thing ever shown as verified
    pending          bytes the editor sent and has not read back yet
    different        bytes read back with another value than the one sent
                     (the JD-Xi did not take it, or it changed on the JD-Xi)

The working state (WS) is the editors' values; SynthMemory (device.memory)
stays what the editors show and send, including writes.

Also: per-part comparison of two readings, to tell what changed on the
JD-Xi while it was away.
"""

from __future__ import annotations

import threading
from typing import Iterable, Optional, Sequence

from jdxi_editor.midi.io.synth_memory import (
    DT1_COMMAND,
    ROLAND_ID,
    SYSEX_END,
    SYSEX_START,
    SynthMemory,
    address_to_linear,
    linear_to_address,
)

# The parts of a program, by the start of their temporary areas (address hex)
PARTS = (
    ("program", ("1800",)),  # Program Common, Vocal FX, effects, zones, arpeggio
    ("digital_1", ("1901",)),
    ("digital_2", ("1921",)),
    ("analog", ("1942",)),
    ("drums", ("1970",)),
)
PART_NAMES = {
    "program": "Program (common, effects, arpeggio)",
    "digital_1": "Digital 1",
    "digital_2": "Digital 2",
    "analog": "Analog",
    "drums": "Drums",
}


def part_of_address(address_hex: str) -> Optional[str]:
    address_hex = address_hex.upper()
    for part, prefixes in PARTS:
        if any(address_hex.startswith(p) for p in prefixes):
            return part
    return None


def _dt1_payload(message: Sequence[int]):
    """(linear start, values) of a DT1, or None."""
    data = [int(b) for b in message]
    if data and data[0] == SYSEX_START:
        data = data[1:]
    if data and data[-1] == SYSEX_END:
        data = data[:-1]
    if len(data) < 13 or data[0] != ROLAND_ID or data[6] != DT1_COMMAND:
        return None
    return address_to_linear(data[7:11]), data[11:-1]


class SynthState:
    """Confirmed, pending and different bytes of one JD-Xi."""

    def __init__(self) -> None:
        self.confirmed = SynthMemory()
        self._pending: dict[int, int] = {}  # linear address -> value sent
        self._different: dict[int, tuple[int, int]] = {}  # linear -> (sent, read)
        self._lock = threading.Lock()

    # ---------------------------------------------------------------- input
    def sent(self, message: Sequence[int]) -> None:
        """A DT1 that went out: pending until read back."""
        found = _dt1_payload(message)
        if found is None:
            return
        start, values = found
        with self._lock:
            for offset, value in enumerate(values):
                self._pending[start + offset] = int(value) & 0x7F
                self._different.pop(start + offset, None)

    def received(self, message: Sequence[int]) -> None:
        """A DT1 from the JD-Xi: confirmed; it settles what was pending there."""
        found = _dt1_payload(message)
        if found is None:
            return
        self.confirmed.record_dt1(message)
        start, values = found
        with self._lock:
            for offset, value in enumerate(values):
                linear = start + offset
                sent = self._pending.pop(linear, None)
                if sent is not None and sent != (int(value) & 0x7F):
                    self._different[linear] = (sent, int(value) & 0x7F)

    def program_changed(self, ranges: Optional[Sequence[tuple[int, int]]] = None) -> None:
        """A new program on the JD-Xi: nothing of the old one holds. With
        *ranges* (linear [start, end)), only a part changed: only those bytes."""
        if ranges is None:
            self.confirmed.clear()
            with self._lock:
                self._pending.clear()
                self._different.clear()
            return
        self.confirmed.forget(ranges)
        with self._lock:
            for table in (self._pending, self._different):
                for linear in [k for k in table if any(s <= k < e for s, e in ranges)]:
                    del table[linear]

    # -------------------------------------------------------------- queries
    def pending_count(self) -> int:
        with self._lock:
            return len(self._pending)

    def is_confirmed(self, address: Sequence[int], size: int = 1) -> bool:
        """Every byte read back and nothing sent since."""
        start = address_to_linear(address)
        if self.confirmed.read(address, size) is None:
            return False
        with self._lock:
            return not any(start + i in self._pending or start + i in self._different
                           for i in range(size))

    def different(self) -> dict:
        """address (hex) -> (sent, read) where the JD-Xi holds another value."""
        with self._lock:
            return {linear_to_address(k).hex(): v for k, v in self._different.items()}

    def snapshot(self) -> dict:
        """The confirmed sections: address (hex) -> bytes (a copy)."""
        found = {}
        for address, size in self.confirmed.sections():
            data = self.confirmed.read(address, size)
            if data is not None:
                found[bytes(address).hex()] = bytes(data)
        return found


def parts_that_differ(before: dict, after: dict, addresses: Optional[Iterable[str]] = None) -> list[str]:
    """The parts (PARTS order) whose sections differ between two snapshots.
    Only sections known in both count (a section never read says nothing)."""
    keys = set(addresses) if addresses is not None else set(before) & set(after)
    changed = set()
    for key in keys:
        if key in before and key in after and before[key] != after[key]:
            part = part_of_address(key)
            if part:
                changed.add(part)
    return [part for part, _p in PARTS if part in changed]


def state_of(helper) -> Optional[SynthState]:
    """The SynthState of *helper*'s JD-Xi (None without a device)."""
    try:
        from jdxi_editor.midi.io.device import device_for

        device = device_for(helper)
    except Exception:
        return None
    return getattr(device, "state", None)
