"""
Module: log_viewer
==================

This module provides a graphical log viewer using PySide6. The `LogViewer` class is a
QMainWindow-based widget that displays the log file written by Decologr. It
automatically refreshes to show new log entries.

Classes:
--------
- `LogViewer`: A main window that displays the log file and refreshes automatically.

Features:
---------
- Dark theme with a modern red-accented styling, in fixed-width text so the
  columns line up; the emoji Decologr puts before each message are left out
  (the level column already says it).
- Two tabs: every line, and the lines that deserve attention (warnings,
  errors and what follows them, e.g. a traceback).
- Automatically reads and displays the log file written by Decologr. Each run
  writes a file named after the time it started, rotated at 1MB, so the file to
  read is taken from the installed log handler rather than from a fixed path
  (see :func:`resolve_log_file`).
- Refreshes periodically to show new log entries, and follows the file across
  rotation. It reads bytes and holds a line still being written, so no line
  is broken or shown twice.
- Provides a "Clear Log" button: the lines written from then on appear.
- Auto-scrolls to the bottom to show the latest entries.

Usage Example:
--------------
>>> viewer = LogViewer()
>>> viewer.show()

"""

import logging
import re
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QTimer
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QTabWidget,
)

from jdxi_editor.log_files import LOG_KEEP_DAYS, log_dir
from jdxi_editor.ui.common import JDXi, QVBoxLayout, QWidget
from jdxi_editor.ui.widgets.rack import RackPanel

ATTENTION = ("WARNING", "ERROR", "CRITICAL")
_ENTRY = re.compile(r"^\[\d\d:\d\d:\d\d\]\s+(\w+)")
_EMOJI = re.compile(
    "[\U0001F000-\U0001FAFF\u2139\u2600-\u27BF\u2B00-\u2BFF\uFE0F\u200D]+ ?"
)
MAX_LINES = 20000  # the view keeps the newest lines (the file keeps them all)


def log_directory() -> Path:
    """
    Directory Decologr writes log files to.

    :return: Path
    """
    return log_dir()


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


def fixed_font() -> QFont:
    """A fixed-width font for the log lines."""
    font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
    font.setFamilies(
        ["Consolas", "Cascadia Mono", "Menlo", "DejaVu Sans Mono", font.family()]
    )
    font.setStyleHint(QFont.StyleHint.Monospace)
    font.setFixedPitch(True)
    font.setPointSize(10)
    return font


def clean(line: str) -> str:
    """The line without the emoji Decologr puts before each message."""
    return _EMOJI.sub("", line)


def needs_attention(
    lines: list[str], following: bool = False
) -> tuple[list[str], bool]:
    """
    The lines with a level from WARNING up, with the lines that continue them.

    :param lines: list[str] log lines
    :param following: bool the line before *lines* continued a warning or an error
    :return: (the lines kept, whether the last line continues one)
    """
    kept = []
    for line in lines:
        match = _ENTRY.match(line)
        if match:
            following = match.group(1).upper() in ATTENTION
        if following and line.strip():
            kept.append(line)
    return kept, following


class LogViewer(QMainWindow):
    def __init__(self, midi_helper=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Log Viewer")
        self.setMinimumSize(980, 400)

        # Apply dark theme styling
        self.setStyleSheet(JDXi.UI.Style.LOG_VIEWER)

        self.log_file = resolve_log_file()

        self.last_position = 0  # bytes already read
        self._partial = b""  # a line still being written
        self._following = False  # the last line read continues a warning or an error
        self._attention_count = 0
        # Track refresh mode: True = fast (500ms), False = slow (30s)
        self.fast_refresh_mode = True

        # Create central widget and layout
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)

        self.tabs = QTabWidget()
        self.log_text = self._text_view()
        self.attention_text = self._text_view()
        self.tabs.addTab(self.log_text, "All")
        self.tabs.addTab(self.attention_text, "")
        self._update_attention_title()
        layout.addWidget(self.tabs)

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

        layout.addWidget(
            QLabel(f"Log files older than {LOG_KEEP_DAYS} days are deleted at start")
        )

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

    def _text_view(self) -> QPlainTextEdit:
        view = QPlainTextEdit()
        view.setReadOnly(True)
        view.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        view.setMaximumBlockCount(MAX_LINES)
        view.setFont(fixed_font())
        return view

    def _update_attention_title(self) -> None:
        self.tabs.setTabText(1, f"Warnings and errors ({self._attention_count})")

    def load_log_file(self):
        """Read the whole file again."""
        self.log_text.clear()
        self.attention_text.clear()
        self.last_position, self._partial, self._following = 0, b"", False
        self._attention_count = 0
        self._update_attention_title()
        if self.log_file is None or not self.log_file.exists():
            self.log_text.setPlainText(self._no_log_file_message())
            return
        self.setWindowTitle(f"Log Viewer - {self.log_file.name}")
        self.refresh_log_file()

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

    def refresh_log_file(self):
        """Append the complete lines written since the last read."""
        if self.log_file is None or not self.log_file.exists():
            # The file is only named once per run, so a missing one means
            # logging has only just started, or the file was rotated away
            self.log_file = resolve_log_file()
            if self.log_file is None:
                return
            self.last_position, self._partial = 0, b""

        try:
            # Rotation moves the file that was being read to "....log.1" and
            # starts a new one, which is shorter: carry on reading from where
            # the old file ended and nothing would ever appear again
            if self.log_file.stat().st_size < self.last_position:
                self.load_log_file()
                return
            # positions in bytes: the emoji are several bytes
            with open(self.log_file, "rb") as f:
                f.seek(self.last_position)
                data = f.read()
                self.last_position = f.tell()
        except OSError:
            # The file may be locked or have just been rotated away
            return
        if not data:
            return
        data = self._partial + data
        complete, newline, self._partial = data.rpartition(b"\n")
        if not newline:
            self._partial = data
            return
        lines = [
            clean(line) for line in complete.decode("utf-8", "replace").splitlines()
        ]
        self._append(self.log_text, lines)
        kept, self._following = needs_attention(lines, self._following)
        if kept:
            self._attention_count += sum(1 for line in kept if _ENTRY.match(line))
            self._append(self.attention_text, kept)
            self._update_attention_title()

    @staticmethod
    def _append(view: QPlainTextEdit, lines: list[str]) -> None:
        bar = view.verticalScrollBar()
        at_end = bar.value() >= bar.maximum() - 2
        view.appendPlainText("\n".join(lines))
        if at_end:  # follow the new lines, unless the user scrolled up to read
            bar.setValue(bar.maximum())

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
        """Empty the view; only the lines written from now on appear (the file is untouched)."""
        self.log_text.clear()
        self.attention_text.clear()
        self._attention_count = 0
        self._update_attention_title()

    def closeEvent(self, event):
        """Stop the refresh timer when window is closed"""
        if hasattr(self, "refresh_timer"):
            self.refresh_timer.stop()
        event.accept()
