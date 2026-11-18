"""
Rack status bar
===============

The strip along the bottom of the Instrument window -- the wheels, the MIDI
indicators and the keyboard -- drawn as part of the instrument rather than as
a status bar, with the active skin's ears at each end.

The ears are the skin's own: a skin that declares none simply gets a plain
strip, so the default JD-Xi look is unchanged.
"""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QRectF
from PySide6.QtGui import QPainter, QPaintEvent
from PySide6.QtWidgets import QStatusBar, QWidget

from jdxi_editor.ui.style.rack_skin import active_skin


class RackStatusBar(QStatusBar):
    """A status bar with the skin's rack ears at each end."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        :param parent: Optional[QWidget] Qt parent
        """
        super().__init__(parent)
        self.setSizeGripEnabled(False)
        self.apply_skin()

    def apply_skin(self) -> None:
        """
        Leave room for the ears the active skin draws, and repaint.

        :return: None
        """
        ears = active_skin().ear_width
        self.setContentsMargins(ears, 0, ears, 0)
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Paint the strip, then its ears over each end.

        :param event: QPaintEvent
        :return: None
        """
        super().paintEvent(event)
        skin = active_skin()
        if not skin.ear_width:
            return
        painter = QPainter(self)
        if not painter.isActive():
            return
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        area = QRectF(self.rect())
        skin.paint_ear(
            painter, QRectF(area.left(), area.top(), skin.ear_width, area.height())
        )
        skin.paint_ear(
            painter,
            QRectF(
                area.right() - skin.ear_width,
                area.top(),
                skin.ear_width,
                area.height(),
            ),
        )
