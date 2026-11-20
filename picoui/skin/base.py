"""
picoui.skin.base
The look of a panel, as an object: the faceplate painted behind the content,
any rack ears beside it, a rail under it, and the palette its display and
lettering pick up.

A skin owns chrome only, never layout. The room it may take is the three
numbers it declares -- :attr:`Skin.ear_width`, :attr:`Skin.bezel` and
:attr:`Skin.rail_height` -- which :meth:`Skin.content_margins` turns into the
margins a :class:`~picoui.skin.widgets.RackPanel` gives its layout, so a skin
cannot quietly grow.

The base is a shiny black panel. A new skin subclasses it and declares those
numbers and its palette. Its look is declared too where it can be: a
:class:`~picoui.skin.spec.FaceSpec` as :attr:`Skin.face` and an
:class:`~picoui.skin.spec.EarSpec` as :attr:`Skin.ear`, which
:mod:`picoui.skin.render` paints. What a spec cannot describe is painted by
overriding a hook (``paint_face``, ``paint_ear``, ``paint_rail``); see
:mod:`picoui.skin.textures` for materials.
"""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QMargins, QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen, QPolygonF

from picoui.skin import render
from picoui.skin.gradient import GradientColorStops, GradientStop, apply_gradient_stops
from picoui.skin.palette import DARK_CHASSIS, DEFAULT_LCD, LIGHT_LETTERING
from picoui.skin.spec import EarSpec, FaceSpec, RailSpec


class Skin:
    """
    A shiny black panel, and the base every skin extends.

    :cvar skin_id: str unique id, used to store the choice
    :cvar label: str the name offered to the user
    :cvar ear_width: px of rack ear at each side; 0 for no ears
    :cvar bezel: px between the faceplate's edge and the content
    :cvar rail_height: px of rail below the content; 0 for none
    """

    skin_id = "default"
    label = "Default"
    ear_width = 0
    bezel = 7
    rail_height = 0
    lcd = DEFAULT_LCD
    foreground = LIGHT_LETTERING
    chassis = DARK_CHASSIS
    #: the glossy material, top to bottom: a skin can be the same panel in a
    #: different plastic or metal by declaring these alone
    face_stops = GradientColorStops(
        (
            GradientStop(0.0, QColor(22, 22, 24)),
            GradientStop(0.5, QColor(10, 10, 11)),
            GradientStop(1.0, QColor(4, 4, 5)),
        )
    )
    #: the rim drawn round the panel
    face_rim = "#000000"
    #: the highlight along its top edge, as r, g, b, a
    face_highlight = (255, 255, 255, 28)
    #: the diagonal reflection's strength, near and far
    sheen_strength = (22, 6)
    #: Section titles printed in the faceplate's ink, rather than the accent
    ink_legends = False
    #: Buttons shaded as caps, and fields as wells milled into the plate
    mounted_controls = False
    #: The faceplate as data. None, or a spec without a material, is the
    #: glossy panel above; a spec's overlays are drawn over either.
    face: Optional[FaceSpec] = None
    #: The ears as data. None leaves :meth:`paint_ear` to paint them, which
    #: the base skin does not.
    ear: Optional[EarSpec] = None
    #: The rail as data, painted in the :attr:`rail_height` below the
    #: content. None leaves :meth:`paint_rail` to paint it.
    rail: Optional[RailSpec] = None

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
        self.paint_ears(painter, rect)
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

    #: Which cheek :meth:`paint_ear` is painting: "left" or "right". Set by
    #: :meth:`paint_ears`, for skins whose two cheeks differ.
    ear_side = "left"

    def paint_ears(self, painter: QPainter, rect: QRectF) -> None:
        """
        Paint an ear at each end of ``rect`` (a panel, or a strip such as a
        status bar), telling :meth:`paint_ear` which side via
        :attr:`ear_side`.

        :param painter: QPainter
        :param rect: QRectF the panel or strip
        :return: None
        """
        if not self.ear_width:
            return
        width = self.ear_width
        for side, left in (("left", rect.left()), ("right", rect.right() - width)):
            self.ear_side = side
            self.paint_ear(painter, QRectF(left, rect.top(), width, rect.height()))
        self.ear_side = "left"

    def paint_face(
        self, painter: QPainter, rect: QRectF, sheen: bool = True
    ) -> None:
        """
        The faceplate this skin's :attr:`face` describes, or, without one,
        a shiny black plastic panel: deep gradient, diagonal sheen, soft rim.

        :param painter: QPainter
        :param rect: QRectF the panel's area
        :param sheen: bool draw the diagonal reflection; the instrument's
            right-hand panel is drawn without it, as on the JD-Xi
        :return: None
        """
        face = self.face
        if face is not None and face.material is not None:
            render.paint_face(face, painter, rect)
            return
        self._paint_glossy(painter, rect, sheen)
        if face is not None:
            render.paint_overlays(face, painter, rect)

    def _paint_glossy(self, painter: QPainter, rect: QRectF, sheen: bool) -> None:
        """
        The glossy panel, in :attr:`face_stops`.

        :param painter: QPainter
        :param rect: QRectF the panel's area
        :param sheen: bool draw the diagonal reflection
        :return: None
        """
        gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        apply_gradient_stops(gradient, self.face_stops)
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
        Paint one rack ear, as :attr:`ear` describes. The default skin has
        none.

        :param painter: QPainter
        :param rect: QRectF the ear's area
        :return: None
        """
        if self.ear is not None:
            render.paint_ear(self.ear, painter, rect, side=self.ear_side)

    def paint_rail(self, painter: QPainter, rect: QRectF) -> None:
        """
        Paint the rail, as :attr:`rail` describes. The default skin has none.

        :param painter: QPainter
        :param rect: QRectF the rail's area
        :return: None
        """
        if self.rail is not None:
            render.paint_rail(self.rail, painter, rect)

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
        render.paint_screw(painter, centre, radius, tint)

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
