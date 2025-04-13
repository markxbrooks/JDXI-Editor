import logging
from typing import Any

from jdxi_editor.globals import LOG_PADDING_WIDTH


def log_parameter(message: str, parameter: Any, float_precision: int = 2, max_length: int = 300):
    type_name = type(parameter).__name__

    if parameter is None:
        formatted_value = "None"
    elif isinstance(parameter, float):
        formatted_value = f"{parameter:.{float_precision}f}"
    elif isinstance(parameter, list):
        formatted_value = ", ".join(str(item) for item in parameter)
    elif isinstance(parameter, dict):
        formatted_value = ", ".join(f"{k}={v}" for k, v in parameter.items())
    elif isinstance(parameter, (bytes, bytearray)):
        formatted_value = " ".join(f"0x{b:02X}" for b in parameter)
    else:
        formatted_value = str(parameter)

    # Truncate long values for neatness
    if len(formatted_value) > max_length:
        formatted_value = formatted_value[:max_length - 3] + "..."

    logging.info(
        f"{message:<{LOG_PADDING_WIDTH}} {type_name:<12} {formatted_value}"
    )
