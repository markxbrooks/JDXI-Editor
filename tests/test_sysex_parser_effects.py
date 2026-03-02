#!/usr/bin/env python3
"""
Unit tests for SysEx parser effects routing.

Verifies that parse_sysex correctly maps LMB bytes to EFFECT_1, EFFECT_2,
DELAY, REVERB for TEMPORARY_PROGRAM area (address 18 00 xx 00).

Run: pytest tests/test_sysex_parser_effects.py -v
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.abspath("."))

from jdxi_editor.midi.sysex.parser.utils import parse_sysex


def _make_sysex_bytes(lmb: int, payload_len: int = 50) -> bytes:
    """Build minimal DT1-style SysEx: F0 41 10 00 00 00 0E 12 18 00 LMB 00 [payload]."""
    header = bytes([0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x12])
    address = bytes([0x18, 0x00, lmb & 0xFF, 0x00])
    payload = bytes([0x40] * payload_len)  # 0x40 = 64, neutral value
    return header + address + payload


class TestSysexParserEffects(unittest.TestCase):
    """Test suite for SysEx parser effects section mapping."""

    def test_parse_effect1_produces_effect1_synth_tone(self):
        """Test that address 18 00 02 00 produces SYNTH_TONE=EFFECT_1."""
        data = _make_sysex_bytes(0x02)
        parsed = parse_sysex(data)
        self.assertEqual(
            parsed.get("SYNTH_TONE"),
            "EFFECT_1",
            "LMB=0x02 should map to EFFECT_1",
        )
        self.assertEqual(parsed.get("TEMPORARY_AREA"), "TEMPORARY_PROGRAM")

    def test_parse_effect2_produces_effect2_synth_tone(self):
        """Test that address 18 00 04 00 produces SYNTH_TONE=EFFECT_2."""
        data = _make_sysex_bytes(0x04)
        parsed = parse_sysex(data)
        self.assertEqual(
            parsed.get("SYNTH_TONE"),
            "EFFECT_2",
            "LMB=0x04 should map to EFFECT_2",
        )

    def test_parse_delay_produces_delay_synth_tone(self):
        """Test that address 18 00 06 00 produces SYNTH_TONE=DELAY."""
        data = _make_sysex_bytes(0x06)
        parsed = parse_sysex(data)
        self.assertEqual(
            parsed.get("SYNTH_TONE"),
            "DELAY",
            "LMB=0x06 should map to DELAY",
        )

    def test_parse_reverb_produces_reverb_synth_tone(self):
        """Test that address 18 00 08 00 produces SYNTH_TONE=REVERB."""
        data = _make_sysex_bytes(0x08)
        parsed = parse_sysex(data)
        self.assertEqual(
            parsed.get("SYNTH_TONE"),
            "REVERB",
            "LMB=0x08 should map to REVERB",
        )

    def test_parse_delay_includes_delay_params(self):
        """Test that DELAY SysEx produces expected param keys."""
        data = _make_sysex_bytes(0x06, payload_len=100)
        parsed = parse_sysex(data)
        self.assertIn("DELAY_LEVEL", parsed)
        self.assertIn("DELAY_ON_OFF", parsed)

    def test_parse_reverb_includes_reverb_params(self):
        """Test that REVERB SysEx produces expected param keys."""
        data = _make_sysex_bytes(0x08, payload_len=100)
        parsed = parse_sysex(data)
        self.assertIn("REVERB_LEVEL", parsed)
        self.assertIn("REVERB_ON_OFF", parsed)


if __name__ == "__main__":
    unittest.main()
