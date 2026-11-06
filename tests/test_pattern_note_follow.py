"""
Pattern Editor (no MIDI hardware): an incoming note sets that channel's pitch combo,
so the next step entered uses it; the 12/16 Steps combo greys out steps 13-16.
"""

import os
import sys

sys.path.insert(0, os.path.abspath("."))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from unittest.mock import MagicMock, Mock

import mido
import pytest
from PySide6.QtWidgets import QApplication

_APP = QApplication.instance() or QApplication([])

from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.pattern.options import DEFAULT_PITCH, DIGITAL_OPTIONS


@pytest.fixture
def editor():
    from jdxi_editor.ui.editors.pattern.pattern import PatternSequenceEditor

    helper = MagicMock(spec=MidiIOHelper)
    helper.midi_message_incoming = MagicMock()
    ed = PatternSequenceEditor(midi_helper=helper, preset_helper=Mock())
    yield ed
    ed.close()
    ed.deleteLater()


def test_pitch_list_covers_the_keyboard_and_starts_on_c4(editor):
    assert DIGITAL_OPTIONS[0] == "C0" and DIGITAL_OPTIONS[-1] == "C8"
    for selector in (editor.digital1_selector, editor.digital2_selector, editor.analog_selector):
        assert selector.currentText() == DEFAULT_PITCH


@pytest.mark.parametrize(
    "channel, note, name, attr",
    [
        (0, 45, "A2", "digital1_selector"),  # the reported case: below C4
        (1, 84, "C6", "digital2_selector"),
        (2, 24, "C1", "analog_selector"),  # below C2
    ],
)
def test_incoming_note_sets_the_channels_combo(editor, channel, note, name, attr):
    editor._combo_synchronizer.process_incoming_midi(
        mido.Message("note_on", channel=channel, note=note, velocity=1)
    )
    assert getattr(editor, attr).currentText() == name


def test_new_step_uses_the_detected_note(editor):
    editor._combo_synchronizer.process_incoming_midi(
        mido.Message("note_on", channel=0, note=45, velocity=90)
    )
    button = editor.buttons[0][0]
    button.setChecked(True)
    editor._on_button_clicked(button, True)
    assert button.note == 45


def test_twelve_steps_greys_out_the_last_four_and_sixteen_restores_them(editor):
    """Steps 13-16 are greyed out in all four rows at 12 steps; their notes come back at 16."""
    kept = editor.buttons[2][14]
    kept.setChecked(True)  # a note in step 15 before switching

    editor.beats_per_measure_combo.setCurrentIndex(1)  # 12 steps
    for row in editor.buttons:
        assert [b.isEnabled() for b in row] == [True] * 12 + [False] * (len(row) - 12)
    assert kept.isChecked()  # kept, not deleted

    editor.beats_per_measure_combo.setCurrentIndex(0)  # back to 16
    for row in editor.buttons:
        assert all(b.isEnabled() for b in row)
    assert kept.isChecked()


def test_save_button_opens_a_save_dialog(editor, monkeypatch, tmp_path):
    """Save asks for a file to save to (it opened an Open dialog), then writes it."""
    from PySide6.QtWidgets import QFileDialog

    calls = []
    target = str(tmp_path / "pattern")

    def fake_save(*args, **kwargs):
        calls.append("save")
        return target, ""

    def fake_open(*args, **kwargs):
        calls.append("open")
        return "", ""

    monkeypatch.setattr(QFileDialog, "getSaveFileName", staticmethod(fake_save))
    monkeypatch.setattr(QFileDialog, "getOpenFileName", staticmethod(fake_open))

    editor.pattern_file_group.save_button.click()
    assert calls == ["save"]
    assert os.path.exists(target + ".mid")

    editor.pattern_file_group.load_button.click()
    assert calls == ["save", "open"]  # Load still opens an Open dialog


def test_step_guide_lines_span_their_steps(editor):
    """Lines of 3 (over steps 1-12), 8 and 4 steps, each from its first step's left edge to its last's right edge."""
    from PySide6.QtCore import QPoint

    editor.resize(1400, 900)
    editor.show()
    _APP.processEvents()
    guide = editor.pattern_widget.step_guide
    buttons = editor.pattern_widget.get_current_measure_widget().buttons[0]

    def left(i):
        return guide.mapFrom(guide.window(), buttons[i].mapTo(guide.window(), QPoint(0, 0))).x()

    def right(i):
        return left(i) + buttons[i].width() - 1

    rows = {}
    for x1, x2, y in guide.segments():
        rows.setdefault(y, []).append((x1, x2))
    threes, eights, fours = (rows[y] for y in sorted(rows))
    assert threes == [(left(i), right(i + 2)) for i in (0, 3, 6, 9)]
    assert eights == [(left(0), right(7)), (left(8), right(15))]
    assert fours == [(left(i), right(i + 3)) for i in (0, 4, 8, 12)]
