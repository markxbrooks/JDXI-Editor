from typing import Callable

from PySide6.QtWidgets import QComboBox, QWidget, QHBoxLayout, QLabel, QLineEdit


def create_combo_box(all_items_label: str = None, items: list = None, slot: Callable = None) -> QComboBox:
    """create combo box"""
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
