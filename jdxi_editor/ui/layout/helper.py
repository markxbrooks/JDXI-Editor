from PySide6.QtWidgets import QHBoxLayout, QPushButton

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.ui.editors.helpers.widgets import create_jdxi_button, create_jdxi_row
from picoui.specs.widgets import ButtonSpec


def add_round_button(icon_enum, text: str, slot, layout: QHBoxLayout):
    """Add a round button + icon/label row (Transport style). Returns the button."""
    btn = create_jdxi_button("")
    if slot is not None:
        btn.clicked.connect(slot)
    layout.addWidget(btn)

    pixmap = JDXi.UI.Icon.get_icon_pixmap(
        icon_enum, color=JDXi.UI.Style.FOREGROUND, size=20
    )
    label_row, _ = create_jdxi_row(text, icon_pixmap=pixmap)
    layout.addWidget(label_row)
    return btn


def add_round_button_from_spec(btn_spec: ButtonSpec) -> QPushButton:
    """Uses a Spec to add a round button + icon/label row (Transport style). Returns the button."""
    return add_round_button(
        icon_enum=btn_spec.icon,
        text=btn_spec.label,
        slot=btn_spec.slot,
        layout=btn_spec.layout,
    )
