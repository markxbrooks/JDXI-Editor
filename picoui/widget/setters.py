from PySide6.QtWidgets import QSpinBox


def set_spinbox_value(spinbox: QSpinBox, value: int):
    """set spinbox value safely"""
    spinbox.blockSignals(True)
    spinbox.setValue(value)
    spinbox.blockSignals(False)
