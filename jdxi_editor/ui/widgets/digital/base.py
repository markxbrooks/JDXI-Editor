"""
Digital Display Base class
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

from decologr import Decologr as log
from PySide6.QtCore import QRect
from PySide6.QtGui import QColor, QFont, QFontDatabase, QLinearGradient, QPainter, QPaintEvent, QPen
from PySide6.QtWidgets import QSizePolicy, QWidget

from jdxi_editor.resources import resource_path
from jdxi_editor.ui.widgets.digital.state import JDXiDisplayState

LCD_FONT_FILE = "JdLCD.ttf"
LCD_FONT_FALLBACKS = (
    "JD LCD Rounded",
    "DS-Digital",
    "Menlo",
    "Monaco",
    "Courier New",
    "monospace",
)

_loaded_lcd_family: str | None = None
_lcd_font_loaded = False


def _lcd_font_candidates() -> tuple[Path, ...]:
    """Return possible paths to the bundled LCD font."""
    package_root = Path(__file__).resolve().parents[3]
    project_root = package_root.parent
    return (
        project_root / "resources" / "fonts" / LCD_FONT_FILE,
        package_root / LCD_FONT_FILE,
        Path(resource_path(os.path.join("resources", "fonts", LCD_FONT_FILE))),
        Path(resource_path(LCD_FONT_FILE)),
    )


def load_lcd_font() -> str | None:
    """
    Register the bundled JD-Xi LCD font once per process.

    :return: The registered font family name, or None if loading failed.
    """
    global _loaded_lcd_family, _lcd_font_loaded

    if _lcd_font_loaded:
        return _loaded_lcd_family

    _lcd_font_loaded = True
    for font_path in _lcd_font_candidates():
        if not font_path.is_file():
            continue
        try:
            font_id = QFontDatabase.addApplicationFont(str(font_path))
        except Exception as ex:
            log.message(
                f"Failed to load LCD font from {font_path}: {ex}",
                level=logging.WARNING,
                scope="DigitalDisplayBase",
            )
            continue
        if font_id < 0:
            continue
        families = QFontDatabase.applicationFontFamilies(font_id)
        if not families:
            continue
        _loaded_lcd_family = families[0]
        log.message(
            f"Loaded LCD font family {_loaded_lcd_family!r} from {font_path}",
            scope="DigitalDisplayBase",
        )
        return _loaded_lcd_family

    log.message(
        "LCD font file not found; using system monospace fallbacks",
        level=logging.WARNING,
        scope="DigitalDisplayBase",
    )
    return None


def lcd_font_families(primary: str | None = None) -> tuple[str, ...]:
    """Build an ordered family list for LCD widgets."""
    load_lcd_font()
    families: list[str] = []
    for name in (primary, _loaded_lcd_family, *LCD_FONT_FALLBACKS):
        if name and name not in families:
            families.append(name)
    return tuple(families)


def get_lcd_font_family() -> str:
    """Return the preferred LCD font family for new widgets."""
    return lcd_font_families()[0]


def lcd_font(
    point_size: int,
    *,
    bold: bool = False,
    primary: str | None = None,
) -> QFont:
    """Build a font with LCD-style family fallbacks."""
    font = QFont()
    font.setFamilies(list(lcd_font_families(primary)))
    font.setPointSize(point_size)
    if bold:
        font.setBold(True)
    return font


class DigitalDisplayBase(QWidget):
    """Base class for JD-Xi style digital displays."""

    def __init__(
        self,
        digital_font_family: str | None = None,
        parent: QWidget = None,
    ):
        super().__init__(parent)
        load_lcd_font()
        self.digital_font_family = digital_font_family or get_lcd_font_family()
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

        import platform

        if platform.system() == "Windows":
            font_size = 13
        else:
            font_size = 19
        display_font = lcd_font(font_size, bold=True, primary=self.digital_font_family)
        painter.setFont(display_font)

        # Draw text
        y_offset = 10
        for text in self.display_texts:
            painter.setPen(QPen(QColor("#FFAA33")))
            rect = QRect(10, y_offset, self.width() - 20, 30)
            painter.drawText(rect, 1, str(text))
            y_offset += 30

    def set_state(self, state: JDXiDisplayState) -> None:
        self.update_display(["", state.tone_name])

    def update_display(self, texts: list) -> None:
        """Update the digital text and trigger repaint."""
        self.display_texts = texts
        self.update()

    def set_upper_display_text(self, text: str) -> None:
        """Update the upper line of the display."""
        self.display_texts[0] = text
        self.update()


# Backwards-compatible alias used by older imports.
LCD_FONT_FAMILIES = LCD_FONT_FALLBACKS
