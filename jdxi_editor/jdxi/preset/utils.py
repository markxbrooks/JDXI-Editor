import logging

from jdxi_editor.midi.data.programs.presets import DIGITAL_PRESET_LIST
from jdxi_editor.ui.editors.helpers.program import get_preset_parameter_value


def get_preset_values(preset_index, preset_list=DIGITAL_PRESET_LIST):
    """Retrieve MSB, LSB, and PC values for a given preset."""
    msb = get_preset_parameter_value("msb", preset_index, preset_list)
    lsb = get_preset_parameter_value("lsb", preset_index, preset_list)
    pc = get_preset_parameter_value("pc", preset_index, preset_list)

    if None in [msb, lsb, pc]:
        logging.error(
            f"Could not retrieve preset parameters for program {preset_index}"
        )
        return None, None, None

    logging.info(f"Retrieved MSB, LSB, PC: {msb}, {lsb}, {pc}")
    return msb, lsb, pc
