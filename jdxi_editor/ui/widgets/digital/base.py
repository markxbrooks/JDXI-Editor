"""
Digital Display Base class
"""

import platform

from PySide6.QtCore import QRect
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPaintEvent, QPen
from PySide6.QtWidgets import QSizePolicy, QWidget

from jdxi_editor.ui.widgets.digital.state import JDXiDisplayState


class DigitalDisplayBase(QWidget):
    """Base class for JD-Xi style digital displays."""

    def __init__(
        self, digital_font_family: str = "JD LCD Rounded", parent: QWidget = None
    ):
        super().__init__(parent)
        """Initialize the DigitalDisplayBase

        :param digital_font_family: str
        :param parent: QWidget
        """
        self.digital_font_family = digital_font_family
        self.display_texts = []
        self.setMinimumSize(210, 70)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def paintEvent(self, event: QPaintEvent) -> None:
        """Handles rendering of the digital digital."""
        painter = QPainter(self)
        if not painter.isActive():
            return
        painter.setRenderHint(QPainter.Antialiasing, False)
        self.draw_display(painter)

    def draw_display(self, painter: QPainter):
        """Draws the LCD-style digital with a gradient glow effect."""
        display_width, display_height = self.width(), self.height()

        # Gradient background
        gradient = QLinearGradient(0, 0, display_width, display_height)
        gradient.setColorAt(0.0, QColor("#321212"))
        gradient.setColorAt(0.3, QColor("#331111"))
        gradient.setColorAt(0.5, QColor("#551100"))
        gradient.setColorAt(0.7, QColor("#331111"))
        gradient.setColorAt(1.0, QColor("#111111"))

        painter.setBrush(gradient)
        painter.setPen(QPen(QColor("#000000"), 2))
        painter.drawRect(0, 0, display_width, display_height)

        # Set font
        if platform.system() == "Windows":
            font_size = 13
        else:
            font_size = 19
        display_font = QFont(self.digital_font_family, font_size, QFont.Bold)
        painter.setFont(display_font)

        # Draw text
        y_offset = 10
        for text in self.display_texts:
            painter.setPen(QPen(QColor("#FFAA33")))
            # rect = QRect(10, y_offset, self.width() - 20, 30)  # Proper text bounding area
            rect = QRect(
                10, y_offset, self.width() - 20, 30
            )  # Proper text bounding area
            painter.drawText(rect, 1, str(text))
            y_offset += 30  # Space out text lines

    def set_state(self, state: JDXiDisplayState) -> None:
        self.update_display(["", state.tone_name])

    def update_display(self, texts: list) -> None:
        """Update the digital text and trigger repaint.

        :param texts: list
        """
        self.display_texts = texts
        self.update()

    def set_upper_display_text(self, text: str) -> None:
        """Update the digital text and trigger repaint.

        :param text: list
        """
        self.display_texts[0] = text
        self.update()
