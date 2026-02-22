"""Global configuration and settings for JD-Xi Editor."""

import logging
from pathlib import Path

from PySide6.QtCore import QSettings

from jdxi_editor.project import __organization_name__, __package_name__, __program__

settings = QSettings(__organization_name__, __program__)

LOGGING = False # bool(settings.value("logging", True, type=bool))

# Key for user preference: when True, note-on/note-off messages are not logged (reduces log volume).
SILENCE_MIDI_NOTE_LOGGING_KEY = "silence_midi_note_logging"


def silence_midi_note_logging() -> bool:
    """True if the user has chosen to silence logging of MIDI note on/off messages. Default True (silence)."""
    val = settings.value(SILENCE_MIDI_NOTE_LOGGING_KEY, True)
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.lower() in ("true", "1", "yes")
    return True
PROFILING = True
logger = logging.getLogger(__package_name__)

LOG_PADDING_WIDTH = 55

BASE_DIR = Path(__file__).resolve().parent
