# log message
import logging

from jdxi_editor.globals import logger
from jdxi_editor.log.emoji import LEVEL_EMOJIS


def log_message(message: str, level: int = logging.INFO) -> None:
    """
    Log a message with an emoji based on the severity level.
    :param message: str message to log
    :param level: int severity level (default: logging.INFO)
    :return: None
    """
    emoji = LEVEL_EMOJIS.get(level, "🔔")
    # Add MIDI flair if message seems MIDI-related
    midi_tag = "🎵" if "midi" in message.lower() or "sysex" in message.lower() else ""
    jdxi_tag = "🎹" if "jdxi" or "jd-xi" in message.lower() in message.lower() else ""
    qc_passed_tag = "✅" if "updat" in message.lower() or "success" in message.lower() else ""
    full_message = f"{emoji}{jdxi_tag}{qc_passed_tag}{midi_tag} {message}"
    logger.log(level, full_message, stacklevel=2)
