"""
A JD-Xi unplugged or switched off: its MIDI input may refuse to close
(Windows: «error closing Windows MM MIDI input port»). Reopened, such a port
received nothing, so a port that fails to close is replaced, and reconnecting
always opens new ports. From JD-Xi Studio (c7ba0fd9, 6ef63b1c).
"""

import os
from unittest.mock import Mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

_APP = QApplication.instance() or QApplication([])

from jdxi_editor.midi.io.helper import MidiIOHelper


def test_a_port_that_does_not_close_is_replaced_and_set_up_again():
    helper = MidiIOHelper()
    dead = Mock()
    dead.is_port_open.return_value = True
    dead.close_port.side_effect = RuntimeError("MidiInWinMM::closePort: error closing")
    helper.midi_in = dead
    helper.close_ports()
    assert helper.midi_in is not dead
    # the new input calls the helper's callback, as the first one did
    assert getattr(helper.midi_in, "_callback", None) == helper.midi_callback


def test_reconnecting_opens_new_ports():
    helper = MidiIOHelper()
    old_in, old_out = helper.midi_in, helper.midi_out
    in_name = next(p for p in helper.get_input_ports() if "JD-Xi" in p)
    out_name = next(p for p in helper.get_output_ports() if "JD-Xi" in p)
    assert helper.reconnect_port_names(in_name, out_name)
    assert helper.midi_in is not old_in and helper.midi_out is not old_out
    assert helper.midi_in.is_port_open() and helper.midi_out.is_port_open()
    assert getattr(helper.midi_in, "_callback", None) == helper.midi_callback
