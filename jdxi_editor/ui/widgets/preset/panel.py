"""
Panel for loading/saving presets
"""

from typing import Any, Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton
)

from jdxi_editor.ui.common import JDXi, QWidget
from jdxi_editor.core.synth.type import JDXiSynth
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.helpers.widgets import create_jdxi_button, create_jdxi_row
from jdxi_editor.ui.editors.preset.editor import PresetEditor
from jdxi_editor.ui.style import JDXiUIDimensions, JDXiUIStyle


class PresetPanel(QWidget):
    """Panel for loading/saving presets"""

    # Define signals
    load_clicked = Signal(int)  # Emits preset number when load clicked
    save_clicked = Signal(int)  # Emits preset number when save clicked

    def __init__(self, midi_helper: MidiIOHelper, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)

        # Preset selector
        self.preset_combo = QComboBox()
        layout.addWidget(self.preset_combo)

        # Load (round button + label)
        load_row = QHBoxLayout()
        self.load_button = self._add_round_action_button(
            JDXi.UI.Icon.FOLDER_NOTCH_OPEN,
            "Load",
            self._on_load,
            load_row,
            name="load"
)
        layout.addLayout(load_row)

        # Save (round button + label)
        save_row = QHBoxLayout()
        self.save_button = self._add_round_action_button(
            JDXi.UI.Icon.FLOPPY_DISK,
            "Save",
            self._on_save,
            save_row,
            name="save"
)
        layout.addLayout(save_row)

        # Create preset editors for each preset_type
        self.analog_editor = PresetEditor(midi_helper, self, JDXiSynth.ANALOG_SYNTH)
        self.digital_1_editor = PresetEditor(
            midi_helper, self, JDXiSynth.DIGITAL_SYNTH_1
        )
        self.digital_2_editor = PresetEditor(
            midi_helper, self, JDXiSynth.DIGITAL_SYNTH_2
        )
        self.drums_editor = PresetEditor(midi_helper, self, JDXiSynth.DRUM_KIT)

    def _add_round_action_button(
        self,
        icon_enum: Any,
        text: str,
        slot: Any,
        layout: QHBoxLayout,
        *,
        name: Optional[str] = None,
        checkable: bool = False
) -> QPushButton:
        """Create a round button with icon + text label (same style as Transport)."""
        btn = create_jdxi_button("")
        btn.setCheckable(checkable)
        if slot is not None:
            btn.clicked.connect(slot)
        if name:
            setattr(self, f"{name}_button", btn)
        layout.addWidget(btn)
        pixmap = JDXi.UI.Icon.get_icon_pixmap(
            icon_enum, color=JDXi.UI.Style.FOREGROUND, size=20
        )
        label_row, _ = create_jdxi_row(text, icon_pixmap=pixmap)
        layout.addWidget(label_row)
        return btn

    def _on_load(self):
        """Handle load button click"""
        preset_num = self.preset_combo.currentIndex()
        self.load_clicked.emit(preset_num)  # convert from 0-based index

    def _on_save(self):
        """Handle save button click"""
        preset_num = self.preset_combo.currentIndex()
        self.save_clicked.emit(preset_num)
