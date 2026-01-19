import json
import unittest
from pathlib import Path

from PySide6.QtWidgets import QApplication
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.sysex.json_composer import JDXiJSONComposer
from jdxi_editor.ui.editors import AnalogSynthEditor

p = QApplication([])


class TestJDXiJSONComposer(unittest.TestCase):
    def setUp(self):
        """
        setUp
        :return:
        """
        self.composer = JDXiJSONComposer()
        self.output_json_file = None
        self.temp_folder = None

    def test_compose_analog_synth_json_file(self):
        """
        test_compose_analog_synth_json_file
        :return:
        """
        midi_helper = MidiIOHelper()
        editor = AnalogSynthEditor(midi_helper)
        temp_folder = Path.home() / "temp_folder"
        self.temp_folder = temp_folder
        output_json_file = self.composer.process_editor(editor, temp_folder)

        # Save for cleanup
        self.output_json_file = output_json_file

        # --- Check file existence ---
        self.assertTrue(output_json_file.exists(), f"Output JSON file not found: {output_json_file}")

        # --- Load the generated JSON ---
        with open(output_json_file, "r", encoding="utf-8") as f:
            generated_data = json.load(f)

        # --- Load the expected JSON ---
        expected_json_path = Path(__file__).parent / "fixtures" / "jdxi_tone_data_19420000.json"
        self.assertTrue(expected_json_path.exists(), f"Expected JSON file not found: {expected_json_path}")

        with open(expected_json_path, "r", encoding="utf-8") as f:
            expected_data = json.load(f)

        # --- Compare content ---
        self.assertEqual(generated_data, expected_data)

    def tearDown(self):
        """
        tearDown method
        :return:
        """
        if self.output_json_file and self.output_json_file.exists():
            try:
                self.output_json_file.unlink()
            except Exception as e:
                print(f"Warning: could not delete file {self.output_json_file}: {e}")

        if self.temp_folder.exists():
            try:
                if not any(self.temp_folder.iterdir()):  # Only remove if empty
                    self.temp_folder.rmdir()
            except Exception as ex:
                print(f"Warning: could not remove temp folder {self.temp_folder}: {ex}")


if __name__ == '__main__':
    unittest.main()
