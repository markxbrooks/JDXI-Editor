"""
picoui.skin.gradient
Gradients as configuration: each stop is a position and a colour, and a
gradient is any number of them in order.

These are generic rendering primitives. Named gradients (a skin's brushed
aluminium, a cabinet's wood) are defined where the material is, and applied
to whatever QGradient is being painted with.

Example:
    >>> from PySide6.QtGui import QLinearGradient
    >>> metal = GradientColorStops((
    ...     GradientStop(0.0, "#8A8A87"),
    ...     GradientStop(0.35, "#B8B8B4"),
    ...     GradientStop(1.0, "#777875"),
    ... ))
    >>> gradient = QLinearGradient(0, 0, 0, 100)
    >>> apply_gradient_stops(gradient, metal)
    >>> [round(position, 2) for position, _colour in gradient.stops()]
    [0.0, 0.35, 1.0]
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, Union

from PySide6.QtGui import QColor, QGradient

ColorLike = Union[QColor, str]


@dataclass(frozen=True)
class GradientStop:
    """
    One stop of a gradient.

    :param position: float where the stop sits, 0 (start) to 1 (end)
    :param color: QColor | str the colour there; a name such as "#8A8A87" is
        turned into a QColor
    """

    position: float
    color: QColor

    def __post_init__(self) -> None:
        if not 0.0 <= float(self.position) <= 1.0:
            raise ValueError(
                f"Gradient position must be between 0 and 1, not {self.position}"
            )
        color = self.color if isinstance(self.color, QColor) else QColor(self.color)
        if not color.isValid():
            raise ValueError(f"Not a colour: {self.color!r}")
        # Frozen: set through object, once, while being built
        object.__setattr__(self, "position", float(self.position))
        object.__setattr__(self, "color", color)


@dataclass(frozen=True)
class GradientColorStops:
    """
    A gradient's stops: at least two, in order of position.

    :param stops: tuple of GradientStop, start to end
    """

    stops: Tuple[GradientStop, ...]

    def __post_init__(self) -> None:
        stops = tuple(self.stops)
        if len(stops) < 2:
            raise ValueError("A gradient needs at least two stops")
        positions = [stop.position for stop in stops]
        if positions != sorted(positions):
            raise ValueError(f"Gradient stops must be in order of position: {positions}")
        object.__setattr__(self, "stops", stops)


def apply_gradient_stops(gradient: QGradient, color_stops: GradientColorStops) -> None:
    """
    Give ``gradient`` every stop of ``color_stops``.

    :param gradient: QGradient the gradient being painted with (the target)
    :param color_stops: GradientColorStops the configuration applied to it
    :return: None
    """
    for stop in color_stops.stops:
        gradient.setColorAt(stop.position, stop.color)
