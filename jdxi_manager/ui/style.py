from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import Qt

class Style:
    """Style constants and common stylesheets for UI"""
    
    # Main application stylesheet
    MAIN_STYLESHEET = """
        QMainWindow, QWidget {
            background-color: black;
            color: red;
            font-family: "Myriad Pro"
        }
        QMenuBar {
            background-color: black;
            color: white;
        }
        QMenuBar::item:selected {
            background-color: #333333;
        }
        QMenu {
            background-color: black;
            color: white;
        }
        QMenu::item:selected {
            background-color: #333333;
        }
        QGroupBox {
            border: 1px solid #333333;
        }
        QLabel {
            background-color: transparent;
        }
        QStatusBar {
            background-color: black;
            color: white;
        }
        QPushButton {
            background-color: #3c3c3c;
            color: #ffffff;
            border: 1px solid #4c4c4c;
            border-radius: 3px;
            padding: 5px;
            min-width: 80px;
        }
        QPushButton:hover {
            background-color: #4c4c4c;
        }
        QPushButton:pressed {
            background-color: #2b2b2b;
        }
        QComboBox {
            background-color: #3c3c3c;
            color: #ffffff;
            border: 1px solid #4c4c4c;
            border-radius: 3px;
            padding: 5px;
        }
        QScrollArea {
            border: none;
        }
        QFrame {
            border: 1px solid #333333;
            border-radius: 4px;
        }
        QSlider::groove:horizontal {
            border: 1px solid #4c4c4c;
            height: 8px;
            background: #2b2b2b;
            margin: 2px 0;
            border-radius: 4px;
        }
        QSlider::handle:horizontal {
            background: #4c4c4c;
            border: 1px solid #5c5c5c;
            width: 18px;
            margin: -2px 0;
            border-radius: 3px;
        }
        QTabWidget::pane {
            border: 1px solid #333333;
        }
        QTabBar::tab {
            background: #2b2b2b;
            color: white;
            padding: 5px;
            border: 1px solid #333333;
        }
        QTabBar::tab:selected {
            background: #3c3c3c;
        }
        QCheckBox {
            color: white;
        }
        QCheckBox::indicator {
            width: 13px;
            height: 13px;
        }
        QCheckBox::indicator:unchecked {
            border: 1px solid #4c4c4c;
            background: #2b2b2b;
        }
        QCheckBox::indicator:checked {
            border: 1px solid #4c4c4c;
            background: #5c5c5c;
        }
    """

    # Colors
    DARK_BG = "#1E1E1E"
    LIGHT_BG = "#2D2D2D"
    
    # Section colors
    HEADER_BG = "#3c3c3c"
    OSC_BG = "#4a4a4a"
    VCF_BG = "#5a5a5a"
    VCA_BG = "#6a6a6a"
    LFO_BG = "#7a7a7a"
    MIX_BG = "#8a8a8a"
    PITCH_ENV_BG = "#9a9a9a"
    VCF_ENV_BG = "#aaaaaa"
    VCA_ENV_BG = "#bbbbbb"
    
    # Editor section colors
    DRUM_PAD_BG = "#4a4a4a"
    PATTERN_BG = "#5a5a5a"
    FX_BG = "#6a6a6a"
    COMMON_BG = "#7a7a7a"
    
    # Additional section colors
    COM_BG = "#2A2A2A"  # Common section
    MOD_BG = "#363636"  # Modulation section
    ARP_BG = "#2A2A2A"  # Arpeggiator section 