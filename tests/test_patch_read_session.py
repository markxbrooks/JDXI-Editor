"""Unit tests for coordinated patch ReadSession (no MIDI hardware)."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("."))

from jdxi_editor.midi.sysex.request.read_session import (
    ReadResult,
    ReadSectionResult,
    SectionStatus,
    address_from_rq1_hex,
    label_for_address,
    normalize_address,
    sections_from_requests,
)

# Minimal RQ1 samples (no MidiRequests import — avoids heavy UI deps in unit tests)
_RQ1_ANALOG = (
    "F0 41 10 00 00 00 0E 11 19 42 00 00 00 00 00 40 65 F7"
)
_RQ1_DIGITAL1 = (
    "F0 41 10 00 00 00 0E 11 19 01 00 00 00 00 00 40 26 F7"
)
_RQ1_EFX1 = (
    "F0 41 10 00 00 00 0E 11 18 00 02 00 00 00 01 11 54 F7"
)
_RQ1_PROGRAM = (
    "F0 41 10 00 00 00 0E 11 18 00 00 00 00 00 00 40 28 F7"
)


class TestAddressFromRq1(unittest.TestCase):
    def test_analog_address(self):
        self.assertEqual(address_from_rq1_hex(_RQ1_ANALOG), "19420000")

    def test_digital1_common(self):
        self.assertEqual(address_from_rq1_hex(_RQ1_DIGITAL1), "19010000")

    def test_effect1(self):
        self.assertEqual(address_from_rq1_hex(_RQ1_EFX1), "18000200")

    def test_program_common(self):
        self.assertEqual(address_from_rq1_hex(_RQ1_PROGRAM), "18000000")

    def test_missing_command_raises(self):
        with self.assertRaises(ValueError):
            address_from_rq1_hex("F0 41 10 F7")


class TestSectionsAndResult(unittest.TestCase):
    def test_sections_from_requests(self):
        sections = sections_from_requests([_RQ1_ANALOG, _RQ1_DIGITAL1])
        self.assertEqual(len(sections), 2)
        self.assertEqual(sections[0].address, "19420000")
        self.assertEqual(sections[0].status, SectionStatus.PENDING)
        self.assertIn("Analog", sections[0].label)

    def test_read_result_complete(self):
        sections = sections_from_requests([_RQ1_ANALOG])
        self.assertFalse(ReadResult(sections=sections).complete)
        sections[0].status = SectionStatus.OK
        self.assertTrue(ReadResult(sections=sections).complete)

    def test_read_result_partial(self):
        sections = sections_from_requests([_RQ1_ANALOG, _RQ1_DIGITAL1])
        sections[0].status = SectionStatus.OK
        sections[1].status = SectionStatus.TIMEOUT
        result = ReadResult(sections=sections)
        self.assertFalse(result.complete)
        self.assertEqual(result.ok_count, 1)
        self.assertIn("timeout", result.summary())

    def test_normalize_address(self):
        self.assertEqual(normalize_address("19 42 00 00"), "19420000")
        self.assertEqual(label_for_address("19420000"), "Analog")
        self.assertIsInstance(
            ReadSectionResult("Analog", "19420000", _RQ1_ANALOG),
            ReadSectionResult,
        )


# --- Matching real hardware replies --------------------------------------------

import json
import time

import mido
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication

from jdxi_editor.midi.sysex.request.read_session import (
    address_from_dt1_bytes,
    address_from_parsed_json,
    start_read_session,
)

_APP = QApplication.instance() or QApplication([])


def _dt1(address: bytes, payload_len: int = 8) -> bytes:
    """A JD-Xi DT1 reply as the hardware sends it (with F0/F7)."""
    body = bytes([0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x12]) + address + bytes(
        [0x40] * payload_len
    )
    checksum = (128 - sum(body[7:]) % 128) % 128
    return bytes([0xF0]) + body + bytes([checksum, 0xF7])


class _FakeHelper(QObject):
    """Stands in for MidiIOHelper: RQ1s go nowhere, replies are emitted by the test."""

    midi_message_incoming = Signal(object)
    midi_sysex_json = Signal(str)

    def __init__(self):
        super().__init__()
        self.sent = []

    def send_raw_message(self, message):
        self.sent.append(bytes(message))
        return True


class _JsonOnlyHelper(QObject):
    midi_sysex_json = Signal(str)

    def send_raw_message(self, message):
        return True


def _pump(seconds=0.05):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        _APP.processEvents()
        time.sleep(0.005)


class TestDt1Matching(unittest.TestCase):
    def test_address_from_dt1_bytes(self):
        reply = _dt1(bytes([0x19, 0x42, 0x00, 0x00]))
        self.assertEqual(address_from_dt1_bytes(reply), "19420000")
        self.assertEqual(address_from_dt1_bytes(reply[1:-1]), "19420000")  # mido data
        rq1 = bytes.fromhex(_RQ1_ANALOG.replace(" ", ""))
        self.assertIsNone(address_from_dt1_bytes(rq1))  # a request, not a reply

    def test_parser_address_is_command_plus_three_bytes(self):
        """Documents why parsed JSON cannot be compared with the RQ1 address directly."""
        from jdxi_editor.midi.sysex.parser.sysex import JDXiSysExParser

        parsed = JDXiSysExParser().parse_bytes(_dt1(bytes([0x19, 0x42, 0x00, 0x00]), 0x40))
        self.assertEqual(parsed["ADDRESS"], "12194200")
        self.assertEqual(address_from_parsed_json(parsed["ADDRESS"]), "19420000")
        self.assertEqual(address_from_parsed_json("19420000"), "19420000")

    def test_hardware_replies_complete_the_read(self):
        helper = _FakeHelper()
        finished = []
        session = start_read_session(
            helper,
            [_RQ1_ANALOG, _RQ1_DIGITAL1, _RQ1_EFX1],
            timeout_ms=2000,
            on_finished=finished.append,
        )
        _pump()
        for address in ([0x19, 0x42, 0, 0], [0x19, 0x01, 0, 0], [0x18, 0x00, 0x02, 0]):
            data = _dt1(bytes(address))
            helper.midi_message_incoming.emit(mido.Message("sysex", data=data[1:-1]))
        _pump()
        self.assertEqual(len(finished), 1)
        self.assertTrue(finished[0].complete, finished[0].summary())
        self.assertFalse(session._connected)
        # The RQ1s go out one at a time through the shared request queue
        from jdxi_editor.midi.io.device import device_for

        self.assertTrue(device_for(helper).requests.wait_idle(2.0))
        self.assertEqual(len(helper.sent), 3)

    def test_loaded_patch_json_is_not_taken_as_a_reply(self):
        """Loading a patch file emits JSON with 4-byte addresses on midi_sysex_json."""
        helper = _FakeHelper()
        finished = []
        start_read_session(helper, [_RQ1_ANALOG], timeout_ms=200, on_finished=finished.append)
        helper.midi_sysex_json.emit(json.dumps({"ADDRESS": "19420000"}))
        _pump(0.4)
        self.assertEqual(finished[0].sections[0].status, SectionStatus.TIMEOUT)

    def test_other_messages_and_other_addresses_are_ignored(self):
        helper = _FakeHelper()
        finished = []
        start_read_session(helper, [_RQ1_ANALOG], timeout_ms=200, on_finished=finished.append)
        helper.midi_message_incoming.emit(mido.Message("note_on", note=60))
        helper.midi_message_incoming.emit(
            mido.Message("sysex", data=_dt1(bytes([0x19, 0x01, 0, 0]))[1:-1])
        )
        _pump(0.4)
        self.assertFalse(finished[0].complete)

    def test_json_fallback_understands_parser_addresses(self):
        helper = _JsonOnlyHelper()
        finished = []
        start_read_session(helper, [_RQ1_ANALOG], timeout_ms=2000, on_finished=finished.append)
        helper.midi_sysex_json.emit(json.dumps({"ADDRESS": "12194200"}))
        _pump()
        self.assertTrue(finished and finished[0].complete)


if __name__ == "__main__":
    unittest.main()
