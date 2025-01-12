from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QComboBox, QPushButton
)
from PySide6.QtCore import Signal
import logging

from jdxi_manager.ui.style import Style

class PresetPanel(QWidget):
    """Panel for loading/saving presets"""
    
    # Define signals
    load_clicked = Signal(int)  # Emits preset number when load clicked
    save_clicked = Signal(int)  # Emits preset number when save clicked
    
    def __init__(self, parent=None):
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
        
    def _on_load(self):
        """Handle load button click"""
        preset_num = self.preset_combo.currentIndex()
        self.load_clicked.emit(preset_num)
        
    def _on_save(self):
        """Handle save button click"""
        preset_num = self.preset_combo.currentIndex()
        self.save_clicked.emit(preset_num) 