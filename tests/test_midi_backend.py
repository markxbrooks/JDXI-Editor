"""
Starting when the system has no MIDI backend.

python-rtmidi raises from MidiIn()/MidiOut() when it cannot reach the
platform's MIDI service, which on Linux is whenever /dev/snd/seq is missing
because the kernel's snd-seq module is not loaded. That is the normal state in
a container and on a CI runner, and it used to stop the editor being built at
all, with a traceback out of _rtmidi rather than a message.
"""

import os
import sys

sys.path.insert(0, os.path.abspath("."))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
import rtmidi
from PySide6.QtWidgets import QApplication

_APP = QApplication.instance() or QApplication([])

from jdxi_editor.midi.io.backend import NoMidiBackend, open_rtmidi

ALSA_ERROR = "MidiInAlsa::initialize: error creating ALSA sequencer client object"


def _raise(*_args, **_kwargs):
    raise RuntimeError(ALSA_ERROR)


def test_a_working_backend_is_passed_through():
    """The real port is returned untouched when rtmidi can be built."""
    sentinel = object()
    assert open_rtmidi(lambda: sentinel, "input") is sentinel


def test_a_missing_backend_gives_a_stand_in():
    port = open_rtmidi(_raise, "input")
    assert isinstance(port, NoMidiBackend)


def test_the_stand_in_answers_every_call_the_editor_makes():
    """
    Whatever the editor asks a port, the stand-in answers.

    These are the rtmidi calls the editor actually makes; a missing one would
    be an AttributeError at some later, less obvious moment.
    """
    port = NoMidiBackend()
    assert port.get_ports() == []
    assert port.is_port_open() is False
    assert port.open_port(0) is None
    assert port.close_port() is None
    assert port.set_callback(lambda *a: None) is None
    assert port.cancel_callback() is None
    assert port.ignore_types(False, False, False) is None
    assert port.send_message([0x90, 0x40, 0x7F]) is None


def test_the_controller_builds_without_a_backend(monkeypatch):
    """MidiIOController used to raise straight out of __init__."""
    from jdxi_editor.midi.io.controller import MidiIOController

    monkeypatch.setattr(rtmidi, "MidiIn", _raise)
    monkeypatch.setattr(rtmidi, "MidiOut", _raise)

    controller = MidiIOController(parent=None)
    assert controller.midi_in.get_ports() == []
    assert controller.midi_out.get_ports() == []
    assert controller.current_in_port is None
    assert controller.current_out_port is None


def test_the_external_controller_builds_without_a_backend(monkeypatch):
    """The controller probe is built in __init__ too, and also used to raise."""
    from jdxi_editor.midi.io.external_controller import ExternalControllerInput

    monkeypatch.setattr(rtmidi, "MidiIn", _raise)
    monkeypatch.setattr(rtmidi, "MidiOut", _raise)

    external = ExternalControllerInput(None)
    # The probe is a stand-in, so there is nothing to list and nothing to open
    assert external.available_ports() == []
    assert external.port_names == []
    assert external.port_name is None
