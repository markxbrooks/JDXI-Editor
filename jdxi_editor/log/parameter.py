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
    """Log a structured representation of a parameter with type, formatted value, and optional emoji context."""

    def format_value(param):
        if param is None:
            return "None"
        if isinstance(param, float):
            return f"{param:.{float_precision}f}"
        if isinstance(param, list):
            try:
                return format_midi_message_to_hex_string(param)
            except TypeError:
                return ", ".join(str(item) for item in param)
        if isinstance(param, dict):
            return ", ".join(f"{k}={v}" for k, v in param.items())
        if isinstance(param, (bytes, bytearray)):
            return " ".join(f"0x{b:02X}" for b in param)
        return str(param)

    type_name = type(parameter).__name__
    formatted_value = format_value(parameter)

    if len(formatted_value) > max_length:
        formatted_value = formatted_value[:max_length - 3] + "..."

    # Style formatting
    padded_message = f"{message:<{LOG_PADDING_WIDTH}}"
    padded_type = f"{type_name:<12}"

    # Emoji & MIDI context
    emoji = LEVEL_EMOJIS.get(level, "🔔")
    midi_tag = "🎵" if any(word in message.lower() for word in ["midi", "sysex", "address"]) else ""

    # Compose final log message
    final_message = f"{emoji} {midi_tag} {padded_message} {padded_type} {formatted_value}".rstrip()

    # Dispatch to appropriate logging level
    logger.log(level, final_message, stacklevel=2)
