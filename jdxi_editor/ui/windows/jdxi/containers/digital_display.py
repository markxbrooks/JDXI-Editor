"""
create digital display container
"""

from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.ui.widgets.display.digital import DigitalDisplay


def add_digital_display(central_widget, parent):
    """Add container with digital display on the JD-Xi image"""
    central_widget.setLayout(QVBoxLayout())

    digital_display_container = QWidget(central_widget)
    digital_display_container.setGeometry(
        JDXi.UI.Dimensions.LED.X,
        JDXi.UI.Dimensions.LED.Y,
        JDXi.UI.Dimensions.LED.WIDTH,
        JDXi.UI.Dimensions.LED.HEIGHT,
    )
    digital_display_layout = QHBoxLayout()
    digital_display_container.setLayout(digital_display_layout)
    digital_display = DigitalDisplay(parent=parent)
    digital_display_layout.addWidget(digital_display)
    return digital_display
