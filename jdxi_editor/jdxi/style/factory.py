"""
Module: style helpers

This module provides functions for dynamically generating Qt style sheets for
various UI components, including sequencer buttons, general buttons, tabs, and editors.
These functions allow for flexible styling customization based on application states.

Functions:
----------
- generate_polyend_sequencer_button_style(is_checked: bool, is_current: bool) -> str:
    Generates a button style for a Polyend-style sequencer based on its checked and current step state.

- generate_sequencer_button_style(active: bool) -> str:
    Generates a QPushButton style for a step sequencer, updating colors based on active/inactive state.

- generate_button_style(bg, border, radius, text_color, hover, border_pressed, ...) -> str:
    Creates a flexible button style dynamically with customizable properties.

- generate_tab_style(bg, border, radius, text_color, hover_bg, hover_border, ...) -> str:
    Generates a QTabBar style for tabs with selectable and hover effects.

- generate_editor_style(accent, accent_hover, background, foreground, font_family, ...) -> str:
    Defines the style for an editor-like UI component, including sliders, buttons, and group boxes.

- toggle_button_style(button, checked: bool):
    Updates the given button's style based on whether it is checked.

- update_button_style(button, checked: bool):
    Toggles the button style dynamically.

- get_button_styles(active: bool) -> str:
    Returns a style sheet string for buttons in active or inactive states.

These functions help ensure a cohesive and visually distinct UI experience, particularly in MIDI sequencers or
other interactive applications.

"""
import platform

from PySide6.QtWidgets import QPushButton

if platform.system() == "Windows":
    FONT_FAMILY = "Segoe UI"
elif platform.system() == "Darwin":
    FONT_FAMILY = "Myriad Pro"
else:
    FONT_FAMILY = "Arial, sans-serif"


def generate_polyend_sequencer_button_style(
    self, is_checked: bool, is_current: bool = False
) -> str:
    """
    Generate button style based on state and current step

    :param self: The instance of the class
    :param is_checked: bool Whether the button is checked
    :param is_current: bool Whether the button is the current step
    :return: str The style sheet for the button
    """
    base_color = "#3498db" if is_checked else "#2c3e50"
    border_color = "#e74c3c" if is_current else base_color

    return f"""
        QPushButton {{
            font-family: {FONT_FAMILY};
            background-color: {base_color};
            border: 2px solid {border_color};
            border-radius: 5px;
            color: white;
            padding: 2px;
        }}
        QPushButton:hover {{
            background-color: {'#2980b9' if is_checked else '#34495e'};
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
            stop:0 #660000, stop:1 #ff1a1a);
        }}
        QPushButton:pressed {{
            background-color: {'#2472a4' if is_checked else '#2c3e50'};
        }}
    """


def generate_sequencer_button_style(active: bool) -> str:
    """
    Generate button style based on active state

    :param active: bool Whether the button is active
    :return: str The style sheet for the button
    """
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
    bg: str,
    border: str,
    radius: int,
    text_color: str,
    hover: str,
    border_pressed: str,
    background_pressed: str = "#666666",
    button_border_width: int = 4,
    font_family: str = FONT_FAMILY,
    font_size: str = "12px",
    button_padding: int = 4,
) -> str:
    """
    Generate address button style dynamically.

    :param border_pressed: str The border color when pressed
    :param background_pressed: str The background color when pressed
    :param button_border_width: int The border width of the button
    :param button_padding: int The padding of the button
    :param font_size: str The font size
    :param font_family: str The font family
    :param bg: str The background color
    :param border: str The border color
    :param radius: int The radius of the button
    :param text_color: str The text color
    :param hover: str The hover color
    """
    return f"""
            QPushButton {{
                font-family: {FONT_FAMILY};
                background-color: {bg};
                border: {button_border_width}px solid {border};
                border-radius: {radius}px;
                color: {text_color};
                font-family: "{font_family}";
                font-size: {font_size};
                padding: {button_padding}px;
            }}
            QPushButton:hover {{
                background-color: {hover};
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #660000, stop:1 {hover});
            }}
            QPushButton:border_pressed, QPushButton:checked {{
                background-color: {background_pressed};
                border: {button_border_width}px solid {border_pressed};
            }}
        """


def generate_tab_style(
    bg: str,
    border: str,
    radius: int,
    text_color: str,
    hover_bg: str,
    hover_border: str,
    selected_bg: str,
    selected_border: str,
    font_family: str = FONT_FAMILY,
    font_size: str = "12px",
    padding: str = "1px 1px",
    margin: str = "1px",
    accent: str = "#FF2200"
):
    """
    Generate address tab style dynamically.

    :param accent:
    :param selected_border:
    :param selected_bg:
    :param hover_border:
    :param font_family: str The font family
    :param margin: str The margin for the tab
    :param padding: str The padding for the tab
    :param font_size: str The font size
    :param bg: str The background color
    :param border: str The border color
    :param radius: int The radius of the tab
    :param text_color: str The text color
    :param hover_bg: str The hover background color
    """
    return f"""
                QTabBar::tab {{
                font-family: {FONT_FAMILY};
                background: {bg};
                color: {text_color};
                padding: {padding};
                margin: {margin};
                border: 2px solid {border};
                border-radius: {radius}px;
                font-family: "{font_family}";
                font-size: {font_size};
            }}

            QTabBar::tab:selected {{
                font-family: {FONT_FAMILY};
                background: {selected_bg};
                color: {text_color};
                border: 2px solid {selected_border};
                font-family: "{font_family}";
                font-size: {font_size};
            }}

            QTabBar::tab:hover {{
                background: {hover_bg};
                border: 2px solid {hover_border};
                font-family: "{font_family}";
                font-size: {font_size};
            }}
            QTabWidget {{
                font-family: {FONT_FAMILY};
                border: none
            }}
            QTabWidget::pane {{
                border: none;
            }}
        """

    # Editor Styles


def generate_editor_style(
    accent: str,
    accent_hover: str,
    background: str,
    foreground: str,
    font_family: str,
    font_size: str,
    padding: int,
    button_padding: int,
    slider_handle: str,
    slider_handle_border: str,
    slider_groove: str,
    slider_neon: str,
    slider_neon_gradient_stop: str,
    font_weight: str = "normal",
    box_width: str = "300px",
) -> str:
    """
    Generate editor style dynamically.

    :param box_width: str width of box widgets such as combo boxes, push button, line edit
    :param font_weight: str The font weight
    :param slider_neon_gradient_stop: str The gradient stop color for the slider handle
    :param slider_neon: str The neon color for the slider handle
    :param slider_groove: str The groove color for the slider
    :param font_family: str The font family
    :param font_size: str The font size
    :param padding: int The padding for the group box
    :param button_padding: int The padding for the button
    :param slider_handle: str The color of the slider handle
    :param slider_handle_border: str The color of the slider handle border
    :param accent: str The accent color
    :param accent_hover: str The accent hover color
    :param background: str The background color
    :param foreground: str The foreground color
    :return: str The style sheet for the editor
    """
    return f"""
        QWidget {{
            font-family: {FONT_FAMILY};
            background-color: {background};
            color: {foreground};
            font-family: "{font_family}";
            font-size: {font_size};
            padding: 1px;
        }}

        QGroupBox {{
            font-family: {font_family};
            border: none;
            border-top: 1px solid {accent};
            border-radius: 3px;
            margin-top: 1px;
            width: 300px;
            padding: {padding}px;
        }}
        
        QPushButton {{
            width: {box_width};
        }}
        
        QGroupBox[adsr="true"] {{
            min-height: 300px;  /* Reduced height for horizontal layout */
        }}

        QSlider::handle:vertical {{
            background: {slider_handle};
            border: 2px solid {slider_handle_border};
            margin: 1px 0;
            border-radius: 4px;
        }}

        QSlider::handle:vertical:hover {{
            border-color: {accent_hover};
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 1px;
            color: {foreground};
            font-weight: {font_weight};
        }}

        QPushButton {{
            font-family: {font_family};
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
            font-family: {font_family};
            background-color: {background};
            border: 1px solid {accent};
            border-radius: 3px;
            padding: 1px;
            color: {foreground};
        }}
        QComboBox {{
            width: {box_width};
        }}
        QComboBox:disabled {{
            color: #333333;
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
            height: 6px;
            border-radius: 2px;
        }}

        QSlider::handle:horizontal{{
            background: {slider_handle};
            border: 3px solid {slider_neon}; /* Neon red border */
            width: 8px;  /* More rectangular */
            height: 2px;  
            margin: -6px;
            padding: 1px;
            border-radius: 4px;
        }}
        QSlider::handle:disabled{{
            background: {slider_handle};
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
            background: {slider_handle};
            border: 2px solid {slider_handle_border};
            width: 18px;
            height: 12px;
            margin: -9px 0;
            border-radius: 9px;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                         stop:0 {slider_neon_gradient_stop}, stop:1 {slider_neon});
            border-radius: 3px;
        }}
        QSlider::handle:vertical:disabled{{
            background: {slider_handle};
            border: 2px solid #333333; /* grey border */
            width: 18px;  /* More rectangular */
            height: 12px;  
            margin: -9px;
            border-radius: 4px;
        }}
        /* Glowing effect when moving */
        QSlider::sub-page:horizontal {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                         stop:0 {slider_neon_gradient_stop}, stop:1 {slider_neon});
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
            color: #FFFFFF;
            font-family: {FONT_FAMILY};
        }}
        QSlider::horizontal {{
            margin-left: 5px;
            margin-right: 5px;
        }}
    """


def get_button_styles(active: bool) -> str:
    """
    Returns the appropriate style for active/inactive button states

    :param active: bool Whether the button is active
    :return: str The style sheet for the button
    """
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
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
            stop:0 #660000, stop:1 #ff1a1a);
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


def toggle_button_style(button: QPushButton, checked: bool):
    """Update button style based on its checked state
    :param button: QPushButton The button to update
    :param checked: bool Whether the button is checked
    """
    button.setStyleSheet(
        generate_sequencer_button_style(checked)
    )  # Example style for checked


def update_button_style(button: QPushButton, checked: bool):
    """Toggle the button style based on the state
    :param button: QPushButton The button to update
    :param checked: bool Whether the button is checked
    """
    button.setStyleSheet(get_button_styles(checked))
