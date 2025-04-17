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
        combined_data = {}

        for editor in editors:
            editor_name = editor.__class__.__name__  # Get the name of the editor class
            combined_data[editor_name] = editor.get_controls_as_dict()

        # Save the combined data to a single JSON file
        with open(file_path, 'w') as file:
            json.dump(combined_data, file, indent=4)

        logging.info(f"All controls saved successfully to {file_path}")

    except Exception as e:
        logging.error(f"Failed to save all controls: {e}")
