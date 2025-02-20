from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QLabel,
    QPushButton,
    QLineEdit,
    QGroupBox,
    QMessageBox,
)
from PySide6.QtCore import Signal, Qt, QSettings
from PySide6.QtGui import QFont
from typing import Optional, List, Dict
import logging
import time

from jdxi_manager.midi import MIDIHelper

# from jdxi_manager.ui.editors.base import BaseEditor
from jdxi_manager.midi.constants import (
    DIGITAL_SYNTH_AREA,
    ANALOG_SYNTH_AREA,
    DRUM_KIT_AREA,
    DT1_COMMAND_12,
    RQ1_COMMAND_11,
)
from jdxi_manager.ui.style import Style
from jdxi_manager.data.preset_type import PresetType
from jdxi_manager.midi.preset_loader import PresetLoader
from jdxi_manager.midi.parameter_handler import ParameterHandler
from jdxi_manager.data.preset_data import DIGITAL_PRESETS, ANALOG_PRESETS, DRUM_PRESETS
from jdxi_manager.ui.widgets.preset_combo_box import PresetComboBox


class PresetEditor(QMainWindow):
    preset_changed = Signal(int, str, int)

    def __init__(
        self,
        midi_helper: Optional[MIDIHelper] = None,
        parent: Optional[QWidget] = None,
        preset_type: str = PresetType.ANALOG,
    ):
        super().__init__(parent)
        self.setMinimumSize(400, 800)
        self.setWindowTitle("Preset Editor")
        self.midi_helper = midi_helper
        self.channel = 1  # Default channel
        self.preset_type = preset_type
        self.parameter_handler = ParameterHandler()

        if midi_helper:
            midi_helper.midi_parameter_changed.connect(
                self.parameter_handler.update_parameter
            )
            self.parameter_handler.parameters_updated.connect(self._update_ui)

        # Set window style
        self.setStyleSheet(Style.EDITOR_STYLE)

        # Create central widget and main layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)  # Add some padding
        main_layout.setSpacing(10)  # Add spacing between widgets
        main_widget.setLayout(main_layout)

        # Create preset control group
        preset_group = QGroupBox("Preset Controls")
        preset_layout = QVBoxLayout()
        preset_group.setLayout(preset_layout)

        # Create preset type selector
        type_row = QHBoxLayout()
        type_row.addWidget(QLabel("Type:"))
        self.type_selector = QComboBox()
        self.type_selector.addItems(
            [
                PresetType.ANALOG,
                PresetType.DIGITAL_1,
                PresetType.DIGITAL_2,
                PresetType.DRUMS,
            ]
        )
        self.settings = QSettings("jdxi_manager", "settings")
        self.type_selector.setCurrentText(preset_type)
        self.type_selector.currentTextChanged.connect(self._on_type_changed)
        type_row.addWidget(self.type_selector)
        preset_layout.addLayout(type_row)

        # Preset ComboBox
        self.preset_combo_box = PresetComboBox(DIGITAL_PRESETS)
        self.preset_combo_box.preset_selected.connect(self._on_preset_changed)
        self.preset_combo_box.preset_loaded.connect(self._on_load_clicked)
        preset_layout.addWidget(self.preset_combo_box)

        # Add preset group to main layout
        main_layout.addWidget(preset_group)

        # Set as central widget
        self.setCentralWidget(main_widget)

        # Adjust window size to fit content
        self.adjustSize()
        self.setFixedHeight(self.sizeHint().height())

        # Store the full preset list and mapping
        self.full_preset_list = self._get_preset_list()
        # Create mapping of display index to original index
        self.index_mapping = list(range(len(self.full_preset_list)))

    def _get_preset_list(self) -> List[str]:
        """Get the appropriate preset list based on type"""
        logging.debug(f"Getting preset list for type: {self.preset_type}")
        if self.preset_type == PresetType.ANALOG:
            return ANALOG_PRESETS
        elif self.preset_type == PresetType.DIGITAL_1:
            return DIGITAL_PRESETS
        else:
            return DRUM_PRESETS

    def _on_type_changed(self, preset_type: str):
        """Handle preset type change"""
        logging.debug(f"Changing preset type to {preset_type}")
        self.preset_type = preset_type
        self.preset_combo_box.set_presets(self._get_preset_list())

    def _on_preset_changed(self, index: int):
        """Handle preset selection changes"""
        if index < 0 or index >= len(self.index_mapping):
            logging.error(
                f"Invalid preset index {index}, max is {len(self.index_mapping)-1}"
            )
            return
        try:
            if self.midi_helper:
                # Get the original index from the mapping
                original_index = self.index_mapping[index]
                logging.debug(
                    f"Selected preset index {index} maps to original index {original_index}"
                )

                # TODO: Add MIDI handling for preset changes using original_index
                pass

            # Get the preset name without the number prefix
            presets = self._get_preset_list()
            if original_index >= len(presets):
                logging.error(
                    f"Original index {original_index} out of range for presets list (max {len(presets)-1})"
                )
                return

            preset_name = presets[original_index].split(": ")[1]

            # Emit signal with all required information
            self.preset_changed.emit(
                original_index + 1,  # original preset number (1-based)
                preset_name,
                self.channel,
            )
        except Exception as e:
            logging.error(f"Error in preset change handler: {str(e)}", exc_info=True)

    def _on_load_clicked(self, original_index: int):
        """Handle Load button click"""
        preset_loader = PresetLoader(self.midi_helper)
        preset_data = {
            "type": self.preset_type,
            "selpreset": original_index + 1,  # Convert to 1-based index
            "modified": 0,
        }
        preset_loader.load_preset(preset_data)
        self.settings.setValue("last_preset/synth_type", self.preset_type)
        self.settings.setValue("last_preset/preset_num", original_index + 1)

    def _update_ui(self, parameters: Dict[str, int]):
        """Update UI with new parameter values"""
        try:
            # Example: Update a label or control with a specific parameter
            # Assuming you have a QLabel or similar widget to display parameter values
            if "0.0.8" in parameters:  # Example address for a parameter
                value = parameters["0.0.8"]
                self.some_label.setText(f"Parameter 0.0.8: {value}")

            # Update other UI elements as needed
            # if '0.1.0' in parameters:
            #     value = parameters['0.1.0']
            #     self.another_control.setValue(value)

        except Exception as e:
            logging.error(f"Error updating UI: {str(e)}", exc_info=True)
