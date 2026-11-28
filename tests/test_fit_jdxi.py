"""Fit to the JD-Xi: what the JD-Xi plays of a MIDI file, and a proposal that
puts its tracks on the JD-Xi's four parts (1, 2, 3, 10)."""

import os
import sys

sys.path.insert(0, os.path.abspath("."))

import mido
from PySide6.QtWidgets import QApplication

_APP = QApplication.instance() or QApplication([])

from jdxi_editor.ui.editors.midi_player import fit_jdxi as fit
from jdxi_editor.ui.editors.midi_player.track.category import TrackCategory


def _song(channels):
    song = mido.MidiFile(type=1, ticks_per_beat=480)
    tempo = mido.MidiTrack([mido.MetaMessage("set_tempo", tempo=500000, time=0)])
    song.tracks.append(tempo)
    for n, channel in enumerate(channels):
        track = mido.MidiTrack([mido.MetaMessage("track_name", name=f"T{n}", time=0)])
        for i in range(3):
            track.append(mido.Message("note_on", channel=channel - 1, note=48 + i, velocity=90, time=0))
            track.append(mido.Message("note_off", channel=channel - 1, note=48 + i, time=240))
        song.tracks.append(track)
    return song


def test_a_file_made_for_the_jdxi_is_ready():
    text, ready = fit.summary(_song([1, 2, 3, 10]))
    assert ready and "4 tracks" in text


def test_a_general_file_says_what_is_not_heard():
    text, ready = fit.summary(_song([1, 5, 6, 10, 12]))
    assert not ready
    assert text == "3 of 5 tracks are on channels no JD-Xi part plays: they are not heard."
    assert fit.summary(None)[1] is False


def test_the_proposal_puts_drums_bass_keys_strings_on_the_parts():
    song = _song([1, 5, 6, 7, 12])
    tracks = fit.note_tracks(song)  # track indices 1..5 (0 is the tempo track)
    classifications = {
        TrackCategory.BASS: [(2, None)],
        TrackCategory.KEYS_GUITARS: [(3, None)],
        TrackCategory.STRINGS: [(4, None)],
        TrackCategory.UNCLASSIFIED: [(5, None)],
    }
    proposal = fit.propose(tracks, drum_indices=[1], classifications=classifications)
    assert proposal == {1: 10, 2: 1, 3: 2, 4: 3, 5: fit.NOT_PLAYED}


def test_one_track_per_melodic_part_the_best_one():
    """45 tracks of an orchestra on two parts were a jumble: each melodic part
    takes the track recognised best for it; the others are not played."""
    from types import SimpleNamespace

    song = _song([1, 5, 6, 7])
    tracks = fit.note_tracks(song)  # indices 1..4
    def stats(score):
        return SimpleNamespace(scores={TrackCategory.KEYS_GUITARS: score})
    classifications = {TrackCategory.KEYS_GUITARS: [(2, stats(40)), (3, stats(90)), (4, stats(60))]}
    proposal = fit.propose(tracks, drum_indices=[], classifications=classifications)
    assert proposal[3] == 2  # the best keys track on Digital 2
    assert proposal[2] == fit.NOT_PLAYED and proposal[4] == fit.NOT_PLAYED
    assert proposal[1] == 1  # nothing recognised for Digital 1: the track already on 1 keeps it


def test_the_dialog_returns_only_the_moves():
    song = _song([1, 5, 2])
    tracks = fit.note_tracks(song)  # 1: ch 1, 2: ch 5, 3: ch 2
    dialog = fit.FitDialog(tracks, {1: 1, 2: 3, 3: fit.NOT_PLAYED})
    assert dialog.changes() == {2: 3, 3: fit.OFF_CHANNEL}
    assert dialog.table.rowCount() == 3
    dialog.combos[2].setCurrentIndex(dialog.combos[2].findData(fit.NOT_PLAYED))
    assert dialog.changes() == {3: fit.OFF_CHANNEL}  # left on 5: nothing to move
    assert "stays on channel 5" in dialog.combos[2].currentText()


def test_the_dialog_can_show_the_parts_as_they_are_now():
    song = _song([1, 5, 2])
    tracks = fit.note_tracks(song)  # 1: ch 1, 2: ch 5, 3: ch 2
    proposal = {1: 10, 2: 3, 3: fit.NOT_PLAYED}
    dialog = fit.FitDialog(tracks, proposal, start_as_now=True)
    assert dialog.changes() == {}  # as now: nothing to move
    assert dialog.combos[2].currentData() == fit.NOT_PLAYED  # channel 5: on no part
    dialog.proposal_button.click()
    assert dialog.changes() == {1: 10, 2: 3, 3: fit.OFF_CHANNEL}
    dialog.as_now_button.click()
    assert dialog.changes() == {}


def test_after_apply_the_dialog_shows_what_was_applied(tmp_path, monkeypatch):
    """It showed the proposal again, as if nothing had been applied."""
    from unittest.mock import Mock

    from PySide6.QtWidgets import QDialog

    from jdxi_editor.midi.io.helper import MidiIOHelper
    from jdxi_editor.ui.editors.midi_player.editor import MidiFilePlayer

    path = tmp_path / "song.mid"
    _song([5, 6]).save(path)
    helper = Mock(spec=MidiIOHelper)
    helper.midi_out = Mock()
    editor = MidiFilePlayer(midi_helper=helper)
    shown = []

    def run(dialog):
        shown.append({i: c.currentData() for i, c in dialog.combos.items()})
        if len(shown) == 1:  # the first time: Digital 2 for the first track
            dialog.combos[1].setCurrentIndex(dialog.combos[1].findData(2))
            dialog.combos[2].setCurrentIndex(dialog.combos[2].findData(fit.NOT_PLAYED))
        return QDialog.DialogCode.Accepted

    monkeypatch.setattr(fit.FitDialog, "exec", run)
    try:
        editor.midi_load_file_from_path(str(path), update_recent_files=False)
        editor.fit_tracks_to_jdxi()
        editor.fit_tracks_to_jdxi()
        assert shown[1] == {1: 2, 2: fit.NOT_PLAYED}
        # another file: its proposal again
        editor.midi_load_file_from_path(str(path), update_recent_files=False)
        assert editor._fit_applied is False
    finally:
        editor.transport_controller.shutdown()
        editor.close()
