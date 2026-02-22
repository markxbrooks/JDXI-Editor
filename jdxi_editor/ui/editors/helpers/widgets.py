"""
Helpers for editors
"""

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QSpinBox,
    QWidget,
)

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.ui.style import JDXiUIDimensions, JDXiUIStyle
from picoui.specs.widgets import ButtonSpec


def set_widget_value_safely(widget: QWidget, value: int) -> None:
    """
    Block signals for the widget, set its value, then unblock signals.

    :param widget: The widget whose value is to be set.
    :param value: The value to set on the widget.
    """
    widget.blockSignals(True)
    if isinstance(widget, QSlider):
        widget.setValue(value)
    elif isinstance(widget, QComboBox):
        widget.setCurrentIndex(value)
    elif isinstance(widget, QSpinBox):
        widget.setValue(value)
    # Add other widget types as needed
    widget.blockSignals(False)


def get_icon_pixmap(icon_name) -> QPixmap | None:
    """get icon pixmap for given name"""
    icon_pixmap = JDXi.UI.Icon.get_icon_pixmap(
        icon_name, color=JDXi.UI.Style.FOREGROUND, size=20
    )
    return icon_pixmap


def create_jdxi_button_with_label_from_spec(
    spec: ButtonSpec, checkable: bool = True
) -> tuple[QWidget, QPushButton]:
    button = create_jdxi_button_from_spec(spec, checkable=checkable)
    classify_tracks_icon_pixmap = get_icon_pixmap(icon_name=spec.icon)
    row, _ = create_jdxi_row(
        spec.label,
        icon_pixmap=classify_tracks_icon_pixmap,
    )
    return row, button


def create_jdxi_button_from_spec(
    spec: ButtonSpec, button_group: QButtonGroup = None, checkable: bool = True
) -> QPushButton:
    """Create a round JD-Xi styled button with optional tooltip."""
    button = QPushButton()
    button.setStyleSheet(JDXiUIStyle.BUTTON_ROUND)
    button.setFixedWidth(JDXiUIDimensions.BUTTON_ROUND.WIDTH)
    button.setFixedHeight(JDXiUIDimensions.BUTTON_ROUND.HEIGHT)
    button.setToolTip(getattr(spec, "tooltip", "") or "")
    button.setCheckable(checkable)
    if getattr(spec, "slot", None) is not None:
        button.clicked.connect(spec.slot)
    if getattr(spec, "grouped", False) and button_group is not None:
        button_group.addButton(button)
    return button


def create_jdxi_button(tooltip: str = "") -> QPushButton:
    """Create a round JD-Xi styled button with optional tooltip."""
    button = QPushButton()
    button.setStyleSheet(JDXiUIStyle.BUTTON_ROUND)
    button.setFixedWidth(JDXiUIDimensions.BUTTON_ROUND.WIDTH)
    button.setFixedHeight(JDXiUIDimensions.BUTTON_ROUND.HEIGHT)
    button.setToolTip(tooltip)
    return button


def create_jdxi_row(
    label: str = "", icon_pixmap: QPixmap | None = None
) -> tuple[QWidget, QLabel]:
    """Create Row"""
    label_row = QWidget()
    label_layout = QHBoxLayout(label_row)
    label_layout.setContentsMargins(0, 0, 0, 0)
    label_layout.setSpacing(4)
    if icon_pixmap and not icon_pixmap.isNull():
        icon_label = QLabel()
        icon_label.setPixmap(icon_pixmap)
        label_layout.addWidget(icon_label)
    label = QLabel(label)
    label.setStyleSheet(JDXi.UI.Style.STYLE_FOREGROUND)
    label_layout.addWidget(label)
    return label_row, label
