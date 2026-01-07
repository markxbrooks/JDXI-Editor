"""log footer message"""

import logging

from jdxi_editor.log.message import log_message


def log_footer_message(message: str, level: int = logging.INFO) -> None:
    """
    Logs a highlighted footer message with separators for visibility.

    :param message: The message to log.
    :param level: Logging level (default: logging.INFO).
    """
    stacklevel = 3
    separator = "=" * 100
    log_message(f"  {message}", level=level, stacklevel=stacklevel)
    log_message(separator, level=level, stacklevel=stacklevel)
