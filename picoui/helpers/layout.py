"""
Layout assembly utilities for PySide6 UI.

Provides create_layout, create_layout_with_widgets, create_row_with_widgets,
and related helpers with consistent typing and behavior.
"""
from __future__ import annotations

from typing import List, Optional, Union

from PySide6.QtCore import QMargins, Qt
from PySide6.QtWidgets import (QFormLayout, QGroupBox, QHBoxLayout, QLabel,
                               QLayout, QVBoxLayout, QWidget, QProgressBar, QSplitter)

from picoui.specs.widgets import ProgressBarSpec


def create_layout(
    vertical: bool = True,
    parent: Optional[QWidget] = None,
    margins: tuple[int, int, int, int] = (0, 0, 0, 0),
    spacing: int = 10,
) -> Union[QVBoxLayout, QHBoxLayout]:
    """
    Create a QVBoxLayout or QHBoxLayout, optionally attached to a parent.

    :param margins: tuple of margins e.g. (0, 0, 0, 0)
    :param vertical: If True, create QVBoxLayout; else QHBoxLayout.
    :param parent: Optional widget to set as the layout's parent.
    :return: The created layout.
    """
    layout_cls = QVBoxLayout if vertical else QHBoxLayout
    if parent is not None:
        layout = layout_cls(parent)
    else:
        layout = layout_cls()
    if margins is not None:
        layout.setContentsMargins(*margins)
    if spacing is not None:
        layout.setSpacing(spacing)
    return layout


LayoutItem = Union[QWidget, QHBoxLayout, QVBoxLayout, QProgressBar, QFormLayout]


def create_group(layout: QHBoxLayout | QVBoxLayout,
                 style_sheet: str = None,
                 width: int = None,
                 height: int = None) -> QGroupBox:
    """create group with optional stylesheet, width and height"""
    group = QGroupBox()
    group.setLayout(layout)
    if style_sheet is not None:
        group.setStyleSheet(style_sheet)
    if width is not None:
        group.setMinimumWidth(width)
    if height is not None:
        group.setMaximumHeight(height)
    return group


def create_progress_bar_from_spec(spec: ProgressBarSpec) -> QProgressBar:
    """Create a progress bar from a :class:`~picoui.specs.widgets.ProgressBarSpec`."""
    return create_progress_bar(
        range_min=spec.range_min,
        range_max=spec.range_max,
        start_value=spec.start_value,
        height=spec.height,
        text_visible=spec.text_visible,
        format_text=spec.format_text,
    )


def create_progress_bar(range_min: int = 0,
                        range_max: int = 100,
                        start_value: int =0,
                        height: int=22,
                        text_visible: bool =True,
                        format_text: str = "loading") -> QProgressBar:
    """create progress bar"""
    progress_bar = QProgressBar()
    progress_bar.setRange(range_min, range_max)
    progress_bar.setValue(start_value)
    progress_bar.setFixedHeight(height)
    progress_bar.setTextVisible(text_visible)
    progress_bar.setFormat(f"%p% — {format_text}…")
    return progress_bar


def create_layout_with_items(
    items: List[LayoutItem | None] | None = None,
    vertical: bool = False,
    start_stretch: bool = True,
    end_stretch: bool = True,
    spacing: Optional[int] = None,
    margins: Optional[Union[QMargins, tuple] ] = None,
    parent: Optional[QWidget] = None,
) -> Union[QHBoxLayout, QVBoxLayout]:
    """
    Create a row (or column) from a list of widgets, with optional stretches.

    :param items: List of widgets or layouts to add.
    :param vertical: If True, use QVBoxLayout; else QHBoxLayout.
    :param start_stretch: Add stretch before widgets.
    :param end_stretch: Add stretch after widgets.
    :param spacing: Optional spacing between items.
    :param margins: Optional layout margins.
    :param parent: Optional parent widget for the layout.
    :return: The created layout (HBox or VBox).
    """
    container_layout = create_layout(vertical=vertical, parent=parent)
    if start_stretch:
        container_layout.addStretch()
    add_items_to_layout(container_layout, items)
    if end_stretch:
        container_layout.addStretch()
    if spacing is not None:
        container_layout.setSpacing(spacing)
    if margins is not None:
        if isinstance(margins, QMargins):
            container_layout.setContentsMargins(margins)
        if isinstance(margins, tuple):
            container_layout.setContentsMargins(*margins)
    return container_layout


def add_items_to_layout(container_layout: QVBoxLayout | QHBoxLayout,
                        items: list[QWidget | QHBoxLayout | QVBoxLayout | QProgressBar | QFormLayout | None] | None):
    """Add items to layout"""
    if items is not None:
        for item in items:
            # Must not use Union[QWidget, QLayout] with isinstance: QWidget wins for buttons,
            # so layouts would never be chosen correctly and widgets would get addLayout().
            if isinstance(item, QLayout):
                container_layout.addLayout(item)
            else:
                container_layout.addWidget(item)


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
    alignment: Qt.AlignmentFlag = Qt.AlignCenter
) -> QVBoxLayout:
    """
    Create a QVBoxLayout with optional spacing and margins.

    :param alignment: Optional alignment.
    :param spacing: Optional spacing.
    :param margins: Optional margins (default 0,0,0,0).
    :return: QVBoxLayout.
    """
    layout = QVBoxLayout()
    if margins is not None:
        layout.setContentsMargins(margins)
    if alignment is not None:
        layout.setAlignment(alignment)
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


def create_widget_with_layout(layout: QLayout) -> QWidget:
    """create a simple widget with a given layout"""
    widget = QWidget()
    widget.setLayout(layout)
    return widget


def create_layout_with_inner_layouts(
    inner_layouts: List[QLayout], vertical: bool = True, stretch: bool = True
) -> QVBoxLayout:
    """
    Create a layout that contains a list of inner layouts, plus a bottom stretch.

    :param stretch: bool whether to add stretch
    :param inner_layouts: Layouts to add.
    :param vertical: If True, use QVBoxLayout; else QHBoxLayout.
    :return: The outer layout.
    """
    layout = create_layout(vertical=vertical)
    for inner in inner_layouts:
        layout.addLayout(inner)
    if stretch:
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


def create_splitter_with_items(items: list[QWidget], sizes) -> QSplitter:
    splitter = QSplitter(Qt.Vertical)
    for item in items:
        splitter.addWidget(item)
    splitter.setSizes(sizes)
    return splitter


def create_widget_layout(widget: QWidget) -> QVBoxLayout:
    lower_layout = QVBoxLayout()
    lower_layout.addWidget(widget)
    return lower_layout