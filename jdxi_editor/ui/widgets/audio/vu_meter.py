"""
Stereo meters.

The skin's ``meter`` style chooses the drawing: two horizontal bars on one dB
scale (MeterStyle.BARS, the default), circular dials (NEEDLES), or a pair of
backlit analogue VU meters (VINTAGE_VU, see analog_vu).
"""

import math
from typing import Optional

from PySide6.QtCore import QPointF, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QSizePolicy, QWidget

from jdxi_editor.audio.audio_snapshot import DB_FLOOR, clip_db
from jdxi_editor.ui.style.rack_skin import MeterStyle, active_skin
from jdxi_editor.ui.widgets.audio.analog_vu import EXPLANATION, paint_vintage_meters

#: -60 dB points up and to the left; 0 dB points up and to the right
NEEDLE_START = 160.0
NEEDLE_SWEEP = 140.0
#: The red zone begins here
OVERLOAD_DB = -3.0
NEEDLE_RADIUS = 0.72
ARC_RADIUS = 0.96

#: Shared scale, left to right
SCALE_DB = (-60.0, -24.0, -12.0, -6.0, -3.0, 0.0)
#: The green of the display takes over from the dim floor here
MID_DB = -12.0
BAR_HEIGHT = 96
_LABEL_W = 28.0
_READOUT_W = 68.0
_SCALE_H = 16.0
_CLIP = QColor(224, 68, 53)


def needle_angle(db: float) -> float:
    """
    Degrees, standard position, for a meter reading.

    :param db: float
    :return: float
    """
    span = (clip_db(db) - DB_FLOOR) / -DB_FLOOR
    return NEEDLE_START - span * NEEDLE_SWEEP


def needle_tip(origin_x: float, origin_y: float, radius: float, db: float) -> tuple[float, float]:
    """
    Where the needle ends.

    :param origin_x: float pivot
    :param origin_y: float pivot
    :param radius: float length
    :param db: float
    :return: tuple x, y in widget coordinates
    """
    angle = math.radians(needle_angle(db))
    return (
        origin_x + radius * math.cos(angle),
        origin_y - radius * math.sin(angle),
    )


def dial_rects(width: float, height: float) -> tuple[QRectF, QRectF]:
    """
    The left and right dials.

    :param width: float
    :param height: float
    :return: tuple of QRectF
    """
    side = min(width / 2.0 - 12.0, height - 8.0)
    side = max(side, 1.0)
    total = side * 2.0 + 8.0
    left = (width - total) / 2.0
    top = (height - side) / 2.0
    return (
        QRectF(left, top, side, side),
        QRectF(left + side + 8.0, top, side, side),
    )


def track_rect(width: float, height: float) -> QRectF:
    """
    The rectangle both bars and the scale share.

    :param width: float
    :param height: float
    :return: QRectF
    """
    return QRectF(
        _LABEL_W,
        _SCALE_H + 2.0,
        max(1.0, width - _LABEL_W - _READOUT_W),
        max(1.0, height - _SCALE_H - 6.0),
    )


def bar_x(rect: QRectF, db: float) -> float:
    """
    The x of a level on the shared scale.

    :param rect: QRectF the track
    :param db: float
    :return: float
    """
    span = (clip_db(db) - DB_FLOOR) / -DB_FLOOR
    return rect.left() + span * rect.width()


def row_bar(track: QRectF, index: int) -> QRectF:
    """
    One channel's bar inside the track.

    :param track: QRectF
    :param index: int 0 is left, 1 is right
    :return: QRectF
    """
    gap = 6.0
    row_h = (track.height() - gap) / 2.0
    top = track.top() + index * (row_h + gap)
    bar_h = min(14.0, max(4.0, row_h - 2.0))
    y = top + (row_h - bar_h) / 2.0
    return QRectF(track.left(), y, track.width(), bar_h)


class VUMeter(QWidget):
    """Stereo levels: bars by default, needles when the skin asks."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._peak = (DB_FLOOR, DB_FLOOR)
        self._hold = (DB_FLOOR, DB_FLOOR)
        self._vu = (DB_FLOOR, DB_FLOOR)
        self._fit_height()

    def sizeHint(self) -> QSize:
        if _vintage():
            return QSize(440, 190)
        if _needles():
            return QSize(400, 180)
        return QSize(400, BAR_HEIGHT)

    def set_levels(
        self,
        peak_left: float,
        peak_right: float,
        vu_left: float,
        vu_right: float,
        hold_left: float,
        hold_right: float,
    ) -> None:
        """
        Store the six meter readings and repaint.

        :return: None
        """
        self._peak = (float(peak_left), float(peak_right))
        self._vu = (float(vu_left), float(vu_right))
        self._hold = (float(hold_left), float(hold_right))
        self._fit_height()
        self.update()

    def paintEvent(self, _event) -> None:
        lcd = active_skin().lcd
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        painter.fillRect(self.rect(), QColor(lcd.bg_edge))
        readings = (
            (self._peak[0], self._vu[0], self._hold[0]),
            (self._peak[1], self._vu[1], self._hold[1]),
        )
        if _vintage():
            paint_vintage_meters(painter, self.width(), self.height(), readings)
        elif _needles():
            for rect, (peak, vu, hold) in zip(dial_rects(self.width(), self.height()), readings):
                self._draw_dial(painter, rect, peak, vu, hold, lcd)
        else:
            self._draw_bars(painter, readings, lcd)
        painter.end()

    def _fit_height(self) -> None:
        self.setToolTip(EXPLANATION if _vintage() else "")
        if _vintage():
            self.setMinimumHeight(150)
            self.setMaximumHeight(16777215)
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            return
        if _needles():
            self.setMinimumHeight(140)
            self.setMaximumHeight(16777215)
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            return
        self.setFixedHeight(BAR_HEIGHT)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def _draw_bars(self, painter, readings, lcd) -> None:
        track = track_rect(self.width(), self.height())
        self._draw_scale(painter, track, lcd)
        for index, (peak, vu, hold) in enumerate(readings):
            bar = row_bar(track, index)
            self._draw_bar(painter, bar, peak, vu, hold, "L" if index == 0 else "R", lcd)

    def _draw_scale(self, painter, track, lcd) -> None:
        font = QFont(painter.font())
        font.setPointSize(8)
        painter.setFont(font)
        painter.setPen(QColor(lcd.text_dim))
        for db in SCALE_DB:
            label = "0" if db == 0.0 else str(int(db))
            x = bar_x(track, db)
            painter.drawText(QRectF(x - 18.0, 0.0, 36.0, _SCALE_H), Qt.AlignmentFlag.AlignCenter, label)

    def _draw_bar(self, painter, bar, peak, vu, hold, name, lcd) -> None:
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(lcd.bg_mid))
        painter.drawRect(bar)
        self._fill_bar(painter, bar, vu, QColor(lcd.text_dim), QColor(lcd.text), _CLIP)
        self._mark(painter, bar, hold, QColor(lcd.text_dim), short=True)
        self._mark(painter, bar, peak, QColor(lcd.text), short=False)
        painter.setPen(QColor(lcd.text))
        painter.drawText(
            QRectF(0.0, bar.top(), _LABEL_W, bar.height()),
            Qt.AlignmentFlag.AlignCenter,
            name,
        )
        painter.drawText(
            QRectF(bar.right() + 6.0, bar.top(), _READOUT_W - 8.0, bar.height()),
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            f"{peak:.1f}",
        )

    def _fill_bar(self, painter, bar, vu, dim, mid, clip) -> None:
        spans = (
            (DB_FLOOR, MID_DB, dim),
            (MID_DB, OVERLOAD_DB, mid),
            (OVERLOAD_DB, 0.0, clip),
        )
        for start_db, end_db, color in spans:
            if vu <= start_db:
                continue
            right_db = min(vu, end_db)
            x0 = bar_x(bar, start_db)
            x1 = bar_x(bar, right_db)
            if x1 <= x0:
                continue
            painter.fillRect(QRectF(x0, bar.top(), x1 - x0, bar.height()), color)

    def _mark(self, painter, bar, db, color, short: bool) -> None:
        x = bar_x(bar, db)
        if short:
            y0 = bar.center().y() - 3.0
            y1 = bar.center().y() + 3.0
        else:
            y0 = bar.top()
            y1 = bar.bottom()
        painter.setPen(QPen(color, 2))
        painter.drawLine(QPointF(x, y0), QPointF(x, y1))

    def _draw_dial(self, painter, rect, peak, vu, hold, lcd) -> None:
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(lcd.bg_mid))
        painter.drawEllipse(rect)
        origin = rect.center()
        radius = rect.width() / 2.0
        self._draw_arc(painter, origin, radius * ARC_RADIUS, OVERLOAD_DB, 0.0, _CLIP)
        self._draw_arc(
            painter, origin, radius * ARC_RADIUS, DB_FLOOR, OVERLOAD_DB, QColor(lcd.text_dim)
        )
        self._draw_needle(painter, origin, radius * 0.45, vu, QColor(lcd.text_dim), 2)
        self._draw_needle(painter, origin, radius * NEEDLE_RADIUS, hold, QColor(lcd.text_dim), 1)
        self._draw_needle(painter, origin, radius * NEEDLE_RADIUS, peak, QColor(lcd.text), 4)

    def _draw_arc(self, painter, origin, radius, start_db, end_db, color) -> None:
        painter.setPen(QPen(color, 4))
        start = needle_tip(origin.x(), origin.y(), radius, start_db)
        end = needle_tip(origin.x(), origin.y(), radius, end_db)
        steps = 12
        previous = start
        for step in range(1, steps + 1):
            db = start_db + (end_db - start_db) * step / steps
            point = needle_tip(origin.x(), origin.y(), radius, db)
            painter.drawLine(QPointF(*previous), QPointF(*point))
            previous = point

    def _draw_needle(self, painter, origin, radius, db, color, width) -> None:
        tip = needle_tip(origin.x(), origin.y(), radius, db)
        painter.setPen(QPen(color, width))
        painter.drawLine(origin, QPointF(*tip))


def _meter_style() -> MeterStyle:
    return getattr(active_skin(), "meter", MeterStyle.BARS)


def _needles() -> bool:
    return _meter_style() == MeterStyle.NEEDLES


def _vintage() -> bool:
    return _meter_style() == MeterStyle.VINTAGE_VU
