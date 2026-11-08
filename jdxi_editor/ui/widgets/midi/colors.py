"""Muted MIDI channel colours for the timeline (UI_CRITIQUE Phase 2)."""

from PySide6.QtGui import QColor

from jdxi_editor.ui.style.midi_player import MidiPlayerStyle


def _channel_colors() -> dict[int, QColor]:
    return {
        ch: QColor(*rgba) for ch, rgba in MidiPlayerStyle.CHANNEL_COLORS.items()
    }


MIDI_CHANNEL_COLORS = _channel_colors()
