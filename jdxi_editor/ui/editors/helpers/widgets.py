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
