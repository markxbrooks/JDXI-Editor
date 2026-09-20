"""Settings gate for MIDI selection cross-validation."""

from jdxi_editor.globals import MIDI_SELECTION_VALIDATION_KEY, settings


def is_midi_selection_validation_enabled() -> bool:
    """True when combo-vs-send validation logging is enabled. Default False."""
    val = settings.value(MIDI_SELECTION_VALIDATION_KEY, False)
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.lower() in ("true", "1", "yes")
    return False
