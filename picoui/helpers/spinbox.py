"""
Create spinbox with label from spec
"""

from PySide6.QtWidgets import QLabel, QSpinBox

from picoui.specs.widgets import SpinBoxSpec


def spinbox_with_label(
    label: str,
    min_val: int = 1,
    max_val: int = 127,
    value: int = None,
    tooltip: str = "",
):
    """create spinbox with label"""
    label = QLabel(label)
    spinbox = QSpinBox()
    spinbox.setRange(min_val, max_val)
    if value is not None:
        spinbox.setValue(value)
    spinbox.setToolTip(tooltip)
    return label, spinbox


def spinbox_with_label_from_spec(spec: SpinBoxSpec):
    """create spinbox with label from spec"""
    label, spinbox = spinbox_with_label(
        label=spec.label,
        min_val=spec.min_val,
        max_val=spec.max_val,
        value=spec.value,
        tooltip=spec.tooltip,
    )
    return label, spinbox
