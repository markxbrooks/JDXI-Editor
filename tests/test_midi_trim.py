#!/usr/bin/env python3
"""
Trimming a MIDI file (keep a range, moved to the start) or one track (remove
its notes outside a range, timing unchanged), and the player's Trim commands.
"""

import os
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import mido
from mido import Message, MetaMessage, MidiFile, MidiTrack
from PySide6.QtWidgets import QApplication, QDialog

from jdxi_editor.midi.file.trim import trim_midi_file, trim_track
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.dialogs.trim import TrimDialog
from jdxi_editor.ui.editors.midi_player.editor import MidiFilePlayer

TPB = 480
BAR = TPB * 4  # 4/4; 2 s at 120 BPM


def _abs(track) -> list[tuple[int, mido.Message]]:
    tick, events = 0, []
    for msg in track:
        tick += msg.time
        events.append((tick, msg))
    return events


def _notes(track) -> list[tuple[int, str, int]]:
    """(tick, on/off, note) for the track's notes."""
    found = []
    for tick, msg in _abs(track):
        if msg.type == "note_on" and msg.velocity > 0:
            found.append((tick, "on", msg.note))
        elif msg.type in ("note_off", "note_on"):
            found.append((tick, "off", msg.note))
    return found


def _end(track) -> int:
    """Length of *track* in ticks."""
    return _abs(track)[-1][0]


def _song() -> MidiFile:
    """
    4 bars at 120 BPM. Lead (ch1): bank+program at 0, a note per bar, tempo
    change to 100 BPM at bar 2, CC7 at bar 2. Bass (ch3): one note held from
    bar 1 to the end, then one in bar 4.
    """
    mid = MidiFile(type=1, ticks_per_beat=TPB)
    lead = MidiTrack()
    lead.append(MetaMessage("track_name", name="Lead", time=0))
    lead.append(MetaMessage("set_tempo", tempo=500000, time=0))
    lead.append(MetaMessage("time_signature", numerator=4, denominator=4, time=0))
    lead.append(Message("control_change", control=0, value=95, channel=0, time=0))
    lead.append(Message("control_change", control=32, value=64, channel=0, time=0))
    lead.append(Message("program_change", program=5, channel=0, time=0))
    for bar in range(4):
        if bar == 1:
            lead.append(MetaMessage("set_tempo", tempo=600000, time=0))
            lead.append(Message("control_change", control=7, value=80, channel=0, time=0))
        lead.append(Message("note_on", note=60 + bar, velocity=90, channel=0, time=0))
        lead.append(Message("note_off", note=60 + bar, velocity=0, channel=0, time=BAR))
    lead.append(MetaMessage("marker", text="old", time=0))
    mid.tracks.append(lead)

    bass = MidiTrack()
    bass.append(MetaMessage("track_name", name="Bass", time=0))
    bass.append(Message("note_on", note=36, velocity=90, channel=2, time=0))
    bass.append(Message("note_off", note=36, velocity=0, channel=2, time=BAR * 3))
    bass.append(Message("note_on", note=40, velocity=90, channel=2, time=0))
    bass.append(Message("note_off", note=40, velocity=0, channel=2, time=BAR))
    mid.tracks.append(bass)
    return mid


# --- trim_midi_file ---------------------------------------------------------


def test_file_trim_keeps_range_moved_to_start():
    trimmed = trim_midi_file(_song(), BAR, BAR * 3)
    lead, bass = trimmed.tracks
    # Bars 2 and 3 of the lead, now bars 1 and 2
    assert _notes(lead) == [(0, "on", 61), (BAR, "off", 61), (BAR, "on", 62), (BAR * 2, "off", 62)]
    # The bass note began before the cut, so it is dropped; bar 4's is after it
    assert _notes(bass) == []
    assert _end(lead) == _end(bass) == BAR * 2
    assert all(t[-1].type == "end_of_track" for t in trimmed.tracks)
    assert trimmed.ticks_per_beat == TPB and trimmed.type == 1


def test_file_trim_carries_state_in_force_at_start():
    lead = trim_midi_file(_song(), BAR + TPB, BAR * 3).tracks[0]
    at_zero = [msg for tick, msg in _abs(lead) if tick == 0 and msg.type != "note_on"]
    kinds = [(m.type, getattr(m, "control", None)) for m in at_zero]
    # Latest tempo (the bar 2 change), not both; bank select before its program
    tempos = [m.tempo for m in at_zero if m.type == "set_tempo"]
    assert tempos == [600000]
    assert ("track_name", None) in kinds and ("time_signature", None) in kinds
    assert kinds.index(("control_change", 0)) < kinds.index(("program_change", None))
    assert ("control_change", 7) in kinds
    # The marker after the range is gone
    assert all(m.type != "marker" for _, m in _abs(lead))


def test_file_trim_releases_notes_at_end():
    # End mid-way through bar 2's note: its note-off moves to the end
    lead = trim_midi_file(_song(), BAR, BAR + TPB).tracks[0]
    assert _notes(lead) == [(0, "on", 61), (TPB, "off", 61)]
    assert _end(lead) == TPB


def test_file_trim_plays_and_saves(tmp_path):
    trimmed = trim_midi_file(_song(), BAR, BAR * 3)
    path = tmp_path / "trimmed.mid"
    trimmed.save(path)
    reloaded = MidiFile(path)
    assert [_notes(t) for t in reloaded.tracks] == [_notes(t) for t in trimmed.tracks]
    # 2 bars at 100 BPM (the tempo in force at bar 2)
    assert reloaded.length == pytest.approx(2 * 4 * 0.6)


def test_trim_does_not_change_the_original():
    song = _song()
    before = [list(t) for t in song.tracks]
    trim_midi_file(song, BAR, BAR * 2)
    trim_track(song.tracks[0], BAR, BAR * 2)
    assert [list(t) for t in song.tracks] == before


@pytest.mark.parametrize("start, end", [(BAR, BAR), (BAR * 2, BAR), (-1, BAR)])
def test_invalid_range_is_refused(start, end):
    with pytest.raises(ValueError):
        trim_midi_file(_song(), start, end)
    with pytest.raises(ValueError):
        trim_track(_song().tracks[0], start, end)


# --- trim_track -----------------------------------------------------------


def test_track_trim_keeps_timing_and_other_events():
    song = _song()
    lead = trim_track(song.tracks[0], BAR, BAR * 3)
    assert _notes(lead) == [(BAR, "on", 61), (BAR * 2, "off", 61), (BAR * 2, "on", 62), (BAR * 3, "off", 62)]
    # Same length; programs, tempo changes and the marker are all still there
    assert _end(lead) == _end(song.tracks[0])
    def others(track):
        return [
            (t, m.type)
            for t, m in _abs(track)
            if "note" not in m.type and m.type != "end_of_track"
        ]

    assert others(lead) == others(song.tracks[0])


def test_track_trim_cuts_held_note_at_end():
    bass = trim_track(_song().tracks[1], 0, BAR)
    assert _notes(bass) == [(0, "on", 36), (BAR, "off", 36)]
    assert _end(bass) == BAR * 4


# --- Dialog -------------------------------------------------------------------


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def _dialog(**kwargs) -> TrimDialog:
    options = dict(
        title="Trim",
        description="",
        start=2.0,
        end=6.0,
        duration=8.0,
        bar_beat=lambda s: (int(s // 2) + 1, 1),
        playhead=lambda: 4.0,
    )
    options.update(kwargs)
    return TrimDialog(**options)


def test_dialog_shows_range_and_bars(app):
    dialog = _dialog()
    assert dialog.range_seconds() == (2.0, 6.0)
    assert dialog.start_position.text() == "bar 2.1"
    assert dialog.end_position.text() == "bar 4.1"
    assert dialog.ok_button.isEnabled()


def test_dialog_refuses_end_before_start(app):
    dialog = _dialog()
    dialog.end_spin.setValue(1.0)
    assert not dialog.ok_button.isEnabled()
    assert dialog.length_label.text() == "End must be after Start"


def test_dialog_clamps_to_duration(app):
    assert _dialog(start=-1.0, end=99.0).range_seconds() == (0.0, 8.0)


# --- Player -------------------------------------------------------------------


@pytest.fixture
def player(app, tmp_path):
    path = tmp_path / "song.mid"
    _song().save(path)
    helper = Mock(spec=MidiIOHelper)
    helper.midi_out = Mock()
    editor = MidiFilePlayer(midi_helper=helper)
    with patch.object(editor, "_notify_pattern_sequencer_file_loaded"):
        assert editor.midi_load_file_from_path(str(path), update_recent_files=False)
    yield editor
    editor.transport_controller.shutdown()
    editor.close()
    app.processEvents()


def _accept_with(range_seconds):
    """Patch TrimDialog so it is accepted with *range_seconds* (or as opened)."""
    shown = {}

    def exec_(dialog):
        shown["range"] = dialog.range_seconds()
        if range_seconds is not None:
            dialog.start_spin.setValue(range_seconds[0])
            dialog.end_spin.setValue(range_seconds[1])
        return QDialog.DialogCode.Accepted

    return patch.object(TrimDialog, "exec", exec_), shown


def test_player_trim_file_uses_loop_range_and_rewinds(player):
    controller = player.transport_controller
    controller.seek_seconds(2.0)
    player.midi_loop_set_a()
    controller.seek_seconds(6.4)  # bar 3 at 100 BPM; snaps to its start
    player.midi_loop_set_b()
    a, b = controller.loop_range_seconds

    patcher, shown = _accept_with(None)
    with patcher:
        player.midi_trim_file()

    assert shown["range"] == pytest.approx((a, b))  # opened on the A–B range
    trimmed = player.midi_state.file
    assert player.midi_file.midi_track_viewer.midi_file is trimmed
    assert _notes(trimmed.tracks[0])[0] == (0, "on", 61)
    assert controller.loop_range_seconds is None
    assert controller.position_seconds == 0.0
    assert controller.duration_seconds == pytest.approx(b - a, abs=0.01)


def test_player_trim_file_whole_song_by_default(player):
    patcher, shown = _accept_with(None)
    with patcher:
        player.midi_trim_file()
    assert shown["range"] == pytest.approx((0.0, player.midi_state.file.length), abs=0.01)


def test_player_trim_track_changes_only_that_track(player):
    before_lead = list(player.midi_state.file.tracks[0])
    viewer = player.midi_file.midi_track_viewer
    patcher, _ = _accept_with((0.0, 2.0))  # bar 1
    with patcher:
        viewer.trim_track_requested.emit(1)
    tracks = player.midi_state.file.tracks
    assert _notes(tracks[1]) == [(0, "on", 36), (BAR, "off", 36)]
    assert list(tracks[0]) == before_lead
    assert viewer.midi_file is player.midi_state.file


def test_player_trim_cancel_changes_nothing(player):
    before = player.midi_state.file
    with patch.object(TrimDialog, "exec", lambda d: QDialog.DialogCode.Rejected):
        player.midi_trim_file()
        player.midi_trim_track(0)
    assert player.midi_state.file is before
