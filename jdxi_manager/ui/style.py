from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import Qt

class Style:
    # Colors
    BACKGROUND = "black"
    TEXT = "white"
    MENU_HOVER = "#333333"
    BORDER = "#333333"
    RED = "#d51e35"
    BLUE = "#00A0E9"
    ORANGE = "#FF8C00"

    # Section colors
    OSC_BG = "#FFA200"  # Orange
    VCF_BG = "#E83939"  # Red
    AMP_BG = "#AF7200"  # Brown
    LFO_BG = "#E86333"  # Orange-Red
    MOD_BG = "#B75628"  # Dark Orange
    COM_BG = "#3A464E"  # Gray
    ARP_BG = "#E86333"  # Orange-Red
    
    # Effects colors
    FX1_BG = "#FF8C00"   # Dark Orange
    FX2_BG = "#FF4500"   # Orange-Red
    REVERB_BG = "#E83939" # Red
    DELAY_BG = "#FF6347"  # Tomato
    CHORUS_BG = "#DC143C" # Crimson
    MASTER_BG = "#8B0000" # Dark Red

    # Common styles
    DARK_THEME = """
        QMainWindow, QDialog {
            background-color: black;
        }
        QWidget {
            background-color: black;
            color: white;
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
        QScrollArea {
            background-color: black;
        }
        QScrollBar {
            background-color: black;
            border: 1px solid #333333;
        }
        QFrame {
            background-color: black;
            color: white;
        }
        QPushButton {
            background-color: black;
            color: white;
            border: 1px solid #333333;
        }
        QComboBox {
            background-color: black;
            color: white;
            border: 1px solid #333333;
            padding: 4px 8px;
            text-align: left;
        }
        QComboBox::drop-down {
            border: none;
            padding-right: 8px;
        }
        QComboBox::down-arrow {
            image: none;
        }
        QComboBox QAbstractItemView {
            background-color: black;
            color: white;
            border: 1px solid #333333;
            selection-background-color: #333333;
        }
        QComboBox QAbstractItemView::item {
            padding: 4px 8px;
            text-align: left;
            min-height: 24px;
        }
        QComboBox::item:selected {
            background-color: #333333;
            color: white;
            text-align: left;
        }
        QComboBox::indicator {
            left: 4px;
        }
        QSlider {
            background-color: black;
        }
        QSlider::groove:horizontal {
            background-color: #d51e35;
            height: 2px;
        }
        QSlider::handle:horizontal {
            background-color: white;
            width: 12px;
            margin: -5px 0;
            border-radius: 6px;
        }
        QSlider::sub-page:horizontal {
            background-color: #d51e35;
        }
    """ 