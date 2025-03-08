from typing import Optional, Dict

from PySide6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QComboBox,
    QGroupBox,
    QPushButton,
    QWidget
)
from PySide6.QtCore import Signal
from jdxi_manager.ui.editors.synth import SynthEditor
from jdxi_manager.midi.io import MIDIHelper
from jdxi_manager.data.presets.type import PresetType
from jdxi_manager.midi.preset.handler import PresetHandler
from jdxi_manager.ui.style import Style


class ProgramEditor(QMainWindow):
    program_changed = Signal(int, str, int)  # (channel, preset_name, program_number)

    def __init__(
        self,
        midi_helper: Optional[MIDIHelper] = None,
        parent: Optional[QWidget] = None,
        preset_handler: PresetHandler = None,
    ):
        super().__init__(parent)
        self.midi_helper = midi_helper
        self.channel = 1  # Default MIDI channel
        self.preset_type = None
        self.preset_handler = preset_handler
        self.programs = {}  # Maps program names to numbers
        self.setup_ui()
        self.populate_programs()
        self.show()

    def setup_ui(self):
        self.setWindowTitle("Program Editor")
        self.setMinimumSize(400, 400)
        center_widget = QWidget()
        layout = QVBoxLayout()
        self.setCentralWidget(center_widget)
        center_widget.setLayout(layout)
        self.setStyleSheet(Style.JDXI_PATCH_MANAGER)
        # Program selection combo box
        self.program_combo_box = QComboBox()
        self.program_combo_box.currentIndexChanged.connect(self.on_program_changed)
        layout.addWidget(self.program_combo_box)    

        # Program parameters group box
        self.program_group_box = QGroupBox("Program Parameters")
        self.program_group_box.setLayout(QVBoxLayout())
        layout.addWidget(self.program_group_box)

        # Save button
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.on_save_clicked)
        layout.addWidget(self.save_button)

        self.setLayout(layout)  

    def populate_programs(self):
        """Populate the program list with available presets."""
        if not self.preset_handler:
            return
        presets = None
        presets = self.preset_handler.get_available_presets()  # Fetch presets
        self.program_combo_box.clear()
        self.programs.clear()

        for number, preset in enumerate(presets):
            self.program_combo_box.addItem(preset, number)
            self.programs[preset] = number

    def on_program_changed(self, index: int):
        """Handle program selection change."""
        if index < 0 or not self.midi_helper:
            return

        program_number = self.program_combo_box.itemData(index)
        program_name = self.program_combo_box.currentText()

        # Send Program Change message
        self.midi_helper.send_program_change(self.channel, program_number)

        # Load the selected preset
        self.load_preset(program_number)

        self.program_changed.emit(self.channel, program_name, program_number)

    def load_preset(self, program_number: int):
        """Load preset data and update UI."""
        if not self.preset_handler:
            return

        preset_data = self.preset_handler.load_preset(program_number)
        if preset_data:
            self._update_ui(preset_data)

    def on_save_clicked(self):
        """Save the modified preset parameters."""
        if not self.preset_handler:
            return

        # Collect parameters from the UI
        parameters = self._collect_ui_data()

        # Get the current program number from the combo box
        current_index = self.program_combo_box.currentIndex()
        program_number = self.program_combo_box.itemData(current_index)

        # Call save_preset with both parameters and program_number
        self.preset_handler.save_preset(program_number, parameters)

    def _update_ui(self, parameters: Dict[str, int]):
        """Update UI elements based on loaded preset data."""
        # TODO: Implement UI updates for parameters

    def _collect_ui_data(self) -> Dict[str, int]:
        """Collect updated UI parameter values."""
        # TODO: Extract parameter values from UI
        return {}

    def _update_program_list(self):
        """Update the program list with available presets."""
        self.populate_programs()

    def _update_program_display(self, program_name: str, program_number: int):
        """Update the program display with the selected program name and number."""
        self.program_combo_box.setCurrentText(program_name)

    def save_preset(self, parameters: dict, program_number: int):
        """Save the current preset to the preset list."""
        # Ensure program_number is a valid index
        if 0 <= program_number < len(self.presets):
            self.presets[program_number] = parameters  # Use program_number as the index
            self.preset_changed.emit(self.current_preset_index, self.channel)
            self.update_display.emit(self.type, self.current_preset_index, self.channel)
            return self.get_current_preset()
        else:
            raise IndexError("Program number out of range")