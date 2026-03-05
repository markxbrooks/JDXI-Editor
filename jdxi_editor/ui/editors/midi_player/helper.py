from typing import Callable

from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.ui.editors.helpers.widgets import create_jdxi_row
from picoui.helpers import create_widget_with_layout
from picoui.specs.widgets import ButtonSpec


def create_widget_cell_with_button_spec(
        spec: ButtonSpec, button
) -> tuple[QWidget, QLabel]:
    """Create Widget With Button Spec"""
    widget = QWidget()
    layout = QHBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(4)
    layout.addWidget(button)
    icon_pixmap = JDXi.UI.Icon.get_icon_pixmap(
        spec.icon, color=JDXi.UI.Style.FOREGROUND, size=20
    )
    row_widget, label = create_jdxi_row(spec.label, icon_pixmap=icon_pixmap)
    layout.addWidget(row_widget)
    return widget, label


def build_panel(builder: Callable) -> QWidget:
    """build the appropriate panel"""
    panel_layout = builder()
    panel_widget = create_widget_with_layout(panel_layout)
    return panel_widget
