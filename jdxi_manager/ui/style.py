from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import Qt

class Style:
    """Central style definitions for JD-Xi Manager"""
    
    # Colors
    BACKGROUND = "#1A1A1A"
    FOREGROUND = "#FFFFFF"
    ACCENT = "#FF0000"
    ACCENT_HOVER = "#FF0000"  # Red for hover
    BORDER = "#333333"
    SLIDER_HANDLE = "#000000"  # Black fill
    SLIDER_HANDLE_BORDER = "#666666"  # Light grey outline
    SLIDER_GROOVE = "#FF0000"  # Red groove
    
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
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 3px;
            background-color: {BACKGROUND};
            color: {ACCENT};
        }}
        
        QLabel {{
            color: {FOREGROUND};
        }}
        
        QSlider::groove:vertical {{
            background: {SLIDER_GROOVE};
            width: {GROOVE_WIDTH};
        }}
        
        QSlider::handle {{
            background: {SLIDER_HANDLE};
            border: 2px solid {SLIDER_HANDLE_BORDER};
            width: {HANDLE_SIZE};
            height: {HANDLE_SIZE};
            margin: -4px -4px;
            border-radius: 4px;  /* Half of width+border for circle */
        }}
        
        QSlider::handle:hover {{
            border-color: {ACCENT_HOVER};
        }}
        
        QComboBox {{
            background-color: {BACKGROUND};
            border: 1px solid {ACCENT};
            border-radius: 3px;
            padding: 3px;
            color: {FOREGROUND};
        }}
        
        QComboBox::drop-down {{
            border: none;
        }}
        
        QComboBox::down-arrow {{
            image: none;
        }}
        
        QScrollBar {{
            background: {BACKGROUND};
            border: 1px solid {BORDER};
        }}
        
        QScrollBar::handle {{
            background: {ACCENT};
            border-radius: 3px;
        }}
    """ 