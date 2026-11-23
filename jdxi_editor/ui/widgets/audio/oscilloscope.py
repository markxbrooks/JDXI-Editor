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


# How fast the range shrinks back once a loud passage has gone: the share
# of the excess kept each frame (about a second at 30 frames a second)
RANGE_RELEASE = 0.9


def trace_y(height: float, sample: float, margin: float = 6.0, full_scale: float = 1.0) -> float:
    """
    Screen y of one sample. Positive samples sit above the centre.

    ``full_scale`` is the value drawn at the top and bottom edges. A sample
    beyond it is held at the edge, so a trace never leaves the chart.

    :param height: float widget height
    :param sample: float about -full_scale..full_scale
    :param margin: float px kept clear of the edges
    :param full_scale: float sample value at the edges, at least 1.0
    :return: float
    """
    mid = height / 2.0
    amp = max(1.0, mid - margin)
    level = float(sample) / max(1.0, float(full_scale))
    level = min(1.0, max(-1.0, level))
    return mid - level * amp


def next_full_scale(current: float, peak: float, release: float = RANGE_RELEASE) -> float:
    """
    The scope's range after a frame whose largest sample is ``peak``.

    It never drops below 1.0, so an ordinary signal is drawn as it always
    was. A louder peak widens it at once; afterwards it eases back towards
    the signal rather than jumping, so the trace does not pump.

    :param current: float the range so far
    :param peak: float largest absolute sample in the new frame
    :param release: float share of the excess over the target kept per frame
    :return: float
    """
    target = max(1.0, float(peak))
    if target >= current:
        return target
    return target + (current - target) * release


class Oscilloscope(QWidget):
    """The waveform, with a grid and one frame of persistence."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setMinimumHeight(160)
        self._left: Optional[np.ndarray] = None
        self._right: Optional[np.ndarray] = None
        self._persist_left: Optional[np.ndarray] = None
        self._persist_right: Optional[np.ndarray] = None
        # Sample value drawn at the top and bottom edges (see next_full_scale)
        self.full_scale = 1.0

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
        # PipeWire and PulseAudio hand over float samples unclipped, so a
        # boosted input goes past +-1.0; widen the range to keep it on screen
        peak = 0.0
        for wave in (self._left, self._right):
            if wave is not None and wave.size:
                peak = max(peak, float(np.nanmax(np.abs(wave))))
        self.full_scale = next_full_scale(self.full_scale, peak)
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
        if self.full_scale > 1.005:
            # The range only widens past full scale, so say by how much
            painter.setPen(QPen(QColor(lcd.text), 1))
            painter.drawText(6, 4 + painter.fontMetrics().ascent(), f"\u00b1{self.full_scale:.1f}")
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
            y_max = trace_y(height, float(wave[index, 1]), full_scale=self.full_scale)
            y_min = trace_y(height, float(wave[index, 0]), full_scale=self.full_scale)
            if y_max > y_min:
                y_max, y_min = y_min, y_max
            top = max(0.0, y_max - 1.0)
            bottom = min(height, y_min + 1.0)
            painter.drawLine(QPointF(x, top), QPointF(x, bottom))
