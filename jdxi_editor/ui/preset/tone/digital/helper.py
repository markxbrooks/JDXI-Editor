"""
Digital preset list

Example:
>>> get_preset_by_program_number("001")
{'id': '001', 'name': 'JP8 Strings1', 'category': 'Strings/Pad', 'msb': 95.0, 'lsb': 64.0, 'pc': 1.0}
>>> get_preset_parameters(1)
(95.0, 64.0, 1.0)
"""

import csv
from io import StringIO
from typing import Optional, Tuple

from jdxi_editor.core.jdxi import JDXi

# placeholder, the file is in the doc directory if needed

RAW_PRESETS_CSV = ""


def generate_preset_list() -> list[dict[str, str]]:
    """Generate a list of presets from RAW_PRESETS_CSV data."""
    presets = []
    csv_file = StringIO(RAW_PRESETS_CSV)
    reader = csv.DictReader(csv_file)

    for row in reader:
        # print(row)
        # Convert numeric fields to integers
        msb = int(row["msb"])
        lsb = int(row["lsb"])
        pc = int(row["pc"])

        presets.append(
            {
                "id": row["id"].zfill(3),
                "name": row["name"],
                "category": row["category"],
                "msb": msb,
                "lsb": lsb,
                "pc": pc,
            }
        )
    return presets


def get_preset_by_program_number(program_number: str | int) -> Optional[dict]:
    """Get preset information by program number.
    :param program_number: str The program number (e.g., '090')
    :return: Optional[dict] The preset information containing msb, lsb, pc, and other details
    :return: None If preset not found
    """
    program_number = str(program_number).zfill(3)
    return next(
        (
            preset
            for preset in JDXi.UI.Preset.Digital.LIST
            if preset["id"] == program_number
        ),
        None,
    )


def get_preset_parameters(program_number: str) -> Optional[Tuple[int, int, int]]:
    """
    Get MSB, LSB, and PC values for a given program number.

    :param program_number: str The program number (e.g., '090')
    :return: Tuple[int, int, int] The MSB, LSB, and PC values as integers
    :return: Optional[Tuple[int, int, int]] The MSB, LSB, and PC values as integers
    :return: None If preset not found
    """
    preset = get_preset_by_program_number(program_number)
    if preset:
        return preset["msb"], preset["lsb"], preset["pc"]  # Already integers
    return None
