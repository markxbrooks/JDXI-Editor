"""
picoui.skin.qt
Where a skin's plain-data colours meet Qt.

:mod:`picoui.skin.gradient` keeps colours as RGBA tuples with no Qt in
them. The painting code turns them into QColors here, at the point of use.
"""

from __future__ import annotations

from PySide6.QtGui import QColor, QGradient

from picoui.skin.gradient import RGBA, ColorValue, GradientColorStops, parse_color


def qcolor(value: ColorValue) -> QColor:
    """
    A QColor from a colour written as "#RRGGBB", (r, g, b) or (r, g, b, a).

    :param value: ColorValue
    :return: QColor, a new one each call
    """
    red, green, blue, alpha = parse_color(value)
    return QColor(red, green, blue, alpha)


def rgba(color: QColor) -> RGBA:
    """
    The (r, g, b, a) of a QColor, as a gradient stop takes it.

    :param color: QColor
    :return: RGBA
    """
    return tuple(color.getRgb())  # type: ignore[return-value]


def apply_gradient_stops(gradient: QGradient, color_stops: GradientColorStops) -> None:
    """
    Give ``gradient`` every stop of ``color_stops``.

    :param gradient: QGradient the gradient being painted with (the target)
    :param color_stops: GradientColorStops the configuration applied to it
    :return: None
    """
    for stop in color_stops.stops:
        gradient.setColorAt(stop.position, QColor(*stop.color))
