from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Signal
from jdxi_manager.midi.constants import Waveform

class WaveformButton(QPushButton):
    """Button for selecting oscillator waveform"""
    
    waveform_selected = Signal(Waveform)  # Emits selected waveform
    
    def __init__(self, waveform: Waveform, parent=None):
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
        self.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                color: #CCCCCC;
                border: 1px solid #666666;
                border-radius: 3px;
                padding: 5px;
            }
            QPushButton:checked {
                background-color: #B22222;
                color: white;
                border: 1px solid #FF4444;
            }
            QPushButton:hover {
                background-color: #444444;
            }
        """)
    
    def _on_clicked(self):
        """Handle button click"""
        if self.isChecked():
            self.waveform_selected.emit(self.waveform) 