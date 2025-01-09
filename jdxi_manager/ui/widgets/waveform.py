from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Signal

class WaveformButton(QPushButton):
    """Button that cycles through waveform types"""
    
    waveformChanged = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_wave = 0
        self.setCheckable(True)
        self.clicked.connect(self._cycle_waveform)
        self._update_text()
        
    def _cycle_waveform(self):
        self._current_wave = (self._current_wave + 1) % 4
        self._update_text()
        self.waveformChanged.emit(self._current_wave)
        
    def _update_text(self):
        waveforms = ["SAW", "SQUARE", "TRIANGLE", "SINE"]
        self.setText(waveforms[self._current_wave])
        
    def value(self):
        return self._current_wave
        
    def setValue(self, value):
        if 0 <= value < 4:
            self._current_wave = value
            self._update_text()
            self.waveformChanged.emit(self._current_wave) 