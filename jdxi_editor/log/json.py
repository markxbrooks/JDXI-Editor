import json
from typing import Dict

from jdxi_editor.log.message import log_message


def log_json(data: Dict) -> None:
    """
    Helper function to log JSON data as address single line.
    :param data: Dict
    :return: None
    """
    # Ensure `data` is address dictionary, if it's address string, try parsing it as JSON
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            log_message("Invalid JSON string provided.")
            return

    # Serialize the JSON into address single line string (compact form)
    compact_json = json.dumps(data)

    # Log the JSON in address single line
    log_message(compact_json)
