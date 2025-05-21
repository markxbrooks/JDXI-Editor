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
            log.message(f"processing editor: {editor} {editor.__class__.__name__}")
            if not hasattr(editor, "address"):
                log.warning(f"Skipping invalid editor: {editor}, has no address")
                continue
            if not hasattr(editor, "get_controls_as_dict"):
                log.warning(f"Skipping invalid editor: {editor}, has no get_controls_as_dict method")
                continue
            
            # Convert address to hex string without spaces
            address_hex = ''.join([f"{x:02x}" for x in editor.address.to_bytes()])

            synth_tone_byte = address_hex[4:6]
            combined_data["ADDRESS"] = address_hex
            
            combined_data["TEMPORARY_AREA"] = parse_sysex_byte(
                editor.address.umb, AddressOffsetTemporaryToneUMB
            )
            synth_tone_map = {
                "20": "PARTIAL_1",
                "21": "PARTIAL_2",
                "22": "PARTIAL_3",
            }
            combined_data["SYNTH_TONE"] = synth_tone_map.get(synth_tone_byte, "UNKNOWN_SYNTH_TONE")
            # Get the raw control values instead of the full control data
            other_data = editor.get_controls_as_dict()
            for k, v in other_data.items():
                # If the value is a list/array, take just the first value (the actual control value)
                if isinstance(v, (list, tuple)) and len(v) > 0:
                    combined_data[k] = v[0]
                else:
                    combined_data[k] = v
                    
        # Save the combined data to a single JSON file
        with open(file_path, "w") as file_name:
            json.dump(combined_data, file_name, indent=4)
        log.message(f"All controls saved successfully to {file_path}")
    except Exception as ex:
        log.error(f"Error saving all controls: {ex}")
