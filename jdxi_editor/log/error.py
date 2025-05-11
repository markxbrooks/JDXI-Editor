""" log message """
import logging
from typing import Optional

from jdxi_editor.globals import logger, LOGGING
from jdxi_editor.log.decorator import decorate_log_message
from jdxi_editor.log.emoji import LEVEL_EMOJIS


def log_error(
    message: str,
    exception: Optional[Exception] = None,
    level: int = logging.ERROR,
    stacklevel=2,
) -> None:
    """
    Log an error message with emojis based on severity and content keywords.

    :param message: str The message to log.
    :param exception: Optional [str] error message
    :param level: int Logging level (default: logging.ERROR).
    :param stacklevel: int sets the stack level to log the message from the caller's context
    :return: None
    """
    if exception:
        message = f"{message}: {exception}"
    full_message = decorate_log_message(message, level)
    if LOGGING:
        logger.log(level, full_message, stacklevel=stacklevel)
