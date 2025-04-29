""" message.py"""
import logging
from typing import Any

from jdxi_editor.globals import LOG_PADDING_WIDTH, logger
from jdxi_editor.midi.data.address.address import AddressMemoryAreaMSB, AddressOffsetTemporaryToneUMB, \
    AddressOffsetProgramLMB, AddressOffsetSuperNATURALLMB
from jdxi_editor.midi.data.parameter.synth import AddressParameter
from jdxi_editor.midi.io.utils import format_midi_message_to_hex_string
from jdxi_editor.ui.windows.midi.debugger import parse_sysex_byte


def log_slider_parameters(umb: int,
                          lmb: int,
                          param: AddressParameter,
                          value: int,
                          slider_value: int,
                          level: int = logging.INFO):
    """Log slider parameters for debugging."""
    synth = f"0x{int(umb):02X}"
    part = f"0x{int(lmb):02X}"

    synth_name = parse_sysex_byte(int(synth, 16), AddressOffsetTemporaryToneUMB)
    if part != "0x00":
        # part_name = parse_sysex_byte(int(part, 16), AddressOffsetProgramLMB)
        part_name = parse_sysex_byte(int(part, 16), AddressOffsetSuperNATURALLMB)
    else:
        part_name = "COMMON"

    message = (
        f"Updating synth {synth:<2} \t {synth_name:<20} "
        f"part {part:<2} \t {part_name:<20} "
        f"{param.name:<30} "
        f"MIDI {value:<4} -> Slider {slider_value}"
    )
    # Use correct logging function depending on level
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

def log_parameter(
    message: str,
    parameter: Any,
    float_precision: int = 2,
    max_length: int = 300,
    level: int = logging.INFO,
):
    type_name = type(parameter).__name__

    if parameter is None:
        formatted_value = "None"
    elif isinstance(parameter, float):
        formatted_value = f"{parameter:.{float_precision}f}"
    elif isinstance(parameter, list):
        try:
            formatted_value = format_midi_message_to_hex_string(parameter)
        except TypeError:
            formatted_value = ", ".join(str(item) for item in parameter)
    elif isinstance(parameter, dict):
        formatted_value = ", ".join(f"{k}={v}" for k, v in parameter.items())
    elif isinstance(parameter, (bytes, bytearray)):
        formatted_value = " ".join(f"0x{b:02X}" for b in parameter)
    else:
        formatted_value = str(parameter)

    if len(formatted_value) > max_length:
        formatted_value = formatted_value[:max_length - 3] + "..."

    padded_message = f"{message:<{LOG_PADDING_WIDTH}}"
    padded_type = f"{type_name:<12}"

    # Add emojis based on log level
    level_emojis = {
        logging.DEBUG: "🔍",
        logging.INFO: "ℹ️",
        logging.WARNING: "⚠️",
        logging.ERROR: "❌",
        logging.CRITICAL: "💥",
    }
    emoji = level_emojis.get(level, "🔔")

    # Add MIDI flair if message seems MIDI-related
    midi_tag = "🎵" if "midi" in message.lower() or "sysex" in message.lower() else ""

    final_message = f"{emoji} {midi_tag} {padded_message} {padded_type} {formatted_value}"

    # Log with appropriate level
    if level == logging.DEBUG:
        logger.debug(final_message, stacklevel=2)
    elif level == logging.INFO:
        logger.info(final_message, stacklevel=2)
    elif level == logging.WARNING:
        logger.warning(final_message, stacklevel=2)
    elif level == logging.ERROR:
        logger.error(final_message, stacklevel=2)
    elif level == logging.CRITICAL:
        logger.critical(final_message, stacklevel=2)
    else:
        logger.log(level, final_message, stacklevel=2)



def log_parameter_old(
    message: str,
    parameter: Any,
    float_precision: int = 2,
    max_length: int = 300,
    level: int = logging.INFO,
):
    type_name = type(parameter).__name__

    if parameter is None:
        formatted_value = "None"
    elif isinstance(parameter, float):
        formatted_value = f"{parameter:.{float_precision}f}"
    elif isinstance(parameter, list):
        try:
            formatted_value = format_midi_message_to_hex_string(parameter)
        except TypeError:
            formatted_value = ", ".join(str(item) for item in parameter)
    elif isinstance(parameter, dict):
        formatted_value = ", ".join(f"{k}={v}" for k, v in parameter.items())
    elif isinstance(parameter, (bytes, bytearray)):
        formatted_value = " ".join(f"0x{b:02X}" for b in parameter)
    else:
        formatted_value = str(parameter)

    if len(formatted_value) > max_length:
        formatted_value = formatted_value[:max_length - 3] + "..."

    padded_message = f"{message:<{LOG_PADDING_WIDTH}}"
    padded_type = f"{type_name:<12}"

    # Use correct logging function depending on level
    if level == logging.DEBUG:
        logger.debug("%s %s %s", padded_message, padded_type, formatted_value, stacklevel=2)
    elif level == logging.INFO:
        logger.info("%s %s %s", padded_message, padded_type, formatted_value, stacklevel=2)
    elif level == logging.WARNING:
        logger.warning("%s %s %s", padded_message, padded_type, formatted_value, stacklevel=2)
    elif level == logging.ERROR:
        logger.error("%s %s %s", padded_message, padded_type, formatted_value, stacklevel=2)
    elif level == logging.CRITICAL:
        logger.critical("%s %s %s", padded_message, padded_type, formatted_value, stacklevel=2)
    else:
        # fallback for non-standard levels
        logger.log(level, "%s %s %s", padded_message, padded_type, formatted_value, stacklevel=2)
