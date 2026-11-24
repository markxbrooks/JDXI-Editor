"""
Talks to a connected JD-Xi.

Run with ``python -m pytest -m hardware``. The default suite skips this
marker. Every test skips when either JD-Xi port is missing. The one write
is a temporary digital-common byte, and it is restored. No program change
is sent, and nothing is written to a user program or to pattern memory.
"""

from __future__ import annotations

import time

import mido
import pytest

from jdxi_editor.midi.io.request_queue import Sysex
from picomidi.message.type import MidoMessageType, MidoMetaMessageType


pytestmark = pytest.mark.hardware

# A name character in the temporary digital common block (the name is the
# first 12 bytes). Temporary tone memory, not a user program slot.
_NAME_INDEX = 2
_REPLY_WAIT_S = 3.0


def _address_and_size(request: str) -> tuple[bytes, int]:
    """4-byte address and byte count of an RQ1."""
    from jdxi_editor.midi.io.request_queue import RQ1_COMMAND, SYSEX_START
    from jdxi_editor.midi.io.synth_memory import address_to_linear

    data = list(bytes.fromhex(request))
    if data and data[0] == Sysex.START:
        data = data[1:]
    assert len(data) >= 15 and data[6] == RQ1_COMMAND
    address = bytes(data[7:11])
    size = address_to_linear(data[11:15])
    assert size > 0
    return address, size


def _address_hex(address: bytes) -> str:
    return "".join(f"{byte:02x}" for byte in address)


def _dt1_payloads(messages, address_hex: str):
    """Payloads of DT1 replies at *address_hex* (``19010000`` form)."""
    from jdxi_editor.midi.io.request_queue import DT1_COMMAND, SYSEX_START, roland_address

    found = []
    for message in messages:
        if getattr(message, "type", None) != "sysex":
            continue
        data = list(message.bytes())
        if data and data[0] == Sysex.START:
            data = data[1:]
        if data and data[-1] == Sysex.END:
            data = data[:-1]
        if roland_address(data, DT1_COMMAND) != address_hex:
            continue
        if len(data) < 13:
            continue
        found.append(bytes(data[11:-1]))
    return found


def _read_area(link, request: str) -> tuple[bytes, bytes]:
    """
    Send one RQ1 and return ``(address, block)`` once a DT1 at that address
    is in memory.
    """
    address, _size = _address_and_size(request)
    start = len(link.messages)
    link.helper.device.request([request])
    assert link.helper.device.requests.wait_idle(_REPLY_WAIT_S)
    replies = _dt1_payloads(link.messages[start:], _address_hex(address))
    assert replies, f"no DT1 reply at {address.hex(' ')}"
    # The instrument answers with the block it has. Program common is shorter
    # than the 64 bytes the RQ1 asks for; memory holds the bytes that arrived.
    payload = max(replies, key=len)
    block = link.helper.device.memory.read(address, len(payload))
    assert block == payload and len(block) > 0
    return address, block


def _all_notes_off(helper) -> None:
    if not helper.midi_out.is_port_open():
        return
    for channel in range(16):
        helper.midi_out.send_message([0xB0 | channel, 123, 0])


@pytest.fixture(scope="session")
def jdxi():
    """Open the JD-Xi input and output for the module; silence on the way out."""
    from PySide6.QtWidgets import QApplication

    from jdxi_editor.midi.io.helper import MidiIOHelper

    QApplication.instance() or QApplication([])
    helper = MidiIOHelper()
    in_port, out_port = helper.find_jdxi_ports()
    if not in_port or not out_port:
        pytest.skip("JD-Xi MIDI input or output is not present")
    assert helper.set_midi_ports(in_port, out_port), (
        f"could not open {in_port!r} and {out_port!r}"
    )
    messages: list = []
    original = helper._handle_midi_message

    def _capture(message):
        messages.append(message)
        original(message)

    helper._handle_midi_message = _capture
    link = type("JDXiLink", (), {})()
    link.helper = helper
    link.messages = messages
    try:
        yield link
    finally:
        _all_notes_off(helper)
        helper.close_ports()


def test_identity(jdxi):
    """Universal identity request; the reply parses as a Roland identity."""
    from jdxi_editor.midi.message.identity_request.message import IdentityRequestMessage
    from jdxi_editor.midi.sysex.parser.sysex import JDXiSysExParser

    start = len(jdxi.messages)
    jdxi.helper.send_raw_message(IdentityRequestMessage().to_message_list())
    deadline = time.monotonic() + 1.5
    parsed = None
    while time.monotonic() < deadline and parsed is None:
        for message in jdxi.messages[start:]:
            if getattr(message, "type", None) != "sysex":
                continue
            raw = bytes(message.bytes())
            try:
                candidate = JDXiSysExParser().parse_to_ir(raw)
            except ValueError:
                continue
            if candidate.message_type == "identity_reply" and candidate.roland_id == 0x41:
                parsed = candidate
                break
        if parsed is None:
            time.sleep(0.05)
    assert parsed is not None
    assert len(parsed.raw) >= 14


def test_program_common(jdxi):
    from jdxi_editor.midi.sysex.request.midi_requests import MidiRequests

    _read_area(jdxi, MidiRequests.PROGRAM_COMMON)


def test_digital_analog_drums(jdxi):
    from jdxi_editor.midi.sysex.request.midi_requests import MidiRequests

    _read_area(jdxi, MidiRequests.DIGITAL1_COMMON)
    _read_area(jdxi, MidiRequests.ANALOG)
    _read_area(jdxi, MidiRequests.DRUMS)


def test_effects(jdxi):
    from jdxi_editor.midi.sysex.request.midi_requests import MidiRequests

    _read_area(jdxi, MidiRequests.PROGRAM_EFFECT1)
    _read_area(jdxi, MidiRequests.PROGRAM_DELAY)


def test_arpeggiator(jdxi):
    from jdxi_editor.midi.sysex.request.midi_requests import MidiRequests

    _read_area(jdxi, MidiRequests.PROGRAM_CONTROLLER)


def test_digital_byte_is_restored(jdxi):
    """
    Move one temporary digital-common byte by one step, read it back, then
    put the original byte back. No program change.
    """
    from jdxi_editor.midi.io.synth_memory import (
        address_to_linear,
        build_dt1,
        linear_to_address,
    )
    from jdxi_editor.midi.sysex.request.midi_requests import MidiRequests

    address, block = _read_area(jdxi, MidiRequests.DIGITAL1_COMMON)
    original = block[_NAME_INDEX]
    changed = (original + 1) & 0x7F
    byte_address = linear_to_address(address_to_linear(address) + _NAME_INDEX)

    def _write(value: int) -> None:
        jdxi.helper.send_raw_message(list(build_dt1(byte_address, [value])))
        time.sleep(0.05)

    def _confirm(expected: int) -> None:
        start = len(jdxi.messages)
        jdxi.helper.device.request([MidiRequests.DIGITAL1_COMMON])
        assert jdxi.helper.device.requests.wait_idle(_REPLY_WAIT_S)
        replies = _dt1_payloads(jdxi.messages[start:], _address_hex(address))
        assert replies, "no DT1 after the temporary write"
        assert any(
            len(payload) > _NAME_INDEX and payload[_NAME_INDEX] == expected
            for payload in replies
        )

    _write(changed)
    try:
        _confirm(changed)
    finally:
        _write(original)
        _confirm(original)


def _one_bar() -> mido.MidiFile:
    """Four digital notes and one drum note, one bar at 120 bpm."""
    from jdxi_editor.midi.channel.channel import MidiChannel

    midi_file = mido.MidiFile(ticks_per_beat=480)
    track = mido.MidiTrack()
    midi_file.tracks.append(track)
    track.append(mido.MetaMessage(MidoMessageType.SET_TEMPO, tempo=500_000, time=0))
    track.append(
        mido.MetaMessage(MidoMetaMessageType.TIME_SIGNATURE, numerator=4, denominator=4, time=0)
    )
    digital = int(MidiChannel.DIGITAL_SYNTH_1)
    drums = int(MidiChannel.DRUM_KIT)
    notes = (60, 64, 67, 72)
    for index, note in enumerate(notes):
        if index == 0:
            track.append(
                mido.Message(
                    MidoMessageType.NOTE_ON,
                    channel=drums,
                    note=36,
                    velocity=100,
                    time=0,
                )
            )
        track.append(
            mido.Message(
                MidoMessageType.NOTE_ON,
                channel=digital,
                note=note,
                velocity=90,
                time=0,
            )
        )
        track.append(
            mido.Message(
                MidoMessageType.NOTE_OFF,
                channel=digital,
                note=note,
                velocity=0,
                time=480,
            )
        )
        if index == 0:
            track.append(
                mido.Message(
                    MidoMessageType.NOTE_OFF,
                    channel=drums,
                    note=36,
                    velocity=0,
                    time=0,
                )
            )
    return midi_file


def test_playback_one_bar(jdxi):
    """Play one bar to the open output, then stop. Pattern memory is untouched."""
    from jdxi_editor.midi.playback.transport import TransportController

    def send(message: mido.Message) -> None:
        jdxi.helper.midi_out.send_message(list(message.bytes()))

    transport = TransportController(send=send)
    transport.load(_one_bar())
    assert transport.play()
    try:
        time.sleep(transport.duration_seconds + 0.25)
    finally:
        transport.stop()
        transport.panic()


def test_recording_one_block(jdxi):
    """Capture one block from an input whose name contains JD-Xi."""
    del jdxi  # MIDI is enough for the other tests; this one needs audio
    from jdxi_editor.audio.audio_buffer import SampleRing
    from jdxi_editor.audio.audio_source import InputDeviceSource

    if not InputDeviceSource.available():
        pytest.skip("sounddevice is not installed")
    match = next(
        (
            (name, index)
            for name, index in InputDeviceSource.input_devices()
            if "jd-xi" in name.casefold()
        ),
        None,
    )
    if match is None:
        pytest.skip("no audio input whose name contains JD-Xi")
    _name, index = match
    ring = SampleRing(capacity=48000)
    source = InputDeviceSource(ring)
    source.start(index)
    try:
        deadline = time.monotonic() + 1.0
        while time.monotonic() < deadline and ring.written() < source.block:
            time.sleep(0.02)
        assert ring.written() > 0
    finally:
        source.stop()
