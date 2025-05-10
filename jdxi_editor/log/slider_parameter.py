"""
Log Slider Parameters
"""
import logging

from jdxi_editor.globals import logger, LOGGING
from jdxi_editor.log.emoji import LEVEL_EMOJIS
from jdxi_editor.midi.data.address.address import (
    AddressOffsetTemporaryToneUMB, AddressOffsetProgramLMB,
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
        if part_lmb != f"{ZERO_BYTE}":
            part_name_lmb = parse_sysex_byte(
                int(part_lmb, 16), AddressOffsetProgramLMB
            )
        else:
            part_name_lmb = "COMMON"

        message = (
            f"Updating [umb {synth_umb:<3} {synth_name_umb:<20}] "
            f"[lmb {part_lmb:<3} {part_name_lmb:<20}] "
            f"[lsb: 0x{param.address:02X} {param.name:<35}] "
            f"midi data: {value:<4} → Slider: {slider_value:.1f}"
        )

        emoji = LEVEL_EMOJIS.get(level, "🔔")

        # Add MIDI flair if message seems MIDI-related
        midi_tag = "🎵" if "midi" in message.lower() or "sysex" in message.lower() else ""
        qc_passed_tag = "✅" if "updat" in message.lower() or "success" in message.lower() else "❌"
        message = f"{emoji}{qc_passed_tag}{midi_tag} {message}"
        if LOGGING:
            if level == logging.DEBUG:
                logger.debug(message, stacklevel=2)
            elif level == logging.INFO:
                logger.info(message, stacklevel=2)
            elif level == logging.WARNING:
                logger.warning(message, stacklevel=2)
            elif level == logging.ERROR:
                logger.error(message, stacklevel=2)
            elif level == logging.CRITICAL:
                logger.critical(message, stacklevel=2)
            else:
                # fallback for non-standard levels
                logger.log(message, stacklevel=2)
    except Exception as ex:
        logger.error(f"Error {ex} occurred logging parameter")
