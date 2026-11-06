"""
Module: JD-Xi Instrument Display Renderer
=========================================

This module provides functions to generate a visual representation of the Roland JD-Xi synthesizer
interface using PySide6. It renders key UI elements, including the digital, sequencer section,
and keyboard.

Functions
---------
- :func:`draw_instrument_pixmap`
- :func:`draw_display`
- :func:`draw_sequencer`

Dependencies
------------
- PySide6.QtCore (Qt)
- PySide6.QtGui (QFont, QPixmap, QImage, QPainter, QPen, QColor)
- jdxi_editor.ui.windows.jdxi.dimensions (JDXI_WIDTH, JDXI_HEIGHT, etc.)

Usage
-----
These functions generate and digital a graphical representation of the JD-Xi’s controls,
which can be integrated into a larger PySide6-based UI.
"""


from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QColor,
    QImage,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QPolygonF,
)

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.ui.style.editor_style import BODY_COLOR, body_texture  # noqa: F401  (BODY_COLOR re-exported)


# The JD-Xi's finish (shared with the editors, see editor_style): rough
# matte black body with a shiny black panel inset, split into two halves
PANEL_INSET = 7  # body visible around the panel, px
PANEL_SPLIT_X = 498  # gap between the left (display, parts) and right halves
PANEL_SPLIT_GAP = 4


def draw_gloss_panel(painter: QPainter, rect: QRectF, sheen: bool) -> None:
    """A shiny black plastic panel: deep gradient, soft edge, optional sheen."""
    gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
    gradient.setColorAt(0, QColor(22, 22, 24))
    gradient.setColorAt(0.5, QColor(10, 10, 11))
    gradient.setColorAt(1, QColor(4, 4, 5))
    path = QPainterPath()
    path.addRoundedRect(rect, 3, 3)
    painter.fillPath(path, gradient)
    if sheen:
        # Diagonal reflection, as the light falls across the left half of the
        # real panel: lighter to the left of a line leaning from top right
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
    # Edge: dark rim with a faint highlight along the top
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.setPen(QPen(QColor(0, 0, 0), 1))
    painter.drawPath(path)
    painter.setPen(QPen(QColor(255, 255, 255, 28), 1))
    painter.drawLine(
        QPointF(rect.left() + 3, rect.top() + 1), QPointF(rect.right() - 3, rect.top() + 1)
    )


def draw_instrument_pixmap() -> QPixmap:
    """
    Create a visual representation of the JD-Xi instrument panel.

    The body is rough matte black (dark grey, with grain); the controls sit on
    an inset of shiny black plastic in two halves, as on the JD-Xi.

    :return: QPixmap representation of the JD-Xi interface.
    :rtype: QPixmap
    """
    jdxi_width = JDXi.UI.Dimensions.INSTRUMENT.WIDTH
    # The control panel only: the keyboard is a widget below it
    jdxi_height = JDXi.UI.Dimensions.INSTRUMENT.PANEL_HEIGHT

    pixmap = QPixmap.fromImage(body_texture(jdxi_width, jdxi_height))
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)  # type: ignore[attr-defined]

    top = PANEL_INSET - 1
    bottom = jdxi_height - PANEL_INSET + 1
    left_half = QRectF(PANEL_INSET, top, PANEL_SPLIT_X - PANEL_INSET, bottom - top)
    right_x = PANEL_SPLIT_X + PANEL_SPLIT_GAP
    right_half = QRectF(right_x, top, jdxi_width - PANEL_INSET - right_x, bottom - top)
    draw_gloss_panel(painter, left_half, sheen=True)
    draw_gloss_panel(painter, right_half, sheen=False)

    draw_sequencer(painter)
    painter.end()
    return pixmap


def draw_sequencer(painter: QPainter) -> None:
    """
    Draw the sequencer section of the JD-Xi interface.

    :param painter: QPainter instance used for drawing.
    :type painter: QPainter
    :return: None
    :rtype: None
    """
    # Panel coordinates: the image is exactly the panel, so the lines line up
    # with the step buttons laid over it
    steps_top = JDXi.UI.Dimensions.SEQUENCER.STEPS_TOP
    sequencer_width = (
        JDXi.UI.Dimensions.SEQUENCER.WIDTH
    )  # Use roughly half keyboard width
    sequencer_x = JDXi.UI.Dimensions.SEQUENCER.X  # Align with right edge of keyboard
    # Calculate step dimensions
    step_count = JDXi.UI.Dimensions.SEQUENCER.STEPS
    step_size = JDXi.UI.Dimensions.SEQUENCER.STEP_SIZE  # Smaller square size
    total_spacing = sequencer_width - (step_count * step_size)
    step_spacing = total_spacing / (step_count - 1)
    # Draw horizontal measure lines (white)
    painter.setPen(QPen(Qt.white, 1))  # type: ignore[attr-defined]
    # Three lines (6 px apart, from line_y - 25) ending 6 px above the steps
    line_y = steps_top + 7
    measure_width = (step_size + step_spacing) * 4  # Width of 4 steps
    line_spacing = step_size / 3  # Space between lines
    time_signatures = [4, 2, 4]  # Time signatures for each beat grid

    for time_signature_number, beats in enumerate(time_signatures):
        for beat_number in range(beats):
            if time_signature_number == 0:
                scaled_measure_width = measure_width * 0.75
            elif beats == 2:
                scaled_measure_width = measure_width * 2.0
            else:
                scaled_measure_width = measure_width
            x1 = int(sequencer_x + (beat_number * scaled_measure_width))
            x2 = int(
                (x1 + scaled_measure_width) - step_spacing
            )  # Stop before next measure
            y = line_y - 25 + time_signature_number * line_spacing
            painter.drawLine(
                int(x1),
                int(y),
                int(x2),
                int(y),
            )
