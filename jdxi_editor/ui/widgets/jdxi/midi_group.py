"""
JDXiMidiGroup - Base class for spec-driven MIDI-related UI groups.
"""

from typing import Any, Optional

from PySide6.QtCore import QMargins
from PySide6.QtWidgets import QVBoxLayout, QWidget

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.playback.state import MidiPlaybackState
from picoui.specs.widgets import ButtonSpec


class JDXiMidiGroup(QWidget):
    """JDXi Midi Widget - spec-driven group with optional midi_state and generic parent."""

    def __init__(
        self,
        parent: Optional["MidiFilePlayer"] = None,
        midi_state: Optional[MidiPlaybackState] = None,
    ):
        super().__init__()
        self.parent = parent
        self.margins: QMargins = JDXi.UI.Dimensions.group.MARGINS
        self.spacing: int = JDXi.UI.Dimensions.group.SPACING
        self.midi_state = midi_state
        self.group_title: Optional[str] = None
        self.specs: dict = self._build_specs()

    def setup_ui(self):
        """Set up UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(self.margins)
        layout.setSpacing(self.spacing)
        group = self._build_group()
        layout.addWidget(group)

    def _build_specs(self) -> dict[str, Any]:
        """build specs for the Midi file player"""
        return {
            "buttons": self._build_button_specs(),
            "message_box": self._build_message_box_specs(),
            "check_box": self._build_check_box_specs(),
            "transport": self._build_transport_specs(),
        }

    def _build_button_specs(self) -> dict[str, ButtonSpec]:
        raise NotImplementedError("Must be implemented by subclass")

    def _build_message_box_specs(self) -> dict[str, Any]:
        pass

    def _build_check_box_specs(self) -> dict[str, Any]:
        pass

    def _build_transport_specs(self) -> dict[str, Any]:
        pass

    def _build_group(self):
        """build layout"""
        raise NotImplementedError("Must be implemented by subclass")
