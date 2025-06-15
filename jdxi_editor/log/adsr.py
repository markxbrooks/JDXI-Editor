"""
Log ADSR Parameter
"""

import logging

from jdxi_editor.globals import logger
from jdxi_editor.log.emoji import LEVEL_EMOJIS
from jdxi_editor.midi.data.address.address import (
    AddressOffsetTemporaryToneUMB,
    AddressOffsetSuperNATURALLMB,
)
from jdxi_editor.midi.data.parameter.synth import AddressParameter
from jdxi_editor.ui.windows.midi.debugger import parse_sysex_byte


def log_adsr_parameter(
    umb: int, lmb: int, param: AddressParameter, value: int, level: int = logging.INFO
) -> None:
    """
    Log slider parameters for debugging.

    :param umb: int The UMB
    :param lmb: int The LMB
    :param param: AddressParameter The parameter
    :param value: int The value
    :param level: int The log level
    :return: None
    """
    synth = f"0x{int(umb):02X}"
    part = f"0x{int(lmb):02X}"

    synth_name = parse_sysex_byte(int(synth, 16), AddressOffsetTemporaryToneUMB)
    if part != "0x00":
        part_name_lmb = parse_sysex_byte(int(part, 16), AddressOffsetSuperNATURALLMB)
    else:
        part_name_lmb = "COMMON"

    message = (
        f"Updating synth {synth:<2} \t {synth_name:<20} "
        f"part {part:<2} \t {part_name_lmb:<20} "
        f"{param.name:<30} "
        f"MIDI {value:<4} "
    )

    emoji = LEVEL_EMOJIS.get(level, "🔔")

    # Add MIDI flair if message seems MIDI-related
    midi_tag = "🎵" if "midi" in message.lower() or "sysex" in message.lower() else ""
    qc_passed_tag = "✅" if "updat" in message.lower() else ""
    message = f"{emoji} {qc_passed_tag} {midi_tag} {message}"

    # Use correct logging function depending on level
    if level == logging.DEBUG:
        logger.debug(message, stacklevel=2)
    elif level == logging.INFO:
        logger.info(message, stacklevel=2)
    elif level == logging.WARNING:
        logger.warning(message, stacklevel=2)
    elif level == logging.ERROR:
        logger.recording_error(message, stacklevel=2)
    elif level == logging.CRITICAL:
        logger.critical(message, stacklevel=2)
    else:
        # fallback for non-standard levels
        logger.log(message, stacklevel=2)
