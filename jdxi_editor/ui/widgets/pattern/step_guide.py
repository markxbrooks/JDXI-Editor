"""
Step Guide

The grey step-length lines printed above the JD-Xi's 16 step buttons, drawn
above the Pattern Editor's steps: groups of 3 steps (across the first 12),
of 8, and of 4.

    ───── ───── ───── ─────
    ─────────────── ───────────────
    ─────── ─────── ─────── ───────
    [ ][ ][ ][ ][ ][ ][ ][ ][ ][ ][ ][ ][ ][ ][ ][ ]

Each line runs from the left edge of its first step to the right edge of its
last, read from the step buttons themselves, so it lines up however the row
is laid out.
"""

from __future__ import annotations

from typing import Callable, Optional, Sequence

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QColor, QPainter, QPaintEvent, QPen
from PySide6.QtWidgets import QSizePolicy, QWidget

# (steps per line, number of lines) for each row, top to bottom
GUIDE_ROWS = ((3, 4), (8, 2), (4, 4))
LINE_COLOR = "#8C8C8C"
LINE_WIDTH = 2
ROW_SPACING = 9  # px between rows (about a quarter of a step, as on the JD-Xi)
MARGIN = 6  # px above the first row and below the last


class StepGuide(QWidget):
    """Step-length lines above a row of step buttons."""

    def __init__(
        self,
        step_buttons: Callable[[], Sequence[QWidget]],
        parent: Optional[QWidget] = None,
    ):
        """
        :param step_buttons: returns the step buttons the lines are drawn over
            (one row of the current measure)
        """
        super().__init__(parent)
        self._step_buttons = step_buttons
        self.setFixedHeight(2 * MARGIN + (len(GUIDE_ROWS) - 1) * ROW_SPACING + LINE_WIDTH)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def segments(self) -> list[tuple[int, int, int]]:
        """(x1, x2, y) of every line, in this widget's coordinates."""
        buttons = list(self._step_buttons() or [])
        if not buttons:
            return []
        edges = []
        for button in buttons:
            left = button.mapTo(self.window(), QPoint(0, 0))
            left = self.mapFrom(self.window(), left).x()
            edges.append((left, left + button.width() - 1))
        result = []
        for row, (length, count) in enumerate(GUIDE_ROWS):
            y = MARGIN + row * ROW_SPACING
            for group in range(count):
                first, last = group * length, (group + 1) * length - 1
                if last < len(edges):
                    result.append((edges[first][0], edges[last][1], y))
        return result

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        pen = QPen(QColor(LINE_COLOR), LINE_WIDTH)
        pen.setCapStyle(Qt.PenCapStyle.FlatCap)
        painter.setPen(pen)
        for x1, x2, y in self.segments():
            painter.drawLine(x1, y, x2, y)
        painter.end()
