"""
SysEx request pacing and echo suppression (no MIDI hardware).

- the shared queue sends one RQ1 at a time, waits for its reply, and drops
  duplicates
- data received from the JD-Xi is not written back to it
- received pitch envelope times reach the sliders as MIDI values
"""

import json
import os
import sys
import threading
import time
import unittest
from unittest.mock import Mock

sys.path.insert(0, os.path.abspath("."))

from PySide6.QtWidgets import QApplication

from jdxi_editor.midi.io.echo_guard import applying_device_data, is_device_echo
from jdxi_editor.midi.io.device import device_for
from jdxi_editor.midi.io.request_queue import SysExRequestQueue

_RQ1_ANALOG = "F0 41 10 00 00 00 0E 11 19 42 00 00 00 00 00 40 65 F7"
_RQ1_DIGITAL1 = "F0 41 10 00 00 00 0E 11 19 01 00 00 00 00 00 40 26 F7"
_DT1_ANALOG = bytes.fromhex("F0 41 10 00 00 00 0E 12 19 42 00 00 01 25 F7")
_DT1_DIGITAL1 = bytes.fromhex("F0 41 10 00 00 00 0E 12 19 01 00 00 01 66 F7")
_CC = bytes([0xB0, 7, 100])

# Digital 1 partial 3 as sent by the JD-Xi: Pitch Env Attack/Decay (07/08) = 10
_DT1_D1_PARTIAL3 = (
    "F0 41 10 00 00 00 0E 12 19 01 22 00 00 00 00 40 40 00 00 0A 0A 40 01 01 7F 40 "
    "40 00 00 24 00 00 40 64 53 00 00 7F 00 40 00 51 00 11 00 00 40 40 40 40 00 58 "
    "00 11 7F 00 50 40 40 40 49 4A 40 40 01 00 00 00 0E 00 00 52 40 07 F7"
)


def _hex(data) -> str:
    return " ".join(f"{b:02X}" for b in data)


def _wait_for(predicate, timeout=1.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.005)
    return predicate()


class TestRequestQueue(unittest.TestCase):
    def setUp(self):
        self.sent = []
        self.queue = SysExRequestQueue(
            lambda data: self.sent.append(_hex(data)),
            reply_timeout=2.0,
            reply_gap=0.0,
            message_gap=0.0,
        )

    def test_duplicate_requests_are_sent_once(self):
        self.assertEqual(self.queue.submit([_RQ1_ANALOG, _RQ1_ANALOG, _RQ1_ANALOG]), 1)
        self.assertTrue(_wait_for(lambda: len(self.sent) == 1))
        self.queue.submit([_RQ1_ANALOG])  # from another editor, still awaiting reply
        self.queue.notify_reply(_DT1_ANALOG)
        self.assertTrue(self.queue.wait_idle(1.0))
        self.assertEqual(self.sent, [_RQ1_ANALOG])

    def test_next_request_waits_for_the_reply(self):
        self.queue.submit([_RQ1_ANALOG, _RQ1_DIGITAL1])
        self.assertTrue(_wait_for(lambda: len(self.sent) == 1))
        time.sleep(0.05)
        self.assertEqual(len(self.sent), 1)  # JD-Xi still answering the first
        self.queue.notify_reply(_DT1_DIGITAL1)  # reply for another address
        time.sleep(0.05)
        self.assertEqual(len(self.sent), 1)
        self.queue.notify_reply(_DT1_ANALOG)
        self.assertTrue(_wait_for(lambda: len(self.sent) == 2))
        self.assertEqual(self.sent, [_RQ1_ANALOG, _RQ1_DIGITAL1])

    def test_request_can_be_sent_again_after_its_reply(self):
        self.queue.submit([_RQ1_ANALOG])
        self.assertTrue(_wait_for(lambda: len(self.sent) == 1))
        self.queue.notify_reply(_DT1_ANALOG)
        self.assertTrue(self.queue.wait_idle(1.0))
        self.queue.submit([_RQ1_ANALOG])
        self.assertTrue(_wait_for(lambda: len(self.sent) == 2))

    def test_unanswered_request_times_out(self):
        queue = SysExRequestQueue(
            lambda data: self.sent.append(_hex(data)), reply_timeout=0.05, reply_gap=0.0
        )
        queue.submit([_RQ1_ANALOG, _RQ1_DIGITAL1])
        self.assertTrue(_wait_for(lambda: len(self.sent) == 2))

    def test_other_messages_are_sent_in_order_without_deduplication(self):
        self.queue.submit([_CC, _CC, _DT1_ANALOG])
        self.assertTrue(self.queue.wait_idle(1.0))
        self.assertEqual(self.sent, [_hex(_CC), _hex(_CC), _hex(_DT1_ANALOG)])

    def test_clear_drops_unsent_requests(self):
        self.queue.submit([_RQ1_ANALOG, _CC, _DT1_ANALOG])
        self.queue.clear()
        self.assertTrue(self.queue.wait_idle(1.0))
        self.assertLessEqual(len(self.sent), 1)  # at most the one already sent
        self.assertEqual(self.queue.submit([_RQ1_ANALOG]), 1)  # can queue it again

    def test_helper_shares_one_queue(self):
        helper = Mock(spec=["send_raw_message"])
        self.assertIs(device_for(helper).requests, device_for(helper).requests)


class TestEchoGuard(unittest.TestCase):
    def test_only_dt1_inside_the_scope_is_an_echo(self):
        self.assertFalse(is_device_echo(_DT1_ANALOG))
        with applying_device_data():
            self.assertTrue(is_device_echo(_DT1_ANALOG))
            self.assertFalse(is_device_echo(bytes.fromhex(_RQ1_ANALOG)))
            self.assertFalse(is_device_echo(_CC))
        self.assertFalse(is_device_echo(_DT1_ANALOG))

    def test_scope_is_per_thread(self):
        results = []
        with applying_device_data():
            worker = threading.Thread(target=lambda: results.append(is_device_echo(_DT1_ANALOG)))
            worker.start()
            worker.join()
        self.assertEqual(results, [False])


class TestDeviceDataNotWrittenBack(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        from jdxi_editor.midi.io.helper import MidiIOHelper

        cls.helper = MidiIOHelper()

    def setUp(self):
        self.out = Mock()
        self.out.is_port_open = Mock(return_value=True)
        self._saved_out = self.helper.midi_out
        self.helper.midi_out = self.out

    def tearDown(self):
        self.helper.midi_out = self._saved_out

    def test_dt1_sent_by_a_sysex_listener_is_dropped(self):
        def listener(_payload):
            self.helper.send_raw_message(_DT1_ANALOG)

        self.helper.midi_sysex_json.connect(listener)
        try:
            self.helper._device_sysex_json.emit(json.dumps({"ADDRESS": "12194200"}))
            self.app.processEvents()
        finally:
            self.helper.midi_sysex_json.disconnect(listener)
        self.out.send_message.assert_not_called()

    def test_user_edits_are_still_sent(self):
        self.assertTrue(self.helper.send_raw_message(_DT1_ANALOG))
        self.out.send_message.assert_called_once()


class TestDigitalPitchEnvFromDevice(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_pitch_env_times_keep_the_received_midi_value(self):
        from jdxi_editor.midi.data.digital.oscillator import DigitalOscillatorWidgetTypes
        from jdxi_editor.midi.data.parameter.digital import DigitalPartialParam
        from jdxi_editor.midi.sysex.parser.sysex import JDXiSysExParser
        from jdxi_editor.ui.editors.digital.editor import DigitalSynthEditor

        sent = []
        helper = Mock()
        helper.send_midi_message = Mock(
            side_effect=lambda m: sent.append(m.to_message_list()) or True
        )
        editor = DigitalSynthEditor(
            midi_helper=helper, preset_helper=Mock(), synth_number=1, parent=None
        )
        try:
            sent.clear()
            parsed = JDXiSysExParser().parse_bytes(bytes.fromhex(_DT1_D1_PARTIAL3))
            editor.dispatch_sysex_to_area(json.dumps(parsed))
            pitch_env = editor.partial_editors[3].oscillator_tab.widget_for(
                DigitalOscillatorWidgetTypes.PITCH_ENV
            )
            for param in (
                DigitalPartialParam.OSC_PITCH_ENV_ATTACK_TIME,
                DigitalPartialParam.OSC_PITCH_ENV_DECAY_TIME,
            ):
                self.assertEqual(pitch_env.controls[param].slider.value(), 10)
            # Anything the widgets emit carries the received value, not 127
            for message in sent:
                if list(message[8:11]) == [0x19, 0x01, 0x22] and message[11] in (7, 8):
                    self.assertEqual(message[12], 10)
        finally:
            editor.close()
            editor.deleteLater()


if __name__ == "__main__":
    unittest.main()
