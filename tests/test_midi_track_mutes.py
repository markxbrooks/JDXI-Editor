"""
Track mutes in the MIDI player's track viewer (no MIDI hardware).

- a mute button click mutes, a second click unmutes (button and state agree)
- channel changes, reordering and in-place edits keep mutes
- muted tracks and channels are drawn dimmed
- each track's velocity slider is kept through edits like its mute
"""

import os
import sys

sys.path.insert(0, os.path.abspath("."))

import mido
import pytest
from PySide6.QtWidgets import QApplication

_APP = QApplication.instance() or QApplication([])

from jdxi_editor.ui.widgets.midi.colors import MIDI_CHANNEL_COLORS
from jdxi_editor.ui.widgets.midi.track_viewer import MidiTrackViewer


def _midi_file(track_count: int = 3) -> mido.MidiFile:
    mid = mido.MidiFile(type=1, ticks_per_beat=480)
    for i in range(track_count):
        track = mido.MidiTrack()
        track.append(mido.MetaMessage("track_name", name=f"T{i}", time=0))
        track.append(mido.Message("note_on", note=60, velocity=64, channel=i, time=0))
        track.append(mido.Message("note_off", note=60, velocity=0, channel=i, time=480))
        mid.tracks.append(track)
    return mid


@pytest.fixture
def viewer():
    v = MidiTrackViewer()
    v.set_midi_file(_midi_file())
    return v


def _names(v):
    return [t.name for t in v.midi_file.tracks]


def test_mute_button_click_mutes_and_unmutes(viewer):
    button = viewer.track_mute_buttons[1]
    button.click()
    assert button.isChecked() and viewer.muted_tracks == {1}
    button.click()
    assert not button.isChecked() and viewer.muted_tracks == set()


def test_mute_changed_reports_final_state(viewer):
    seen = []
    viewer.mute_changed.connect(lambda: seen.append(set(viewer.muted_tracks)))
    viewer.track_mute_buttons[2].click()
    assert seen == [{2}]


def test_channel_change_keeps_mutes(viewer):
    viewer.track_mute_buttons[1].click()
    viewer.change_track_channel(0, 5)
    assert viewer.muted_tracks == {1}
    assert viewer.track_mute_buttons[1].isChecked()
    assert viewer.midi_track_widgets[1].muted


def test_move_keeps_mutes_with_their_tracks(viewer):
    viewer.track_mute_buttons[0].click()  # T0
    viewer.move_track(0, 2)
    assert _names(viewer) == ["T1", "T2", "T0"]
    assert viewer.muted_tracks == {2}
    viewer.move_track(2, 0)
    assert _names(viewer) == ["T0", "T1", "T2"]
    assert viewer.muted_tracks == {0}


def test_new_file_starts_unmuted_edits_keep_mutes(viewer):
    viewer.track_mute_buttons[2].click()
    viewer.set_midi_file(viewer.midi_file, keep_track_state=True)
    assert viewer.muted_tracks == {2}
    viewer.set_midi_file(_midi_file())
    assert viewer.muted_tracks == set()
    assert not viewer.track_mute_buttons[2].isChecked()


def test_muted_track_drawn_dimmed(viewer):
    widget = viewer.midi_track_widgets[1]
    widget.resize(200, 30)
    widget.cached_pixmap = widget.render_track_to_pixmap()
    viewer.track_mute_buttons[1].click()
    assert widget.muted and widget.cached_pixmap is None  # redrawn


def test_channel_mute_matches_channel_and_leaves_colours(viewer):
    alpha = MIDI_CHANNEL_COLORS[0].alpha()
    viewer.toggle_channel_mute(1, True)  # buttons are 1-16
    widget = viewer.midi_track_widgets[0]  # plays on channel 1 (0-based 0)
    assert widget._is_channel_muted(0)
    assert not viewer.midi_track_widgets[1]._is_channel_muted(1)
    widget.resize(200, 30)
    widget.render_track_to_pixmap()
    assert MIDI_CHANNEL_COLORS[0].alpha() == alpha


def test_velocity_slider_sets_scale(viewer):
    changes = []
    viewer.track_velocity_changed.connect(lambda: changes.append(1))
    viewer.track_velocity_sliders[0].setValue(150)
    assert viewer.get_track_velocity_scales() == {0: 1.5}
    assert changes == [1]
    viewer.track_velocity_sliders[0].setValue(100)
    assert viewer.get_track_velocity_scales() == {}


def test_velocity_follows_moved_track_and_resets_on_new_file(viewer):
    viewer.track_velocity_sliders[0].setValue(40)  # T0
    viewer.move_track(0, 2)
    assert viewer.get_track_velocity_scales() == {2: 0.4}
    assert viewer.track_velocity_sliders[2].value() == 40
    assert viewer.track_velocity_sliders[0].value() == 100
    viewer.change_track_channel(2, 7)
    assert viewer.get_track_velocity_scales() == {2: 0.4}
    viewer.set_midi_file(_midi_file())
    assert viewer.get_track_velocity_scales() == {}
