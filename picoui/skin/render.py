"""
picoui.skin.render
Painting from the specs in :mod:`picoui.skin.spec`.

:func:`paint_face`, :func:`paint_ear` and :func:`paint_rail` draw a whole
faceplate, cheek or rail. They are built on three dispatchers, which pick the
painter for each spec by its type: :func:`paint_fill` for materials,
:func:`paint_decoration` for what is drawn on the face, and
:func:`paint_detail` for what is drawn on a cheek or the rail. A new kind of material or decoration is added by
registering a painter for it, without touching the ones here::

    @paint_decoration.register
    def _(decoration: Stars, painter: QPainter, rect: QRectF) -> None:
        ...
"""

from __future__ import annotations

from functools import singledispatch
from typing import List

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen

from picoui.skin.gradient import apply_gradient_stops
from picoui.skin.spec import (
    Band,
    BrushedFill,
    EarSpec,
    FaceSpec,
    Frame,
    GradientBand,
    GradientFill,
    Grille,
    InsetRim,
    Keyboard,
    MaterialBand,
    PatchCord,
    PebbleFill,
    RailSpec,
    Rule,
    SaggingCable,
    SolidFill,
    StepButtons,
    Wash,
    WoodFill,
)
from picoui.skin.textures import GRAIN_SATIN, brushed_tile, pebble_tile, wood_tile

#: Screws are left off a cheek shorter than this: they would not read as
#: screws
MIN_SCREW_HEIGHT = 34


def _tile_height(rect: QRectF) -> int:
    return max(1, int(round(rect.height())))


# --- Materials --------------------------------------------------------------


@singledispatch
def paint_fill(material, painter: QPainter, rect: QRectF) -> None:
    """
    Fill ``rect`` with ``material``.

    :param material: a material spec
    :param painter: QPainter
    :param rect: QRectF the area
    :return: None
    """
    raise TypeError(f"No painter registered for material {type(material).__name__}")


@paint_fill.register
def _(material: GradientFill, painter: QPainter, rect: QRectF) -> None:
    end = rect.topRight() if material.direction == "horizontal" else rect.bottomLeft()
    gradient = QLinearGradient(rect.topLeft(), end)
    apply_gradient_stops(gradient, material.stops)
    painter.fillRect(rect, gradient)


@paint_fill.register
def _(material: BrushedFill, painter: QPainter, rect: QRectF) -> None:
    grain = GRAIN_SATIN if material.grain is None else material.grain
    tile = brushed_tile(
        _tile_height(rect), material.stops, grain=grain, coverage=material.coverage
    )
    painter.drawTiledPixmap(rect, tile)


@paint_fill.register
def _(material: WoodFill, painter: QPainter, rect: QRectF) -> None:
    painter.drawTiledPixmap(rect, wood_tile(_tile_height(rect), material.stops))


@paint_fill.register
def _(material: SolidFill, painter: QPainter, rect: QRectF) -> None:
    painter.fillRect(rect, material.color)


@paint_fill.register
def _(material: PebbleFill, painter: QPainter, rect: QRectF) -> None:
    tile = pebble_tile(material.size, material.color, material.grain)
    painter.drawTiledPixmap(rect, tile)


# --- Decorations ------------------------------------------------------------


def _band_top(rect: QRectF, edge: str, offset: float, thickness: float) -> float:
    if edge == "top":
        return rect.top() + offset
    return rect.bottom() - offset - thickness


@singledispatch
def paint_decoration(decoration, painter: QPainter, rect: QRectF) -> None:
    """
    Draw ``decoration`` on the face occupying ``rect``.

    :param decoration: a decoration spec
    :param painter: QPainter
    :param rect: QRectF the face
    :return: None
    """
    raise TypeError(
        f"No painter registered for decoration {type(decoration).__name__}"
    )


@paint_decoration.register
def _(band: Band, painter: QPainter, rect: QRectF) -> None:
    top = _band_top(rect, band.edge, band.offset, band.thickness)
    width = rect.width() / len(band.colors)
    painter.setPen(Qt.PenStyle.NoPen)
    for index, color in enumerate(band.colors):
        painter.setBrush(color)
        painter.drawRect(
            QRectF(rect.left() + index * width, top, width, band.thickness)
        )


@paint_decoration.register
def _(band: GradientBand, painter: QPainter, rect: QRectF) -> None:
    top = _band_top(rect, band.edge, band.offset, band.thickness)
    span = band.thickness if band.span is None else band.span
    if band.edge == "top":
        start, end = QPointF(rect.left(), top), QPointF(rect.left(), top + span)
    else:
        outer = top + band.thickness
        start, end = QPointF(rect.left(), outer), QPointF(rect.left(), outer - span)
    gradient = QLinearGradient(start, end)
    apply_gradient_stops(gradient, band.stops)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(gradient)
    painter.drawRect(QRectF(rect.left(), top, rect.width(), band.thickness))


@paint_decoration.register
def _(band: MaterialBand, painter: QPainter, rect: QRectF) -> None:
    top = _band_top(rect, band.edge, band.offset, band.thickness)
    painter.save()
    painter.setClipRect(
        QRectF(rect.left(), top, rect.width(), band.thickness),
        Qt.ClipOperation.IntersectClip,
    )
    paint_fill(band.material, painter, rect)
    painter.restore()


@paint_decoration.register
def _(rule: Rule, painter: QPainter, rect: QRectF) -> None:
    y = rect.top() + rule.offset if rule.edge == "top" else rect.bottom() - rule.offset
    painter.setPen(QPen(rule.color, rule.width))
    painter.drawLine(
        QPointF(rect.left() + rule.inset, y), QPointF(rect.right() - rule.inset, y)
    )


@paint_decoration.register
def _(rim: InsetRim, painter: QPainter, rect: QRectF) -> None:
    pen = QPen(rim.color, rim.width)
    pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.setPen(pen)
    inset = rim.width / 2
    painter.drawRoundedRect(
        rect.adjusted(inset, inset, -inset, -inset), rim.radius, rim.radius
    )


def paint_screw(painter: QPainter, centre: QPointF, radius: float, tint: QColor) -> None:
    """
    A rack screw: a slotted head.

    The painter is restored afterwards. The head is a filled ellipse, and
    a brush left set is what painted a whole cheek in the screw's colour.

    :param painter: QPainter
    :param centre: QPointF middle of the screw
    :param radius: float screw radius in px
    :param tint: QColor the metal's colour
    :return: None
    """
    painter.save()
    painter.setPen(QPen(QColor(0, 0, 0, 160), 1))
    painter.setBrush(tint)
    painter.drawEllipse(centre, radius, radius)
    painter.setPen(QPen(QColor(0, 0, 0, 120), 1))
    painter.drawLine(
        QPointF(centre.x() - radius * 0.55, centre.y()),
        QPointF(centre.x() + radius * 0.55, centre.y()),
    )
    painter.restore()


@paint_decoration.register
def _(frame: Frame, painter: QPainter, rect: QRectF) -> None:
    left, top, right, bottom = frame.inset
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.setPen(QPen(frame.color, frame.width))
    painter.drawRect(rect.adjusted(left, top, -right, -bottom))


@paint_decoration.register
def _(wash: Wash, painter: QPainter, rect: QRectF) -> None:
    gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
    apply_gradient_stops(gradient, wash.stops)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(gradient)
    painter.drawRect(rect)


#: The white keys of an octave a black key follows: C, D, F, G and A
_BLACK_AFTER = (0, 1, 3, 4, 5)


@paint_decoration.register
def _(keyboard: Keyboard, painter: QPainter, rect: QRectF) -> None:
    top = _band_top(rect, keyboard.edge, keyboard.offset, keyboard.thickness)
    strip = QRectF(rect.left(), top, rect.width(), keyboard.thickness)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(keyboard.ivory)
    painter.drawRect(strip)

    whites = 7 * keyboard.octaves
    key = strip.width() / whites
    painter.setPen(QPen(keyboard.divider, 1))
    for index in range(1, whites):
        x = strip.left() + index * key
        painter.drawLine(QPointF(x, strip.top()), QPointF(x, strip.bottom()))

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(keyboard.black)
    half = keyboard.black_width / 2
    for octave in range(keyboard.octaves):
        for white in _BLACK_AFTER:
            centre = strip.left() + (octave * 7 + white + 1) * key
            painter.drawRect(
                QRectF(
                    centre - key * half,
                    strip.top(),
                    key * keyboard.black_width,
                    strip.height() * keyboard.black_depth,
                )
            )


@paint_decoration.register
def _(row: StepButtons, painter: QPainter, rect: QRectF) -> None:
    top = _band_top(rect, row.edge, row.offset, row.thickness)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(row.background)
    painter.drawRect(QRectF(rect.left(), top, rect.width(), row.thickness))

    step = rect.width() / row.count
    buttons = top + row.button_top
    height = row.thickness - row.button_top
    lights = row.lights
    for index in range(row.count):
        left = rect.left() + index * step
        first = index % row.group == 0
        gap = row.group_gap if first and row.group_gap is not None else row.gap
        gap += step * row.gap_fraction
        painter.setBrush(row.colors[index % len(row.colors)])
        painter.drawRect(QRectF(left + gap, buttons, step - gap * 2, height))
        if lights is not None:
            lit = index % lights.every == 0
            painter.setBrush(lights.on if lit else lights.off)
            painter.drawRect(
                QRectF(left + step * 0.3, top, max(1.0, step * 0.4), lights.height)
            )


# --- Details: on a cheek or the rail ----------------------------------------


@singledispatch
def paint_detail(detail, painter: QPainter, rect: QRectF, side: str) -> None:
    """
    Draw ``detail`` on a cheek or the rail occupying ``rect``.

    :param detail: a detail spec
    :param painter: QPainter
    :param rect: QRectF the cheek or rail
    :param side: "left" or "right" for a cheek, "rail" for the rail
    :return: None
    """
    raise TypeError(f"No painter registered for detail {type(detail).__name__}")


def jack_points(rect: QRectF, loop_height: float) -> List[QPointF]:
    """
    Centres of the jacks on a cheek: a pair to loop a cable between, or, on
    a strip shorter than ``loop_height``, a single jack.

    :param rect: QRectF the cheek
    :param loop_height: float px
    :return: list of QPointF
    """
    x = rect.center().x()
    if rect.height() < loop_height:
        return [QPointF(x, rect.top() + rect.height() * 0.4)]
    # Closer to the ends on a tall cheek; on a short strip (a band, a status
    # bar) far enough apart for both jacks
    spread = 0.2 if rect.height() >= 90 else 0.27
    return [
        QPointF(x, rect.top() + rect.height() * spread),
        QPointF(x, rect.top() + rect.height() * (1.0 - spread)),
    ]


def jack_radius(rect: QRectF) -> float:
    """Smaller jacks on a short strip, so a pair still fits."""
    return max(2.5, min(rect.width() * 0.3, rect.height() * 0.17))


def paint_jack(painter: QPainter, centre: QPointF, width: float) -> None:
    """A jack socket: a silver nut round a black hole."""
    radius = max(3.0, width * 0.3)
    painter.setPen(QPen(QColor(20, 20, 20), 1))
    painter.setBrush(QColor(150, 150, 146))
    painter.drawEllipse(centre, radius, radius)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(4, 4, 4))
    painter.drawEllipse(centre, radius * 0.45, radius * 0.45)


def paint_plug(painter: QPainter, centre: QPointF, width: float, colour: QColor) -> None:
    """The plug in a jack, in its cable's colour."""
    radius = max(2.4, width * 0.2)
    painter.setPen(QPen(colour.darker(160), 1))
    painter.setBrush(colour)
    painter.drawEllipse(centre, radius, radius)


def paint_cable(
    painter: QPainter, path: QPainterPath, colour: QColor, width: float = 3.0
) -> None:
    """A cable: a dark edge, its colour, and a thin highlight."""
    painter.setBrush(Qt.BrushStyle.NoBrush)
    for pen_colour, pen_width in (
        (colour.darker(220), width + 1.4),
        (colour, width),
        (colour.lighter(150), max(0.8, width * 0.3)),
    ):
        pen = QPen(pen_colour, pen_width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawPath(path)


@paint_detail.register
def _(cord: PatchCord, painter: QPainter, rect: QRectF, side: str) -> None:
    painter.save()
    jacks = jack_points(rect, cord.loop_height)
    size = jack_radius(rect) / 0.3
    for jack in jacks:
        paint_jack(painter, jack, size)
    left_cheek = side != "right"
    colour = cord.colors[0 if left_cheek else 1]
    # Bowed toward the outer edge, so the cable clears the panel
    bow = rect.left() + 1.5 if left_cheek else rect.right() - 1.5
    width = min(cord.width, max(2.0, rect.height() * 0.09))
    cable = QPainterPath(jacks[0])
    if len(jacks) == 2:
        reach = (jacks[1].y() - jacks[0].y()) * 0.25
        cable.cubicTo(
            QPointF(bow, jacks[0].y() + reach),
            QPointF(bow, jacks[1].y() - reach),
            jacks[1],
        )
    else:
        # One jack: the cable hangs off it and out of the strip
        cable.cubicTo(
            QPointF(bow, jacks[0].y()),
            QPointF(bow, rect.bottom()),
            QPointF(bow, rect.bottom() + 2.0),
        )
    painter.save()
    painter.setClipRect(rect)
    paint_cable(painter, cable, colour, width=width)
    painter.restore()
    for jack in jacks:
        paint_plug(painter, jack, size, colour)
    painter.restore()


@paint_detail.register
def _(grille: Grille, painter: QPainter, rect: QRectF, side: str) -> None:
    inset_x, inset_y = grille.inset
    plate = rect.adjusted(inset_x, inset_y, -inset_x, -inset_y)
    if plate.width() <= 4 or plate.height() <= 8:
        return  # too small to read as a grille
    painter.setPen(QPen(grille.rim, 1))
    painter.setBrush(grille.plate)
    painter.drawRoundedRect(plate, 2, 2)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(grille.holes)
    pitch, radius = grille.pitch, grille.hole_radius
    y = plate.top() + pitch / 2
    row = 0
    while y < plate.bottom() - 1.0:
        x = plate.left() + pitch / 2 + (pitch / 2 if row % 2 else 0.0)
        while x < plate.right() - 1.0:
            painter.drawEllipse(QPointF(x, y), radius, radius)
            x += pitch
        y += pitch
        row += 1


@paint_detail.register
def _(cable: SaggingCable, painter: QPainter, rect: QRectF, side: str) -> None:
    top = rect.top() + 4.0
    start = QPointF(rect.left() + cable.inset, top)
    end = QPointF(rect.right() - cable.inset, top)
    # Lowest in the middle, just inside the rail: a cubic with both control
    # points at height c bottoms out at (top + 3c) / 4
    lowest = rect.bottom() - 2.5
    low = (4.0 * lowest - top) / 3.0
    path = QPainterPath(start)
    path.cubicTo(
        QPointF(start.x() + rect.width() * 0.25, low),
        QPointF(end.x() - rect.width() * 0.25, low),
        end,
    )
    painter.save()
    painter.setClipRect(rect)
    paint_cable(painter, path, cable.color, width=cable.width)
    painter.restore()
    # Plugged in at each end
    for point in (start, end):
        paint_jack(painter, point, cable.jack_size)
        paint_plug(painter, point, cable.jack_size, cable.color)


# --- Face and ear -----------------------------------------------------------


def paint_face(face: FaceSpec, painter: QPainter, rect: QRectF) -> None:
    """
    A faceplate from its spec: material and decorations clipped to the
    rounded outline, then the rim, then any overlays.

    A face without a material is the base skin's glossy panel, which
    :class:`~picoui.skin.base.Skin` paints itself; only its overlays are
    drawn here (see :func:`paint_overlays`).

    :param face: FaceSpec with a material
    :param painter: QPainter
    :param rect: QRectF the face
    :return: None
    """
    path = QPainterPath()
    path.addRoundedRect(rect, face.radius, face.radius)
    painter.save()
    painter.setClipPath(path)
    paint_fill(face.material, painter, rect)
    for decoration in face.decorations:
        paint_decoration(decoration, painter, rect)
    painter.restore()

    if face.rim is not None:
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(face.rim, 1))
        painter.drawPath(path)
    paint_overlays(face, painter, rect)


def paint_overlays(face: FaceSpec, painter: QPainter, rect: QRectF) -> None:
    """
    The decorations drawn over a finished face, unclipped.

    :param face: FaceSpec
    :param painter: QPainter
    :param rect: QRectF the face
    :return: None
    """
    for overlay in face.overlays:
        paint_decoration(overlay, painter, rect)


def paint_ear(
    ear: EarSpec, painter: QPainter, rect: QRectF, side: str = "left"
) -> None:
    """
    A cheek from its spec: material, wash, seam, details, rim, then screws.

    :param ear: EarSpec
    :param painter: QPainter
    :param rect: QRectF the cheek
    :param side: "left" or "right", the side of the face it is on; the seam
        runs along the edge facing the face
    :return: None
    """
    painter.save()
    paint_fill(ear.material, painter, rect)
    if ear.wash is not None:
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(ear.wash)
        painter.drawRect(rect)
    if ear.seam is not None:
        painter.setPen(QPen(ear.seam, 1))
        inner = rect.right() if side == "left" else rect.left()
        painter.drawLine(QPointF(inner, rect.top()), QPointF(inner, rect.bottom()))
    for detail in ear.details:
        paint_detail(detail, painter, rect, side)
    if ear.rim is not None:
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(ear.rim, 1))
        painter.drawRect(rect)
    if ear.screw is not None and rect.height() >= MIN_SCREW_HEIGHT:
        x = rect.center().x()
        for y in (rect.top() + ear.screw_inset, rect.bottom() - ear.screw_inset):
            paint_screw(painter, QPointF(x, y), ear.screw_radius, ear.screw)
    painter.restore()


def paint_rail(rail: RailSpec, painter: QPainter, rect: QRectF) -> None:
    """
    The rail from its spec: material, the line along its top, then details.

    :param rail: RailSpec
    :param painter: QPainter
    :param rect: QRectF the rail
    :return: None
    """
    painter.save()
    paint_fill(rail.material, painter, rect)
    if rail.line is not None:
        painter.setPen(QPen(rail.line, 1))
        painter.drawLine(rect.topLeft(), rect.topRight())
    for detail in rail.details:
        paint_detail(detail, painter, rect, "rail")
    painter.restore()
