from PySide6.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout

from jdxi_editor.ui.widgets.display.digital import DigitalDisplay
from jdxi_editor.ui.windows.jdxi.dimensions import JDXI_DISPLAY_X, JDXI_DISPLAY_Y, JDXI_DISPLAY_WIDTH, \
    JDXI_DISPLAY_HEIGHT


def add_overlaid_controls(central_widget, parent):
    """Add interactive controls overlaid on the JD-Xi image"""
    # Create absolute positioning layout
    central_widget.setLayout(QVBoxLayout())

    digital_display_container = QWidget(central_widget)
    digital_display_container.setGeometry(
        JDXI_DISPLAY_X, JDXI_DISPLAY_Y, JDXI_DISPLAY_WIDTH, JDXI_DISPLAY_HEIGHT
    )
    digital_display_layout = QHBoxLayout()
    digital_display_container.setLayout(digital_display_layout)
    digital_display = DigitalDisplay(parent=parent)
    digital_display_layout.addWidget(digital_display)
    return digital_display
