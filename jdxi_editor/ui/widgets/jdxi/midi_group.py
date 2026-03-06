"""
USB Recording Widget
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import pyaudio
from decologr import Decologr as log
from PySide6.QtCore import QMargins, Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.playback.state import MidiPlaybackState
from jdxi_editor.midi.utils.helpers import start_recording
from jdxi_editor.midi.utils.usb_recorder import USBRecorder
from jdxi_editor.ui.editors.helpers.widgets import create_jdxi_button_from_spec
from jdxi_editor.ui.editors.midi_player.helper import (
    create_widget_cell_with_button_spec,
)
from jdxi_editor.ui.widgets.editor.helper import (
    create_group_and_grid_layout,
    create_icon_and_label,
)
from jdxi_editor.ui.windows.jdxi.utils import show_message_box_from_spec
from picoui.specs.widgets import (
    ButtonSpec,
    FileSelectionMode,
    FileSelectionSpec,
    get_file_save_from_spec,
)


class JDXiMidiGroup(QWidget):
    """JDXi Midi Widget"""

    def __init__(self, midi_state: MidiPlaybackState, parent: "MidiFilePlayer"):
        super().__init__()
        """constructor"""
        self.parent = parent
        self.midi_state = midi_state
        self.group_title: str | None = None
        self.specs: dict = self._build_specs()

    def setup_ui(self):
        """Set up UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
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
