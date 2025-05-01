""" log message """
import logging

from jdxi_editor.globals import logger
from jdxi_editor.log.emoji import LEVEL_EMOJIS


def log_message(message: str, level: int = logging.INFO) -> None:
    """
    Log a message with emojis based on severity and content keywords.

    :param message: The message to log.
    :param level: Logging level (default: logging.INFO).
    """
    msg_lower = message.lower()

    emoji = LEVEL_EMOJIS.get(level, "🔔")
    midi_tag = "🎵" if "midi" in msg_lower or "sysex" in msg_lower else ""
    jdxi_tag = "🎹" if "jdxi" in msg_lower or "jd-xi" in msg_lower else ""
    qc_passed_tag = "✅" if "update" in msg_lower or "success" in msg_lower else ""
    qc_failed_tag = "❌" if "fail" in msg_lower else ""

    # Combine emoji tags, then append message
    tags = f"{emoji}{jdxi_tag}{qc_passed_tag}{qc_failed_tag}{midi_tag}"
    full_message = f"{tags} {message}".strip()

    logger.log(level, full_message, stacklevel=2)

