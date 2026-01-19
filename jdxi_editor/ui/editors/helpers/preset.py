"""
preset retrieval

Example:
>>> get_preset_parameter_value(parameter="msb", id="001")
95
>>> get_preset_parameter_value(parameter="lsb", id="010")
64
"""

import re
from typing import Any, Dict, List, Optional, Union

from jdxi_editor.core.jdxi import JDXi


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
    parameter: str, id: Union[str, int], preset_list: list = None
) -> Union[Optional[int], Any]:
    """
    Retrieve a specific parameter value from a preset by its ID.

    :param parameter: Name of the parameter to retrieve.
    :param id: Preset ID (e.g., "001" or integer 1).
    :param preset_list: List of preset dictionaries or dictionary format (PROGRAM_CHANGE).
    :return: The parameter value, or None if not found.
    """
    # --- Normalize ID to string, padded to 3 characters (e.g., "001")
    if preset_list is None:
        preset_list = JDXi.UI.Preset.Digital.PROGRAM_CHANGE

    # Convert dictionary format (Digital/Analog PROGRAM_CHANGE) to list format if needed
    if isinstance(preset_list, dict):
        # Convert dictionary {1: {"Name": "...", "Category": "...", "MSB": 95, ...}, ...} to list format
        converted_preset_list = [
            {
                "id": f"{preset_id:03d}",  # Format as "001", "002", etc.
                "name": preset_data.get("Name", ""),
                "category": preset_data.get("Category", ""),
                "msb": preset_data.get("MSB", 0),
                "lsb": preset_data.get("LSB", 0),
                "pc": preset_data.get("PC", preset_id),
            }
            for preset_id, preset_data in sorted(preset_list.items())
        ]
    else:
        # Already a list (Drum format or already converted)
        converted_preset_list = preset_list

    if isinstance(id, int):
        id = f"{id:03d}"

    preset = next((p for p in converted_preset_list if str(p.get("id")) == id), None)
    if not preset:
        return None

    value = preset.get(parameter)
    if value is None:
        return None

    # --- Convert string values to int if expected
    if parameter in ["msb", "lsb", "pc"]:
        try:
            return int(value)
        except ValueError:
            return None

    return value
