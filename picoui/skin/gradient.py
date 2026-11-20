"""
picoui.skin.gradient
Gradients as configuration: each stop is a position and a colour, and a
gradient is any number of them in order.

These are plain data, with no Qt in them: a colour is an ``(r, g, b, a)``
tuple of 0-255 integers, written as that tuple, as ``(r, g, b)``, or as
``"#RRGGBB"``. So a gradient can be declared, compared, hashed (the tiles
drawn from one are cached by it) and stored without a QApplication.
:func:`picoui.skin.qt.apply_gradient_stops` gives one to a QGradient when
it is painted.

Named gradients (a skin's brushed aluminium, a cabinet's wood) are defined
where the material is.

Example:
    >>> metal = GradientColorStops((
    ...     GradientStop(0.0, "#8A8A87"),
    ...     GradientStop(0.35, (184, 184, 180)),
    ...     GradientStop(1.0, (119, 120, 117, 255)),
    ... ))
    >>> metal.stops[0].color
    (138, 138, 135, 255)
    >>> metal.stops[1].hex
    '#B8B8B4'
    >>> GradientStop(0.0, "#777875") == GradientStop(0.0, (119, 120, 117))
    True
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Tuple, Union

#: A colour as 0-255 integers: red, green, blue, alpha
RGBA = Tuple[int, int, int, int]

#: A colour as a gradient may be written: "#RRGGBB", (r, g, b) or
#: (r, g, b, a), each 0-255
ColorValue = Union[str, Tuple[int, int, int], Tuple[int, int, int, int]]

_HEX = re.compile(r"#([0-9A-Fa-f]{6})")


def parse_color(value: ColorValue) -> RGBA:
    """
    The ``(r, g, b, a)`` of a colour written as "#RRGGBB", (r, g, b) or
    (r, g, b, a).

    Eight-digit hex is refused: Qt reads it as #AARRGGBB and CSS as
    #RRGGBBAA, so a colour with alpha is written as a tuple.

    :param value: ColorValue
    :return: RGBA
    :raises ValueError: if it is not a colour
    """
    if isinstance(value, str):
        match = _HEX.fullmatch(value.strip())
        if not match:
            raise ValueError(
                f"Not a colour: {value!r}; write '#RRGGBB', or a tuple for alpha"
            )
        digits = match.group(1)
        return (int(digits[0:2], 16), int(digits[2:4], 16), int(digits[4:6], 16), 255)
    if isinstance(value, tuple) and len(value) in (3, 4):
        channels = tuple(value) + ((255,) if len(value) == 3 else ())
        if all(isinstance(c, int) and not isinstance(c, bool) and 0 <= c <= 255 for c in channels):
            return channels  # type: ignore[return-value]
    raise ValueError(f"Not a colour: {value!r}; write '#RRGGBB', (r, g, b) or (r, g, b, a)")


@dataclass(frozen=True)
class GradientStop:
    """
    One stop of a gradient.

    :param position: float where the stop sits, 0 (start) to 1 (end)
    :param color: ColorValue the colour there, kept as an RGBA tuple
    """

    position: float
    color: RGBA

    def __post_init__(self) -> None:
        if not 0.0 <= float(self.position) <= 1.0:
            raise ValueError(
                f"Gradient position must be between 0 and 1, not {self.position}"
            )
        # Frozen: set through object, once, while being built
        object.__setattr__(self, "position", float(self.position))
        object.__setattr__(self, "color", parse_color(self.color))

    @property
    def hex(self) -> str:
        """The colour as "#RRGGBB", leaving out its alpha."""
        return "#{:02X}{:02X}{:02X}".format(*self.color[:3])


@dataclass(frozen=True)
class GradientColorStops:
    """
    A gradient's stops: at least two, in order of position.

    :param stops: tuple of GradientStop, start to end
    """

    stops: tuple[GradientStop, ...]

    def __post_init__(self) -> None:
        stops = tuple(self.stops)
        if len(stops) < 2:
            raise ValueError("A gradient needs at least two stops")
        positions = [stop.position for stop in stops]
        if positions != sorted(positions):
            raise ValueError(f"Gradient stops must be in order of position: {positions}")
        object.__setattr__(self, "stops", stops)


def __getattr__(name: str):
    # apply_gradient_stops lived here; it needs Qt, so it lives in
    # picoui.skin.qt, and an old import is handed it from there
    if name == "apply_gradient_stops":
        from picoui.skin.qt import apply_gradient_stops

        return apply_gradient_stops
    raise AttributeError(name)
