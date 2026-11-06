"""
Lit partial switches (no MIDI hardware).

- LitButton lights (glow) when checked, also when set with signals blocked
- PartialSwitch emits (partial, on, selected); setOn leaves SELECT alone
- an incoming PARTIALn_SWITCH no longer clears that partial's SELECT
"""

import os
import sys

sys.path.insert(0, os.path.abspath("."))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

_APP = QApplication.instance() or QApplication([])

from jdxi_editor.midi.data.digital.partial import DigitalPartial
from jdxi_editor.ui.widgets.panel.partial import PartialsPanel
from jdxi_editor.ui.widgets.switch.lit_button import LitButton
from jdxi_editor.ui.widgets.switch.partial import PartialSwitch


def test_lit_button_glows_when_checked_even_with_signals_blocked():
    button = LitButton("ON")
    assert button.graphicsEffect() is None
    button.blockSignals(True)
    button.setChecked(True)
    button.blockSignals(False)
    assert button.is_lit() and button.graphicsEffect() is not None
    button.click()
    assert not button.is_lit() and button.graphicsEffect() is None


def test_partial_switch_emits_and_set_on_keeps_select():
    switch = PartialSwitch(DigitalPartial.PARTIAL_2)
    seen = []
    switch.stateChanged.connect(lambda p, on, sel: seen.append((p, on, sel)))
    switch.select_check.click()
    assert seen[-1] == (DigitalPartial.PARTIAL_2, False, True)
    switch.setOn(True)
    assert switch.enable_check.isChecked() and switch.select_check.isChecked()


def test_panel_labels_each_partial():
    from PySide6.QtWidgets import QLabel

    panel = PartialsPanel()
    assert [w.text() for w in panel.findChildren(QLabel)] == [
        "PARTIAL 1",
        "PARTIAL 2",
        "PARTIAL 3",
    ]
    assert set(panel.switches) == set(DigitalPartial.get_partials())


def test_incoming_partial_switch_keeps_selection():
    from unittest.mock import Mock

    from jdxi_editor.midi.io.helper import MidiIOHelper
    from jdxi_editor.midi.sysex.partial.switch import PartialSwitchState
    from jdxi_editor.ui.editors.digital.editor import DigitalSynthEditor

    editor = DigitalSynthEditor(midi_helper=MidiIOHelper(), preset_helper=Mock())
    try:
        switch = editor.partials_panel.switches[DigitalPartial.PARTIAL_1]
        assert switch.select_check.isChecked()  # default: partial 1 on and selected
        param = Mock()
        param.name = PartialSwitchState.PARTIAL1_SWITCH
        successes, failures = [], []
        editor._update_partial_selection_switch(param, 1, successes, failures)
        assert successes and not failures
        assert switch.enable_check.isChecked() and switch.select_check.isChecked()
    finally:
        editor.close()
