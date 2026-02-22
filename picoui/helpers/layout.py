"""
Layout assembly utilities for PySide6 UI.

Provides create_layout, create_layout_with_widgets, create_row_with_widgets,
and related helpers with consistent typing and behavior.
"""

from typing import List, Optional, Union

from PySide6.QtCore import QMargins
from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLayout,
    QVBoxLayout,
    QWidget,
)


def create_layout(
    vertical: bool = True,
    parent_widget: Optional[QWidget] = None,
) -> Union[QVBoxLayout, QHBoxLayout]:
    """
    Create a QVBoxLayout or QHBoxLayout, optionally attached to a parent.

    :param vertical: If True, create QVBoxLayout; else QHBoxLayout.
    :param parent_widget: Optional widget to set as the layout's parent.
    :return: The created layout.
    """
    layout_cls = QVBoxLayout if vertical else QHBoxLayout
    if parent_widget is not None:
        return layout_cls(parent_widget)
    return layout_cls()


def create_layout_with_widgets(
    widgets: List[QWidget],
    vertical: bool = False,
    top_stretch: bool = True,
    bottom_stretch: bool = True,
    spacing: Optional[int] = None,
    margins: Optional[QMargins] = None,
    parent_widget: Optional[QWidget] = None,
) -> Union[QHBoxLayout, QVBoxLayout]:
    """
    Create a row (or column) from a list of widgets, with optional stretches.

    :param widgets: List of widgets to add.
    :param vertical: If True, use QVBoxLayout; else QHBoxLayout.
    :param top_stretch: Add stretch before widgets.
    :param bottom_stretch: Add stretch after widgets.
    :param spacing: Optional spacing between items.
    :param margins: Optional layout margins.
    :param parent_widget: Optional parent widget for the layout.
    :return: The created layout (HBox or VBox).
    """
    layout = create_layout(vertical=vertical, parent_widget=parent_widget)
    if top_stretch:
        layout.addStretch()
    for widget in widgets:
        layout.addWidget(widget)
    if bottom_stretch:
        layout.addStretch()
    if spacing is not None:
        layout.setSpacing(spacing)
    if margins is not None:
        layout.setContentsMargins(margins)
    return layout


def create_row_with_widgets(widgets: List[QWidget], spacing: int = 4) -> QHBoxLayout:
    """
    Create a horizontal layout with widgets and no stretches.

    :param widgets: List of widgets to add.
    :param spacing: Spacing between widgets.
    :return: QHBoxLayout.
    """
    row = QHBoxLayout()
    row.setSpacing(spacing)
    for widget in widgets:
        row.addWidget(widget)
    return row


def create_left_aligned_row(widgets: List[QWidget]) -> QHBoxLayout:
    """
    Create a left-aligned horizontal layout (stretch only on the right).

    :param widgets: List of widgets to add.
    :return: QHBoxLayout with widgets left-aligned.
    """
    row = QHBoxLayout()
    for widget in widgets:
        row.addWidget(widget)
    row.addStretch()
    return row


def create_vertical_layout(
    spacing: Optional[int] = None,
    margins: Optional[QMargins] = None,
) -> QVBoxLayout:
    """
    Create a QVBoxLayout with optional spacing and margins.

    :param spacing: Optional spacing.
    :param margins: Optional margins (default 0,0,0,0).
    :return: QVBoxLayout.
    """
    layout = QVBoxLayout()
    if margins is not None:
        layout.setContentsMargins(margins)
    if spacing is not None:
        layout.setSpacing(spacing)
    return layout


def create_form_layout(parent: Optional[QWidget] = None) -> QFormLayout:
    """
    Create a form layout with zero margins and small spacing.

    :param parent: Optional parent widget.
    :return: QFormLayout.
    """
    layout = QFormLayout(parent)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(4)
    return layout


def create_layout_with_inner_layouts(
    inner_layouts: List[QLayout],
    vertical: bool = True,
) -> QVBoxLayout:
    """
    Create a layout that contains a list of inner layouts, plus a bottom stretch.

    :param inner_layouts: Layouts to add.
    :param vertical: If True, use QVBoxLayout; else QHBoxLayout.
    :return: The outer layout.
    """
    layout = create_layout(vertical=vertical)
    for inner in inner_layouts:
        layout.addLayout(inner)
    layout.addStretch()
    return layout


def create_header_row(
    label: str,
    show_label: bool,
    spacing: int = 4,
) -> tuple[QHBoxLayout, QLabel]:
    """
    Create a header row with an optional label.

    :param label: Text for the label.
    :param show_label: Whether the label is visible.
    :param spacing: Spacing for the row layout.
    :return: Tuple of (QHBoxLayout, QLabel).
    """
    row = QHBoxLayout()
    row.setSpacing(spacing)
    label_widget = QLabel(label)
    label_widget.setVisible(show_label)
    row.addWidget(label_widget)
    return row, label_widget
