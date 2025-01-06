from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import Qt

class Style:
    # Colors
    BACKGROUND = "#3C3C3C"
    DIVIDER = "#232323"
    FONT_COLOR = "#FFFFFF"
    BUTTON_COLOR = "#303030"
    BUTTON_SELECTED = "#2897B7"
    BUTTON_DISABLED = "#545454"
    
    # Title strip colors
    OSC_BG = "#FFA200"  # Orange
    VCF_BG = "#E83939"  # Red
    AMP_BG = "#AF7200"  # Brown
    COM_BG = "#3A464E"  # Gray
    CFG_BG = "#3C3C3C"  # Dark Gray
    LFO_BG = "#E86333"  # Orange-Red
    
    # Fonts
    STANDARD_FONT = QFont("Sans", 10)
    SMALL_FONT = QFont("Sans", 8)
    SMALL_BOLD_FONT = QFont("Sans", 8, QFont.Bold)
    MIDI_CONFIG_FONT = QFont("Sans", 9)
    PATCH_NAME_FONT = QFont("Fixed", 10)
    BUTTON_FONT = QFont("Sans", 9, QFont.Bold)
    
    # Dimensions
    DIVIDER_WIDTH = 1
    PADDING_Y = 5
    BUTTON_PADDING_X = 6
    BUTTON_PADDING_Y = 3
    
    @classmethod
    def apply_to_widget(cls, widget):
        """Apply default style to a widget"""
        widget.setFont(cls.STANDARD_FONT)
        widget.setStyleSheet(f"""
            QWidget {{
                background-color: {cls.BACKGROUND};
                color: {cls.FONT_COLOR};
            }}
            QPushButton {{
                background-color: {cls.BUTTON_COLOR};
                color: {cls.BUTTON_SELECTED};
                border: none;
                padding: {cls.BUTTON_PADDING_Y}px {cls.BUTTON_PADDING_X}px;
                font: {cls.BUTTON_FONT.toString()};
            }}
            QPushButton:disabled {{
                color: {cls.BUTTON_DISABLED};
            }}
            QFrame {{
                border: {cls.DIVIDER_WIDTH}px solid {cls.DIVIDER};
            }}
        """) 