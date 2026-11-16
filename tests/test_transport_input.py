"""Unit tests for MiniLab CC and VMX-8 note transport bindings."""

from __future__ import annotations

import os

import mido
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402

from jdxi_editor.midi.playback.transport_input import (  # noqa: E402
    DEFAULT_TRANSPORT_BINDINGS,
    MINILAB3_TRANSPORT_BINDINGS,
    VMX8_TRANSPORT_BINDINGS,
    MidiCCBinding,
    MidiNoteBinding,
    TransportAction,
    TransportInputMapper,
)


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


def _note(note: int, velocity: int = 127, channel: int = 0, off: bool = False):
    if off or velocity == 0:
        return mido.Message("note_off", note=note, velocity=0, channel=channel)
    return mido.Message("note_on", note=note, velocity=velocity, channel=channel)


def _cc(control: int, value: int, channel: int = 0):
    return mido.Message(
        "control_change", control=control, value=value, channel=channel
    )


def test_minilab_play_pause_stop_ccs(qapp):
    calls = []
    mapper = TransportInputMapper(
        on_play=lambda: calls.append("play"),
        on_pause=lambda: calls.append("pause"),
        on_stop=lambda: calls.append("stop"),
        bindings=MINILAB3_TRANSPORT_BINDINGS,
    )
    mapper.handle_message(_cc(107, 127))
    mapper.handle_message(_cc(107, 0))
    mapper.handle_message(_cc(108, 127))
    mapper.handle_message(_cc(108, 0))
    mapper.handle_message(_cc(106, 127))
    mapper.handle_message(_cc(106, 0))
    assert calls == ["play", "pause", "stop"]


def test_vmx8_play_and_pause_notes(qapp):
    calls = []
    mapper = TransportInputMapper(
        on_play=lambda: calls.append("play"),
        on_pause=lambda: calls.append("pause"),
        bindings=VMX8_TRANSPORT_BINDINGS,
    )
    mapper.handle_message(_note(94))
    mapper.handle_message(_note(93))
    assert calls == ["play", "pause"]


def test_play_release_does_nothing(qapp):
    calls = []
    mapper = TransportInputMapper(
        on_play=lambda: calls.append("play"),
        bindings=VMX8_TRANSPORT_BINDINGS,
    )
    mapper.handle_message(_note(94))
    mapper.handle_message(_note(94, off=True))
    mapper.handle_message(_note(94, velocity=0))
    assert calls == ["play"]


def test_unmapped_and_wrong_channel_ignored(qapp):
    calls = []
    mapper = TransportInputMapper(
        on_play=lambda: calls.append("play"),
        bindings=DEFAULT_TRANSPORT_BINDINGS,
    )
    mapper.handle_message(_note(60))
    mapper.handle_message(_note(94, channel=1))
    mapper.handle_message(_cc(107, 127, channel=1))
    mapper.handle_message(_cc(7, 64))
    assert calls == []


def test_bindings_can_remap_cc(qapp):
    calls = []
    mapper = TransportInputMapper(
        on_pause=lambda: calls.append("pause"),
        bindings=(MidiCCBinding(TransportAction.PAUSE, 0, 20),),
    )
    mapper.handle_message(_cc(108, 127))  # MiniLab pause, not bound
    mapper.handle_message(_cc(20, 127))
    assert calls == ["pause"]


def test_bindings_can_remap_note(qapp):
    calls = []
    mapper = TransportInputMapper(
        on_pause=lambda: calls.append("pause"),
        bindings=(MidiNoteBinding(TransportAction.PAUSE, 0, 60),),
    )
    mapper.handle_message(_note(94))
    mapper.handle_message(_note(60))
    assert calls == ["pause"]


def test_rewind_hold_seeks_backward_until_release(qapp):
    position = [10.0]
    seeks = []

    def seek(seconds: float) -> None:
        position[0] = seconds
        seeks.append(seconds)

    mapper = TransportInputMapper(
        seek_seconds=seek,
        get_position=lambda: position[0],
        get_duration=lambda: 30.0,
        seek_rate=4.0,
        seek_tick_ms=50,
        bindings=VMX8_TRANSPORT_BINDINGS,
    )
    mapper.handle_message(_note(91))
    assert seeks, "first tick should seek immediately"
    assert seeks[0] < 10.0

    before = len(seeks)
    mapper._on_seek_tick()
    assert len(seeks) == before + 1
    assert seeks[-1] < seeks[0]

    mapper.handle_message(_note(91, off=True))
    after_release = len(seeks)
    mapper._on_seek_tick()
    assert len(seeks) == after_release


def test_fast_forward_hold_seeks_forward(qapp):
    position = [1.0]
    seeks = []

    def seek(seconds: float) -> None:
        position[0] = seconds
        seeks.append(seconds)

    mapper = TransportInputMapper(
        seek_seconds=seek,
        get_position=lambda: position[0],
        get_duration=lambda: 30.0,
        seek_rate=4.0,
        seek_tick_ms=50,
        bindings=VMX8_TRANSPORT_BINDINGS,
    )
    mapper.handle_message(_note(92))
    assert seeks[0] > 1.0
    mapper.handle_message(_note(92, off=True))


def test_seek_clamped_to_duration(qapp):
    seeks = []
    mapper = TransportInputMapper(
        seek_seconds=seeks.append,
        get_position=lambda: 29.9,
        get_duration=lambda: 30.0,
        seek_rate=40.0,
        seek_tick_ms=50,
        bindings=VMX8_TRANSPORT_BINDINGS,
    )
    mapper.handle_message(_note(92))
    assert seeks[-1] == 30.0
    mapper.stop_hold()

    seeks.clear()
    mapper = TransportInputMapper(
        seek_seconds=seeks.append,
        get_position=lambda: 0.1,
        get_duration=lambda: 30.0,
        seek_rate=40.0,
        seek_tick_ms=50,
        bindings=VMX8_TRANSPORT_BINDINGS,
    )
    mapper.handle_message(_note(91))
    assert seeks[-1] == 0.0
    mapper.stop_hold()


def test_record_press_invokes_handler(qapp):
    calls = []
    mapper = TransportInputMapper(
        on_record=lambda: calls.append("record"),
        bindings=VMX8_TRANSPORT_BINDINGS,
    )
    mapper.handle_message(_note(95))
    mapper.handle_message(_note(95, off=True))
    assert calls == ["record"]


def test_default_includes_minilab_and_vmx8():
    minilab = {b.action: b for b in MINILAB3_TRANSPORT_BINDINGS}
    assert minilab[TransportAction.PLAY].control == 107
    assert minilab[TransportAction.STOP].control == 106
    assert minilab[TransportAction.PAUSE].control == 108

    notes = {
        b.action: b.note for b in VMX8_TRANSPORT_BINDINGS if isinstance(b, MidiNoteBinding)
    }
    assert notes == {
        TransportAction.PLAY: 94,
        TransportAction.PAUSE: 93,
        TransportAction.RECORD: 95,
        TransportAction.REWIND: 91,
        TransportAction.FAST_FORWARD: 92,
    }

    assert set(DEFAULT_TRANSPORT_BINDINGS) == set(
        (*MINILAB3_TRANSPORT_BINDINGS, *VMX8_TRANSPORT_BINDINGS)
    )


def test_vmx8_cc_mode_transport(qapp):
    """In CC mode the VMX-8 buttons send CC 52-56 on channel 1: 127 press, 0 release."""
    calls = []
    position = [10.0]
    mapper = TransportInputMapper(
        on_play=lambda: calls.append("play"),
        on_pause=lambda: calls.append("pause"),
        on_record=lambda: calls.append("record"),
        seek_seconds=lambda s: (calls.append(("seek", s)), position.__setitem__(0, s)),
        get_position=lambda: position[0],
        get_duration=lambda: 30.0,
        bindings=VMX8_TRANSPORT_BINDINGS,
    )
    for control in (52, 53, 54):  # B0 34/35/36 7F then 00
        mapper.handle_message(_cc(control, 127))
        mapper.handle_message(_cc(control, 0))
    assert calls == ["play", "pause", "record"]

    calls.clear()
    mapper.handle_message(_cc(55, 127))  # rewind: seeks back while held
    mapper.handle_message(_cc(55, 0))
    mapper.handle_message(_cc(56, 127))  # fast forward
    mapper.handle_message(_cc(56, 0))
    seeks = [c[1] for c in calls]
    assert seeks[0] < 10.0 and seeks[1] > seeks[0]
    mapper._on_seek_tick()  # released: no more seeking
    assert len(calls) == 2


def test_vmx8_transport_ccs_do_not_clash_with_its_knobs():
    from jdxi_editor.midi.io.controller_map import VMX8_FILTER_MAP

    ccs = {b.control for b in VMX8_TRANSPORT_BINDINGS if isinstance(b, MidiCCBinding)}
    assert ccs == {52, 53, 54, 55, 56}
    assert not ccs & set(VMX8_FILTER_MAP)
