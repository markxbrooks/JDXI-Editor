from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import Qt


class Style:
    """Central style definitions for JD-Xi Manager"""

    # Colors
    COM_BG = "#000000"
    TITLE_TEXT = "#FFFFFF"
    BACKGROUND = "#000000"  # """"#1A1A1A"
    FOREGROUND = "#FFFFFF"
    ACCENT = "#FF2200"  # Red accent color
    ACCENT_HOVER = "#FF2200"  # Red for hover
    ANALOG_ACCENT = "#00A0E9"
    ANALOG_ACCENT_HOVER = "#00A0E9"
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
    ANALOG_SYNTH_PART_LABEL_STYLE = f"""
                font-family: "Myriad Pro", Arial;
                font-size: 13px;
                color: {ANALOG_ACCENT};  /* Blue for Analog */
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
            min-height: 400px;  /* Reduced height for horizontal layout */
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
            border: 2px solid {ACCENT_HOVER};
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
        
        QSlider::handle:vertical {{
            background: {SLIDER_HANDLE};
            border: 2px solid {SLIDER_HANDLE_BORDER};
            width: 18px;
            height: 18px;
            margin: -9px 0;
            border-radius: 9px;
        }}
        
        QSlider::handle:vertical:hover {{
            border-color: {ACCENT_HOVER};
        }}
        
        QComboBox::drop-down {{
            border: none;
        }}
        
        QComboBox::down-arrow {{
            image: none;
        }}
    """

    ANALOG_EDITOR_STYLE_V3 = f"""
        QWidget {{
            background-color: {BACKGROUND};
            color: {FOREGROUND};
            font-family: {FONT_FAMILY};
            font-size: {FONT_SIZE};
        }}

        QGroupBox {{
            border: 1px solid {ANALOG_ACCENT};
            border-radius: 3px;
            margin-top: 1.5ex;
            padding: 10px;
        }}

        QGroupBox[adsr="true"] {{
            min-height: 400px;  /* Reduced height for horizontal layout */
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
            border: 1px solid {ANALOG_ACCENT};  /* Red border */
            border-radius: 3px;
            padding: 5px;
            color: {FOREGROUND};
        }}

        QPushButton:hover {{
            background-color: {ANALOG_ACCENT};  /* Red background on hover */
            color: {BACKGROUND};
        }}

        QPushButton:checked {{
            background-color: {ANALOG_ACCENT};  /* Red background when checked */
            color: {BACKGROUND};
        }}

        QComboBox {{
            background-color: {BACKGROUND};
            border: 1px solid {ANALOG_ACCENT};  /* Red border */
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
            border: 2px solid {ANALOG_ACCENT_HOVER};
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
            border-color: {ANALOG_ACCENT_HOVER};
        }}

        QSlider::handle:vertical {{
            background: {SLIDER_HANDLE};
            border: 2px solid {SLIDER_HANDLE_BORDER};
            width: 40px;
            height: 18px;
            margin: -9px 0;
            border-radius: 6px;
        }}

        QSlider::handle:vertical:hover {{
            border-color: {ANALOG_ACCENT};
        }}
        QSlider::tick-mark {{
            background: #ff4500; /* Bright tick marks */
            width: 2px;
            height: 2px;
        }}
        QComboBox::drop-down {{
            border: none;
        }}

        QComboBox::down-arrow {{
            image: none;
        }}

    """

    ANALOG_EDITOR_STYLE_V2 = f"""
        QWidget {{
            background-color: {BACKGROUND};
            color: {FOREGROUND};
            font-family: {FONT_FAMILY};
            font-size: {FONT_SIZE};
        }}

        QGroupBox {{
            border: 1px solid {ANALOG_ACCENT};
            border-radius: 3px;
            margin-top: 1.5ex;
            padding: 10px;
        }}

        QGroupBox[adsr="true"] {{
            min-height: 400px;  /* Reduced height for horizontal layout */
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
            border: 1px solid {ANALOG_ACCENT};  /* Red border */
            border-radius: 3px;
            padding: 5px;
            color: {FOREGROUND};
        }}

        QPushButton:hover {{
            background-color: {ANALOG_ACCENT};  /* Red background on hover */
            color: {BACKGROUND};
        }}

        QPushButton:checked {{
            background-color: {ANALOG_ACCENT};  /* Red background when checked */
            color: {BACKGROUND};
        }}

        QComboBox {{
            background-color: {BACKGROUND};
            border: 1px solid {ANALOG_ACCENT};  /* Red border */
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
            border: 2px solid {ANALOG_ACCENT_HOVER};
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
            border-color: {ANALOG_ACCENT_HOVER};
        }}

        QSlider::handle:vertical {{
            background: {SLIDER_HANDLE};
            border: 2px solid {SLIDER_HANDLE_BORDER};
            width: 18px;
            height: 18px;
            margin: -9px 0;
            border-radius: 9px;
        }}

        QSlider::handle:vertical:hover {{
            border-color: {ANALOG_ACCENT_HOVER};
        }}
        QSlider::groove:vertical {{
            background: {SLIDER_GROOVE};
            width: 6px;
            border-radius: 1px;
        }}

        QComboBox::drop-down {{
            border: none;
        }}

        QComboBox::down-arrow {{
            image: none;
        }}
    """

    ANALOG_EDITOR_STYLE = f"""
        QWidget {{
            background-color: {BACKGROUND};
            color: {FOREGROUND};
            font-family: {FONT_FAMILY};
            font-size: {FONT_SIZE};
        }}

        QGroupBox {{
            border: 1px solid {ANALOG_ACCENT};
            border-radius: 3px;
            margin-top: 1.5ex;
            padding: 10px;
        }}

        QGroupBox[adsr="true"] {{
            min-height: 400px;  /* Reduced height for horizontal layout */
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
            border: 1px solid {ANALOG_ACCENT};  /* Red border */
            border-radius: 3px;
            padding: 5px;
            color: {FOREGROUND};
        }}

        QPushButton:hover {{
            background-color: {ANALOG_ACCENT};  /* Red background on hover */
            color: {BACKGROUND};
        }}

        QPushButton:checked {{
            background-color: {ANALOG_ACCENT};  /* Red background when checked */
            color: {BACKGROUND};
        }}

        QComboBox {{
            background-color: {BACKGROUND};
            border: 1px solid {ANALOG_ACCENT};  /* Red border */
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
            border: 2px solid {ANALOG_ACCENT};
        }}
        QSlider::handle:vertical {{
            background: {SLIDER_HANDLE};
            border: 2px solid {SLIDER_HANDLE_BORDER};
            width: 18px;
            height: 18px;
            margin: -9px 0;
            border-radius: 9px;
        }}
        
        QSlider::handle:vertical:hover {{
            border-color: {ACCENT_HOVER};
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
            border-color: {ANALOG_ACCENT};
        }}

        QComboBox::drop-down {{
            border: none;
        }}

        QComboBox::down-arrow {{
            image: none;
        }}
        QSlider::groove:vertical {{
            background: red;
            width: 6px;
            border-radius: 3px;
        }}
        
        QSlider::handle:vertical {{
            background: gray;
            border: 1px solid darkgray;
            width: 14px;
            height: 14px;
            margin: -6px 0;
            border-radius: 7px;
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

    JDXI_TABS_STYLE = """
            QTabBar::tab {
                background: #000000;       /* Default tab background */
                color: white;           /* Default text color */
                padding: 8px 12px;      /* Padding for tab spacing */
                margin: 2px;
                border: 2px solid #666; /* Default border */
                border-radius: 4px;
                font-family: "Myriad Pro", "sans serif"
            }

            QTabBar::tab:selected {
                background: #222222;    /* Selected tab background */
                color: white;           /* Selected text color */
                border: 2px solid #ff6666; /* Border for selected tab */
                font-family: "Myriad Pro", "sans serif"
            }

            QTabBar::tab:hover {
                background: #222222;       /* Hover effect */
                border: 2px solid #ff9999;
                font-family: "Myriad Pro", "sans serif"
            }
        """

    JDXI_ANALOG_TABS_STYLE = """
            QTabBar::tab {
                background: #000000;       /* Default tab background */
                color: white;           /* Default text color */
                padding: 8px 12px;      /* Padding for tab spacing */
                margin: 2px;
                border: 2px solid #666; /* Default border */
                border-radius: 4px;
                font-family: "Myriad Pro", "sans serif"
            }

            QTabBar::tab:selected {
                background: #222222;    /* Selected tab background */
                color: white;           /* Selected text color */
                border: 2px solid #00A0E9; /* Border for selected tab */
                font-family: "Myriad Pro", "sans serif"
            }

            QTabBar::tab:hover {
                background: #00A0C1;       /* Hover effect */
                border: 2px solid #00A0E9;
                font-family: "Myriad Pro", "sans serif"
            }
            QTabWidget::pane {
                border: 1px solid #00A0E9;
            }
        """

    JDXI_DRUM_TABS_STYLE = """
            QTabBar::tab {
                background: #000000;       /* Default tab background */
                color: white;           /* Default text color */
                padding: 3px 3px;      /* Padding for tab spacing */
                margin: 1px;
                border: 1px solid #666; /* Default border */
                border-radius: 4px;
                font-family: "Myriad Pro", "sans serif";
                font-size: "8pt"
            }

            QTabBar::tab:selected {
                background: #222222;    /* Selected tab background */
                color: white;           /* Selected text color */
                border: 2px solid #ff6666; /* Border for selected tab */
                font-family: "Myriad Pro", "sans serif";
                font-size: "8pt"
            }

            QTabBar::tab:hover {
                background: #222222;       /* Hover effect */
                border: 2px solid #ff9999;
                font-family: "Myriad Pro", "sans serif";
                font-size: "8pt"
            }
        """
    ADSR_STYLE = """
    QSlider::groove:vertical {
        background: #1A1A1A; /* Dark background */
        width: 6px; /* Thin groove */
        border-radius: 3px;
    }

    QSlider::handle:vertical {
        background: black;
        border: 2px solid #ff4500; /* Bright red/orange border */
        width: 40px;  /* Wider handle */
        height: 10px;  /* Shorter handle */
        margin: -2p x -5px; /* Centers the handle */
        border-radius: 2px;
    }

    QSlider::sub-page:vertical {
        background: rgba(255, 69, 0, 0.5); /* Glowing effect on filled portion */
        border-radius: 3px;
    }

    QSlider::add-page:vertical {
        background: #333333; /* Unfilled portion */
        border-radius: 3px;
    }

    QSlider::tick-mark {
        background: #ff4500; /* Bright tick marks */
        width: 2px;
        height: 2px;
    }
"""
    ADSR_STYLE_old = """
          QSlider:vertical {
              background: #333; /* Background of the slider */
              width: 30px; /* Width of the fader */
              border: 1px solid #FF6D00; /* External border color */
              border-radius: 5px; /* Rounded edges */
          }
          QSlider::handle:vertical {
              background: #FF6D00; /* Color of the fader handle */
              width: 20px; /* Width of the handle */
              border-radius: 5px; /* Rounded edges */
          }
          QSlider::handle:vertical:hover {
              background: #FF8C00; /* Color on hover */
          }
          QSlider::groove:vertical {
              background: #666; /* Color of the groove */
              width: 10px; /* Width of the groove */
          }
          QSlider::sub-page:vertical {
              background: #FF3D00; /* Color of the filled area */
          }
          QSlider::add-page:vertical {
              background: #333; /* Color of the unfilled area */
          }
          QSlider::tick:vertical {
              background: #FF6D00; /* Color of the tick marks */
              width: 2px; /* Width of the tick marks */
              margin-left: -5px; /* Positioning ticks */
          }
          QSlider::tick-mark:vertical {
              width: 3px;
              height: 3px;
              color: #FF6D00; /* Color of the tick marks */
          }"""

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

    # Default and active styles
    BUTTON_DEFAULT = """
         QPushButton {
             background: #000000;       /* Default tab background */
             color: #AAAAAA;           /* Default text color */
             padding: 8px 12px;      /* Padding for tab spacing */
             margin: 2px;
             border: 2px solid #666; /* Default border */
             border-radius: 4px;
             font-family: "Myriad Pro", "sans serif"
         }
         QPushButton:hover {
             background-color: #1A1A1A;
             border: 2px solid #ff4d4d;
         }
         QPushButton:pressed {
             background-color: #333333;
             border: 2px solid #ff6666;
         }
     """

    BUTTON_ACTIVE = """
         QPushButton {
             color: white;
             background-color: #222222;
             border: 2px solid #ff4d4d;
             border-radius: 4px;
             padding: 8px 12px;      /* Padding for tab spacing */
         }
         QPushButton:hover {
             background-color: #ff8080;
             border: 2px solid #ff9999;
         }
         QPushButton:pressed {
             background-color: #ff4d4d;
             border: 2px solid #ff3333;
         }
     """

    # Default and active styles
    ANALOG_BUTTON_DEFAULT = """
         QPushButton {
             background: #000000;       /* Default tab background */
             color: #AAAAAA;           /* Default text color */
             padding: 8px 12px;      /* Padding for tab spacing */
             margin: 2px;
             border: 2px solid #666; /* Default border */
             border-radius: 4px;
             font-family: "Myriad Pro", "sans serif"
         }
         QPushButton:hover {
             background-color: #1A1A1A;
             border: 2px solid #00A0E9;
         }
         QPushButton:pressed {
             background-color: #333333;
             border: 2px solid #00A0E9;
         }
     """

    ANALOG_BUTTON_ACTIVE = """
         QPushButton {
             color: white;
             background-color: #222222;
             border: 2px solid #00A0E9;
             border-radius: 4px;
             padding: 8px 12px;      /* Padding for tab spacing */
         }
         QPushButton:hover {
             background-color: #00A0C1;
             border: 2px solid #00A0E9;
         }
         QPushButton:pressed {
             background-color: #ff4d4d;
             border: 2px solid #00A0E9;
         }
     """

    ANALOG_BUTTON = """
            QPushButton {
                background-color: #222222;
                color: #CCCCCC;
                border: 1px solid #666666;
                border-radius: 3px;
                padding: 5px;
            }
            QPushButton:checked {
                background-color: #333333;
                color: white;
                border: 1px solid #00A0E9;
            }
            QPushButton:hover {
                background-color: #444444;
            }
        """


def sequencer_button_style(active):
    return f"""
        QPushButton {{
            border: 4px solid {'#ff6666' if active else '#666666'};
            background-color: {'#333333' if active else 'black'};
            border-radius: 3px;
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
    """


def toggle_button_style(button, checked):
    """Update button style based on its checked state"""
    button.setStyleSheet(sequencer_button_style(checked))  # Example style for checked


def update_button_style(button, checked):
    """Toggle the button style based on the state"""
    button.setStyleSheet(get_button_styles(checked))


def get_button_styles(active):
    """Returns the appropriate style for active/inactive states"""
    if active:
        return """
            QPushButton {
                background-color: #333333;
                border: 4px solid #ff6666;
                border-radius: 15px;
            }
        """
    else:
        return """
            QPushButton {
                background-color: #222222;
                border: 4px solid #666666;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #1A1A1A;
                border: 4px solid #ff4d4d;
            }
            QPushButton:pressed {
                background-color: #333333;
                border: 4px solid #ff6666;
            }
        """
