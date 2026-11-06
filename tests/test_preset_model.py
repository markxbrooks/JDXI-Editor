"""Unit tests for Preset domain model and load_presets boundary."""

import unittest

from jdxi_editor.midi.bank import Bank
from jdxi_editor.ui.preset.model import Preset, ProgramChangeSelection, load_presets
from jdxi_editor.ui.preset.source import PresetSource


class TestPreset(unittest.TestCase):
    def test_midi_address(self) -> None:
        preset = Preset(
            name="JP8 Strings1",
            bank=Bank(msb=95, lsb=64),
            program=0,
            id="001",
        )
        self.assertEqual(preset.midi_address, (95, 64, 0))

    def test_program_out_of_range(self) -> None:
        with self.assertRaises(ValueError):
            Preset(name="x", bank=Bank(), program=128)
        with self.assertRaises(ValueError):
            Preset(name="x", bank=Bank(), program=-1)


class TestProgramChangeSelection(unittest.TestCase):
    def test_delegates_bank_program_name(self) -> None:
        preset = Preset(
            name="Warm",
            bank=Bank(msb=87, lsb=0),
            program=12,
        )
        selection = ProgramChangeSelection(channel=2, preset=preset)
        self.assertEqual(selection.bank, preset.bank)
        self.assertEqual(selection.program, 12)
        self.assertEqual(selection.name, "Warm")

    def test_channel_out_of_range(self) -> None:
        preset = Preset(name="x", bank=Bank(), program=0)
        with self.assertRaises(ValueError):
            ProgramChangeSelection(channel=16, preset=preset)


class TestLoadPresets(unittest.TestCase):
    def test_digital_first_preset_wire_address(self) -> None:
        presets = load_presets(PresetSource.DIGITAL)
        self.assertGreater(len(presets), 0)
        first = presets[0]
        self.assertEqual(first.name, "JP8 Strings1")
        self.assertEqual(first.source, PresetSource.DIGITAL)
        self.assertEqual(first.midi_address, (95, 64, 0))

    def test_digital_preset_131_uses_lsb_65(self) -> None:
        presets = load_presets(PresetSource.DIGITAL)
        # Catalog PC 131 → wire Bank(95, 65), program 2
        match = next(p for p in presets if p.id == "131" or p.id.lstrip("0") == "131")
        self.assertEqual(match.bank, Bank(msb=95, lsb=65))
        self.assertEqual(match.program, 2)
        self.assertEqual(match.preset_number, 131)

    def test_analog_and_drums_load(self) -> None:
        analog = load_presets(PresetSource.ANALOG)
        drums = load_presets(PresetSource.DRUMS)
        self.assertGreater(len(analog), 0)
        self.assertGreater(len(drums), 0)
        self.assertTrue(all(isinstance(p, Preset) for p in analog))
        self.assertTrue(all(p.source == PresetSource.DRUMS for p in drums))


if __name__ == "__main__":
    unittest.main()
