"""
picoui.skin.spec
What a faceplate and its cheeks look like, as data.

A skin can describe its face and ears with these instead of painting them:
a material to fill with, the decorations printed or moulded on top (edge
bands, rules), a rim, and for an ear its screws. The specs are plain data,
with no Qt in them: every colour is kept as an ``(r, g, b, a)`` tuple (see
:mod:`picoui.skin.gradient`), so a skin's look can be declared, compared,
hashed or loaded from a file without a QApplication.
:mod:`picoui.skin.render` turns them into painting, and
:class:`~picoui.skin.base.JDXiSkin` calls it when a skin declares
:attr:`~picoui.skin.base.JDXiSkin.face` or :attr:`~picoui.skin.base.JDXiSkin.ear`.

Every spec is a frozen dataclass, so a skin's look is a value: two skins can
share one, and :func:`dataclasses.replace` makes a variant.

Example:
    >>> from picoui.skin.gradient import GradientColorStops, GradientStop
    >>> charcoal = GradientColorStops((
    ...     GradientStop(0.0, "#343538"),
    ...     GradientStop(1.0, "#212224"),
    ... ))
    >>> face = FaceSpec(
    ...     material=GradientFill(charcoal),
    ...     decorations=(Band("bottom", 4, ("#E33B2E", "#EE7B2C")),),
    ...     rim="#101112",
    ... )
    >>> face.decorations[0].edge
    'bottom'
    >>> face.rim
    (16, 17, 18, 255)

The machine details that make a skin recognisable are specs too, so any
skin can use them: a :class:`Keyboard` of step keys, a row of
:class:`StepButtons` (with :class:`StepLights` over them), a
:class:`PatchCord` on each cheek, a speaker :class:`Grille`, and a
:class:`SaggingCable` along a :class:`RailSpec`.

Something none of these describe is painted by overriding a paint hook, or
added as a new kind of decoration by registering it with
:func:`picoui.skin.render.paint_decoration` (on the face) or
:func:`picoui.skin.render.paint_detail` (on a cheek or the rail).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple, Union

from picoui.skin.gradient import ColorValue, GradientColorStops, parse_color

#: A colour as a skin may write it: "#RRGGBB", (r, g, b) or (r, g, b, a),
#: each 0-255. Every spec keeps it as an RGBA tuple.
ColorSpec = ColorValue

EDGES = ("top", "bottom")
DIRECTIONS = ("vertical", "horizontal")


def _set_colors(spec: object, *names: str) -> None:
    """Turn the named fields of a frozen spec into RGBA tuples, once, when built."""
    for name in names:
        value = getattr(spec, name)
        if value is not None:
            object.__setattr__(spec, name, parse_color(value))


def _check_edge(edge: str) -> None:
    if edge not in EDGES:
        raise ValueError(f"Edge must be one of {EDGES}, not {edge!r}")


# --- Materials: what an area is filled with ---------------------------------


@dataclass(frozen=True)
class GradientFill:
    """
    A smooth gradient, as painted metal or moulded plastic.

    :param stops: GradientColorStops the colours across the area
    :param direction: "vertical" (top to bottom) or "horizontal" (left to
        right, as a cheek shading away from its outer edge)
    """

    stops: GradientColorStops
    direction: str = "vertical"

    def __post_init__(self) -> None:
        if self.direction not in DIRECTIONS:
            raise ValueError(
                f"Direction must be one of {DIRECTIONS}, not {self.direction!r}"
            )


@dataclass(frozen=True)
class BrushedFill:
    """
    Horizontally brushed metal (see :func:`picoui.skin.textures.brushed_tile`).

    :param stops: GradientColorStops the metal's shading down the face
    :param grain: int strength of the brushing; None for the satin default
    :param coverage: float share of rows that take a stroke, in 0..1
    """

    stops: GradientColorStops
    grain: Optional[int] = None
    coverage: float = 1.0


@dataclass(frozen=True)
class WoodFill:
    """
    Wood, the grain running along it (see :func:`picoui.skin.textures.wood_tile`).

    :param stops: GradientColorStops the colour through the wood
    """

    stops: GradientColorStops


@dataclass(frozen=True)
class SolidFill:
    """
    One flat colour, as a plain plate.

    :param color: ColorSpec
    """

    color: ColorSpec

    def __post_init__(self) -> None:
        _set_colors(self, "color")


@dataclass(frozen=True)
class PebbleFill:
    """
    Textured matte paint, speckled in no direction (see
    :func:`picoui.skin.textures.pebble_tile`).

    :param color: ColorSpec the paint
    :param size: int px of the repeating tile
    :param grain: int strength of the speckle
    """

    color: ColorSpec
    size: int = 64
    grain: int = 10

    def __post_init__(self) -> None:
        _set_colors(self, "color")


Material = Union[GradientFill, BrushedFill, WoodFill, SolidFill, PebbleFill]


# --- Decorations: drawn on the face, inside its outline ---------------------


@dataclass(frozen=True)
class Band:
    """
    A solid band the full width of the face, along its top or bottom edge.

    Several colours split the band into equal blocks, left to right, as the
    TR-808's run of step-button colours.

    :param edge: "top" or "bottom"
    :param thickness: float px
    :param colors: tuple of ColorSpec, one or more
    :param offset: float px in from the edge
    """

    edge: str
    thickness: float
    colors: Tuple[ColorSpec, ...]
    offset: float = 0.0

    def __post_init__(self) -> None:
        _check_edge(self.edge)
        colors = tuple(parse_color(color) for color in self.colors)
        if not colors:
            raise ValueError("A band needs at least one colour")
        object.__setattr__(self, "colors", colors)


@dataclass(frozen=True)
class GradientBand:
    """
    A band shaded across its thickness, as a lit chamfer.

    :param edge: "top" or "bottom"
    :param thickness: float px of band drawn
    :param stops: GradientColorStops from the edge inwards
    :param offset: float px in from the edge
    :param span: float px the gradient runs over, from the band's outer
        side; None for its thickness. A longer span leaves the band in the
        lighter part of the gradient.
    """

    edge: str
    thickness: float
    stops: GradientColorStops
    offset: float = 0.0
    span: Optional[float] = None

    def __post_init__(self) -> None:
        _check_edge(self.edge)


@dataclass(frozen=True)
class MaterialBand:
    """
    A band of another material along the top or bottom edge, as the wooden
    lip of a cabinet above its panel.

    The material is laid as if it covered the whole face, and shows only in
    the band, so a wood or metal tile shades the same as it would on the
    cheeks beside it.

    :param edge: "top" or "bottom"
    :param thickness: float px
    :param material: Material
    :param offset: float px in from the edge
    """

    edge: str
    thickness: float
    material: "Material"
    offset: float = 0.0

    def __post_init__(self) -> None:
        _check_edge(self.edge)


@dataclass(frozen=True)
class Rule:
    """
    A line across the face, parallel to its top or bottom edge.

    :param edge: "top" or "bottom"
    :param offset: float px from that edge to the line's centre
    :param color: ColorSpec
    :param width: float pen width in px
    :param inset: float px left clear at each end
    """

    edge: str
    offset: float
    color: ColorSpec
    width: float = 1.0
    inset: float = 1.0

    def __post_init__(self) -> None:
        _check_edge(self.edge)
        _set_colors(self, "color")


@dataclass(frozen=True)
class InsetRim:
    """
    A border stroked just inside the face's edge, as a coloured body showing
    round an inset panel.

    :param color: ColorSpec
    :param width: float px
    :param radius: float corner radius in px
    """

    color: ColorSpec
    width: float = 2.0
    radius: float = 2.0

    def __post_init__(self) -> None:
        _set_colors(self, "color")


@dataclass(frozen=True)
class Frame:
    """
    A box stroked inside the face, as a printed section outline.

    :param color: ColorSpec
    :param inset: (left, top, right, bottom) px in from each edge
    :param width: float pen width in px
    """

    color: ColorSpec
    inset: Tuple[float, float, float, float] = (2.0, 2.0, 2.0, 2.0)
    width: float = 1.0

    def __post_init__(self) -> None:
        _set_colors(self, "color")


@dataclass(frozen=True)
class Wash:
    """
    A translucent gradient over the whole face, to shade a texture.

    :param stops: GradientColorStops, usually with alpha
    """

    stops: GradientColorStops


@dataclass(frozen=True)
class Keyboard:
    """
    A strip of piano keys along an edge, as the TB-303's step buttons.

    :param thickness: float px
    :param octaves: int octaves across the face
    :param ivory: ColorSpec the white keys
    :param black: ColorSpec the black keys
    :param divider: ColorSpec the lines between white keys
    :param edge: "top" or "bottom"
    :param offset: float px in from the edge
    :param black_depth: float share of the strip the black keys reach down
    :param black_width: float black key width, as a share of a white key's
    """

    thickness: float
    octaves: int
    ivory: ColorSpec
    black: ColorSpec
    divider: ColorSpec = (120, 118, 110)
    edge: str = "bottom"
    offset: float = 0.0
    black_depth: float = 0.62
    black_width: float = 0.6

    def __post_init__(self) -> None:
        _check_edge(self.edge)
        if self.octaves < 1:
            raise ValueError("A keyboard needs at least one octave")
        _set_colors(self, "ivory", "black", "divider")


@dataclass(frozen=True)
class StepLights:
    """
    An LED over each step button, lit on the first step of each group.

    :param height: float px
    :param on: ColorSpec a lit LED
    :param off: ColorSpec an unlit one
    :param every: int a light is lit every this many steps
    """

    height: float
    on: ColorSpec
    off: ColorSpec
    every: int = 4

    def __post_init__(self) -> None:
        _set_colors(self, "on", "off")


@dataclass(frozen=True)
class StepButtons:
    """
    A row of step buttons, pads or keys along an edge, with the background
    showing between them.

    :param thickness: float px of the whole row, lights included
    :param count: int buttons across the face
    :param colors: tuple of ColorSpec, taken in turn by each button
    :param background: ColorSpec the strip or slot behind them
    :param group: int buttons per group; the first of each takes ``group_gap``
    :param gap: float px clear at each side of a button
    :param group_gap: float px at each side of a group's first button; None
        for ``gap``
    :param gap_fraction: float added to the gap, as a share of a button's
        pitch, for keys that keep their proportions at any width
    :param button_top: float px from the row's top to the buttons; the
        lights, if any, sit above them
    :param lights: Optional[StepLights]
    :param edge: "top" or "bottom"
    :param offset: float px in from the edge
    """

    thickness: float
    count: int
    colors: Tuple[ColorSpec, ...]
    background: ColorSpec
    group: int = 1
    gap: float = 0.0
    group_gap: Optional[float] = None
    gap_fraction: float = 0.0
    button_top: float = 0.0
    lights: Optional[StepLights] = None
    edge: str = "bottom"
    offset: float = 0.0

    def __post_init__(self) -> None:
        _check_edge(self.edge)
        if self.count < 1 or self.group < 1:
            raise ValueError("Step buttons need a count and a group of at least one")
        colors = tuple(parse_color(color) for color in self.colors)
        if not colors:
            raise ValueError("Step buttons need at least one colour")
        object.__setattr__(self, "colors", colors)
        _set_colors(self, "background")


Decoration = Union[
    Band, GradientBand, MaterialBand, Rule, InsetRim, Frame, Wash, Keyboard, StepButtons
]


# --- Details: drawn on a cheek or the rail ----------------------------------


@dataclass(frozen=True)
class PatchCord:
    """
    Jacks on a cheek with a cable looped between them, bowed toward the
    outer edge so it clears the panel; on a strip too short for two jacks,
    one jack with the cable hanging off it.

    :param colors: (left, right) ColorSpec the cable on each cheek
    :param width: float cable thickness in px
    :param loop_height: float px below which a cheek holds one jack
    """

    colors: Tuple[ColorSpec, ColorSpec]
    width: float = 3.6
    loop_height: float = 28.0

    def __post_init__(self) -> None:
        colors = tuple(parse_color(color) for color in self.colors)
        if len(colors) != 2:
            raise ValueError("A patch cord needs a colour for each cheek")
        object.__setattr__(self, "colors", colors)


@dataclass(frozen=True)
class Grille:
    """
    A speaker grille: a plate punched with staggered round holes.

    :param plate: ColorSpec the plate
    :param holes: ColorSpec what shows through the holes
    :param rim: ColorSpec the plate's outline
    :param inset: (x, y) px from the cheek's sides and ends
    :param pitch: float px between holes
    :param hole_radius: float px
    """

    plate: ColorSpec
    holes: ColorSpec
    rim: ColorSpec
    inset: Tuple[float, float] = (4.0, 6.0)
    pitch: float = 3.2
    hole_radius: float = 1.0

    def __post_init__(self) -> None:
        _set_colors(self, "plate", "holes", "rim")


@dataclass(frozen=True)
class SaggingCable:
    """
    A cable along the rail, plugged in at each end and sagging between.

    :param color: ColorSpec
    :param width: float cable thickness in px
    :param inset: float px from each end of the rail to its jack
    :param jack_size: float size the jacks and plugs are drawn for
    """

    color: ColorSpec
    width: float = 3.0
    inset: float = 10.0
    jack_size: float = 15.0

    def __post_init__(self) -> None:
        _set_colors(self, "color")


Detail = Union[PatchCord, Grille, SaggingCable]


# --- The face and the ears --------------------------------------------------


@dataclass(frozen=True)
class FaceSpec:
    """
    A faceplate: filled, decorated, then outlined.

    :param material: Material to fill with; None keeps the base skin's
        glossy panel (its ``face_stops``, sheen, rim and highlight)
    :param decorations: drawn in order on the face, clipped to its outline
    :param rim: ColorSpec outline, or None for none; ignored with the
        glossy panel
    :param radius: float corner radius in px
    :param overlays: drawn in order after the rim, unclipped
    """

    material: Optional[Material] = None
    decorations: Tuple[Decoration, ...] = ()
    rim: Optional[ColorSpec] = "#000000"
    radius: float = 2.0
    overlays: Tuple[Decoration, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "decorations", tuple(self.decorations))
        object.__setattr__(self, "overlays", tuple(self.overlays))
        _set_colors(self, "rim")


@dataclass(frozen=True)
class EarSpec:
    """
    A rack ear or end cheek, painted at each side of the face.

    :param material: Material to fill with
    :param wash: ColorSpec laid over the material to darken or tint it
    :param seam: ColorSpec line along the edge that meets the face
    :param details: drawn in order after the seam, before the rim: a patch
        cord, a grille
    :param rim: ColorSpec outline round the cheek
    :param screw: ColorSpec screw heads; None for a bare cheek. Screws are
        left off a cheek too short for them to read as screws.
    :param screw_radius: float px
    :param screw_inset: float px from the top and bottom to each screw
    """

    material: Material
    wash: Optional[ColorSpec] = None
    seam: Optional[ColorSpec] = None
    details: Tuple[Detail, ...] = ()
    rim: Optional[ColorSpec] = None
    screw: Optional[ColorSpec] = None
    screw_radius: float = 4.0
    screw_inset: float = 12.0

    def __post_init__(self) -> None:
        object.__setattr__(self, "details", tuple(self.details))
        _set_colors(self, "wash", "seam", "rim", "screw")


@dataclass(frozen=True)
class RailSpec:
    """
    The rail under the face: filled, ruled along its top, then any details.

    :param material: Material
    :param line: ColorSpec along the top edge, or None
    :param details: drawn in order on top: a sagging cable
    """

    material: Material
    line: Optional[ColorSpec] = None
    details: Tuple[Detail, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "details", tuple(self.details))
        _set_colors(self, "line")
