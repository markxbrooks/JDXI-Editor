"""
Lit Button

A checkable button that lights like a JD-Xi panel button: dark when off,
filled with the illuminated red (with a soft glow) when on.

Example:
    >>> button = LitButton("ON")          # doctest: +SKIP
    >>> button.setChecked(True)           # lit, even with signals blocked
"""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QPushButton, QWidget

from jdxi_editor.ui.style.editor_style import AppEditorStyle as Style

GLOW_RADIUS = 16


class LitButton(QPushButton):
    """Checkable panel-style button with an LED-like lit state."""

    def __init__(
        self, text: str, parent: Optional[QWidget] = None, color: Optional[str] = None
    ) -> None:
        """
        :param text: label (shown as written; panel labels are uppercase)
        :param color: lit colour (default: the illuminated red)
        """
        super().__init__(text, parent)
        self._color = color or Style.ACCENT
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(self.stylesheet(self._color))
        self._update_glow()

    @staticmethod
    def stylesheet(color: str) -> str:
        lit_border = QColor(color).lighter(125).name()
        return f"""
        QPushButton {{
            background-color: {Style.SURFACE};
            border: 1px solid {Style.BORDER};
            border-radius: 3px;
            color: {Style.TEXT_SECONDARY};
            padding: 3px 10px;
            font-size: 10px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            border-color: {Style.BORDER_HOVER};
            color: {Style.TEXT};
        }}
        QPushButton:checked {{
            background-color: {color};
            border-color: {lit_border};
            color: #FFFFFF;
        }}
        QPushButton:disabled {{
            color: {Style.BORDER_HOVER};
        }}
        """

    def checkStateSet(self) -> None:
        """setChecked() from code (also with signals blocked): update the glow."""
        super().checkStateSet()
        self._update_glow()

    def nextCheckState(self) -> None:
        """A click: update the glow."""
        super().nextCheckState()
        self._update_glow()

    def is_lit(self) -> bool:
        return self.isChecked()

    def _update_glow(self) -> None:
        if self.isChecked():
            glow = QGraphicsDropShadowEffect(self)
            glow.setBlurRadius(GLOW_RADIUS)
            glow.setOffset(0, 0)
            color = QColor(self._color)
            color.setAlpha(170)
            glow.setColor(color)
            self.setGraphicsEffect(glow)
        else:
            self.setGraphicsEffect(None)
