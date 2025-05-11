"""
Module: log_viewer
==================

This module provides a graphical log viewer using PySide6. The `LogViewer` class is a
QMainWindow-based widget that displays real-time logging messages in a styled QTextEdit
widget. It supports color-coded log levels and provides a button to clear the log display.

Classes:
--------
- `LogViewer`: A main window that captures and displays log messages in real time.
- `LogHandler`: A custom logging handler that redirects log output to the `QTextEdit` widget.

Features:
---------
- Dark theme with a modern red-accented styling.
- Supports logging levels with color-coded messages:
  - **Red** for errors
  - **Orange** for warnings
  - **White** for info messages
  - **Gray** for debug messages
- Provides a "Clear Log" button to reset the log display.
- Automatically removes the log handler when closed.

Usage Example:
--------------
>>> viewer = LogViewer()
>>> viewer.show()
>>> log_message("This is an info message.")
>>> log_message("This is an error message.")

"""


import logging
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTextEdit, QPushButton

from jdxi_editor.log.emoji import LEVEL_EMOJIS
from jdxi_editor.jdxi.style import JDXiStyle


class LogViewer(QMainWindow):
    def __init__(self, midi_helper=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Log Viewer")
        self.setMinimumSize(980, 400)

        # Apply dark theme styling
        self.setStyleSheet(JDXiStyle.LOG_VIEWER)

        # Create central widget and layout
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)

        # Create log text area
        self.log_text = QTextEdit()
        self.log_text.setLineWrapMode(QTextEdit.NoWrap)
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
        self.setFormatter(
            logging.Formatter(
                "%(filename)-20s| %(lineno)-5s| %(levelname)-8s| %(message)-24s"
            )
        )

    def emit(self, record):
        self.format(record)
        # Add emojis based on log level
        LEVEL_EMOJIS.get(record.levelno, "🔔")
        message = self.format(record)
        # Add MIDI flair if message seems MIDI-related
        # midi_tag = "🎵" if "midi" in message.lower() or "sysex" in message.lower() else ""
        # jdxi_tag = "🎹" if "jdxi" or "jd-xi" in message.lower() in message.lower() else ""
        # qc_passed_tag = "✅" if "updat" in message.lower() or "success" in message.lower() else ""
        full_message = (
            message  # f"{emoji}{jdxi_tag}{qc_passed_tag}{midi_tag} {message}"
        )
        self.text_widget.append(full_message)
