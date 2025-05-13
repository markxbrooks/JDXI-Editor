""" log message """

import logging

from jdxi_editor.globals import logger, LOGGING
from jdxi_editor.log.decorator import decorate_log_message


def log_message(message: str, level: int = logging.INFO, stacklevel=2, silent=False) -> None:
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
