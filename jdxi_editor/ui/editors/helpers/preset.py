import re
from typing import List, Dict, Optional, Union, Any

from jdxi_editor.midi.data.programs.digital import DIGITAL_PRESET_LIST


def get_preset_list_number_by_name(
    preset_name: str, preset_list: List[Dict[str, str]]
) -> Optional[int]:
    """
    Retrieve a program's number (without bank letter) by its name using regex search

    :param preset_name: str
    :param preset_list: list
    :return: int preset id
    """
    preset = next(
        (
            p
            for p in preset_list
            if re.search(re.escape(preset_name), p["name"], re.IGNORECASE)
        ),
        None,
    )
    return int(preset["id"]) if preset else 0


def get_preset_parameter_value(
    parameter: str,
    id: Union[str, int],
    preset_list: List[dict] = DIGITAL_PRESET_LIST
) -> Union[Optional[int], Any]:
    """
    Retrieve a specific parameter value from a preset by its ID.

    :param parameter: Name of the parameter to retrieve.
    :param id: Preset ID (e.g., "001" or integer 1).
    :param preset_list: List of preset dictionaries.
    :return: The parameter value, or None if not found.
    """
    # Normalize ID to string, padded to 3 characters (e.g., "001")
    if isinstance(id, int):
        id = f"{id:03d}"

    preset = next((p for p in preset_list if str(p.get("id")) == id), None)
    if not preset:
        return None

    value = preset.get(parameter)
    if value is None:
        return None

    # Convert string values to int if expected
    if parameter in ["msb", "lsb", "pc"]:
        try:
            return int(value)
        except ValueError:
            return None

    return value
