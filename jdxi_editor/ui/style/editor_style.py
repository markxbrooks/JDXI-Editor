"""
Shared restrained editor chrome (UI_CRITIQUE).

Grey idle borders and soft sliders; accent only for focus / active states.
Used app-wide via Theme.apply_editor_style; MidiPlayer/Pattern subclass this.
"""

from __future__ import annotations

import tempfile
from functools import lru_cache
from pathlib import Path
from typing import Optional


@lru_cache(maxsize=None)
def _icon_file(name: str, color: str, size: int = 12) -> str:
    """
    A qtawesome icon saved as PNG, for stylesheet ``image: url(...)``.

    Style sheets can only use image files; this draws the icon once per run
    (needs a QApplication) into the temp folder.
    """
    import qtawesome as qta

    folder = Path(tempfile.gettempdir()) / "jdxi_editor_icons"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{name.replace('.', '_')}_{color.lstrip('#')}_{size}.png"
    if not path.exists():
        qta.icon(name, color=color).pixmap(size, size).save(str(path))
    return path.as_posix()


# The JD-Xi's finish: rough matte black body (reads as dark grey) with a
# shiny black panel where the controls are
BODY_COLOR = "#2C2C2C"
BODY_GRAIN = 7  # +/- grey levels of texture noise
BODY_PROPERTY = "jdxiBody"  # set on an editor's root widget (see mark_editor_body)
FLAT_PROPERTY = "jdxiFlat"  # set on a tab stack nested in a glossy panel (see mark_flat)
SHEEN_PROPERTY = "jdxiSheen"  # set on an editor's outermost panels (see mark_sheen_panels)
SHEEN_SLICE = 3  # px of the panel image kept unstretched at each edge (rim, top highlight)
GLOSS_GRADIENT = (
    "qlineargradient(x1:0, y1:0, x2:0, y2:1,"
    " stop:0 #161618, stop:0.5 #0A0A0B, stop:1 #050506)"
)


def body_texture(width: int, height: int, seed: int = 7):
    """QImage of the matte body: BODY_COLOR with fine random grain."""
    import numpy as np
    from PySide6.QtGui import QColor, QImage

    rng = np.random.default_rng(seed)  # the same grain every run
    base = QColor(BODY_COLOR).red()
    grain = rng.integers(-BODY_GRAIN, BODY_GRAIN + 1, size=(height, width))
    grey = np.clip(base + grain, 0, 255).astype(np.uint32)
    argb = np.ascontiguousarray((0xFF << 24) | (grey << 16) | (grey << 8) | grey)
    image = QImage(argb.data, width, height, width * 4, QImage.Format.Format_RGB32)
    return image.copy()  # own the pixels (the numpy buffer goes away)


@lru_cache(maxsize=None)
def _body_grain_file(size: int = 128) -> str:
    """A tile of the body texture as PNG, for stylesheet background-image."""
    folder = Path(tempfile.gettempdir()) / "jdxi_editor_icons"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"body_grain_{BODY_COLOR.lstrip('#')}_{BODY_GRAIN}_{size}.png"
    if not path.exists():
        body_texture(size, size).save(str(path))
    return path.as_posix()


def mark_editor_body(widget) -> None:
    """Paint *widget* (an editor's root) with the matte body finish."""
    from PySide6.QtCore import Qt

    widget.setProperty(BODY_PROPERTY, True)
    widget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)


def _gloss_panel_file(width: int = 1000, height: int = 420) -> str:
    """
    The Instrument window's glossy panel (gradient, diagonal sheen, rim and
    top highlight) as PNG, for stylesheet border-image on editor panels.
    """
    folder = Path(tempfile.gettempdir()) / "jdxi_editor_icons"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"gloss_panel_{width}x{height}.png"
    if not path.exists():
        from PySide6.QtCore import QRectF, Qt
        from PySide6.QtGui import QImage, QPainter

        from jdxi_editor.ui.image.instrument import draw_gloss_panel

        image = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
        image.fill(Qt.GlobalColor.transparent)
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        draw_gloss_panel(painter, QRectF(0.5, 0.5, width - 1, height - 1), sheen=True)
        painter.end()
        image.save(str(path))
    return path.as_posix()


def mark_sheen_panels(editor) -> None:
    """
    Give *editor*'s outermost panels (tab panes and groups not inside another
    one) the Instrument window's glossy sheen. Panels inside them keep the
    plain gradient, so the reflection is not repeated.
    """
    from PySide6.QtWidgets import QGroupBox, QTabWidget, QWidget

    panel_types = (QGroupBox, QTabWidget)
    for widget in editor.findChildren(QWidget):
        if not isinstance(widget, panel_types) or widget.property(FLAT_PROPERTY):
            continue
        parent = widget.parentWidget()
        while parent is not None and parent is not editor:
            if isinstance(parent, panel_types):
                break
            parent = parent.parentWidget()
        if parent is editor:
            mark_sheen(widget)


def mark_sheen(widget) -> None:
    """Give *widget* (a QGroupBox or QTabWidget panel) the Instrument window's glossy sheen."""
    widget.setProperty(SHEEN_PROPERTY, True)
    widget.style().unpolish(widget)
    widget.style().polish(widget)


def mark_flat(widget) -> None:
    """
    Draw the groups inside *widget* (nested in a glossy panel) flat on that
    panel, as sections; a tab widget's pane is drawn flat too.
    """
    widget.setProperty(FLAT_PROPERTY, True)
    widget.style().unpolish(widget)
    widget.style().polish(widget)


def _jdxi_slider_rules(analog: bool = False) -> str:
    """
    The one slider look (both orientations): black handle with a neon border,
    dark groove, filled part in a neon gradient. Red, or the Analog neon blue.

    Vertical rules are the same as JDXiUIStyle.ADSR / ADSR_ANALOG, which the
    synth sections apply, so every slider of a kind looks alike.
    """
    from jdxi_editor.ui.style.jdxi import JDXiUIStyle as S

    neon = S.SLIDER_NEON_ANALOG if analog else S.SLIDER_NEON
    stop = S.SLIDER_NEON_GRADIENT_STOP_ANALOG if analog else S.SLIDER_NEON_GRADIENT_STOP
    hover = "#3399ff" if analog else "#ff3333"
    return f"""
        QSlider::groove:vertical {{
            background: #111;
            width: 6px;
            border-radius: 3px;
        }}
        QSlider::handle:vertical {{
            background: black;
            border: 2px solid {neon};
            width: 10px;
            height: 10px;
            margin: -8px;
            margin-bottom: 2px;
            margin-top: 1px;  /* else a handle at maximum is clipped at the top */
        }}
        QSlider::handle:vertical:hover {{
            border: 2px solid {hover};
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {stop}, stop:1 {neon});
        }}
        QSlider::sub-page:vertical {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {stop}, stop:1 {neon});
            border-radius: 3px;
        }}
        QSlider::add-page:vertical {{
            background: #222;
            border-radius: 3px;
        }}
        QSlider::groove:horizontal {{
            background: #111;
            height: 6px;
            border-radius: 3px;
        }}
        QSlider::handle:horizontal {{
            background: black;
            border: 2px solid {neon};
            width: 10px;
            height: 10px;
            margin: -4px 0;
        }}
        QSlider::handle:horizontal:hover {{
            border: 2px solid {hover};
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {stop}, stop:1 {neon});
        }}
        QSlider::sub-page:horizontal {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {stop}, stop:1 {neon});
            border-radius: 3px;
        }}
        QSlider::add-page:horizontal {{
            background: #222;
            border-radius: 3px;
        }}
        QSlider::handle:disabled {{
            border: 2px solid #333333;
        }}
        QSlider::sub-page:disabled {{
            background: #333333;
        }}
    """


class AppEditorStyle:
    """Design tokens + chrome stylesheet for all editors."""

    BACKGROUND = "#151515"
    SURFACE = "#202020"
    SURFACE_ALT = "#292929"
    BORDER = "#383838"
    BORDER_HOVER = "#555555"

    # JD-Xi identity: metallic for sections, illuminated for active, LCD for displays
    METALLIC_RED = "#A71920"
    ACCENT = "#E04435"  # illuminated red (active / focus)
    ACCENT_HOVER = "#F05A5A"
    BORDER_ACTIVE = ACCENT
    LCD_ORANGE = "#FF6A00"
    LCD_ORANGE_DIM = "#CC5500"
    LCD_BG_EDGE = "#1A0A0A"
    LCD_BG_MID = "#331111"
    LCD_BG_GLOW = "#551100"

    TEXT = "#E6E6E6"
    TEXT_SECONDARY = "#999999"

    FONT_PANEL = "12px"
    FONT_TRACK_NAME = "12px"
    FONT_TRACK_SECONDARY = "10px"
    FONT_CONTROL = "11px"
    FONT_RULER = "10px"
    FONT_STATUS = "11px"

    SPACING_RELATED = 8
    SPACING_GROUP = 14
    PANEL_PADDING = 12

    @classmethod
    def editor_stylesheet(cls, *, accent: Optional[str] = None) -> str:
        """
        Restrained editor chrome.

        GroupBoxes use grey borders (never an accent top stripe).
        ``accent`` tints focus/hover/checked only (e.g. Analog cyan).
        """
        focus = accent or cls.ACCENT
        # Prefer a lighter hover when using default red; otherwise reuse accent
        hover = cls.ACCENT_HOVER if accent is None else accent
        # Section chrome uses metallic red for selected tab underline (digital path)
        section = accent or cls.METALLIC_RED
        return f"""
        /* JD-Xi finish: the editor's root is the rough matte body; panels
           (group boxes, tab panes) are glossy black; everything between is
           transparent so the finish shows through */
        QWidget {{
            background-color: transparent;
            color: {cls.TEXT};
            font-size: {cls.FONT_CONTROL};
        }}
        QWidget[{BODY_PROPERTY}="true"] {{
            background-color: {BODY_COLOR};
            background-image: url({_body_grain_file()});
        }}
        QAbstractItemView, QTextEdit, QPlainTextEdit, QMenu, QToolTip {{
            background-color: {cls.SURFACE};
        }}
        QGroupBox {{
            background: {GLOSS_GRADIENT};
            border: 1px solid #000000;
            border-top: 1px solid #3A3A3C;
            border-radius: 4px;
            margin-top: 10px;
            padding: {cls.PANEL_PADDING}px;
            font-size: {cls.FONT_PANEL};
            font-weight: 600;
            color: {cls.TEXT};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 4px;
            color: {cls.TEXT_SECONDARY};
            font-size: {cls.FONT_PANEL};
        }}
        /* A group inside a panel is a section printed on it (as on the JD-Xi):
           no black box of its own, just its title and a thin rule */
        QGroupBox QGroupBox {{
            background: transparent;
            border: none;
            border-top: 1px solid #2E2E30;
            border-radius: 0;
        }}
        QLabel {{
            color: {cls.TEXT};
            font-size: {cls.FONT_CONTROL};
        }}
        {_jdxi_slider_rules(analog=accent is not None)}
        QCheckBox::indicator:checked {{
            border: 2px solid {focus};
        }}
        QLineEdit {{
            background-color: {cls.SURFACE_ALT};
            border: 1px solid {cls.BORDER};
            border-radius: 3px;
            color: {cls.TEXT};
            padding: 2px 4px;
            font-size: {cls.FONT_TRACK_NAME};
        }}
        QLineEdit:focus {{
            border-color: {focus};
        }}
        /* Plain buttons (round JD-Xi buttons style themselves) */
        QPushButton {{
            background-color: {cls.SURFACE_ALT};
            border: 1px solid {cls.BORDER};
            border-radius: 3px;
            padding: 3px 8px;
            color: {cls.TEXT};
        }}
        QPushButton:hover {{
            border-color: {cls.BORDER_HOVER};
        }}
        QPushButton:pressed {{
            background-color: {cls.SURFACE};
        }}
        QPushButton:disabled {{
            color: {cls.TEXT_SECONDARY};
        }}
        QComboBox {{
            background-color: {cls.SURFACE_ALT};
            border: 1px solid {cls.BORDER};
            border-radius: 3px;
            padding: 2px 6px;
            color: {cls.TEXT};
        }}
        QComboBox:hover {{
            border-color: {cls.BORDER_HOVER};
        }}
        QComboBox:focus {{
            border-color: {focus};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 18px;
        }}
        QComboBox::down-arrow {{
            image: url({_icon_file("mdi.chevron-down", cls.TEXT_SECONDARY)});
            width: 12px;
            height: 12px;
        }}
        QComboBox::down-arrow:hover, QComboBox::down-arrow:on {{
            image: url({_icon_file("mdi.chevron-down", cls.TEXT)});
        }}
        QComboBox QAbstractItemView {{
            background-color: {cls.SURFACE};
            border: 1px solid {cls.BORDER};
            selection-background-color: {cls.SURFACE_ALT};
            selection-color: {cls.TEXT};
        }}
        QSpinBox, QDoubleSpinBox {{
            background-color: {cls.SURFACE_ALT};
            border: 1px solid {cls.BORDER};
            border-radius: 3px;
            padding: 2px 4px;
            color: {cls.TEXT};
        }}
        QSpinBox:focus, QDoubleSpinBox:focus {{
            border-color: {focus};
        }}
        QTabWidget::pane {{
            border: 1px solid #000000;
            border-top: 1px solid #3A3A3C;
            background: {GLOSS_GRADIENT};
        }}
        /* An editor's outermost panels: the Instrument window's glossy panel */
        QGroupBox[{SHEEN_PROPERTY}="true"],
        QTabWidget[{SHEEN_PROPERTY}="true"]::pane {{
            background: transparent;
            border-width: {SHEEN_SLICE}px;
            border-image: url({_gloss_panel_file()}) {SHEEN_SLICE} {SHEEN_SLICE} {SHEEN_SLICE} {SHEEN_SLICE} stretch stretch;
        }}
        /* A widget marked flat (mark_flat) sits on the glossy panel
           around it, and so do its groups. Marked explicitly: a descendant
           selector would also match every editor, as all of them sit in the
           main window's tabs. */
        QTabWidget[{FLAT_PROPERTY}="true"]::pane,
        QWidget[{FLAT_PROPERTY}="true"] QGroupBox {{
            background: transparent;
            border: none;
            border-top: 1px solid #2E2E30;
            border-radius: 0;
        }}
        QTabBar::tab {{
            background-color: {cls.SURFACE_ALT};
            border: none;
            border-bottom: 2px solid transparent;
            color: {cls.TEXT_SECONDARY};
            padding: 6px 12px;
            margin-right: 2px;
        }}
        QTabBar::tab:selected {{
            color: {cls.TEXT};
            background-color: {cls.SURFACE};
            border-bottom: 2px solid {section};
        }}
        QTabBar::tab:hover {{
            color: {cls.TEXT};
            border-bottom: 2px solid {cls.BORDER_HOVER};
        }}
        /* Thin grey scrollbars */
        QScrollBar:horizontal {{
            background: {cls.BACKGROUND};
            border: none;
            height: 10px;
            margin: 0;
        }}
        QScrollBar:vertical {{
            background: {cls.BACKGROUND};
            border: none;
            width: 10px;
            margin: 0;
        }}
        QScrollBar::handle:horizontal, QScrollBar::handle:vertical {{
            background: {cls.BORDER};
            border: none;
            border-radius: 4px;
            min-width: 24px;
            min-height: 24px;
        }}
        QScrollBar::handle:hover {{
            background: {cls.BORDER_HOVER};
        }}
        QScrollBar::add-line, QScrollBar::sub-line {{
            width: 0;
            height: 0;
            border: none;
        }}
        QScrollBar::add-page, QScrollBar::sub-page {{
            background: none;
        }}
        """


# Alias used as JDXi.UI.EditorStyle
EditorStyle = AppEditorStyle
