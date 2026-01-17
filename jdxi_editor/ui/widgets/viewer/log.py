"""
Module: log_viewer
==================

This module provides a graphical log viewer using PySide6. The `LogViewer` class is a
QMainWindow-based widget that displays the log file written by Decologr in a styled QTextEdit
widget. It automatically refreshes to show new log entries.

Classes:
--------
- `LogViewer`: A main window that displays the log file and refreshes automatically.

Features:
---------
- Dark theme with a modern red-accented styling.
- Automatically reads and displays the log file written by Decologr.
- Refreshes periodically to show new log entries.
- Provides a "Clear Log" button to reset the log display.
- Auto-scrolls to the bottom to show the latest entries.

Usage Example:
--------------
>>> viewer = LogViewer()
>>> viewer.show()

"""

from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.jdxi.jdxi import JDXi
from jdxi_editor.project import __package_name__


class LogViewer(QMainWindow):
    def __init__(self, midi_helper=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Log Viewer")
        self.setMinimumSize(980, 400)

        # Apply dark theme styling
        self.setStyleSheet(JDXi.Style.LOG_VIEWER)

        # Determine log file path (Decologr writes to ~/.{package_name}/logs/{package_name}.log)
        log_dir = Path.home() / f".{__package_name__}" / "logs"
        self.log_file = log_dir / f"{__package_name__}.log"

        # Track the last position we read from in the file
        self.last_position = 0
        # Track refresh mode: True = fast (500ms), False = slow (30s)
        self.fast_refresh_mode = True

        # Create central widget and layout
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)

        # Create log text area
        self.log_text = QTextEdit()
        self.log_text.setLineWrapMode(QTextEdit.NoWrap)
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

        # Create button layout
        button_layout = QHBoxLayout()

        # Create clear button
        clear_button = QPushButton("Clear Log")
        clear_button.clicked.connect(self.clear_log)
        button_layout.addWidget(clear_button)

        # Create refresh mode toggle button
        self.refresh_mode_button = QPushButton("Fast Refresh (500ms)")
        self.refresh_mode_button.setCheckable(True)
        self.refresh_mode_button.setChecked(True)
        self.refresh_mode_button.clicked.connect(self.toggle_refresh_mode)
        button_layout.addWidget(self.refresh_mode_button)

        layout.addLayout(button_layout)

        # Set central widget
        self.setCentralWidget(main_widget)

        # Load initial log content
        self.load_log_file()

        # Set up timer to refresh log file periodically
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_log_file)
        self.refresh_timer.start(500)  # Start with fast refresh (500ms)

    def load_log_file(self):
        """Load the entire log file into the text widget"""
        if self.log_file.exists():
            try:
                with open(self.log_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    self.log_text.setPlainText(content)
                    self.last_position = len(content)
                    # Scroll to bottom
                    cursor = self.log_text.textCursor()
                    cursor.movePosition(cursor.MoveOperation.End)
                    self.log_text.setTextCursor(cursor)
            except Exception as e:
                self.log_text.setPlainText(
                    f"Error reading log file: {e}\n\nLog file path: {self.log_file}"
                )
        else:
            self.log_text.setPlainText(
                f"Log file not found.\n\nExpected location: {self.log_file}"
            )

    def refresh_log_file(self):
        """Read new lines from the log file and append them"""
        if not self.log_file.exists():
            return

        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                # Seek to last position
                f.seek(self.last_position)
                # Read new content
                new_content = f.read()
                if new_content:
                    # Append new content
                    self.log_text.moveCursor(
                        self.log_text.textCursor().MoveOperation.End
                    )
                    self.log_text.insertPlainText(new_content)
                    # Update position
                    self.last_position = f.tell()
                    # Scroll to bottom
                    cursor = self.log_text.textCursor()
                    cursor.movePosition(cursor.MoveOperation.End)
                    self.log_text.setTextCursor(cursor)
        except Exception:
            # Silently ignore errors (file might be locked or deleted)
            pass

    def toggle_refresh_mode(self):
        """Toggle between fast refresh (500ms) and slow refresh (30s)"""
        self.fast_refresh_mode = not self.fast_refresh_mode

        if self.fast_refresh_mode:
            self.refresh_timer.setInterval(500)  # 500ms
            self.refresh_mode_button.setText("Fast Refresh (500ms)")
        else:
            self.refresh_timer.setInterval(30000)  # 30 seconds
            self.refresh_mode_button.setText("Slow Refresh (30s)")

        # Restart timer with new interval
        self.refresh_timer.start()

    def clear_log(self):
        """Clear the log display"""
        self.log_text.clear()
        self.last_position = 0

    def closeEvent(self, event):
        """Stop the refresh timer when window is closed"""
        if hasattr(self, "refresh_timer"):
            self.refresh_timer.stop()
        event.accept()
