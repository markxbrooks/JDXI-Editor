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

The reusable part -- the :class:`~picoui.skin.Skin` base, its palettes and
textures, the :class:`~picoui.skin.SkinRegistry` and the RackPanel / RackEars
widgets -- lives in :mod:`picoui.skin`. This module holds the editor's own
skins, its :data:`REGISTRY` of them, and the restyling the editor needs when
the skin changes (the registry's listener).

Adding one means subclassing :class:`RackSkin`, declaring those three numbers
and overriding a paint hook or two, then adding it to :data:`REGISTRY`.

The choice is remembered in QSettings under ``ui/skin``.
"""

from __future__ import annotations

import re
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

from picoui.skin import (  # noqa: F401  re-exported: the editor imports them from here
    DARK_CHASSIS,
    DARK_LETTERING,
    LIGHT_LETTERING,
    Chassis,
    Foreground,
    LcdPalette,
    QSettingsStore,
    Skin,
    SkinRegistry,
    set_default_registry,
)
from picoui.skin.textures import (  # noqa: F401
    ALUMINIUM,
    GRAIN_SATIN,
    GUNMETAL,
    TEAK,
    WALNUT,
    brushed_tile as _brushed_tile,
    pebble_tile as _pebble_tile,
    wood_tile as _wood_tile,
)

#: QSettings key holding the chosen skin's id
SKIN_SETTING = "ui/skin"


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


class RackSkin(Skin):
    """
    The JD-Xi's shiny black panel, and the base every editor skin extends.

    The painting, margins and palette machinery are picoui's
    :class:`~picoui.skin.Skin`; what is added here is the JD-Xi's own display
    and the editor's features a skin can switch on (punched-card MIDI lanes,
    needle or vintage meters on the Audio Monitor).
    """

    skin_id = "glossy_black"
    label = "JD-Xi Black"
    lcd = ROLAND_LCD
    #: MIDI lanes drawn as punched cards on wood.
    punched_cards = False
    #: Wood behind those lanes. None uses the studio walnut. A skin that is
    #: not a wooden cabinet overrides :meth:`lane_backing` instead.
    lane_wood = None
    #: Circular needles on the Audio Monitor. The default meter is the bars.
    needle_meters = False
    #: Backlit analogue VU meters on the Audio Monitor, cream faces with a
    #: needle and a red zone, as studio gear of the Minimoog's era had.
    vintage_vu = False

    def lane_backing(self, height: int) -> QPixmap:
        """
        The surface the punched-card lanes of the MIDI player lie on: this
        skin's wood, or the studio walnut.

        :param height: int tile height in px
        :return: QPixmap tile
        """
        return _wood_tile(max(1, int(height)), self.lane_wood or WALNUT)

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
    punched_cards = True
    #: Backlit analogue VU meters on the Audio Monitor, as 1970s studio
    #: gear had
    vintage_vu = True
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

    def lane_backing(self, height: int) -> QPixmap:
        """The cards lie on the same satin aluminium as the faceplate, not wood."""
        return _brushed_tile(max(1, int(height)), ALUMINIUM, grain=4, coverage=0.35)

    def paint_ear(self, painter: QPainter, rect: QRectF) -> None:
        gradient = QLinearGradient(rect.topLeft(), rect.topRight())
        gradient.setColorAt(0, QColor(138, 138, 135))
        gradient.setColorAt(1, QColor(166, 166, 163))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.fillRect(rect, gradient)
        self.outline_ear(
            painter, rect, QColor(119, 120, 117), QColor(197, 197, 193), radius=4.5
        )


#: The Juno-106's end cheeks: a redder, sunlit mahogany than the walnut above
JUNO_WOOD = ((0.0, 176, 102, 52), (0.45, 146, 78, 38), (1.0, 102, 50, 24))


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


#: The Minimoog's cabinet, taken from the lit rail: a honey walnut
MINI_WOOD = ((0.0, 206, 156, 112), (0.45, 186, 128, 86), (1.0, 140, 88, 52))

#: The Minimoog has no screen. The editor's display takes the cream of the
#: legends printed on its black panel.
MINI_LCD = LcdPalette(
    bg_edge="#12100E",
    bg_mid="#1E1A16",
    bg_glow="#2C261E",
    text="#F4E6C8",
    text_dim="#A89878",
)


class MiniMoogSkin(RackSkin):
    """
    The Minimoog: a matte black panel set in a walnut cabinet.

    The cabinet is the wood at each end and the lip above and below the
    panel. Its lanes are punched cards, on this cabinet's own wood.
    """

    skin_id = "minimoog"
    label = "Mini Moog"
    ear_width = 18
    bezel = 6
    #: The wooden rail under the panel
    rail_height = 8
    lcd = MINI_LCD
    foreground = LIGHT_LETTERING
    punched_cards = True
    lane_wood = MINI_WOOD
    vintage_vu = True
    chassis = Chassis(
        body="#241C16", surface="#141210", surface_alt="#1C1916",
        border="#3A322C", accent="#E06A32",
    )
    #: How much of the top slice is the cabinet lip, inside SHEEN_SLICE_TOP
    lip = 4

    def paint_face(
        self, painter: QPainter, rect: QRectF, sheen: bool = True
    ) -> None:
        path = QPainterPath()
        path.addRoundedRect(rect, 2, 2)
        painter.save()
        painter.setClipPath(path)

        gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        gradient.setColorAt(0.0, QColor(36, 34, 32))
        gradient.setColorAt(0.55, QColor(22, 20, 18))
        gradient.setColorAt(1.0, QColor(12, 10, 9))
        painter.fillRect(rect, gradient)

        height = max(1, int(round(rect.height())))
        painter.drawTiledPixmap(
            QRectF(rect.left(), rect.top(), rect.width(), self.lip),
            _wood_tile(height, MINI_WOOD),
        )
        painter.setPen(QPen(QColor(48, 28, 16), 1))
        painter.drawLine(
            QPointF(rect.left(), rect.top() + self.lip),
            QPointF(rect.right(), rect.top() + self.lip),
        )
        painter.restore()

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(8, 7, 6), 1))
        painter.drawPath(path)

    def paint_ear(self, painter: QPainter, rect: QRectF) -> None:
        """A cabinet cheek. The sides are plain wood, with no rack screws."""
        height = max(1, int(round(rect.height())))
        painter.drawTiledPixmap(rect, _wood_tile(height, MINI_WOOD))
        self.outline_ear(painter, rect, QColor(110, 64, 32))

    def paint_rail(self, painter: QPainter, rect: QRectF) -> None:
        """The wooden rail under the panel, the same plank as the cheeks."""
        span = max(1, int(round(rect.bottom())))
        painter.drawTiledPixmap(rect, _wood_tile(span, MINI_WOOD))
        painter.setPen(QPen(QColor(48, 28, 16), 1))
        painter.drawLine(rect.topLeft(), rect.topRight())


#: The MC-101's small monochrome OLED: white pixels on true black
OLED_LCD = LcdPalette(
    bg_edge="#000000",
    bg_mid="#040506",
    bg_glow="#0B0D10",
    text="#F2F5F7",
    text_dim="#8C949B",
)


class Mc101Skin(RackSkin):
    """
    The MC-101 groovebox: a compact matte black body, a white OLED, and the
    sixteen backlit step pads along its front edge.

    The pads are what the machine is recognised by, so, like the TR-909's
    buttons, they go in the faceplate's bottom edge and appear on every
    panel. Each group of four is lit in its own colour, as the pads take the
    colour of the track being edited, with the first step of each group
    brightest. The sides are the moulded body itself: no wood, no screws.
    """

    skin_id = "mc101"
    label = "MC-101"
    ear_width = 8
    bezel = 6
    rail_height = 0
    lcd = OLED_LCD
    foreground = LIGHT_LETTERING
    chassis = Chassis(
        body="#18191B", surface="#0E0F10", surface_alt="#1B1C1F",
        border="#36383C", accent="#18C8E8",
    )
    #: the pads' lit colours, one per group of four steps
    pad_colors = ("#18C8E8", "#F23C8C", "#FFB000", "#5ADC3C")
    #: an unlit pad, and the slot the pads sit in
    pad_off_color = "#2A2C30"
    slot_color = "#060607"
    #: the pad row's height, inside editor_style.SHEEN_SLICE_BOTTOM
    pad_band = 5
    steps = 16
    steps_per_group = 4

    def paint_face(
        self, painter: QPainter, rect: QRectF, sheen: bool = True
    ) -> None:
        path = QPainterPath()
        path.addRoundedRect(rect, 3, 3)
        painter.save()
        painter.setClipPath(path)

        # Matte black moulding: a soft fall-off, no reflection
        gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        gradient.setColorAt(0.0, QColor(40, 41, 44))
        gradient.setColorAt(0.5, QColor(30, 31, 34))
        gradient.setColorAt(1.0, QColor(22, 23, 25))
        painter.fillRect(rect, gradient)
        # The bevel where the top surface turns down
        painter.setPen(QPen(QColor(78, 80, 85), 1))
        painter.drawLine(
            QPointF(rect.left() + 2, rect.top() + 0.5),
            QPointF(rect.right() - 2, rect.top() + 0.5),
        )

        self.paint_pads(
            painter,
            QRectF(
                rect.left(),
                rect.bottom() - (self.pad_band + 1),
                rect.width(),
                self.pad_band + 1,
            ),
        )
        painter.restore()

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(6, 6, 7), 1))
        painter.drawPath(path)

    def pad_color(self, index: int) -> str:
        """The colour step `index` is lit in: its group's, dimmer off the beat."""
        colour = QColor(self.pad_colors[(index // self.steps_per_group) % len(self.pad_colors)])
        if index % self.steps_per_group:
            colour = colour.darker(190)
        return colour.name()

    def paint_pads(self, painter: QPainter, rect: QRectF) -> None:
        """
        The sixteen step pads in their slot.

        :param painter: QPainter
        :param rect: QRectF the band along the bottom of the face
        :return: None
        """
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(self.slot_color))
        painter.drawRect(rect)
        step = rect.width() / self.steps
        top = rect.top() + 1
        for index in range(self.steps):
            left = rect.left() + index * step
            gap = 1.6 if index % self.steps_per_group == 0 else 0.8
            painter.setBrush(QColor(self.pad_color(index)))
            painter.drawRect(QRectF(left + gap, top, step - gap * 2, self.pad_band))

    def paint_ear(self, painter: QPainter, rect: QRectF) -> None:
        """The rounded side of the body, in the same matte black."""
        gradient = QLinearGradient(rect.topLeft(), rect.topRight())
        gradient.setColorAt(0, QColor(20, 21, 23))
        gradient.setColorAt(0.5, QColor(34, 35, 38))
        gradient.setColorAt(1, QColor(20, 21, 23))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.fillRect(rect, gradient)
        self.outline_ear(painter, rect, QColor(6, 6, 7))


class PatchCordsMixin:
    """
    Patch cords on a skin's cheeks: jacks, with a cable looped between two
    of them (or, on a very short strip, hanging off one), bowed toward the
    outer edge so it clears the panel. Each cheek's cable takes its colour
    from :attr:`cable_colors` by side (``ear_side``, set by ``paint_ears``):
    the first on the left, the second on the right.

    Mixed into a skin before its base class; the skin's ``paint_ear`` paints
    its own cheek and then calls :meth:`paint_patch_cord`.
    """

    #: cables: left cheek, right cheek (and any more the skin uses)
    cable_colors = ("#D23A2E", "#E8B828")
    #: cable thickness, px
    cable_width = 3.6
    #: below this height a cheek holds one jack, with the cable hanging off
    #: it; above it, two jacks with the cable looped between them
    loop_height = 28

    def jack_points(self, rect: QRectF) -> list:
        """
        Centres of the jacks on a cheek: a pair to loop a cable between, or
        on a very short strip a single jack.
        """
        x = rect.center().x()
        if rect.height() < self.loop_height:
            return [QPointF(x, rect.top() + rect.height() * 0.4)]
        # Closer to the ends on a tall cheek; on a short strip (the MIDI
        # player's bands, the status bar) far enough apart for both jacks
        spread = 0.2 if rect.height() >= 90 else 0.27
        return [
            QPointF(x, rect.top() + rect.height() * spread),
            QPointF(x, rect.top() + rect.height() * (1.0 - spread)),
        ]

    def jack_radius(self, rect: QRectF) -> float:
        """Smaller jacks on a short strip, so a pair still fits."""
        return max(2.5, min(rect.width() * 0.3, rect.height() * 0.17))

    def paint_patch_cord(self, painter: QPainter, rect: QRectF) -> None:
        """Jacks on the cheek ``rect``, and this side's cable between them."""
        painter.save()
        jacks = self.jack_points(rect)
        radius = self.jack_radius(rect)
        for jack in jacks:
            self.paint_jack(painter, jack, radius / 0.3)
        left_cheek = self.ear_side == "left"
        colour = QColor(self.cable_colors[0 if left_cheek else 1])
        # Bowed toward the outer edge, so the cable clears the panel
        bow = rect.left() + 1.5 if left_cheek else rect.right() - 1.5
        width = min(self.cable_width, max(2.0, rect.height() * 0.09))
        if len(jacks) == 2:
            reach = (jacks[1].y() - jacks[0].y()) * 0.25
            cable = QPainterPath(jacks[0])
            cable.cubicTo(
                QPointF(bow, jacks[0].y() + reach),
                QPointF(bow, jacks[1].y() - reach),
                jacks[1],
            )
        else:
            # One jack: the cable hangs off it and out of the strip
            cable = QPainterPath(jacks[0])
            cable.cubicTo(
                QPointF(bow, jacks[0].y()),
                QPointF(bow, rect.bottom()),
                QPointF(bow, rect.bottom() + 2.0),
            )
        painter.save()
        painter.setClipRect(rect)
        self.paint_cable(painter, cable, colour, width=width)
        painter.restore()
        for jack in jacks:
            self.paint_plug(painter, jack, radius / 0.3, colour)
        painter.restore()

    @staticmethod
    def paint_jack(painter: QPainter, centre: QPointF, width: float) -> None:
        """A jack socket: a silver nut round a black hole."""
        radius = max(3.0, width * 0.3)
        painter.setPen(QPen(QColor(20, 20, 20), 1))
        painter.setBrush(QColor(150, 150, 146))
        painter.drawEllipse(centre, radius, radius)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(4, 4, 4))
        painter.drawEllipse(centre, radius * 0.45, radius * 0.45)

    @staticmethod
    def paint_plug(painter: QPainter, centre: QPointF, width: float, colour: QColor) -> None:
        """The plug in a jack, in its cable's colour."""
        radius = max(2.4, width * 0.2)
        painter.setPen(QPen(colour.darker(160), 1))
        painter.setBrush(colour)
        painter.drawEllipse(centre, radius, radius)

    @staticmethod
    def paint_cable(painter: QPainter, path: QPainterPath, colour: QColor, width: float = 3.0) -> None:
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



#: The MS-20 has no screen. The editor's display takes the white of the
#: lettering printed on its black panel, on a cold dark ground.
ICE_LCD = LcdPalette(
    bg_edge="#0B0C0D",
    bg_mid="#15181A",
    bg_glow="#1F2427",
    text="#E6EEF0",
    text_dim="#8E9A9F",
)


class Ms20Skin(PatchCordsMixin, RackSkin):
    """
    The Korg MS-20: a matte black panel with its sections boxed in white
    lines, and patch cables.

    Editor panels are drawn from a stretched image that keeps only a few
    pixels of each edge sharp, so cables across their middle would be
    distorted and sit behind the controls. They get the white section box,
    drawn in that sharp edge. The cables are on the rack-mounted panels
    instead, where nothing lies behind them: each cheek is a small patch bay
    with a cable looped between two jacks, and a third cable sags along a
    slim rail under the panel, plugged into the foot of each cheek.
    """

    skin_id = "ms20"
    label = "MS-20"
    ear_width = 20
    bezel = 6
    #: The rail the long cable hangs in
    rail_height = 12
    lcd = ICE_LCD
    foreground = Foreground(
        text="#F2F2F0", text_secondary="#B4B4B0", rule="#5A5A58"
    )
    chassis = Chassis(
        body="#1C1C1C", surface="#101010", surface_alt="#1A1A1A",
        border="#444444", accent="#D23A2E",
    )
    #: the white section outline
    section_line = "#E4E4E0"
    #: cables: left cheek, right cheek, and the one along the rail
    cable_colors = ("#D23A2E", "#E8B828", "#2F6FD0")
    #: the cheeks and rail: dark grey plate
    plate_color = "#262626"
    def paint_face(
        self, painter: QPainter, rect: QRectF, sheen: bool = True
    ) -> None:
        path = QPainterPath()
        path.addRoundedRect(rect, 2, 2)
        gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        gradient.setColorAt(0.0, QColor(34, 34, 34))
        gradient.setColorAt(0.5, QColor(24, 24, 24))
        gradient.setColorAt(1.0, QColor(16, 16, 16))
        painter.fillPath(path, gradient)
        # The section box, inside the sharp edge of the panel image
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(self.section_line), 1))
        painter.drawRect(rect.adjusted(2.0, 2.0, -2.0, -3.0))
        painter.setPen(QPen(QColor(6, 6, 6), 1))
        painter.drawPath(path)

    def paint_ear(self, painter: QPainter, rect: QRectF) -> None:
        """A patch bay: jacks on a dark plate, with a cable looped outward."""
        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.fillRect(rect, QColor(self.plate_color))
        self.paint_patch_cord(painter, rect)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(8, 8, 8), 1))
        painter.drawRect(rect)
        painter.restore()

    def paint_rail(self, painter: QPainter, rect: QRectF) -> None:
        """A slim rail under the panel, with a cable sagging along it."""
        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.fillRect(rect, QColor(self.plate_color))
        colour = QColor(self.cable_colors[2])
        inset = self.ear_width / 2.0
        top = rect.top() + 4.0
        start = QPointF(rect.left() + inset, top)
        end = QPointF(rect.right() - inset, top)
        # Lowest in the middle, just inside the rail: a cubic with both
        # control points at height c bottoms out at (top + 3c) / 4
        lowest = rect.bottom() - 2.5
        low = (4.0 * lowest - top) / 3.0
        cable = QPainterPath(start)
        cable.cubicTo(
            QPointF(start.x() + rect.width() * 0.25, low),
            QPointF(end.x() - rect.width() * 0.25, low),
            end,
        )
        painter.setPen(QPen(QColor(8, 8, 8), 1))
        painter.drawLine(rect.topLeft(), rect.topRight())
        painter.save()
        painter.setClipRect(rect)
        self.paint_cable(painter, cable, colour, width=self.cable_width * 0.85)
        painter.restore()
        # Plugged in at each end
        for point in (start, end):
            self.paint_jack(painter, point, self.ear_width * 0.75)
            self.paint_plug(painter, point, self.ear_width * 0.75, colour)
        painter.restore()

#: The SH-101 has no screen, only red LEDs over its sequencer and arpeggio
#: keys; the editor's display takes those
SH101_LED_LCD = LcdPalette(
    bg_edge="#110706",
    bg_mid="#240C0A",
    bg_glow="#3B120E",
    text="#FF4E3A",
    text_dim="#A9321F",
)


class Sh101Skin(RackSkin):
    """
    The SH-101: a dark matte control panel set in a coloured plastic body.

    The SH-101 came in grey, red and blue, so it is offered in all three,
    as the JD-Xi is in black, red and white. What changes is the body: the
    rim of plastic showing round the panel, the lip along its front edge,
    the sides, and the chassis behind everything. The panel itself stays the
    same dark charcoal. A portable synth, so the sides are plain moulded
    plastic: no rack screws.

    The body colours are mid tones, dark enough that white lettering stays
    legible on the body as well as the panel.
    """

    skin_id = "sh101_grey"
    label = "SH-101 Grey"
    ear_width = 14
    bezel = 6
    rail_height = 0
    lcd = SH101_LED_LCD
    foreground = Foreground(
        text="#FFFFFF", text_secondary="#E4E4E0", rule="#55565A"
    )
    #: the plastic body
    body_color = "#707270"
    #: the plastic showing round the inset panel, and its front lip
    rim_width = 2
    lip = 3

    def __init__(self) -> None:
        body = QColor(self.body_color)
        self.chassis = Chassis(
            body=self.body_color,
            surface="#141516",
            surface_alt="#1F2022",
            border=body.darker(150).name(),
            accent=body.lighter(140).name(),
        )

    def paint_face(
        self, painter: QPainter, rect: QRectF, sheen: bool = True
    ) -> None:
        path = QPainterPath()
        path.addRoundedRect(rect, 3, 3)
        painter.save()
        painter.setClipPath(path)
        # The dark slider panel: matte, a soft fall-off
        gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        gradient.setColorAt(0.0, QColor(44, 45, 47))
        gradient.setColorAt(0.5, QColor(32, 33, 35))
        gradient.setColorAt(1.0, QColor(22, 23, 24))
        painter.fillRect(rect, gradient)
        # The body's front lip, inside the image's sharp bottom edge
        body = QColor(self.body_color)
        painter.fillRect(
            QRectF(rect.left(), rect.bottom() - self.lip, rect.width(), self.lip),
            body.darker(115),
        )
        painter.restore()
        # The plastic round the panel
        pen = QPen(body, self.rim_width)
        pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(pen)
        inset = self.rim_width / 2
        painter.drawRoundedRect(rect.adjusted(inset, inset, -inset, -inset), 2, 2)
        # Where the moulding catches the light
        painter.setPen(QPen(body.lighter(135), 1))
        painter.drawLine(
            QPointF(rect.left() + 3, rect.top() + 0.5),
            QPointF(rect.right() - 3, rect.top() + 0.5),
        )

    def paint_ear(self, painter: QPainter, rect: QRectF) -> None:
        """A side of the moulded body, rounded off toward its outer edge."""
        body = QColor(self.body_color)
        gradient = QLinearGradient(rect.topLeft(), rect.topRight())
        gradient.setColorAt(0.0, body.darker(118))
        gradient.setColorAt(0.5, body)
        gradient.setColorAt(1.0, body.darker(118))
        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.fillRect(rect, gradient)
        painter.restore()
        self.outline_ear(painter, rect, body.darker(170))


class Sh101RedSkin(Sh101Skin):
    """The SH-101 in red."""

    skin_id = "sh101_red"
    label = "SH-101 Red"
    body_color = "#C42C24"


class Sh101BlueSkin(Sh101Skin):
    """The SH-101 in blue."""

    skin_id = "sh101_blue"
    label = "SH-101 Blue"
    body_color = "#2A5DB4"


#: Every skin, by id, in the order they are offered
def _editor_settings_store() -> Optional[QSettingsStore]:
    try:
        from jdxi_editor.project import __organization_name__, __program__
    except Exception:
        return None
    return QSettingsStore(__organization_name__, __program__, SKIN_SETTING)


#: The ARP 2600 has no screen. The editor's display takes the white of the
#: legends printed on its dark panel, on black.
ARP_LCD = LcdPalette(
    bg_edge="#0A0B0C",
    bg_mid="#141618",
    bg_glow="#1E2124",
    text="#E8EAEC",
    text_dim="#9A9FA4",
)


class Arp2600Skin(PatchCordsMixin, RackSkin):
    """
    The ARP 2600: a dark charcoal panel printed in white, in a black case,
    with its speakers behind perforated grilles, and patch cords looped over
    them as on the MS-20's cheeks (white on the left, orange on the right).

    The panel's look is its printing: white legends, white boxes round the
    module titles and white signal-flow lines between them. Editor panels
    get a white box and the printed flow line along the top, inside the
    sharp edges of the panel image (so section titles print in that white,
    ink_legends). On the hardware the speaker grilles are in the panel's
    lower corners; here they are the cheeks either side, the one place on a
    rack panel nothing else sits. The case's black base runs under the panel
    as a rail, and its red power lamp is the accent.
    """

    skin_id = "arp2600"
    label = "ARP 2600"
    ear_width = 26
    bezel = 6
    rail_height = 6
    lcd = ARP_LCD
    foreground = Foreground(
        text="#F0F0EE", text_secondary="#B9BCBF", rule="#6A6E72"
    )
    ink_legends = True
    chassis = Chassis(
        body="#1B1C1E", surface="#111213", surface_alt="#1C1E20",
        border="#45494D", accent="#E0302A",
    )
    #: the painted panel, top to bottom
    panel_stops = ((0.0, 50, 53, 57), (0.5, 42, 45, 48), (1.0, 33, 35, 38))
    #: the white printing
    print_color = "#E6E8EA"
    #: the black case
    case_stops = ((0.0, 30, 31, 33), (1.0, 14, 15, 16))
    #: patch cords over the grilles: white like the printing on the left,
    #: ARP orange on the right
    cable_colors = ("#D9DBDD", "#E07A26")
    vintage_vu = True

    def paint_face(
        self, painter: QPainter, rect: QRectF, sheen: bool = True
    ) -> None:
        path = QPainterPath()
        path.addRoundedRect(rect, 2, 2)
        painter.save()
        painter.setClipPath(path)
        gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        for position, red, green, blue in self.panel_stops:
            gradient.setColorAt(position, QColor(red, green, blue))
        painter.fillRect(rect, gradient)
        ink = QColor(self.print_color)
        # The white box round the section, as round each module's title
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(ink, 1))
        painter.drawRect(rect.adjusted(1.5, 1.5, -1.5, -2.5))
        # The printed signal-flow line, inside the sharp top edge
        faint = QColor(ink)
        faint.setAlpha(150)
        painter.setPen(QPen(faint, 1))
        painter.drawLine(
            QPointF(rect.left() + 4, rect.top() + 4.0),
            QPointF(rect.right() - 4, rect.top() + 4.0),
        )
        painter.restore()
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(8, 8, 9), 1))
        painter.drawPath(path)

    def _paint_case(self, painter: QPainter, rect: QRectF, horizontal: bool) -> None:
        if horizontal:
            gradient = QLinearGradient(rect.topLeft(), rect.topRight())
        else:
            gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        for position, red, green, blue in self.case_stops:
            gradient.setColorAt(position, QColor(red, green, blue))
        painter.fillRect(rect, gradient)

    def paint_ear(self, painter: QPainter, rect: QRectF) -> None:
        """A speaker grille: a field of round holes in the black case."""
        painter.save()
        self._paint_case(painter, rect, horizontal=True)
        grille = rect.adjusted(4, 6, -4, -6)
        if grille.width() > 4 and grille.height() > 8:
            # Holes punched in the charcoal panel, as on the hardware
            red, green, blue = self.panel_stops[1][1:]
            painter.setPen(QPen(QColor(8, 8, 9), 1))
            painter.setBrush(QColor(red, green, blue))
            painter.drawRoundedRect(grille, 2, 2)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(4, 4, 5))
            step = 3.2
            y = grille.top() + 1.6
            row = 0
            while y < grille.bottom() - 1.0:
                x = grille.left() + 1.6 + (step / 2 if row % 2 else 0.0)
                while x < grille.right() - 1.0:
                    painter.drawEllipse(QPointF(x, y), 1.0, 1.0)
                    x += step
                y += step
                row += 1
        # A patch cord looped over the grille, as on the MS-20's cheeks
        self.paint_patch_cord(painter, rect)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(4, 4, 5), 1))
        painter.drawRect(rect)
        painter.restore()

    def paint_rail(self, painter: QPainter, rect: QRectF) -> None:
        """The case's black base, under the panel."""
        painter.save()
        self._paint_case(painter, rect, horizontal=False)
        painter.setPen(QPen(QColor(4, 4, 5), 1))
        painter.drawLine(rect.topLeft(), rect.topRight())
        painter.restore()


#: The editor's skins, in the order they are offered; the default registry,
#: which RackPanel and RackEars follow. Changing skin restyles the editor
#: (see _restyle_application, the registry's listener).
REGISTRY = SkinRegistry(
    (        RackSkin(),
        RedJdxiSkin(),
        WhiteJdxiSkin(),
        JdxiRackSkin(),
        Tr808Skin(),
        Tb303Skin(),
        Tr909Skin(),
        Jupiter8Skin(),
        Juno106Skin(),
        MiniMoogSkin(),
        Mc101Skin(),
        Ms20Skin(),
        Sh101Skin(),
        Sh101RedSkin(),
        Sh101BlueSkin(),
        Arp2600Skin(),
        Brushed70sSkin(),
        IvoryWalnutSkin(),
    
    ),
    default_id="glossy_black",
    store=_editor_settings_store(),
)
set_default_registry(REGISTRY)

#: Every skin, by id, in the order they are offered (the registry's own dict)
SKINS: Dict[str, RackSkin] = REGISTRY.skins


def skin_by_id(skin_id: Optional[str]) -> RackSkin:
    """
    The skin ``skin_id`` names, falling back to the default.

    :param skin_id: Optional[str] a key of :data:`SKINS`
    :return: RackSkin
    """
    return REGISTRY.get(skin_id)


def active_skin() -> RackSkin:
    """
    The skin everything is drawn with.

    :return: RackSkin
    """
    return REGISTRY.active()


def set_active_skin(skin: "str | RackSkin", *, remember: bool = True) -> RackSkin:
    """
    Change the skin, and restyle the running application.

    :param skin: str | RackSkin the skin, or its id
    :param remember: bool store the choice for next time
    :return: RackSkin the skin now in use
    """
    return REGISTRY.set_active(skin, remember=remember)


#: the panel image's filename in a stylesheet, whichever skin rendered it
_PANEL_IMAGE = re.compile(r"gloss_panel_[A-Za-z0-9_]+_(?P<size>\d+x\d+)\.png")


def _restyle_application(_skin: Optional[RackSkin] = None) -> None:
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
    from jdxi_editor.ui.widgets.midi.track_viewer import MidiTrackViewer
    from jdxi_editor.ui.widgets.rack.ears import RackEars
    from jdxi_editor.ui.widgets.rack.panel import RackPanel

    for widget in application.allWidgets():
        if isinstance(widget, (RackEars, MidiTrackViewer)):
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


REGISTRY.add_listener(_restyle_application)
