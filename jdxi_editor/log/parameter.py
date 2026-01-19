"""
Log parameters as Key, values, showing types and midi values
"""

import logging
from typing import Any

from decologr import decorate_log_message
from jdxi_editor.globals import LOG_PADDING_WIDTH, LOGGING, logger
from picomidi.utils.formatting import (
    format_message_to_hex_string as format_midi_message_to_hex_string,
)


def log_parameter(
    message: str,
    parameter: Any,
    float_precision: int = 2,
    max_length: int = 300,
    level: int = logging.INFO,
    silent: bool = False,
):
    """
    Log a structured representation of a parameter with type, formatted value, and optional emoji context.

    :param silent: bool suppress the log or not
    :param message: str The message to log.
    :param parameter: Any The parameter to log.
    :param float_precision: int The float precision.
    :param max_length: int The max length.
    :param level: int The log level.
    """

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
            # Safely convert to int for formatting
            return " ".join(
                f"0x{int(b) if not isinstance(b, int) else b:02X}" for b in param
            )
        return str(param)

    type_name = type(parameter).__name__
    formatted_value = format_value(parameter)

    if len(formatted_value) > max_length:
        formatted_value = formatted_value[: max_length - 3] + "..."

    # Style formatting
    padded_message = f"{message:<{LOG_PADDING_WIDTH}}"
    padded_type = f"{type_name:<12}"

    # Compose final log message
    formatted_message = f"{padded_message} {padded_type} {formatted_value}".rstrip()
    final_message = decorate_log_message(formatted_message, level)
    if LOGGING and not silent:
        # Dispatch to appropriate logging level
        logger.log(level, final_message, stacklevel=2)
