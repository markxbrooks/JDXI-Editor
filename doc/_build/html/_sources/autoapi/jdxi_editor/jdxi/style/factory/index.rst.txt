jdxi_editor.jdxi.style.factory
==============================

.. py:module:: jdxi_editor.jdxi.style.factory

.. autoapi-nested-parse::

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



Attributes
----------

.. autoapisummary::

   jdxi_editor.jdxi.style.factory.FONT_FAMILY


Functions
---------

.. autoapisummary::

   jdxi_editor.jdxi.style.factory.generate_polyend_sequencer_button_style
   jdxi_editor.jdxi.style.factory.generate_sequencer_button_style
   jdxi_editor.jdxi.style.factory.generate_button_style
   jdxi_editor.jdxi.style.factory.generate_tab_style
   jdxi_editor.jdxi.style.factory.generate_editor_style
   jdxi_editor.jdxi.style.factory.get_button_styles
   jdxi_editor.jdxi.style.factory.toggle_button_style
   jdxi_editor.jdxi.style.factory.update_button_style


Module Contents
---------------

.. py:data:: FONT_FAMILY
   :value: 'Segoe UI'


.. py:function:: generate_polyend_sequencer_button_style(self, is_checked: bool, is_current: bool = False) -> str

   Generate button style based on state and current step

   :param self: The instance of the class
   :param is_checked: bool Whether the button is checked
   :param is_current: bool Whether the button is the current step
   :return: str The style sheet for the button


.. py:function:: generate_sequencer_button_style(active: bool) -> str

   Generate button style based on active state

   :param active: bool Whether the button is active
   :return: str The style sheet for the button


.. py:function:: generate_button_style(bg: str, border: str, radius: int, text_color: str, hover: str, border_pressed: str, background_pressed: str = '#666666', button_border_width: int = 4, font_family: str = FONT_FAMILY, font_size: str = '12px', button_padding: int = 4) -> str

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


.. py:function:: generate_tab_style(bg: str, border: str, radius: int, text_color: str, hover_bg: str, hover_border: str, selected_bg: str, selected_border: str, font_family: str = FONT_FAMILY, font_size: str = '12px', padding: str = '1px 1px', margin: str = '1px', accent: str = '#FF2200')

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


.. py:function:: generate_editor_style(accent: str, accent_hover: str, background: str, foreground: str, font_family: str, font_size: str, padding: int, button_padding: int, slider_handle: str, slider_handle_border: str, slider_groove: str, slider_neon: str, slider_neon_gradient_stop: str, font_weight: str = 'normal', box_width: str = '100px') -> str

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


.. py:function:: get_button_styles(active: bool) -> str

   Returns the appropriate style for active/inactive button states

   :param active: bool Whether the button is active
   :return: str The style sheet for the button


.. py:function:: toggle_button_style(button: PySide6.QtWidgets.QPushButton, checked: bool)

   Update button style based on its checked state
   :param button: QPushButton The button to update
   :param checked: bool Whether the button is checked


.. py:function:: update_button_style(button: PySide6.QtWidgets.QPushButton, checked: bool)

   Toggle the button style based on the state
   :param button: QPushButton The button to update
   :param checked: bool Whether the button is checked


