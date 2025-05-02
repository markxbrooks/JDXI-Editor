"""
Save all controls to a single JSON file.
This module provides a function to save the controls from multiple editor instances
to a single JSON file. The function takes a list of editor instances and a file path
as input, and it combines the controls into a single JSON object before saving it.
"""

import json


from jdxi_editor.log.error import log_error
from jdxi_editor.log.message import log_message


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
            combined_data["ADDRESS"] = editor.sysex_address
            editor_part = editor.sysex_address.umb.name  # Get the part of the editor class
            combined_data[editor_part] = editor.get_controls_as_dict()
        # Save the combined data to a single JSON file
        with open(file_path, 'w') as file_name:
            json.dump(combined_data, file_name, indent=4)
        log_message(f"All controls saved successfully to {file_path}")
    except Exception as ex:
        log_error(f"Error saving all controls: {ex}")
