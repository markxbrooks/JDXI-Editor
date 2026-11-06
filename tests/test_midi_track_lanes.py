"""
MIDI player track rows (no MIDI hardware).

- a lane is a miniature piano roll: notes keep their length and pitch
- a track without notes (tempo / conductor) draws nothing and has no channel
- channel and name edits in the header apply immediately, in place
"""

import os
import sys

sys.path.insert(0, os.path.abspath("."))

import mido
import pytest
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication

_APP = QApplication.instance() or QApplication([])

from jdxi_editor.ui.style.midi_player import MidiPlayerStyle
from jdxi_editor.ui.widgets.midi.track import MidiTrackWidget
from jdxi_editor.ui.widgets.midi.track_viewer import MidiTrackViewer


def _file() -> mido.MidiFile:
    mid = mido.MidiFile(type=1, ticks_per_beat=480)
    tempo = mido.MidiTrack()
    tempo.append(mido.MetaMessage("set_tempo", tempo=500000, time=0))
    tempo.append(mido.MetaMessage("end_of_track", time=1920))
    lead = mido.MidiTrack()
    lead.append(mido.MetaMessage("track_name", name="Lead  ", time=0))
    lead.append(mido.Message("note_on", note=60, velocity=100, channel=0, time=0))
    lead.append(mido.Message("note_off", note=60, velocity=0, channel=0, time=960))
    lead.append(mido.Message("note_on", note=72, velocity=100, channel=0, time=0))
    lead.append(mido.Message("note_on", note=72, velocity=0, channel=0, time=960))
    mid.tracks.extend([tempo, lead])
    return mid


@pytest.fixture
def viewer():
    v = MidiTrackViewer()
    v.set_midi_file(_file())
    return v


def test_notes_keep_length_and_pitch():
    mid = _file()
    widget = MidiTrackWidget(mid.tracks[1], 1, mid.length, 480)
    notes = widget.track_data["notes"]
    assert [(round(s, 2), round(e, 2), p) for s, e, p, _ in notes] == [
        (0.0, 0.5, 60),
        (0.5, 1.0, 72),
    ]
    assert widget.track_data["pitch_range"] == (60, 72)
    assert "Lead | Notes: 2 | Channel: 1" == widget.toolTip()


def test_track_without_notes_draws_nothing():
    mid = _file()
    widget = MidiTrackWidget(mid.tracks[0], 0, mid.length, 480)
    widget.resize(300, MidiPlayerStyle.TRACK_HEIGHT)
    image = widget.render_track_to_pixmap().toImage()
    background = QColor(MidiPlayerStyle.BACKGROUND).rgb()
    # Everything but the row separator is background
    assert all(
        image.pixel(x, y) == background
        for x in range(0, 300, 7)
        for y in range(0, MidiPlayerStyle.TRACK_HEIGHT - 2, 5)
    )


def test_tempo_track_has_no_channel_selector(viewer):
    assert 0 not in viewer.track_channel_spins
    assert 1 in viewer.track_channel_spins
    assert not viewer.track_velocity_sliders[0].isVisibleTo(viewer)
    assert viewer._track_name_edits[1].text() == "Lead"  # padding removed


def test_rows_have_fixed_height(viewer):
    assert all(
        row.height() == MidiPlayerStyle.TRACK_HEIGHT or row.maximumHeight() == MidiPlayerStyle.TRACK_HEIGHT
        for row in viewer._draggable_rows.values()
    )


def test_channel_edit_applies_in_place(viewer):
    viewer.track_mute_buttons[1].click()
    spin = viewer.track_channel_spins[1]
    files = []
    viewer.file_changed.connect(files.append)
    spin.setValue(2)
    spin.setValue(3)  # arrows clicked twice: one change after the delay
    assert files == []
    viewer.flush_pending_edits()
    assert len(files) == 1 and files[0] is viewer.midi_file
    track = viewer.midi_file.tracks[1]
    assert {m.channel for m in track if hasattr(m, "channel")} == {2}
    assert viewer.track_channel_spins[1] is spin  # row not rebuilt
    assert viewer._track_part_labels[1].text() == "Analog"
    assert viewer.muted_tracks == {1}
    assert {m.channel for m in viewer.midi_track_widgets[1].track if hasattr(m, "channel")} == {2}


def test_channel_edit_applies_after_delay(viewer):
    viewer.track_channel_spins[1].setValue(10)
    from PySide6.QtTest import QTest

    QTest.qWait(viewer.CHANNEL_EDIT_DELAY_MS + 200)
    assert {m.channel for m in viewer.midi_file.tracks[1] if hasattr(m, "channel")} == {9}
    assert viewer._track_part_labels[1].text() == "Drums"


def test_name_edit_renames_once(viewer):
    edit = viewer._track_name_edits[1]
    edit.setText("Strings")
    edit.editingFinished.emit()
    track = viewer.midi_file.tracks[1]
    assert track.name == "Strings"
    assert sum(1 for m in track if m.type == "track_name") == 1
    files = []
    viewer.file_changed.connect(files.append)
    edit.editingFinished.emit()  # unchanged: nothing to do
    assert files == []


# --- Ruler -------------------------------------------------------------------

from PySide6.QtCore import QPoint
from PySide6.QtGui import QPainter, QPixmap

from jdxi_editor.ui.widgets.midi.time_ruler import (
    MIN_LABEL_SPACING,
    RulerMarker,
    TimeRulerWidget,
)


def test_ruler_numbers_fewer_bars_when_zoomed_out():
    pixmap = QPixmap(10, 10)
    painter = QPainter(pixmap)
    try:
        assert TimeRulerWidget._label_interval(60.0, painter, 100) == 1
        assert TimeRulerWidget._label_interval(15.0, painter, 100) == 2
        interval = TimeRulerWidget._label_interval(3.0, painter, 100)
        assert 3.0 * interval >= MIN_LABEL_SPACING and 3.0 * interval / 2 < MIN_LABEL_SPACING
    finally:
        painter.end()


def test_markers_at_the_same_time_share_a_flag_and_tooltip():
    ruler = TimeRulerWidget()
    ruler.set_midi_file(_file())
    ruler.resize(400, 34)
    ruler.set_markers(
        [RulerMarker(0.0, f"Ch{c} PC 1", key=c) for c in (1, 2, 3)]
        + [RulerMarker(1.5, "Ch1 PC 9", key=9)]
    )
    groups = ruler._marker_groups()
    assert [len(g) for g in groups] == [3, 1]
    near = ruler._markers_near(QPoint(2, 5))
    assert [m.label for m in near] == ["Ch1 PC 1", "Ch2 PC 1", "Ch3 PC 1"]


# --- Player panels -----------------------------------------------------------

from unittest.mock import Mock

from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.midi_player.editor import MidiFilePlayer


def test_unused_channels_dimmed_and_classification_is_one_row(tmp_path):
    path = tmp_path / "song.mid"
    _file().save(path)
    helper = Mock(spec=MidiIOHelper)
    helper.midi_out = Mock()
    editor = MidiFilePlayer(midi_helper=helper)
    try:
        editor.midi_load_file_from_path(str(path), update_recent_files=False)
        buttons = editor.mute_channels_group.mute_channel_buttons
        assert buttons[1].property("unused") is False
        assert buttons[2].property("unused") is True
        group = editor.classification_group
        tops = {
            b.geometry().top()
            for b in (
                group.detect_drums_button,
                group.classify_tracks_button,
                group.apply_presets_button,
            )
        }
        assert len(tops) == 1  # one row
        assert not hasattr(group, "apply_all_track_changes_button")
    finally:
        editor.transport_controller.shutdown()
        editor.close()
