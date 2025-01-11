from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QPushButton, QScrollArea, QWidget
)
from PySide6.QtCore import Signal
import logging

class PresetPanel(QFrame):
    """Panel for selecting and managing presets"""
    
    presetChanged = Signal(int, str)  # Emits (preset_number, preset_name)
    
    def __init__(self, preset_type, parent=None):
        """Initialize preset panel
        
        Args:
            preset_type: Type of presets to display (e.g. 'digital1', 'analog')
            parent: Parent widget
        """
        super().__init__(parent)
        self.preset_type = preset_type
        self.parent = parent
        
        # Create UI
        self._create_ui()
        
    def _create_ui(self):
        """Create the user interface"""
        layout = QVBoxLayout(self)
        
        # Create header row
        header = QHBoxLayout()
        
        # Preset selector
        self.preset_combo = QComboBox()
        self._load_presets()
        header.addWidget(self.preset_combo)
        
        # Load/Save buttons
        load_btn = QPushButton("Load")
        load_btn.clicked.connect(self._load_preset)
        header.addWidget(load_btn)
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._save_preset)
        header.addWidget(save_btn)
        
        layout.addLayout(header)
        
    def _load_presets(self):
        """Load preset list into combo box"""
        try:
            # Add preset names (placeholder for now)
            presets = [f"{i+1:03d}: Preset {i+1}" for i in range(128)]
            
            # Add to combo box
            self.preset_combo.clear()
            self.preset_combo.addItems(presets)
            
        except Exception as e:
            logging.error(f"Error loading presets: {str(e)}")
            
    def _load_preset(self):
        """Load selected preset"""
        try:
            preset_num = self.preset_combo.currentIndex() + 1
            preset_name = self.preset_combo.currentText()
            
            # Emit signal
            self.presetChanged.emit(preset_num, preset_name)
            
            # Forward to parent if available
            if self.parent and hasattr(self.parent, 'load_preset'):
                self.parent.load_preset(preset_name)
                
        except Exception as e:
            logging.error(f"Error loading preset: {str(e)}")
            
    def _save_preset(self):
        """Save current settings to selected preset"""
        try:
            preset_num = self.preset_combo.currentIndex() + 1
            preset_name = self.preset_combo.currentText()
            
            # Forward to parent if available
            if self.parent and hasattr(self.parent, 'save_preset'):
                self.parent.save_preset(preset_num, preset_name)
                
        except Exception as e:
            logging.error(f"Error saving preset: {str(e)}") 