from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QComboBox, QMessageBox
)
from PySide6.QtCore import QTimer
import logging

from ...data.presets import PRESET_MAP, DRUM_KITS, DRUM_KIT_MAP
from ...midi import MIDIHelper, MIDIConnection

class PresetPanel(QWidget):
    def __init__(self, category, editor, parent=None):
        super().__init__(parent)
        self.category = category
        self.editor = editor
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Create preset selector
        self.preset_box = QComboBox()
        self.preset_box.currentTextChanged.connect(self._load_preset)
        layout.addWidget(self.preset_box)
        
        # Update preset list
        self.update_preset_list()

    def _load_preset(self):
        """Load selected preset"""
        try:
            preset_name = self.preset_box.currentText()
            if not preset_name:
                return
            
            logging.info(f"Loading preset: {preset_name}")
            
            # Get preset index from name
            if 'digital' in self.category:
                preset_index = list(PRESET_MAP.values()).index(preset_name)
            elif 'drums' in self.category:
                preset_index = list(DRUM_KIT_MAP.keys()).index(preset_name)
            else:
                preset_index = int(preset_name[:3]) - 1  # For analog presets
            
            preset_num = preset_index + 1  # Convert to 1-based
            
            # Create load request message
            msg = MIDIHelper.create_parameter_message(
                0x18,  # System area
                0x00,  # No part number
                0x00,  # Load command
                preset_index
            )
            
            # Send using singleton connection
            if self.editor.main_window and self.editor.main_window.midi_out:
                self.editor.main_window.midi_out.send_message(msg)
                # Update display immediately with known info
                self.editor._update_main_window_preset(preset_num, preset_name)
                logging.info(f"Successfully sent load request for: {preset_name}")
                
                # Request current patch data after a short delay
                QTimer.singleShot(100, self.editor._request_patch_data)
            
        except Exception as e:
            logging.error(f"Error loading preset: {str(e)}")

    def update_preset_list(self):
        """Update the preset list based on category"""
        self.preset_box.clear()
        
        if 'digital' in self.category:
            self.preset_box.addItems(PRESET_MAP.values())
        elif 'drums' in self.category:
            self.preset_box.addItems(DRUM_KITS)
        else:
            # For analog synth, use number-only presets
            self.preset_box.addItems([f"{i:03d}" for i in range(1, 17)]) 