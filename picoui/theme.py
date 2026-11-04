"""
Centralized theme management for PicoUI hosts.

Applies qdarktheme (when available), optional custom stylesheets, and
consistent widget styling across applications.
"""

from __future__ import annotations

from typing import Optional

from decologr import Decologr as log
from PySide6.QtCore import QObject, Qt
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication, QStyleFactory, QWidget
from picoui.utils.strenum import StrEnum


try:
    import darkdetect

    HAS_DARKDETECT = True
except ImportError:
    HAS_DARKDETECT = False

try:
    import qdarktheme

    HAS_QDARKTHEME = True
except ImportError:
    HAS_QDARKTHEME = False


class ThemeType(StrEnum):
    """Supported theme modes."""

    DARK = "dark"
    LIGHT = "light"
    AUTO = "auto"


class ThemeManager(QObject):
    """Singleton theme manager for PicoUI applications."""

    _instance: Optional["ThemeManager"] = None
    Theme: type[ThemeType] = ThemeType

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return
        super().__init__()
        self._initialized = True
        self._theme: ThemeType = ThemeType.AUTO
        self._resolved: ThemeType = ThemeType.DARK
        self._corner_shape: str = "rounded"
        self._custom_applied: bool = False

    @property
    def theme(self) -> str:
        """Last requested theme mode (may be ``auto``)."""
        return self._theme

    @property
    def resolved_theme(self) -> str:
        """Concrete light/dark theme currently in effect."""
        return self._resolved

    @staticmethod
    def detect() -> str:
        """Return ``light`` or ``dark`` from the OS, defaulting to dark."""
        if not HAS_DARKDETECT:
            return ThemeType.DARK
        try:
            return ThemeType.DARK if darkdetect.isDark() else ThemeType.LIGHT
        except Exception:
            log.warning("Theme detection failed, defaulting to dark")
            return ThemeType.DARK

    @staticmethod
    def resolve(theme: ThemeType = ThemeType.AUTO) -> str:
        """Resolve ``auto`` to a concrete light/dark value."""
        if theme == ThemeType.AUTO:
            return ThemeManager.detect()
        if theme in (ThemeType.LIGHT, ThemeType.DARK):
            return theme
        log.warning(f"Unknown theme {theme!r}, defaulting to dark")
        return ThemeType.DARK

    @staticmethod
    def stylesheet(theme: ThemeType = ThemeType.AUTO, corner_shape: str = "rounded") -> str:
        """Return a qdarktheme stylesheet, or an empty string if unavailable."""
        if not HAS_QDARKTHEME or not hasattr(qdarktheme, "load_stylesheet"):
            return ""
        resolved = ThemeManager.resolve(theme)
        try:
            return qdarktheme.load_stylesheet(resolved, corner_shape=corner_shape)
        except TypeError:
            return qdarktheme.load_stylesheet(resolved)
        except Exception as ex:
            log.error(f"Error loading qdarktheme stylesheet: {ex}")
            return ""

    @staticmethod
    def palette(theme: ThemeType = ThemeType.AUTO) -> QPalette | None:
        """Return a full qdarktheme palette, or ``None`` if unavailable."""
        if not HAS_QDARKTHEME or not hasattr(qdarktheme, "load_palette"):
            return None
        resolved = ThemeManager.resolve(theme)
        try:
            # for_stylesheet=False fills Base/Button/Window. setup_theme uses
            # True, which leaves those roles as Qt defaults (white on Windows).
            return qdarktheme.load_palette(resolved)
        except Exception as ex:
            log.error(f"Error loading qdarktheme palette: {ex}")
            return None

    @staticmethod
    def css_colors(theme: str | None = None) -> dict[str, str]:
        """Hex colors for QSS. Never use CSS ``palette()`` for fills on Windows."""
        manager = ThemeManager()
        resolved = ThemeManager.resolve(theme or manager._resolved)
        pal = ThemeManager.palette(resolved)
        if pal is None:
            if resolved == ThemeType.LIGHT:
                return {
                    "base": "#ffffff",
                    "button": "#f0f0f0",
                    "window": "#f5f5f5",
                    "text": "#1a1a1a",
                    "mid": "#c0c0c0",
                    "highlight": "#0078d4",
                    "highlighted_text": "#ffffff",
                    "alternate": "#f5f5f5",
                }
            return {
                "base": "#202124",
                "button": "#2d2e30",
                "window": "#202124",
                "text": "#e8eaed",
                "mid": "#5f6368",
                "highlight": "#8ab4f8",
                "highlighted_text": "#202124",
                "alternate": "#292a2d",
            }
        role = QPalette.ColorRole
        return {
            "base": pal.color(role.Base).name(),
            "button": pal.color(role.Button).name(),
            "window": pal.color(role.Window).name(),
            "text": pal.color(role.Text).name(),
            "mid": pal.color(role.Mid).name(),
            "highlight": pal.color(role.Highlight).name(),
            "highlighted_text": pal.color(role.HighlightedText).name(),
            "alternate": pal.color(role.AlternateBase).name(),
        }

    @staticmethod
    def text_widget_stylesheet(
        selector: str = "QTextEdit",
        font_family: str | None = None,
        font_size_pt: int | str | None = None,
        font_bold: bool = False,
    ) -> str:
        """Widget QSS that includes fill colors so Windows does not paint white."""
        c = ThemeManager.css_colors()
        parts = [
            f"background-color: {c['base']}",
            f"color: {c['text']}",
            f"border: 1px solid {c['mid']}",
        ]
        if font_family:
            parts.append(f"font-family: {font_family}")
        if font_size_pt is not None:
            parts.append(f"font-size: {font_size_pt}pt")
        parts.append(f"font-weight: {'bold' if font_bold else 'normal'}")
        return f"{selector} {{ {'; '.join(parts)}; }}"

    @staticmethod
    def apply_theme(
        theme: ThemeType = ThemeType.DARK,
        corner_shape: str = "rounded",
        additional_qss: str | None = None,
        include_custom: bool = True,
    ) -> bool:
        """
        Apply qdarktheme to the application.

        :param theme: ``auto``, ``light``, or ``dark``
        :param corner_shape: qdarktheme corner shape (``rounded`` or ``sharp``)
        :param additional_qss: Extra QSS merged into qdarktheme (overrides include_custom)
        :param include_custom: Include PicoUI custom QSS via qdarktheme ``additional_qss``
        :return: True if a theme was applied
        """
        manager = ThemeManager()
        manager._theme = theme
        manager._corner_shape = corner_shape
        resolved = ThemeManager.resolve(theme)
        manager._resolved = resolved

        if not HAS_QDARKTHEME:
            log.debug("qdarktheme not available, skipping theme application")
            return False

        try:
            app = QApplication.instance()
            if not app:
                log.warning("No QApplication instance found for theme application")
                return False

            manager._custom_applied = False
            propagate = getattr(
                Qt.ApplicationAttribute,
                "AA_UseStyleSheetPropagationInWidgetStyles",
                None,
            )
            if propagate is not None:
                app.setAttribute(propagate, True)
            extra = additional_qss
            if extra is None and include_custom:
                extra = ThemeManager.get_custom_stylesheet()

            # setup_theme() installs QDarkThemeStyle, which on Windows proxies the
            # native style. That style ignores QSS fills for unselected tabs and
            # QGroupBox titles. Fusion + stylesheet + a full palette honors them.
            if hasattr(qdarktheme, "stop_sync"):
                try:
                    qdarktheme.stop_sync()
                except Exception:
                    pass

            fusion = QStyleFactory.create("Fusion")
            app.setStyle(fusion if fusion is not None else "Fusion")

            stylesheet = ThemeManager.stylesheet(resolved, corner_shape=corner_shape)
            if extra:
                stylesheet = (stylesheet or "") + extra
            if stylesheet:
                app.setStyleSheet(stylesheet)
            else:
                log.warning("qdarktheme API not recognized")
                return False

            palette = ThemeManager.palette(resolved)
            if palette is not None:
                app.setPalette(palette)
            manager._custom_applied = bool(extra)
            log.info(f"qdarktheme applied: {theme} (resolved {resolved})")
            return True
        except Exception as ex:
            log.error(f"Error applying qdarktheme: {ex}")
            return False

    @staticmethod
    def apply_style(widget: QWidget, style: str) -> None:
        """Apply a stylesheet string to a widget."""
        if widget:
            widget.setStyleSheet(style)

    @staticmethod
    def apply_table_style(widget: QWidget) -> None:
        """Apply charcoal embossed table styling."""
        table_style = """
            QTableWidget {
                background-color: #1a1a1a;
                border: 1px solid #333333;
                border-radius: 8px;
                gridline-color: #2a2a2a;
                color: #ffffff;
                selection-background-color: #3a3a3a;
                selection-color: #ffffff;
            }

            QTableWidget::item {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2a2a2a,
                    stop:0.5 #252525,
                    stop:1 #1f1f1f);
                border: 1px solid #1a1a1a;
                border-radius: 4px;
                padding: 4px;
                color: #ffffff;
            }

            QTableWidget::item:selected {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3a3a3a,
                    stop:0.5 #353535,
                    stop:1 #2f2f2f);
                border: 1px solid #4a4a4a;
            }

            QTableWidget::item:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #323232,
                    stop:0.5 #2d2d2d,
                    stop:1 #282828);
                border: 1px solid #3a3a3a;
            }

            QHeaderView::section {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2a2a2a,
                    stop:1 #1f1f1f);
                color: #ffffff;
                padding: 6px;
                border: 1px solid #1a1a1a;
                border-radius: 4px;
                font-weight: bold;
            }

            QTableCornerButton::section {
                background-color: #1a1a1a;
                border: 1px solid #333333;
                border-radius: 8px 0 0 0;
            }
        """
        ThemeManager.apply_style(widget, table_style)

    @staticmethod
    def get_custom_stylesheet() -> str:
        """Extras that complement qdarktheme, using hex colors from a full palette."""
        font_family = "Consolas, 'Courier New', monospace"
        c = ThemeManager.css_colors()
        return f"""
        QWidget {{
            font-family: {font_family};
        }}

        QTableView {{
            gridline-color: {c['mid']};
            selection-background-color: {c['highlight']};
            selection-color: {c['highlighted_text']};
            alternate-background-color: {c['alternate']};
            border: 1px solid {c['mid']};
            border-radius: 8px;
            padding: 4px;
        }}

        QHeaderView::section {{
            background-color: {c['button']};
            padding: 8px 12px;
            border: 1px solid {c['mid']};
            border-radius: 6px;
            font-weight: bold;
            margin: 2px;
        }}

        QTableView::item {{
            padding: 4px;
            border-radius: 4px;
        }}

        QTableView::item:selected {{
            background-color: {c['highlight']};
            color: {c['highlighted_text']};
        }}

        QPushButton {{
            min-height: 20px;
            padding: 4px 8px;
            border-radius: 4px;
            border: 1px solid {c['mid']};
            font-weight: 500;
        }}

        QPushButton:hover {{
            border: 1px solid {c['highlight']};
        }}

        QTabWidget::pane {{
            border: 1px solid {c['mid']};
            border-radius: 8px;
            padding: 4px;
            background-color: {c['base']};
        }}

        QTabBar {{
            qproperty-drawBase: 0;
            background-color: transparent;
        }}

        QTabBar::tab {{
            padding: 10px 16px;
            margin-right: 4px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            border: 1px solid {c['mid']};
            border-bottom: none;
            background-color: {c['button']};
            color: {c['text']};
            min-width: 80px;
        }}

        QTabBar::tab:!selected {{
            background-color: {c['button']};
            color: {c['text']};
        }}

        QTabBar::tab:selected {{
            background-color: {c['base']};
            color: {c['text']};
            border-bottom: 2px solid {c['highlight']};
            font-weight: bold;
        }}

        QStatusBar {{
            border-top: 1px solid {c['mid']};
            background-color: {c['window']};
            padding: 4px;
        }}

        QDialog {{
            background-color: {c['window']};
            border-radius: 12px;
        }}

        QDialogButtonBox {{
            spacing: 8px;
            padding: 8px;
        }}

        QLineEdit, QTextEdit, QPlainTextEdit {{
            border: 1px solid {c['mid']};
            border-radius: 6px;
            padding: 6px 10px;
            background-color: {c['base']};
            color: {c['text']};
            selection-background-color: {c['highlight']};
            selection-color: {c['highlighted_text']};
        }}

        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border: 2px solid {c['highlight']};
        }}

        QComboBox {{
            border: 1px solid {c['mid']};
            border-radius: 6px;
            padding: 6px 10px;
            min-height: 20px;
            background-color: {c['button']};
            color: {c['text']};
        }}

        QComboBox:hover {{
            border: 1px solid {c['highlight']};
        }}

        QComboBox::drop-down {{
            border: none;
            border-left: 1px solid {c['mid']};
            border-top-right-radius: 6px;
            border-bottom-right-radius: 6px;
            width: 20px;
        }}

        QComboBox QAbstractItemView {{
            border: 1px solid {c['mid']};
            border-radius: 6px;
            background-color: {c['base']};
            color: {c['text']};
            selection-background-color: {c['highlight']};
            selection-color: {c['highlighted_text']};
            padding: 4px;
        }}

        QCheckBox, QRadioButton {{
            spacing: 8px;
            padding: 4px;
        }}

        QGroupBox {{
            background-color: {c['window']};
            color: {c['text']};
            border: 1px solid {c['mid']};
            border-radius: 8px;
            margin-top: 12px;
            padding-top: 12px;
            font-weight: bold;
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 8px;
            color: {c['text']};
            background-color: {c['window']};
        }}

        QLabel {{
            background-color: transparent;
        }}

        QScrollBar:vertical {{
            border: none;
            background-color: {c['base']};
            width: 12px;
            margin: 0;
            border-radius: 6px;
        }}

        QScrollBar::handle:vertical {{
            background-color: {c['mid']};
            min-height: 30px;
            border-radius: 6px;
            margin: 2px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {c['highlight']};
        }}

        QScrollBar:horizontal {{
            border: none;
            background-color: {c['base']};
            height: 12px;
            margin: 0;
            border-radius: 6px;
        }}

        QScrollBar::handle:horizontal {{
            background-color: {c['mid']};
            min-width: 30px;
            border-radius: 6px;
            margin: 2px;
        }}

        QScrollBar::handle:horizontal:hover {{
            background-color: {c['highlight']};
        }}

        QSpinBox, QDoubleSpinBox {{
            border: 1px solid {c['mid']};
            border-radius: 6px;
            padding: 4px 8px;
            min-height: 24px;
            background-color: {c['base']};
            color: {c['text']};
        }}

        QSpinBox:focus, QDoubleSpinBox:focus {{
            border: 2px solid {c['highlight']};
        }}

        QListWidget, QTreeWidget {{
            border: 1px solid {c['mid']};
            border-radius: 8px;
            padding: 4px;
        }}

        QListWidget::item, QTreeWidget::item {{
            padding: 4px;
            border-radius: 4px;
        }}

        QListWidget::item:selected, QTreeWidget::item:selected {{
            background-color: {c['highlight']};
            color: {c['highlighted_text']};
        }}

        QMenuBar {{
            background-color: {c['window']};
            border-bottom: 1px solid {c['mid']};
            padding: 4px;
            spacing: 8px;
        }}

        QMenuBar::item {{
            padding: 6px 12px;
            border-radius: 4px;
        }}

        QMenuBar::item:selected {{
            background-color: {c['highlight']};
            color: {c['highlighted_text']};
        }}

        QMenu {{
            border: 1px solid {c['mid']};
            border-radius: 6px;
            padding: 4px;
            background-color: {c['window']};
            color: {c['text']};
        }}

        QMenu::item {{
            padding: 6px 24px;
            border-radius: 4px;
        }}

        QMenu::item:selected {{
            background-color: {c['highlight']};
            color: {c['highlighted_text']};
        }}

        QMenu::separator {{
            height: 1px;
            background-color: {c['mid']};
            margin: 4px 8px;
        }}
        """

    @staticmethod
    def apply_custom_stylesheet() -> bool:
        """Re-apply theme with PicoUI custom QSS via qdarktheme additional_qss."""
        manager = ThemeManager()
        if HAS_QDARKTHEME:
            return ThemeManager.apply_theme(
                manager._theme,
                manager._corner_shape,
                include_custom=True,
            )
        try:
            app = QApplication.instance()
            if not app:
                log.warning("No QApplication instance found for stylesheet application")
                return False
            app.setStyleSheet(ThemeManager.get_custom_stylesheet())
            manager._custom_applied = True
            return True
        except Exception as ex:
            log.error(f"Error applying custom stylesheet: {ex}")
            return False

    @staticmethod
    def initialize(
        theme: ThemeType = ThemeType.AUTO,
        apply_custom: bool = True,
        apply_qdarktheme: bool = True,
        corner_shape: str = "rounded",
    ) -> bool:
        """
        Initialize the theme system.

        :param theme: ``auto``, ``light``, or ``dark``
        :param apply_custom: Whether to include PicoUI custom CSS
        :param apply_qdarktheme: Whether to apply qdarktheme
        :param corner_shape: qdarktheme corner shape
        :return: True if requested steps succeeded
        """
        if apply_qdarktheme:
            return ThemeManager.apply_theme(
                theme,
                corner_shape=corner_shape,
                include_custom=apply_custom,
            )
        if apply_custom:
            return ThemeManager.apply_custom_stylesheet()
        return True

    @staticmethod
    def get_progress_bar_style(use_custom_colors: bool = False) -> str:
        """Progress-bar stylesheet; splash screens typically use custom colors."""
        if use_custom_colors:
            return """
            QProgressBar {
                background-color: rgb(82, 64, 157);
                color: #fff;
                border-style: none;
                border-radius: 10px;
                text-align: center;
                height: 50px;
            }

            QProgressBar::chunk {
                border-radius: 10px;
                background: qlineargradient(
                    spread:pad,
                    x1:0, y1:0.711364,
                    x2:1, y2:0.523,
                    stop:0 rgba(0, 0, 199, 255),
                    stop:1 rgba(170, 85, 255, 255)
                );
            }
            """
        return """
            QProgressBar {{
                background-color: {mid};
                color: {text};
                border-style: none;
                border-radius: 10px;
                text-align: center;
                height: 20px;
                min-width: 300px;
            }}

            QProgressBar::chunk {{
                border-radius: 10px;
                background-color: {highlight};
            }}
            """.format(**ThemeManager.css_colors())
