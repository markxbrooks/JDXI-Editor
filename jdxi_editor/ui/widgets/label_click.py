"""
Make the label next to a round JD-Xi button act as part of the button.

Editor actions are drawn as a 30 px round button with an icon and a text label
beside it (Load, Previous, Read from JD-Xi, ...). The label is a separate
widget, so a click on the words did nothing and only the small circle reacted.
``make_label_clickable`` installs a filter on the label row: a left click on it
clicks the round button next to it in the same layout, and the pointer shows a
hand over it. The button can also be given explicitly.
"""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtWidgets import QAbstractButton, QLayout, QWidget

#: A round button is at most this wide and as wide as it is high, with no text
_ROUND_BUTTON_MAX_SIZE = 48


def _is_round_button(widget: Optional[QWidget]) -> bool:
    if not isinstance(widget, QAbstractButton) or widget.text():
        return False
    width, height = widget.maximumWidth(), widget.maximumHeight()
    return width == height and width <= _ROUND_BUTTON_MAX_SIZE


def _neighbours_in_layout(layout: QLayout, target: QWidget) -> list[QWidget]:
    """The widgets just before and after *target* in *layout* (searched recursively)."""
    items = [layout.itemAt(i) for i in range(layout.count())]
    for index, item in enumerate(items):
        if item.widget() is target:
            around = []
            for j in (index - 1, index + 1):
                if 0 <= j < len(items) and items[j].widget() is not None:
                    around.append(items[j].widget())
            return around
        if item.layout() is not None:
            found = _neighbours_in_layout(item.layout(), target)
            if found:
                return found
    return []


def find_round_button_for(label_row: QWidget) -> Optional[QAbstractButton]:
    """The round button that belongs to *label_row*: explicit, else its layout neighbour."""
    explicit = label_row.property("jdxiButton")
    if isinstance(explicit, QAbstractButton):
        return explicit
    parent = label_row.parentWidget()
    if parent is None or parent.layout() is None:
        return None
    neighbours = _neighbours_in_layout(parent.layout(), label_row)
    # The button usually sits before its label; the one after is the next action's
    for widget in neighbours:
        if _is_round_button(widget):
            return widget
    return None


class _LabelClickForwarder(QObject):
    """Event filter forwarding left clicks on a label row to its round button."""

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        kind = event.type()
        if kind == QEvent.Type.Enter:
            button = find_round_button_for(watched)
            watched.setCursor(
                Qt.CursorShape.PointingHandCursor if button else Qt.CursorShape.ArrowCursor
            )
            return False
        if kind not in (QEvent.Type.MouseButtonPress, QEvent.Type.MouseButtonRelease):
            return False
        if event.button() != Qt.MouseButton.LeftButton:
            return False
        button = find_round_button_for(watched)
        if button is None or not button.isEnabled():
            return False
        if kind == QEvent.Type.MouseButtonPress:
            button.setDown(True)
            return True
        button.setDown(False)
        if watched.rect().contains(event.position().toPoint()):
            button.click()
        return True


def make_label_clickable(
    label_row: QWidget, button: Optional[QAbstractButton] = None
) -> QWidget:
    """
    Let a click on *label_row* click its round button.

    :param label_row: the widget with the button's icon and text
    :param button: the button; if omitted, the round button next to the row in its layout
    :return: label_row
    """
    if button is not None:
        label_row.setProperty("jdxiButton", button)
    if label_row.property("jdxiClickForwarder") is None:
        forwarder = _LabelClickForwarder(label_row)
        label_row.installEventFilter(forwarder)
        label_row.setProperty("jdxiClickForwarder", True)
    return label_row
