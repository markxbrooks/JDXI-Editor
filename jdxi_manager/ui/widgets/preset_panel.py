from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
)
from PySide6.QtCore import Signal
import logging

from jdxi_manager.ui.style import Style
from jdxi_manager.midi import MIDIHelper
from jdxi_manager.ui.editors.preset import PresetEditor
from jdxi_manager.data.preset_type import PresetType


class PresetPanel(QWidget):
    """Panel for loading/saving presets"""

    # Define signals
    load_clicked = Signal(int)  # Emits preset number when load clicked
    save_clicked = Signal(int)  # Emits preset number when save clicked

    def __init__(self, midi_helper: MIDIHelper, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)

        # Preset selector
        self.preset_combo = QComboBox()
        layout.addWidget(self.preset_combo)

        # Load button
        load_btn = QPushButton("Load")
        load_btn.clicked.connect(self._on_load)
        layout.addWidget(load_btn)

        # Save button
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._on_save)
        layout.addWidget(save_btn)

        # Create preset editors for each type
        self.analog_editor = PresetEditor(midi_helper, self, PresetType.ANALOG)
        self.digital_1_editor = PresetEditor(midi_helper, self, PresetType.DIGITAL_1)
        self.digital_2_editor = PresetEditor(midi_helper, self, PresetType.DIGITAL_2)
        self.drums_editor = PresetEditor(midi_helper, self, PresetType.DRUMS)

    def _on_load(self):
        """Handle load button click"""
        preset_num = self.preset_combo.currentIndex()
        self.load_clicked.emit(preset_num)

    def _on_save(self):
        """Handle save button click"""
        preset_num = self.preset_combo.currentIndex()
        self.save_clicked.emit(preset_num)
