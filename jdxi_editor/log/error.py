""" log message """
import logging
from typing import Optional

from jdxi_editor.globals import logger, LOGGING
from jdxi_editor.log.emoji import LEVEL_EMOJIS


def log_error(message: str, error_message: Optional[str] = None, level: int = logging.ERROR, stacklevel=2) -> None:
    """
    Log an error message with emojis based on severity and content keywords.

    :param stacklevel: int sets the stack level to log the message from the caller's context
    :param error_message: Optional [str] error message
    :param message: str The message to log.
    :param level: int Logging level (default: logging.ERROR).
    :return: None
    """
    if error_message:
        message = f"{message}: {error_message}"
    emoji = LEVEL_EMOJIS.get(level, "🔔")
    midi_tag = "🎵" if "midi" in message or "sysex" in message else ""
    jdxi_tag = "🎹" if "jdxi" in message or "jd-xi" in message else ""
    qc_passed_tag = "✅" if "update" in message or "success" in message else ""
    qc_failed_tag = "❌" if "fail" in message else ""

    # Combine emoji tags, then append message
    tags = f"{emoji}{jdxi_tag}{qc_passed_tag}{qc_failed_tag}{midi_tag}"
    full_message = f"{tags} {message}".strip()
    if LOGGING:
        logger.log(level, full_message, stacklevel=stacklevel)

