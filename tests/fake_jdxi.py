"""
A simulated JD-Xi on the other end of a MidiIOHelper: it answers the Identity
Request as a Roland JD-Xi, keeps what DT1s write and answers RQ1s from it.
"""

from __future__ import annotations

import threading
from unittest.mock import Mock

import mido
from PySide6.QtCore import QObject, Signal

from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.io.synth_memory import build_dt1

IDENTITY_REPLY = (0x7E, 0x10, 0x06, 0x02, 0x41, 0x0E, 0x03, 0x00, 0x00, 0x00, 0x03, 0x00, 0x00)


class FakeJDXi(QObject):
    """The JD-Xi on the other end of a MidiIOHelper."""

    reply = Signal(object)

    def __init__(self, helper: MidiIOHelper):
        super().__init__()
        self.helper = helper
        self.memory: dict[int, int] = {}  # 4-byte address (as a number) -> byte
        self.writes: list[bytes] = []
        self.silent = False
        self.refuse_sends = False
        self._lock = threading.Lock()
        self.reply.connect(
            lambda data: helper._handle_midi_message(mido.Message("sysex", data=data))
        )
        for name in ("midi_out", "midi_in"):
            port = Mock()
            port.is_port_open.return_value = True
            setattr(helper, name, port)
        helper.send_raw_message = self.send
        helper.send_midi_message = lambda message: self.send(
            list(message.to_message_list())
        )

    @staticmethod
    def _number(address) -> int:
        a = list(address)
        return a[0] << 21 | a[1] << 14 | a[2] << 7 | a[3]

    def load(self, messages) -> None:
        for message in messages:
            self._write(bytes(message))

    def _write(self, data: bytes) -> None:
        start = self._number(data[8:12])
        with self._lock:
            for i, byte in enumerate(data[12:-2]):
                self.memory[start + i] = byte

    def read(self, address, size: int) -> bytes:
        start = self._number(address)
        with self._lock:
            return bytes(self.memory.get(start + i, 0) for i in range(size))

    def send(self, message) -> bool:
        data = bytes(int(b) for b in message)
        if self.refuse_sends:
            return False
        if data[:1] == b"\xf0" and data[1:2] == b"\x7e" and data[3:5] == b"\x06\x01":
            # Identity Request: a Roland JD-Xi answers (as the real one does)
            self.reply.emit(list(IDENTITY_REPLY))
            return True
        if data[:7] != bytes([0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E]):
            return True
        if data[7] == 0x12:
            self.writes.append(data)
            self._write(data)
        elif data[7] == 0x11 and not self.silent:
            size = self._number(data[12:16])
            reply = build_dt1(list(data[8:12]), self.read(data[8:12], size))
            self.reply.emit(list(bytes(reply)[1:-1]))  # queued to the main thread
        return True
