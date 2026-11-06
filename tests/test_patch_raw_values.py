"""
Patches are saved in raw MIDI values and restored exactly (no MIDI hardware).

- SynthMemory keeps the JD-Xi's bytes from DT1 replies and writes
- a section from memory is saved with its DT1 and loads back byte for byte
- old bundles (display units) are converted to raw values when loaded
- program changes clear the memory; Read from JD-Xi covers every section
"""

import json
import os
import sys
import tempfile
import time
import unittest
import zipfile
from pathlib import Path
from unittest.mock import Mock

sys.path.insert(0, os.path.abspath("."))

import mido
from PySide6.QtWidgets import QApplication

_APP = QApplication.instance() or QApplication([])

from jdxi_editor.midi.data.parameter.analog.address import AnalogParam
from jdxi_editor.midi.data.parameter.digital import DigitalPartialParam as P
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.io.synth_memory import SynthMemory, build_dt1
from jdxi_editor.midi.sysex.patch_bundle import (
    convert_editor_sections,
    section_param_dt1s,
    write_memory_sections,
)
from jdxi_editor.midi.sysex.patch_values import (
    display_to_midi,
    param_class_for_address,
    upgrade_legacy_section,
)
from jdxi_editor.midi.sysex.request.read_session import (
    label_for_address,
    patch_section_requests,
)

# Replies from the JD-Xi (program H1)
_PROGRAM_COMMON = (
    "F0 41 10 00 00 00 0E 12 18 00 00 00 53 4D 41 4C 4C 54 4F 57 4E 20 42 4F 20 20 20 "
    "20 7F 02 0E 0E 00 00 00 01 01 01 01 00 00 00 00 00 00 00 00 00 55 F7"
)
_D1_PARTIAL3 = (
    "F0 41 10 00 00 00 0E 12 19 01 22 00 00 00 00 40 40 00 00 0A 0A 40 01 01 7F 40 "
    "40 00 00 24 00 00 40 64 53 00 00 7F 00 40 00 51 00 11 00 00 40 40 40 40 00 58 "
    "00 11 7F 00 50 40 40 40 49 4A 40 40 01 00 00 00 0E 00 00 52 40 07 F7"
)
_DRUM_COMMON = (
    "F0 41 10 00 00 00 0E 12 19 70 00 00 54 52 2D 36 30 36 20 4B 69 74 20 31 5D 00 "
    "00 00 00 0D 05 F7"
)
_REPLIES = [_PROGRAM_COMMON, _D1_PARTIAL3, _DRUM_COMMON]


class TestSynthMemory(unittest.TestCase):
    def test_reply_is_a_section(self):
        memory = SynthMemory()
        self.assertTrue(memory.record_dt1(bytes.fromhex(_D1_PARTIAL3)))
        self.assertEqual(memory.sections(), [(bytes.fromhex("19012200"), 61)])
        self.assertEqual(
            memory.section_dt1(bytes.fromhex("19012200"), 61), bytes.fromhex(_D1_PARTIAL3)
        )

    def test_parameter_write_updates_a_section(self):
        memory = SynthMemory()
        memory.record_dt1(bytes.fromhex(_D1_PARTIAL3))
        memory.record_dt1(build_dt1(bytes.fromhex("19012207"), [0x40]))  # pitch env attack
        data = memory.read(bytes.fromhex("19012200"), 61)
        self.assertEqual(data[7], 0x40)
        self.assertEqual(len(memory.sections()), 1)  # a 1-byte write is not a section

    def test_section_crossing_a_7_bit_boundary(self):
        memory = SynthMemory()
        start = bytes.fromhex("18000200")
        memory.record_dt1(build_dt1(start, [1] * 145))  # Effect 1: 18 00 02 00..18 00 03 10
        self.assertEqual(memory.read(bytes.fromhex("18000310"), 1), b"\x01")
        self.assertIsNone(memory.read(bytes.fromhex("18000311"), 1))

    def test_not_a_dt1(self):
        rq1 = bytes.fromhex("F0 41 10 00 00 00 0E 11 19 42 00 00 00 00 00 40 65 F7")
        self.assertFalse(SynthMemory().record_dt1(rq1))


class TestDisplayToMidi(unittest.TestCase):
    def test_widget_units(self):
        self.assertEqual(display_to_midi(P.AMP_PAN, -35), 29)
        self.assertEqual(display_to_midi(P.AMP_ENV_ATTACK_TIME, 290), 36)
        self.assertEqual(display_to_midi(P.AMP_ENV_SUSTAIN_LEVEL, 0.39), 50)
        self.assertEqual(display_to_midi(P.OSC_PITCH_ENV_ATTACK_TIME, 402.0), 10)
        self.assertEqual(display_to_midi(AnalogParam.OSC_PITCH_COARSE, 0), 64)

    def test_param_class_from_address(self):
        self.assertIs(param_class_for_address("19420000"), AnalogParam)
        self.assertIs(param_class_for_address("19012100"), P)
        self.assertIsNone(param_class_for_address("02000000"))

    def test_legacy_section_converted_once(self):
        legacy = {"ADDRESS": "19420000", "OSC_PITCH_COARSE": 0, "TONE_NAME_1": 80}
        upgraded = upgrade_legacy_section(legacy)
        self.assertEqual(upgraded["OSC_PITCH_COARSE"], 64)
        self.assertEqual(upgraded["TONE_NAME_1"], 80)  # character codes are raw
        self.assertEqual(upgrade_legacy_section(upgraded), upgraded)


class TestSectionParamMessages(unittest.TestCase):
    def test_raw_values_written_unconverted(self):
        messages = section_param_dt1s(
            {"ADDRESS": "19420000", "VALUE_FORMAT": "midi", "TONE_NAME_1": 80, "OSC_PITCH_COARSE": 64}
        )
        by_offset = {m[11]: m[12] for m in messages}
        self.assertEqual(by_offset[0x00], 80)
        self.assertEqual(by_offset[AnalogParam.OSC_PITCH_COARSE.address], 64)

    def test_four_nibble_parameter(self):
        from jdxi_editor.midi.data.parameter.drum.partial import DrumPartialParam

        param = DrumPartialParam.WMT1_WAVE_NUMBER_L
        (message,) = section_param_dt1s(
            {"ADDRESS": "19702e00", "VALUE_FORMAT": "midi", param.name: 0x1234}
        )
        self.assertEqual(list(message[12:16]), [0x1, 0x2, 0x3, 0x4])


class TestBundleRoundTrip(unittest.TestCase):
    def setUp(self):
        # A helper of its own (MidiIOHelper is a singleton): editors built by
        # other tests stay connected to the shared one and queue read
        # requests when a patch loads, delaying these messages
        self._shared_helper = MidiIOHelper._instance
        MidiIOHelper._instance = None
        self.helper = MidiIOHelper()
        MidiIOHelper._instance = self._shared_helper
        self._saved_out = self.helper.midi_out
        self.sent = []
        self.helper.midi_out = Mock()
        self.helper.midi_out.is_port_open = Mock(return_value=True)
        self.helper.midi_out.send_message = Mock(side_effect=lambda m: self.sent.append(bytes(m)))
        self.memory = self.helper.device.memory
        self.memory.clear()

    def tearDown(self):
        self.helper.midi_out = self._saved_out
        self.memory.clear()

    def _receive(self, hex_message: str) -> None:
        data = bytes.fromhex(hex_message)[1:-1]
        self.helper._handle_midi_message(mido.Message("sysex", data=data))

    def test_saved_from_memory_and_restored_exactly(self):
        for reply in _REPLIES:
            self._receive(reply)
        folder = Path(tempfile.mkdtemp())
        written = write_memory_sections(self.memory, folder)
        self.assertEqual(written, {"18000000", "19012200", "19700000"})
        partial = json.loads((folder / "jdxi_tone_data_19012200.json").read_text())
        self.assertEqual(partial["VALUE_FORMAT"], "midi")
        self.assertEqual(partial["OSC_PITCH_ENV_ATTACK_TIME"], 10)

        bundle = folder / "patch.msz"
        with zipfile.ZipFile(bundle, "w") as zf:
            for path in folder.glob("*.json"):
                zf.write(path, path.name)
        names = []
        tone = lambda name, synth: names.append((synth, name))
        program = lambda name: names.append(("PROGRAM", name))
        self.helper.update_tone_name.connect(tone)
        self.helper.update_program_name.connect(program)
        try:
            self.memory.clear()
            self.helper.load_patch(str(bundle))
            # Wait for our own DT1s (other objects may also use the shared
            # helper's request queue, so its being idle proves nothing)
            expected = sorted(bytes.fromhex(r) for r in _REPLIES)
            deadline = time.monotonic() + 5.0
            while time.monotonic() < deadline:
                _APP.processEvents()
                if all(m in self.sent for m in expected):
                    break
                time.sleep(0.01)
            _APP.processEvents()
        finally:
            self.helper.update_tone_name.disconnect(tone)
            self.helper.update_program_name.disconnect(program)
        # Each section goes back as its DT1 (open editors may also send requests)
        written_back = [m for m in self.sent if len(m) > 7 and m[7] == 0x12]
        for message in expected:  # each section restored byte for byte, once
            self.assertEqual(written_back.count(message), 1)
        self.assertIn(("PROGRAM", "SMALLTOWN BO"), names)
        self.assertIn(("DRUM_KIT", "TR-606 Kit 1"), names)

    def test_editor_sections_are_converted_except_memory_ones(self):
        folder = Path(tempfile.mkdtemp())
        legacy = {"ADDRESS": "19420000", "OSC_PITCH_COARSE": 0}
        (folder / "jdxi_tone_data_19420000.json").write_text(json.dumps(legacy))
        self.assertEqual(convert_editor_sections(folder, skip=set()), 1)
        saved = json.loads((folder / "jdxi_tone_data_19420000.json").read_text())
        self.assertEqual(saved["OSC_PITCH_COARSE"], 64)
        self.assertEqual(convert_editor_sections(folder, skip=set()), 0)

    def test_program_change_clears_memory(self):
        self._receive(_D1_PARTIAL3)
        self.helper._handle_midi_message(mido.Message("program_change", channel=15, program=64))
        self.assertEqual(self.memory.sections(), [])
        self._receive(_D1_PARTIAL3)
        self.helper.send_raw_message([0xCF, 64])
        self.assertEqual(self.memory.sections(), [])


class TestReadEverySection(unittest.TestCase):
    def test_patch_sections(self):
        labels = [label for label, _ in patch_section_requests()]
        self.assertEqual(len(labels), 61)
        self.assertIn("Arpeggio / Controller", labels)
        self.assertIn("Drum Partial 38 (note 73)", labels)

    def test_drum_partial_label(self):
        self.assertEqual(label_for_address("19703600"), "Drum Partial 5 (note 40)")


if __name__ == "__main__":
    unittest.main()
