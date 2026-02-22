"""
Defines the SettingsFieldSpec dataclass, which outlines the specifications
for a settings field. This includes attributes such as label, key, icon,
widget type, and other related properties.

The SettingsFieldSpec class is designed to provide a structured definition
for a settings field, commonly used in UI components or configurations.
"""

from __future__ import annotations

from dataclasses import dataclass

from picoui.widget.type import WidgetType


@dataclass
class SettingsFieldSpec:
    label: str
    key: str = None
    icon: str = None
    widget_type: str = WidgetType.LINEEDIT
    default: str = ""
    value: str | bool | int = None
    placeholder: str | None = None
    tooltip: str | None = None