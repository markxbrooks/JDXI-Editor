"""Global configuration and settings for JD-Xi Editor."""

import logging

from PySide6.QtCore import QSettings

from jdxi_editor.project import (
    __organization_name__,
    __package_name__,
    __program__,
    __project__,
    __version__,
)

settings = QSettings(__organization_name__, __program__)

LOGGING = bool(settings.value("logging", True, type=bool))
PROFILING = False
logger = logging.getLogger(__package_name__)

LOG_PADDING_WIDTH = 55
