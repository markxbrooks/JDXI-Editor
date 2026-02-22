"""Global configuration and settings for JD-Xi Editor."""

import logging
from pathlib import Path

from PySide6.QtCore import QSettings

from jdxi_editor.project import __organization_name__, __package_name__, __program__

settings = QSettings(__organization_name__, __program__)

LOGGING = bool(settings.value("logging", True, type=bool))
PROFILING = True
logger = logging.getLogger(__package_name__)

LOG_PADDING_WIDTH = 55

BASE_DIR = Path(__file__).resolve().parent
