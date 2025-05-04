"""
Partial Panel
"""

import qtawesome as qta
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel

from jdxi_editor.midi.data.digital import DigitalPartial
from jdxi_editor.jdxi.style import JDXIStyle
from jdxi_editor.ui.widgets.switch.partial import PartialSwitch


class PartialsPanel(QWidget):
    """Panel containing all partial switches"""

    def __init__(self, parent: QWidget = None):
        """Initialize the PartialsPanel.

        :param parent: QWidget
        """
        super().__init__(parent)

        layout = QVBoxLayout()
        layout.setSpacing(5)
        self.setLayout(layout)

        partial_layout = QHBoxLayout()
        partial_layout.setSpacing(5)
        self.setLayout(partial_layout)

        # Create switches for each partial (not structure types)
        self.switches = {}
        for partial in DigitalPartial.get_partials():  # Only get actual partials
            group_box = QGroupBox(f"Partial {partial}")
            group_layout = QHBoxLayout()
            partial_icon = QLabel()
            qta_icon = qta.icon(
                f"mdi.numeric-{partial}-circle-outline", color="#666666"
            )
            partial_icon_pixmap = qta_icon.pixmap(
                JDXIStyle.ICON_SIZE, JDXIStyle.ICON_SIZE
            )  # Set the desired size
            partial_icon.setPixmap(partial_icon_pixmap)
            group_layout.addWidget(partial_icon)
            switch = PartialSwitch(partial)
            self.switches[partial] = switch
            group_layout.addWidget(switch)
            group_layout.setSpacing(5)
            group_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            group_box.setLayout(group_layout)
            partial_layout.addWidget(group_box)

        layout.addLayout(partial_layout)
        # Style
        self.setStyleSheet(JDXIStyle.PARTIALS_PANEL)
