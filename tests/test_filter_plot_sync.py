"""
The filter chart follows the filter mode and the cutoff (no MIDI hardware).

A program change makes the JD-Xi send FILTER_MODE_SWITCH; that goes through
update_controls_state(), not the mode buttons, and used to leave the chart in
bypass (not drawn) while the sliders were enabled.
"""

import os
import sys

sys.path.insert(0, os.path.abspath("."))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from unittest.mock import Mock

import pytest
from PySide6.QtWidgets import QApplication

_APP = QApplication.instance() or QApplication([])

from jdxi_editor.midi.io.helper import MidiIOHelper


@pytest.fixture
def analog():
    from jdxi_editor.ui.editors.analog.editor import AnalogSynthEditor

    editor = AnalogSynthEditor(MidiIOHelper(), Mock())
    editor.resize(1400, 900)
    editor.show()
    _APP.processEvents()
    yield editor
    editor.close()


def _receive_mode(editor, value: int) -> None:
    editor._handle_filter_mode_switch(
        editor.SYNTH_SPEC.Param.FILTER_MODE_SWITCH, value, [], []
    )


def test_incoming_lpf_enables_the_chart_and_cutoff_redraws_it(analog):
    widget = analog.filter_section.filter_widget
    _receive_mode(analog, 1)
    assert widget.plot.enabled and widget.plot.filter_mode == "lpf"
    before = widget.plot.grab().toImage()
    widget.cutoff_param_control.slider.setValue(20)
    _APP.processEvents()
    assert widget.plot.grab().toImage() != before


def test_incoming_bypass_disables_chart_and_controls(analog):
    section = analog.filter_section
    _receive_mode(analog, 1)
    _receive_mode(analog, 0)
    assert not section.filter_widget.plot.enabled
    assert section.filter_widget.plot.filter_mode == "bypass"
    assert not section.filter_group.isEnabled()


def test_digital_chart_follows_every_filter_mode():
    from jdxi_editor.ui.editors.digital.editor import DigitalSynthEditor

    editor = DigitalSynthEditor(midi_helper=MidiIOHelper(), preset_helper=Mock())
    try:
        section = list(editor.partial_editors.values())[0].filter_tab
        for value, name in ((2, "hpf"), (3, "bpf"), (1, "lpf"), (0, "bypass")):
            section.update_controls_state(value)
            assert section.filter_widget.plot.filter_mode == name
            assert section.filter_widget.plot.enabled == (value != 0)
    finally:
        editor.close()
