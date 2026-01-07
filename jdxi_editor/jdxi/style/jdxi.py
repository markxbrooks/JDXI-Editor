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

import platform

from jdxi_editor.jdxi.style.factory import (
    generate_button_style,
    generate_editor_style,
    generate_tab_style,
)


class JDXiStyle:
    """Central style definitions for JD-Xi Manager"""

    # Colors

    TRACK_LABEL_WIDTH = 70
    TRACK_BUTTON_WIDTH = 20
    TRACK_SPINBOX_WIDTH = 40
    PWM_WIDGET_HEIGHT = 250
    ADSR_PLOT_WIDTH = 300
    ADSR_PLOT_HEIGHT = 200
    INSTRUMENT_IMAGE_WIDTH = 350
    INSTRUMENT_IMAGE_HEIGHT = 200  # Maximum height to prevent elongation
    TITLE_TEXT = "#FFFFFF"
    BACKGROUND = "#000000"  # 1A1A1A"
    BACKGROUND_GRADIENT = (
        "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #000000, stop:1 #1A1A1A)"
    )
    BACKGROUND_PRESSED = "#666666"
    BUTTON_BACKGROUND = "#222222"
    BUTTON_BACKGROUND_PRESSED = "#333333"
    FOREGROUND = "#FFFFFF"
    PADDING = 10  # in px
    SPACING = 10  # in px
    ICON_PIXMAP_SIZE = 30  # in px
    TRACK_ICON_PIXMAP_SIZE = 50  # in px
    BUTTON_PADDING = 1
    ACCENT = "#FF2200"  # Red accent color
    ACCENT_HOVER = "#FF4400"  # Brighter red for hover
    ACCENT_ANALOG = "#00A0E9"
    ACCENT_ANALOG_HOVER = "#00C0FF"  # Brighter cyan for hover
    ACCENT_GLOW = "#FF6666"  # Glow color for red accents
    ACCENT_ANALOG_GLOW = "#66C0FF"  # Glow color for analog accents
    BORDER = "#333333"
    SLIDER_HANDLE = "#000000"  # Black fill
    SLIDER_HANDLE_BORDER = "#666666"  # Light grey outline
    SLIDER_GROOVE = "#666666"  # grey groove
    SLIDER_NEON = "#ff1a1a"
    SLIDER_NEON_GRADIENT_STOP = "#660000"
    SLIDER_NEON_ANALOG = "#1a1aff"
    SLIDER_NEON_GRADIENT_STOP_ANALOG = "#000066"
    # Enhanced neon gradients for better glow effect
    SLIDER_NEON_GRADIENT = f"qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {SLIDER_NEON_GRADIENT_STOP}, stop:0.5 {SLIDER_NEON}, stop:1 #ff3333)"
    SLIDER_NEON_ANALOG_GRADIENT = f"qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {SLIDER_NEON_GRADIENT_STOP_ANALOG}, stop:0.5 {SLIDER_NEON_ANALOG}, stop:1 #3399ff)"
    ACCENT_PRESSED = "#FF6666"
    FONT_SIZE = "10"
    ACCENT_ANALOG_PRESSED = "#417ffa"

    #  Dimensions
    BUTTON_ROUND_RADIUS = 15
    BUTTON_RECT_RADIUS = 6
    BUTTON_BORDER_WIDTH = 4
    HANDLE_SIZE = "6px"
    GROOVE_WIDTH = "2px"
    ICON_SIZE = 20
    TAB_BUTTON_RECT_RADIUS = 6

    MAX_RULER_HEIGHT = 200  # Maximum height for the ruler in the midi player
    TRACK_HEIGHT_MINIMUM = 40  # Minimum height for the tracks in the midi player

    FONT_RED = "#d51e35"  # Base red

    # Fonts
    if platform.system() == "Windows":
        FONT_FAMILY = "Orbitron"
        FONT_SIZE = "10px"
        FONT_SIZE_SPLASH_SCREEN = "14px"
    elif platform.system() == "Darwin":
        FONT_FAMILY = "Orbitron"  # "Myriad Pro"
        FONT_SIZE = "11px"
        FONT_SIZE_SPLASH_SCREEN = "14px"
    else:
        FONT_FAMILY = "Orbitron"

        FONT_SIZE_SPLASH_SCREEN = "36px"
    FONT_FAMILY_MONOSPACE = "Consolas"
    FONT_SIZE_MAIN_TABS = "14px"
    FONT_WEIGHT_BOLD = "bold"
    FONT_WEIGHT_NORMAL = "normal"
    GREY = "#CCCCCC"
    # Define button styles
    BUTTON_ROUND = generate_button_style(
        BACKGROUND,
        BORDER,
        BUTTON_ROUND_RADIUS,
        FOREGROUND,
        ACCENT_HOVER,
        ACCENT_PRESSED,
    )
    BORDER_PRESSED = "#2D2D2D"
    BUTTON_ROUND_SELECTED = generate_button_style(
        BACKGROUND,
        BORDER,
        BUTTON_ROUND_RADIUS,
        FOREGROUND,
        ACCENT_HOVER,
        ACCENT_PRESSED,
    )
    BUTTON_ROUND_ACTIVE = generate_button_style(
        bg=BUTTON_BACKGROUND,
        border=ACCENT_HOVER,
        radius=BUTTON_ROUND_RADIUS,
        text_color=FOREGROUND,
        hover=ACCENT_HOVER,
        border_pressed=ACCENT_PRESSED,
    )
    BUTTON_ROUND_SMALL = generate_button_style(
        bg=BORDER,
        border="black",
        radius=10,
        text_color="#AAAAAA",
        hover=ACCENT_HOVER,
        border_pressed=ACCENT_PRESSED,
        font_size=FONT_SIZE,
        button_padding=BUTTON_PADDING,
        button_border_width=1,
    )
    BUTTON_RECT = generate_button_style(
        BACKGROUND, BORDER, BUTTON_RECT_RADIUS, FOREGROUND, ACCENT_HOVER, ACCENT_PRESSED
    )
    BUTTON_RECT_SELECTED = generate_button_style(
        BACKGROUND, BORDER, BUTTON_RECT_RADIUS, FOREGROUND, ACCENT_HOVER, ACCENT_PRESSED
    )
    BUTTON_RECT_ACTIVE = generate_button_style(
        bg=BUTTON_BACKGROUND,
        border=ACCENT_HOVER,
        radius=BUTTON_RECT_RADIUS,
        text_color=FOREGROUND,
        hover=ACCENT_HOVER,
        border_pressed=ACCENT_PRESSED,
    )

    # Analog Button Styles
    BUTTON_RECT_ANALOG = generate_button_style(
        BACKGROUND,
        ACCENT_ANALOG,
        BUTTON_RECT_RADIUS,
        FOREGROUND,
        ACCENT_ANALOG_HOVER,
        ACCENT_PRESSED,
    )
    BUTTON_ANALOG_ACTIVE = generate_button_style(
        bg=BUTTON_BACKGROUND,
        border=ACCENT_ANALOG,
        radius=BUTTON_RECT_RADIUS,
        text_color=FOREGROUND,
        hover=ACCENT_ANALOG_HOVER,
        border_pressed=ACCENT_ANALOG_PRESSED,
    )
    BUTTON_WAVEFORM = generate_button_style(
        bg=BUTTON_BACKGROUND,
        border=BACKGROUND_PRESSED,
        radius=12,  # More circular
        text_color=GREY,
        hover="#444444",
        border_pressed=ACCENT_PRESSED,
        background_pressed=BUTTON_BACKGROUND_PRESSED,
        button_border_width=2,  # Thinner border for waveform buttons
        font_family=FONT_FAMILY,
        font_size=FONT_SIZE,
        button_padding=BUTTON_PADDING,
    )

    BUTTON_WAVEFORM_ANALOG = generate_button_style(
        bg=BUTTON_BACKGROUND,
        border=BACKGROUND_PRESSED,
        radius=3,
        text_color=GREY,
        hover="#444444",
        border_pressed=ACCENT_ANALOG,
        background_pressed=BUTTON_BACKGROUND_PRESSED,
        button_border_width=BUTTON_BORDER_WIDTH,
        font_family=FONT_FAMILY,
        font_size=FONT_SIZE,
        button_padding=BUTTON_PADDING,
    )

    CREDITS_LABEL_STYLE = f"""
            /* QLabels */
                QLabel {{
                    font-family: {FONT_FAMILY};
                    color: 'black';
                    background: #FFFFFF;
            }}
            """

    EDITOR = generate_editor_style(
        accent=ACCENT,
        accent_hover=ACCENT_HOVER,
        background=BACKGROUND,
        foreground=FOREGROUND,
        font_family=FONT_FAMILY,
        font_size=FONT_SIZE,
        padding=PADDING,
        button_padding=BUTTON_PADDING,
        slider_handle=SLIDER_HANDLE,
        slider_handle_border=SLIDER_HANDLE_BORDER,
        slider_groove=SLIDER_GROOVE,
        slider_neon=SLIDER_NEON,
        slider_neon_gradient_stop=SLIDER_NEON_GRADIENT_STOP,
    )

    EDITOR_ANALOG = generate_editor_style(
        accent=ACCENT_ANALOG,
        accent_hover=ACCENT_ANALOG_HOVER,
        background=BACKGROUND,
        foreground=FOREGROUND,
        font_family=FONT_FAMILY,
        font_size=FONT_SIZE,
        padding=PADDING,
        button_padding=BUTTON_PADDING,
        slider_handle=SLIDER_HANDLE,
        slider_handle_border=SLIDER_HANDLE_BORDER,
        slider_groove=SLIDER_GROOVE,
        slider_neon=SLIDER_NEON_ANALOG,
        slider_neon_gradient_stop=SLIDER_NEON_GRADIENT_STOP_ANALOG,
    )

    EDITOR_TITLE_LABEL = f"""
                font-family: {FONT_FAMILY}, sans-serif;
                font-size: 20px;
                font-weight: bold;
                letter-spacing: 2px;
                color: {ACCENT};
            """

    ANALOG_SECTION_HEADER = f"""
                font-family: {FONT_FAMILY}, sans-serif;
                font-weight: bold;
                font-size: 18px;
                color: {ACCENT_ANALOG};
                letter-spacing: 1px;
            """

    DIGITAL_SECTION_HEADER = f"""
                font-family: {FONT_FAMILY}, sans-serif;
                font-weight: bold;
                font-size: 18px;
                color: {ACCENT};
                letter-spacing: 1px;
            """

    INSTRUMENT = f"""
            QMainWindow {{
                background: {BACKGROUND_GRADIENT};
            }}
            QWidget {{
                font-family: {FONT_FAMILY};
                margin: 0px;
                padding: 0px;
                background: {BACKGROUND_GRADIENT};
                color: white;
            }}
            QMenuBar {{
                background-color: black;
                color: white;
            }}
            QMenuBar::item:selected {{
                background-color: #333333;
            }}
            QMenu {{
                background-color: black;
                color: white;
            }}
            QMenu::item:selected {{
                background-color: #333333;
            }}
            QGroupBox {{
                font-family: {FONT_FAMILY};
                border: none;
                border-top: 1px solid #333333;
                margin: 1px;
                padding: 1px;
            }}
            QGroupBox::title {{
                font-family: {FONT_FAMILY};
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 1px;
                background-color: black;
            }}
            QLabel {{
                background-color: transparent;
                color: white;
            }}
            QStatusBar {{
                background-color: black;
                color: "{ACCENT}";
            }}
            QSlider {{
                margin-bottom: 2px;
                margin-top: 2px;
            }}
        """

    INSTRUMENT_IMAGE_LABEL = """
            QLabel {
                    height: 150px;
                    background-color: transparent;
                    border: none;
                }
        """

    LOG_VIEWER = """
            QMainWindow {
                background-color: #2E2E2E;
            }
            QWidget {
                background-color: #2E2E2E;
                color: #FFFFFF;
                font-family: 'Myriad Pro';
            }
            QTextEdit {
                background-color: #1A1A1A;
                color: #FFFFFF;
                border: 1px solid #FF0000;
                border-radius: 3px;
                padding: 5px;
                font-family: 'Consolas';
            }
            QPushButton {
                background-color: #3D3D3D;
                color: #FFFFFF;
                border: 1px solid #FF0000;
                border-radius: 3px;
                padding: 5px 15px;
                font-family: 'Myriad Pro';
            }
            QPushButton:hover {
                background-color: #4D4D4D;
                border: 1px solid #FF3333;
            }
            QPushButton:pressed {
                background-color: #2D2D2D;
            }
        """

    MIDI_MESSAGE_MONITOR = f"""
            QTextEdit {{
                font-family: 'Consolas', 'Courier New', monospace;
                background-color: #1E1E1E;
                color: #FFCC00;
                border: 1px solid {ACCENT};
                border-radius: 4px;
                padding: 5px;
                font-size: 11px;
            }}
            QTextEdit:focus {{
                border: 2px solid {ACCENT};
                background-color: #252525;
            }}
        """

    MIXER_LABEL_ANALOG = f"""
                font-size: 16px;
                font-weight: bold;
                color: {ACCENT_ANALOG};
            """

    MIXER_LABEL = f"""
        QLabel {{
                font-family: {FONT_FAMILY};
                font-size: 16px;
                font-weight: bold;
                color: {ACCENT};
                }}
    """

    PROGRAM_PRESET_GROUPS = f"""            
         QGroupBox {{
                 font-family: {FONT_FAMILY};
                 width: 300px;
                 border: none;
                 border-top: 1px solid {ACCENT};
                 margin: 1px;
                 padding: 1px;
             }}"""

    PROGRAM_PRESET_GROUP_WIDTH = 300

    PROGRESS_BAR = f"""
        QProgressBar {{
            background-color: #333;
            color: white;
            font-family: '{FONT_FAMILY_MONOSPACE}';
            border: 2px solid #444;
            border-radius: 10px;
            text-align: center;
        }}
        QProgressBar::chunk {{
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                             stop:0 #660000, stop:1 #ff1a1a);
            border-radius: 10px;
        }}
        """

    SLIDER_VERTICAL = f"""
        /* Groove (Track) */
        QSlider::groove:vertical {{
            font-family: {FONT_FAMILY};
            background: #111; /* Dark background */
            width: 6px;
            border-radius: 3px;
        }}

        /* Handle (Knob) */
        QSlider::handle:vertical {{
            background: black;
            border: 2px solid #ff1a1a; /* Neon red border */
            width: 10px;  /* More rectangular */
            height: 10px;  
            margin: -8px;
            margin-bottom: 2px;
            margin-top: 1px;
            border-radius: 5px;
        }}
        /* Handle (Knob) */
        QSlider::handle:vertical:disabled {{
            background: black;
            border: 2px solid #333333; /* grey border */
            width: 10px;  /* More rectangular */
            height: 10px;  
            margin: -10px;
            border-radius: 5px;
        }}
        /* greyed out groove */
        QSlider::sub-page:vertical:disabled {{
            background: #333333;
            border-radius: 3px;
        }}

        /* Glowing effect when moving */
        QSlider::sub-page:vertical {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                         stop:0 #660000, stop:1 #ff1a1a);
            border-radius: 3px;
        }}
        /* Glowing effect when moving */
        QSlider::sub-page:vertical:disabled:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                         stop:0 #660000, stop:1 #ff1a1a);
            border-radius: 3px;
        }}

        /* Unfilled portion */
        QSlider::add-page:vertical {{
            font-family: {FONT_FAMILY};
            background: #222;
            border-radius: 3px;
        }}

        /* Tick Marks (Small dashes on both sides) */
        QSlider::tick-mark {{
            background: #ff1a1a;
            width: 4px;
            height: 2px;
            border-radius: 1px;
            margin-left: -8px;
            margin-right: 8px;
        }}
        QSlider::horizontal {{
            margin-left: 6px;
            margin-right: 6x;
        }}

        /* Handle Hover Effect */
        QSlider::handle:vertical:hover {{
            border: 2px solid #ff3333;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
             stop:0 #660000, stop:1 #ff1a1a);
        }}
        /* Spin Box */
        QSpinBox, QDoubleSpinBox {{
            background-color: #222;
            border: 1px solid #ff1a1a;
            border-radius: 3px;
            padding: 1px;
            margin: -2px;
            color: #ff1a1a;
        }}
        /* QLabels */
        QLabel {{
            color: "{FONT_RED}";
        }}
    """

    SPLASH_SCREEN = generate_editor_style(
        accent=ACCENT,
        accent_hover=ACCENT_HOVER,
        background=BACKGROUND,
        foreground=FOREGROUND,
        font_family=FONT_FAMILY,
        font_size=FONT_SIZE_SPLASH_SCREEN,
        padding=PADDING,
        button_padding=BUTTON_PADDING,
        slider_handle=SLIDER_HANDLE,
        slider_handle_border=SLIDER_HANDLE_BORDER,
        slider_groove=SLIDER_GROOVE,
        slider_neon=SLIDER_NEON,
        slider_neon_gradient_stop=SLIDER_NEON_GRADIENT_STOP,
        font_weight=FONT_WEIGHT_BOLD,
    )

    SPLITTER = """
                 QSplitter::handle {
                     background-color: #444;
                     border: 1px solid #666;
                 }
                 QSplitter::handle:vertical {
                     height: 6px;
                 }
                 QSplitter::handle:horizontal {
                     width: 6px;
                 }
             """

    # Define Tab styles using get_tab_style function
    TABS = generate_tab_style(
        bg=BACKGROUND,
        border=BACKGROUND_PRESSED,
        radius=TAB_BUTTON_RECT_RADIUS,
        text_color="white",
        hover_bg=BUTTON_BACKGROUND,
        hover_border="#ff9999",
        selected_bg=BUTTON_BACKGROUND,
        selected_border=ACCENT,
    )

    TABS_ANALOG = generate_tab_style(
        bg=BACKGROUND,
        border=BACKGROUND_PRESSED,
        radius=TAB_BUTTON_RECT_RADIUS,
        text_color="white",
        hover_bg="#00A0C1",
        hover_border="#00A0E9",
        selected_bg=BUTTON_BACKGROUND,
        selected_border="#00A0E9",
    )

    TABS_DRUMS = generate_tab_style(
        bg=BACKGROUND,
        border=BACKGROUND_PRESSED,
        radius=TAB_BUTTON_RECT_RADIUS,
        text_color="white",
        hover_bg=BUTTON_BACKGROUND,
        hover_border="#ff9999",
        selected_bg=BUTTON_BACKGROUND,
        selected_border="#ff6666",
    )

    TABS_MAIN_EDITOR = (
        generate_tab_style(
            bg=BACKGROUND,
            border=BACKGROUND_PRESSED,
            radius=TAB_BUTTON_RECT_RADIUS,
            text_color="white",
            hover_bg=BUTTON_BACKGROUND,
            hover_border="#ff9999",
            selected_bg=BUTTON_BACKGROUND,
            selected_border="#ff6666",
            font_size=FONT_SIZE_MAIN_TABS,
            font_family=FONT_FAMILY,
        )
        + f"""
        QTabBar[analogTabSelected="true"]::tab:selected {{
            font-family: {FONT_FAMILY};
            background: {BUTTON_BACKGROUND};
            color: white;
            border: 2px solid {ACCENT_ANALOG};
            font-size: {FONT_SIZE_MAIN_TABS};
        }}
        QTabBar[analogTabSelected="true"]::tab:hover {{
            background: {BUTTON_BACKGROUND};
            border: 2px solid {ACCENT_ANALOG_HOVER};
            font-family: {FONT_FAMILY};
            font-size: {FONT_SIZE_MAIN_TABS};
        }}
        """
    )

    SLIDER = f"""
            QSlider::handle:horizontal{{
                background: {SLIDER_HANDLE};
                border: 3px solid {SLIDER_NEON}; /* Neon red border */
                width: 8px;  /* More rectangular */
                height: 2px;  
                margin: -6px;
                padding: 1px;
                border-radius: 4px;
            }}
            QSlider::handle:disabled{{
                background: {SLIDER_HANDLE};
                border: 2px solid #333333; /* grey border */
                width: 8px;  /* More rectangular */
                height: 2px;  
                margin: -6px;
                padding: 1px;
                border-radius: 4px;
            }}
            /* Unfilled portion */
            QSlider::add-page:horizontal {{
                background: #222;
                border-radius: 3px;
            }}
            QSlider::handle:vertical {{
                background: {SLIDER_HANDLE};
                border: 2px solid {SLIDER_HANDLE_BORDER};
                width: 18px;
                height: 12px;
                margin: -9px 0;
                border-radius: 9px;
            }}
            QSlider::handle:vertical:disabled{{
                background: {SLIDER_HANDLE};
                border: 2px solid #333333; /* grey border */
                width: 18px;  /* More rectangular */
                height: 12px;  
                margin: -9px;
                border-radius: 4px;
            }}
            /* Glowing effect when moving */
            QSlider::sub-page:horizontal {{
                background: qlineargradient(x1:1, y1:0, x2:0, y2:0, 
                             stop:0 {SLIDER_NEON_GRADIENT_STOP}, stop:1 {SLIDER_NEON});
                border-radius: 3px;
            }}
            /* Glowing effect when moving */
            QSlider::sub-page:horizontal:disabled {{
                background: #333333;
                border-radius: 3px;
            }}

            /* Unfilled portion */
            QSlider::add-page:horizontal {{
                background: #222;
                border-radius: 3px;
            }}
            /* QLabels */
            QLabel {{
                color: {ACCENT};
            }}
            QSlider::horizontal {{
                margin-left: 5px;
                margin-right: 5px;
            }}
        """

    SLIDER_DISABLED = f"""
                QSlider::handle:horizontal{{
                background: {SLIDER_HANDLE};
                border: 3px solid #333333; /* Neon red border */
                width: 8px;  /* More rectangular */
                height: 2px;  
                margin: -6px;
                padding: 1px;
                border-radius: 4px;
            }}
            QSlider::handle:disabled{{
                background: {SLIDER_HANDLE};
                border: 2px solid #333333; /* grey border */
                width: 8px;  /* More rectangular */
                height: 2px;  
                margin: -6px;
                padding: 1px;
                border-radius: 4px;
            }}
            /* Unfilled portion */
            QSlider::add-page:horizontal {{
                background: #222;
                border-radius: 3px;
            }}
            QSlider::handle:vertical {{
                background: {SLIDER_HANDLE};
                border: 2px solid #333333;
                width: 18px;
                height: 12px;
                margin: -9px 0;
                border-radius: 9px;
            }}
            QSlider::handle:vertical:disabled{{
                background: {SLIDER_HANDLE};
                border: 2px solid #333333; /* grey border */
                width: 18px;  /* More rectangular */
                height: 12px;  
                margin: -9px;
                border-radius: 4px;
            }}
            /* Glowing effect when moving */
            QSlider::sub-page:horizontal {{
                background: qlineargradient(x1:1, y1:0, x2:0, y2:0, 
                             stop:0 {SLIDER_NEON_GRADIENT_STOP}, stop:1 {SLIDER_NEON});
                border-radius: 3px;
            }}
            /* Glowing effect when moving */
            QSlider::sub-page:horizontal:disabled {{
                background: #333333;
                border-radius: 3px;
            }}

            /* Unfilled portion */
            QSlider::add-page:horizontal {{
                background: #222;
                border-radius: 3px;
            }}
            /* QLabels */
            QLabel {{
                color: {ACCENT};
            }}
            QSlider::horizontal {{
                margin-left: 5px;
                margin-right: 5px;
            }}
        """

    TRANSPARENT = f"""
        QMainWindow, QWidget, QMenuBar {{
            background-color: transparent;
            color: "{FONT_RED}";
        }}
        QSlider {{
            border: #333333;
        }}
        QPushButton {{
            background-color: transparent;
            border: 1px solid red;
            color: "{FONT_RED}";
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
            stop:0 #660000, stop:1 #ff1a1a);
        }}
        QStatusBar {{
            background-color: transparent;
            color: "{FONT_RED}";
        }}
    """

    TRANSPARENT_WHITE = f"""
        QMainWindow, QWidget, QMenuBar {{
            background-color: transparent;
            color: "{FONT_RED}";
        }}
        QLabel {{
            background-color: transparent;
            color: "white";
        }}
        QPushButton {{
            background-color: transparent;
            border: 1px solid red;
            color: "{FONT_RED}";
        }}
        QPushButton:hover {{
            background-color: rgba(255, 0, 0, 30);
        }}
        QStatusBar {{
            background-color: transparent;
            color: "{FONT_RED}";
        }}
    """

    # Status indicator styles with glow effect
    STATUS_INDICATOR_ACTIVE = f"""
        QLabel {{
            background-color: {ACCENT};
            border-radius: 8px;
            min-width: 12px;
            min-height: 12px;
            max-width: 12px;
            max-height: 12px;
        }}
    """

    STATUS_INDICATOR_INACTIVE = f"""
        QLabel {{
            background-color: #333333;
            border: 1px solid #666666;
            border-radius: 8px;
            min-width: 12px;
            min-height: 12px;
            max-width: 12px;
            max-height: 12px;
        }}
    """

    STATUS_INDICATOR_ANALOG_ACTIVE = f"""
        QLabel {{
            background-color: {ACCENT_ANALOG};
            border-radius: 8px;
            min-width: 12px;
            min-height: 12px;
            max-width: 12px;
            max-height: 12px;
        }}
    """

    # Enhanced button glow style
    BUTTON_GLOW_RED = f"""
        QPushButton {{
            border: 2px solid {ACCENT};
            background-color: {BUTTON_BACKGROUND};
        }}
        QPushButton:hover {{
            border: 2px solid {ACCENT_HOVER};
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #330000, stop:1 {ACCENT_HOVER});
        }}
        QPushButton:pressed {{
            border: 2px solid {ACCENT_PRESSED};
            background-color: {BUTTON_BACKGROUND_PRESSED};
        }}
    """

    BUTTON_GLOW_ANALOG = f"""
        QPushButton {{
            border: 2px solid {ACCENT_ANALOG};
            background-color: {BUTTON_BACKGROUND};
        }}
        QPushButton:hover {{
            border: 2px solid {ACCENT_ANALOG_HOVER};
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #003333, stop:1 {ACCENT_ANALOG_HOVER});
        }}
        QPushButton:pressed {{
            border: 2px solid {ACCENT_ANALOG_PRESSED};
            background-color: {BUTTON_BACKGROUND_PRESSED};
        }}
    """

    ADSR_ANALOG = f"""
        QGroupBox {{
             font-family: {FONT_FAMILY};
             width: 300px;
             border: none;
             border-top: 1px solid {ACCENT_ANALOG};
             margin: 1px;
             padding: 1px;
         }}
        /* Groove (Track) */
        QSlider::groove:vertical {{
            font-family: {FONT_FAMILY};
            background: #111; /* Dark background */
            width: 6px;
            border-radius: 3px;
            border-radius: 3px;
            border-radius: 3px;
        }}

        /* Handle (Knob) */
        QSlider::handle:vertical {{
            background: black;
            border: 2px solid #1a1aff; /* Neon blue border */
            width: 10px;  /* More rectangular */
            height: 10px;  
            margin: -10px;
            margin-bottom: 2px;
            margin-top: 2px;
            border-radius: 5px;
            padding: 1px;
        }}

        /* Glowing effect when moving */
        QSlider::sub-page:vertical {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                         stop:0 #000066, stop:1 #1a1aff);
            border-radius: 3px;
        }}
        /* Handle (Knob) */
        QSlider::handle:vertical:disabled {{
            background: black;
            border: 2px solid #333333; /* grey border */
            width: 10px;  /* More rectangular */
            height: 10px;  
            margin: -10px;
            border-radius: 5px;
        }}
        /* greyed out groove */
        QSlider::sub-page:vertical:disabled {{
            background: #333333;
            border-radius: 3px;
        }}

        /* Unfilled portion */
        QSlider::add-page:vertical {{
            background: #222;
            border-radius: 3px;
        }}

        /* Tick Marks (Small dashes on both sides) */
        QSlider::tick-mark {{
            background: #1a1aff;
            width: 4px;
            height: 2px;
            border-radius: 1px;
            margin-left: 2px;
            margin-right: 2px;
        }}

        /* Handle Hover Effect */
        QSlider::handle:vertical:hover {{
            border: 2px solid #3333ff;
        }}
        /* Spin Box */
        QSpinBox, QDoubleSpinBox {{
            background-color: #222;
            border: 1px solid #00A0E9;
            border-radius: 3px;
            padding: 1px;
            margin: -2px;
            width: 40px;
            color: #00A0E9;
        }}
        /* QLabels */
        QLabel {{
            color: #00A0E9;
        }}
    """

    ADSR = f"""
         QGroupBox {{
             font-family: {FONT_FAMILY};
             width: 200px;
             border: none;
             border-top: 1px solid {ACCENT};
             margin: 1px;
             padding: 1px;
         }}
        /* Groove (Track) */
        QSlider::groove:vertical {{
            font-family: {FONT_FAMILY};
            background: #111; /* Dark background */
            width: 6px;
            border-radius: 3px;
        }}

        /* Handle (Knob) */
        QSlider::handle:vertical {{
            background: black;
            border: 2px solid #ff1a1a; /* Neon red border */
            width: 10px;  /* More rectangular */
            height: 10px;  
            margin: -8px;
            margin-bottom: 2px;
            margin-top: 1px;
            border-radius: 5px;
        }}
        /* Handle (Knob) */
        QSlider::handle:vertical:disabled {{
            background: black;
            border: 2px solid #333333; /* grey border */
            width: 10px;  /* More rectangular */
            height: 10px;  
            margin: -10px;
            border-radius: 5px;
        }}
        /* greyed out groove */
        QSlider::sub-page:vertical:disabled {{
            background: #333333;
            border-radius: 3px;
        }}

        /* Glowing effect when moving */
        QSlider::sub-page:vertical {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                         stop:0 #660000, stop:1 #ff1a1a);
            border-radius: 3px;
        }}
        /* Glowing effect when moving */
        QSlider::sub-page:vertical:disabled:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                         stop:0 #660000, stop:1 #ff1a1a);
            border-radius: 3px;
        }}

        /* Unfilled portion */
        QSlider::add-page:vertical {{
            font-family: {FONT_FAMILY};
            background: #222;
            border-radius: 3px;
        }}

        /* Tick Marks (Small dashes on both sides) */
        QSlider::tick-mark {{
            background: #ff1a1a;
            width: 4px;
            height: 2px;
            border-radius: 1px;
            margin-left: -8px;
            margin-right: 8px;
        }}
        QSlider::horizontal {{
            margin-left: 6px;
            margin-right: 6x;
        }}

        /* Handle Hover Effect */
        QSlider::handle:vertical:hover {{
            border: 2px solid #ff3333;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
             stop:0 #660000, stop:1 #ff1a1a);
        }}
        /* Spin Box */
        QSpinBox, QDoubleSpinBox {{
            background-color: #222;
            border: 1px solid #ff1a1a;
            border-radius: 3px;
            padding: 1px;
            margin: -2px;
            color: #ff1a1a;
        }}
        /* QLabels */
        QLabel {{
            color: "{FONT_RED}";
        }}
    """

    ADSR_DISABLED = f"""
            QSlider {{
                font-family: {FONT_FAMILY};
            }}
            QLabel {{
                font-family: {FONT_FAMILY};
            }}
            /* Groove (Track) */
            QSlider::groove:vertical {{
                background: #111; /* Dark background */
                width: 6px;
                border-radius: 3px;
            }}

            /* Handle (Knob) */
            QSlider::handle:vertical {{
                background: black;
                border: 2px solid #333333; /* Neon red border */
                width: 10px;  /* More rectangular */
                height: 10px;  
                margin: -8px;
                margin-bottom: 2px;
                margin-top: 2px;
                border-radius: 5px;
            }}
            /* Handle (Knob) */
            QSlider::handle:vertical:disabled {{
                background: black;
                border: 2px solid #333333; /* grey border */
                width: 10px;  /* More rectangular */
                height: 10px;  
                margin: -10px;
                border-radius: 5px;
            }}
            /* greyed out groove */
            QSlider::sub-page:vertical:disabled {{
                background: #333333;
                border-radius: 3px;
            }}

            /* Glowing effect when moving */
            QSlider::sub-page:vertical {{
                font-family: {FONT_FAMILY};
                background: #333333;
                border-radius: 3px;
            }}

            /* Unfilled portion */
            QSlider::add-page:vertical {{
                background: #222;
                border-radius: 3px;
            }}

            /* Tick Marks (Small dashes on both sides) */
            QSlider::tick-mark {{
                background: #333333;
                width: 4px;
                height: 2px;
                border-radius: 1px;
                margin-left: -8px;
                margin-right: 8px;
            }}
            QSlider::horizontal {{
                margin-left: 6px;
                margin-right: 6x;
            }}

            /* Handle Hover Effect */
            QSlider::handle:vertical:hover {{
                border: 2px solid #ff1a1a;
            }}
            /* Spin Box */
            QSpinBox, QDoubleSpinBox {{
                background-color: #222;
                border: 1px solid #ff1a1a;
                border-radius: 3px;
                padding: 1px;
                margin: -2px;
                color: #ff1a1a;
            }}
            /* QLabels */
            QLabel {{
                color: "{FONT_RED}";
            }}
        """

    ADSR_PLOT = """
        QWidget {
            background-color: #333333;
        }
    """

    COMBO_BOX = f"""
    QComboBox {{
        font-family: {FONT_FAMILY};
        background-color: {BACKGROUND};
        border: 1px solid {ACCENT};
        border-radius: 3px;
        padding: 1px;
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

    COMBO_BOX_ANALOG = f"""
        QComboBox {{
            font-family: {FONT_FAMILY};
            background-color: {BACKGROUND};
            border: 1px solid {ACCENT_ANALOG};
            border-radius: 3px;
            padding: 1px;
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

    LABEL_SUB = f"""
            font-family: "{FONT_FAMILY}";
            font-size: 13px;
            color: #d51e35;
            font-weight: bold;
        """

    LABEL = f"""
            font-family: "{FONT_FAMILY}";
            font-size: 14px;
            color: #d51e35;
            font-weight: bold;
            background: transparent;
        """

    QLABEL = f"""
        QLabel {{
            font-family: "{FONT_FAMILY}";
            font-size: 14px;
            color: #d51e35;
            font-weight: bold;
            background: transparent;
        }}
    """

    QLINEEDIT = f"""
        QLineEdit {{
            font-family: "{FONT_FAMILY}";
            font-size: 12px;
            color: #FFFFFF;
            background: #1a1a1a;
            font-weight: bold;
        }}
    """

    KEYBOARD_DRUM_LABELS = """
                QLabel {
                    color: #808080;
                    font-size: 7px;
                    font-family: monospace;
                    padding: 2px;
                    min-width: 30px;
                }
            """

    INSTRUMENT_TITLE_LABEL = f"""
            font-family: "{FONT_FAMILY_MONOSPACE}";
            color: #FFBB33;
            font-size: 16px;
            font-weight: bold;

            QGroupBox {{
                height: 60;
                border: 2px solid black;
                border-radius: 5px;
                padding: 1px;
                margin: 1px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #321212,
                    stop: 0.3 #331111,
                    stop: 0.5 #551100,
                    stop: 0.7 #331111,
                    stop: 1 #321212
                );
            }}
            """
    INSTRUMENT_SUBTITLE_LABEL = f"""
            font-family: "{FONT_FAMILY_MONOSPACE}";
            color: #FFBB33;
            font-size: 12px;
            font-weight: bold;
            """

    INSTRUMENT_IMAGE_LABEL = f"""        
        QGroupBox {{
            font-family: {FONT_FAMILY};
            height: 60;
            width: 80px;
            background-color: #000000;
            border: 1px solid {BACKGROUND_PRESSED};
            border-radius: 5px;
            padding: 1px;
            margin: 1px;
            }}
        """

    LABEL_SYNTH_PART = f"""
                font-family: "{FONT_FAMILY}";
                font-size: 13px;
                color: "{FONT_RED}";  /* Base red */
                font-weight: bold;
            """

    LABEL_ANALOG_SYNTH_PART = f"""
                font-family: "{FONT_FAMILY}";
                font-size: 13px;
                color: {ACCENT_ANALOG};  /* Blue for Analog */
                font-weight: bold;
            """

    DRUM_GROUP = f"""
                QGroupBox {{
                font-family: {FONT_FAMILY};
                width: 50px;
                height: 60;
            }}
            """
    TAB_TITLE_ANALOG = f"""
        QTabBar::tab:selected:analog {{
        font-family: {FONT_FAMILY};
        font-size: 13px;
        font-weight: bold;
        color: {ACCENT_ANALOG};
    }}
    QTabBar::tab:hover:analog {{
    font-family: {FONT_FAMILY};
        font-size: 13px;
        font-weight: bold;
        color: {ACCENT_ANALOG};
    }}
    QTabBar::tab:selected {{
        font-family: {FONT_FAMILY};
        font-size: 13px;
        font-weight: bold;
        color: {ACCENT_ANALOG};
    }}
    """

    GROUP_BOX_ANALOG = f"""
        QGroupBox {{
            font-family: {FONT_FAMILY};
            border: none;
            color: #FFFFFF;
            border-top: 1px solid {ACCENT_ANALOG};
            margin: 10px;
            padding: 10px;
        }}
        QGroupBox::title {{
            font-family: {FONT_FAMILY};
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 10 10px;
            background-color: black;
        }}
        """

    PATCH_MANAGER = f"""
            QMainWindow {{
                background-color: #2E2E2E;
                font-family: {FONT_FAMILY};
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
                padding: 1px;
                font-family: 'Consolas';
            }}
            QPushButton {{
                background-color: #3D3D3D;
                color: #FFFFFF;
                border: 1px solid #FF0000;
                border-radius: 3px;
                padding: 1px 1px;
                font-family: "{FONT_FAMILY}";
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                         stop:0 #660000, stop:1 #ff1a1a);
                border: 1px solid #FF3333;
            }}
            QPushButton:pressed {{
                background-color: {BORDER_PRESSED};
            }}
            QLabel {{
                color: #FFFFFF;
                font-family: "{FONT_FAMILY}";
            }}
        """
    LABEL_WHEEL = f"""            
        QLabel {{
                color: red;
                font-family: "{FONT_FAMILY}";
            }}
        """

    PARTIAL_SWITCH = f"""
                QCheckBox {{
                    color: {GREY};
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
                    background: {BACKGROUND_PRESSED};
                    border-color: #FF4444;
                }}
            """

    PARTIALS_PANEL = f"""  
        QGroupBox {{
            font-family: {FONT_FAMILY};
            color: {GREY};
            height: 60;
            font-size: 12px;
            border: 0px;
            border-top: 2px solid #444444;  /* Only top border */
            border-radius: 3px;
            margin-top: 1px;
            padding: 1px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 1px;
            margin-top: 1px;
            background-color: {BORDER_PRESSED};
        }}
    """

    DEBUGGER = f"""
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
                padding: 1px;
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
                padding: 1px 1px;
                font-family: "{FONT_FAMILY}";
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                         stop:0 #660000, stop:1 #ff1a1a);
                border: 1px solid #FF3333;
            }}
            QPushButton:pressed {{
                background-color: {BACKGROUND_PRESSED};
            }}
        """

    SEQUENCER = f"""
            font-family: "{FONT_FAMILY}";
            font-size: 14px;
            color: #d51e35;
            font-weight: bold;
            background: transparent;
        """

    PARTS_SELECT = f"""
            font-family: {FONT_FAMILY};
            font-size: 14px;
            color: #d51e35;
            font-weight: bold;
            background: transparent;
            padding-bottom: 1px;
        """
