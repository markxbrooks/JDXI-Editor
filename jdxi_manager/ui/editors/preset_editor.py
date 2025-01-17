from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QComboBox, QLabel, QPushButton
)
from PySide6.QtCore import Signal
from typing import Optional, List
import logging

from jdxi_manager.midi import MIDIHelper
from jdxi_manager.ui.editors.base_editor import BaseEditor
from jdxi_manager.midi.constants import (
    DIGITAL_SYNTH_AREA,
    ANALOG_SYNTH_AREA,
    DRUM_KIT_AREA,
    DT1_COMMAND_12,
    RQ1_COMMAND_11
)

# Preset lists
ANALOG_PRESETS = [
    'Toxic Bass 1', 'Sub Bass 1', 'Backwards 1', 'Fat as That1', 'Saw+Sub Bs 1', 'Saw Bass 1', 'Pulse Bass 1',
    # ... rest of analog presets ...
]

DIGITAL_PRESETS = [
    'JP8 Strings1', 'Soft Pad 1', 'JP8 Strings2', 'JUNO Str 1', 'Oct Strings', 'Brite Str 1', 'Boreal Pad',
    # ... rest of digital presets ...
]

DRUM_PRESETS = [
    'TR-909 Kit 1', 'TR-808 Kit 1', '707&727 Kit1', 'CR-78 Kit 1', 'TR-606 Kit 1', 'TR-626 Kit 1', 'EDM Kit 1',
    # ... rest of drum presets ...
]

class PresetType:
    ANALOG = "Analog"
    DIGITAL = "Digital"
    DRUMS = "Drums"

class PresetEditor(QMainWindow):
    preset_changed = Signal(int, str, int)

    def __init__(self, midi_helper: Optional[MIDIHelper] = None, parent: Optional[QWidget] = None, preset_type: str = PresetType.ANALOG):
        super().__init__(parent)
        self.setWindowTitle(f"{preset_type} Preset Editor")
        self.midi_helper = midi_helper
        self.channel = 1  # Default channel
        self.preset_type = preset_type
        
        # Create central widget and main layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        
        # Create preset type selector
        type_row = QHBoxLayout()
        type_row.addWidget(QLabel("Type:"))
        self.type_selector = QComboBox()
        self.type_selector.addItems([PresetType.ANALOG, PresetType.DIGITAL, PresetType.DRUMS])
        self.type_selector.setCurrentText(preset_type)
        self.type_selector.currentTextChanged.connect(self._on_type_changed)
        type_row.addWidget(self.type_selector)
        main_layout.addLayout(type_row)
        
        # Create preset selector
        preset_row = QHBoxLayout()
        preset_row.addWidget(QLabel("Preset:"))
        self.preset_selector = QComboBox()
        self._update_preset_list()
        self.preset_selector.currentIndexChanged.connect(self._on_preset_changed)
        preset_row.addWidget(self.preset_selector)
        main_layout.addLayout(preset_row)
        
        # Create button row
        button_row = QHBoxLayout()
        self.load_button = QPushButton("Load")
        self.load_button.clicked.connect(self._on_load_clicked)
        button_row.addWidget(self.load_button)
        main_layout.addLayout(button_row)
        
        # Create editor widget
        self.editor = BaseEditor(midi_helper, self)
        main_layout.addWidget(self.editor)
        
        # Set as central widget
        self.setCentralWidget(main_widget)

    def _get_preset_list(self) -> List[str]:
        """Get the appropriate preset list based on type"""
        if self.preset_type == PresetType.ANALOG:
            return ANALOG_PRESETS
        elif self.preset_type == PresetType.DIGITAL:
            return DIGITAL_PRESETS
        else:
            return DRUM_PRESETS

    def _update_preset_list(self):
        """Update the preset selector with appropriate list"""
        presets = self._get_preset_list()
        self.preset_selector.clear()
        self.preset_selector.addItems([
            f"{i+1:03d}: {preset}" for i, preset in enumerate(presets)
        ])

    def _on_type_changed(self, preset_type: str):
        """Handle preset type change"""
        self.preset_type = preset_type
        self._update_preset_list()

    def _on_preset_changed(self, index: int):
        """Handle preset selection changes"""
        if self.midi_helper:
            # TODO: Add MIDI handling for preset changes
            pass
            
        # Get the preset name without the number prefix
        presets = self._get_preset_list()
        preset_name = presets[index]
        
        # Emit signal with all required information
        self.preset_changed.emit(
            index + 1,  # preset number (1-based)
            preset_name,
            self.channel
        ) 

    def _get_area_for_type(self) -> int:
        """Get MIDI area based on preset type"""
        if self.preset_type == PresetType.ANALOG:
            return ANALOG_SYNTH_AREA
        elif self.preset_type == PresetType.DIGITAL:
            return DIGITAL_SYNTH_AREA
        else:
            return DRUM_KIT_AREA

    def _on_load_clicked(self):
        """Handle Load button click"""
        if not self.midi_helper:
            return

        try:
            current_index = self.preset_selector.currentIndex()

            # First message - Main preset load command (15 bytes)
            # F0 41 10 00 00 00 0E 12 18 00 20 06 5F 63 F7
            data = [0x18, 0x00, 0x20, 0x06, 0x5F]  # Fixed values for Digital Synth
            checksum = self._calculate_checksum(data)
            self.midi_helper.send_message([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, DT1_COMMAND_12, 
                *data, checksum, 0xF7
            ])

            # Additional messages for digital synth
            if self.preset_type == PresetType.DIGITAL:
                # Second message (15 bytes)
                # F0 41 10 00 00 00 0E 12 18 00 20 07 40 01 F7
                data = [0x18, 0x00, 0x20, 0x07, 0x40]
                checksum = self._calculate_checksum(data)
                self.midi_helper.send_message([
                    0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, DT1_COMMAND_12,
                    *data, checksum, 0xF7
                ])

                # Third message (15 bytes)
                # F0 41 10 00 00 00 0E 12 18 00 20 08 00 40 F7
                data = [0x18, 0x00, 0x20, 0x08, 0x00]
                checksum = self._calculate_checksum(data)
                self.midi_helper.send_message([
                    0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, DT1_COMMAND_12,
                    *data, checksum, 0xF7
                ])

                # Additional parameter messages (18 bytes)
                params = [
                    (0x00, 0x40), (0x20, 0x3D), (0x21, 0x3D),
                    (0x22, 0x3D), (0x50, 0x25)
                ]

                for param, value in params:
                    # Format: F0 41 10 00 00 00 0E 11 19 01 [param] 00 00 00 00 [value] [checksum] F7
                    data = [0x19, 0x01, param, 0x00, 0x00, 0x00, 0x00, value]
                    checksum = self._calculate_checksum(data)
                    msg = [
                        0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, RQ1_COMMAND_11,  # Header
                        *data,  # Parameter data
                        checksum,  # Checksum
                        0xF7  # End of SysEx
                    ]
                    logging.debug(f"Sending parameter message: {' '.join([f'{b:02x}' for b in msg])}")
                    self.midi_helper.send_message(msg)

            logging.debug(f"Loaded {self.preset_type} preset {current_index + 1}")

        except Exception as e:
            logging.error(f"Error loading preset: {str(e)}")

    def _calculate_checksum(self, data: List[int]) -> int:
        """Calculate Roland checksum for parameter messages"""
        checksum = sum(data) & 0x7F
        return (128 - checksum) & 0x7F