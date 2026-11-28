"""
The connection to the JD-Xi in one place.

- no ports: OFFLINE; ports open: asked who it is (DETECTED → VERIFYING)
- only a Roland JD-Xi's Identity Reply makes it ONLINE
- a device that does not answer, or another device, never gets ONLINE
- closing a port: OFFLINE at once, also from ONLINE
- unanswered requests: UNSTABLE; a whole reading: ONLINE again
- an Identity Reply through the real MIDI input reaches the connection
"""

from __future__ import annotations

import os
import sys
from unittest.mock import Mock

import mido
import pytest
from PySide6.QtWidgets import QApplication

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from jdxi_editor.midi.io import connection as conn  # noqa: E402

JDXI_REPLY = [0x7E, 0x10, 0x06, 0x02, 0x41, 0x0E, 0x03, 0x00, 0x00, 0x00, 0x03, 0x00, 0x00]
OTHER_REPLY = [0x7E, 0x10, 0x06, 0x02, 0x42, 0x1A, 0x01, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00]  # not Roland


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


class Helper:
    """Two ports and an Identity Request that is only counted."""

    def __init__(self, open_=True):
        self.midi_out = Mock()
        self.midi_in = Mock()
        self.set_open(open_)
        self.asked = 0

    def set_open(self, value: bool) -> None:
        self.midi_out.is_port_open.return_value = value
        self.midi_in.is_port_open.return_value = value

    def send_identity_request(self) -> bool:
        self.asked += 1
        return True


def _connection(helper):
    return conn.Connection(helper, poll_ms=0)  # polled by hand


def test_no_ports_is_offline(app):
    helper = Helper(open_=False)
    c = _connection(helper)
    c.poll()
    assert c.state == conn.OFFLINE and not c.can_talk() and helper.asked == 0


def test_only_a_jdxi_identity_makes_it_online(app):
    helper = Helper()
    c = _connection(helper)
    states = []
    c.changed.connect(states.append)
    c.poll()
    assert c.state == conn.VERIFYING and helper.asked == 1 and not c.can_talk()
    c.identity_reply(OTHER_REPLY)  # another device: never ONLINE (SD-17)
    assert c.state == conn.VERIFYING
    c.identity_reply(JDXI_REPLY)
    assert c.state == conn.ONLINE and c.can_talk() and c.verified()
    assert states == [conn.DETECTED, conn.VERIFYING, conn.ONLINE]


def test_a_silent_device_is_asked_again_but_not_too_often(app, monkeypatch):
    helper = Helper()
    c = _connection(helper)
    now = [100.0]
    monkeypatch.setattr("time.monotonic", lambda: now[0])
    c.poll()
    c.poll()
    assert helper.asked == 1  # within the retry time
    now[0] += conn.VERIFY_RETRY_MS / 1000 + 0.1
    c.poll()
    assert helper.asked == 2 and c.state == conn.VERIFYING


def test_a_closed_port_is_offline_at_once(app):
    helper = Helper()
    c = _connection(helper)
    c.poll()
    c.identity_reply(JDXI_REPLY)
    assert c.can_talk()
    helper.set_open(False)
    c.poll()
    assert c.state == conn.OFFLINE and not c.can_talk()
    helper.set_open(True)
    c.poll()
    assert c.state == conn.VERIFYING  # asked again: it may be another device now


def test_unanswered_requests_make_it_unstable_until_a_whole_reading(app):
    helper = Helper()
    c = _connection(helper)
    c.poll()
    c.identity_reply(JDXI_REPLY)
    c.request_unanswered()
    assert c.state == conn.ONLINE
    c.request_unanswered()
    assert c.state == conn.UNSTABLE and c.can_talk() and not c.verified()
    c.reading_complete()
    assert c.state == conn.ONLINE and c.verified()


def test_the_identity_reply_through_the_midi_input_reaches_the_connection(app):
    from jdxi_editor.midi.io.helper import MidiIOHelper

    helper = MidiIOHelper()
    saved = helper.midi_out, helper.midi_in
    try:
        for name in ("midi_out", "midi_in"):
            port = Mock()
            port.is_port_open.return_value = True
            setattr(helper, name, port)
        c = conn.connection_for(helper)
        c.set_state_for_tests(conn.VERIFYING)
        helper._handle_midi_message(mido.Message("sysex", data=JDXI_REPLY))
        QApplication.processEvents()
        assert c.state == conn.ONLINE and conn.connection_for(helper) is c
    finally:
        helper.midi_out, helper.midi_in = saved
        c.set_state_for_tests(conn.OFFLINE)


def test_a_jdxi_switched_off_goes_offline_and_comes_back(app, monkeypatch):
    """Switched off, the JD-Xi's ports stayed open: the badge said «JD-Xi connected»."""
    monkeypatch.setattr(conn, "SILENCE_CHECK", True)
    helper = Helper()
    c = _connection(helper)
    now = [100.0]
    monkeypatch.setattr("time.monotonic", lambda: now[0])
    c.poll()
    c.identity_reply(JDXI_REPLY)
    assert c.state == conn.ONLINE
    asked = helper.asked
    now[0] += 1
    c.heard()  # it talks: nothing asked
    now[0] += conn.SILENT_ASK_S - 0.5
    c.poll()
    assert helper.asked == asked and c.state == conn.ONLINE
    now[0] += 1  # silent: asked who it is
    c.poll()
    assert helper.asked == asked + 1 and c.state == conn.ONLINE
    now[0] += conn.LOST_AFTER_S  # no answer: off-line, ports still open
    c.poll()
    assert c.state == conn.OFFLINE and not c.can_talk()
    now[0] += conn.VERIFY_RETRY_MS / 1000 + 0.1
    c.poll()  # asked again, quietly: still OFFLINE, not «verifying»
    assert c.state == conn.OFFLINE and helper.asked == asked + 2
    c.identity_reply(JDXI_REPLY)  # switched on again
    assert c.state == conn.ONLINE
    now[0] += 1
    c.poll()
    assert c.state == conn.ONLINE


def test_any_midi_from_the_jdxi_counts_as_heard(app):
    from jdxi_editor.midi.io.input_handler import MidiInHandler

    c = _connection(Helper())
    handler = Mock()
    handler._jdxi_connection = c
    handler._handle_midi_message = Mock()
    MidiInHandler.midi_callback(handler, ([0xF8], 0.0), None)
    assert c._last_heard is not None
