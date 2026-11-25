"""
MidiIOHelper inherits signals from two QObject bases; connecting to them must
not trip PySide's "Sort Warning" about the order of its signals and slots.
"""

import os
import sys
import warnings

sys.path.insert(0, os.path.abspath("."))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

_APP = QApplication.instance() or QApplication([])

from jdxi_editor.midi.io.helper import MidiIOHelper


def test_connecting_to_both_bases_keeps_the_metaobject_ordered():
    helper = MidiIOHelper()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        helper.midi_message_outgoing.connect(lambda message: None)
        helper.midi_message_incoming.connect(lambda message: None)
        helper.midi_sysex_json.connect(lambda payload: None)
    assert not [w for w in caught if "Sort Warning" in str(w.message)]


def test_device_sysex_still_reaches_the_editors():
    helper = MidiIOHelper()
    received = []
    helper.midi_sysex_json.connect(received.append)
    helper._device_sysex_json.emit('{"x": 1}')
    _APP.processEvents()
    assert received == ['{"x": 1}']
