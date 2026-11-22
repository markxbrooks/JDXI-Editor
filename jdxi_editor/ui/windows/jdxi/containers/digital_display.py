"""
create digital digital container
"""

from PySide6.QtWidgets import QHBoxLayout, QWidget

from jdxi_editor.ui.widgets.digital.display import DigitalDisplay


def add_digital_display(host: QWidget, parent, digital_font_family=None):
    """Add the digital display to ``host`` on the JD-Xi image"""
    digital_display_layout = QHBoxLayout(host)
    # The display is drawn at its full size from here; the host's own edge
    # trims it, as the panel's display window does
    digital_display_layout.setContentsMargins(11, 11, 0, 0)
    digital_display = DigitalDisplay(
        parent=parent,
        digital_font_family=digital_font_family,
    )
    digital_display_layout.addWidget(digital_display)
    return digital_display
