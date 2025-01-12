from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt, QTimer

class DigitalDisplay(QLabel):
    """Digital LCD-style display widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                background-color: #000;
                color: #0F0;
                font-family: monospace;
                font-size: 14px;
                padding: 5px;
                border: 1px solid #333;
            }
        """)
        
        # Default text
        self.setText("JD-Xi")
        
        # Update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(1000)  # Update every second
        
        # Get MIDI connection
        from jdxi_manager.midi.connection import MIDIConnection
        self.midi = MIDIConnection()

    def update_status(self):
        """Update connection status display"""
        if self.midi and self.midi.is_connected:
            self.setText(f"JD-Xi v{self.midi.device_version}")
        else:
            self.setText("Not Connected")
            # Try to identify device if not connected
            if self.midi:
                self.midi.identify_device() 