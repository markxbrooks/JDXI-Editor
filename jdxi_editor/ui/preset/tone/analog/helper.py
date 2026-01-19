"""
Analog presets

Example:
>>> result = get_preset_by_program_number(1)
>>> print(result)
{'id': '001', 'name': 'Toxic Bass 1', 'msb': 94.0, 'lsb': 64.0, 'pc': 1.0, 'category': 'Bass'}
>>> result2 = get_preset_parameters(1)
>>> print(result2)
(94.0, 64.0, 1.0)
"""

from typing import Any

from jdxi_editor.core.jdxi import JDXi


def get_preset_by_program_number(program_number: int) -> dict[str, Any] | None:
    """
    get_preset_by_program_number

    :param program_number: int Program number
    :return: Program details or None if not found
    """
    return next(
        (
            preset
            for preset in JDXi.UI.Preset.Analog.PROGRAM_CHANGE
            if preset["pc"] == program_number
        ),
        None,
    )


def get_preset_parameters(program_number: int) -> tuple[float, float, float]:
    """
    get_preset_parameters

    :param program_number: int
    :return: tuple of (msb, lsb, pc)
    :raises: ValueError if preset not found
    """
    preset = get_preset_by_program_number(program_number)
    if preset is None:
        raise ValueError(f"Preset with program number {program_number} not found")
    return preset["msb"], preset["lsb"], preset["pc"]
