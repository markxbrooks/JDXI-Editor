"""
TimeRulerWidget
"""

import mido
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPaintEvent, QPen
from PySide6.QtWidgets import QWidget

from jdxi_editor.jdxi.jdxi import JDXi


class TimeRulerWidget(QWidget):
    """
    TimeRulerWidget
    """

    def __init__(self, midi_file: mido.MidiFile = None, parent: QWidget = None):
        super().__init__(parent)
        self.midi_file_cached_total_length = None
        self.midi_file = midi_file
        self.setMinimumHeight(20)
        self.setMaximumHeight(JDXi.UI.Style.MAX_RULER_HEIGHT)
        # List of (seconds: float, color: QColor | None, label: str | None)
        self._markers = []

    def set_midi_file(self, midi_file: mido.MidiFile) -> None:
        self.midi_file = midi_file
        self.midi_file_cached_total_length = self.midi_file.length
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        if not self.midi_file:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        duration = self.midi_file_cached_total_length
        width = self.width()
        height = self.height()

        num_marks = int(duration) + 1
        spacing = width / duration if duration else width

        font = painter.font()
        font.setPointSize(8)
        painter.setFont(font)
        painter.setPen(QPen(Qt.white))

        for second in range(num_marks):
            if second % 10 == 0:
                # Draw major ticks every 10 seconds
                x = int(second * spacing)
                painter.drawLine(x, 0, x, height)
                painter.drawText(x + 2, height - 4, f"{second}s")

        # Draw markers
        for seconds, color, label in self._markers:
            if duration <= 0:
                continue
            x = int((seconds / duration) * width)
            pen = QPen(
                color if isinstance(color, QColor) else QColor(JDXi.UI.Style.ACCENT)
            )
            pen.setWidth(2)
            painter.setPen(pen)
            # Marker line
            painter.drawLine(x, 0, x, height // 2)
            # Optional label just above midline
            if label:
                painter.drawText(x + 3, (height // 2) - 2, label)

    def add_marker(
        self, seconds: float, color: QColor | None = None, label: str | None = None
    ) -> None:
        """Add a time marker in seconds and repaint."""
        try:
            if seconds < 0:
                seconds = 0.0
        except Exception:
            seconds = 0.0
        self._markers.append((float(seconds), color, label))
        self.update()

    def clear_markers(self) -> None:
        """Clear all time markers and repaint."""
        self._markers.clear()
        self.update()
