"""
Get preset Values

Example:
>>> get_preset_values(preset_index=1)
(95, 64, 1)
"""

from decologr import Decologr as log
from jdxi_editor.core.jdxi import JDXi


def get_preset_values(preset_index: int, preset_list=JDXi.UI.Preset.Digital.LIST):
    """
    Retrieve MSB, LSB, and PC values for a given preset.

    :param preset_index: int The index of the preset
    :param preset_list: list The list of presets
    :return: tuple The MSB, LSB, and PC values
    """
    # Lazy import to avoid circular dependency
    from jdxi_editor.ui.editors.helpers.preset import get_preset_parameter_value

    msb = get_preset_parameter_value("msb", preset_index, preset_list)
    lsb = get_preset_parameter_value("lsb", preset_index, preset_list)
    pc = get_preset_parameter_value("pc", preset_index, preset_list)

    if None in [msb, lsb, pc]:
        log.message(f"Could not retrieve preset parameters for program {preset_index}")
        return None, None, None

    log.message(f"Retrieved MSB, LSB, PC: {msb}, {lsb}, {pc}")
    return msb, lsb, pc
