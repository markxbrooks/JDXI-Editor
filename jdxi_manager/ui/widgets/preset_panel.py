from PySide6.QtWidgets import QWidget, QHBoxLayout, QComboBox, QLabel
from PySide6.QtCore import Signal
import logging

from ...midi.messages import create_parameter_message, create_patch_load_message

class PresetPanel(QWidget):
    presetChanged = Signal(int, str)  # Emits (preset_number, preset_name)
    
    def __init__(self, synth_type, editor, parent=None):
        super().__init__(parent)
        self.synth_type = synth_type
        self.editor = editor
        
        # Create UI
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Add label
        label = QLabel("Preset:")
        layout.addWidget(label)
        
        # Create preset combo box
        self.preset_combo = QComboBox()
        self.preset_combo.currentIndexChanged.connect(self._handle_preset_change)
        layout.addWidget(self.preset_combo)
        
        # Load initial presets
        self._load_presets()
        
    def _load_presets(self):
        """Load preset list"""
        try:
            # Load preset names (placeholder for now)
            presets = [f"{i+1:03d}: Preset {i+1}" for i in range(128)]
            
            # Add to combo box
            self.preset_combo.clear()
            self.preset_combo.addItems(presets)
            
        except Exception as e:
            logging.error(f"Error loading presets: {str(e)}")
            
    def _handle_preset_change(self, index):
        """Handle preset selection change"""
        try:
            preset_num = index + 1  # Convert to 1-based
            preset_name = self.preset_combo.currentText()
            
            logging.info(f"Loading preset: {preset_name}")
            
            # Create program change message
            msg = create_patch_load_message(preset_num)
            
            # Send via editor's MIDI out
            if self.editor and self.editor.main_window:
                if hasattr(self.editor.main_window, 'midi_out'):
                    self.editor.main_window.midi_out.send_message(msg)
                    
            # Emit signal
            self.presetChanged.emit(preset_num, preset_name)
            
        except Exception as e:
            logging.error(f"Error loading preset: {str(e)}") 