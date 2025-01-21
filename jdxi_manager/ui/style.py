from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import Qt

class Style:
    """Central style definitions for JD-Xi Manager"""
    
    # Colors
    COM_BG = "#000000"
    TITLE_TEXT = "#FFFFFF"
    BACKGROUND = "#000000" # """"#1A1A1A"
    FOREGROUND = "#FFFFFF"
    ACCENT = "#FF0000"  # Red accent color
    ACCENT_HOVER = "#FF0000"  # Red for hover
    BORDER = "#333333"
    SLIDER_HANDLE = "#000000"  # Black fill
    SLIDER_HANDLE_BORDER = "#666666"  # Light grey outline
    SLIDER_GROOVE = "#666666"  # grey groove

    ICON_SIZE = 20 # Size of icons in Editor Group boxes
    # Dimensions
    HANDLE_SIZE = "6px"       # Circle diameter
    GROOVE_WIDTH = "2px"      # Groove thickness
    
    # Fonts
    FONT_FAMILY = "Myriad Pro, Arial, sans-serif"
    FONT_SIZE = "12px"
    
    # Common style sheet for all editors
    EDITOR_STYLE = f"""
        QWidget {{
            background-color: {BACKGROUND};
            color: {FOREGROUND};
            font-family: {FONT_FAMILY};
            font-size: {FONT_SIZE};
        }}
        
        QGroupBox {{
            border: 1px solid {ACCENT};
            border-radius: 3px;
            margin-top: 1.5ex;
            padding: 10px;
        }}
        
        QGroupBox[adsr="true"] {{
            min-height: 120px;  /* Reduced height for horizontal layout */
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 3px;
            background-color: {BACKGROUND};
            color: {TITLE_TEXT};  /* Red text */
        }}
        
        QPushButton {{
            background-color: {BACKGROUND};
            border: 1px solid {ACCENT};  /* Red border */
            border-radius: 3px;
            padding: 5px;
            color: {FOREGROUND};
        }}
        
        QPushButton:hover {{
            background-color: {ACCENT};  /* Red background on hover */
            color: {BACKGROUND};
        }}
        
        QPushButton:checked {{
            background-color: {ACCENT};  /* Red background when checked */
            color: {BACKGROUND};
        }}
        
        QComboBox {{
            background-color: {BACKGROUND};
            border: 1px solid {ACCENT};  /* Red border */
            border-radius: 3px;
            padding: 3px;
            color: {FOREGROUND};
        }}
        
        QScrollBar {{
            background: {BACKGROUND};
            border: 1px solid {BORDER};
        }}
        
        QScrollBar::handle {{
            background: {SLIDER_HANDLE_BORDER};  /* Grey scrollbar handle */
            border-radius: 3px;
        }}
        
        QScrollBar::handle:hover {{
            background: {ACCENT_HOVER};
        }}
        
        QLabel {{
            color: {FOREGROUND};
        }}
        
        QSlider::groove:horizontal {{
            background: {SLIDER_GROOVE};
            height: {GROOVE_WIDTH};
            border-radius: 1px;
        }}
        
        QSlider::handle:horizontal {{
            background: {SLIDER_HANDLE};
            border: 2px solid {SLIDER_HANDLE_BORDER};
            width: 18px;
            height: 18px;
            margin: -9px 0;
            border-radius: 9px;
        }}
        
        QSlider::handle:horizontal:hover {{
            border-color: {ACCENT_HOVER};
        }}
        
        QComboBox::drop-down {{
            border: none;
        }}
        
        QComboBox::down-arrow {{
            image: none;
        }}
    """ 