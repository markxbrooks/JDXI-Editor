#!/usr/bin/env python3
"""
Unit tests for PlaybackEngine (midi_player/playback/engine.py).

Lock tempo, ScheduledEvent behavior, and on_event timing without GUI.
"""

import sys
import os

from picomidi import MidiTempo

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mido import MidiFile, MidiTrack, Message, MetaMessage
from unittest.mock import patch

import pytest


def _make_simple_midi():
    """One track: set_tempo 120 BPM, note_on 60 at 0, note_off 60 at 480, note_on 62 at 480, note_off 62 at 720."""
    mid = MidiFile(type=1, ticks_per_beat=480)
    track = MidiTrack()
    mid.tracks.append(track)
    track.append(MetaMessage("set_tempo", tempo=500000, time=0))  # 120 BPM
    track.append(Message("note_on", note=60, velocity=64, channel=0, time=0))
    track.append(Message("note_off", note=60, velocity=0, channel=0, time=480))
    track.append(Message("note_on", note=62, velocity=64, channel=0, time=0))
    track.append(Message("note_off", note=62, velocity=0, channel=0, time=240))
    return mid


def test_engine_load_file_builds_events_and_tempo():
    """load_file() builds event list and tempo map; reset() is applied."""
    from picomidi.playback.engine import PlaybackEngine

    mid = _make_simple_midi()
    engine = PlaybackEngine()
    engine.load_file(mid)

    assert engine.midi_file is mid
    assert engine.ticks_per_beat == 480
    assert 0 in engine._tempo_map
    assert engine._tempo_map[0] == MidiTempo.BPM_120_USEC
    # 4 note events (no set_tempo in event list)
    assert len(engine.events) == 4
    assert engine.event_index == 0
    assert engine._is_playing is False


def test_engine_start_sets_position_and_playing():
    """start(0) sets event index and playing flag."""
    from picomidi.playback.engine import PlaybackEngine

    mid = _make_simple_midi()
    engine = PlaybackEngine()
    engine.load_file(mid)

    with patch("jdxi_editor.ui.editors.midi_player.playback.engine.time") as mock_time:
        mock_time.time.return_value = 1000.0
        engine.start(0)

    assert engine.start_tick == 0
    assert engine._start_time == 1000.0
    assert engine._is_playing is True
    assert engine.event_index == 0


def test_engine_process_until_now_calls_on_event_at_correct_times():
    """process_until_now() invokes on_event for due events only; timing is segment-wise."""
    from picomidi.playback.engine import PlaybackEngine

    mid = _make_simple_midi()
    engine = PlaybackEngine()
    engine.load_file(mid)
    received = []

    def capture(msg):
        received.append(msg)

    engine.on_event = capture

    # Start at t=1000.0
    with patch("jdxi_editor.ui.editors.midi_player.playback.engine.time") as mock_time:
        mock_time.time.return_value = 1000.0
        engine.start(0)

    # At t=1000.25 (elapsed 0.25s): only note_on 60 (tick 0) is due. Tick 480 = 0.5s.
    with patch("jdxi_editor.ui.editors.midi_player.playback.engine.time") as mock_time:
        mock_time.time.return_value = 1000.25
        engine.process_until_now()

    assert len(received) == 1
    assert received[0].type == "note_on"
    assert received[0].note == 60

    # At t=1000.6 (elapsed 0.6s): note_on 60, note_off 60, note_on 62 are due (ticks 0, 480, 480).
    with patch("jdxi_editor.ui.editors.midi_player.playback.engine.time") as mock_time:
        mock_time.time.return_value = 1000.6
        engine.process_until_now()

    assert len(received) == 3
    assert received[1].type == "note_off"
    assert received[1].note == 60
    assert received[2].type == "note_on"
    assert received[2].note == 62

    # At t=1001.0 (elapsed 1.0s): note_off 62 (tick 720 = 0.75s) is due; then playback ends.
    with patch("jdxi_editor.ui.editors.midi_player.playback.engine.time") as mock_time:
        mock_time.time.return_value = 1001.0
        engine.process_until_now()

    assert len(received) == 4
    assert received[3].type == "note_off"
    assert received[3].note == 62
    assert engine._is_playing is False


def test_engine_stop_clears_playing():
    """stop() sets _is_playing False; position is unchanged."""
    from picomidi.playback.engine import PlaybackEngine

    mid = _make_simple_midi()
    engine = PlaybackEngine()
    engine.load_file(mid)
    with patch("jdxi_editor.ui.editors.midi_player.playback.engine.time") as mock_time:
        mock_time.time.return_value = 1000.0
        engine.start(0)
    assert engine._is_playing is True
    engine.stop()
    assert engine._is_playing is False
    assert engine.event_index == 0


def test_engine_mute_track_filters_events():
    """Events from a muted track are not sent via on_event."""
    from picomidi.playback.engine import PlaybackEngine

    mid = _make_simple_midi()
    engine = PlaybackEngine()
    engine.load_file(mid)
    engine.mute_track(0, True)
    received = []
    engine.on_event = received.append

    with patch("jdxi_editor.ui.editors.midi_player.playback.engine.time") as mock_time:
        mock_time.time.side_effect = [1000.0, 1001.0]
        engine.start(0)
        engine.process_until_now()

    assert len(received) == 0
    assert engine._is_playing is False


def test_engine_mute_channel_filters_events():
    """Events on a muted channel are not sent."""
    from picomidi.playback.engine import PlaybackEngine

    mid = _make_simple_midi()
    engine = PlaybackEngine()
    engine.load_file(mid)
    engine.mute_channel(0, True)
    received = []
    engine.on_event = received.append

    with patch("jdxi_editor.ui.editors.midi_player.playback.engine.time") as mock_time:
        mock_time.time.side_effect = [1000.0, 1001.0]
        engine.start(0)
        engine.process_until_now()

    assert len(received) == 0


def test_engine_scrub_to_tick_repositions():
    """scrub_to_tick() updates event index and start position."""
    from picomidi.playback.engine import PlaybackEngine

    mid = _make_simple_midi()
    engine = PlaybackEngine()
    engine.load_file(mid)

    engine.scrub_to_tick(480)
    assert engine.event_index >= 1
    assert engine.start_tick == 480


def test_engine_reset_clears_position_not_mute():
    """reset() clears position and playing; mute/suppress are unchanged."""
    from picomidi.playback.engine import PlaybackEngine

    mid = _make_simple_midi()
    engine = PlaybackEngine()
    engine.load_file(mid)
    engine.mute_track(0, True)
    engine.reset()

    assert engine.event_index == 0
    assert engine.start_tick == 0
    assert engine._is_playing is False
    assert 0 in engine._muted_tracks


def test_engine_tick_to_seconds_segment_wise():
    """_tick_to_seconds uses segment-wise tempo (variable tempo)."""
    from picomidi.playback.engine import PlaybackEngine

    # Two tempos: 500000 (120 BPM) for 0–480, then 250000 (240 BPM) for 480+
    mid = MidiFile(type=1, ticks_per_beat=480)
    track = MidiTrack()
    mid.tracks.append(track)
    track.append(MetaMessage(MidoMetaMessageType.SET_TEMPO.value, tempo=500000, time=0))
    track.append(MetaMessage(MidoMetaMessageType.SET_TEMPO.value, tempo=250000, time=480))
    track.append(Message("note_on", note=60, velocity=64, channel=0, time=0))
    track.append(Message("note_off", note=60, velocity=0, channel=0, time=960))

    engine = PlaybackEngine()
    engine.load_file(mid)

    # 0–480 at 120 BPM: 480 ticks = 1 beat = 0.5s
    t480 = engine._tick_to_seconds(480)
    assert abs(t480 - 0.5) < 1e-6
    # 0–960: 0.5s + 480 ticks at 240 BPM = 0.5 + 0.25 = 0.75s
    t960 = engine._tick_to_seconds(960)
    assert abs(t960 - 0.75) < 1e-6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
