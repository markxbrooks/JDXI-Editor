"""
Save all controls to a single JSON file.
This module provides a function to save the controls from multiple editor instances
to a single JSON file. The function takes a list of editor instances and a file path
as input, and it combines the controls into a single JSON object before saving it.
"""

import json


from jdxi_editor.log.logger import Logger as log
from jdxi_editor.midi.data.address.address import AddressOffsetTemporaryToneUMB
from jdxi_editor.ui.windows.midi.debugger import parse_sysex_byte


def save_all_controls_to_single_file(editors: list, file_path: str) -> None:
    """
    Save the controls from all editors to a single JSON file.

    :param editors: list A list of editor instances (e.g., AnalogSynthEditor, DigitalSynthEditor).
    :param file_path: str The file path where the combined JSON data will be saved.
    :return: None
    """
    try:
        combined_data = {"JD_XI_HEADER": "f041100000000e"}
        for editor in editors:
            if not hasattr(editor, "address") or not hasattr(editor, "get_controls_as_dict"):
                log.warning(f"Skipping invalid editor: {editor}")
                continue
            combined_data["ADDRESS"] = str(editor.address)
            combined_data["TEMPORARY_AREA"] = parse_sysex_byte(
                editor.address.umb, AddressOffsetTemporaryToneUMB
            )
            other_data = editor.get_controls_as_dict()
            for k, v in other_data.items():
                combined_data[k] = v
        # Save the combined data to a single JSON file
        with open(file_path, "w") as file_name:
            json.dump(combined_data, file_name, indent=4)
        log.message(f"All controls saved successfully to {file_path}")
    except Exception as ex:
        log.error(f"Error saving all controls: {ex}")
