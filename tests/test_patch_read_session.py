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


if __name__ == "__main__":
    unittest.main()
