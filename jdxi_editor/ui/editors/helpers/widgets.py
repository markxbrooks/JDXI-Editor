from PySide6.QtWidgets import QWidget, QSlider, QComboBox, QSpinBox


def set_widget_value_safely(widget: QWidget, value: int):
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
