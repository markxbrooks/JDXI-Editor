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


@dataclass(frozen=True)
class Chassis:
    """
    The body the panels are mounted on, and the control surfaces on it.

    The faceplate is only part of a skin: behind it is the instrument's body,
    and standing on it are the tabs, lists and fields. Those stay dark even
    on a pale skin -- they are the electronics, not the chassis -- so they
    are given here rather than derived from the faceplate.

    :param body: str the matte body behind the panels
    :param surface: str control surfaces (selected tab, lists, menus)
    :param surface_alt: str quieter control surfaces (unselected tabs)
    :param border: str outlines between them
    :param accent: str the skin's own accent, for the selected tab's underline
    """

    body: str
    surface: str
    surface_alt: str
    border: str
    accent: str


#: The JD-Xi's matte black body and the application's dark controls
DARK_CHASSIS = Chassis(
    body="#2C2C2C",
    surface="#202020",
    surface_alt="#292929",
    border="#383838",
    accent="#E04435",
)


#: What the dark skins use: the application's own colours
LIGHT_LETTERING = Foreground(
    text="#E6E6E6", text_secondary="#999999", rule="#3A3A3C"
)

#: Silkscreen on a pale faceplate. The secondary ink is dark enough to hold
#: up on the body as well as the panel, which is a shade deeper.
DARK_LETTERING = Foreground(
    text="#1E1E1C", text_secondary="#3A3935", rule="#7A7A77"
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

#: The TB-303's red LED numerals, harder and purer than the 808's
LED_303_LCD = LcdPalette(
    bg_edge="#140604",
    bg_mid="#2A0A06",
    bg_glow="#49100A",
    text="#FF1F10",
    text_dim="#A81608",
)

#: The TR-909's red LED display, in its dark neutral bezel
LED_909_LCD = LcdPalette(
    bg_edge="#0E0D0D",
    bg_mid="#241513",
    bg_glow="#3E1A15",
    text="#FF3A20",
    text_dim="#AD2412",
)

#: The Jupiter-8's patch number display
LED_JP8_LCD = LcdPalette(
    bg_edge="#100706",
    bg_mid="#270C08",
    bg_glow="#43130D",
    text="#FF2A14",
    text_dim="#A81B0C",
)

#: A green fluorescent display, as 1970s rack gear had
VINTAGE_GREEN_LCD = LcdPalette(
    bg_edge="#07140C",
    bg_mid="#0C2415",
    bg_glow="#12361F",
    text="#5BFF9B",
    text_dim="#2E9960",
)

#: The Juno-106 has no screen of its own; the editor's display takes the
#: cool grey-blue of the panel rather than another machine's orange or red
JUNO_LCD = LcdPalette(
    bg_edge="#101418",
    bg_mid="#1A222C",
    bg_glow="#243448",
    text="#C5D8EA",
    text_dim="#7A94AE",
)


class RackSkin:
    """
    The JD-Xi's shiny black panel, and the base every other skin extends.

    :cvar ear_width: px of rack ear at each side; 0 for no ears
    :cvar bezel: px between the faceplate's edge and the content
    :cvar rail_height: px of accent stripe below the content; 0 for none
    """

    skin_id = "glossy_black"
    label = "JD-Xi Black"
    ear_width = 0
    bezel = 7
    rail_height = 0
    lcd = ROLAND_LCD
    foreground = LIGHT_LETTERING
    chassis = DARK_CHASSIS
    #: the glossy material, top to bottom: a skin can be the same panel in a
    #: different plastic or metal by declaring these alone
    face_stops = ((0.0, 22, 22, 24), (0.5, 10, 10, 11), (1.0, 4, 4, 5))
    #: the rim drawn round the panel
    face_rim = "#000000"
    #: the highlight along its top edge, as r, g, b, a
    face_highlight = (255, 255, 255, 28)
    #: the diagonal reflection's strength, near and far
    sheen_strength = (22, 6)
    #: Section titles printed in the faceplate's ink, rather than the accent.
    #: The JD-Xi's own panels keep their red rules.
    ink_legends = False
    #: Buttons shaded as caps, and fields as wells milled into the plate.
    mounted_controls = False

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

    def paint_face(
        self, painter: QPainter, rect: QRectF, sheen: bool = True
    ) -> None:
        """
        A shiny black plastic panel: deep gradient, diagonal sheen, soft rim.

        :param painter: QPainter
        :param rect: QRectF the panel's area
        :param sheen: bool draw the diagonal reflection; the instrument's
            right-hand panel is drawn without it, as on the JD-Xi
        :return: None
        """
        gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        for position, red, green, blue in self.face_stops:
            gradient.setColorAt(position, QColor(red, green, blue))
        path = QPainterPath()
        path.addRoundedRect(rect, 3, 3)
        painter.fillPath(path, gradient)

        # The light falls across the panel from the top right, as on the
        # Instrument window's panel
        if sheen:
            self._paint_sheen(painter, rect, path)

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(self.face_rim), 1))
        painter.drawPath(path)
        painter.setPen(QPen(QColor(*self.face_highlight), 1))
        painter.drawLine(
            QPointF(rect.left() + 3, rect.top() + 1),
            QPointF(rect.right() - 3, rect.top() + 1),
        )

    def _paint_sheen(
        self, painter: QPainter, rect: QRectF, path: QPainterPath
    ) -> None:
        """
        The diagonal reflection across the glossy panel.

        :param painter: QPainter
        :param rect: QRectF the panel's area
        :param path: QPainterPath the panel's outline, to clip against
        :return: None
        """
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
        near, far = self.sheen_strength
        shine = QLinearGradient(rect.topLeft(), rect.bottomRight())
        shine.setColorAt(0, QColor(255, 255, 255, near))
        shine.setColorAt(1, QColor(255, 255, 255, far))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(shine)
        painter.drawPolygon(reflection)
        painter.restore()

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

    def outline_ear(
        self,
        painter: QPainter,
        rect: QRectF,
        rim: QColor,
        screw: Optional[QColor] = None,
        radius: float = 4.0,
        inset: float = 12,
    ) -> None:
        """
        Stroke a cheek and, when it is tall enough, its screws.

        The stroke does not fill. Each cheek is painted in turn, and a brush
        still set from the first cheek's screws would fill the second.

        :param painter: QPainter
        :param rect: QRectF the cheek
        :param rim: QColor the outline
        :param screw: Optional[QColor] the screw head; none leaves the cheek bare
        :param radius: float screw radius in px
        :param inset: float how far the screws sit in from the top and bottom
        :return: None
        """
        painter.save()
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(rim, 1))
        painter.drawRect(rect)
        if screw is not None and rect.height() >= 34:
            x = rect.center().x()
            for y in (rect.top() + inset, rect.bottom() - inset):
                self.paint_screw(painter, QPointF(x, y), radius, screw)
        painter.restore()


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
    them appears on every panel in the application. The ears are not part of
    that image -- a nine-slice would stretch them -- so a RackPanel or a
    RackEars strip draws them itself.
    """

    skin_id = "jdxi_rack"
    label = "JD-Xi Rackmount"
    ear_width = 16
    bezel = 6
    rail_height = 0
    lcd = JDXV_BLUE_LCD
    #: the illuminated red of the stripe (AppEditorStyle.ACCENT)
    chassis = Chassis(
        body="#2A2C30", surface="#202225", surface_alt="#292C30",
        border="#3A3D42", accent="#E04435",
    )
    rail_color = "#E04435"
    #: thickness of that stripe, within the nine-slice bottom edge
    #: (editor_style.SHEEN_SLICE_BOTTOM), leaving room for the rim below it
    rail_thickness = 4

    def paint_face(
        self, painter: QPainter, rect: QRectF, sheen: bool = True
    ) -> None:
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


#: Satin aluminium, a neutral grey-silver: highlight, base and shadow down
#: the face. The channels stay within a few points of each other, so the
#: metal reads as silver rather than as bronze.
ALUMINIUM = (
    (0.0, 197, 197, 193),   # #C5C5C1 highlight
    (0.30, 184, 184, 181),
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
def _brushed_tile(
    height: int, stops: tuple, grain: int = GRAIN_SATIN, coverage: float = 1.0
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
    :param stops: tuple of (position, red, green, blue) down the face
    :param grain: int strength of the brushing
    :param coverage: float share of rows that take a stroke, in 0..1
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
        elif coverage < 1.0 and noise.random() > coverage:
            continue
        alpha = max(1, round(grain * strength))
        shade = 255 if noise.random() < 0.5 else 0
        painter.setPen(QPen(QColor(shade, shade, shade, alpha), 1))
        painter.drawLine(0, y, width, y)
    painter.end()
    return tile


class Brushed70sSkin(RackSkin):
    """
    Satin-finished aluminium with a green display, as 1970s rack gear had.

    The panel is a bevel: lit along its top edge, shadowed along its bottom,
    with the grain kept faint enough that the metal reads by its gradient
    rather than by its texture. Legends are ink, and red is reserved for lamps.
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
    ink_legends = True
    mounted_controls = True
    chassis = Chassis(
        body="#8A8A87", surface="#101010", surface_alt="#191919",
        border="#4A4A47", accent="#E04435",
    )
    #: the chassis, for anything wanting to match it
    base_color = "#A6A6A3"
    highlight_color = "#C5C5C1"
    shadow_color = "#777875"

    def paint_face(
        self, painter: QPainter, rect: QRectF, sheen: bool = True
    ) -> None:
        path = QPainterPath()
        path.addRoundedRect(rect, 2, 2)
        painter.save()
        painter.setClipPath(path)
        height = max(1, int(round(rect.height())))
        # Grain about 70% quieter than GRAIN_SATIN, and only on some rows,
        # so the brushing shows up close and the gradient carries the metal.
        painter.drawTiledPixmap(
            rect, _brushed_tile(height, ALUMINIUM, grain=4, coverage=0.35)
        )

        # A lip with some thickness: the light catches the top edge and
        # leaves the bottom in shadow. Two pixels, so it survives inside
        # the unstretched rim of the panel image.
        painter.setPen(QPen(QColor(230, 230, 226), 2))
        painter.drawLine(
            QPointF(rect.left() + 1, rect.top() + 1),
            QPointF(rect.right() - 1, rect.top() + 1),
        )
        painter.setPen(QPen(QColor(242, 242, 238, 150), 2))
        painter.drawLine(
            QPointF(rect.left() + 1, rect.top() + 3.5),
            QPointF(rect.right() - 1, rect.top() + 3.5),
        )
        painter.setPen(QPen(QColor(119, 120, 117), 2))
        painter.drawLine(
            QPointF(rect.left() + 1, rect.bottom() - 2),
            QPointF(rect.right() - 1, rect.bottom() - 2),
        )
        painter.setPen(QPen(QColor(90, 91, 88, 170), 2))
        painter.drawLine(
            QPointF(rect.left() + 1, rect.bottom() - 4.5),
            QPointF(rect.right() - 1, rect.bottom() - 4.5),
        )
        painter.restore()

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(119, 120, 117), 1))
        painter.drawPath(path)

    def paint_ear(self, painter: QPainter, rect: QRectF) -> None:
        gradient = QLinearGradient(rect.topLeft(), rect.topRight())
        gradient.setColorAt(0, QColor(138, 138, 135))
        gradient.setColorAt(1, QColor(166, 166, 163))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.fillRect(rect, gradient)
        self.outline_ear(
            painter, rect, QColor(119, 120, 117), QColor(197, 197, 193), radius=4.5
        )


#: Walnut, as used for the end cheeks of studio gear
WALNUT = ((0.0, 122, 78, 44), (0.5, 96, 59, 32), (1.0, 74, 44, 24))

#: The darker wood of a TR-808's side panels
TEAK = ((0.0, 104, 66, 34), (0.5, 82, 51, 26), (1.0, 60, 37, 19))

#: The Juno-106's end cheeks: a redder, sunlit mahogany than the walnut above
JUNO_WOOD = ((0.0, 176, 102, 52), (0.45, 146, 78, 38), (1.0, 102, 50, 24))


@lru_cache(maxsize=4)
def _pebble_tile(size: int, color: str, grain: int = 10) -> QPixmap:
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
    chassis = Chassis(
        body="#CFC7B6", surface="#241F18", surface_alt="#2F2920",
        border="#5A5043", accent="#684022",
    )
    stripe_color = "#684022"
    stripe_thickness = 2

    def paint_face(
        self, painter: QPainter, rect: QRectF, sheen: bool = True
    ) -> None:
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
        self.outline_ear(
            painter, rect, QColor(48, 28, 14), QColor(196, 186, 168)
        )


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
    chassis = Chassis(
        body="#232426", surface="#1C1D1F", surface_alt="#27282B",
        border="#3A3B3E", accent="#E8622A",
    )
    accent_color = "#E8622A"
    #: the four step-button colours, left to right
    step_colors = ("#E33B2E", "#EE7B2C", "#EFC93F", "#EDE9DC")
    step_band = 4

    def paint_face(
        self, painter: QPainter, rect: QRectF, sheen: bool = True
    ) -> None:
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
        self.outline_ear(painter, rect, QColor(30, 18, 9))


class Tb303Skin(RackSkin):
    """
    The TB-303 Bass Line: the silver box, orange knob line, red LED numerals
    and the little keyboard of step buttons along the bottom.

    Its faceplate is flat painted metal rather than brushed, which is what
    separates it from the satin aluminium skin at a glance; the keyboard
    band separates it from everything else. Both live in the face, so they
    reach every panel rather than only a RackPanel.
    """

    skin_id = "tb303"
    label = "TB-303"
    ear_width = 14
    bezel = 6
    rail_height = 0
    lcd = LED_303_LCD
    foreground = Foreground(
        text="#1E1E1C", text_secondary="#35342F", rule="#6E7472"
    )
    #: the orange of the Bass Line knobs
    chassis = Chassis(
        body="#8A8F8D", surface="#232524", surface_alt="#2E312F",
        border="#4A4E4C", accent="#E87328",
    )
    accent_color = "#E87328"
    #: the step buttons' keyboard: ivory keys, black keys, and their shadow
    key_ivory = "#E6E3D8"
    key_black = "#1A1A1A"
    #: height of that keyboard, within the nine-slice bottom edge
    key_band = 5
    #: keyboards drawn across the source image, before it is stretched
    key_octaves = 4

    def paint_face(
        self, painter: QPainter, rect: QRectF, sheen: bool = True
    ) -> None:
        path = QPainterPath()
        path.addRoundedRect(rect, 2, 2)
        painter.save()
        painter.setClipPath(path)

        # Flat painted metal: a cool grey, no grain
        gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        gradient.setColorAt(0.0, QColor(168, 173, 171))
        gradient.setColorAt(0.45, QColor(142, 148, 146))
        gradient.setColorAt(1.0, QColor(110, 116, 114))
        painter.fillRect(rect, gradient)

        painter.setPen(QPen(QColor(206, 210, 208), 1))
        painter.drawLine(
            QPointF(rect.left() + 1, rect.top() + 0.5),
            QPointF(rect.right() - 1, rect.top() + 0.5),
        )
        # The orange line the knobs stand on
        painter.setPen(QPen(QColor(self.accent_color), 1))
        painter.drawLine(
            QPointF(rect.left() + 1, rect.top() + 2.5),
            QPointF(rect.right() - 1, rect.top() + 2.5),
        )

        self.paint_keyboard(
            painter,
            QRectF(
                rect.left(),
                rect.bottom() - self.key_band,
                rect.width(),
                self.key_band,
            ),
        )
        painter.restore()

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(74, 78, 77), 1))
        painter.drawPath(path)

    def paint_keyboard(self, painter: QPainter, rect: QRectF) -> None:
        """
        The step buttons, laid out as the keyboard they are on the machine.

        :param painter: QPainter
        :param rect: QRectF the band along the bottom of the face
        :return: None
        """
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(self.key_ivory))
        painter.drawRect(rect)

        whites = 7 * self.key_octaves
        key = rect.width() / whites
        painter.setPen(QPen(QColor(120, 118, 110), 1))
        for index in range(1, whites):
            x = rect.left() + index * key
            painter.drawLine(QPointF(x, rect.top()), QPointF(x, rect.bottom()))

        # Black keys sit over the gaps after C, D, F, G and A
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(self.key_black))
        for octave in range(self.key_octaves):
            for white in (0, 1, 3, 4, 5):
                centre = rect.left() + (octave * 7 + white + 1) * key
                painter.drawRect(
                    QRectF(
                        centre - key * 0.3,
                        rect.top(),
                        key * 0.6,
                        rect.height() * 0.62,
                    )
                )

    def paint_ear(self, painter: QPainter, rect: QRectF) -> None:
        """A painted metal cheek, matching the box."""
        gradient = QLinearGradient(rect.topLeft(), rect.topRight())
        gradient.setColorAt(0, QColor(126, 132, 130))
        gradient.setColorAt(1, QColor(152, 158, 156))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.fillRect(rect, gradient)
        self.outline_ear(
            painter, rect, QColor(72, 76, 75), QColor(182, 188, 186), inset=11
        )


class Tr909Skin(RackSkin):
    """
    The TR-909: a light grey box with blue silkscreen, dark end cheeks, and
    the sixteen cream step buttons with a red LED over each one.

    That row of buttons and lights is the machine's face, so it goes in the
    faceplate's bottom edge and appears on every panel. The steps are drawn
    in fours, as they are grouped on the hardware.
    """

    skin_id = "tr909"
    label = "TR-909"
    ear_width = 14
    bezel = 6
    rail_height = 0
    lcd = LED_909_LCD
    foreground = Foreground(
        text="#1E1E1C", text_secondary="#35342F", rule="#9A9A95"
    )
    #: the blue of the 909's silkscreen groupings
    chassis = Chassis(
        body="#9A9A95", surface="#232423", surface_alt="#2E2F2E",
        border="#4C4D4B", accent="#2C6AB0",
    )
    accent_color = "#2C6AB0"
    #: the step buttons, their lights, and the strip they sit in
    button_color = "#E8E6DC"
    led_color = "#FF3A20"
    led_off_color = "#3A1410"
    strip_color = "#4A4A47"
    #: height of the button row and of the lights above it
    button_band = 4
    led_band = 2
    #: sixteen steps, in four groups of four
    steps = 16
    steps_per_group = 4

    def paint_face(
        self, painter: QPainter, rect: QRectF, sheen: bool = True
    ) -> None:
        path = QPainterPath()
        path.addRoundedRect(rect, 2, 2)
        painter.save()
        painter.setClipPath(path)

        # Light grey painted steel, flat
        gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        gradient.setColorAt(0.0, QColor(214, 214, 209))
        gradient.setColorAt(0.45, QColor(198, 198, 193))
        gradient.setColorAt(1.0, QColor(168, 168, 163))
        painter.fillRect(rect, gradient)

        painter.setPen(QPen(QColor(238, 238, 234), 1))
        painter.drawLine(
            QPointF(rect.left() + 1, rect.top() + 0.5),
            QPointF(rect.right() - 1, rect.top() + 0.5),
        )
        # The blue rule the groups are printed against
        painter.setPen(QPen(QColor(self.accent_color), 1))
        painter.drawLine(
            QPointF(rect.left() + 1, rect.top() + 2.5),
            QPointF(rect.right() - 1, rect.top() + 2.5),
        )

        self.paint_steps(
            painter,
            QRectF(
                rect.left(),
                rect.bottom() - (self.button_band + self.led_band),
                rect.width(),
                self.button_band + self.led_band,
            ),
        )
        painter.restore()

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(104, 104, 100), 1))
        painter.drawPath(path)

    def paint_steps(self, painter: QPainter, rect: QRectF) -> None:
        """
        The step buttons, each under its own light.

        :param painter: QPainter
        :param rect: QRectF the band along the bottom of the face
        :return: None
        """
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(self.strip_color))
        painter.drawRect(rect)

        step = rect.width() / self.steps
        lights = rect.top()
        buttons = rect.top() + self.led_band
        for index in range(self.steps):
            left = rect.left() + index * step
            # A wider gap every four steps, as the hardware groups them
            gap = 1.6 if index % self.steps_per_group == 0 else 0.8
            body = QRectF(left + gap, buttons, step - gap * 2, self.button_band)
            painter.setBrush(QColor(self.button_color))
            painter.drawRect(body)
            # The light sits over the button, lit on the downbeat of each group
            lit = index % self.steps_per_group == 0
            painter.setBrush(
                QColor(self.led_color if lit else self.led_off_color)
            )
            painter.drawRect(
                QRectF(
                    left + step * 0.3, lights, max(1.0, step * 0.4), self.led_band
                )
            )

    def paint_ear(self, painter: QPainter, rect: QRectF) -> None:
        """A dark moulded cheek, as the 909 has at each end."""
        gradient = QLinearGradient(rect.topLeft(), rect.topRight())
        gradient.setColorAt(0, QColor(62, 62, 60))
        gradient.setColorAt(1, QColor(44, 44, 42))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.fillRect(rect, gradient)
        self.outline_ear(
            painter, rect, QColor(22, 22, 21), QColor(128, 128, 124), inset=11
        )


class Jupiter8Skin(RackSkin):
    """
    The Jupiter-8: a textured near-black panel under bold red section bars,
    with the run of coloured patch buttons along the bottom.

    The red header bar is what the eye remembers of a JP-8, so it takes the
    whole of the faceplate's top edge rather than the hairline the other
    skins draw there, and the patch buttons are discrete keys with gaps
    rather than a continuous stripe.
    """

    skin_id = "jupiter8"
    label = "Jupiter-8"
    ear_width = 14
    bezel = 6
    rail_height = 0
    lcd = LED_JP8_LCD
    foreground = LIGHT_LETTERING
    chassis = Chassis(
        body="#1F1F1F", surface="#1A1A1A", surface_alt="#252525",
        border="#3A3A3A", accent="#E03A20",
    )
    #: the red of the section headers
    header_color = "#E03A20"
    #: how much of the top edge that bar takes (editor_style.SHEEN_SLICE_TOP)
    header_band = 3
    #: the patch buttons, in the order they run across the panel
    button_colors = (
        "#D8392A",  # red
        "#E8762A",  # orange
        "#E8C02A",  # yellow
        "#E4E0D6",  # white
        "#3FA85A",  # green
        "#2F7FD0",  # blue
    )
    button_band = 4
    buttons = 18

    def paint_face(
        self, painter: QPainter, rect: QRectF, sheen: bool = True
    ) -> None:
        path = QPainterPath()
        path.addRoundedRect(rect, 2, 2)
        painter.save()
        painter.setClipPath(path)

        # Textured matte paint, not the gloss of the default skin
        painter.drawTiledPixmap(rect, _pebble_tile(64, "#282828"))
        shade = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        shade.setColorAt(0.0, QColor(255, 255, 255, 10))
        shade.setColorAt(1.0, QColor(0, 0, 0, 40))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(shade)
        painter.drawRect(rect)

        # The section header bar across the top
        painter.setBrush(QColor(self.header_color))
        painter.drawRect(
            QRectF(rect.left(), rect.top(), rect.width(), self.header_band)
        )
        painter.setPen(QPen(QColor(12, 12, 12), 1))
        painter.drawLine(
            QPointF(rect.left(), rect.top() + self.header_band + 0.5),
            QPointF(rect.right(), rect.top() + self.header_band + 0.5),
        )

        self.paint_buttons(
            painter,
            QRectF(
                rect.left(),
                rect.bottom() - self.button_band,
                rect.width(),
                self.button_band,
            ),
        )
        painter.restore()

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(10, 10, 10), 1))
        painter.drawPath(path)

    def paint_buttons(self, painter: QPainter, rect: QRectF) -> None:
        """
        The patch buttons: separate keys with the panel showing between them.

        :param painter: QPainter
        :param rect: QRectF the band along the bottom of the face
        :return: None
        """
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(26, 26, 26))
        painter.drawRect(rect)
        step = rect.width() / self.buttons
        for index in range(self.buttons):
            painter.setBrush(
                QColor(self.button_colors[index % len(self.button_colors)])
            )
            painter.drawRect(
                QRectF(
                    rect.left() + index * step + step * 0.16,
                    rect.top() + 1,
                    step * 0.68,
                    rect.height() - 1,
                )
            )

    def paint_ear(self, painter: QPainter, rect: QRectF) -> None:
        """A silver end cheek, the same metal on both sides."""
        gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        gradient.setColorAt(0.0, QColor(208, 208, 204))
        gradient.setColorAt(0.5, QColor(188, 188, 184))
        gradient.setColorAt(1.0, QColor(168, 168, 164))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(gradient)
        painter.drawRect(rect)
        self.outline_ear(
            painter, rect, QColor(96, 96, 92), QColor(120, 120, 116), inset=11
        )


class RedJdxiSkin(RackSkin):
    """
    The red JD-Xi: the same glossy black control panel, set into a scarlet
    body instead of the matte black one.

    What changes is almost all chassis rather than faceplate -- the body
    around the panels, the keyboard strip, the lettering on them -- so the
    panel keeps the thin red edge the hardware shows where the inset meets
    the body, which is also what tells this skin's faceplate apart from the
    plain glossy one.
    """

    skin_id = "jdxi_red"
    label = "JD-Xi Red"
    ear_width = 14
    bezel = 6
    rail_height = 0
    lcd = ROLAND_LCD
    foreground = Foreground(
        text="#FFFFFF", text_secondary="#F3D3D1", rule="#8A2A26"
    )
    chassis = Chassis(
        body="#D81F1C", surface="#1A1A1A", surface_alt="#262626",
        border="#8A2A26", accent="#FF5247",
    )
    #: the body showing around the inset panel
    rim_color = "#D81F1C"
    rim_width = 2

    def paint_face(
        self, painter: QPainter, rect: QRectF, sheen: bool = True
    ) -> None:
        super().paint_face(painter, rect, sheen=sheen)
        pen = QPen(QColor(self.rim_color), self.rim_width)
        pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(pen)
        inset = self.rim_width / 2
        painter.drawRoundedRect(rect.adjusted(inset, inset, -inset, -inset), 2, 2)

    def paint_ear(self, painter: QPainter, rect: QRectF) -> None:
        """A cheek of the red body."""
        gradient = QLinearGradient(rect.topLeft(), rect.topRight())
        gradient.setColorAt(0, QColor(196, 28, 25))
        gradient.setColorAt(1, QColor(168, 24, 21))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.fillRect(rect, gradient)
        self.outline_ear(
            painter, rect, QColor(96, 14, 12), QColor(214, 214, 210), inset=11
        )


class WhiteJdxiSkin(RackSkin):
    """
    The white JD-Xi: a silver control panel set into a white body.

    The panel is the same glossy construction as the default skin -- the
    gradient, the diagonal reflection, the rim and the top highlight -- in
    light metal instead of black plastic, so it is declared as colours
    rather than painted again. The sheen is stronger than the black panel's,
    because a bright surface returns more of the light that falls on it.
    """

    skin_id = "jdxi_white"
    label = "JD-Xi White"
    ear_width = 14
    bezel = 6
    rail_height = 0
    lcd = ROLAND_LCD
    foreground = DARK_LETTERING
    chassis = Chassis(
        body="#EFEFEC", surface="#1E1E1E", surface_alt="#2A2A2A",
        border="#B8B8B2", accent="#E04435",
    )
    face_stops = ((0.0, 226, 231, 235), (0.5, 208, 213, 217), (1.0, 184, 190, 195))
    face_rim = "#8E979B"
    face_highlight = (255, 255, 255, 200)
    sheen_strength = (60, 12)

    def paint_ear(self, painter: QPainter, rect: QRectF) -> None:
        """A cheek of the white body."""
        gradient = QLinearGradient(rect.topLeft(), rect.topRight())
        gradient.setColorAt(0, QColor(228, 228, 224))
        gradient.setColorAt(1, QColor(246, 246, 243))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.fillRect(rect, gradient)
        self.outline_ear(
            painter, rect, QColor(174, 174, 168), QColor(150, 152, 150), inset=11
        )


class Juno106Skin(RackSkin):
    """
    The Juno-106: a matte slate panel, a red bar and a blue bar along the
    top, and wooden end cheeks.

    The bars are the coloured section rules across the machine, so they take
    the faceplate's top edge, which the nine-slice keeps at its own size.
    The cheeks are the wood at each end, drawn as the ears.
    """

    skin_id = "juno106"
    label = "Juno-106"
    ear_width = 18
    bezel = 6
    rail_height = 0
    lcd = JUNO_LCD
    foreground = LIGHT_LETTERING
    chassis = Chassis(
        body="#2E3236", surface="#141618", surface_alt="#1E2226",
        border="#4A4E52", accent="#D4202A",
    )
    #: the red and blue section rules, top to bottom
    red_bar = "#D4202A"
    blue_bar = "#2F6FBE"
    #: each bar's thickness, together inside editor_style.SHEEN_SLICE_TOP
    bar = 2

    def paint_face(
        self, painter: QPainter, rect: QRectF, sheen: bool = True
    ) -> None:
        path = QPainterPath()
        path.addRoundedRect(rect, 2, 2)
        painter.save()
        painter.setClipPath(path)

        gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        gradient.setColorAt(0.0, QColor(62, 66, 70))
        gradient.setColorAt(0.55, QColor(54, 58, 62))
        gradient.setColorAt(1.0, QColor(44, 48, 52))
        painter.fillRect(rect, gradient)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(self.red_bar))
        painter.drawRect(QRectF(rect.left(), rect.top(), rect.width(), self.bar))
        painter.setBrush(QColor(self.blue_bar))
        painter.drawRect(
            QRectF(rect.left(), rect.top() + self.bar, rect.width(), self.bar)
        )
        painter.restore()

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(18, 20, 22), 1))
        painter.drawPath(path)

    def paint_ear(self, painter: QPainter, rect: QRectF) -> None:
        """A mahogany end cheek, with the dark screws the Juno uses."""
        height = max(1, int(round(rect.height())))
        painter.drawTiledPixmap(rect, _wood_tile(height, JUNO_WOOD))
        self.outline_ear(painter, rect, QColor(62, 32, 16), QColor(36, 32, 28))


#: Every skin, by id, in the order they are offered
SKINS: Dict[str, RackSkin] = {
    skin.skin_id: skin
    for skin in (
        RackSkin(),
        RedJdxiSkin(),
        WhiteJdxiSkin(),
        JdxiRackSkin(),
        Tr808Skin(),
        Tb303Skin(),
        Tr909Skin(),
        Jupiter8Skin(),
        Juno106Skin(),
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
    from jdxi_editor.ui.style.jdxi import JDXiUIStyle

    chassis = chassis_rules()
    mounted = active_skin().mounted_controls
    cap = JDXiUIStyle.BUTTON_ROUND_CAP
    flat = JDXiUIStyle.BUTTON_ROUND
    desired_cap = cap if mounted else flat
    previous_cap = flat if mounted else cap

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
    from jdxi_editor.ui.widgets.rack.ears import RackEars
    from jdxi_editor.ui.widgets.rack.panel import RackPanel

    for widget in application.allWidgets():
        if isinstance(widget, RackEars):
            widget.apply_skin()
        elif isinstance(widget, RackPanel) and widget._pinned_skin is None:
            widget.refresh_skin()
        sheet = widget.styleSheet()
        if sheet == previous_cap:
            widget.setStyleSheet(desired_cap)
        elif sheet and ("gloss_panel_" in sheet or CHASSIS_MARKER in sheet):
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
