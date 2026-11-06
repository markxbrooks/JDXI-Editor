#!/usr/bin/env python3
"""
Unit tests for PlaybackEngine (picomidi.playback.engine).

Lock tempo, ScheduledEvent behavior, transport (pause/resume/stop/seek),
held-note release and on_event timing without GUI.
"""

import os
import sys
from unittest.mock import patch

import pytest
from mido import Message, MetaMessage, MidiFile, MidiTrack

from picomidi import MidiTempo
from picomidi.message.type import MidoMetaMessageType
from picomidi.playback.engine import PlaybackEngine, TransportState

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class FakeClock:
    """Settable replacement for PlaybackEngine._now."""

    def __init__(self, now: float = 1000.0):
        self.now = now

    def __call__(self) -> float:
        return self.now


@pytest.fixture
def clock():
    fake = FakeClock()
    with patch.object(PlaybackEngine, "_now", staticmethod(fake)):
        yield fake


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


def _make_two_tempo_midi():
    """120 BPM for ticks 0–480, then 240 BPM; one note from 480 to 1440."""
    mid = MidiFile(type=1, ticks_per_beat=480)
    track = MidiTrack()
    mid.tracks.append(track)
    track.append(MetaMessage(MidoMetaMessageType.SET_TEMPO.value, tempo=500000, time=0))
    track.append(MetaMessage(MidoMetaMessageType.SET_TEMPO.value, tempo=250000, time=480))
    track.append(Message("note_on", note=60, velocity=64, channel=0, time=0))
    track.append(Message("note_off", note=60, velocity=0, channel=0, time=960))
    return mid


def _loaded_engine(mid=None):
    engine = PlaybackEngine()
    engine.load_file(mid or _make_simple_midi())
    received = []
    engine.on_event = received.append
    return engine, received


def test_engine_load_file_builds_events_and_tempo():
    """load_file() builds event list and tempo map; reset() is applied."""
    engine, _ = _loaded_engine()

    assert engine.ticks_per_beat == 480
    assert 0 in engine._tempo_map
    assert engine._tempo_map[0] == MidiTempo.BPM_120_USEC
    # 4 note events (no set_tempo in event list)
    assert len(engine.events) == 4
    assert engine.event_index == 0
    assert engine.length_ticks == 720
    assert abs(engine.duration_seconds - 0.75) < 1e-6
    assert engine._is_playing is False


def test_engine_start_sets_position_and_playing(clock):
    """start(0) sets event index and playing flag."""
    engine, _ = _loaded_engine()
    engine.start(0)

    assert engine.start_tick == 0
    assert engine._start_time == 1000.0
    assert engine._is_playing is True
    assert engine.event_index == 0


def test_engine_process_until_now_calls_on_event_at_correct_times(clock):
    """process_until_now() invokes on_event for due events only; timing is segment-wise."""
    engine, received = _loaded_engine()
    engine.start(0)

    # Elapsed 0.25s: only note_on 60 (tick 0) is due. Tick 480 = 0.5s.
    clock.now = 1000.25
    assert engine.process_until_now() is False
    assert [(m.type, m.note) for m in received] == [("note_on", 60)]

    # Elapsed 0.6s: note_off 60 and note_on 62 (tick 480) are due too.
    clock.now = 1000.6
    engine.process_until_now()
    assert [(m.type, m.note) for m in received[1:]] == [
        ("note_off", 60),
        ("note_on", 62),
    ]

    # Elapsed 1.0s: note_off 62 (tick 720 = 0.75s) is due; then playback ends.
    clock.now = 1001.0
    assert engine.process_until_now() is True
    assert (received[3].type, received[3].note) == ("note_off", 62)
    assert engine._is_playing is False
    assert engine.state == TransportState.STOPPED


def test_engine_reports_end_only_once(clock):
    """process_until_now() returns True only on the call that reaches the end."""
    engine, _ = _loaded_engine()
    engine.start(0)
    clock.now = 1001.0
    assert engine.process_until_now() is True
    clock.now = 1002.0
    assert engine.process_until_now() is False
    assert engine.position_seconds == pytest.approx(0.75)
    assert engine.start_tick == engine.length_ticks


def test_engine_stop_clears_playing_and_keeps_position(clock):
    """stop() sets _is_playing False; position is unchanged."""
    engine, _ = _loaded_engine()
    engine.start(0)
    clock.now = 1000.25
    engine.process_until_now()
    engine.stop()

    assert engine._is_playing is False
    assert engine.position_seconds == pytest.approx(0.25)
    assert engine.start_tick == 240


def test_engine_stop_releases_sounding_notes(clock):
    """Notes sounding when stopped get a note_off."""
    engine, received = _loaded_engine()
    engine.start(0)
    clock.now = 1000.25
    engine.process_until_now()  # note_on 60
    engine.stop()

    assert (received[-1].type, received[-1].note) == ("note_off", 60)
    assert engine._held_notes == {}


def test_engine_pause_resume_does_not_burst(clock):
    """Time spent paused does not count: no burst of events on resume."""
    engine, received = _loaded_engine()
    engine.start(0)
    clock.now = 1000.25
    engine.process_until_now()  # note_on 60
    engine.pause()
    assert engine.state == TransportState.PAUSED
    assert (received[-1].type, received[-1].note) == ("note_off", 60)  # released
    sent_before_resume = len(received)

    clock.now = 1010.0  # paused for ~10 s
    engine.process_until_now()
    assert len(received) == sent_before_resume  # nothing sent while paused
    assert engine.position_seconds == pytest.approx(0.25)

    engine.resume()
    engine.process_until_now()
    assert len(received) == sent_before_resume  # still at 0.25 s, nothing due
    clock.now = 1010.3  # position 0.55 s
    engine.process_until_now()
    assert [(m.type, m.note) for m in received[sent_before_resume:]] == [
        ("note_off", 60),
        ("note_on", 62),
    ]


def test_engine_seek_keeps_state(clock):
    """seek_tick() repositions without starting or stopping playback."""
    engine, received = _loaded_engine()
    engine.seek_tick(480)
    assert engine.state == TransportState.STOPPED
    assert engine.position_seconds == pytest.approx(0.5)

    engine.start(engine.start_tick)
    engine.process_until_now()
    # Events before tick 480 are skipped
    assert [(m.type, m.note) for m in received] == [("note_off", 60), ("note_on", 62)]

    clock.now = 1000.1
    engine.seek_seconds(0.0)
    assert engine.state == TransportState.PLAYING
    assert engine.position_seconds == pytest.approx(0.0)
    assert (received[-1].type, received[-1].note) == ("note_off", 62)  # released


def test_engine_scrub_to_tick_repositions():
    """scrub_to_tick() updates event index and start position."""
    engine, _ = _loaded_engine()
    engine.scrub_to_tick(480)
    assert engine.event_index >= 1
    assert engine.start_tick == 480


def test_engine_mute_track_filters_events(clock):
    """Events from a muted track are not sent via on_event."""
    engine, received = _loaded_engine()
    engine.mute_track(0, True)
    engine.start(0)
    clock.now = 1001.0
    engine.process_until_now()

    assert received == []
    assert engine._is_playing is False


def test_engine_mute_channel_filters_events(clock):
    """Events on a muted channel are not sent."""
    engine, received = _loaded_engine()
    engine.mute_channel(0, True)
    engine.start(0)
    clock.now = 1001.0
    engine.process_until_now()

    assert received == []


def test_engine_mute_during_playback_releases_notes(clock):
    """Muting a channel mid-note sends note_off so the note does not hang."""
    engine, received = _loaded_engine()
    engine.start(0)
    engine.process_until_now()  # note_on 60
    engine.mute_channel(0, True)
    assert (received[-1].type, received[-1].note) == ("note_off", 60)


def test_engine_release_sustain(clock):
    """A sustain pedal left down is released on stop."""
    mid = _make_simple_midi()
    mid.tracks[0].insert(1, Message("control_change", control=64, value=127, time=0))
    engine, received = _loaded_engine(mid)
    engine.start(0)
    engine.process_until_now()
    engine.stop()
    assert any(
        m.type == "control_change" and m.control == 64 and m.value == 0
        for m in received
    )


def _make_two_track_unison_midi():
    """Tracks 0 and 1 both play note 60 on channel 0 from tick 0 to 480."""
    mid = MidiFile(type=1, ticks_per_beat=480)
    for _ in range(2):
        track = MidiTrack()
        track.append(Message("note_on", note=60, velocity=64, channel=0, time=0))
        track.append(Message("note_off", note=60, velocity=0, channel=0, time=480))
        mid.tracks.append(track)
    return mid


def test_engine_unmute_during_playback_restores_controllers(clock):
    """Unmuting sends the program, CCs and bend the muted track skipped."""
    engine, received = _loaded_engine(_make_patch_change_midi())
    engine.mute_track(0, True)
    engine.start(0)
    clock.now = 1000.75  # tick 720: past the bend, before program 7
    engine.process_until_now()
    assert received == []

    engine.mute_track(0, False)
    assert _summary(received) == [
        ("cc", 0, 95),
        ("cc", 32, 64),
        ("pc", 3),
        ("cc", 7, 90),
        ("bend", 2000),
    ]


def test_engine_unmute_while_paused_restores_on_resume(clock):
    engine, received = _loaded_engine(_make_patch_change_midi())
    engine.mute_channel(0, True)
    engine.start(0)
    clock.now = 1000.75
    engine.process_until_now()
    engine.pause()
    engine.mute_channel(0, False)
    assert received == []
    engine.resume()
    assert ("pc", 3) in _summary(received)


def test_engine_mute_call_that_changes_nothing_sends_nothing(clock):
    """The UI re-sends every mute flag on each toggle; repeats are ignored."""
    engine, received = _loaded_engine(_make_patch_change_midi())
    engine.start(0)
    engine.process_until_now()
    received.clear()
    engine.mute_channel(0, False)
    engine.mute_track(0, False)
    assert received == []


def test_engine_mute_track_keeps_other_tracks_unison_note(clock):
    """Muting one of two tracks playing the same note leaves the other's held."""
    engine, received = _loaded_engine(_make_two_track_unison_midi())
    engine.start(0)
    engine.process_until_now()
    received.clear()
    engine.mute_track(1, True)
    assert _summary(received) == [("note_off",)]
    assert engine._held_notes == {(0, 60): {0}}
    engine.stop()
    assert engine._held_notes == {}


def test_engine_track_velocity_scale(clock):
    """Note-on velocities are scaled per track; the file is unchanged."""
    engine, received = _loaded_engine(_make_two_track_unison_midi())
    engine.set_track_velocity_scale(0, 0.5)
    engine.set_track_velocity_scale(1, 3.0)
    engine.start(0)
    engine.process_until_now()
    assert sorted(m.velocity for m in received if m.type == "note_on") == [32, 127]
    assert engine.midi_file.tracks[0][0].velocity == 64


def test_engine_velocity_scale_keeps_notes_audible_and_note_offs(clock):
    engine, received = _loaded_engine()
    engine.set_track_velocity_scale(0, 0.0)
    engine.start(0)
    clock.now = 1001.0
    engine.process_until_now()
    assert [m.velocity for m in received if m.type == "note_on"] == [1, 1]
    assert [m.velocity for m in received if m.type == "note_off"] == [0, 0]

    engine.set_track_velocity_scale(0, 1.0)
    assert engine._velocity_scales == {}


def test_engine_reset_clears_position_not_mute():
    """reset() clears position and playing; mute/suppress are unchanged."""
    engine, _ = _loaded_engine()
    engine.mute_track(0, True)
    engine.reset()

    assert engine.event_index == 0
    assert engine.start_tick == 0
    assert engine._is_playing is False
    assert 0 in engine._muted_tracks


def test_engine_tick_to_seconds_segment_wise():
    """_tick_to_seconds uses segment-wise tempo (variable tempo)."""
    engine, _ = _loaded_engine(_make_two_tempo_midi())

    # 0–480 at 120 BPM: 480 ticks = 1 beat = 0.5s
    assert engine._tick_to_seconds(480) == pytest.approx(0.5)
    # 0–960: 0.5s + 480 ticks at 240 BPM = 0.5 + 0.25 = 0.75s
    assert engine._tick_to_seconds(960) == pytest.approx(0.75)


def test_engine_seconds_to_tick_inverts_tempo_map():
    """seconds_to_tick is the inverse of tick_to_seconds across tempo changes."""
    engine, _ = _loaded_engine(_make_two_tempo_midi())

    for tick in (0, 240, 480, 720, 1440):
        assert engine.seconds_to_tick(engine.tick_to_seconds(tick)) == pytest.approx(
            tick, abs=1
        )
    assert engine.tempo_at_tick(0) == 500000
    assert engine.tempo_at_tick(960) == 250000


def test_engine_start_mid_file_uses_absolute_time(clock):
    """Starting after a tempo change schedules events with the right tempo."""
    engine, received = _loaded_engine(_make_two_tempo_midi())
    engine.start(480)  # 0.5 s into the file; note_off at 1440 is 1.0 s
    clock.now = 1000.45
    engine.process_until_now()
    assert [m.type for m in received] == ["note_on"]
    clock.now = 1000.55
    engine.process_until_now()
    assert [m.type for m in received] == ["note_on", "note_off"]



def _make_patch_change_midi():
    """Bank+PC at tick 0, volume at 0, a new PC at tick 960, bend at 480; notes throughout."""
    mid = MidiFile(type=1, ticks_per_beat=480)
    track = MidiTrack()
    mid.tracks.append(track)
    track.append(MetaMessage("set_tempo", tempo=500000, time=0))
    track.append(Message("control_change", control=0, value=95, channel=0, time=0))
    track.append(Message("control_change", control=32, value=64, channel=0, time=0))
    track.append(Message("program_change", program=3, channel=0, time=0))
    track.append(Message("control_change", control=7, value=90, channel=0, time=0))
    track.append(Message("note_on", note=60, velocity=64, channel=0, time=0))
    track.append(Message("pitchwheel", pitch=2000, channel=0, time=480))
    track.append(Message("note_off", note=60, velocity=0, channel=0, time=0))
    track.append(Message("program_change", program=7, channel=0, time=480))
    track.append(Message("note_on", note=62, velocity=64, channel=0, time=0))
    track.append(Message("note_off", note=62, velocity=0, channel=0, time=960))
    return mid


def _summary(messages):
    out = []
    for m in messages:
        if m.type == "program_change":
            out.append(("pc", m.program))
        elif m.type == "control_change":
            out.append(("cc", m.control, m.value))
        elif m.type == "pitchwheel":
            out.append(("bend", m.pitch))
        else:
            out.append((m.type,))
    return out


def test_engine_start_mid_file_restores_controllers(clock):
    """Starting after a patch change sends bank, program, CC and bend first."""
    engine, received = _loaded_engine(_make_patch_change_midi())
    engine.start(1200)
    assert _summary(received) == [
        ("cc", 0, 95),
        ("cc", 32, 64),
        ("pc", 7),
        ("cc", 7, 90),
        ("bend", 2000),
    ]


def test_engine_chase_respects_suppression_and_mute(clock):
    """Chased values pass the same mute/suppress filter as playback."""
    engine, received = _loaded_engine(_make_patch_change_midi())
    engine.suppress_control_changes = True
    engine.start(1200)
    assert _summary(received) == [("pc", 7), ("bend", 2000)]

    engine, received = _loaded_engine(_make_patch_change_midi())
    engine.mute_channel(0, True)
    engine.start(1200)
    assert received == []


def test_engine_seek_sends_only_changed_controllers(clock):
    """Seeking within the same patch does not resend the program change."""
    engine, received = _loaded_engine(_make_patch_change_midi())
    engine.start(0)
    engine.process_until_now()  # bank, pc 3, volume, note_on 60
    received.clear()
    engine.seek_tick(240)  # still patch 3, no bend yet
    assert _summary(received) == [("note_off",)]  # held note released only

    received.clear()
    engine.seek_tick(1200)  # past pc 7 and the bend
    assert ("pc", 7) in _summary(received)
    assert ("bend", 2000) in _summary(received)

    received.clear()
    engine.seek_tick(0)  # back before the bend: bend is reset to centre
    assert ("bend", 0) in _summary(received)


def test_engine_seek_while_paused_chases_on_resume(clock):
    """A seek made while paused restores controllers when playback resumes."""
    engine, received = _loaded_engine(_make_patch_change_midi())
    engine.start(0)
    engine.process_until_now()
    engine.pause()
    engine.seek_tick(1200)
    received.clear()
    engine.resume()
    assert ("pc", 7) in _summary(received)


def test_engine_whole_file_loop(clock):
    """With looping on, the end wraps to the start instead of finishing."""
    engine, received = _loaded_engine()
    engine.set_loop(True)
    engine.start(0)
    clock.now = 1000.8  # past the 0.75 s end
    assert engine.process_until_now() is False
    assert engine.state == TransportState.PLAYING
    # Wrapped with 0.05 s overshoot; the tick-0 note_on played again
    assert engine.position_seconds == pytest.approx(0.05, abs=1e-6)
    assert [(m.type, m.note) for m in received if m.type.startswith("note")][-1] == (
        "note_on",
        60,
    )


def test_engine_ab_loop(clock):
    """An A–B loop repeats only the range and skips events at B."""
    engine, received = _loaded_engine()
    engine.set_loop(True, (0, 480))  # first beat only
    engine.start(0)
    clock.now = 1000.55
    engine.process_until_now()
    notes = [(m.type, m.note) for m in received]
    # note_on 60 (t=0); wrap at 0.5 s releases 60 and replays the start; note_on 62 at B never plays
    assert ("note_on", 62) not in notes
    assert notes.count(("note_on", 60)) == 2
    assert engine.position_seconds == pytest.approx(0.05, abs=1e-6)


def test_engine_loop_ignored_when_started_after_end(clock):
    """Starting beyond the A–B range plays on to the end of the file."""
    engine, _ = _loaded_engine()
    engine.set_loop(True, (0, 240))
    engine.start(480)
    clock.now = 1001.0
    assert engine.process_until_now() is True


def test_engine_speed_scales_time(clock):
    """At half speed, file time advances at half the wall-clock rate."""
    engine, received = _loaded_engine()
    engine.set_speed(0.5)
    engine.start(0)
    clock.now = 1000.6  # 0.3 s of file time
    engine.process_until_now()
    assert [(m.type, m.note) for m in received] == [("note_on", 60)]
    assert engine.position_seconds == pytest.approx(0.3)

    engine.set_speed(1.0)  # re-anchors without jumping
    assert engine.position_seconds == pytest.approx(0.3)
    clock.now = 1000.85
    assert engine.position_seconds == pytest.approx(0.55)


def test_engine_midi_clock(clock):
    """Clock out: Start, 24 clocks per beat, Stop at the end."""
    engine, received = _loaded_engine()
    engine.set_send_clock(True)
    engine.start(0)
    clock.now = 1000.5  # one beat at 120 BPM (clock at 0.5 s itself is due too)
    engine.process_until_now()
    types = [m.type for m in received]
    assert types[0] == "start"
    assert types.count("clock") == 25
    clock.now = 1001.0
    engine.process_until_now()
    assert received[-1].type == "stop"


def test_engine_midi_clock_song_position_on_seek(clock):
    """Seeking while playing sends Stop, Song Position Pointer, Continue."""
    engine, received = _loaded_engine()
    engine.set_send_clock(True)
    engine.start(0)
    received.clear()
    engine.seek_tick(480)  # one beat = 4 sixteenths
    clock_msgs = [m for m in received if m.type in ("stop", "songpos", "continue")]
    assert [m.type for m in clock_msgs] == ["stop", "songpos", "continue"]
    assert clock_msgs[1].pos == 4


def test_engine_bar_beat_follows_time_signature():
    """Bar/beat numbering follows time-signature changes."""
    mid = MidiFile(type=1, ticks_per_beat=480)
    track = MidiTrack()
    mid.tracks.append(track)
    track.append(MetaMessage("time_signature", numerator=3, denominator=4, time=0))
    # Two bars of 3/4 (2880 ticks), then 6/8
    track.append(MetaMessage("time_signature", numerator=6, denominator=8, time=2880))
    track.append(Message("note_on", note=60, velocity=64, time=0))
    track.append(Message("note_off", note=60, velocity=0, time=2880))
    engine, _ = _loaded_engine(mid)

    assert engine.bar_beat_at_tick(0) == (1, 1)
    assert engine.bar_beat_at_tick(480) == (1, 2)
    assert engine.bar_beat_at_tick(1440) == (2, 1)
    assert engine.bar_beat_at_tick(2880) == (3, 1)  # 6/8 starts at bar 3
    assert engine.bar_beat_at_tick(2880 + 240) == (3, 2)  # eighth-note beats
    assert engine.bar_beat_at_tick(2880 + 1440) == (4, 1)
    assert engine.time_signature_at_tick(3000) == (6, 8)
    assert engine.nearest_bar_tick(1300) == 1440
    assert engine.nearest_bar_tick(200) == 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
