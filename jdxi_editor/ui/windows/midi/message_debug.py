"""
message_debug module
====================

MIDIMessageDebug is a Qt-based main window for logging and displaying MIDI messages. It provides a real-time log view where MIDI messages can be logged with timestamps, allowing for easy debugging of MIDI communication.

Attributes:
    log_view (QTextEdit): A text edit widget used to display the MIDI message log.

Methods:
    log_message(message, direction="→"): Logs a MIDI message with a timestamp. Optionally, the direction (input or output) of the message can be specified.
    clear_log(): Clears the message log view.
"""

from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTextEdit


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
