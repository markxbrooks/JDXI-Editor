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
    # COM_BG = "#000000"
    TITLE_TEXT = "#FFFFFF"
    BACKGROUND = "#000000"  # """"#1A1A1A"
    BACKGROUND_PRESSED = "#666666"
    BUTTON_BACKGROUND = "#222222"
    FOREGROUND = "#FFFFFF"
    PADDING = 2  # in px
    BUTTON_PADDING = 2
    ACCENT = "#FF2200"  # Red accent color
    ACCENT_HOVER = "#FF2200"  # Red for hover
    ACCENT_ANALOG = "#00A0E9"
    ACCENT_ANALOG_HOVER = "#00A0E9"
    BORDER = "#333333"
    SLIDER_HANDLE = "#000000"  # Black fill
    SLIDER_HANDLE_BORDER = "#666666"  # Light grey outline
    SLIDER_GROOVE = "#666666"  # grey groove
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
    FONT_FAMILY = "Myriad Pro, Arial, sans-serif"
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
        bg="#333333",
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
        background_pressed="#333333",
        button_border_width=1,
        font_family="Arial, sans-serif",
        font_size="12px",
        button_padding=5
    )

    JDXI_BUTTON_WAVEFORM_ANALOG = generate_button_style(
        bg=BUTTON_BACKGROUND,
        border=BACKGROUND_PRESSED,
        radius=3,
        text_color="#CCCCCC",
        hover="#444444",
        border_pressed=ACCENT_ANALOG,
        background_pressed="#333333",
        button_border_width=1,
        font_family="Arial, sans-serif",
        font_size="12px",
        button_padding=5
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

    JDXI_ADSR = """
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

    JDXI_LABEL_SUB = """
            font-family: "Myriad Pro", Arial;
            font-size: 13px;
            color: #d51e35;
            font-weight: bold;
        """

    JDXI_LABEL = """
            font-family: "Myriad Pro", Arial;
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
            font-size: 16px;
            font-weight: bold;
        """

    JDXI_LABEL_SYNTH_PART = """
                font-family: "Myriad Pro", Arial;
                font-size: 13px;
                color: #d51e35;  /* Base red */
                font-weight: bold;
            """

    JDXI_LABEL_ANALOG_SYNTH_PART = f"""
                font-family: "Myriad Pro", Arial;
                font-size: 13px;
                color: {ACCENT_ANALOG};  /* Blue for Analog */
                font-weight: bold;
            """

    JDXI_DRUM_GROUP = """
                QGroupBox {
                width: 100px;
            }
            """

    JDXI_PATCH_MANAGER = """
            QMainWindow {
                background-color: #2E2E2E;
            }
            QWidget {
                background-color: #2E2E2E;
                color: #FFFFFF;
                font-family: 'Myriad Pro';
            }
            QLineEdit {
                background-color: #1A1A1A;
                color: #FFFFFF;
                border: 1px solid #FF0000;
                border-radius: 3px;
                padding: 2px;
                font-family: 'Consolas';
            }
            QPushButton {
                background-color: #3D3D3D;
                color: #FFFFFF;
                border: 1px solid #FF0000;
                border-radius: 3px;
                padding: 2px 15px;
                font-family: 'Myriad Pro';
            }
            QPushButton:hover {
                background-color: #4D4D4D;
                border: 1px solid #FF3333;
            }
            QPushButton:border_pressed {
                background-color: #2D2D2D;
            }
            QLabel {
                color: #FFFFFF;
                font-family: 'Myriad Pro';
            }
        """

    JDXI_PARTIAL_SWITCH = """
                QCheckBox {
                    color: #CCCCCC;
                    font-size: 10px;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                    background: #333333;
                    border: 1px solid #555555;
                    border-radius: 8px;
                }
                QCheckBox::indicator:checked {
                    background: #666666;
                    border-color: #FF4444;
                }
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

    JDXI_DEBUGGER = """
            QMainWindow {
                background-color: #2E2E2E;
            }
            QWidget {
                background-color: #2E2E2E;
                color: #FFFFFF;
                font-family: 'Myriad Pro';
            }
            QPlainTextEdit {
                background-color: #1A1A1A;
                color: #FFFFFF;
                border: 1px solid #FF0000;
                border-radius: 3px;
                padding: 3px;
                font-family: 'Consolas';
            }
            QTextEdit {
                background-color: #1A1A1A;
                color: #FFFFFF;
                border: 1px solid #FF0000;
                border-radius: 3px;
                padding: 2px;
                font-family: 'Consolas';
            }
            QPushButton {
                background-color: #3D3D3D;
                color: #FFFFFF;
                border: 1px solid #FF0000;
                border-radius: 3px;
                padding: 2px 15px;
                font-family: 'Myriad Pro';
            }
            QPushButton:hover {
                background-color: #4D4D4D;
                border: 1px solid #FF3333;
            }
            QPushButton:border_pressed {
                background-color: #2D2D2D;
            }
        """

    JDXI_SEQUENCER = """
            font-family: "Myriad Pro", Arial;
            font-size: 14px;
            color: #d51e35;
            font-weight: bold;
            background: transparent;
        """

    JDXI_PARTS_SELECT = """
            font-family: "Myriad Pro", Arial;
            font-size: 14px;
            color: #d51e35;
            font-weight: bold;
            background: transparent;
            padding-bottom: 10px;
        """


