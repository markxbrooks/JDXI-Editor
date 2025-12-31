""" log header message """
import logging

from jdxi_editor.log.message import log_message


def log_header_message(message: str, level: int = logging.INFO) -> None:
    """
    Logs a visually distinct header message with separator lines and emojis.

    :param message: The message to log.
    :param level: Logging level (default: logging.INFO).
    """
    stacklevel: int = 3
    full_separator: str = f"{'=' * 142}"
    separator: str = f"{'=' * 100}"

    log_message(f"\n{full_separator}", level=level, stacklevel=stacklevel)
    log_message(f"{message}", level=level, stacklevel=stacklevel)
    log_message(separator, level=level, stacklevel=stacklevel)

