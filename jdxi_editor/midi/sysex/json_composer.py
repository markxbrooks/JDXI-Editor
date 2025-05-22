"""
JDXiSysExComposer
"""

import json
import os
from pathlib import Path
from typing import Optional


from jdxi_editor.log.logger import Logger as log
from jdxi_editor.midi.data.address.address import AddressOffsetTemporaryToneUMB
from jdxi_editor.ui.editors import SynthEditor
from jdxi_editor.ui.windows.midi.debugger import parse_sysex_byte


class JDXiJSONComposer:
    """ JSON SysExComposer """

    def __init__(self, editor: Optional[SynthEditor] = None):
        self.json_string = None
        if editor:
            self.editor = editor
            self.address = editor.address
        self.temp_folder = Path.home() / ".jdxi_editor" / "temp"
        if not os.path.exists(self.temp_folder):
            self.temp_folder.mkdir(parents=True, exist_ok=True)

    def compose_message(
        self,
        editor: SynthEditor,
    ) -> Optional[str]:
        """
        :param editor: SynthEditor Editor instance to process
        :return: str JSON SysEx message
        """
        if editor:
            self.editor = editor
            self.address = editor.address
        try:
            editor_data = {"JD_XI_HEADER": "f041100000000e"}
            if not hasattr(editor, "address"):
                log.warning(f"Skipping invalid editor: {editor}, has no address")
                return None
            if not hasattr(editor, "get_controls_as_dict"):
                log.warning(f"Skipping invalid editor: {editor}, has no get_controls_as_dict method")
                return None
            # Convert address to hex string without spaces
            address_hex = ''.join([f"{x:02x}" for x in editor.address.to_bytes()])
            synth_tone_byte = address_hex[4:6]
            editor_data["ADDRESS"] = address_hex

            editor_data["TEMPORARY_AREA"] = parse_sysex_byte(
                editor.address.umb, AddressOffsetTemporaryToneUMB
            )
            synth_tone_map = {
                "20": "PARTIAL_1",
                "21": "PARTIAL_2",
                "22": "PARTIAL_3",
            }
            editor_data["SYNTH_TONE"] = synth_tone_map.get(synth_tone_byte, "UNKNOWN_SYNTH_TONE")
            # Get the raw control values instead of the full control data
            other_data = editor.get_controls_as_dict()
            for k, v in other_data.items():
                # If the value is a list/array, take just the first value (the actual control value)
                if isinstance(v, (list, tuple)) and len(v) > 0:
                    editor_data[k] = v[0]
                else:
                    editor_data[k] = v
                # Convert combined_data to JSON string
                self.json_string = editor_data # json.dumps(editor_data, indent=4)
            return self.json_string

        except (ValueError, TypeError, OSError, IOError) as ex:
            log.error(f"Error sending message: {ex}")
            return None

    def save_json(self, file_path: str) -> None:
        """
        Save the JSON string to a file
        :param file_path: str File path to save the JSON
        :return: None
        """
        try:
            with open(file_path, "w", encoding="utf-8") as file_handle:
                json.dump(self.json_string, file_handle, ensure_ascii=False, indent=2)
            log.message(f"JSON saved successfully to {file_path}")
        except Exception as ex:
            log.error(f"Error saving JSON: {ex}")

    def process_editor(self, editor: SynthEditor, temp_folder: Path) -> None:
        """
        Process the editor and save the JSON
        :param editor: SynthEditor Editor instance to process
        :param temp_folder: str Temporary folder to save the JSON
        :return: None
        """
        if temp_folder:
            self.temp_folder = temp_folder
        self.compose_message(editor)
        address_hex = ''.join([f"{x:02x}" for x in editor.address.to_bytes()])
        json_temp_file = (
                self.temp_folder
                / f"jdxi_tone_data_{address_hex}.json"
        )
        self.save_json(str(json_temp_file))
        log.message(f"JSON saved successfully to {json_temp_file}")
