from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import Qt


class Style:
    """Central style definitions for JD-Xi Manager"""

    # Colors
    COM_BG = "#000000"
    TITLE_TEXT = "#FFFFFF"
    BACKGROUND = "#000000"  # """"#1A1A1A"
    FOREGROUND = "#FFFFFF"
    ACCENT = "#FF0000"  # Red accent color
    ACCENT_HOVER = "#FF0000"  # Red for hover
    BORDER = "#333333"
    SLIDER_HANDLE = "#000000"  # Black fill
    SLIDER_HANDLE_BORDER = "#666666"  # Light grey outline
    SLIDER_GROOVE = "#666666"  # grey groove

    ICON_SIZE = 20  # Size of icons in Editor Group boxes
    # Dimensions
    HANDLE_SIZE = "6px"  # Circle diameter
    GROOVE_WIDTH = "2px"  # Groove thickness

    # Fonts
    FONT_FAMILY = "Myriad Pro, Arial, sans-serif"
    FONT_SIZE = "12px"

    # Common style sheet for all buttons
    BUTTON_STYLE = f"""
            QPushButton {{
                background-color: black;
                border: 4px solid #666666;
                border-radius: 15px;
                padding: 0px;
            }}
            QPushButton:hover {{
                background-color: #1A1A1A;
                border-color: #ff4d4d;
            }}
            QPushButton:pressed {{
                background-color: #333333;
                border-color: #ff6666;
            }}
            QPushButton:checked {{
                background-color: black;
                border: 4px solid #d51e35;
                border-radius: 15px;
                padding: 0px;
            }}
        """
    SYNTH_PART_LABEL_STYLE = """
                font-family: "Myriad Pro", Arial;
                font-size: 13px;
                color: #d51e35;  /* Base red */
                font-weight: bold;
            """
    ANALOG_SYNTH_PART_LABEL_STYLE = """
                font-family: "Myriad Pro", Arial;
                font-size: 13px;
                color: #00A0E9;  /* Blue for Analog */
                font-weight: bold;
            """
    TONE_BUTTON_STYLE = f"""
            QPushButton {{
                background-color: #333333;  /* Dark grey */
                border-radius: 12px;  /* Half of the diameter for circular shape */
                color: white;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #444444;  /* Slightly lighter grey on hover */
            }}
            QPushButton:pressed {{
                background-color: #555555;  /* Even lighter grey when pressed */
            }}
        """
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
    DRUMS_STYLE = """
            QMainWindow {
                background-color: #2E2E2E;
                color: #FFFFFF;
            }
            QLabel {
                color: #FFFFFF;
                font-family: 'Myriad Pro';
            }
            QComboBox {
                background-color: #3D3D3D;
                color: #FFFFFF;
                border: 1px solid #555555;
                padding: 5px;
                font-family: 'Myriad Pro';
            }
            QComboBox:hover {
                border: 1px solid #777777;
            }
            QPushButton {
                background-color: #3D3D3D;
                color: #FFFFFF;
                border: 1px solid #555555;
                padding: 5px 15px;
                font-family: 'Myriad Pro';
            }
            QPushButton:hover {
                background-color: #4D4D4D;
                border: 1px solid #777777;
            }
            QLineEdit {
                background-color: #3D3D3D;
                color: #FFFFFF;
                border: 1px solid #555555;
                padding: 5px;
                font-family: 'Myriad Pro';
            }
            QFrame {
                border-radius: 3px;
                margin-top: 0.5em;
                color: #FFFFFF;
                font-family: 'Myriad Pro';
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
        """

    JDXI_STYLE = """
            QMainWindow {
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
        """
