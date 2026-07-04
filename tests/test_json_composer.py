import json
import tempfile
import unittest
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QWidget

from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.sysex.json_composer import JDXiJSONComposer
from jdxi_editor.ui.editors import AnalogSynthEditor

_app = None


def get_qapp():
    global _app
    if _app is None:
        _app = QApplication.instance()
        if _app is None:
            _app = QApplication([])
    return _app


class TestJDXiJSONComposer(unittest.TestCase):
    def setUp(self):
        get_qapp()
        self.composer = JDXiJSONComposer()
        self.output_json_file = None
        self.temp_folder = None
        self._container = QWidget()
        self._container.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
        self._editor = None

    def test_compose_analog_synth_json_file(self):
        midi_helper = MidiIOHelper()
        editor = AnalogSynthEditor(midi_helper, parent=self._container)
        editor.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
        editor.show()
        QApplication.processEvents()
        self._editor = editor

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_folder = Path(temp_dir)
            self.temp_folder = temp_folder
            output_json_file = self.composer.process_editor(editor, temp_folder)
            self.output_json_file = output_json_file

            self.assertTrue(
                output_json_file.exists(),
                f"Output JSON file not found: {output_json_file}",
            )

            with open(output_json_file, "r", encoding="utf-8") as f:
                generated_data = json.load(f)

            expected_json_path = (
                Path(__file__).parent / "fixtures" / "jdxi_tone_data_19420000.json"
            )
            self.assertTrue(
                expected_json_path.exists(),
                f"Expected JSON file not found: {expected_json_path}",
            )

            with open(expected_json_path, "r", encoding="utf-8") as f:
                expected_data = json.load(f)

            self.assertEqual(set(generated_data.keys()), set(expected_data.keys()))
            for key, expected_value in expected_data.items():
                self.assertEqual(
                    generated_data[key],
                    expected_value,
                    f"Mismatch for key {key!r}",
                )

    def tearDown(self):
        if self._editor is not None:
            self._editor.close()
            self._editor.setParent(None)
            self._editor.deleteLater()
            self._editor = None
        if self._container is not None:
            self._container.deleteLater()
            self._container = None
        QApplication.processEvents()


if __name__ == "__main__":
    unittest.main()
