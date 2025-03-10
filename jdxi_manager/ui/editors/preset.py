"""
Preset Editor Module

This module defines the `PresetEditor` class, a PySide6-based GUI component for managing and editing
synthesizer presets. The `PresetEditor` allows users to select, load, and modify presets, integrating
MIDI communication for real-time parameter updates.

Classes:
    - PresetEditor: A `QMainWindow` subclass that provides an interface for selecting and managing
      synthesizer presets, handling MIDI interactions, and updating UI elements accordingly.

Signals:
    - preset_changed(int, str, int): Emitted when a preset is selected or changed.
      It provides the preset index, name, and MIDI channel.

Features:
    - Preset selection via a combo box categorized by preset type (Analog, Digital 1, Digital 2, Drums).
    - Integration with a `MIDIHelper` for sending and receiving MIDI messages.
    - Dynamic UI updates based on MIDI parameter changes.
    - Saves user-selected preset type and preset number using `QSettings`.
    - Supports different preset lists based on the selected preset type.

Usage:
    ```python
    from PySide6.QtWidgets import QApplication
    from midi_helper import MIDIHelper
    import sys

    app = QApplication(sys.argv)
    midi_helper = MIDIHelper()
    editor = PresetEditor(midi_helper)
    editor.show()
    sys.exit(app.exec())
    ```

Dependencies:
    - PySide6 (for UI components)
    - MIDIHelper (for MIDI communication)
    - ParameterHandler (for handling and updating MIDI parameters)
    - PresetLoader (for loading preset data)
    - QSettings (for storing user preferences)
"""

import logging
from typing import Optional, List, Dict

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QLabel,
    QGroupBox,
)
from PySide6.QtCore import Signal, QSettings

from jdxi_manager.data.presets.data import (
    DIGITAL_PRESETS_ENUMERATED,
    ANALOG_PRESETS_ENUMERATED,
    DRUM_PRESETS_ENUMERATED,
)
from jdxi_manager.data.presets.type import PresetType
from jdxi_manager.midi.io import MIDIHelper
from jdxi_manager.midi.preset.loader import PresetLoader
from jdxi_manager.midi.preset.parameter_handler import ParameterHandler
from jdxi_manager.ui.style import Style
from jdxi_manager.ui.widgets.preset.combo_box import PresetComboBox


class PresetEditor(QMainWindow):
    """Editor window for Presets"""

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
        self.setStyleSheet(Style.JDXI_EDITOR)

        # Create central widget and main layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)  # Add some padding
        main_layout.setSpacing(10)  # Add spacing between widgets
        main_widget.setLayout(main_layout)

        # Create preset control area
        preset_group = QGroupBox("Preset Controls")
        preset_layout = QVBoxLayout()
        preset_group.setLayout(preset_layout)

        # Create preset preset_type selector
        type_row = QHBoxLayout()
        type_row.addWidget(QLabel("Type:"))
        self.type_selector = QComboBox()
        self.type_selector.addItems(
            [
                PresetType.DIGITAL_1,
                PresetType.DIGITAL_2,
                PresetType.ANALOG,
                PresetType.DRUMS,
            ]
        )
        self.settings = QSettings("jdxi_manager", "settings")
        self.type_selector.setCurrentText(preset_type)
        self.type_selector.currentTextChanged.connect(self._on_type_changed)
        type_row.addWidget(self.type_selector)
        preset_layout.addLayout(type_row)

        # Preset ComboBox
        self.preset_combo_box = PresetComboBox(DIGITAL_PRESETS_ENUMERATED)
        self.preset_combo_box.preset_selected.connect(self._on_preset_changed)
        self.preset_combo_box.preset_loaded.connect(self._on_load_clicked)
        preset_layout.addWidget(self.preset_combo_box)

        # Add preset area to main layout
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
        """Get the appropriate preset list based on preset_type"""
        logging.debug(f"Getting preset list for preset_type: {self.preset_type}")
        if self.preset_type == PresetType.ANALOG:
            return ANALOG_PRESETS_ENUMERATED
        if self.preset_type == PresetType.DIGITAL_1:
            return DIGITAL_PRESETS_ENUMERATED
        return DRUM_PRESETS_ENUMERATED

    def _on_type_changed(self, preset_type: str):
        """Handle preset preset_type change"""
        logging.debug(f"Changing preset preset_type to {preset_type}")
        self.preset_type = preset_type
        self.preset_combo_box.set_presets(self._get_preset_list())

    def _on_preset_changed(self, index: int, channel: int):
        """Handle preset selection changes"""
        if index < 0 or index >= len(self.index_mapping):
            logging.error(
                f"Invalid preset index {index}, max is {len(self.index_mapping)-1}"
            )
            return
        try:
            if self.midi_helper:
                self.midi_helper.send_program_change(index, channel)
                # Get the original index from the mapping
                original_index = self.index_mapping[index]
                logging.debug(
                    f"Selected preset index {index} maps to original index {original_index}"
                )
            self.channel = channel
            # Get the preset name without the number prefix
            presets = self._get_preset_list()
            if original_index >= len(presets):
                logging.error(
                    f"Original index {original_index} out of range for presets list "
                    f"(max {len(presets)-1})"
                )
                return

            preset_name = presets[original_index].split(": ")[1]

            # Emit signal with all required information
            self.preset_changed.emit(
                original_index + 1,  # original preset number (1-based)
                preset_name,
                channel,
            )
        except Exception as ex:
            logging.error(
                f"Error in preset change handler: " f"{str(ex)}", exc_info=True
            )

    def _on_load_clicked(self, original_index: int):
        """Handle Load button click"""
        preset_loader = PresetLoader(self.midi_helper)
        preset_data = {
            "preset_type": self.preset_type,
            "selpreset": original_index,
            "modified": 0,
            "channel": self.channel,
        }
        preset_loader.load_preset(preset_data)
        # self.settings.setValue("last_preset/synth_type", self.preset_type)
        # self.settings.setValue("last_preset/preset_num", original_index + 1)

    def _update_ui(self, parameters: Dict[str, int]):
        """Update UI with new parameter values"""
        # not implemented
        try:
            # Example: Update address label or control with address specific parameter
            if "0.0.8" in parameters:  # Example address for address parameter
                value = parameters["0.0.8"]
                self.some_label.setText(f"Parameter 0.0.8: {value}")
        except Exception as ex:
            logging.error(f"Error updating UI: {str(ex)}", exc_info=True)
