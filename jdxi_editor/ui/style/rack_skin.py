"""
Rack skins
==========

The look of a panel, as an object: the faceplate painted behind the content,
any rack ears beside it, and the palette its display picks up.

A skin owns chrome only, never layout. The room it is allowed to take is the
three numbers it declares -- :attr:`RackSkin.ear_width`, :attr:`RackSkin.bezel`
and :attr:`RackSkin.rail_height` -- which
:meth:`RackSkin.content_margins` turns into the margins
:class:`~jdxi_editor.ui.widgets.rack.panel.RackPanel` sets on its layout.
Everything left over belongs to the content, so a skin cannot quietly grow.

The default skin is the JD-Xi's shiny black panel exactly as it was before
skins existed, so wrapping something in a RackPanel changes nothing until
another skin is chosen.

A skin drives three things:

- the chrome a :class:`RackPanel` paints,
- the panel image behind an editor's outermost groups (``mark_sheen``, which
  reaches them as a stylesheet ``border-image``: see
  :func:`jdxi_editor.ui.style.editor_style.gloss_panel_file`),
- the colours of the LCD widgets, so a brushed aluminium faceplate is not left
  with a Roland-orange display.

Adding one means subclassing :class:`RackSkin`, declaring those three numbers
and overriding a paint hook or two, then adding it to :data:`SKINS`.

The choice is remembered in QSettings under ``ui/skin``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from random import Random
from pathlib import Path
from typing import Dict, Optional

from PySide6.QtCore import QMargins, QPointF, QRectF, Qt
from PySide6.QtGui import (
    QColor,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QPolygonF,
)

#: QSettings key holding the chosen skin's id
SKIN_SETTING = "ui/skin"


@dataclass(frozen=True)
class LcdPalette:
    """
    Colours of a display, so it matches the faceplate around it.

    :param bg_edge: str darkest part of the screen, at its edges
    :param bg_mid: str screen between edge and glow
    :param bg_glow: str backlight in the middle of the screen
    :param text: str the characters
    :param text_dim: str secondary lines
    """

    bg_edge: str
    bg_mid: str
    bg_glow: str
    text: str
    text_dim: str


@dataclass(frozen=True)
class Foreground:
    """
    Lettering printed on the faceplate, and the rules drawn between it.

    The chassis and the controls are different surfaces: the silkscreen on a
    pale faceplate has to be dark, while the buttons and fields sitting in it
    keep their own dark surfaces and light text. Only the chassis is covered
    here, which is why a light skin does not simply invert the whole UI.

    :param text: str labels and group text on the faceplate
    :param text_secondary: str quieter labels on the faceplate
    :param rule: str hairlines drawn on the faceplate
    """

    text: str
    text_secondary: str
    rule: str


#: What the dark skins use: the application's own colours
LIGHT_LETTERING = Foreground(
    text="#E6E6E6", text_secondary="#999999", rule="#3A3A3C"
)

#: Silkscreen on a pale faceplate
DARK_LETTERING = Foreground(
    text="#1E1E1C", text_secondary="#46453F", rule="#7A7A77"
)


#: The JD-Xi's orange-on-dark-red display
ROLAND_LCD = LcdPalette(
    bg_edge="#1A0A0A",
    bg_mid="#331111",
    bg_glow="#551100",
    text="#FF6A00",
    text_dim="#CC5500",
)

#: The blue backlit screen of the rackmount unit
JDXV_BLUE_LCD = LcdPalette(
    bg_edge="#07234F",
    bg_mid="#0E3C86",
    bg_glow="#1557BF",
    text="#CFEEFF",
    text_dim="#7FB4E6",
)

#: Warm amber on near-black, as on painted studio gear
AMBER_LCD = LcdPalette(
    bg_edge="#120E08",
    bg_mid="#241A0C",
    bg_glow="#3A2810",
    text="#FFB545",
    text_dim="#B87A28",
)

#: The red LEDs of a TR-808's step buttons
LED_RED_LCD = LcdPalette(
    bg_edge="#120807",
    bg_mid="#2A100C",
    bg_glow="#431711",
    text="#FF4A33",
    text_dim="#B3301F",
)

#: A green fluorescent display, as 1970s rack gear had
VINTAGE_GREEN_LCD = LcdPalette(
    bg_edge="#07140C",
    bg_mid="#0C2415",
    bg_glow="#12361F",
    text="#5BFF9B",
    text_dim="#2E9960",
)


class RackSkin:
    """
    The JD-Xi's shiny black panel, and the base every other skin extends.

    :cvar ear_width: px of rack ear at each side; 0 for no ears
    :cvar bezel: px between the faceplate's edge and the content
    :cvar rail_height: px of accent stripe below the content; 0 for none
    """

    skin_id = "glossy_black"
    label = "Glossy Black"
    ear_width = 0
    bezel = 7
    rail_height = 0
    lcd = ROLAND_LCD
    foreground = LIGHT_LETTERING

    def content_margins(self) -> QMargins:
        """
        The room this skin's chrome needs.

        :return: QMargins left, top, right, bottom
        """
        return QMargins(
            self.ear_width + self.bezel,
            self.bezel,
            self.ear_width + self.bezel,
            self.bezel + self.rail_height,
        )

    def paint(self, painter: QPainter, rect: QRectF) -> None:
        """
        Paint the whole faceplate: face, then ears, then rail.

        :param painter: QPainter
        :param rect: QRectF the panel's area
        :return: None
        """
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.paint_face(painter, rect)
        if self.ear_width:
            self.paint_ear(
                painter,
                QRectF(rect.left(), rect.top(), self.ear_width, rect.height()),
            )
            self.paint_ear(
                painter,
                QRectF(
                    rect.right() - self.ear_width,
                    rect.top(),
                    self.ear_width,
                    rect.height(),
                ),
            )
        if self.rail_height:
            self.paint_rail(
                painter,
                QRectF(
                    rect.left(),
                    rect.bottom() - self.rail_height,
                    rect.width(),
                    self.rail_height,
                ),
            )

    def paint_face(self, painter: QPainter, rect: QRectF) -> None:
        """
        A shiny black plastic panel: deep gradient, diagonal sheen, soft rim.

        :param painter: QPainter
        :param rect: QRectF the panel's area
        :return: None
        """
        gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        gradient.setColorAt(0, QColor(22, 22, 24))
        gradient.setColorAt(0.5, QColor(10, 10, 11))
        gradient.setColorAt(1, QColor(4, 4, 5))
        path = QPainterPath()
        path.addRoundedRect(rect, 3, 3)
        painter.fillPath(path, gradient)

        # The light falls across the panel from the top right, as on the
        # Instrument window's panel
        painter.save()
        painter.setClipPath(path)
        reflection = QPolygonF(
            [
                rect.topLeft(),
                QPointF(rect.left() + rect.width() * 0.86, rect.top()),
                QPointF(rect.left() + rect.width() * 0.58, rect.bottom()),
                rect.bottomLeft(),
            ]
        )
        shine = QLinearGradient(rect.topLeft(), rect.bottomRight())
        shine.setColorAt(0, QColor(255, 255, 255, 22))
        shine.setColorAt(1, QColor(255, 255, 255, 6))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(shine)
        painter.drawPolygon(reflection)
        painter.restore()

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(0, 0, 0), 1))
        painter.drawPath(path)
        painter.setPen(QPen(QColor(255, 255, 255, 28), 1))
        painter.drawLine(
            QPointF(rect.left() + 3, rect.top() + 1),
            QPointF(rect.right() - 3, rect.top() + 1),
        )

    def paint_ear(self, painter: QPainter, rect: QRectF) -> None:
        """
        Paint one rack ear. The default skin has none.

        :param painter: QPainter
        :param rect: QRectF the ear's area
        :return: None
        """

    def paint_rail(self, painter: QPainter, rect: QRectF) -> None:
        """
        Paint the accent stripe. The default skin has none.

        :param painter: QPainter
        :param rect: QRectF the stripe's area
        :return: None
        """

    @staticmethod
    def paint_screw(
        painter: QPainter, centre: QPointF, radius: float, tint: QColor
    ) -> None:
        """
        A rack screw: a slotted head, for skins whose ears carry them.

        :param painter: QPainter
        :param centre: QPointF middle of the screw
        :param radius: float screw radius in px
        :param tint: QColor the metal's colour
        :return: None
        """
        painter.setPen(QPen(QColor(0, 0, 0, 160), 1))
        painter.setBrush(tint)
        painter.drawEllipse(centre, radius, radius)
        painter.setPen(QPen(QColor(0, 0, 0, 120), 1))
        painter.drawLine(
            QPointF(centre.x() - radius * 0.55, centre.y()),
            QPointF(centre.x() + radius * 0.55, centre.y()),
        )


class JdxiRackSkin(RackSkin):
    """
    The JD-Xi as a 1U rack unit, after the JDXV: brushed gunmetal rather than
    the shiny black plastic, a lit chamfer along the top, a red stripe along
    the bottom, and a blue backlit screen.

    The chamfer and the stripe are painted as part of the face rather than as
    chrome around it. That costs no room -- both sit in the bezel the content
    already leaves free -- and, more importantly, it is what makes the skin
    recognisable: the faceplate reaches an editor's groups as a nine-slice
    image whose top and bottom edges are drawn unstretched, so anything in
    them appears on every panel in the application, while the ears can only
    ever be drawn by a RackPanel.
    """

    skin_id = "jdxi_rack"
    label = "JD-Xi Rackmount"
    ear_width = 16
    bezel = 6
    rail_height = 0
    lcd = JDXV_BLUE_LCD
    #: the illuminated red of the stripe (AppEditorStyle.ACCENT)
    rail_color = "#E04435"
    #: thickness of that stripe, within the nine-slice bottom edge
    #: (editor_style.SHEEN_SLICE_BOTTOM), leaving room for the rim below it
    rail_thickness = 4

    def paint_face(self, painter: QPainter, rect: QRectF) -> None:
        path = QPainterPath()
        path.addRoundedRect(rect, 3, 3)
        painter.save()
        painter.setClipPath(path)

        # Brushed gunmetal, not the glossy black of the default skin
        height = max(1, int(round(rect.height())))
        painter.drawTiledPixmap(rect, _brushed_tile(height, GUNMETAL, grain=10))

        # The chamfer along the top, catching the light
        painter.setPen(Qt.PenStyle.NoPen)
        bevel = QLinearGradient(rect.topLeft(), QPointF(rect.left(), rect.top() + 3))
        bevel.setColorAt(0, QColor(126, 132, 140))
        bevel.setColorAt(1, QColor(74, 78, 85))
        painter.setBrush(bevel)
        painter.drawRect(QRectF(rect.left(), rect.top(), rect.width(), 2))
        painter.setPen(QPen(QColor(0, 0, 0, 90), 1))
        painter.drawLine(
            QPointF(rect.left(), rect.top() + 2.5),
            QPointF(rect.right(), rect.top() + 2.5),
        )

        # The red stripe, just inside the bottom edge
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(self.rail_color))
        painter.drawRect(
            QRectF(
                rect.left(),
                rect.bottom() - self.rail_thickness,
                rect.width(),
                self.rail_thickness,
            )
        )
        painter.restore()

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(12, 13, 15), 1))
        painter.drawPath(path)

    def paint_ear(self, painter: QPainter, rect: QRectF) -> None:
        """A rack ear: the same metal, with its mounting screws and a seam."""
        height = max(1, int(round(rect.height())))
        painter.drawTiledPixmap(rect, _brushed_tile(height, GUNMETAL, grain=7))
        # Darker than the face, and parted from it by a seam
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 0, 0, 60))
        painter.drawRect(rect)
        painter.setPen(QPen(QColor(0, 0, 0, 170), 1))
        inner = rect.right() if rect.left() < 1 else rect.left()
        painter.drawLine(QPointF(inner, rect.top()), QPointF(inner, rect.bottom()))
        if rect.height() < 34:  # too short for screws to read as screws
            return
        x = rect.center().x()
        for y in (rect.top() + 11, rect.bottom() - 11):
            self.paint_screw(painter, QPointF(x, y), 4.0, QColor(118, 124, 132))


#: Satin aluminium: highlight, base and shadow down the face
ALUMINIUM = (
    (0.0, 197, 197, 193),   # #C5C5C1 highlight
    (0.30, 174, 174, 171),
    (0.62, 166, 166, 163),  # #A6A6A3 base
    (1.0, 119, 120, 117),   # #777875 shadow
)

#: The JDXV's dark gunmetal faceplate
GUNMETAL = ((0.0, 62, 66, 72), (0.35, 52, 55, 61), (0.6, 44, 47, 52), (1.0, 32, 34, 38))

#: Strength of the brushing. Real satin metal scatters light far more softly
#: than a drawn line per row: anything much above this reads as corduroy
#: rather than as a machined surface. This is a row-to-row luminance swing
#: about a third of what the first cut of the skin had.
GRAIN_SATIN = 13


@lru_cache(maxsize=8)
def _brushed_tile(height: int, stops: tuple, grain: int = GRAIN_SATIN) -> QPixmap:
    """
    A tile of horizontally brushed metal, drawn once and reused.

    Brushing is drawn line by line, which is too slow to repeat on every
    repaint, so a tile the full height of the panel is cached and tiled
    across it.

    The grain is jittered rather than a strict light/dark alternation: an
    exact two-row repeat reads as scan lines, while varying the strength
    along the surface, with the occasional brighter scratch, reads as
    brushed metal. The jitter is seeded, so the surface is the same every
    run.

    :param height: int tile height in px
    :param stops: tuple of (position, red, green, blue) down the face
    :param grain: int strength of the brushing
    :param width: int tile width in px
    :return: QPixmap tile
    """
    width = 64
    tile = QPixmap(width, height)
    painter = QPainter(tile)
    gradient = QLinearGradient(0, 0, 0, height)
    for position, red, green, blue in stops:
        gradient.setColorAt(position, QColor(red, green, blue))
    painter.fillRect(0, 0, width, height, gradient)

    noise = Random(7)  # the same surface every run
    for y in range(height):
        strength = noise.uniform(0.35, 1.0)
        if noise.random() < 0.06:  # an occasional deeper scratch
            strength = 1.6
        alpha = max(1, round(grain * strength))
        shade = 255 if noise.random() < 0.5 else 0
        painter.setPen(QPen(QColor(shade, shade, shade, alpha), 1))
        painter.drawLine(0, y, width, y)
    painter.end()
    return tile


class Brushed70sSkin(RackSkin):
    """
    Satin-finished aluminium with a green display, as 1970s rack gear had.

    The panel is a shallow bevel: lit along its top edge, shadowed along its
    bottom, with the grain kept faint enough that the metal reads by its
    gradient rather than by its texture.
    """

    skin_id = "brushed_70s"
    label = "Brushed Metal (70s)"
    ear_width = 18
    bezel = 6
    rail_height = 0
    lcd = VINTAGE_GREEN_LCD
    # Near-white lettering on satin aluminium is 1.96:1, well under the 4.5:1
    # that body text needs: this faceplate has to be written on in ink
    foreground = DARK_LETTERING
    #: the chassis, for anything wanting to match it
    base_color = "#A6A6A3"
    highlight_color = "#C5C5C1"
    shadow_color = "#777875"

    def paint_face(self, painter: QPainter, rect: QRectF) -> None:
        path = QPainterPath()
        path.addRoundedRect(rect, 2, 2)
        painter.save()
        painter.setClipPath(path)
        height = max(1, int(round(rect.height())))
        painter.drawTiledPixmap(rect, _brushed_tile(height, ALUMINIUM))

        # A shallow bevel: the light catches the top edge and leaves the
        # bottom in shadow, which is what gives a flat fill its depth
        painter.setPen(QPen(QColor(222, 222, 218), 1))
        painter.drawLine(
            QPointF(rect.left() + 1, rect.top() + 0.5),
            QPointF(rect.right() - 1, rect.top() + 0.5),
        )
        painter.setPen(QPen(QColor(236, 236, 232, 120), 1))
        painter.drawLine(
            QPointF(rect.left() + 1, rect.top() + 1.5),
            QPointF(rect.right() - 1, rect.top() + 1.5),
        )
        painter.setPen(QPen(QColor(94, 95, 92), 1))
        painter.drawLine(
            QPointF(rect.left() + 1, rect.bottom() - 1.5),
            QPointF(rect.right() - 1, rect.bottom() - 1.5),
        )
        painter.setPen(QPen(QColor(70, 71, 69, 140), 1))
        painter.drawLine(
            QPointF(rect.left() + 1, rect.bottom() - 2.5),
            QPointF(rect.right() - 1, rect.bottom() - 2.5),
        )
        painter.restore()

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(88, 89, 86), 1))
        painter.drawPath(path)

    def paint_ear(self, painter: QPainter, rect: QRectF) -> None:
        gradient = QLinearGradient(rect.topLeft(), rect.topRight())
        gradient.setColorAt(0, QColor(138, 138, 134))
        gradient.setColorAt(1, QColor(170, 170, 166))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.fillRect(rect, gradient)
        painter.setPen(QPen(QColor(90, 90, 88), 1))
        painter.drawRect(rect)
        if rect.height() < 34:
            return
        x = rect.center().x()
        for y in (rect.top() + 12, rect.bottom() - 12):
            self.paint_screw(painter, QPointF(x, y), 4.5, QColor(205, 205, 200))


#: Walnut, as used for the end cheeks of studio gear
WALNUT = ((0.0, 122, 78, 44), (0.5, 96, 59, 32), (1.0, 74, 44, 24))

#: The darker wood of a TR-808's side panels
TEAK = ((0.0, 104, 66, 34), (0.5, 82, 51, 26), (1.0, 60, 37, 19))


@lru_cache(maxsize=4)
def _wood_tile(height: int, stops: tuple) -> QPixmap:
    """
    A tile of wood, the grain running along the cheek.

    :param height: int tile height in px
    :param stops: tuple of (position, red, green, blue) through the wood
    :return: QPixmap 64px wide tile
    """
    width = 64
    tile = QPixmap(width, height)
    painter = QPainter(tile)
    gradient = QLinearGradient(0, 0, 0, height)
    for position, red, green, blue in stops:
        gradient.setColorAt(position, QColor(red, green, blue))
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


class IvoryWalnutSkin(RackSkin):
    """
    Ivory painted steel with walnut end cheeks, as on 1970s studio gear.

    The one pale faceplate in the set, which is why :class:`Foreground`
    exists: its lettering is ink rather than near-white, while the controls
    standing on it keep their dark surfaces.
    """

    skin_id = "ivory_walnut"
    label = "Ivory & Walnut"
    ear_width = 18
    bezel = 6
    rail_height = 0
    lcd = AMBER_LCD
    foreground = Foreground(
        text="#22201C", text_secondary="#5F584C", rule="#B9AE99"
    )
    #: the walnut pinstripe along the bottom, this skin's signature
    stripe_color = "#684022"
    stripe_thickness = 2

    def paint_face(self, painter: QPainter, rect: QRectF) -> None:
        path = QPainterPath()
        path.addRoundedRect(rect, 2, 2)
        painter.save()
        painter.setClipPath(path)

        gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        gradient.setColorAt(0.0, QColor(243, 238, 227))
        gradient.setColorAt(0.45, QColor(232, 225, 210))
        gradient.setColorAt(1.0, QColor(208, 199, 181))
        painter.fillRect(rect, gradient)

        painter.setPen(QPen(QColor(255, 253, 248), 1))
        painter.drawLine(
            QPointF(rect.left() + 1, rect.top() + 0.5),
            QPointF(rect.right() - 1, rect.top() + 0.5),
        )
        painter.setPen(QPen(QColor(168, 158, 140), 1))
        painter.drawLine(
            QPointF(rect.left() + 1, rect.bottom() - 3.5),
            QPointF(rect.right() - 1, rect.bottom() - 3.5),
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(self.stripe_color))
        painter.drawRect(
            QRectF(
                rect.left(),
                rect.bottom() - self.stripe_thickness,
                rect.width(),
                self.stripe_thickness,
            )
        )
        painter.restore()

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(150, 140, 122), 1))
        painter.drawPath(path)

    def paint_ear(self, painter: QPainter, rect: QRectF) -> None:
        """A walnut end cheek rather than a rack ear."""
        height = max(1, int(round(rect.height())))
        painter.drawTiledPixmap(rect, _wood_tile(height, WALNUT))
        painter.setPen(QPen(QColor(48, 28, 14), 1))
        painter.drawRect(rect)
        if rect.height() < 34:
            return
        x = rect.center().x()
        for y in (rect.top() + 12, rect.bottom() - 12):
            self.paint_screw(painter, QPointF(x, y), 4.0, QColor(196, 186, 168))


class Tr808Skin(RackSkin):
    """
    The TR-808: matte charcoal, orange silkscreen, teak cheeks, and the
    step-button run of red, orange, yellow and white along the bottom.

    That run of colour is the machine, so it goes in the face rather than in
    chrome around it: the bottom edge of the nine-slice is drawn on every
    panel in the application, where ears and rails never appear.
    """

    skin_id = "tr808"
    label = "TR-808"
    ear_width = 14
    bezel = 6
    rail_height = 0
    lcd = LED_RED_LCD
    foreground = Foreground(
        text="#E8E4DA", text_secondary="#A09A8E", rule="#4A4B4D"
    )
    #: the Roland orange of the lettering and the rule under it
    accent_color = "#E8622A"
    #: the four step-button colours, left to right
    step_colors = ("#E33B2E", "#EE7B2C", "#EFC93F", "#EDE9DC")
    step_band = 4

    def paint_face(self, painter: QPainter, rect: QRectF) -> None:
        path = QPainterPath()
        path.addRoundedRect(rect, 2, 2)
        painter.save()
        painter.setClipPath(path)

        # Matte charcoal, cooler and flatter than the glossy panel
        gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        gradient.setColorAt(0.0, QColor(52, 53, 56))
        gradient.setColorAt(0.5, QColor(42, 43, 45))
        gradient.setColorAt(1.0, QColor(33, 34, 36))
        painter.fillRect(rect, gradient)

        # The orange rule printed under the machine's name
        painter.setPen(QPen(QColor(70, 71, 74), 1))
        painter.drawLine(
            QPointF(rect.left() + 1, rect.top() + 0.5),
            QPointF(rect.right() - 1, rect.top() + 0.5),
        )
        painter.setPen(QPen(QColor(self.accent_color), 1))
        painter.drawLine(
            QPointF(rect.left() + 1, rect.top() + 2.5),
            QPointF(rect.right() - 1, rect.top() + 2.5),
        )

        # The step buttons, in their four colours across the bottom
        painter.setPen(Qt.PenStyle.NoPen)
        width = rect.width() / len(self.step_colors)
        for index, colour in enumerate(self.step_colors):
            painter.setBrush(QColor(colour))
            painter.drawRect(
                QRectF(
                    rect.left() + index * width,
                    rect.bottom() - self.step_band,
                    width,
                    self.step_band,
                )
            )
        painter.restore()

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(16, 17, 18), 1))
        painter.drawPath(path)

    def paint_ear(self, painter: QPainter, rect: QRectF) -> None:
        """A teak side panel, as the 808 has."""
        height = max(1, int(round(rect.height())))
        painter.drawTiledPixmap(rect, _wood_tile(height, TEAK))
        painter.setPen(QPen(QColor(30, 18, 9), 1))
        painter.drawRect(rect)


#: Every skin, by id, in the order they are offered
SKINS: Dict[str, RackSkin] = {
    skin.skin_id: skin
    for skin in (
        RackSkin(),
        JdxiRackSkin(),
        Tr808Skin(),
        Brushed70sSkin(),
        IvoryWalnutSkin(),
    )
}

#: The skin in use; None until first asked for, then read from settings
_active: Optional[RackSkin] = None


def skin_by_id(skin_id: Optional[str]) -> RackSkin:
    """
    The skin ``skin_id`` names, falling back to the default.

    :param skin_id: Optional[str] a key of :data:`SKINS`
    :return: RackSkin
    """
    return SKINS.get(str(skin_id), SKINS["glossy_black"])


def active_skin() -> RackSkin:
    """
    The skin everything is drawn with.

    :return: RackSkin
    """
    global _active
    if _active is None:
        _active = skin_by_id(_stored_skin_id())
    return _active


def set_active_skin(skin: "str | RackSkin", *, remember: bool = True) -> RackSkin:
    """
    Change the skin, and restyle the running application.

    :param skin: str | RackSkin the skin, or its id
    :param remember: bool store the choice for next time
    :return: RackSkin the skin now in use
    """
    global _active
    _active = skin_by_id(skin) if isinstance(skin, str) else skin
    if remember:
        _store_skin_id(_active.skin_id)
    _restyle_application()
    return _active


def _stored_skin_id() -> Optional[str]:
    """
    The skin id saved in settings, if any.

    :return: Optional[str]
    """
    try:
        from PySide6.QtCore import QSettings

        from jdxi_editor.project import __organization_name__, __program__

        value = QSettings(__organization_name__, __program__).value(SKIN_SETTING)
    except Exception:  # settings are a convenience, never a reason to fail
        return None
    return str(value) if value else None


def _store_skin_id(skin_id: str) -> None:
    """
    Remember the chosen skin.

    :param skin_id: str
    :return: None
    """
    try:
        from PySide6.QtCore import QSettings

        from jdxi_editor.project import __organization_name__, __program__

        settings = QSettings(__organization_name__, __program__)
        settings.setValue(SKIN_SETTING, skin_id)
        settings.sync()
    except Exception:
        pass


#: the panel image's filename in a stylesheet, whichever skin rendered it
_PANEL_IMAGE = re.compile(r"gloss_panel_[A-Za-z0-9_]+_(?P<size>\d+x\d+)\.png")


def _restyle_application() -> None:
    """
    Repoint the chrome at the new skin's panel image.

    The panel behind an editor's outermost groups reaches them as a stylesheet
    ``border-image``, whose path names the skin that rendered it. Every editor
    carries its own stylesheet, with its own accent, and is a child of the main
    window rather than a window itself, so the path is swapped in place
    wherever it appears: rebuilding the stylesheets instead would reach none of
    them, and would throw away each editor's accent.

    :return: None
    """
    from PySide6.QtWidgets import QApplication, QWidget

    application = QApplication.instance()
    if application is None:
        return

    from jdxi_editor.ui.style.editor_style import AppEditorStyle, gloss_panel_file

    gloss_panel_file.cache_clear()
    # The stylesheet is not cached today, but may be
    clear = getattr(AppEditorStyle.editor_stylesheet, "cache_clear", None)
    if callable(clear):
        clear()

    from jdxi_editor.ui.style.editor_style import CHASSIS_MARKER, chassis_rules

    chassis = chassis_rules()

    def repoint(sheet: str) -> str:
        """The same stylesheet, with this skin's panel image and lettering."""
        sheet = _PANEL_IMAGE.sub(
            lambda match: Path(gloss_panel_file(*_size(match.group("size")))).name,
            sheet,
        )
        # The chassis block is last, so it can be replaced wholesale; rewriting
        # colours in place would catch the controls' text as well
        marker = sheet.find(CHASSIS_MARKER)
        return sheet if marker < 0 else sheet[:marker] + chassis

    if "gloss_panel_" in (application.styleSheet() or ""):
        application.setStyleSheet(repoint(application.styleSheet()))
    for widget in application.allWidgets():
        sheet = widget.styleSheet()
        if sheet and ("gloss_panel_" in sheet or CHASSIS_MARKER in sheet):
            widget.setStyleSheet(repoint(sheet))
        # QWidget.update explicitly: an item view overrides update() with one
        # that demands a model index, and would raise on a bare call
        QWidget.update(widget)


def _size(size: str) -> tuple:
    """
    The width and height a panel image's name ends with.

    :param size: str e.g. ``"1000x420"``
    :return: tuple[int, int]
    """
    width, _, height = size.partition("x")
    return int(width), int(height)
