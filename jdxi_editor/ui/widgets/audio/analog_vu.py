"""
Vintage VU meters: a pair of backlit cream faces in a dark housing, each with
a needle on a classic VU scale, a red zone above 0 VU and a peak LED.

The scale is a VU scale, not a digital one. The level it shows is the
average (RMS) level in dBFS from the analyser, read against a reference:
0 VU is ``VU_REFERENCE_DBFS`` (-18 dBFS, the usual digital studio alignment).
That is printed on the face, and the digital peak is shown on its own, as a
number in dBFS and as the LED, so the two are not confused.

As on a real VU meter the scale is linear in voltage, so -20 to -10 VU is
squeezed into the left end and 0 VU sits about two thirds of the way across.
"""

from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QRadialGradient,
)

#: 0 VU is this many dBFS (RMS)
VU_REFERENCE_DBFS = -18.0
#: The ends of the scale, in VU
VU_MIN = -20.0
VU_MAX = 3.0
#: Numbered marks; 0 to +3 are the red zone
VU_MARKS = (-20, -10, -7, -5, -3, -2, -1, 0, 1, 2, 3)
#: Percentage marks under the arc (100% is 0 VU)
PERCENT_MARKS = (20, 40, 60, 80, 100)
#: The peak LED lights when the held digital peak reaches this
PEAK_LED_DBFS = -1.0
REFERENCE_NOTE = f"0 VU = {VU_REFERENCE_DBFS:g} dBFS"
#: What the meters show, for the tooltip
EXPLANATION = (
    f"VU meters: the needle is the average (RMS) level, {REFERENCE_NOTE}.\n"
    "PEAK is the digital peak level in dBFS; the LED lights when it "
    f"reaches {PEAK_LED_DBFS:g} dBFS."
)

#: Widest swing of the needle either side of upright, degrees
MAX_HALF_SWEEP = 48.0

FACE_LIGHT = QColor("#FFF3D2")  # behind the needle, where the lamp is
FACE_EDGE = QColor("#CDB98A")  # the corners, out of the lamp's reach
INK = QColor("#1C1A16")
RED = QColor("#C42A1E")
LED_OFF = QColor("#3C1712")
LED_ON = QColor("#FF3B26")
HOUSING_TOP = QColor("#2A2B2E")
HOUSING_BOTTOM = QColor("#121214")


def vu_from_dbfs(dbfs: float) -> float:
    """The VU reading of an RMS level in dBFS (not clamped)."""
    return float(dbfs) - VU_REFERENCE_DBFS


def scale_fraction(vu: float) -> float:
    """
    Where `vu` sits across the scale, 0 at -20 VU's end to 1 at +3 VU, linear
    in voltage as a VU meter is. Readings off the scale rest on its pins.
    """
    vu = min(max(vu, VU_MIN), VU_MAX)
    low = 10 ** (VU_MIN / 20.0)
    high = 10 ** (VU_MAX / 20.0)
    return (10 ** (vu / 20.0) - low) / (high - low)


def face_rects(width: float, height: float) -> tuple[QRectF, QRectF, QRectF]:
    """
    The housing and the left and right faces inside it.

    :return: (housing, left face, right face)
    """
    margin = 4.0
    housing = QRectF(margin, margin, max(1.0, width - 2 * margin), max(1.0, height - 2 * margin))
    pad = max(6.0, min(14.0, housing.height() * 0.07))
    gap = pad * 1.6
    face_w = max(1.0, (housing.width() - 2 * pad - gap) / 2.0)
    face_h = max(1.0, housing.height() - 2 * pad)
    # Keep the faces about 1.65 : 1, centred, as meter faces are
    if face_w / face_h > 1.9:
        face_w = face_h * 1.9
    elif face_w / face_h < 1.3:
        face_h = face_w / 1.3
    total = face_w * 2 + gap
    left = housing.center().x() - total / 2.0
    top = housing.center().y() - face_h / 2.0
    return (
        housing,
        QRectF(left, top, face_w, face_h),
        QRectF(left + face_w + gap, top, face_w, face_h),
    )


class FaceGeometry:
    """The pivot, arc and sweep of one face."""

    def __init__(self, face: QRectF):
        self.face = face
        self.pivot = QPointF(face.center().x(), face.bottom() + face.height() * 0.32)
        arc_top = face.top() + face.height() * 0.40
        self.radius = self.pivot.y() - arc_top
        half = math.degrees(math.asin(min(1.0, face.width() * 0.40 / self.radius)))
        self.half_sweep = min(MAX_HALF_SWEEP, half)

    def angle(self, vu: float) -> float:
        """Degrees from upright, positive to the right."""
        return -self.half_sweep + 2.0 * self.half_sweep * scale_fraction(vu)

    def point(self, vu: float, radius_scale: float = 1.0) -> QPointF:
        theta = math.radians(self.angle(vu))
        r = self.radius * radius_scale
        return QPointF(self.pivot.x() + r * math.sin(theta), self.pivot.y() - r * math.cos(theta))


def paint_vintage_meters(painter: QPainter, width: float, height: float, readings) -> None:
    """
    Paint the housing and both faces.

    :param readings: two (peak dBFS, vu dBFS, held peak dBFS) tuples, left then right
    """
    housing, *faces = face_rects(width, height)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    _paint_housing(painter, housing)
    for face, name, (peak, vu, hold) in zip(faces, ("L", "R"), readings):
        _paint_face(painter, face, name, peak, vu_from_dbfs(vu), hold)


def _paint_housing(painter: QPainter, rect: QRectF) -> None:
    gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
    gradient.setColorAt(0.0, HOUSING_TOP)
    gradient.setColorAt(1.0, HOUSING_BOTTOM)
    painter.setPen(QPen(QColor("#060607"), 1))
    painter.setBrush(gradient)
    painter.drawRoundedRect(rect, 5, 5)
    painter.setPen(QPen(QColor(255, 255, 255, 30), 1))
    painter.drawLine(
        QPointF(rect.left() + 5, rect.top() + 1.5), QPointF(rect.right() - 5, rect.top() + 1.5)
    )


def _font(painter: QPainter, px: float, bold: bool = False) -> QFont:
    font = QFont(painter.font())
    font.setPixelSize(max(6, int(round(px))))
    font.setBold(bold)
    return font


def _paint_face(painter: QPainter, face: QRectF, name: str, peak: float, vu: float, hold: float) -> None:
    geo = FaceGeometry(face)
    h = face.height()
    path = QPainterPath()
    path.addRoundedRect(face, 3, 3)

    # The recess the face sits in, then the backlit card
    painter.setPen(QPen(QColor("#050505"), 2))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawRoundedRect(face.adjusted(-1.5, -1.5, 1.5, 1.5), 4, 4)
    glow = QRadialGradient(QPointF(face.center().x(), face.bottom()), face.width() * 0.75)
    glow.setColorAt(0.0, FACE_LIGHT)
    glow.setColorAt(1.0, FACE_EDGE)
    painter.fillPath(path, glow)

    painter.save()
    painter.setClipPath(path)
    _paint_scale(painter, geo)

    # VU, and what 0 VU means here
    painter.setPen(INK)
    painter.setFont(_font(painter, h * 0.17, bold=True))
    # In the top-left corner, above the scale's low end
    painter.drawText(
        QRectF(face.left() + face.width() * 0.05, face.top() + h * 0.03, face.width() * 0.3, h * 0.18),
        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
        "VU",
    )
    painter.setFont(_font(painter, h * 0.07))
    note = QRectF(face.left() + face.width() * 0.05, face.top() + h * 0.20, face.width() * 0.5, h * 0.09)
    used = painter.fontMetrics().boundingRect(REFERENCE_NOTE).width()
    note.setWidth(used + 2)
    if not note.intersects(_mark_label_rect(geo, -7)) and not note.intersects(_mark_label_rect(geo, -5)):
        # On a small face it would run into the numbers: the tooltip says it
        painter.drawText(note, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, REFERENCE_NOTE)
    # The digital peak, kept apart from the VU reading
    painter.drawText(
        QRectF(face.left(), face.bottom() - h * 0.16, face.width() * 0.94, h * 0.12),
        Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
        f"PEAK {peak:.1f} dBFS",
    )
    painter.setFont(_font(painter, h * 0.10, bold=True))
    painter.drawText(
        QRectF(face.left() + face.width() * 0.06, face.bottom() - h * 0.16, face.width() * 0.2, h * 0.12),
        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
        name,
    )

    _paint_needle(painter, geo, vu)
    # Glass: a faint reflection over the top of the face
    shine = QLinearGradient(face.topLeft(), QPointF(face.left(), face.top() + h * 0.5))
    shine.setColorAt(0.0, QColor(255, 255, 255, 46))
    shine.setColorAt(1.0, QColor(255, 255, 255, 0))
    painter.fillRect(QRectF(face.left(), face.top(), face.width(), h * 0.5), shine)
    painter.restore()

    _paint_led(painter, face, hold >= PEAK_LED_DBFS)


def _paint_scale(painter: QPainter, geo: FaceGeometry) -> None:
    h = geo.face.height()
    stroke = max(1.0, h * 0.012)
    # The arc: black up to 0 VU, a thick red band above it
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.setPen(QPen(INK, stroke))
    _arc(painter, geo, VU_MIN, 0.0, 1.0)
    band = QPen(RED, max(2.0, h * 0.045))
    band.setCapStyle(Qt.PenCapStyle.FlatCap)
    painter.setPen(band)
    _arc(painter, geo, 0.0, VU_MAX, 0.985)

    painter.setFont(_font(painter, h * 0.105))
    for vu in VU_MARKS:
        colour = RED if vu > 0 else INK
        painter.setPen(QPen(colour, stroke * (1.6 if vu in (-20, -10, 0, 3) else 1.0)))
        painter.drawLine(geo.point(vu, 1.0), geo.point(vu, 1.075))
        label = str(abs(vu)) if vu else "0"
        painter.drawText(_mark_label_rect(geo, vu), Qt.AlignmentFlag.AlignCenter, label)
    # Minus at the left end, plus at the right, as on the hardware
    painter.setFont(_font(painter, h * 0.13, bold=True))
    for vu, sign, colour in ((VU_MIN, "−", INK), (VU_MAX, "+", RED)):
        centre = geo.point(vu, 0.9)
        offset = -h * 0.08 if vu < 0 else h * 0.08
        painter.setPen(colour)
        painter.drawText(
            QRectF(centre.x() + offset - h * 0.08, centre.y() - h * 0.08, h * 0.16, h * 0.16),
            Qt.AlignmentFlag.AlignCenter,
            sign,
        )

    # Percent, small, under the arc, when there is room for it
    if geo.face.width() >= 170:
        painter.setPen(QPen(INK, max(1.0, stroke * 0.8)))
        painter.setFont(_font(painter, h * 0.07))
        for percent in PERCENT_MARKS:
            vu = 20.0 * math.log10(percent / 100.0)
            if vu < VU_MIN:
                continue
            painter.drawLine(geo.point(vu, 0.94), geo.point(vu, 0.985))
            centre = geo.point(vu, 0.88)
            painter.drawText(
                QRectF(centre.x() - h * 0.1, centre.y() - h * 0.05, h * 0.2, h * 0.1),
                Qt.AlignmentFlag.AlignCenter,
                str(percent),
            )


def _mark_label_rect(geo: FaceGeometry, vu: float) -> QRectF:
    """Where a scale number is printed."""
    h = geo.face.height()
    centre = geo.point(vu, 1.16)
    return QRectF(centre.x() - h * 0.12, centre.y() - h * 0.07, h * 0.24, h * 0.14)


def _arc(painter: QPainter, geo: FaceGeometry, start: float, end: float, radius_scale: float) -> None:
    steps = 32
    path = QPainterPath(geo.point(start, radius_scale))
    for step in range(1, steps + 1):
        path.lineTo(geo.point(start + (end - start) * step / steps, radius_scale))
    painter.drawPath(path)


def _paint_needle(painter: QPainter, geo: FaceGeometry, vu: float) -> None:
    h = geo.face.height()
    tip = geo.point(vu, 1.1)
    # A soft shadow cast on the card, then the needle
    shadow_offset = QPointF(h * 0.025, h * 0.02)
    painter.setPen(QPen(QColor(0, 0, 0, 55), max(1.5, h * 0.018)))
    painter.drawLine(geo.pivot + shadow_offset, tip + shadow_offset)
    pen = QPen(INK, max(1.2, h * 0.013))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen)
    painter.drawLine(geo.pivot, tip)


def _paint_led(painter: QPainter, face: QRectF, lit: bool) -> None:
    h = face.height()
    radius = max(3.0, h * 0.045)
    centre = QPointF(face.right() - h * 0.12, face.top() + h * 0.13)
    if lit:
        halo = QRadialGradient(centre, radius * 3.2)
        halo.setColorAt(0.0, QColor(255, 80, 50, 150))
        halo.setColorAt(1.0, QColor(255, 80, 50, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(halo)
        painter.drawEllipse(centre, radius * 3.2, radius * 3.2)
    bulb = QRadialGradient(centre - QPointF(radius * 0.3, radius * 0.3), radius * 1.3)
    base = LED_ON if lit else LED_OFF
    bulb.setColorAt(0.0, base.lighter(170 if lit else 140))
    bulb.setColorAt(1.0, base)
    painter.setPen(QPen(QColor("#0A0A0A"), 1.2))
    painter.setBrush(bulb)
    painter.drawEllipse(centre, radius, radius)


def led_centre(face: QRectF) -> QPointF:
    """Where the peak LED sits on a face (for tests)."""
    h = face.height()
    return QPointF(face.right() - h * 0.12, face.top() + h * 0.13)
