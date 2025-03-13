"""
Unit tests for the parse_sysex function.

This module tests the parsing of JD-Xi SysEx messages, ensuring that
tone parameters are correctly extracted from valid and edge-case inputs.
"""

import unittest

from jdxi_editor.midi.parsers import parse_sysex


class TestParseSysex(unittest.TestCase):
    def setUp(self):
        self.sysex_message = bytes([
            0xF0, 0x41, 0x10, 0x00, 0x00, 0x0E, 0x12, 0x01,
            0x00, 0x00, 0x00, 0x01, 0x54, 0x00, 0x00, 0x55,
            0x40, 0x00, 0x00, 0x00, 0x40, 0x00, 0x7F, 0x01,
            0x54, 0x00, 0x00, 0x55, 0x40, 0x00, 0x64, 0x40,
            0x40, 0x00, 0x7F, 0x01, 0x01, 0x01, 0x01, 0x01,
            0x01, 0x40, 0x40, 0x00, 0x00, 0x00, 0x05, 0x05,
            0x00, 0x01, 0x00, 0x02, 0x40, 0x00, 0x64, 0x00,
            0x00, 0x01, 0x00, 0x00, 0x01, 0x00, 0x64, 0x7F,
            0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0x6B, 0xF7,
        ])

        self.sysex_message_trance_pad = bytes([
            0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x1A,
            0x01, 0x00, 0x00, 0x00, 0x54, 0x72, 0x61, 0x6E,
            0x63, 0x65, 0x20, 0x50, 0x61, 0x64, 0x00, 0x64,
            0x32, 0x02, 0x00, 0x00, 0x00, 0x01, 0x55, 0x40,
            0x00, 0x00, 0x40, 0x7F, 0x01, 0x64, 0xF7,
        ])

    def test_parse_sysex_valid_message(self):
        parsed_data = parse_sysex(self.sysex_message)

        self.assertIsInstance(parsed_data, dict)
        self.assertIn("JD_XI_HEADER", parsed_data)
        self.assertIn("ADDRESS", parsed_data)
        self.assertIn("TEMPORARY_AREA", parsed_data)
        self.assertIn("SYNTH_TONE", parsed_data)
        self.assertIn("TONE_NAME", parsed_data)

        self.assertEqual(parsed_data["TEMPORARY_AREA"], "Unknown")  # Adjust based on expected parsing
        self.assertEqual(parsed_data["SYNTH_TONE"], "TONE_COMMON")  # Adjust if necessary

    def test_parse_sysex_insufficient_data(self):
        insufficient_data = bytes([0xF0, 0x41])  # Too short
        parsed_data = parse_sysex(insufficient_data)

        self.assertEqual(parsed_data["TEMPORARY_AREA"], "Unknown")
        self.assertEqual(parsed_data["SYNTH_TONE"], "Unknown")

    def test_parse_sysex_trance_pad(self):
        parsed_data = parse_sysex(self.sysex_message_trance_pad)

        self.assertIsInstance(parsed_data, dict)
        self.assertIn("TONE_NAME", parsed_data)
        self.assertEqual(parsed_data["TONE_NAME"], "Trance Pad")


if __name__ == "__main__":
    unittest.main()
