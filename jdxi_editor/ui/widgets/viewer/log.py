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
- Automatically reads and displays the log file written by Decologr. Each run
  writes a file named after the time it started, rotated at 1MB, so the file to
  read is taken from the installed log handler rather than from a fixed path
  (see :func:`resolve_log_file`).
- Refreshes periodically to show new log entries, and follows the file across
  rotation.
- Provides a "Clear Log" button to reset the log digital.
- Auto-scrolls to the bottom to show the latest entries.

Usage Example:
--------------
>>> viewer = LogViewer()
>>> viewer.show()

"""

import logging
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QPushButton, QTextEdit

from jdxi_editor.project import __package_name__
from jdxi_editor.ui.common import JDXi, QVBoxLayout, QWidget
from jdxi_editor.ui.widgets.rack import RackPanel


def log_directory() -> Path:
    """
    Directory Decologr writes log files to.

    :return: Path
    """
    return Path.home() / f".{__package_name__}" / "logs"


def resolve_log_file(log_dir: Optional[Path] = None) -> Optional[Path]:
    """
    The log file currently being written.

    Decologr names each run's file after the time it started
    (``jdxi_editor-01Feb2026-10-32-09.log``) and rotates it at 1MB, so there is
    no file at a fixed path to open. The handler installed by ``setup_logging``
    knows the name, so it is asked first; failing that, the newest file in the
    log directory is used, preferring one that is not a rotated backup.

    :param log_dir: Optional[Path] directory to search; defaults to
        :func:`log_directory`
    :return: Optional[Path] the log file, or None if there is none
    """
    for handler in logging.getLogger().handlers:
        base_filename = getattr(handler, "baseFilename", None)
        if base_filename:
            return Path(base_filename)

    directory = log_directory() if log_dir is None else log_dir
    try:
        candidates = [path for path in directory.glob("*.log*") if path.is_file()]
    except OSError:
        return None
    if not candidates:
        return None
    # Rotation renames the live file to "....log.1" and opens a new ".log", so
    # a plain ".log" is the one being written to even when a backup is newer.
    current = [path for path in candidates if path.suffix == ".log"]
    return max(current or candidates, key=lambda path: path.stat().st_mtime)


class LogViewer(QMainWindow):
    def __init__(self, midi_helper=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Log Viewer")
        self.setMinimumSize(980, 400)

        # Apply dark theme styling
        self.setStyleSheet(JDXi.UI.Style.LOG_VIEWER)

        self.log_file = resolve_log_file()

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
        # Mounted as a rack unit: the ears are the skin's, and the
        # skins without them simply draw none
        self.setCentralWidget(RackPanel(main_widget))

        # Load initial log content
        self.load_log_file()

        # Set up timer to refresh log file periodically
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_log_file)
        self.refresh_timer.start(500)  # Start with fast refresh (500ms)

    def load_log_file(self):
        """Load the entire log file into the text widget"""
        if self.log_file is None or not self.log_file.exists():
            self.log_text.setPlainText(self._no_log_file_message())
            return
        try:
            with open(self.log_file, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
                self.log_text.setPlainText(content)
                self.last_position = f.tell()
                self._scroll_to_end()
            self.setWindowTitle(f"Log Viewer - {self.log_file.name}")
        except OSError as ex:
            self.log_text.setPlainText(
                f"Error reading log file: {ex}\n\nLog file path: {self.log_file}"
            )

    def _no_log_file_message(self) -> str:
        """
        What to show when there is no log file to read.

        :return: str
        """
        directory = log_directory()
        message = [
            "No log file found.",
            "",
            f"Log directory: {directory}",
        ]
        if not directory.exists():
            message.append("")
            message.append("The directory does not exist yet; it is created when")
            message.append("logging starts.")
        return "\n".join(message)

    def _scroll_to_end(self) -> None:
        """
        Scroll the view to the newest entry.

        :return: None
        """
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)

    def refresh_log_file(self):
        """Read new lines from the log file and append them"""
        if self.log_file is None or not self.log_file.exists():
            # The file is only named once per run, so a missing one means
            # logging has only just started, or the file was rotated away
            self.log_file = resolve_log_file()
            if self.log_file is None:
                return
            self.last_position = 0

        try:
            # Rotation moves the file that was being read to "....log.1" and
            # starts a new one, which is shorter: carry on reading from where
            # the old file ended and nothing would ever appear again
            if self.log_file.stat().st_size < self.last_position:
                self.load_log_file()
                return

            with open(self.log_file, "r", encoding="utf-8", errors="replace") as f:
                f.seek(self.last_position)
                new_content = f.read()
                if new_content:
                    self.log_text.moveCursor(
                        self.log_text.textCursor().MoveOperation.End
                    )
                    self.log_text.insertPlainText(new_content)
                    self.last_position = f.tell()
                    self._scroll_to_end()
        except OSError:
            # The file may be locked or have just been rotated away
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
        """Clear the log digital"""
        self.log_text.clear()
        self.last_position = 0

    def closeEvent(self, event):
        """Stop the refresh timer when window is closed"""
        if hasattr(self, "refresh_timer"):
            self.refresh_timer.stop()
        event.accept()
