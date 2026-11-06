"""
Digital Display Base class
"""

from __future__ import annotations

import logging
import os
import platform
from pathlib import Path
from typing import Optional

from decologr import Decologr as log
from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontDatabase,
    QLinearGradient,
    QPainter,
    QPaintEvent,
    QPen,
)
from PySide6.QtWidgets import QSizePolicy, QWidget

from jdxi_editor.resources import resource_path
from jdxi_editor.ui.style.editor_style import AppEditorStyle
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
        self.display_texts: list[str] = []
        self.setMinimumSize(210, 70)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def paintEvent(self, event: QPaintEvent) -> None:
        """Handles rendering of the digital digital."""
        painter = QPainter(self)
        if not painter.isActive():
            return
        painter.setRenderHint(QPainter.Antialiasing, False)
        self.draw_display(painter)

    def _paint_lcd_panel(self, painter: QPainter) -> None:
        """Signature LCD bezel: dark red gradient + subtle inner edge."""
        style = AppEditorStyle
        w, h = self.width(), self.height()

        gradient = QLinearGradient(0, 0, 0, h)
        gradient.setColorAt(0.0, QColor(style.LCD_BG_EDGE))
        gradient.setColorAt(0.35, QColor(style.LCD_BG_MID))
        gradient.setColorAt(0.55, QColor(style.LCD_BG_GLOW))
        gradient.setColorAt(1.0, QColor(style.LCD_BG_EDGE))

        painter.setBrush(gradient)
        painter.setPen(QPen(QColor("#0A0505"), 2))
        painter.drawRect(0, 0, w, h)

        # Inner highlight (top) / shadow (bottom) for LCD depth
        painter.setPen(QPen(QColor(80, 40, 20, 90), 1))
        painter.drawLine(3, 3, w - 4, 3)
        painter.setPen(QPen(QColor(0, 0, 0, 120), 1))
        painter.drawLine(3, h - 4, w - 4, h - 4)

    def draw_display(self, painter: QPainter):
        """Draws the LCD-style digital with a gradient glow effect."""
        self._paint_lcd_panel(painter)

        if platform.system() == "Windows":
            font_size = 13
        else:
            font_size = 16
        display_font = lcd_font(font_size, bold=True, primary=self.digital_font_family)
        painter.setFont(display_font)

        line_h = 22 if len(self.display_texts) > 2 else 28
        y_offset = 8
        for i, text in enumerate(self.display_texts):
            # Primary line (tone) brighter; secondary lines slightly dimmer
            color = (
                AppEditorStyle.LCD_ORANGE
                if i == 0 or (i == 1 and len(self.display_texts) <= 2)
                else AppEditorStyle.LCD_ORANGE_DIM
            )
            # Prefer last non-empty line as hero when upper is a status line
            if len(self.display_texts) >= 2 and i == len(self.display_texts) - 1:
                color = AppEditorStyle.LCD_ORANGE
            painter.setPen(QPen(QColor(color)))
            rect = QRect(10, y_offset, self.width() - 20, line_h)
            painter.drawText(
                rect,
                int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
                str(text),
            )
            y_offset += line_h

    def set_state(self, state: JDXiDisplayState) -> None:
        lines = [state.tone_name]
        detail = state.bank_detail_line()
        if detail:
            lines.append(detail)
        self.update_display(lines)

    def update_display(self, texts: list) -> None:
        """Update the digital text and trigger repaint."""
        self.display_texts = [str(t) for t in texts]
        self.update()

    def set_upper_display_text(self, text: str) -> None:
        """Update the upper line of the display."""
        if not self.display_texts:
            self.display_texts = [text]
        else:
            self.display_texts[0] = text
        self.update()

    def set_wire_detail(
        self,
        *,
        bank_msb: Optional[int] = None,
        bank_lsb: Optional[int] = None,
        program: Optional[int] = None,
    ) -> None:
        """Set or clear the BANK / PC detail line under the tone name."""
        tone = ""
        if self.display_texts:
            # Prefer the last line as tone when an upper status line exists
            tone = self.display_texts[-1] if len(self.display_texts) > 1 else self.display_texts[0]
            if len(self.display_texts) > 1 and self.display_texts[0]:
                # Keep upper status (tempo / bar) + tone + wire
                upper = self.display_texts[0]
                detail = JDXiDisplayState.format_bank_line(bank_msb, bank_lsb, program)
                lines = [upper, tone]
                if detail:
                    lines.append(detail)
                self.update_display(lines)
                return

        detail = JDXiDisplayState.format_bank_line(bank_msb, bank_lsb, program)
        lines = [tone] if tone else []
        if detail:
            lines.append(detail)
        if lines:
            self.update_display(lines)


# Backwards-compatible alias used by older imports.
LCD_FONT_FAMILIES = LCD_FONT_FALLBACKS
