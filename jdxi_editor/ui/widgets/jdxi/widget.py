"""
USB Recording Widget
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import pyaudio
from PySide6.QtCore import Qt, QMargins
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QCheckBox, QComboBox, QGridLayout, QHBoxLayout

from decologr import Decologr as log
from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.playback.state import MidiPlaybackState
from jdxi_editor.midi.utils.helpers import start_recording
from jdxi_editor.midi.utils.usb_recorder import USBRecorder
from jdxi_editor.ui.editors.helpers.widgets import create_jdxi_button_from_spec
from jdxi_editor.ui.editors.midi_player.helper import create_widget_cell_with_button_spec
from jdxi_editor.ui.widgets.editor.helper import create_icon_and_label, create_group_and_grid_layout
from jdxi_editor.ui.windows.jdxi.utils import show_message_box_from_spec
from picoui.specs.widgets import ButtonSpec, FileSelectionSpec, FileSelectionMode, get_file_save_from_spec


class JDXiMidiGrid(QWidget):
    """JDXi Midi Grid"""

    def __init__(self, midi_state: MidiPlaybackState, parent: QWidget):
        super().__init__()
        """constructor"""
        self.parent = parent
        self.grid_title: str | None = None
        self.layout: QGridLayout | None = None
        self.midi_state = midi_state
        self.specs = self._build_specs()

    def setup_ui(self):
        """Set up UI"""
        row = 0
        layout = QHBoxLayout(self)
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
        group, grid = create_group_and_grid_layout(self.grid_title)
        layout.addWidget(group)
        self._build_layout(grid, row)

    def _build_specs(self) -> dict[str, Any]:
        """build specs for the Midi file player"""
        return {
            "buttons": self._build_button_specs(),
        }

    def _build_button_specs(self) -> dict[str, ButtonSpec]:
        raise NotImplementedError("Must be implemented by subclass")

    def _build_layout(self, grid: QGridLayout, row: int):
        """build layout"""
        raise NotImplementedError("Must be implemented by subclass")
