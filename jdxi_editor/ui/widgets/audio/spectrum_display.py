"""
31 lit segments, one column per spectrum band.

A band at 0 dB reaches the top. A band on the floor draws nothing.
"""

from typing import Optional

import numpy as np
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QWidget

from jdxi_editor.audio.audio_snapshot import BAND_COUNT, DB_FLOOR, clip_db
from jdxi_editor.ui.style.rack_skin import active_skin

SEGMENT = 4
GAP = 2


def column_rect(width: float, index: int, count: int = BAND_COUNT) -> tuple[float, float]:
    """
    The left edge and width of one band.

    :param width: float widget width
    :param index: int band
    :param count: int bands
    :return: tuple left, width
    """
    column = width / count
    return index * column, column


class SpectrumDisplay(QWidget):
    """LED columns for the spectrum snapshot."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setMinimumHeight(140)
        self._bands = np.full(BAND_COUNT, DB_FLOOR, dtype=np.float64)

    def set_spectrum(self, bands: np.ndarray) -> None:
        """
        Store the band levels and repaint.

        :param bands: np.ndarray dB, one value per band
        :return: None
        """
        values = np.full(BAND_COUNT, DB_FLOOR, dtype=np.float64)
        count = min(BAND_COUNT, int(np.asarray(bands).shape[0]))
        values[:count] = np.asarray(bands, dtype=np.float64)[:count]
        self._bands = values
        self.update()

    def paintEvent(self, _event) -> None:
        lcd = active_skin().lcd
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(lcd.bg_edge))
        color = QColor(lcd.text)
        height = float(self.height())
        width = float(self.width())
        usable = max(1.0, height - 4.0)
        for index, level in enumerate(self._bands):
            span = (clip_db(float(level)) - DB_FLOOR) / -DB_FLOOR
            lit = span * usable
            left, column = column_rect(width, index)
            y = height - 2.0
            floor = height - 2.0 - lit
            while y - SEGMENT >= floor:
                painter.fillRect(
                    int(left) + 1,
                    int(y - SEGMENT),
                    max(1, int(column) - 2),
                    SEGMENT,
                    color,
                )
                y -= SEGMENT + GAP
        painter.end()
