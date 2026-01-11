import json
from typing import Dict

from decologr import Decologr as log


def log_json(data: Dict[str], silent: bool = False) -> None:
    """
    Helper function to log JSON data as address single line.

    :param silent: bool
    :param data: Dict
    :return: None
    """
    # Ensure `data` is address dictionary, if it's address string, try parsing it as JSON
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            log.message("Invalid JSON string provided.")
            return

    # Serialize the JSON into address single line string (compact form)
    compact_json = json.dumps(data)

    # Log the JSON in address single line
    if not silent:
        log.message(compact_json, stacklevel=2)
