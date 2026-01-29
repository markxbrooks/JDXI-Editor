"""
Centralized theme management for JD-Xi Editor.

Provides a single point of control for applying themes, custom stylesheets,
and ensuring consistent styling across the application.
"""

from typing import Optional

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QApplication, QWidget

from decologr import Decologr as log
from jdxi_editor.ui.style import JDXiUIStyle

# Optional imports for theme detection
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


class ThemeManager(QObject):
    """Centralized theme management for JD-Xi Editor"""

    _instance: Optional["ThemeManager"] = None

    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the ThemeManager"""
        if hasattr(self, "_initialized"):
            return
        super().__init__()
        self._initialized = True

    @staticmethod
    def apply_theme(theme: str = "dark") -> bool:
        """
        Apply qdarktheme to the application (optional).

        :param theme: Theme mode - "auto", "light", or "dark"
        :return: True if theme was applied successfully, False otherwise
        """
        if not HAS_QDARKTHEME:
            log.debug("qdarktheme not available, skipping theme application")
            return False

        try:
            app = QApplication.instance()
            if not app:
                log.warning("No QApplication instance found for theme application")
                return False

            # Resolve "auto" theme to actual theme
            resolved_theme = theme
            if theme == "auto":
                if HAS_DARKDETECT:
                    try:
                        resolved_theme = "dark" if darkdetect.isDark() else "light"
                        log.debug(f"Auto theme detected: {resolved_theme}")
                    except Exception:
                        resolved_theme = "dark"
                        log.warning("Theme detection failed, defaulting to dark")
                else:
                    resolved_theme = "dark"
                    log.debug("darkdetect not available, defaulting to dark")

            # Try new API first (qdarktheme >= 2.0) - accepts "auto"
            if hasattr(qdarktheme, "setup_theme"):
                qdarktheme.setup_theme(theme)  # setup_theme accepts "auto"
                log.info(f"qdarktheme applied: {theme}")
                return True
            # Fallback to old API (qdarktheme < 2.0) - only accepts "dark" or "light"
            elif hasattr(qdarktheme, "load_stylesheet"):
                # load_stylesheet doesn't accept "auto", so use resolved theme
                stylesheet = qdarktheme.load_stylesheet(resolved_theme)
                app.setStyleSheet(stylesheet)
                log.info(f"qdarktheme applied via stylesheet: {resolved_theme}")
                return True
            else:
                log.warning("qdarktheme API not recognized")
                return False

        except Exception as ex:
            log.error(f"Error applying qdarktheme: {ex}")
            return False

    @staticmethod
    def apply_style(widget: QWidget, style: str) -> None:
        """
        Apply a style string to a widget.

        :param widget: QWidget to apply style to
        :param style: str Style sheet string
        """
        if widget:
            widget.setStyleSheet(style)

    @staticmethod
    def apply_editor_title_label(widget: QWidget) -> None:
        """Apply editor title label style"""
        ThemeManager.apply_style(widget, JDXiUIStyle.EDITOR_TITLE_LABEL)

    @staticmethod
    def apply_analog_section_header(widget: QWidget) -> None:
        """Apply analog section header style"""
        ThemeManager.apply_style(widget, JDXiUIStyle.ANALOG_SECTION_HEADER)

    @staticmethod
    def apply_digital_section_header(widget: QWidget) -> None:
        """Apply digital section header style"""
        ThemeManager.apply_style(widget, JDXiUIStyle.DIGITAL_SECTION_HEADER)

    @staticmethod
    def apply_midi_monitor(widget: QWidget) -> None:
        """Apply MIDI message monitor style"""
        ThemeManager.apply_style(widget, JDXiUIStyle.WINDOW_MIDI_MESSAGE_MONITOR)

    @staticmethod
    def apply_status_indicator_active(widget: QWidget, analog: bool = False) -> None:
        """
        Apply active status indicator style

        :param widget: QWidget to style
        :param analog: bool If True, use analog (blue) style, else digital (red)
        """
        if analog:
            ThemeManager.apply_style(widget, JDXiUIStyle.STATUS_INDICATOR_ANALOG_ACTIVE)
        else:
            ThemeManager.apply_style(widget, JDXiUIStyle.STATUS_INDICATOR_ACTIVE)

    @staticmethod
    def apply_status_indicator_inactive(widget: QWidget) -> None:
        """Apply inactive status indicator style"""
        ThemeManager.apply_style(widget, JDXiUIStyle.STATUS_INDICATOR_INACTIVE)

    @staticmethod
    def apply_button_glow_red(widget: QWidget) -> None:
        """Apply red glow button style"""
        ThemeManager.apply_style(widget, JDXiUIStyle.BUTTON_GLOW_RED)

    @staticmethod
    def apply_button_glow_analog(widget: QWidget) -> None:
        """Apply analog (blue) glow button style"""
        ThemeManager.apply_style(widget, JDXiUIStyle.BUTTON_GLOW_ANALOG)

    @staticmethod
    def apply_waveform_button(widget: QWidget, analog: bool = False) -> None:
        """
        Apply waveform button style

        :param widget: QWidget to style
        :param analog: bool If True, use analog style, else digital
        """
        if analog:
            ThemeManager.apply_style(widget, JDXiUIStyle.BUTTON_WAVEFORM_ANALOG)
        else:
            ThemeManager.apply_style(widget, JDXiUIStyle.BUTTON_WAVEFORM)

    @staticmethod
    def apply_instrument_background(widget: QWidget) -> None:
        """Apply instrument background gradient style"""
        ThemeManager.apply_style(widget, JDXiUIStyle.INSTRUMENT)

    @staticmethod
    def apply_table_style(widget: QWidget) -> None:
        """Apply table style with rounded corners and charcoal embossed cells"""
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
            
            QTableWidget::item:focus {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3a3a3a,
                    stop:0.5 #353535,
                    stop:1 #2f2f2f);
                border: 1px solid #ff2200;
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
            
            QHeaderView::section:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #323232,
                    stop:1 #272727);
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
        """
        Get custom application-wide stylesheet additions.

        These styles complement qdarktheme (if available) and provide JD-Xi Editor-specific styling
        with rounded corners, improved spacing, modern aesthetics, and recent styling improvements.

        :return: Additional CSS stylesheet string
        """
        bg_gradient = JDXiUIStyle.BACKGROUND_GRADIENT
        font_family = JDXiUIStyle.FONT_FAMILY
        return f"""
        /* Custom JD-Xi Editor styles with rounded corners and improved spacing */
        QMainWindow {{
            background: {bg_gradient};
        }}
        
        QWidget {{
            font-family: {font_family};
        }}

        /* Tables with rounded corners and better spacing */
        QTableView {{
            gridline-color: palette(mid);
            selection-background-color: palette(highlight);
            selection-color: palette(highlighted-text);
            alternate-background-color: palette(alternate-base);
            border: 1px solid palette(mid);
            border-radius: 8px;
            padding: 4px;
            spacing: 2px;
        }}

        QHeaderView::section {{
            background-color: palette(button);
            padding: 8px 12px;
            border: 1px solid palette(mid);
            border-radius: 6px;
            font-weight: bold;
            margin: 2px;
        }}

        QTableView::item {{
            padding: 4px;
            border-radius: 4px;
        }}

        QTableView::item:selected {{
            background-color: palette(highlight);
            color: palette(highlighted-text);
            border-radius: 4px;
        }}

        QTableView::item:hover {{
            background-color: palette(highlight);
            border-radius: 4px;
            opacity: 0.8;
        }}

        /* Buttons with rounded corners and improved spacing */
        QPushButton {{
            min-height: 20px;
            padding: 4px 8px;
            border-radius: 4px;
            border: 1px solid palette(mid);
            font-weight: 500;
        }}

        QPushButton:hover {{
            background-color: palette(button);
            border: 1px solid palette(highlight);
            opacity: 0.9;
        }}

        QPushButton:pressed {{
            background-color: palette(button);
            border: 1px solid palette(highlight);
            opacity: 0.7;
        }}

        QPushButton:disabled {{
            background-color: palette(button);
            color: palette(mid);
            opacity: 0.5;
        }}

        /* Tabs with rounded corners */
        QTabWidget::pane {{
            border: 1px solid palette(mid);
            border-radius: 8px;
            padding: 4px;
            background-color: palette(base);
        }}

        QTabBar::tab {{
            padding: 10px 16px;
            margin-right: 4px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            border: 1px solid palette(mid);
            border-bottom: none;
            border-radius: 4px 4px 0 0;
            background-color: palette(button);
            min-width: 80px;
        }}

        QTabBar::tab:selected {{
            background-color: palette(base);
            border-bottom: 2px solid palette(highlight);
            font-weight: bold;
            border-radius: 4px 4px 0 0;
        }}

        QTabBar::tab:hover:!selected {{
            background-color: palette(button);
            opacity: 0.95;
        }}

        /* Status bar with rounded top corners */
        QStatusBar {{
            border-top: 1px solid palette(mid);
            background-color: palette(window);
            padding: 4px;
        }}

        QStatusBar::item {{
            border: none;
            padding: 2px 8px;
        }}

        /* Dialogs with rounded corners */
        QDialog {{
            background-color: palette(window);
            border-radius: 12px;
        }}

        QDialogButtonBox {{
            button-layout: 1; /* Windows style */
            spacing: 8px;
            padding: 8px;
        }}

        QDialogButtonBox QPushButton {{
            min-width: 90px;
            padding: 6px 20px;
        }}

        /* Input fields with rounded corners */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            border: 1px solid palette(mid);
            border-radius: 6px;
            padding: 6px 10px;
            background-color: #1a1a1a;
            color: #ffffff;
            selection-background-color: palette(highlight);
            selection-color: palette(highlighted-text);
        }}

        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border: 2px solid palette(highlight);
            border-radius: 6px;
        }}

        /* Combo boxes with rounded corners */
        QComboBox {{
            border: 1px solid palette(mid);
            border-radius: 6px;
            padding: 6px 10px;
            min-height: 20px;
        }}

        QComboBox:hover {{
            border: 1px solid palette(highlight);
        }}

        QComboBox::drop-down {{
            border: none;
            border-left: 1px solid palette(mid);
            border-top-right-radius: 6px;
            border-bottom-right-radius: 6px;
            width: 20px;
        }}

        QComboBox QAbstractItemView {{
            border: 1px solid palette(mid);
            border-radius: 6px;
            selection-background-color: palette(highlight);
            selection-color: palette(highlighted-text);
            padding: 4px;
        }}

        /* Checkboxes and radio buttons */
        QCheckBox, QRadioButton {{
            spacing: 8px;
            padding: 4px;
        }}

        QCheckBox::indicator, QRadioButton::indicator {{
            width: 18px;
            height: 18px;
            border-radius: 4px;
            border: 2px solid palette(mid);
        }}

        QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
            background-color: palette(highlight);
            border-color: palette(highlight);
        }}

        /* Group boxes with rounded corners */
        QGroupBox {{
            border: 1px solid palette(mid);
            border-radius: 8px;
            margin-top: 12px;
            padding-top: 12px;
            font-weight: bold;
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 8px;
            background-color: palette(window);
        }}

        /* Scroll bars with rounded corners */
        QScrollBar:vertical {{
            border: none;
            background-color: palette(base);
            width: 12px;
            margin: 0;
            border-radius: 6px;
        }}

        QScrollBar::handle:vertical {{
            background-color: palette(mid);
            min-height: 30px;
            border-radius: 6px;
            margin: 2px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: palette(highlight);
        }}

        QScrollBar:horizontal {{
            border: none;
            background-color: palette(base);
            height: 12px;
            margin: 0;
            border-radius: 6px;
        }}

        QScrollBar::handle:horizontal {{
            background-color: palette(mid);
            min-width: 30px;
            border-radius: 6px;
            margin: 2px;
        }}

        QScrollBar::handle:horizontal:hover {{
            background-color: palette(highlight);
        }}

        /* Labels */
        QLabel[loading="true"] {{
            color: palette(highlight);
            font-weight: bold;
            padding: 4px;
        }}

        /* Spin boxes with rounded corners */
        QSpinBox, QDoubleSpinBox {{
            border: 1px solid palette(mid);
            border-radius: 6px;
            padding: 4px 8px;
            min-height: 24px;
        }}

        QSpinBox:focus, QDoubleSpinBox:focus {{
            border: 2px solid palette(highlight);
        }}

        /* List widgets with rounded corners */
        QListWidget {{
            border: 1px solid palette(mid);
            border-radius: 8px;
            padding: 4px;
        }}

        QListWidget::item {{
            padding: 6px;
            border-radius: 4px;
            margin: 2px;
        }}

        QListWidget::item:selected {{
            background-color: palette(highlight);
            color: palette(highlighted-text);
        }}

        QListWidget::item:hover {{
            background-color: palette(highlight);
            opacity: 0.85;
        }}

        /* Tree widgets with rounded corners */
        QTreeWidget {{
            border: 1px solid palette(mid);
            border-radius: 8px;
            padding: 4px;
        }}

        QTreeWidget::item {{
            padding: 4px;
            border-radius: 4px;
        }}

        QTreeWidget::item:selected {{
            background-color: palette(highlight);
            color: palette(highlighted-text);
        }}

        QTreeWidget::item:hover {{
            background-color: palette(highlight);
            opacity: 0.85;
        }}

        /* Visual separators */
        QFrame[frameShape="4"] {{  /* HLine */
            max-height: 1px;
            background-color: palette(mid);
            border: none;
            margin: 12px 0;
        }}

        QFrame[frameShape="5"] {{  /* VLine */
            max-width: 1px;
            background-color: palette(mid);
            border: none;
            margin: 0 12px;
        }}

        /* Button variants */
        QPushButton[class="primary"] {{
            background-color: palette(highlight);
            color: palette(highlighted-text);
            font-weight: bold;
            min-height: 27px;
            padding: 7px 15px;
        }}

        QPushButton[class="primary"]:hover {{
            background-color: palette(highlight);
            opacity: 0.9;
        }}

        QPushButton[class="primary"]:pressed {{
            background-color: palette(highlight);
            opacity: 0.7;
        }}

        QPushButton[class="secondary"] {{
            background-color: palette(button);
            color: palette(button-text);
            border: 1px solid palette(mid);
        }}

        QPushButton[class="danger"] {{
            background-color: #f44336;
            color: white;
            border: 1px solid #d32f2f;
        }}

        QPushButton[class="danger"]:hover {{
            background-color: #e53935;
        }}

        /* Typography hierarchy */
        QLabel[class="heading"] {{
            font-size: 16px;
            font-weight: bold;
            color: palette(text);
            margin: 8px 0;
        }}

        QLabel[class="subheading"] {{
            font-size: 14px;
            font-weight: 600;
            color: palette(text);
            margin: 6px 0;
        }}

        QLabel[class="caption"] {{
            font-size: 11px;
            color: palette(mid);
            margin: 4px 0;
        }}

        /* Status badges */
        QLabel[status="success"] {{
            background-color: #4caf50;
            color: white;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
        }}

        QLabel[status="warning"] {{
            background-color: #ff9800;
            color: white;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
        }}

        QLabel[status="error"] {{
            background-color: #f44336;
            color: white;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
        }}

        QLabel[status="info"] {{
            background-color: palette(highlight);
            color: palette(highlighted-text);
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
        }}

        /* Form layouts */
        QFormLayout {{
            spacing: 12px;
        }}

        QFormLayout > QLabel {{
            padding-right: 12px;
            min-width: 120px;
        }}

        QFormLayout > QWidget {{
            min-height: 32px;
        }}

        /* Focus indicators */
        QPushButton:focus,
        QLineEdit:focus,
        QComboBox:focus,
        QSpinBox:focus {{
            outline: 2px solid palette(highlight);
            outline-offset: 2px;
        }}

        /* Menu bar */
        QMenuBar {{
            background-color: palette(window);
            border-bottom: 1px solid palette(mid);
            padding: 4px;
            spacing: 8px;
        }}

        QMenuBar::item {{
            padding: 6px 12px;
            border-radius: 4px;
        }}

        QMenuBar::item:selected {{
            background-color: palette(highlight);
            color: palette(highlighted-text);
        }}

        QMenu {{
            border: 1px solid palette(mid);
            border-radius: 6px;
            padding: 4px;
        }}

        QMenu::item {
            padding: 6px 24px;
            border-radius: 4px;
        }

        QMenu::item:selected {
            background-color: palette(highlight);
            color: palette(highlighted-text);
        }

        QMenu::separator {
            height: 1px;
            background-color: palette(mid);
            margin: 4px 8px;
        }

        /* Enhanced table row alternation */
        QTableView {
            alternate-background-color: palette(alternate-base);
        }

        QTableView::item:alternate {
            background-color: palette(alternate-base);
        }

        QTableView::item:hover {{
            border-left: 3px solid palette(highlight);
        }}
        """.format(
            background_gradient=JDXiUIStyle.BACKGROUND_GRADIENT,
            font_family=JDXiUIStyle.FONT_FAMILY,
        )

    @staticmethod
    def apply_custom_stylesheet() -> bool:
        """
        Apply custom stylesheet to the application.

        :return: True if stylesheet was applied successfully, False otherwise
        """
        try:
            app = QApplication.instance()
            if not app:
                log.warning("No QApplication instance found for stylesheet application")
                return False

            custom_css = ThemeManager.get_custom_stylesheet()
            app_instance = QApplication.instance()
            if not app_instance:
                log.warning("No QApplication instance found for custom stylesheet")
                return False
            current_stylesheet = app_instance.styleSheet()

            # Append custom stylesheet to existing one
            if current_stylesheet:
                app_instance.setStyleSheet(current_stylesheet + custom_css)
            else:
                app_instance.setStyleSheet(custom_css)

            log.info("Custom stylesheet applied")
            return True

        except Exception as ex:
            log.error(f"Error applying custom stylesheet: {ex}")
            return False

    @staticmethod
    def initialize(
        theme: str = "dark", apply_custom: bool = True, apply_qdarktheme: bool = False
    ) -> bool:
        """
        Initialize theme system with optional qdarktheme and custom JD-Xi styles.

        This is the main entry point for theme initialization.

        :param theme: Theme mode - "auto", "light", or "dark" (only used if apply_qdarktheme=True)
        :param apply_custom: Whether to apply custom JD-Xi Editor stylesheet
        :param apply_qdarktheme: Whether to apply qdarktheme (requires qdarktheme package)
        :return: True if initialization was successful, False otherwise
        """
        success = True
        if apply_qdarktheme:
            success = ThemeManager.apply_theme(theme)
        if apply_custom:
            custom_success = ThemeManager.apply_custom_stylesheet()
            success = success and custom_success
        return success

    @staticmethod
    def get_progress_bar_style(use_custom_colors: bool = False) -> str:
        """
        Get progress bar stylesheet.

        :param use_custom_colors: If True, use custom gradient colors (for splash screen).
                                  If False, use theme-aware colors.
        :return: Progress bar CSS stylesheet
        """
        if use_custom_colors:
            # Custom colors for splash screen
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
        else:
            # Theme-aware colors
            return """
            QProgressBar {
                background-color: palette(mid);
                color: palette(text);
                border-style: none;
                border-radius: 10px;
                text-align: center;
                height: 20px;
                min-width: 300px;
            }

            QProgressBar::chunk {
                border-radius: 10px;
                background: qlineargradient(
                    spread:pad,
                    x1:0, y1:0.5,
                    x2:1, y2:0.5,
                    stop:0 palette(highlight),
                    stop:1 palette(highlight)
                );
            }
            """
