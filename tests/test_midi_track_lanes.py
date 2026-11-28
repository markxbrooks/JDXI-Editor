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
    from jdxi_editor.ui.style.rack_skin import active_skin, set_active_skin

    previous = active_skin().skin_id
    set_active_skin("glossy_black", remember=False)
    try:
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
    finally:
        set_active_skin(previous, remember=False)


@pytest.mark.parametrize("skin_id", ["brushed_70s", "minimoog"])
def test_punched_card_lanes(skin_id):
    from jdxi_editor.ui.style.rack_skin import active_skin, set_active_skin

    previous = active_skin().skin_id
    set_active_skin(skin_id, remember=False)
    try:
        mid = _file()
        widget = MidiTrackWidget(mid.tracks[1], 1, mid.length, 480)
        widget.resize(300, MidiPlayerStyle.TRACK_HEIGHT)
        image = widget.render_track_to_pixmap().toImage()
        card = image.pixelColor(10, 10)
        assert card.red() > 240 and card.green() > 240 and card.blue() > 240
        holes = [
            image.pixelColor(x, y)
            for x in range(0, 300, 2)
            for y in range(4, MidiPlayerStyle.TRACK_HEIGHT - 4, 2)
        ]
        assert any(c.red() < 40 and c.green() < 40 and c.blue() < 40 for c in holes)

        viewer = MidiTrackViewer()
        viewer.resize(400, 240)
        viewer.show()
        QApplication.processEvents()
        shot = viewer.grab().toImage()
        viewer.close()
        viewer.set_midi_file(_file())
        from jdxi_editor.ui.style.rack_skin import active_skin

        ink = active_skin().foreground
        assert ink.text in viewer._track_name_edits[1].styleSheet()
        assert ink.text_secondary in viewer._track_part_labels[1].styleSheet()
        backing = shot.pixelColor(shot.width() // 2, shot.height() // 3)
        if skin_id == "minimoog":  # the cabinet's walnut
            assert backing.red() > backing.blue() + 30
            assert backing.red() > backing.green()
        else:  # the faceplate's satin aluminium: neutral silver, not wood
            channels = (backing.red(), backing.green(), backing.blue())
            assert max(channels) - min(channels) <= 10, backing.name()
            assert backing.lightness() > 100, backing.name()
    finally:
        set_active_skin(previous, remember=False)


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
        assert "Digital 1" in buttons[1].toolTip() and buttons[1].property("part") is True
        assert "no JD-Xi part" in buttons[5].toolTip() and buttons[5].property("part") is False
        group = editor.classification_group
        tops = {b.geometry().top() for b in (group.fit_tracks_button, group.apply_presets_button)}
        assert len(tops) == 1  # one row
        # the file's only notes are on channel 1: ready for the JD-Xi
        assert group.summary_label.text().startswith("Ready for the JD-Xi")
        assert not hasattr(group, "apply_all_track_changes_button")
    finally:
        editor.transport_controller.shutdown()
        editor.close()


def test_a_track_without_a_name_shows_what_it_plays():
    """No name in the file: the instrument, in grey (GM program, or the file's
    instrument name; channel 10: drums) instead of «Unnamed»."""
    from jdxi_editor.midi.track.instrument import instrument_hint

    flute = mido.MidiTrack([mido.Message("program_change", channel=2, program=73, time=0),
                            mido.Message("note_on", channel=2, note=72, time=0)])
    named = mido.MidiTrack([mido.MetaMessage("instrument_name", name="Tubular Bells", time=0)])
    drums = mido.MidiTrack([mido.Message("note_on", channel=9, note=36, time=0)])
    assert instrument_hint(flute) == "Flute"
    assert instrument_hint(named) == "Tubular Bells"
    assert instrument_hint(drums) == "Drums"
    assert instrument_hint(mido.MidiTrack()) is None
    song = _file()
    song.tracks.append(flute)
    viewer = MidiTrackViewer()
    viewer.set_midi_file(song)
    edit = viewer._track_name_edits[2]
    assert edit.text() == "" and edit.placeholderText() == "Flute"
    assert viewer._track_name_edits[1].text() == "Lead"  # a real name stays
