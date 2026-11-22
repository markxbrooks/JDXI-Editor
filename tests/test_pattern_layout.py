"""
Pattern Editor layout (offscreen, no MIDI hardware).

- each part's header (name, note, mute) sits on the same row as its steps
- steps are grouped in beats of four
- active steps are filled in the part colour; the playhead is a light outline
"""

import os
import sys

sys.path.insert(0, os.path.abspath("."))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from unittest.mock import Mock

import pytest
from PySide6.QtCore import QPoint
from PySide6.QtWidgets import QApplication

_APP = QApplication.instance() or QApplication([])

from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.style.midi_player import PatternEditorStyle
from jdxi_editor.ui.widgets.pattern.measure_widget import BEAT_GAP, STEP_SPACING


@pytest.fixture
def editor():
    from jdxi_editor.ui.editors.pattern.pattern import PatternSequenceEditor

    helper = Mock(spec=MidiIOHelper)
    helper.midi_out = Mock()
    helper.send_raw_message = lambda b: True
    pattern = PatternSequenceEditor(midi_helper=helper, preset_helper=Mock())
    pattern.resize(1600, 1000)
    pattern.show()
    _APP.processEvents()
    yield pattern
    pattern.transport_controller.shutdown()
    pattern.close()
    _APP.processEvents()


def _centre_y(widget) -> int:
    return widget.mapTo(widget.window(), QPoint(0, widget.height() // 2)).y()


def test_headers_line_up_with_step_rows(editor):
    measure = editor.pattern_widget.get_current_measure_widget()
    for row, mute in enumerate(editor.mute_buttons):
        assert abs(_centre_y(mute) - _centre_y(measure.buttons[row][0])) <= 2


def test_steps_grouped_in_beats(editor):
    row = editor.pattern_widget.get_current_measure_widget().buttons[0]
    gaps = [row[i + 1].x() - (row[i].x() + row[i].width()) for i in range(15)]
    assert gaps[3] == gaps[7] == gaps[11] == STEP_SPACING + BEAT_GAP
    assert set(gaps[:3] + gaps[4:7]) == {STEP_SPACING}


def test_active_step_in_part_colour_and_playhead_outline():
    for row, colour in PatternEditorStyle.PART_COLORS.items():
        style = PatternEditorStyle.step_button_style(True, row=row)
        assert f"background-color: {colour.lower()}" in style.lower()
    playhead = PatternEditorStyle.step_button_style(False, is_current=True, row=0)
    assert f"3px solid {PatternEditorStyle.PLAYHEAD}" in playhead


def test_mute_keeps_its_style_and_mutes_the_channel(editor):
    mute = editor.mute_buttons[1]
    style = mute.styleSheet()
    mute.click()
    assert mute.isChecked() and mute.styleSheet() == style
    assert len(editor.muted_channels) == 1
    mute.click()
    assert editor.muted_channels == []


def test_toolbar_labels_and_usb_toggle(editor):
    assert editor.beats_per_measure_combo.itemText(0) == "16 steps"
    assert not editor.usb_recorder.isVisible()
    editor.usb_recorder_toggle.click()
    assert editor.usb_recorder.isVisible()


def test_section_range_counts_steps_from_one(editor, monkeypatch):
    from PySide6.QtWidgets import QMessageBox

    monkeypatch.setattr(QMessageBox, "warning", lambda *a, **k: None)
    measure = editor.pattern_widget.get_current_measure_widget()
    measure.buttons[0][2].setChecked(True)  # step 3
    editor.start_step_spinbox.setValue(3)
    editor.end_step_spinbox.setValue(3)
    editor._copy_section()
    editor.start_step_spinbox.setValue(9)  # paste at step 9
    editor._paste_section()
    assert measure.buttons[0][8].isChecked()
    assert [b.column for b in measure.buttons[0] if b.isChecked()] == [2, 8]


def test_muted_row_is_dimmed_in_every_measure_and_stays_editable(editor):
    editor.pattern_widget.add_measure()
    editor.mute_buttons[2].click()
    editor.pattern_widget.add_measure()  # added while muted
    for measure in editor.pattern_widget.get_measure_widgets():
        assert all(b.property("muted") for b in measure.buttons[2])
        assert not any(b.property("muted") for b in measure.buttons[1])
        assert all(b.isEnabled() for b in measure.buttons[2])
    style = PatternEditorStyle.step_button_style(True, row=2)
    assert 'QPushButton[muted="true"]' in style
    editor.mute_buttons[2].click()
    for measure in editor.pattern_widget.get_measure_widgets():
        assert not any(b.property("muted") for b in measure.buttons[2])


def test_combo_boxes_have_an_arrow():
    import os

    style = PatternEditorStyle.editor_stylesheet()
    start = style.index("QComboBox::down-arrow")
    url = style[style.index("url(", start) + 4 : style.index(")", start)]
    assert os.path.exists(url)


# --- Measure strip -----------------------------------------------------------


def test_strip_has_a_tile_per_measure_and_selects_on_click(editor):
    strip = editor.pattern_widget.measure_strip
    editor._add_measure()
    editor._add_measure()
    assert strip.count() == editor.pattern_widget.get_measure_count() == 3
    strip.tiles[2].clicked.emit(2)
    assert editor.pattern_widget.current_measure_index == 2
    assert strip.current() == 2 and strip.tiles[2].selected
    assert not strip.tiles[0].selected


def test_plus_tile_adds_like_add_measure(editor):
    pw = editor.pattern_widget
    pw.get_current_measure_widget().buttons[3][0].setChecked(True)
    editor.copy_previous_measure_checkbox.setChecked(True)
    pw.measure_strip.add_tile.clicked.emit()
    assert pw.get_measure_count() == 2
    assert pw.get_measure_widgets()[1].buttons[3][0].isChecked()  # copied
    assert editor.total_measures == 2


def test_tile_shows_steps_and_playing_marker(editor):
    strip = editor.pattern_widget.measure_strip
    tile = strip.tiles[0]
    assert tile.active_steps() == 0
    editor.pattern_widget.get_current_measure_widget().buttons[0][4].setChecked(True)
    assert tile.active_steps() == 1
    editor.pattern_widget.set_playing_measure(0)
    assert tile.playing
    editor.pattern_widget.set_playing_measure(None)
    assert not tile.playing


def test_loading_resets_the_strip(editor):
    editor.pattern_widget.clear_and_reset(3)
    strip = editor.pattern_widget.measure_strip
    assert strip.count() == 3 and strip.current() == 0


# --- Transport and Clear ---------------------------------------------------


def test_transport_is_the_shared_group_and_shows_state(editor):
    from picomidi.playback.engine import TransportState
    from PySide6.QtWidgets import QGroupBox

    transport = editor.pattern_transport
    assert transport.findChild(QGroupBox).title() == "Transport"  # as the MIDI Player
    transport.set_state(TransportState.PLAYING)
    assert editor.play_button.isChecked() and not editor.stop_button.isChecked()
    transport.set_state(TransportState.PAUSED)
    assert transport.pause_label.text() == "Resume"
    transport.set_state(TransportState.STOPPED)
    assert editor.stop_button.isChecked() and transport.pause_label.text() == "Pause"


def _answer_clear(monkeypatch, choice: str):
    from PySide6.QtWidgets import QMessageBox

    def fake_exec(box):
        for button in box.buttons():
            if button.text().startswith(choice):
                box._chosen = button
                return 0
        box._chosen = None
        return 0

    monkeypatch.setattr(QMessageBox, "exec", fake_exec)
    monkeypatch.setattr(QMessageBox, "clickedButton", lambda box: box._chosen)


def test_clear_asks_and_clears_measure_or_pattern(editor, monkeypatch):
    pw = editor.pattern_widget
    editor._add_measure()
    for measure in pw.get_measure_widgets():
        measure.buttons[0][0].setChecked(True)
    pw.select_measure(1)

    _answer_clear(monkeypatch, "Cancel")
    editor.confirm_clear()
    assert all(m.buttons[0][0].isChecked() for m in pw.get_measure_widgets())

    _answer_clear(monkeypatch, "Clear Measure")
    editor.confirm_clear()
    first, second = pw.get_measure_widgets()
    assert first.buttons[0][0].isChecked() and not second.buttons[0][0].isChecked()

    _answer_clear(monkeypatch, "Clear Whole")
    editor.confirm_clear()
    assert pw.get_measure_count() == 1 and editor.total_measures == 1
    assert pw.measure_strip.count() == 1
    assert not pw.get_measure_widgets()[0].buttons[0][0].isChecked()


# --- Display and playback follow -------------------------------------------


def test_display_shows_tempo_and_file(editor, tmp_path):
    assert editor.digital_title.display_texts[0] == "Tempo: 120 BPM"  # at startup
    editor.tempo_spinbox.setValue(132)
    assert editor.digital_title.display_texts[0] == "Tempo: 132 BPM"
    measure = editor.pattern_widget.get_current_measure_widget()
    button = measure.buttons[3][0]
    button.setChecked(True)
    editor._on_button_clicked(button, True)
    path = tmp_path / "groove.mid"
    editor.save_pattern(str(path))
    assert editor.digital_title.text == "Saved: groove.mid"
    editor.load_pattern(str(path))
    assert editor.digital_title.text == "Loaded: groove.mid"
    assert editor.digital_title.display_texts[0].startswith("Tempo:")  # kept
    editor.clear_pattern()
    assert editor.digital_title.text == "New pattern"


def test_grid_follows_playback_into_the_next_measure(editor):
    pw = editor.pattern_widget
    editor._add_measure()
    editor._add_measure()
    editor.current_step = 0
    editor._playback_last_bar_index = -1  # as when playback starts
    widgets = pw.get_measure_widgets()
    for step in (15, 16, 33):  # bar 0 step 15, bar 1 step 0, bar 2 step 1
        bar = step // 16
        editor._sync_sequencer_on_step_change(bar, editor._playback_last_bar_index)
        assert pw.current_measure_index == bar
        assert pw.sequencer_display.itemAt(0).widget() is widgets[bar]
        assert pw.measure_strip.current() == bar and pw.measure_strip.tiles[bar].playing
