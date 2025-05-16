"""
Log Slider Parameters
"""

import logging

from jdxi_editor.globals import logger, LOGGING
from jdxi_editor.log.decorator import decorate_log_message
from jdxi_editor.midi.data.address.address import (
    AddressOffsetTemporaryToneUMB, AddressOffsetAnalogLMB, AddressOffsetDrumKitLMB,
)
from jdxi_editor.midi.data.address.sysex import ZERO_BYTE
from jdxi_editor.midi.data.parameter.synth import AddressParameter
from jdxi_editor.ui.windows.midi.debugger import parse_sysex_byte


def log_slider_parameters(
    umb: int,
    lmb: int,
    param: AddressParameter,
    value: int,
    slider_value: int,
    level: int = logging.INFO,
) -> None:
    """
    Log slider parameters for debugging.
    :param umb: int The UMB
    :param lmb: int The LMB
    :param param: AddressParameter The parameter
    :param value: int The value
    :param slider_value: int The slider value
    :param level: int The log level
    :return: None
    """
    try:
        synth_umb = f"0x{int(umb):02X}"
        part_lmb = f"0x{int(lmb):02X}"
        synth_name_umb = parse_sysex_byte(int(synth_umb, 16), AddressOffsetTemporaryToneUMB)
        if synth_name_umb == AddressOffsetTemporaryToneUMB.DRUM_KIT_PART.name:
            address_offset = AddressOffsetDrumKitLMB
        else:
            address_offset = AddressOffsetAnalogLMB
        if part_lmb != f"{ZERO_BYTE}":
            part_name_lmb = parse_sysex_byte(
                int(part_lmb, 16), address_offset
            )
        else:
            part_name_lmb = "COMMON"

        message = (
            f"Updating [umb {synth_umb:<3} {synth_name_umb:<20}] "
            f"[lmb {part_lmb:<3} {part_name_lmb:<20}] "
            f"[lsb: 0x{param.address:02X} {param.name:<35}] "
            f"midi data: {value:<4} → Slider: {slider_value:.1f}"
        )

        decorated_message = decorate_log_message(message, level)
        if LOGGING:
            logger.log(level, decorated_message, stacklevel=2)
    except Exception as ex:
        logger.error(f"Error {ex} occurred logging parameter")
