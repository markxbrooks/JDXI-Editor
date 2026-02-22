"""
This module provides utility functions for creating Qt UI elements based
on a `SettingsFieldSpec` specification or parameters. Functions include
the creation of checkboxes, buttons, and configurable line edits for use
in settings or forms.

Functions:
- create_checkbox_from_spec: Creates a QCheckBox using settings field
  specifications.
- create_button_from_spec: Creates a QPushButton using settings field
  specifications.
- create_settings_line_edit: Creates a QLineEdit with settings and
  additional optional parameters.
"""

from __future__ import annotations

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QCheckBox, QLineEdit, QPushButton

from picoui.dialogs.preferences.spec import SettingsFieldSpec
from picoui.widget.helper import create_button, create_checkbox


def create_checkbox_from_spec(spec: SettingsFieldSpec) -> QCheckBox:
    """Create a checkbox from a SettingsFieldSpec"""
    check_box = create_checkbox(label=spec.label, value=spec.value)
    return check_box


def create_button_from_spec(spec: SettingsFieldSpec) -> QPushButton:
    """Create a button from a SettingsFieldSpec"""
    button = create_button(label=spec.label, tooltip=spec.tooltip)
    return button


def create_settings_line_edit(
    key: str,
    default: str = "",
    placeholder: str | None = None,
    tooltip: str | None = None,
    type_=str,
    settings: QSettings = None,
) -> QLineEdit:
    """create settings line edit"""
    value = settings.value(key, default, type=type_)
    if value is None:
        value = default

    line_edit = QLineEdit()
    line_edit.setText(value)

    if placeholder:
        line_edit.setPlaceholderText(placeholder)

    if tooltip:
        line_edit.setToolTip(tooltip)

    return line_edit