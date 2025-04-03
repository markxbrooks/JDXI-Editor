"""
This module defines the `Style` class, which centralizes all style configurations
for the JD-Xi Manager application. It includes color definitions, dimensions, fonts,
and styles for buttons, sliders, tabs, labels, and other UI elements.

Attributes:
    Colors:
        TITLE_TEXT (str): Color for title text.
        BACKGROUND (str): Main background color.
        BACKGROUND_PRESSED (str): Background color when a button is pressed.
        BUTTON_BACKGROUND (str): Background color for buttons.
        FOREGROUND (str): Main foreground color.
        ACCENT (str): Primary red accent color.
        ACCENT_HOVER (str): Hover color for accent elements.
        ACCENT_ANALOG (str): Blue accent color for analog components.
        ACCENT_ANALOG_HOVER (str): Hover color for analog accent elements.
        BORDER (str): Border color for UI elements.
        SLIDER_HANDLE (str): Color of the slider handle.
        SLIDER_HANDLE_BORDER (str): Border color of the slider handle.
        SLIDER_GROOVE (str): Color of the slider groove.
        ACCENT_PRESSED (str): Color of the accent when pressed.
        ACCENT_ANALOG_PRESSED (str): Color of the analog accent when pressed.

    Dimensions:
        BUTTON_ROUND_RADIUS (int): Radius for round buttons.
        BUTTON_RECT_RADIUS (int): Radius for rectangular buttons.
        BUTTON_BORDER_WIDTH (int): Border width for buttons.
        HANDLE_SIZE (str): Size of slider handles.
        GROOVE_WIDTH (str): Width of the slider groove.
        ICON_SIZE (int): Default icon size.
        TAB_BUTTON_RECT_RADIUS (int): Radius for tab buttons.

    Fonts:
        FONT_FAMILY (str): Default font family.
        FONT_SIZE (str): Default font size.

    Button Styles:
        JDXI_BUTTON_ROUND: Standard round button style.
        JDXI_BUTTON_ROUND_SELECTED: Style for selected round buttons.
        JDXI_BUTTON_ROUND_ACTIVE: Style for active round buttons.
        JDXI_BUTTON_ROUND_SMALL: Small round button style.
        JDXI_BUTTON_RECT: Standard rectangular button style.
        JDXI_BUTTON_RECT_SELECTED: Style for selected rectangular buttons.
        JDXI_BUTTON_RECT_ACTIVE: Style for active rectangular buttons.
        JDXI_BUTTON_RECT_ANALOG: Rectangular button style for analog components.
        JDXI_BUTTON_ANALOG_ACTIVE: Active analog button style.
        JDXI_BUTTON_WAVEFORM: Button style for waveform selection.
        JDXI_BUTTON_WAVEFORM_ANALOG: Button style for analog waveform selection.

    Tab Styles:
        JDXI_TABS: Standard tab button styles.
        JDXI_TABS_ANALOG: Tab button styles for analog components.
        JDXI_TABS_DRUMS: Tab button styles for drum components.

    Editor Styles:
        JDXI_EDITOR: Style for the main editor UI.
        JDXI_EDITOR_ANALOG: Style for the analog editor UI.

    Additional Styles:
        JDXI: General application styling.
        JDXI_ADSR: Styling for ADSR envelope sliders.
        JDXI_LABEL_SUB: Sub-label text style.
        JDXI_LABEL: Standard label style.
        JDXI_KEYBOARD_DRUM_LABELS: Style for drum labels in the keyboard section.
        JDXI_INSTRUMENT_TITLE_LABEL: Style for instrument title labels.
        JDXI_LABEL_SYNTH_PART: Style for synthesizer part labels.
        JDXI_LABEL_ANALOG_SYNTH_PART: Style for analog synthesizer part labels.
        JDXI_DRUM_GROUP: Style for drum group UI elements.
        JDXI_PATCH_MANAGER: Styles specific to the patch manager.
        JDXI_PARTIAL_SWITCH: Style for partial switch elements.
        JDXI_PARTIALS_PANEL: Styling for the panel displaying partials.
        JDXI_DEBUGGER: Styles for the debugger window.
        JDXI_SEQUENCER: Styling for the sequencer UI.
        JDXI_PARTS_SELECT: Style for part selection elements.

"""
from jdxi_editor.ui.style.helpers import generate_button_style, generate_tab_style, generate_editor_style


class Style:
    """Central style definitions for JD-Xi Manager"""

    # Colors
    TITLE_TEXT = "#FFFFFF"
    BACKGROUND = "#000000"  # """"#1A1A1A"
    BACKGROUND_PRESSED = "#666666"
    BUTTON_BACKGROUND = "#222222"
    BUTTON_BACKGROUND_PRESSED = "#333333"
    FOREGROUND = "#FFFFFF"
    PADDING = 1  # in px
    BUTTON_PADDING = 1
    ACCENT = "#FF2200"  # Red accent color
    ACCENT_HOVER = "#FF2200"  # Red for hover
    ACCENT_ANALOG = "#00A0E9"
    ACCENT_ANALOG_HOVER = "#00A0E9"
    BORDER = "#333333"
    SLIDER_HANDLE = "#000000"  # Black fill
    SLIDER_HANDLE_BORDER = "#666666"  # Light grey outline
    SLIDER_GROOVE = "#666666"  # grey groove
    SLIDER_NEON = "#ff1a1a"
    SLIDER_NEON_GRADIENT_STOP = "#660000"
    SLIDER_NEON_ANALOG = "#1a1aff"
    SLIDER_NEON_GRADIENT_STOP_ANALOG = "#000066"
    ACCENT_PRESSED = "#FF6666"

    ACCENT_ANALOG_PRESSED = "#417ffa"


    # Dimensions
    BUTTON_ROUND_RADIUS = 15
    BUTTON_RECT_RADIUS = 6
    BUTTON_BORDER_WIDTH = 4
    HANDLE_SIZE = "6px"
    GROOVE_WIDTH = "2px"
    ICON_SIZE = 20
    TAB_BUTTON_RECT_RADIUS = 6

    # Fonts
    FONT_FAMILY = "Myriad Pro, Segoe UI, Arial, sans-serif"
    FONT_SIZE = "12px"
    # Define button styles
    JDXI_BUTTON_ROUND = generate_button_style(
        BACKGROUND, BORDER, BUTTON_ROUND_RADIUS, FOREGROUND, ACCENT_HOVER, ACCENT_PRESSED
    )
    JDXI_BUTTON_ROUND_SELECTED = generate_button_style(
        BACKGROUND, BORDER, BUTTON_ROUND_RADIUS, FOREGROUND, ACCENT_HOVER, ACCENT_PRESSED
    )
    JDXI_BUTTON_ROUND_ACTIVE = generate_button_style(
        bg=BUTTON_BACKGROUND,
        border=ACCENT_HOVER,
        radius=BUTTON_ROUND_RADIUS,
        text_color=FOREGROUND,
        hover=ACCENT_HOVER,
        border_pressed=ACCENT_PRESSED,
    )
    JDXI_BUTTON_ROUND_SMALL = generate_button_style(
        bg=BORDER,
        border=BORDER,
        radius=12,
        text_color=FOREGROUND,
        hover=ACCENT_HOVER,
        border_pressed=ACCENT_PRESSED,
        font_size="16px",
        button_padding=3
    )
    JDXI_BUTTON_RECT = generate_button_style(
        BACKGROUND, BORDER, BUTTON_RECT_RADIUS, FOREGROUND, ACCENT_HOVER, ACCENT_PRESSED
    )
    JDXI_BUTTON_RECT_SELECTED = generate_button_style(
        BACKGROUND, BORDER, BUTTON_RECT_RADIUS, FOREGROUND, ACCENT_HOVER, ACCENT_PRESSED
    )
    JDXI_BUTTON_RECT_ACTIVE = generate_button_style(
        bg=BUTTON_BACKGROUND,
        border=ACCENT_HOVER,
        radius=BUTTON_RECT_RADIUS,
        text_color=FOREGROUND,
        hover=ACCENT_HOVER,
        border_pressed=ACCENT_PRESSED,
    )

    # Analog Button Styles
    JDXI_BUTTON_RECT_ANALOG = generate_button_style(
        BACKGROUND,
        ACCENT_ANALOG,
        BUTTON_RECT_RADIUS,
        FOREGROUND,
        ACCENT_ANALOG_HOVER,
        ACCENT_PRESSED,
    )
    JDXI_BUTTON_ANALOG_ACTIVE = generate_button_style(
        bg=BUTTON_BACKGROUND,
        border=ACCENT_ANALOG,
        radius=BUTTON_RECT_RADIUS,
        text_color=FOREGROUND,
        hover=ACCENT_ANALOG_HOVER,
        border_pressed=ACCENT_ANALOG_PRESSED,
    )
    JDXI_BUTTON_WAVEFORM = generate_button_style(
        bg=BUTTON_BACKGROUND,
        border=BACKGROUND_PRESSED,
        radius=3,
        text_color="#CCCCCC",
        hover="#444444",
        border_pressed=ACCENT_PRESSED,
        background_pressed=BUTTON_BACKGROUND_PRESSED,
        button_border_width=BUTTON_BORDER_WIDTH,
        font_family=FONT_FAMILY,
        font_size=FONT_SIZE,
        button_padding=BUTTON_PADDING
    )

    JDXI_BUTTON_WAVEFORM_ANALOG = generate_button_style(
        bg=BUTTON_BACKGROUND,
        border=BACKGROUND_PRESSED,
        radius=3,
        text_color="#CCCCCC",
        hover="#444444",
        border_pressed=ACCENT_ANALOG,
        background_pressed=BUTTON_BACKGROUND_PRESSED,
        button_border_width=BUTTON_BORDER_WIDTH,
        font_family=FONT_FAMILY,
        font_size=FONT_SIZE,
        button_padding=BUTTON_PADDING
    )

    # Define Tab styles using get_tab_style function
    JDXI_TABS = generate_tab_style(
        bg=BACKGROUND,
        border=BACKGROUND_PRESSED,
        radius=TAB_BUTTON_RECT_RADIUS,
        text_color="white",
        hover_bg=BUTTON_BACKGROUND,
        hover_border="#ff9999",
        selected_bg=BUTTON_BACKGROUND,
        selected_border="#ff6666",
    )

    JDXI_TABS_ANALOG = generate_tab_style(
        bg=BACKGROUND,
        border=BACKGROUND_PRESSED,
        radius=TAB_BUTTON_RECT_RADIUS,
        text_color="white",
        hover_bg="#00A0C1",
        hover_border="#00A0E9",
        selected_bg=BUTTON_BACKGROUND,
        selected_border="#00A0E9",
    )

    JDXI_TABS_DRUMS = generate_tab_style(
        bg=BACKGROUND,
        border=BACKGROUND_PRESSED,
        radius=TAB_BUTTON_RECT_RADIUS,
        text_color="white",
        hover_bg=BUTTON_BACKGROUND,
        hover_border="#ff9999",
        selected_bg=BUTTON_BACKGROUND,
        selected_border="#ff6666",
    )

    JDXI_EDITOR = generate_editor_style(
        ACCENT,
        ACCENT_HOVER,
        BACKGROUND,
        FOREGROUND,
        FONT_FAMILY,
        FONT_SIZE,
        PADDING,
        BUTTON_PADDING,
        SLIDER_HANDLE,
        SLIDER_HANDLE_BORDER,
        SLIDER_GROOVE,
        SLIDER_NEON,
        SLIDER_NEON_GRADIENT_STOP,
    )

    JDXI_EDITOR_ANALOG = generate_editor_style(
        ACCENT_ANALOG,
        ACCENT_ANALOG_HOVER,
        BACKGROUND,
        FOREGROUND,
        FONT_FAMILY,
        FONT_SIZE,
        PADDING,
        BUTTON_PADDING,
        SLIDER_HANDLE,
        SLIDER_HANDLE_BORDER,
        SLIDER_GROOVE,
        SLIDER_NEON_ANALOG,
        SLIDER_NEON_GRADIENT_STOP_ANALOG,
    )

    JDXI = """
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
                border: none;
                border-top: 1px solid #333333;
                margin-top: 1em;
                padding-top: 0.5em;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
                background-color: black;
            }
            QLabel {
                background-color: transparent;
            }
            QStatusBar {
                background-color: black;
                color: white;
            }
        """

    JDXI_ADSR_ANALOG = """
        /* Groove (Track) */
        QSlider::groove:vertical {
            background: #111; /* Dark background */
            width: 6px;
            border-radius: 3px;
        }

        /* Handle (Knob) */
        QSlider::handle:vertical {
            background: black;
            border: 2px solid #1a1aff; /* Neon blue border */
            width: 10px;  /* More rectangular */
            height: 10px;  
            margin: -10px;
            border-radius: 5px;
            padding: 4px;
        }

        /* Glowing effect when moving */
        QSlider::sub-page:vertical {
            background: qlineargradient(x1:0, y1:1, x2:0, y2:0, 
                         stop:0 #000066, stop:1 #1a1aff);
            border-radius: 3px;
        }
        /* Handle (Knob) */
        QSlider::handle:vertical:disabled {
            background: black;
            border: 2px solid #333333; /* grey border */
            width: 10px;  /* More rectangular */
            height: 10px;  
            margin: -10px;
            border-radius: 5px;
        }
        /* greyed out groove */
        QSlider::sub-page:vertical:disabled {
            background: #333333;
            border-radius: 3px;
        }

        /* Unfilled portion */
        QSlider::add-page:vertical {
            background: #222;
            border-radius: 3px;
        }

        /* Tick Marks (Small dashes on both sides) */
        QSlider::tick-mark {
            background: #1a1aff;
            width: 4px;
            height: 2px;
            border-radius: 1px;
            margin-left: -8px;
            margin-right: 8px;
        }

        /* Handle Hover Effect */
        QSlider::handle:vertical:hover {
            border: 2px solid #3333ff;
        }
        /* Spin Box */
        QSpinBox, QDoubleSpinBox {
            background-color: #222;
            border: 1px solid #00A0E9;
            border-radius: 3px;
            padding: 4px;
            margin: -2px;
            width: 40px;
            color: #00A0E9;
        }
        /* QLabels */
        QLabel {
            color: #00A0E9;
        }
    """

    JDXI_ADSR = """
        /* Groove (Track) */
        QSlider::groove:vertical {
            background: #111; /* Dark background */
            width: 6px;
            border-radius: 3px;
        }

        /* Handle (Knob) */
        QSlider::handle:vertical {
            background: black;
            border: 2px solid #ff1a1a; /* Neon red border */
            width: 10px;  /* More rectangular */
            height: 10px;  
            margin: -10px;
            border-radius: 5px;
        }
        /* Handle (Knob) */
        QSlider::handle:vertical:disabled {
            background: black;
            border: 2px solid #333333; /* grey border */
            width: 10px;  /* More rectangular */
            height: 10px;  
            margin: -10px;
            border-radius: 5px;
        }
        /* greyed out groove */
        QSlider::sub-page:vertical:disabled {
            background: #333333;
            border-radius: 3px;
        }

        /* Glowing effect when moving */
        QSlider::sub-page:vertical {
            background: qlineargradient(x1:0, y1:1, x2:0, y2:0, 
                         stop:0 #660000, stop:1 #ff1a1a);
            border-radius: 3px;
        }

        /* Unfilled portion */
        QSlider::add-page:vertical {
            background: #222;
            border-radius: 3px;
        }

        /* Tick Marks (Small dashes on both sides) */
        QSlider::tick-mark {
            background: #ff1a1a;
            width: 4px;
            height: 2px;
            border-radius: 1px;
            margin-left: -8px;
            margin-right: 8px;
        }

        /* Handle Hover Effect */
        QSlider::handle:vertical:hover {
            border: 2px solid #ff3333;
        }
        /* Spin Box */
        QSpinBox, QDoubleSpinBox {
            background-color: #222;
            border: 1px solid #ff1a1a;
            border-radius: 3px;
            padding: 2px;
            margin: -2px;
            color: #ff1a1a;
        }
        /* QLabels */
        QLabel {
            color: #ff1a1a;
        }
    """

    JDXI_ADSR_VERY_VNEW = """
        /* Groove (Track) */
        QSlider::groove:vertical {
            background: #111;
            width: 6px;
            border-radius: 3px;
        }
        /* Handle (Knob) */
        QSlider::handle:vertical {
            background: black;
            border: 2px solid #ff1a1a;
            width: 24px;
            height: 16px;
            margin: -6px;
            border-radius: 2px;
            box-shadow: 0px 0px 10px #ff1a1a;
        }

        /* Glowing effect when moving */
        QSlider::sub-page:vertical {
            background: qlineargradient(x1:0, y1:1, x2:0, y2:0, 
                         stop:0 #660000, stop:1 #ff1a1a);
            border-radius: 3px;
        }

        /* Unfilled portion */
        QSlider::add-page:vertical {
            background: #222;
            border-radius: 3px;
        }

        /* Tick Marks (Fake tick marks using box-shadow) */
        QSlider::tick-mark:vertical {
            background-color: transparent;
            width: 6px;
            height: 6px;
            border-radius: 3px;
            margin-left: -12px;  /* Positioning to the left */
            margin-right: 12px;  /* Positioning to the right */
            box-shadow: 
                -8px 0px 0px 2px #ff1a1a,  /* Left ticks */
                8px 0px 0px 2px #ff1a1a;   /* Right ticks */
        }

        /* Handle Hover Effect */
        QSlider::handle:vertical:hover {
            border: 2px solid #ff3333;
            box-shadow: 0px 0px 15px #ff3333;
        }
    """

    JDXI_ADSR_NEW = """
    /* Groove (Track) */
    QSlider::groove:vertical {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                     stop:0 #222, stop:1 #111); /* Metallic effect */
        width: 8px;
        border-radius: 4px;
    }

    /* Handle (Knob) */
    QSlider::handle:vertical {
        background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, 
                     fx:0.5, fy:0.5, stop:0 #ff4500, stop:1 #7a1c00); 
        border: 2px solid #ff4500; /* Neon-like border */
        width: 16px;  
        height: 16px;
        margin: -6px;
        border-radius: 8px;
    }

    /* Filled portion (moving slider) */
    QSlider::sub-page:vertical {
        background: qlineargradient(x1:0, y1:1, x2:0, y2:0, 
                     stop:0 #ff4500, stop:1 #ff9966);
        border-radius: 4px;
    }

    /* Unfilled portion */
    QSlider::add-page:vertical {
        background: #2a2a2a;
        border-radius: 4px;
    }

    /* Tick Marks */
    QSlider::tick-mark {
        background: #ff6500; /* More visible */
        width: 3px;
        height: 3px;
        border-radius: 2px;
    }

    /* Glow Effect */
    QSlider::handle:vertical:hover {
        background: qradialgradient(cx:0.5, cy:0.5, radius:0.6, 
                     fx:0.5, fy:0.5, stop:0 #ff5722, stop:1 #7a1c00);
        border: 2px solid #ff9966;
    }
"""


    JDXI_ADSR_OLD = """
    QSlider::groove:vertical {
        background: #1A1A1A; /* Dark background */
        width: 6px; /* Thin groove */
        border-radius: 5px;
    }

    QSlider::handle:vertical {
        background: black;
        border: 2px solid #ff4500; /* Bright red/orange border */
        width: 40px;  /* Wider handle */
        height: 12px;  /* Shorter handle */
        margin: -2p x -5px; /* Centers the handle */
        border-radius: 5px;
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

    JDXI_COMBO_BOX = f"""
    QComboBox {{
        background-color: {BACKGROUND};
        border: 1px solid {ACCENT};
        border-radius: 3px;
        padding: 3px;
        color: {FOREGROUND};
    }}

    /* Style for the dropdown button */
    QComboBox::drop-down {{
        border: none;
        width: 20px;
        height: 20px;
    }}

    /* Custom small down arrow */
    QComboBox::down-arrow {{
        width: 16px; /* Adjust arrow size */
        height: 10px;
    }}

    /* Custom small up arrow (if needed for editable combobox) */
    QComboBox::up-arrow {{
        width: 16px; /* Adjust arrow size */
        height: 10px;
    }}

    /* Scrollbar styling */
    QScrollBar:vertical {{
        background: black;
        border: 2px solid #ff4500;
        width: 20px;
        border-radius: 5px;
    }}
    """

    JDXI_COMBO_BOX_ANALOG = f"""
        QComboBox {{
            background-color: {BACKGROUND};
            border: 1px solid {ACCENT_ANALOG};
            border-radius: 3px;
            padding: 3px;
            color: {FOREGROUND};
        }}

        /* Style for the dropdown button */
        QComboBox::drop-down {{
            border: none;
            width: 20px;
            height: 20px;
        }}

        /* Custom small down arrow */
        QComboBox::down-arrow {{
            width: 16px; /* Adjust arrow size */
            height: 10px;
        }}

        /* Custom small up arrow (if needed for editable combobox) */
        QComboBox::up-arrow {{
            width: 16px; /* Adjust arrow size */
            height: 10px;
        }}

        /* Scrollbar styling */
        QScrollBar:vertical {{
            background: black;
            border: 2px solid #ff4500;
            width: 20px;
            border-radius: 5px;
        }}
    """

    JDXI_LABEL_SUB = f"""
            font-family: "{FONT_FAMILY}";
            font-size: 13px;
            color: #d51e35;
            font-weight: bold;
        """

    JDXI_LABEL = f"""
            font-family: "{FONT_FAMILY}";
            font-size: 14px;
            color: #d51e35;
            font-weight: bold;
            background: transparent;
        """

    JDXI_KEYBOARD_DRUM_LABELS = """
                QLabel {
                    color: #808080;
                    font-size: 7px;
                    font-family: monospace;
                    padding: 2px;
                    min-width: 30px;
                }
            """

    JDXI_INSTRUMENT_TITLE_LABEL = """
            color: #FFBB33;
            font-size: 16px;
            font-weight: bold;
            font-family: "Consolas";

            QGroupBox {
                border: 2px solid black;
                border-radius: 5px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #321212,
                    stop: 0.3 #331111,
                    stop: 0.5 #551100,
                    stop: 0.7 #331111,
                    stop: 1 #321212
                );
            }
            """

    JDXI_LABEL_SYNTH_PART = f"""
                font-family: "{FONT_FAMILY}";
                font-size: 13px;
                color: #d51e35;  /* Base red */
                font-weight: bold;
            """

    JDXI_LABEL_ANALOG_SYNTH_PART = f"""
                font-family: "{FONT_FAMILY}";
                font-size: 13px;
                color: {ACCENT_ANALOG};  /* Blue for Analog */
                font-weight: bold;
            """

    JDXI_DRUM_GROUP = """
                QGroupBox {
                width: 100px;
            }
            """

    JDXI_PATCH_MANAGER = f"""
            QMainWindow {{
                background-color: #2E2E2E;
            }}
            QWidget {{
                background-color: #2E2E2E;
                color: #FFFFFF;
                font-family: "{FONT_FAMILY}";
            }}
            QLineEdit {{
                background-color: #1A1A1A;
                color: #FFFFFF;
                border: 1px solid #FF0000;
                border-radius: 3px;
                padding: 2px;
                font-family: 'Consolas';
            }}
            QPushButton {{
                background-color: #3D3D3D;
                color: #FFFFFF;
                border: 1px solid #FF0000;
                border-radius: 3px;
                padding: 2px 15px;
                font-family: "{FONT_FAMILY}";
            }}
            QPushButton:hover {{
                background-color: #4D4D4D;
                border: 1px solid #FF3333;
            }}
            QPushButton:border_pressed {{
                background-color: #2D2D2D;
            }}
            QLabel {{
                color: #FFFFFF;
                font-family: "{FONT_FAMILY}";
            }}
        """

    JDXI_PARTIAL_SWITCH = f"""
                QCheckBox {{
                    color: #CCCCCC;
                    font-size: 10px;
                }}
                QCheckBox::indicator {{
                    width: 16px;
                    height: 16px;
                    background: #333333;
                    border: 1px solid #555555;
                    border-radius: 8px;
                }}
                QCheckBox::indicator:checked {{
                    background: #666666;
                    border-color: #FF4444;
                }}
            """

    JDXI_PARTIALS_PANEL = """  
            QGroupBox {
                color: #CCCCCC;
                font-size: 12px;
                border: 0px solid #444444;
                border-radius: 3px;
                margin-top: 2px;
                padding: 2px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 2px;
                background-color: #2D2D2D;
            }
        """  # this may be sub-classed

    JDXI_DEBUGGER = f"""
            QMainWindow {{
                background-color: #2E2E2E;
            }}
            QWidget {{
                background-color: #2E2E2E;
                color: #FFFFFF;
                font-family: '{FONT_FAMILY}';
            }}
            QPlainTextEdit {{
                background-color: #1A1A1A;
                color: #FFFFFF;
                border: 1px solid #FF0000;
                border-radius: 3px;
                padding: 3px;
                font-family: 'Consolas';
            }}
            QTextEdit {{
                background-color: #1A1A1A;
                color: #FFFFFF;
                border: 1px solid #FF0000;
                border-radius: 3px;
                padding: 2px;
                font-family: 'Consolas';
            }}
            QPushButton {{
                background-color: #3D3D3D;
                color: #FFFFFF;
                border: 1px solid #FF0000;
                border-radius: 3px;
                padding: 2px 15px;
                font-family: "{FONT_FAMILY}";
            }}
            QPushButton:hover {{
                background-color: #4D4D4D;
                border: 1px solid #FF3333;
            }}
            QPushButton:border_pressed {{
                background-color: #2D2D2D;
            }}
        """

    JDXI_SEQUENCER = f"""
            font-family: "{FONT_FAMILY}";
            font-size: 14px;
            color: #d51e35;
            font-weight: bold;
            background: transparent;
        """

    JDXI_PARTS_SELECT = f"""
            font-family: {FONT_FAMILY};
            font-size: 14px;
            color: #d51e35;
            font-weight: bold;
            background: transparent;
            padding-bottom: 10px;
        """


