""" log message """
import logging

from jdxi_editor.globals import logger, LOGGING
from jdxi_editor.log.emoji import LEVEL_EMOJIS


def log_message(message: str, level: int = logging.INFO, stacklevel=2, silent=False) -> None:
    """
    Log a message with emojis based on severity and content keywords.

    :param stacklevel: int sets the stack level to log the message from the caller's context
    :param message: str The message to log.
    :param level: int Logging level (default: logging.INFO).
    :param silent: bool
    :return: None
    """
    # msg_lower = message.lower()

    emoji = LEVEL_EMOJIS.get(level, "🔔")
    midi_tag = "🎵" if "midi" in message or "sysex" in message else ""
    jdxi_tag = "🎹" if "jdxi" in message or "jd-xi" in message else ""
    qc_passed_tag = "✅" if "update" in message or "success" in message else ""
    qc_failed_tag = "❌" if "fail" in message else ""

    # Combine emoji tags, then append message
    tags = f"{emoji}{jdxi_tag}{qc_passed_tag}{qc_failed_tag}{midi_tag}"
    full_message = f"{tags} {message}".strip()
    if LOGGING and not silent:
        logger.log(level, full_message, stacklevel=stacklevel)
