from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTextEdit, QPushButton
from PySide6.QtCore import Qt
import logging

class LogViewer(QMainWindow):
    def __init__(self, midi_helper=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Log Viewer")
        self.setMinimumSize(980, 400)
        
        # Apply dark theme styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2E2E2E;
            }
            QWidget {
                background-color: #2E2E2E;
                color: #FFFFFF;
                font-family: 'Myriad Pro';
            }
            QTextEdit {
                background-color: #1A1A1A;
                color: #FFFFFF;
                border: 1px solid #FF0000;
                border-radius: 3px;
                padding: 5px;
                font-family: 'Consolas';
            }
            QPushButton {
                background-color: #3D3D3D;
                color: #FFFFFF;
                border: 1px solid #FF0000;
                border-radius: 3px;
                padding: 5px 15px;
                font-family: 'Myriad Pro';
            }
            QPushButton:hover {
                background-color: #4D4D4D;
                border: 1px solid #FF3333;
            }
            QPushButton:pressed {
                background-color: #2D2D2D;
            }
        """)
        
        # Create central widget and layout
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        
        # Create log text area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        # Create clear button
        clear_button = QPushButton("Clear Log")
        clear_button.clicked.connect(self.clear_log)
        layout.addWidget(clear_button)
        
        # Set central widget
        self.setCentralWidget(main_widget)
        
        # Set up log handler
        self.log_handler = LogHandler(self.log_text)
        logging.getLogger().addHandler(self.log_handler)
        
    def clear_log(self):
        """Clear the log display"""
        self.log_text.clear()
        
    def closeEvent(self, event):
        """Remove log handler when window is closed"""
        logging.getLogger().removeHandler(self.log_handler)
        event.accept()

class LogHandler(logging.Handler):
    """Custom logging handler to display logs in QTextEdit"""
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
        self.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s %(filename)s:%(lineno)d'
        ))
        
    def emit(self, record):
        msg = self.format(record)
        # Add color based on log level
        if record.levelno >= logging.ERROR:
            msg = f'<span style="color: #FF0000;">{msg}</span>'  # Red for errors
        elif record.levelno >= logging.WARNING:
            msg = f'<span style="color: #FFA500;">{msg}</span>'  # Orange for warnings
        elif record.levelno >= logging.INFO:
            msg = f'<span style="color: #FFFFFF;">{msg}</span>'  # White for info
        else:
            msg = f'<span style="color: #888888;">{msg}</span>'  # Grey for debug
            
        self.text_widget.append(msg) 