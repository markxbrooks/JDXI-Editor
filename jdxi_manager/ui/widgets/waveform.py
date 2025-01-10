from PySide6.QtWidgets import QPushButton, QMenu
from PySide6.QtCore import Signal
from jdxi_manager.midi.constants import Waveform

class WaveformButton(QPushButton):
    """Button for selecting waveforms with dropdown menu"""
    
    # Add signal for waveform changes
    waveform_changed = Signal(object)  # Will emit the new waveform value
    
    def __init__(self, label="Waveform", parent=None):
        super().__init__(label, parent)
        self._waveform = Waveform.SAW  # Default to saw wave
        self._setup_menu()
        
    def _setup_menu(self):
        """Create dropdown menu with waveform options"""
        menu = QMenu(self)
        
        # Add waveform options using constants
        waveforms = [
            ("Saw", Waveform.SAW),
            ("Square", Waveform.SQUARE),
            ("Triangle", Waveform.TRIANGLE),
            ("Sine", Waveform.SINE),
            ("Noise", Waveform.NOISE),
            ("Super Saw", Waveform.SUPER_SAW),
            ("PCM", Waveform.PCM)
        ]
        
        for name, value in waveforms:
            action = menu.addAction(name)
            action.setData(value)
            action.triggered.connect(
                lambda checked, v=value: self._on_waveform_selected(v)
            )
            
        self.setMenu(menu)
        
    def _on_waveform_selected(self, value):
        """Handle waveform selection"""
        self._waveform = value
        # Find action with matching value
        for action in self.menu().actions():
            if action.data() == value:
                self.setText(f"Wave: {action.text()}")
                break
        # Emit signal with new value
        self.waveform_changed.emit(value)
        
    def setWaveform(self, value):
        """Set waveform value programmatically"""
        # Validate value is a valid waveform
        if not hasattr(Waveform, str(value)):
            return
            
        self._waveform = value
        # Find action with matching value and update text
        for action in self.menu().actions():
            if action.data() == value:
                self.setText(f"Wave: {action.text()}")
                break
            
    def getWaveform(self):
        """Get current waveform value"""
        return self._waveform 