"""Undo, redo and reload in a tone editor.

A control the user moves is a step. A value applied with its signals blocked
came from the JD-Xi and is not. Reload restores the values from before the
first change. A program change clears the steps.
"""

import os
import sys
from unittest.mock import MagicMock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout

from jdxi_editor.ui.editors.analog.editor import AnalogSynthEditor
from jdxi_editor.ui.editors.digital.editor import DigitalSynthEditor
from jdxi_editor.ui.editors.drum.editor import DrumCommonEditor
from jdxi_editor.ui.editors.history import EditHistory, install_edit_history
from jdxi_editor.ui.editors.synth.base import SynthBase
from jdxi_editor.ui.editors.synth.editor import SynthEditor

_APP = QApplication.instance() or QApplication(sys.argv)


class _Control:
    """A stand-in control: setValue is what Undo calls, and it sends."""

    def __init__(self, value=0):
        self._value = value
        self.sent = []

    def value(self):
        return self._value

    def setValue(self, value):
        self._value = int(value)
        self.sent.append(self._value)


def _history():
    editor = SynthBase()
    editor.setLayout(QVBoxLayout())
    return install_edit_history(editor), editor


def _move(history, control, new):
    old = control.value()
    control._value = (
        new  # the control already shows the new value when a step is recorded
    )
    history.record(control, old, new)


def test_a_change_undoes_redoes_and_reloads(monkeypatch):
    now = {"t": 0.0}
    monkeypatch.setattr(
        "jdxi_editor.ui.editors.history.time.monotonic", lambda: now["t"]
    )
    history, editor = _history()
    control = _Control(10)
    _move(history, control, 40)
    now["t"] += 2  # later than the drag window: a second step
    _move(history, control, 55)
    assert editor.findChild(QPushButton, "editUndo").isEnabled()
    assert not editor.findChild(QLabel, "editModified").isHidden()

    assert history.undo()
    assert control.value() == 40
    assert control.sent == [40]
    assert history.undo()
    assert control.value() == 10
    assert editor.findChild(QLabel, "editModified").isHidden()
    assert history.redo()
    assert control.value() == 40
    assert history.revert()
    assert control.value() == 10
    assert not history.can_undo()
    assert not history.can_restore()


def test_a_drag_is_one_step_and_a_return_to_the_start_is_none():
    history, _editor = _history()
    control = _Control(0)
    _move(history, control, 10)
    _move(history, control, 25)
    _move(history, control, 0)  # back where the drag started
    assert not history.can_undo()

    _move(history, control, 10)
    _move(history, control, 25)
    other = _Control(0)
    _move(history, other, 3)  # a different control: its own step
    assert history.undo()
    assert other.value() == 0
    assert control.value() == 25
    assert history.undo()
    assert control.value() == 0


def test_several_controls_in_one_gesture_are_one_step():
    history, _editor = _history()
    first, second = _Control(1), _Control(2)
    history.begin_group()
    _move(history, first, 5)
    _move(history, second, 8)
    history.end_group()
    assert history.undo()
    assert (first.value(), second.value()) == (1, 2)
    assert not history.can_undo()
    assert history.redo()
    assert (first.value(), second.value()) == (5, 8)


def test_a_value_from_the_jdxi_is_not_a_step_and_replaces_the_old_one():
    history, _editor = _history()
    control = _Control(0)
    history.record(control, 0, 30)
    control.setValue(30)
    history.external_change(control)  # the instrument now holds something else
    control._value = 70
    assert not history.can_undo()
    history.record(control, 70, 71)
    assert history.undo()
    assert control.value() == 70  # back to the instrument's value, not 0


def test_a_program_change_clears_the_steps():
    history, editor = _history()
    control = _Control()
    _move(history, control, 1)
    editor.device_refresher = MagicMock()
    SynthEditor._handle_program_change(editor, 0, 3)
    assert not history.can_undo()
    editor.device_refresher.schedule.assert_called_once()


def test_moving_a_slider_records_undo_and_a_blocked_value_does_not():
    editor = SynthBase(midi_helper=MagicMock())
    editor.setLayout(QVBoxLayout())
    install_edit_history(editor)
    sent = []
    editor.send_midi_parameter = (
        lambda param, value, address=None: sent.append(value) or True
    )

    class Param:
        name = "LEVEL"
        min_val = 0
        max_val = 127
        is_bipolar = False

    slider = editor._create_parameter_slider(Param(), "Level")
    slider.blockSignals(True)
    slider.setValue(15)  # a read from the JD-Xi
    slider.blockSignals(False)
    assert not editor.history.can_undo()

    slider.setValue(40)
    assert sent[-1] == 40
    assert editor.history.can_undo()
    editor.findChild(QPushButton, "editUndo").click()
    assert slider.value() == 15
    assert sent[-1] == 15

    slider.setValue(40)
    slider.setValue(60)
    editor.findChild(QPushButton, "editReload").click()
    assert slider.value() == 15
    assert not editor.history.can_undo()


def test_a_child_editors_control_uses_the_tone_editors_history():
    editor = SynthBase(midi_helper=MagicMock())
    editor.setLayout(QVBoxLayout())
    install_edit_history(editor)
    editor.send_midi_parameter = lambda *args, **kwargs: True
    section = SynthBase(midi_helper=MagicMock(), parent=editor)
    section.send_midi_parameter = lambda *args, **kwargs: True

    class Param:
        name = "CUTOFF"
        min_val = 0
        max_val = 127
        is_bipolar = False

    slider = section._create_parameter_slider(Param(), "Cutoff")
    slider.setValue(20)
    assert editor.history.can_undo()
    editor.history.undo()
    assert slider.value() == 0


def test_the_tone_editors_offer_undo_redo_and_reload():
    helper, presets = MagicMock(), MagicMock()
    for editor in (
        DigitalSynthEditor(midi_helper=helper, preset_helper=presets, synth_number=1),
        AnalogSynthEditor(midi_helper=helper, preset_helper=presets),
        DrumCommonEditor(midi_helper=helper, preset_helper=presets),
    ):
        assert editor.history.can_undo() is False
        for name in ("editUndo", "editRedo", "editReload"):
            button = editor.findChild(QPushButton, name)
            assert button is not None and not button.isEnabled(), name
        editor.close()
