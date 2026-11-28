"""
Preferences › Text size: Normal, Large, Larger, for the text only.

The editor's style sheets write their sizes by hand (``font-size: 11px``) in
many places. Rather than change each, with a size above Normal every style
sheet set on a widget goes through :func:`scale_style`: sizes below MIN_PX are
raised, and all sizes are multiplied by the chosen scale. Knobs, graphs and
spacing keep their size. The application font and the LCD text are scaled
the same way. At Normal nothing changes. It applies from the next start.

``JDXI_TEXT_SIZE`` (100, 112, 125) overrides the setting (screenshots).

From JD-Xi Studio 82d8c075.
"""

from __future__ import annotations

import os
import re
from functools import lru_cache

SETTING = "ui/text_size"
SIZES = {100: "Normal", 112: "Large", 125: "Larger"}
MIN_PX = 12  # with a larger text size, no text smaller than this

_FONT_PX = re.compile(r"(font-size\s*:\s*)(\d+(?:\.\d+)?)px", re.IGNORECASE)
_FONT_PT = re.compile(r"(font-size\s*:\s*)(\d+(?:\.\d+)?)pt", re.IGNORECASE)


@lru_cache(maxsize=1)
def scale() -> float:
    """The chosen text size as a factor (1.0 at Normal)."""
    forced = os.environ.get("JDXI_TEXT_SIZE")
    value = None
    if forced and forced.isdigit():
        value = int(forced)
    else:
        try:
            from PySide6.QtCore import QSettings

            from jdxi_editor.project import __organization_name__, __program__

            value = int(
                QSettings(__organization_name__, __program__).value(SETTING, 100)
            )
        except (TypeError, ValueError, ImportError):
            value = 100
    return (value if value in SIZES else 100) / 100.0


def px(size: float) -> int:
    """
    A text size in px: at least MIN_PX, times the scale.

    Tiny sizes (below 7 px) are not text but tricks (an invisible label, a
    dot): they stay.
    """
    if size < 7:
        return int(size)
    return int(round(max(size, MIN_PX) * scale()))


@lru_cache(maxsize=4096)
def scale_style(css: str) -> str:
    """The style sheet with its text sizes raised and scaled."""
    if not css or scale() == 1.0:
        return css
    out = _FONT_PX.sub(lambda m: f"{m.group(1)}{px(float(m.group(2)))}px", css)
    return _FONT_PT.sub(
        lambda m: f"{m.group(1)}{round(max(float(m.group(2)), 9) * scale(), 1)}pt",
        out,
    )


_installed = False


def install(app) -> None:
    """
    From now on every style sheet set on a widget or on the app has its text
    scaled, and the application font is scaled. Nothing at Normal.
    """
    global _installed
    if _installed or scale() == 1.0:
        return
    _installed = True
    from PySide6.QtWidgets import QApplication, QWidget

    original_widget = QWidget.setStyleSheet
    original_app = QApplication.setStyleSheet

    def widget_set(self, css):
        original_widget(self, scale_style(css))

    def app_set(self, css):
        original_app(self, scale_style(css))

    QWidget.setStyleSheet = widget_set
    QApplication.setStyleSheet = app_set
    font = app.font()
    if font.pointSizeF() > 0:
        font.setPointSizeF(max(font.pointSizeF(), 9.5) * scale())
    elif font.pixelSize() > 0:
        font.setPixelSize(px(font.pixelSize()))
    app.setFont(font)
