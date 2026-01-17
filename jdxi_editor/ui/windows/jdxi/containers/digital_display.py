"""
create digital display container
"""

from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from jdxi_editor.ui.style.dimensions import JDXiDimensions
from jdxi_editor.ui.widgets.display.digital import DigitalDisplay


def add_digital_display(central_widget, parent):
    """Add container with digital display on the JD-Xi image"""
    central_widget.setLayout(QVBoxLayout())

    digital_display_container = QWidget(central_widget)
    digital_display_container.setGeometry(
        JDXiDimensions.LED.X,
        JDXiDimensions.LED.Y,
        JDXiDimensions.LED.WIDTH,
        JDXiDimensions.LED.HEIGHT,
    )
    digital_display_layout = QHBoxLayout()
    digital_display_container.setLayout(digital_display_layout)
    digital_display = DigitalDisplay(parent=parent)
    digital_display_layout.addWidget(digital_display)
    return digital_display
