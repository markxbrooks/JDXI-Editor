from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Signal
from jdxi_manager.midi.data.constants import Waveform
from PIL import Image, ImageDraw
import base64
from io import BytesIO


class WaveformButton(QPushButton):
    """Button for selecting oscillator waveform"""
    
    waveform_selected = Signal(Waveform)  # Emits selected waveform
    
    def __init__(self, waveform: Waveform, style="digital", parent=None):
        """Initialize waveform button
        
        Args:
            waveform: Waveform enum value
            parent: Parent widget
        """
        super().__init__(parent)
        self.waveform = waveform
        self.setText(waveform.display_name)
        self.setCheckable(True)
        self.clicked.connect(self._on_clicked)

        # Style
        self.setMinimumWidth(60)
    
    def _on_clicked(self):
        """Handle button click"""
        if self.isChecked():
            self.waveform_selected.emit(self.waveform)
