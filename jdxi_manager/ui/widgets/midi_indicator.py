from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import QTimer

class MIDIIndicator(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(16, 16)
        self.setEnabled(False)  # Make it look like an indicator
        
        # Setup flash timer
        self.flash_timer = QTimer()
        self.flash_timer.setSingleShot(True)
        self.flash_timer.timeout.connect(self._reset_color)
        
        # Initial style
        self.setStyleSheet("""
            QPushButton {
                background-color: black;
                border: 2px solid #333333;
                border-radius: 8px;
            }
        """)
        
    def flash(self):
        """Flash the indicator red"""
        self.setStyleSheet("""
            QPushButton {
                background-color: #d51e35;
                border: 2px solid #333333;
                border-radius: 8px;
            }
        """)
        
        # Reset after 50ms
        self.flash_timer.start(50)
        
    def _reset_color(self):
        """Reset to default color"""
        self.setStyleSheet("""
            QPushButton {
                background-color: black;
                border: 2px solid #333333;
                border-radius: 8px;
            }
        """) 