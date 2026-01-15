"""
Helpers to create HBox and VBoxes
"""

from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout


def create_hrow_layout(widget_list: list) -> QHBoxLayout:
    """create a row from a list of widgets"""
    row = QHBoxLayout()
    row.addStretch()
    for widget in widget_list:
        row.addWidget(widget)
    row.addStretch()
    return row


def create_vcolumn_layout(inner_layout: QHBoxLayout) -> QVBoxLayout:
    """create vbox layout"""
    vlayout = QVBoxLayout()
    vlayout.addLayout(inner_layout)
    return vlayout
