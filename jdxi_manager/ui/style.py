from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import Qt

class Style:
    """Application style constants"""
    
    # Colors
    RED = "#FF0000"
    GREEN = "#00FF00"
    BLUE = "#0000FF"
    ORANGE = "#FFA500"
    YELLOW = "#FFFF00"
    WHITE = "#FFFFFF"
    BLACK = "#000000"
    
    # Background colors
    DARK_BG = "#1E1E1E"
    LIGHT_BG = "#2D2D2D"
    
    # Section background colors
    COM_BG = "#2A2A2A"  # Common section
    OSC_BG = "#2D2D2D"  # Oscillator section
    VCF_BG = "#303030"  # Filter section
    AMP_BG = "#333333"  # Amplifier section
    MOD_BG = "#363636"  # Modulation section
    ARP_BG = "#2A2A2A"  # Arpeggiator section
    
    # Theme definitions
    DARK_THEME = f"""
        QMainWindow, QDialog {{
            background-color: {DARK_BG};
            color: {WHITE};
        }}
        QWidget {{
            background-color: {DARK_BG};
            color: {WHITE};
        }}
        QPushButton {{
            background-color: {LIGHT_BG};
            color: {WHITE};
            border: 1px solid {WHITE};
            border-radius: 3px;
            padding: 5px;
            min-width: 80px;
        }}
        QPushButton:hover {{
            background-color: {BLUE};
        }}
        QPushButton:pressed {{
            background-color: {DARK_BG};
        }}
        QComboBox {{
            background-color: {LIGHT_BG};
            color: {WHITE};
            border: 1px solid {WHITE};
            border-radius: 3px;
            padding: 5px;
        }}
        QGroupBox {{
            border: 1px solid {WHITE};
            margin-top: 0.5em;
            padding-top: 0.5em;
        }}
    """
    
    # Specific component styles
    ARP_STYLE = f"""
        QWidget {{
            background-color: {ARP_BG};
            color: {WHITE};
        }}
        QPushButton {{
            background-color: {LIGHT_BG};
            color: {WHITE};
            border: 1px solid {ORANGE};
            border-radius: 3px;
            padding: 5px;
        }}
        QPushButton:checked {{
            background-color: {ORANGE};
            color: {BLACK};
        }}
        QLabel {{
            color: {ORANGE};
        }}
    """ 