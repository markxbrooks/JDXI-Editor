"""Tests for MIDI selection info resolvers."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("."))

from jdxi_editor.core.jdxi import JDXi
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
        self.assertEqual(info.cc0, 95)
        self.assertEqual(info.cc32, 65)
        self.assertEqual(info.midi_pc, 54)
        self.assertEqual(info.preset_pc, 55)

    def test_digital_tone_248(self):
        info = resolve_tone_midi(
            248,
            self.digital_list,
            channel=MidiChannel.DIGITAL_SYNTH_1,
        )
        self.assertIsNotNone(info)
        self.assertEqual(info.midi_pc, 119)
        self.assertEqual(info.preset_pc, 120)

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
        self.assertEqual(info.preset_pc, 1)

    def test_program_a01(self):
        info = resolve_program_midi("A", 1)
        self.assertIsNotNone(info)
        self.assertEqual(info.channel, MidiChannel.PROGRAM)
        self.assertEqual(info.cc0, 85)
        self.assertEqual(info.cc32, 64)
        self.assertEqual(info.midi_pc, 0)
        self.assertEqual(info.program_id, "A01")

    def test_program_e05(self):
        info = resolve_program_midi_from_id("E05")
        self.assertIsNotNone(info)
        self.assertEqual(info.cc0, 85)
        self.assertEqual(info.cc32, 0)
        self.assertEqual(info.midi_pc, 4)
        self.assertEqual(info.program_id, "E05")

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
        self.assertIn("Ch 3", info.channel_display)
        self.assertEqual(info.midi_pc, 54)

    def test_format_none(self):
        self.assertEqual(format_midi_wire_info(None), "MIDI  —")

    def test_format_includes_program_id(self):
        info = resolve_program_midi_from_id("A13")
        text = format_midi_wire_info(info)
        self.assertIn("A13", text)
        self.assertIn("CC0: 85", text)


if __name__ == "__main__":
    unittest.main()
