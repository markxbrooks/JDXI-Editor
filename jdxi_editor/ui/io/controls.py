import json
import logging


def save_all_controls_to_single_file(editors, file_path):
    """
    Save the controls from all editors to a single JSON file.

    Args:
        editors (list): A list of editor instances (e.g., AnalogSynthEditor, DigitalSynthEditor).
        file_path (str): The file path where the combined JSON data will be saved.
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

        logging.info(f"All controls saved successfully to {file_path}")

    except Exception as e:
        logging.error(f"Failed to save all controls: {e}")
