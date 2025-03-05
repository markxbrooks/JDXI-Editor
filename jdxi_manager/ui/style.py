from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import Qt


def generate_polyend_sequencer_button_style(self, is_checked: bool, is_current: bool = False) -> str:
    """Generate button style based on state and current step"""
    base_color = "#3498db" if is_checked else "#2c3e50"
    border_color = "#e74c3c" if is_current else base_color

    return f"""
        QPushButton {{
            background-color: {base_color};
            border: 2px solid {border_color};
            border-radius: 5px;
            color: white;
            padding: 5px;
        }}
        QPushButton:hover {{
            background-color: {'#2980b9' if is_checked else '#34495e'};
        }}
        QPushButton:pressed {{
            background-color: {'#2472a4' if is_checked else '#2c3e50'};
        }}
    """

def generate_sequencer_button_style(active):
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
        QPushButton:border_pressed {{
            background-color: #333333;
            border-color: #ff6666;
        }}
    """


def generate_button_style(
    bg,
    border,
    radius,
    text_color,
    hover,
    border_pressed,
    background_pressed="#666666",
    button_border_width=4,
    font_family="Myriad Pro, Arial, sans-serif",
    font_size="12px",
    button_padding=8,
):
    """Generate address button style dynamically."""
    return f"""
            QPushButton {{
                background-color: {bg};
                border: {button_border_width}px solid {border};
                border-radius: {radius}px;
                color: {text_color};
                font-family: {font_family};
                font-size: {font_size};
                padding: {button_padding}px;
            }}
            QPushButton:hover {{
                background-color: {hover};
            }}
            QPushButton:border_pressed, QPushButton:checked {{
                background-color: {background_pressed};
                border: {button_border_width}px solid {border_pressed};
            }}
        """


def generate_tab_style(
    bg,
    border,
    radius,
    text_color,
    hover_bg,
    hover_border,
    selected_bg,
    selected_border,
    font_family="Myriad Pro, Arial, sans-serif",
    font_size="12px",
    padding="8px 12px",
    margin="2px",
):
    """Generate address tab style dynamically."""
    return f"""
            QTabBar::tab {{
                background: {bg};
                color: {text_color};
                padding: {padding};
                margin: {margin};
                border: 2px solid {border};
                border-radius: {radius}px;
                font-family: {font_family};
                font-size: {font_size};
            }}

            QTabBar::tab:selected {{
                background: {selected_bg};
                color: {text_color};
                border: 2px solid {selected_border};
                font-family: {font_family};
                font-size: {font_size};
            }}

            QTabBar::tab:hover {{
                background: {hover_bg};
                border: 2px solid {hover_border};
                font-family: {font_family};
                font-size: {font_size};
            }}

            QTabWidget::pane {{
                border: 1px solid {selected_border};
            }}
        """

    # Editor Styles


def generate_editor_style(
    accent,
    accent_hover,
    background,
    foreground,
    font_family,
    font_size,
    button_padding,
    slider_handle,
    slider_handle_border,
    slider_groove,
):
    return f"""
        QWidget {{
            background-color: {background};
            color: {foreground};
            font-family: {font_family};
            font-size: {font_size};
            padding: 2px;
        }}

        QGroupBox {{
            border: 1px solid {accent};
            border-radius: 3px;
            margin-top: 1.5ex;
            padding: {button_padding}px;
        }}
        
        QGroupBox[adsr="true"] {{
            min-height: 400px;  /* Reduced height for horizontal layout */
        }}
        
        QSlider::handle:vertical {{
            background: {slider_handle};
            border: 2px solid {slider_handle_border};
            width: 18px;
            height: 18px;
            margin: -9px 0;
            border-radius: 3px;
        }}
        
        QSlider::handle:vertical:hover {{
            border-color: {accent_hover};
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 3px;
            color: {foreground};
        }}

        QPushButton {{
            background-color: {background};
            border: 1px solid {accent};
            border-radius: 3px;
            padding: {button_padding}px;
            color: {foreground};
        }}

        QPushButton:hover, QPushButton:checked {{
            background-color: {accent};
            color: {background};
        }}

        QComboBox, QScrollBar {{
            background-color: {background};
            border: 1px solid {accent};
            border-radius: 3px;
            padding: 3px;
            color: {foreground};
        }}

        QScrollBar::handle {{
            background: {slider_handle_border};
            border-radius: 3px;
        }}

        QScrollBar::handle:hover {{
            border: 2px solid {accent};
        }}

        QSlider::groove:horizontal {{
            background: {slider_groove};
            height: 2px;
            border-radius: 1px;
        }}

        QSlider::handle:horizontal, QSlider::handle:vertical {{
            background: {slider_handle};
            border: 2px solid {slider_handle_border};
            width: 18px;
            height: 18px;
            margin: -9px 0;
            border-radius: 9px;
        }}
    """


class Style:
    """Central style definitions for JD-Xi Manager"""

    # Colors
    # COM_BG = "#000000"
    TITLE_TEXT = "#FFFFFF"
    BACKGROUND = "#000000"  # """"#1A1A1A"
    BACKGROUND_PRESSED = "#666666"
    FOREGROUND = "#FFFFFF"
    PADDING = 2  # in px
    BUTTON_PADDING = 3
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
    BUTTON_PADDING = 8
    HANDLE_SIZE = "6px"
    GROOVE_WIDTH = "2px"
    ICON_SIZE = 20
    TAB_BUTTON_RADIUS = 6

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
        bg="#222222",
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
        bg="#222222",
        border=ACCENT_HOVER,
        radius=BUTTON_ROUND_RADIUS,
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
        bg="#222222",
        border=ACCENT_ANALOG,
        radius=BUTTON_RECT_RADIUS,
        text_color=FOREGROUND,
        hover=ACCENT_ANALOG_HOVER,
        border_pressed=ACCENT_ANALOG_PRESSED,
    )

    # Define Tab styles using get_tab_style function
    JDXI_TABS = generate_tab_style(
        bg="#000000",
        border="#666666",
        radius=TAB_BUTTON_RADIUS,
        text_color="white",
        hover_bg="#222222",
        hover_border="#ff9999",
        selected_bg="#222222",
        selected_border="#ff6666",
    )

    JDXI_TABS_ANALOG = generate_tab_style(
        bg="#000000",
        border="#666666",
        radius=TAB_BUTTON_RADIUS,
        text_color="white",
        hover_bg="#00A0C1",
        hover_border="#00A0E9",
        selected_bg="#222222",
        selected_border="#00A0E9",
    )

    JDXI_TABS_DRUMS = generate_tab_style(
        bg="#000000",
        border="#666666",
        radius=TAB_BUTTON_RADIUS,
        text_color="white",
        hover_bg="#222222",
        hover_border="#ff9999",
        selected_bg="#222222",
        selected_border="#ff6666",
    )

    JDXI_EDITOR = generate_editor_style(
        ACCENT,
        ACCENT_HOVER,
        BACKGROUND,
        FOREGROUND,
        FONT_FAMILY,
        FONT_SIZE,
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
                width: 240px;
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
            QPushButton:border_pressed {
                background-color: #2D2D2D;
            }
            QLabel {
                color: #FFFFFF;
                font-family: 'Myriad Pro';
            }
        """

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
                padding: 5px;
                font-family: 'Consolas';
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


def toggle_button_style(button, checked):
    """Update button style based on its checked state"""
    button.setStyleSheet(
        generate_sequencer_button_style(checked)
    )  # Example style for checked


def update_button_style(button, checked):
    """Toggle the button style based on the state"""
    button.setStyleSheet(get_button_styles(checked))


def get_button_styles(active):
    """Returns the appropriate style for active/inactive states"""
    base_style = """
        QPushButton {
            border-radius: 15px;
            border: 4px solid;
        }
        QPushButton:border_pressed {
            background-color: #333333;
            border: 4px solid #ff6666;
        }
        QPushButton:hover {
            background-color: #1A1A1A;
            border: 4px solid #ff4d4d;
        }
    """
    if active:
        return (
            base_style
            + """
            QPushButton {
                background-color: #333333;
                border-color: #ff6666;
            }
        """
        )
    else:
        return (
            base_style
            + """
            QPushButton {
                background-color: #222222;
                border-color: #666666;
            }
        """
        )
