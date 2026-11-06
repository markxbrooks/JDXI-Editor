"""
Patch names and Digital sections survive save and load (no MIDI hardware).

- loading a bundle updates the program / tone titles from the Common blocks
- the Digital editor and its partial panels save their section controls
- the tone name is saved in Common only; Tone Modify has its own address
"""

import json
import os
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import Mock

sys.path.insert(0, os.path.abspath("."))

from PySide6.QtWidgets import QApplication

_APP = QApplication.instance() or QApplication([])

from jdxi_editor.midi.data.parameter.digital import (
    DigitalCommonParam,
    DigitalModifyParam,
    DigitalPartialParam,
)
from jdxi_editor.midi.io.helper import MidiIOHelper, patch_json_tone_name
from jdxi_editor.midi.sysex.json_composer import JDXiJSONComposer
from jdxi_editor.midi.sysex.parser.sysex import JDXiSysExParser
from jdxi_editor.ui.editors.digital.editor import DigitalSynthEditor

# Digital 1 Common from the JD-Xi: "MKS-50 Bass1"
_DT1_D1_COMMON = (
    "F0 41 10 00 00 00 0E 12 19 01 00 00 4D 4B 53 2D 35 30 20 42 61 73 73 31 07 00 "
    "00 00 00 00 00 13 01 41 02 02 00 00 00 01 01 00 00 00 00 00 00 00 00 00 00 00 "
    "00 00 00 00 00 00 00 00 00 01 01 01 00 00 15 00 00 04 0E 40 03 00 00 00 40 F7"
)


def _name_codes(name: str) -> dict:
    return {f"TONE_NAME_{i}": ord(c) for i, c in enumerate(name.ljust(12)[:12], 1)}


def _section(address: str, area: str, tone: str, **values) -> dict:
    return {
        "JD_XI_HEADER": "f041100000000e",
        "ADDRESS": address,
        "TEMPORARY_AREA": area,
        "SYNTH_TONE": tone,
        **values,
    }


class TestPatchJsonToneName(unittest.TestCase):
    def test_saved_character_codes(self):
        self.assertEqual(patch_json_tone_name(_name_codes("SMALLTOWN BO")), "SMALLTOWN BO")

    def test_trailing_spaces_removed(self):
        self.assertEqual(patch_json_tone_name(_name_codes("TR-606")), "TR-606")

    def test_parsed_text(self):
        self.assertEqual(patch_json_tone_name({"TONE_NAME": "MKS-50 Bass1"}), "MKS-50 Bass1")

    def test_no_name(self):
        self.assertEqual(patch_json_tone_name({"PROGRAM_LEVEL": 127}), "")


class TestLoadBundleUpdatesTitles(unittest.TestCase):
    def setUp(self):
        self.helper = MidiIOHelper()
        self._saved_out = self.helper.midi_out
        self.helper.midi_out = Mock()
        self.helper.midi_out.is_port_open = Mock(return_value=True)
        self.names = []
        self._tone = lambda name, synth: self.names.append((synth, name))
        self._program = lambda name: self.names.append(("PROGRAM", name))
        self.helper.update_tone_name.connect(self._tone)
        self.helper.update_program_name.connect(self._program)

    def tearDown(self):
        self.helper.update_tone_name.disconnect(self._tone)
        self.helper.update_program_name.disconnect(self._program)
        self.helper.midi_out = self._saved_out

    def _bundle(self, sections: list[dict]) -> str:
        path = Path(tempfile.mkdtemp()) / "patch.msz"
        with zipfile.ZipFile(path, "w") as zf:
            for section in sections:
                zf.writestr(f"jdxi_tone_data_{section['ADDRESS']}.json", json.dumps(section))
        return str(path)

    def test_common_names_update_titles(self):
        path = self._bundle(
            [
                _section("18000000", "TEMPORARY_PROGRAM", "COMMON", **_name_codes("SMALLTOWN BO")),
                _section("19010000", "DIGITAL_SYNTH_1", "COMMON", **_name_codes("MKS-50 Bass1")),
                _section("19700000", "DRUM_KIT", "COMMON", **_name_codes("TR-606 Kit 1")),
                # partial blocks carry no name
                _section("19012000", "DIGITAL_SYNTH_1", "PARTIAL_1", OSC_WAVEFORM=0),
            ]
        )
        self.helper.load_patch(path)
        _APP.processEvents()
        self.assertIn(("PROGRAM", "SMALLTOWN BO"), self.names)
        self.assertIn(("DIGITAL_SYNTH_1", "MKS-50 Bass1"), self.names)
        self.assertIn(("DRUM_KIT", "TR-606 Kit 1"), self.names)
        self.assertEqual(len(self.names), 3)


class TestDigitalEditorSave(unittest.TestCase):
    def setUp(self):
        self.editor = DigitalSynthEditor(
            midi_helper=Mock(), preset_helper=Mock(), synth_number=1, parent=None
        )

    def tearDown(self):
        self.editor.close()
        self.editor.deleteLater()

    def test_section_controls_are_collected(self):
        editor_params = self.editor.all_controls()
        self.assertTrue(any(isinstance(p, DigitalCommonParam) for p in editor_params))
        self.assertTrue(any(isinstance(p, DigitalModifyParam) for p in editor_params))
        # Partials belong to their panels, which are saved on their own
        self.assertFalse(any(isinstance(p, DigitalPartialParam) for p in editor_params))
        panel = self.editor.partial_editors[1]
        self.assertGreater(len(panel.get_controls_as_dict()), 30)

    def test_save_writes_common_with_name_and_modify(self):
        parsed = JDXiSysExParser().parse_bytes(bytes.fromhex(_DT1_D1_COMMON))
        self.editor.dispatch_sysex_to_area(json.dumps(parsed))
        self.editor.set_instrument_title_label("MKS-50 Bass1", "DIGITAL_SYNTH_1")
        out = Path(tempfile.mkdtemp())
        composer = JDXiJSONComposer()
        composer.process_editor(self.editor, out)
        for panel in self.editor.partial_editors.values():
            composer.process_editor(panel, out)

        files = {f.stem.split("_")[-1]: json.loads(f.read_text()) for f in out.glob("*.json")}
        self.assertEqual(
            sorted(files), ["19010000", "19012000", "19012100", "19012200", "19015000"]
        )
        self.assertEqual(patch_json_tone_name(files["19010000"]), "MKS-50 Bass1")
        self.assertEqual(files["19015000"]["SYNTH_TONE"], "MODIFY")
        self.assertEqual(patch_json_tone_name(files["19015000"]), "")
        self.assertGreater(len(files["19012000"]), 30)


if __name__ == "__main__":
    unittest.main()
