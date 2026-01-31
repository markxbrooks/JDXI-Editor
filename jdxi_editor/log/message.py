"""log message"""

import logging

from decologr import decorate_log_message

from jdxi_editor.globals import LOGGING, logger


def log_message(
    message: str, level: int = logging.INFO, stacklevel: int = 2, silent: bool = False
) -> None:
    """
    Log a message with emojis based on severity and content keywords.

    :param stacklevel: int sets the stack level to log the message from the caller's context
    :param message: str The message to log.
    :param level: int Logging level (default: logging.INFO).
    :param silent: bool
    :return: None
    """
    decorated_message = decorate_log_message(message, level)
    if LOGGING and not silent:
        logger.log(level, decorated_message, stacklevel=stacklevel)
