"""
Contains the WidgetType data class, which defines various types of widgets as
class attributes.
"""

from dataclasses import dataclass


@dataclass
class WidgetType:
    """WidgetType"""
    LINEEDIT: str = "line_edit"
    COMBOBOX: str = "combobox"
    CHECKBOX: str = "checkbox"
    PUSHBUTTON: str = "pushbutton"
