"""
Group box helpers for PySide6 UI.

Provides build_group and group_with_layout with consistent handling of
layout, list of widgets, or single widget. Supports optional attribute
setting via group_from_definition.
"""

from typing import Any, List, Optional, Protocol, Union

from PySide6.QtWidgets import (
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLayout,
    QVBoxLayout,
    QWidget,
)

from picoui.helpers.layout import create_layout, create_layout_with_items


class GroupDefinition(Protocol):
    """Protocol for group box definition (label and optional attr_name)."""

    label: str
    attr_name: str


def build_group(
    title: str,
    layout_or_widget: Union[List[QWidget], QWidget, QLayout, None],
) -> QGroupBox:
    """
    Create a QGroupBox with either a layout, a list of widgets, or a single widget.

    :param title: Group box title.
    :param layout_or_widget: A QLayout, list of QWidget, single QWidget, or None (empty layout).
    :return: Configured QGroupBox.
    :raises TypeError: If layout_or_widget is not a supported type.
    """
    group = QGroupBox(title)
    if isinstance(layout_or_widget, list):
        group.setLayout(create_layout_with_items(layout_or_widget))
    elif isinstance(layout_or_widget, QLayout):
        group.setLayout(layout_or_widget)
    elif isinstance(layout_or_widget, QWidget):
        group.setLayout(create_layout_with_items([layout_or_widget]))
    elif layout_or_widget is None:
        group.setLayout(create_layout(vertical=True))
    else:
        raise TypeError(
            f"layout_or_widget must be list[QWidget], QWidget, QLayout, or None; got {type(layout_or_widget)}"
        )
    return group


def group_with_layout(
    label: Optional[str] = None,
    layout: Optional[Union[QHBoxLayout, QVBoxLayout, QGridLayout, QFormLayout]] = None,
    vertical: bool = True,
    style_sheet: Optional[str] = None,
) -> tuple[QGroupBox, Union[QHBoxLayout, QVBoxLayout, QGridLayout, QFormLayout]]:
    """
    Create a QGroupBox and a layout; optionally set the layout and style.

    :param label: Optional group box title.
    :param layout: Optional existing layout; if None, a new layout is created.
    :param vertical: If True and layout is None, create QVBoxLayout; else QHBoxLayout.
    :param style_sheet: Optional stylesheet for the group.
    :return: Tuple of (QGroupBox, layout).
    """
    group = QGroupBox(label) if label else QGroupBox()
    if layout is None:
        layout = create_layout(vertical=vertical)
    group.setLayout(layout)
    if style_sheet is not None:
        group.setStyleSheet(style_sheet)
    return group, layout


def group_from_definition(
    key: GroupDefinition,
    layout_or_widget: Union[List[QWidget], QWidget, QLayout, None],
    set_attr: Optional[Any] = None,
    attr_name: Optional[str] = None,
) -> QGroupBox:
    """
    Create a QGroupBox using a definition (protocol with .label and .attr_name).
    Optionally set the result as an attribute on another object.

    :param key: Object with .label and .attr_name (e.g. enum or mixin).
    :param layout_or_widget: Layout, widget(s), or None for the group content.
    :param set_attr: If set, the created group is assigned to setattr(set_attr, attr_name, group).
    :param attr_name: Attribute name; defaults to key.attr_name.
    :return: The created QGroupBox.
    """
    group = build_group(key.label, layout_or_widget)
    if set_attr is not None:
        target_attr = attr_name if attr_name is not None else key.attr_name
        setattr(set_attr, target_attr, group)
    return group
