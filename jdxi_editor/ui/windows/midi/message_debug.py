from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTextEdit
from PySide6.QtCore import Qt

class MIDIMessageDebug(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("MIDI Message Debug")
        self.setMinimumSize(600, 400)
        
        # Create central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Create log view
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setLineWrapMode(QTextEdit.NoWrap)
        self.log_view.setStyleSheet("""
            QTextEdit {
                font-family: monospace;
                background-color: #1E1E1E;
                color: #FFFFFF;
            }
        """)
        layout.addWidget(self.log_view)
        
    def log_message(self, message, direction="→"):
        """Log address MIDI message with timestamp"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        if isinstance(message, (list, bytes)):
            hex_str = ' '.join([f"{b:02X}" for b in message])
            self.log_view.append(f"{timestamp} {direction} {hex_str}")
        else:
            self.log_view.append(f"{timestamp} {direction} {message}")
        
    def clear_log(self):
        """Clear the log view"""
        self.log_view.clear() 