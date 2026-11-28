"""
JDXiDevice: the request queue, memory mirror and echo guard of one JD-Xi.

- the MIDI helper reports traffic to its device (replies, writes, program changes)
- echoes of received data are dropped, other messages are sent
- devices are independent: each has its own queue and memory
"""

import os
import sys

sys.path.insert(0, os.path.abspath("."))

from unittest.mock import Mock

import mido
from PySide6.QtWidgets import QApplication

_APP = QApplication.instance() or QApplication([])

from jdxi_editor.midi.io.device import JDXiDevice, device_for
from jdxi_editor.midi.io.echo_guard import EchoGuard
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.io.synth_memory import build_dt1

_ADDRESS = bytes.fromhex("19420000")
_REPLY = build_dt1(_ADDRESS, list(range(10)))  # a section reply (>= 8 bytes)
_WRITE = build_dt1(bytes.fromhex("19420003"), [0x55])


def _device():
    sent = []
    return JDXiDevice(sent.append, echo_guard=EchoGuard()), sent


def test_reply_is_recorded_and_program_change_clears():
    device, _ = _device()
    device.received(_REPLY[1:-1])  # mido sysex data: no F0/F7
    assert device.memory.sections() == [(_ADDRESS, 10)]
    device.received([0xCF, 0x10])
    assert device.memory.sections() == []


def test_a_tone_change_forgets_only_its_part():
    """
    A program change on a part's channel replaces that part's tone only;
    channel 16 is the whole program; other channels change nothing.
    """
    device, _ = _device()
    digital_1 = bytes.fromhex("19010000")
    program_part_analog = bytes.fromhex("18002200")
    for address in (_ADDRESS, digital_1, program_part_analog):
        device.received(build_dt1(address, list(range(10))))
    device.received([0xC0, 0x05])  # Digital 1 (channel 1)
    assert device.memory.read(digital_1, 10) is None
    assert device.memory.read(_ADDRESS, 10) is not None
    device.received([0xC2, 0x05])  # Analog: its tone and its Program Part entry
    assert device.memory.read(_ADDRESS, 10) is None
    assert device.memory.read(program_part_analog, 10) is None
    device.received(build_dt1(digital_1, list(range(10))))
    device.received([0xC5, 0x01])  # channel 6: not a JD-Xi part
    assert device.memory.read(digital_1, 10) is not None
    device.sent([0xCF, 0x01])  # the program (channel 16): everything
    assert device.memory.sections() == []


def test_a_write_the_port_refuses_is_not_held():
    """A write recorded as sent but refused by the port is forgotten, and the window is told."""
    helper = MidiIOHelper()
    helper.device.memory.clear()
    helper.device.received(_REPLY)
    saved_out = helper.midi_out
    helper.midi_out = Mock()
    helper.midi_out.is_port_open = Mock(return_value=True)
    helper.midi_out.send_message.side_effect = OSError("device unplugged")
    told = []
    helper.midi_send_failed.connect(told.append)
    try:
        assert helper.send_raw_message(list(_WRITE)) is False
        assert helper.device.memory.read(bytes.fromhex("19420003"), 1) is None
        assert helper.device.memory.read(_ADDRESS, 3) == bytes([0, 1, 2])
        assert told and "unplugged" in told[0]
    finally:
        helper.midi_send_failed.disconnect(told.append)
        helper.midi_out = saved_out
        helper.device.memory.clear()


def test_sent_write_updates_memory():
    device, _ = _device()
    device.received(_REPLY)
    device.sent(list(_WRITE))
    assert device.memory.read(_ADDRESS, 4) == bytes([0, 1, 2, 0x55])


def test_echo_dropped_only_inside_scope():
    device, _ = _device()
    assert device.before_send(_WRITE)
    with device.applying_device_data():
        assert not device.before_send(_WRITE)
        assert device.before_send([0xB0, 7, 100])  # not a DT1
    assert device.before_send(_WRITE)


def test_devices_are_independent():
    first, _ = _device()
    second, _ = _device()
    first.received(_REPLY)
    assert second.memory.sections() == []
    assert first.requests is not second.requests
    with first.applying_device_data():
        assert second.before_send(_WRITE)


def test_request_goes_through_queue():
    device, sent = _device()
    assert device.request([_WRITE]) == 1
    assert device.requests.wait_idle(2.0)
    assert [bytes(m) for m in sent] == [_WRITE]


def test_helper_reports_traffic_to_its_device():
    helper = MidiIOHelper()
    helper.device.memory.clear()
    saved_out = helper.midi_out
    helper.midi_out = Mock()
    helper.midi_out.is_port_open = Mock(return_value=True)
    try:
        helper._handle_midi_message(mido.Message("sysex", data=_REPLY[1:-1]))
        assert helper.device.memory.sections() == [(_ADDRESS, 10)]
        helper.send_raw_message(list(_WRITE))
        assert helper.device.memory.read(bytes.fromhex("19420003"), 1) == b"\x55"
        with helper.device.applying_device_data():
            helper.midi_out.send_message.reset_mock()
            helper.send_raw_message(list(_WRITE))
            helper.midi_out.send_message.assert_not_called()  # echo dropped
        helper._handle_midi_message(mido.Message("program_change", channel=15, program=3))
        assert helper.device.memory.sections() == []
        assert device_for(helper) is helper.device
    finally:
        helper.midi_out = saved_out
        helper.device.memory.clear()
