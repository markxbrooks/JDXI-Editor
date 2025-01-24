from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QComboBox, QLabel, QPushButton, QLineEdit, QGroupBox, QMessageBox
)
from PySide6.QtCore import Signal, Qt, QSettings
from PySide6.QtGui import QFont
from typing import Optional, List, Dict
import logging
import time

from jdxi_manager.midi import MIDIHelper
from jdxi_manager.ui.editors.base_editor import BaseEditor
from jdxi_manager.midi.constants import (
    DIGITAL_SYNTH_AREA,
    ANALOG_SYNTH_AREA,
    DRUM_KIT_AREA,
    DT1_COMMAND_12,
    RQ1_COMMAND_11
)
from jdxi_manager.ui.style import Style
from jdxi_manager.data.preset_type import PresetType
from jdxi_manager.midi.preset_loader import PresetLoader
from jdxi_manager.midi.parameter_handler import ParameterHandler
from jdxi_manager.data.preset_data import (DIGITAL_PRESETS, ANALOG_PRESETS, DRUM_PRESETS)

class PresetEditor(QMainWindow):
    preset_changed = Signal(int, str, int)

    def __init__(self, midi_helper: Optional[MIDIHelper] = None, parent: Optional[QWidget] = None, preset_type: str = PresetType.ANALOG):
        super().__init__(parent)
        self.setMinimumSize(400, 800)
        self.setWindowTitle("Preset Editor")
        self.midi_helper = midi_helper
        self.channel = 1  # Default channel
        self.preset_type = preset_type
        self.parameter_handler = ParameterHandler()
        
        if midi_helper:
            midi_helper.parameter_received.connect(self.parameter_handler.update_parameter)
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
        self.type_selector.addItems([
            PresetType.ANALOG,
            PresetType.DIGITAL_1,
            PresetType.DIGITAL_2,
            PresetType.DRUMS
        ])
        self.settings = QSettings("jdxi_manager", "settings")
        self.type_selector.setCurrentText(preset_type)
        self.type_selector.currentTextChanged.connect(self._on_type_changed)
        type_row.addWidget(self.type_selector)
        preset_layout.addLayout(type_row)
        
        # Create search box
        search_row = QHBoxLayout()
        search_row.addWidget(QLabel("Search:"))
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search presets...")
        self.search_box.textChanged.connect(self._filter_presets)
        search_row.addWidget(self.search_box)
        preset_layout.addLayout(search_row)
        
        # Create preset selector
        preset_row = QHBoxLayout()
        preset_row.addWidget(QLabel("Preset:"))
        self.preset_selector = QComboBox()
        self.preset_selector.currentIndexChanged.connect(self._on_preset_changed)
        self.preset_selector.setMinimumWidth(200)
        
        # Initialize with first preset selected
        self._update_preset_list()
        if self.preset_selector.count() > 0:
            self.preset_selector.setCurrentIndex(0)
        preset_row.addWidget(self.preset_selector)
        preset_layout.addLayout(preset_row)
        
        # Create bank and slot frame that's only visible when saving
        #self.save_frame = QGroupBox("Save Settings")
        #save_layout = QVBoxLayout()
        #self.save_frame.setLayout(save_layout)
        # self.save_frame.setVisible(False)  # Hidden by default
        
        # Add bank selector to save frame
        #bank_row = QHBoxLayout()
        #bank_row.addWidget(QLabel("Bank:"))
        #self.bank_selector = QComboBox()
        #self.bank_selector.addItems(['E', 'F', 'G', 'H'])  # Only show user banks
        #bank_row.addWidget(self.bank_selector)
        #save_layout.addLayout(bank_row)
        
        # Add slot selector to save frame
        #slot_row = QHBoxLayout()
        #slot_row.addWidget(QLabel("Slot:"))
        #self.slot_selector = QComboBox()
        #self.slot_selector.addItems([f"{i:02d}" for i in range(1, 65)])
        #slot_row.addWidget(self.slot_selector)
        #save_layout.addLayout(slot_row)
        
        # Create button row
        button_row = QHBoxLayout()
        self.load_button = QPushButton("Load")
        self.load_button.clicked.connect(self._on_load_clicked)
        #self.save_button = QPushButton("Save...")
        #self.save_button.clicked.connect(self._toggle_save_frame)
        #self.confirm_save_button = QPushButton("Confirm Save")
        #self.confirm_save_button.clicked.connect(self._on_save_clicked)
        button_row.addWidget(self.load_button)
        #button_row.addWidget(self.save_button)
        
        # Add buttons to layouts
        preset_layout.addLayout(button_row)
        #save_layout.addWidget(self.confirm_save_button)
        
        # Add save frame to preset layout
        #preset_layout.addWidget(self.save_frame)
        
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
        else:  # PresetType.DRUMS
            return DRUM_PRESETS

    def _filter_presets(self, search_text: str):
        """Filter presets based on search text"""
        # Temporarily disconnect the signal
        self.preset_selector.currentIndexChanged.disconnect(self._on_preset_changed)
        
        if not search_text:
            # If search is empty, show all presets
            filtered_presets = self.full_preset_list
            self.index_mapping = list(range(len(self.full_preset_list)))
        else:
            # Filter presets that contain the search text (case-insensitive)
            search_text = search_text.lower()
            filtered_indices = [
                i for i, preset in enumerate(self.full_preset_list)
                if search_text in preset.lower()
            ]
            filtered_presets = [self.full_preset_list[i] for i in filtered_indices]
            self.index_mapping = filtered_indices
        
        # Update the preset selector with filtered items
        self.preset_selector.clear()
        self.preset_selector.addItems([
            preset.split(': ')[1] for preset in filtered_presets
        ])
        
        # Reconnect the signal and select first item if available
        self.preset_selector.currentIndexChanged.connect(self._on_preset_changed)
        if self.preset_selector.count() > 0:
            self.preset_selector.setCurrentIndex(0)

    def _update_preset_list(self):
        """Update the preset selector with appropriate list"""
        # Temporarily disconnect the signal to prevent -1 index
        self.preset_selector.currentIndexChanged.disconnect(self._on_preset_changed)
        
        self.full_preset_list = self._get_preset_list()
        # Reset the index mapping when updating preset list
        self.index_mapping = list(range(len(self.full_preset_list)))
        
        self.preset_selector.clear()
        self.preset_selector.addItems([
            preset.split(': ')[1] for preset in self.full_preset_list
        ])
        
        # Reconnect the signal
        self.preset_selector.currentIndexChanged.connect(self._on_preset_changed)

    def _on_type_changed(self, preset_type: str):
        """Handle preset type change"""
        logging.debug(f"Changing preset type to {preset_type}")
        self.preset_type = preset_type
        self.search_box.clear()  # Clear search when changing type
        # Update preset list and reset mapping
        self._update_preset_list()
        # Select first preset if available
        if self.preset_selector.count() > 0:
            self.preset_selector.setCurrentIndex(0)

    def _on_preset_changed(self, index: int):
        """Handle preset selection changes"""
        try:
            if index < 0 or index >= len(self.index_mapping):
                logging.warning(f"Invalid preset index {index}, max is {len(self.index_mapping)-1}")
                return
            
            if self.midi_helper:
                # Get the original index from the mapping
                original_index = self.index_mapping[index]
                logging.debug(f"Selected preset index {index} maps to original index {original_index}")
                
                # TODO: Add MIDI handling for preset changes using original_index
                pass
                
            # Get the preset name without the number prefix
            presets = self._get_preset_list()
            if original_index >= len(presets):
                logging.error(f"Original index {original_index} out of range for presets list (max {len(presets)-1})")
                return
            
            preset_name = presets[original_index].split(': ')[1]
            
            # Emit signal with all required information
            self.preset_changed.emit(
                original_index + 1,  # original preset number (1-based)
                preset_name,
                self.channel
            )
        except Exception as e:
            logging.error(f"Error in preset change handler: {str(e)}", exc_info=True)

    def _get_area_for_type(self) -> int:
        """Get MIDI area based on preset type"""
        if self.preset_type == PresetType.ANALOG:
            return ANALOG_SYNTH_AREA
        elif self.preset_type == PresetType.DIGITAL_1:
            return DIGITAL_SYNTH_AREA
        else:
            return DRUM_KIT_AREA

    def _on_load_clicked(self):
        """Handle Load button click"""
        current_index = self.preset_selector.currentIndex()
        preset_loader = PresetLoader(self.midi_helper)
        preset_data = {
            'type': self.preset_type,  # Ensure this is a valid type like 'SN1', 'SN2', etc.
            'selpreset': current_index + 1,  # Convert to 1-based index
            'modified': 0  # or 1, depending on your logic
        }
        preset_loader.load_preset(preset_data)
        self.settings.setValue('last_preset/synth_type', self.preset_type)
        self.settings.setValue('last_preset/preset_num', current_index + 1)
        # self.settings.setValue('last_preset/channel', self.channel)

    def _toggle_save_frame(self):
        """Toggle visibility of save settings"""
        self.save_frame.setVisible(not self.save_frame.isVisible())
        if self.save_frame.isVisible():
            self.save_button.setText("Cancel Save")
        else:
            self.save_button.setText("Save...")

    def _on_save_clicked(self):
        """Handle Save button click"""
        if not self.midi_helper:
            QMessageBox.warning(self, "Error", "MIDI device not available")
            return

        try:
            bank = self.bank_selector.currentText()
            slot = int(self.slot_selector.currentText())
            
            # Confirm save operation
            reply = QMessageBox.question(
                self, 
                "Confirm Save",
                f"Save current {self.preset_type} preset to Bank {bank} Slot {slot}?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                return

            logging.debug(f"Saving {self.preset_type} preset to bank {bank} slot {slot}")

            # Convert bank letter to number (E=4, F=5, G=6, H=7)
            bank_num = ord(bank) - ord('A')
            
            # Calculate the appropriate area based on preset type
            area = PresetType.get_area_code(self.preset_type)

            # Send save command sequence
            # First message - Set bank and slot
            data = [0x18, 0x00, area, 0x06, bank_num]
            checksum = self._calculate_checksum(data)
            self.midi_helper.send_message([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, DT1_COMMAND_12,
                *data, checksum, 0xF7
            ])

            # Second message - Set slot number
            data = [0x18, 0x00, area, 0x07, slot - 1]  # Convert to 0-based index
            checksum = self._calculate_checksum(data)
            self.midi_helper.send_message([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, DT1_COMMAND_12,
                *data, checksum, 0xF7
            ])

            # Third message - Send save command
            data = [0x18, 0x00, area, 0x09, 0x00]  # 0x09 is save command
            checksum = self._calculate_checksum(data)
            self.midi_helper.send_message([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, DT1_COMMAND_12,
                *data, checksum, 0xF7
            ])

            QMessageBox.information(
                self,
                "Success",
                f"Successfully saved {self.preset_type} preset to Bank {bank} Slot {slot}"
            )
            
            # Hide save frame after successful save
            self._toggle_save_frame()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error saving preset: {str(e)}"
            )
            logging.error(f"Error saving {self.preset_type} preset: {str(e)}", exc_info=True)

    def request_current_parameters(self):
        """Request current parameters from the synth"""
        if self.midi_helper:
            PresetLoader.request_current_parameters(
                self.midi_helper,
                self.preset_type
            )
            
    def _update_ui(self, parameters: Dict[str, int]):
        """Update UI with new parameter values"""
        try:
            # Example: Update a label or control with a specific parameter
            # Assuming you have a QLabel or similar widget to display parameter values
            if '0.0.8' in parameters:  # Example address for a parameter
                value = parameters['0.0.8']
                self.some_label.setText(f"Parameter 0.0.8: {value}")

            # Update other UI elements as needed
            # if '0.1.0' in parameters:
            #     value = parameters['0.1.0']
            #     self.another_control.setValue(value)

        except Exception as e:
            logging.error(f"Error updating UI: {str(e)}", exc_info=True)