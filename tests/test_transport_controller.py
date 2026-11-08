#!/usr/bin/env python3
"""
Tests for TransportController (jdxi_editor.midi.playback.transport).

Runs the real scheduler thread against a short file and checks the
transport contract: state signals, end-of-song handling, pause/seek.
"""

import os
import time

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from mido import Message, MetaMessage, MidiFile, MidiTrack
from PySide6.QtWidgets import QApplication

from jdxi_editor.midi.playback.transport import TransportController
from picomidi.playback.engine import TransportState


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def _short_midi(note_ticks: int = 240) -> MidiFile:
    """120 BPM, one note of *note_ticks* (240 ticks = 0.25 s)."""
    mid = MidiFile(type=1, ticks_per_beat=480)
    track = MidiTrack()
    mid.tracks.append(track)
    track.append(MetaMessage("set_tempo", tempo=500000, time=0))
    track.append(Message("note_on", note=60, velocity=100, channel=0, time=0))
    track.append(Message("note_off", note=60, velocity=0, channel=0, time=note_ticks))
    return mid


def _wait_until(app, condition, timeout: float = 3.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        app.processEvents()
        if condition():
            return True
        time.sleep(0.005)
    return False


@pytest.fixture
def transport(app):
    sent = []
    controller = TransportController(send=sent.append)
    controller.sent = sent
    states = []
    controller.state_changed.connect(states.append)
    controller.states = states
    finished = []
    controller.finished.connect(lambda: finished.append(True))
    controller.finished_calls = finished
    yield controller
    controller.shutdown()


def test_play_without_file_does_nothing(transport):
    assert transport.play() is False
    assert transport.state == TransportState.STOPPED
    assert transport.states == []


def test_end_of_song_returns_to_stopped_once(app, transport):
    transport.load(_short_midi())
    transport.play()
    assert transport.states == [TransportState.PLAYING]

    assert _wait_until(app, lambda: transport.finished_calls)
    # Let any further (incorrect) end notifications arrive
    _wait_until(app, lambda: False, timeout=0.2)

    assert transport.finished_calls == [True]
    assert transport.states == [TransportState.PLAYING, TransportState.STOPPED]
    assert transport.position_seconds == 0.0  # rewound
    assert [m.type for m in transport.sent] == ["note_on", "note_off"]


def test_play_after_end_starts_from_top(app, transport):
    transport.load(_short_midi())
    transport.play()
    assert _wait_until(app, lambda: transport.finished_calls)
    transport.play()
    assert transport.state == TransportState.PLAYING
    assert _wait_until(app, lambda: len(transport.finished_calls) == 2)


def test_pause_and_resume_keep_position(app, transport):
    transport.load(_short_midi(note_ticks=4800))  # 5 s
    transport.play()
    _wait_until(app, lambda: transport.position_seconds > 0.1)
    transport.pause()
    paused_at = transport.position_seconds
    assert transport.state == TransportState.PAUSED
    assert transport.sent[-1].type == "note_off"  # held note released

    _wait_until(app, lambda: False, timeout=0.2)
    assert transport.position_seconds == paused_at

    transport.toggle_play_pause()
    assert transport.state == TransportState.PLAYING
    assert transport.position_seconds == pytest.approx(paused_at, abs=0.05)
    assert transport.states == [
        TransportState.PLAYING,
        TransportState.PAUSED,
        TransportState.PLAYING,
    ]


def test_seek_while_stopped_does_not_play(app, transport):
    transport.load(_short_midi(note_ticks=4800))
    positions = []
    transport.position_changed.connect(positions.append)
    transport.seek_seconds(2.0)

    assert transport.state == TransportState.STOPPED
    assert transport.position_seconds == pytest.approx(2.0, abs=0.01)
    assert positions and positions[-1] == pytest.approx(2.0, abs=0.01)

    transport.play()
    assert transport.position_seconds == pytest.approx(2.0, abs=0.05)


def test_stop_rewinds_and_silences(app, transport):
    transport.load(_short_midi(note_ticks=4800))
    transport.play()
    _wait_until(app, lambda: transport.sent)
    transport.stop()

    assert transport.state == TransportState.STOPPED
    assert transport.position_seconds == 0.0
    assert transport.finished_calls == []  # stop is not end-of-song
    note_offs = [m for m in transport.sent if m.type == "note_off"]
    assert note_offs and note_offs[0].note == 60
    all_notes_off = [
        m for m in transport.sent if m.type == "control_change" and m.control == 123
    ]
    assert len(all_notes_off) == 16


def test_reload_keeps_position_and_state(app, transport):
    midi = _short_midi(note_ticks=4800)
    transport.load(midi)
    transport.play()
    _wait_until(app, lambda: transport.position_seconds > 0.1)
    transport.pause()
    paused_at = transport.position_seconds

    transport.load(midi, keep_position=True)
    assert transport.state == TransportState.PAUSED
    assert transport.position_seconds == pytest.approx(paused_at, abs=0.01)


def test_mute_applies_during_playback(app, transport):
    transport.load(_short_midi(note_ticks=4800))
    transport.play()
    _wait_until(app, lambda: transport.sent)
    transport.set_mutes(muted_tracks=set(), muted_channels={0})
    assert transport.sent[-1].type == "note_off"


def test_loop_whole_song_never_finishes(app, transport):
    transport.load(_short_midi())  # 0.25 s
    changes = []
    transport.loop_changed.connect(lambda: changes.append(True))
    transport.set_loop(True)
    assert changes and transport.loop_enabled
    transport.play()
    _wait_until(app, lambda: False, timeout=0.7)
    assert transport.state == TransportState.PLAYING
    assert transport.finished_calls == []
    assert [m.type for m in transport.sent].count("note_on") >= 2


def test_ab_range_kept_across_reload_and_cleared_on_new_file(app, transport):
    midi = _short_midi(note_ticks=4800)
    transport.load(midi)
    transport.set_loop(True, 1.0, 2.0)
    assert transport.loop_range_seconds == pytest.approx((1.0, 2.0), abs=0.01)
    transport.load(midi, keep_position=True)
    assert transport.loop_range_seconds == pytest.approx((1.0, 2.0), abs=0.01)
    transport.load(_short_midi())
    assert transport.loop_range_seconds is None


def test_speed_slows_position(app, transport):
    transport.load(_short_midi(note_ticks=4800))
    transport.set_speed(0.5)
    transport.play()
    start = time.monotonic()
    _wait_until(app, lambda: False, timeout=0.4)
    elapsed = time.monotonic() - start
    assert transport.position_seconds == pytest.approx(elapsed * 0.5, abs=0.06)
