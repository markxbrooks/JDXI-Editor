""" parameter.py"""
import logging
from typing import Any

from jdxi_editor.globals import LOG_PADDING_WIDTH, logger
from jdxi_editor.log.emoji import LEVEL_EMOJIS
from jdxi_editor.midi.io.utils import format_midi_message_to_hex_string


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

    emoji = LEVEL_EMOJIS.get(level, "🔔")

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
