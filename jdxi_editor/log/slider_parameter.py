"""
Log Slider Parameters
"""

import logging
from typing import Union

from decologr import decorate_log_message
from decologr.logger import format_scope
from picomidi.sysex.parameter.address import AddressParameter

from jdxi_editor.globals import LOGGING, logger
from jdxi_editor.midi.data.address.address import (
    JDXiSysExOffsetDrumKitLMB,
    JDXiSysExOffsetProgramLMB,
    JDXiSysExOffsetSuperNATURALLMB,
    JDXiSysExOffsetTemporaryToneUMB,
    RolandSysExAddress,
)
from jdxi_editor.midi.data.address.sysex import ZERO_BYTE
from jdxi_editor.ui.windows.midi.debugger import parse_sysex_byte


def log_slider_parameters(
    address: RolandSysExAddress,
    param: AddressParameter,
    midi_value: int,
    slider_value: Union[int, float],
    level: int = logging.INFO,
    scope: str = None
) -> None:
    """
    Log slider parameters for debugging.

    :param address: int The address
    :param param: AddressParameter The parameter
    :param midi_value: int The value
    :param slider_value: int The slider value
    :param level: int The log level
    :return: None
    """
    try:
        synth_umb = f"0x{int(address.umb):02X}"
        part_lmb = f"0x{int(address.lmb):02X}"
        synth_name_umb = parse_sysex_byte(
            int(synth_umb, 16), JDXiSysExOffsetTemporaryToneUMB
        )
        if synth_name_umb == JDXiSysExOffsetTemporaryToneUMB.DRUM_KIT.name:
            address_offset_cls = JDXiSysExOffsetDrumKitLMB
        elif synth_name_umb in [
            JDXiSysExOffsetTemporaryToneUMB.DIGITAL_SYNTH_1.name,
            JDXiSysExOffsetTemporaryToneUMB.DIGITAL_SYNTH_2.name,
        ]:
            address_offset_cls = JDXiSysExOffsetSuperNATURALLMB
        else:
            address_offset_cls = JDXiSysExOffsetProgramLMB
        if part_lmb != f"{ZERO_BYTE}":
            part_name_lmb = parse_sysex_byte(int(part_lmb, 16), address_offset_cls)
        else:
            part_name_lmb = "COMMON"

        message = (
            f"[umb] [{synth_umb:<3} {synth_name_umb:<20}] "
            f"[lmb] [{part_lmb:<3} {part_name_lmb:<20}] "
            f"[lsb] [0x{param.address:02X} {param.name:<35}] "
            f"[midi data] [{midi_value:<4} → Slider: {slider_value:.1f}]"
        )

        if scope is not None:
            scope_str = format_scope(scope)
            message = f"{scope_str} {message}"

        decorated_message = decorate_log_message(message, level)
        if LOGGING:
            logger.log(level, decorated_message, stacklevel=2)
    except Exception as ex:
        logger.error(
            "[log_slider_parameters] Error %s occurred logging parameter", ex
        )
