""" log header message """
import logging

from jdxi_editor.log.message import log_message


def log_header_message(message: str, level: int = logging.INFO) -> None:
    """
    Log a message with emojis based on severity and content keywords.

    :param message: The message to log.
    :param level: Logging level (default: logging.INFO).
    """
    stacklevel = 3
    log_message("\n======================================================================================================================================", level=level, stacklevel=stacklevel)
    log_message(f"  {message}", level=level, stacklevel=stacklevel)
    log_message("============================================================================================", level=level, stacklevel=stacklevel)

