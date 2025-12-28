"""
Centralized theme management for JD-Xi Editor.

Provides a single point of control for applying themes, custom stylesheets,
and ensuring consistent styling across the application.
"""

from typing import Optional
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import QObject

from jdxi_editor.jdxi.style import JDXiStyle
from jdxi_editor.log.logger import Logger as log


class JDXiThemeManager(QObject):
    """Centralized theme management for JD-Xi Editor"""
    
    _instance: Optional['JDXiThemeManager'] = None
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the ThemeManager"""
        if hasattr(self, '_initialized'):
            return
        super().__init__()
        self._initialized = True
    
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
        JDXiThemeManager.apply_style(widget, JDXiStyle.EDITOR_TITLE_LABEL)
    
    @staticmethod
    def apply_analog_section_header(widget: QWidget) -> None:
        """Apply analog section header style"""
        JDXiThemeManager.apply_style(widget, JDXiStyle.ANALOG_SECTION_HEADER)
    
    @staticmethod
    def apply_digital_section_header(widget: QWidget) -> None:
        """Apply digital section header style"""
        JDXiThemeManager.apply_style(widget, JDXiStyle.DIGITAL_SECTION_HEADER)
    
    @staticmethod
    def apply_midi_monitor(widget: QWidget) -> None:
        """Apply MIDI message monitor style"""
        JDXiThemeManager.apply_style(widget, JDXiStyle.MIDI_MESSAGE_MONITOR)
    
    @staticmethod
    def apply_status_indicator_active(widget: QWidget, analog: bool = False) -> None:
        """
        Apply active status indicator style
        
        :param widget: QWidget to style
        :param analog: bool If True, use analog (blue) style, else digital (red)
        """
        if analog:
            JDXiThemeManager.apply_style(widget, JDXiStyle.STATUS_INDICATOR_ANALOG_ACTIVE)
        else:
            JDXiThemeManager.apply_style(widget, JDXiStyle.STATUS_INDICATOR_ACTIVE)
    
    @staticmethod
    def apply_status_indicator_inactive(widget: QWidget) -> None:
        """Apply inactive status indicator style"""
        JDXiThemeManager.apply_style(widget, JDXiStyle.STATUS_INDICATOR_INACTIVE)
    
    @staticmethod
    def apply_button_glow_red(widget: QWidget) -> None:
        """Apply red glow button style"""
        JDXiThemeManager.apply_style(widget, JDXiStyle.BUTTON_GLOW_RED)
    
    @staticmethod
    def apply_button_glow_analog(widget: QWidget) -> None:
        """Apply analog (blue) glow button style"""
        JDXiThemeManager.apply_style(widget, JDXiStyle.BUTTON_GLOW_ANALOG)
    
    @staticmethod
    def apply_waveform_button(widget: QWidget, analog: bool = False) -> None:
        """
        Apply waveform button style
        
        :param widget: QWidget to style
        :param analog: bool If True, use analog style, else digital
        """
        if analog:
            JDXiThemeManager.apply_style(widget, JDXiStyle.BUTTON_WAVEFORM_ANALOG)
        else:
            JDXiThemeManager.apply_style(widget, JDXiStyle.BUTTON_WAVEFORM)
    
    @staticmethod
    def apply_instrument_background(widget: QWidget) -> None:
        """Apply instrument background gradient style"""
        JDXiThemeManager.apply_style(widget, JDXiStyle.INSTRUMENT)
    
    @staticmethod
    def apply_table_style(widget: QWidget) -> None:
        """Apply table style with rounded corners and charcoal embossed cells"""
        # This uses the style from program.py's _get_table_style method
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
        JDXiThemeManager.apply_style(widget, table_style)
    
    @staticmethod
    def get_application_style() -> str:
        """
        Get the complete application-wide stylesheet.
        
        This combines all the recent styling improvements into a single stylesheet
        that can be applied to the QApplication instance.
        
        :return: str Complete stylesheet string
        """
        return f"""
            /* Application-wide background gradient */
            QMainWindow {{
                background: {JDXiStyle.BACKGROUND_GRADIENT};
            }}
            
            QWidget {{
                font-family: {JDXiStyle.FONT_FAMILY};
            }}
            
            /* Enhanced button glow effects */
            QPushButton:hover {{
                border: 2px solid {JDXiStyle.ACCENT_GLOW};
            }}
            
            /* Enhanced slider gradients */
            QSlider::sub-page:vertical {{
                background: {JDXiStyle.SLIDER_NEON_GRADIENT};
            }}
            
            QSlider::sub-page:horizontal {{
                background: {JDXiStyle.SLIDER_NEON_GRADIENT};
            }}
        """
    
    @staticmethod
    def apply_application_style() -> bool:
        """
        Apply the complete application-wide stylesheet to the QApplication instance.
        
        :return: bool True if successful, False otherwise
        """
        try:
            app = QApplication.instance()
            if not app:
                log.warning("No QApplication instance found for theme application")
                return False
            
            app_style = JDXiThemeManager.get_application_style()
            current_style = app.styleSheet()
            
            # Append to existing stylesheet if present
            if current_style:
                app.setStyleSheet(current_style + app_style)
            else:
                app.setStyleSheet(app_style)
            
            log.info("JD-Xi application theme applied successfully")
            return True
            
        except Exception as ex:
            log.error(f"Error applying application theme: {ex}")
            return False
    
    @staticmethod
    def initialize() -> bool:
        """
        Initialize the theme system.
        
        This is the main entry point for theme initialization.
        
        :return: bool True if initialization was successful, False otherwise
        """
        return JDXiThemeManager.apply_application_style()


# Convenience instance getter
def get_theme_manager() -> JDXiThemeManager:
    """Get the singleton ThemeManager instance"""
    return JDXiThemeManager()
