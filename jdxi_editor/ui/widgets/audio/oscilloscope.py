"""
A phosphor oscilloscope for the two captured channels.

The left trace is the display colour. The right trace is the dimmer colour.
The previous frame is drawn first, so a trace leaves a short trail.
"""

from typing import Optional

import numpy as np
from PySide6.QtCore import QPointF
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from jdxi_editor.ui.style.rack_skin import active_skin


def trace_y(height: float, sample: float, margin: float = 6.0) -> float:
    """
    Screen y of one sample. Positive samples sit above the centre.

    :param height: float widget height
    :param sample: float about -1..1
    :param margin: float px kept clear of the edges
    :return: float
    """
    mid = height / 2.0
    amp = max(1.0, mid - margin)
    return mid - float(sample) * amp


class Oscilloscope(QWidget):
    """The waveform, with a grid and one frame of persistence."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setMinimumHeight(160)
        self._left: Optional[np.ndarray] = None
        self._right: Optional[np.ndarray] = None
        self._persist_left: Optional[np.ndarray] = None
        self._persist_right: Optional[np.ndarray] = None

    def set_waveform(
        self, left: Optional[np.ndarray], right: Optional[np.ndarray]
    ) -> None:
        """
        Replace the traces. The previous ones stay for one frame.

        :param left: Optional[np.ndarray] ``(columns, 2)`` min/max
        :param right: Optional[np.ndarray] ``(columns, 2)`` min/max
        :return: None
        """
        self._persist_left = self._left
        self._persist_right = self._right
        self._left = None if left is None else np.array(left, dtype=np.float32, copy=True)
        self._right = None if right is None else np.array(right, dtype=np.float32, copy=True)
        self.update()

    def paintEvent(self, _event) -> None:
        lcd = active_skin().lcd
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(lcd.bg_edge))
        self._draw_grid(painter, QColor(lcd.text_dim))
        zero = QColor(lcd.text_dim)
        painter.setPen(QPen(zero, 1))
        painter.drawLine(0, int(self.height() / 2), self.width(), int(self.height() / 2))
        self._draw_trace(painter, self._persist_left, QColor(lcd.text_dim))
        self._draw_trace(painter, self._persist_right, QColor(lcd.text_dim))
        self._draw_trace(painter, self._left, QColor(lcd.text))
        self._draw_trace(painter, self._right, QColor(lcd.text))
        painter.end()

    def _draw_grid(self, painter: QPainter, color: QColor) -> None:
        faint = QColor(color)
        faint.setAlpha(70)
        painter.setPen(QPen(faint, 1))
        width = self.width()
        height = self.height()
        for step in range(1, 8):
            x = int(width * step / 8)
            painter.drawLine(x, 0, x, height)
        for fraction in (0.25, 0.75):
            y = int(height * fraction)
            painter.drawLine(0, y, width, y)

    def _draw_trace(self, painter: QPainter, wave: Optional[np.ndarray], color: QColor) -> None:
        if wave is None or wave.shape[0] == 0:
            return
        painter.setPen(QPen(color, 1))
        width = float(self.width())
        height = float(self.height())
        count = wave.shape[0]
        for index in range(count):
            x = (index + 0.5) * width / count
            y_max = trace_y(height, float(wave[index, 1]))
            y_min = trace_y(height, float(wave[index, 0]))
            if y_max > y_min:
                y_max, y_min = y_min, y_max
            painter.drawLine(QPointF(x, y_max - 1.0), QPointF(x, y_min + 1.0))
