"""
Rack ears
=========

The active skin's rack ears at each end of a horizontal strip: the upper and
lower bands of the MIDI player, where a full :class:`RackPanel` would paint a
second faceplate behind one that is already there.

A skin that declares no ears (the default JD-Xi panel) adds no margin and
draws nothing, so the strip is unchanged until a rack skin is chosen.
"""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QRectF
from PySide6.QtGui import QPainter, QPaintEvent
from PySide6.QtWidgets import QSizePolicy, QVBoxLayout, QWidget

from jdxi_editor.ui.style.rack_skin import active_skin


class RackEars(QWidget):
    """A strip with the skin's rack ears at each end and content between them."""

    def __init__(self, content: QWidget, parent: Optional[QWidget] = None) -> None:
        """
        :param content: QWidget the face between the ears
        :param parent: Optional[QWidget] Qt parent
        """
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.addWidget(content)
        self.apply_skin()

    def apply_skin(self) -> None:
        """
        Leave room for the ears the active skin draws, and repaint.

        :return: None
        """
        ears = active_skin().ear_width
        self.layout().setContentsMargins(ears, 0, ears, 0)
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Paint an ear over each end. The face between them is the content.

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
        width = skin.ear_width
        skin.paint_ear(painter, QRectF(area.left(), area.top(), width, area.height()))
        skin.paint_ear(
            painter,
            QRectF(area.right() - width, area.top(), width, area.height()),
        )
