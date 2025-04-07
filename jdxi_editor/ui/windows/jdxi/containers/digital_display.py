"""
create digital display container
"""
from PySide6.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout

from jdxi_editor.ui.widgets.display.digital import DigitalDisplay
from jdxi_editor.ui.windows.jdxi.dimensions import JDXIDimensions


def add_digital_display(central_widget, parent):
    """Add container with digital display on the JD-Xi image"""
    central_widget.setLayout(QVBoxLayout())

    digital_display_container = QWidget(central_widget)
    digital_display_container.setGeometry(
        JDXIDimensions.DISPLAY_X,
        JDXIDimensions.DISPLAY_Y,
        JDXIDimensions.DISPLAY_WIDTH,
        JDXIDimensions.DISPLAY_HEIGHT
    )
    digital_display_layout = QHBoxLayout()
    digital_display_container.setLayout(digital_display_layout)
    digital_display = DigitalDisplay(parent=parent)
    digital_display_layout.addWidget(digital_display)
    return digital_display
