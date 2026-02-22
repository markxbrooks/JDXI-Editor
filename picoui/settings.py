"""
This module provides centralised keys/constants for various purposes such as
environment variables, map types, logging levels, and preference settings
used in the application.

It includes a set of classes that contain standardised constants and values
to ensure consistent handling of these elements across the program.
"""

from __future__ import annotations

import logging
from typing import ClassVar
from PySide6.QtCore import QSettings

from decologr import Decologr as log
from jdxi_editor.project import __project__, __program__


class PicoUIConstants:
    """Centralised keys/constants for preferences keys and environment vars."""

    PROJECT: ClassVar[str] = __project__
    PROGRAM: ClassVar[str] = __program__

    CONFIG_KEYS = {
        "LOG_LEVEL": "log_level",
        # Add other constants here
    }


class PicoUISettings:
    """Centralised keys/constants for preferences keys and environment vars."""

    PROJECT: ClassVar[str] = __project__
    PROGRAM: ClassVar[str] = __program__
    LOG_LEVEL = "log_level"
    FONT = "font"


class PicoUIConfig:
    """Handles dynamic configs and persistent changes."""

    def __init__(self):
        self.settings = QSettings(PicoUIConstants.PROJECT, PicoUIConstants.PROGRAM)
        self.log_levels = {
            0: logging.NOTSET,
            1: logging.DEBUG,
            2: logging.INFO,
            # Extend as needed
        }

    def update_log_level(self, index: int) -> None:
        """
        Updates the log level in persistent settings and applies globally.

        Args:
            index (int): The log level index to set.

        Raises:
            ValueError: If the index is out of range.
        """
        if index not in self.log_levels:
            raise ValueError(f"Invalid log level index: {index}")

        log_level = self.log_levels[index]
        self.settings.setValue(PicoUIConstants.CONFIG_KEYS["LOG_LEVEL"], log_level)

        log.message(f"Log level updated to {log_level}")
        logging.getLogger(PicoUIConstants.PROJECT).setLevel(log_level)