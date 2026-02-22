"""
This module provides convenience functions for creating PySide6 UI components
such as checkboxes, buttons, button boxes, and row layouts.

These functions simplify the creation and configuration of commonly used
Qt widgets, allowing for consistent layout structures and streamlined
UI initialization.
"""

from typing import Any, Callable

from PySide6.QtWidgets import (QComboBox, QFileDialog, QLineEdit, QFormLayout,
                               QWidget)

from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import (QCheckBox, QDialogButtonBox, QHBoxLayout,
                               QLabel, QPushButton)

from picoui.icons import IconRegistry
from picoui.specs.widgets import (
    ButtonSpec,
    CheckBoxSpec,
    ComboBoxSpec,
    FileSelectionSpec,
)


def create_button_box(
    label: str = "OK", parent: QWidget = None
) -> tuple[QDialogButtonBox, QPushButton]:
    """create button box"""
    button_box = QtWidgets.QDialogButtonBox(parent)
    button_box.setGeometry(QtCore.QRect(150, 250, 341, 32))
    button_box.setOrientation(QtCore.Qt.Horizontal)
    button_box.setStandardButtons(
        QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok
    )
    button_box.setObjectName("button_box")
    # Add Reset to Defaults button
    reset_button = button_box.addButton(label, QtWidgets.QDialogButtonBox.ActionRole)
    return button_box, reset_button


def create_row(
    icon_name: str,
    label_text: str,
    widget: QWidget,
) -> QHBoxLayout:
    """create row layout"""
    layout = QHBoxLayout()

    icon = QLabel()
    icon.setPixmap(IconRegistry.get_icon(icon_name))
    label = QLabel(label_text)

    layout.addWidget(icon)
    layout.addWidget(label)
    layout.addWidget(widget)

    return layout


def create_checkbox(label: str = None, value: bool = False) -> QCheckBox:
    """Create a checkbox from label and value, or from a CheckBoxSpec."""
    check_box = QCheckBox(label or "")
    check_box.setLayoutDirection(QtCore.Qt.RightToLeft)
    check_box.setChecked(bool(value))
    return check_box


def create_checkbox_from_spec(spec: CheckBoxSpec) -> QCheckBox:
    """Create a checkbox from a CheckBoxSpec."""
    check_box = create_checkbox(label=spec.label, value=spec.checked_state)
    if spec.tooltip:
        check_box.setToolTip(spec.tooltip)
    if spec.slot is not None:
        check_box.stateChanged.connect(spec.slot)
    return check_box


def create_button(
    label: str = None, tooltip: str = None, spec: ButtonSpec = None
) -> QPushButton:
    """Create a button from label/tooltip or from a ButtonSpec."""
    if spec is not None:
        label = spec.label or ""
        tooltip = spec.tooltip or None
    button = QPushButton(label or "")
    if tooltip:
        button.setToolTip(tooltip)
    if spec is not None and spec.slot is not None:
        button.clicked.connect(spec.slot)
    return button


def create_button_from_spec(spec: ButtonSpec) -> QPushButton:
    """Create a button from a ButtonSpec."""
    return create_button(spec=spec)


def create_combo_box(
    all_items_label: str = None,
    items: list = None,
    slot: Callable = None,
    spec: ComboBoxSpec = None,
) -> QComboBox:
    """Create a combo box from arguments or from a ComboBoxSpec."""
    if spec is not None:
        items = spec.items or []
        slot = spec.slot
        combo = QComboBox()
        combo.addItems(items)
        if spec.tooltip:
            combo.setToolTip(spec.tooltip)
        if slot is not None:
            combo.currentTextChanged.connect(slot)
        return combo
    combo = QComboBox()
    if all_items_label is not None:
        combo.addItem(all_items_label)
    if items is not None:
        combo.addItems(sorted(set(items)))
    if slot is not None:
        combo.currentTextChanged.connect(slot)
    return combo


def create_row_with_widgets(widgets: list[QWidget]):
    """create row with widgets"""
    row = QHBoxLayout()
    row.setSpacing(4)
    for widget in widgets:
        row.addWidget(widget)
    return row


def create_combo_row(label: str = None, all_items_label: str = None, items: list = None, slot=None) -> tuple[
    QHBoxLayout, QComboBox]:
    """create combo row"""
    label_widget = QLabel(label)
    combo = create_combo_box(all_items_label, items, slot)
    widgets = [
        label_widget,
        combo
    ]
    row = create_row_with_widgets(widgets)
    return row, combo


def create_line_edit(style_sheet: str, placeholder: str, slot: Callable) -> QLineEdit:
    """create line edit"""
    line_edit = QLineEdit()
    line_edit.setStyleSheet(style_sheet)
    line_edit.setPlaceholderText(placeholder)
    line_edit.textChanged.connect(slot)
    return line_edit


def create_header_row(label: str, show_label: bool, spacing: int = 4) -> tuple[QHBoxLayout, Any]:
    """create a header row"""
    row = QHBoxLayout()
    row.setSpacing(spacing)
    label_widget = QLabel(label)
    label_widget.setVisible(show_label)
    row.addWidget(label_widget)
    return row, label_widget


def create_form_layout(parent) -> QFormLayout:
    """Create form layout"""
    layout = QFormLayout(parent)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(4)
    return layout


def get_file_path_from_spec(
    parent: QWidget, spec: FileSelectionSpec, start_dir: str = ""
) -> str | None:
    """Open a file dialog from a FileSelectionSpec; returns selected path or None."""
    if spec.mode == "save":
        path, _ = QFileDialog.getSaveFileName(
            parent,
            spec.caption,
            start_dir or spec.default_name,
            spec.filter,
        )
    else:
        path, _ = QFileDialog.getOpenFileName(
            parent,
            spec.caption,
            start_dir,
            spec.filter,
        )
    return path if path else None
