"""Tests for MIDI selection info resolvers."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("."))

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.bank import Bank
from jdxi_editor.midi.channel.channel import MidiChannel
from jdxi_editor.ui.midi.selection_info import (
    format_midi_wire_info,
    resolve_program_midi,
    resolve_program_midi_from_id,
    resolve_tone_midi,
    resolve_tone_midi_for_channel,
)


class TestMidiSelectionInfo(unittest.TestCase):
    """Resolver tests for program and tone wire-format display."""

    @classmethod
    def setUpClass(cls):
        cls.digital_list = JDXi.UI.Preset.Digital.LIST
        cls.analog_list = JDXi.UI.Preset.Analog.PROGRAM_CHANGE

    def test_digital_tone_183(self):
        info = resolve_tone_midi(
            183,
            self.digital_list,
            channel=MidiChannel.DIGITAL_SYNTH_1,
            channel_label="Digital 1",
        )
        self.assertIsNotNone(info)
        self.assertEqual(info.bank, Bank(msb=95, lsb=65))
        self.assertEqual(info.cc0, 95)
        self.assertEqual(info.cc32, 65)
        self.assertEqual(info.midi_pc, 54)
        self.assertEqual(info.program, 54)

    def test_digital_tone_248(self):
        info = resolve_tone_midi(
            248,
            self.digital_list,
            channel=MidiChannel.DIGITAL_SYNTH_1,
        )
        self.assertIsNotNone(info)
        self.assertEqual(info.midi_pc, 119)

    def test_digital_tone_001(self):
        info = resolve_tone_midi(
            1,
            self.digital_list,
            channel=MidiChannel.DIGITAL_SYNTH_1,
        )
        self.assertIsNotNone(info)
        self.assertEqual(info.cc0, 95)
        self.assertEqual(info.cc32, 64)
        self.assertEqual(info.midi_pc, 0)

    def test_program_a01(self):
        info = resolve_program_midi("A", 1)
        self.assertIsNotNone(info)
        self.assertEqual(info.channel, MidiChannel.PROGRAM)
        self.assertEqual(info.cc0, 85)
        self.assertEqual(info.cc32, 64)
        self.assertEqual(info.midi_pc, 0)

    def test_program_e05(self):
        info = resolve_program_midi_from_id("E05")
        self.assertIsNotNone(info)
        self.assertEqual(info.cc0, 85)
        self.assertEqual(info.cc32, 0)
        self.assertEqual(info.midi_pc, 4)

    def test_program_h64(self):
        info = resolve_program_midi_from_id("H64")
        self.assertIsNotNone(info)
        self.assertEqual(info.cc0, 85)
        self.assertEqual(info.cc32, 1)
        self.assertEqual(info.midi_pc, 127)

    def test_invalid_program_id(self):
        self.assertIsNone(resolve_program_midi_from_id(""))
        self.assertIsNone(resolve_program_midi_from_id("X99"))
        self.assertIsNone(resolve_program_midi("Z", 1))

    def test_invalid_tone_id(self):
        self.assertIsNone(
            resolve_tone_midi(999, self.digital_list, channel=MidiChannel.DIGITAL_SYNTH_1)
        )
        self.assertIsNone(
            resolve_tone_midi("abc", self.digital_list, channel=MidiChannel.DIGITAL_SYNTH_1)
        )

    def test_cheat_channel_override(self):
        info = resolve_tone_midi_for_channel(
            183,
            self.digital_list,
            MidiChannel.ANALOG_SYNTH,
            "Analog",
        )
        self.assertIsNotNone(info)
        self.assertEqual(info.channel, MidiChannel.ANALOG_SYNTH)
        self.assertTrue(
            "Ch.3" in info.channel_display or "Ch 3" in info.channel_display
        )
        self.assertEqual(info.midi_pc, 54)

    def test_format_none(self):
        self.assertEqual(format_midi_wire_info(None), "MIDI  —")

    def test_format_wire_values(self):
        info = resolve_program_midi_from_id("A13")
        text = format_midi_wire_info(info)
        self.assertIn("CC#0 85", text)
        self.assertIn("PC ", text)


class TestMidiSelectionValidation(unittest.TestCase):
    """Validation core: byte build/parse round-trip and compare."""

    @classmethod
    def setUpClass(cls):
        cls.digital_list = JDXi.UI.Preset.Digital.LIST

    def test_build_parse_round_trip_tone_183(self):
        from jdxi_editor.midi.validation.selection import (
            build_bank_select_pc_bytes,
            compare_wire_info,
            parse_bank_select_pc_sequence,
        )

        expected = resolve_tone_midi(
            183,
            self.digital_list,
            channel=MidiChannel.DIGITAL_SYNTH_1,
        )
        self.assertIsNotNone(expected)
        messages = build_bank_select_pc_bytes(
            expected.channel, expected.cc0, expected.cc32, expected.midi_pc
        )
        actual = parse_bank_select_pc_sequence(messages)
        self.assertIsNotNone(actual)
        result = compare_wire_info(expected, actual)
        self.assertTrue(result.ok, result.diff_fields)

    def test_compare_detects_wrong_lsb(self):
        from jdxi_editor.midi.validation.selection import (
            ValidationResult,
            wire_info_from_bank_pc,
        )

        expected = wire_info_from_bank_pc(2, 95, 65, 54)
        actual = wire_info_from_bank_pc(2, 95, 64, 54)
        result = ValidationResult.compare(expected, actual)
        self.assertFalse(result.ok)
        self.assertIn("bank", result.diff_fields)

    def test_compare_detects_wrong_channel(self):
        from jdxi_editor.midi.validation.selection import (
            compare_wire_info,
            wire_info_from_bank_pc,
        )

        expected = wire_info_from_bank_pc(2, 95, 65, 54)
        actual = wire_info_from_bank_pc(1, 95, 65, 54)
        result = compare_wire_info(expected, actual)
        self.assertFalse(result.ok)
        self.assertIn("channel", result.diff_fields)

    def test_program_e05_build_matches_resolver(self):
        from jdxi_editor.midi.validation.selection import (
            build_bank_select_pc_bytes,
            parse_bank_select_pc_sequence,
            validate_bank_select_pc_send,
        )

        expected = resolve_program_midi_from_id("E05")
        self.assertIsNotNone(expected)
        messages = build_bank_select_pc_bytes(
            expected.channel, expected.cc0, expected.cc32, expected.midi_pc
        )
        parsed = parse_bank_select_pc_sequence(messages)
        self.assertIsNotNone(parsed)
        result = validate_bank_select_pc_send(
            expected.channel,
            expected.cc0,
            expected.cc32,
            expected.midi_pc,
            expected,
        )
        self.assertIsNotNone(result)
        self.assertTrue(result.ok)

    def test_automation_insert_bytes_match_cheat_load(self):
        from jdxi_editor.midi.validation.selection import build_bank_select_pc_bytes

        cheat = resolve_tone_midi_for_channel(
            183,
            self.digital_list,
            MidiChannel.ANALOG_SYNTH,
            "Analog",
        )
        self.assertIsNotNone(cheat)
        self.assertEqual((cheat.cc0, cheat.cc32, cheat.midi_pc), (95, 65, 54))
        automation_bytes = build_bank_select_pc_bytes(
            MidiChannel.ANALOG_SYNTH, cheat.cc0, cheat.cc32, cheat.midi_pc
        )
        cheat_bytes = build_bank_select_pc_bytes(
            cheat.channel, cheat.cc0, cheat.cc32, cheat.midi_pc
        )
        self.assertEqual(automation_bytes, cheat_bytes)


if __name__ == "__main__":
    unittest.main()
