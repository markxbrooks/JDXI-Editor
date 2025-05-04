"""
Emoji logger formatter for Python's logging module.
This formatter defines emojis to log messages based on their severity level.
"""
import logging

LEVEL_EMOJIS = {
    logging.DEBUG: "🔍",
    logging.INFO: "ℹ️",
    logging.WARNING: "⚠️",
    logging.ERROR: "❌",
    logging.CRITICAL: "💥",
}
