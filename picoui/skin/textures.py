"""
picoui.skin.textures
Materials a skin can paint with: brushed metal, wood grain and a moulded
speckle. Each is drawn once into a tile (cached) and tiled across the area,
and every tile is seeded, so a surface looks the same on every run.
"""

from __future__ import annotations

from functools import lru_cache
from random import Random

from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPen, QPixmap

from picoui.skin.gradient import GradientColorStops, GradientStop
from picoui.skin.qt import apply_gradient_stops


#: Satin aluminium, a neutral grey-silver: highlight, base and shadow down
#: the face. The channels stay within a few points of each other, so the
#: metal reads as silver rather than as bronze.
ALUMINIUM = GradientColorStops(
    (
        GradientStop(0.0, (197, 197, 193)),  # #C5C5C1 highlight
        GradientStop(0.30, (184, 184, 181)),
        GradientStop(0.62, (166, 166, 163)),  # #A6A6A3 base
        GradientStop(1.0, (119, 120, 117)),  # #777875 shadow
    )
)

#: The JDXV's dark gunmetal faceplate
GUNMETAL = GradientColorStops(
    (
        GradientStop(0.0, (62, 66, 72)),
        GradientStop(0.35, (52, 55, 61)),
        GradientStop(0.6, (44, 47, 52)),
        GradientStop(1.0, (32, 34, 38)),
    )
)

#: Strength of the brushing. Real satin metal scatters light far more softly
#: than a drawn line per row: anything much above this reads as corduroy
#: rather than as a machined surface. This is a row-to-row luminance swing
#: about a third of what the first cut of the skin had.
GRAIN_SATIN = 13


@lru_cache(maxsize=8)
def brushed_tile(
    height: int,
    stops: GradientColorStops,
    grain: int = GRAIN_SATIN,
    coverage: float = 1.0,
) -> QPixmap:
    """
    A tile of horizontally brushed metal, drawn once and reused.

    Brushing is drawn line by line, which is too slow to repeat on every
    repaint, so a tile the full height of the panel is cached and tiled
    across it.

    The grain is jittered rather than a strict light/dark alternation: an
    exact two-row repeat reads as scan lines, while varying the strength
    along the surface, with the occasional brighter scratch, reads as
    brushed metal. The jitter is seeded, so the surface is the same every
    run. ``coverage`` of 1 draws every row; a lower value leaves most rows
    as bare metal, so the grain only shows up close. Callers that pass 1
    keep the previous stroke pattern.

    :param height: int tile height in px
    :param stops: GradientColorStops the metal's shading down the face
    :param grain: int strength of the brushing
    :param coverage: float share of rows that take a stroke, in 0..1
    :return: QPixmap tile
    """
    width = 64
    tile = QPixmap(width, height)
    painter = QPainter(tile)
    gradient = QLinearGradient(0, 0, 0, height)
    apply_gradient_stops(gradient, stops)
    painter.fillRect(0, 0, width, height, gradient)

    noise = Random(7)  # the same surface every run
    for y in range(height):
        strength = noise.uniform(0.35, 1.0)
        if noise.random() < 0.06:  # an occasional deeper scratch
            strength = 1.6
        elif coverage < 1.0 and noise.random() > coverage:
            continue
        alpha = max(1, round(grain * strength))
        shade = 255 if noise.random() < 0.5 else 0
        painter.setPen(QPen(QColor(shade, shade, shade, alpha), 1))
        painter.drawLine(0, y, width, y)
    painter.end()
    return tile


#: Walnut, as used for the end cheeks of studio gear
WALNUT = GradientColorStops(
    (
        GradientStop(0.0, (122, 78, 44)),
        GradientStop(0.5, (96, 59, 32)),
        GradientStop(1.0, (74, 44, 24)),
    )
)

#: The darker wood of a TR-808's side panels
TEAK = GradientColorStops(
    (
        GradientStop(0.0, (104, 66, 34)),
        GradientStop(0.5, (82, 51, 26)),
        GradientStop(1.0, (60, 37, 19)),
    )
)


@lru_cache(maxsize=4)
def pebble_tile(size: int, color: str, grain: int = 10) -> QPixmap:
    """
    A tile of textured matte paint, as on a Jupiter-8's panel.

    Unlike the brushed tile the speckle runs in no direction, which is what
    separates a moulded painted surface from a machined one.

    :param size: int tile edge in px
    :param color: str the paint's colour
    :param grain: int strength of the speckle
    :return: QPixmap square tile, which repeats in both directions
    """
    tile = QPixmap(size, size)
    painter = QPainter(tile)
    painter.fillRect(0, 0, size, size, QColor(color))
    noise = Random(23)  # the same moulding every run
    for y in range(size):
        for x in range(size):
            if noise.random() < 0.55:
                continue
            shade = 255 if noise.random() < 0.45 else 0
            painter.setPen(
                QPen(QColor(shade, shade, shade, noise.randint(1, grain)), 1)
            )
            painter.drawPoint(x, y)
    painter.end()
    return tile


@lru_cache(maxsize=4)
def wood_tile(height: int, stops: GradientColorStops) -> QPixmap:
    """
    A tile of wood, the grain running along the cheek.

    :param height: int tile height in px
    :param stops: GradientColorStops the colour through the wood
    :return: QPixmap 64px wide tile
    """
    width = 64
    tile = QPixmap(width, height)
    painter = QPainter(tile)
    gradient = QLinearGradient(0, 0, 0, height)
    apply_gradient_stops(gradient, stops)
    painter.fillRect(0, 0, width, height, gradient)
    noise = Random(11)  # the same plank every run
    for y in range(height):
        if noise.random() < 0.45:  # grain is sparse, not every row
            continue
        if noise.random() < 0.6:
            shade = QColor(40, 22, 10, noise.randint(18, 48))
        else:
            shade = QColor(190, 140, 90, 22)
        painter.setPen(QPen(shade, 1))
        painter.drawLine(0, y, width, y)
    painter.end()
    return tile
