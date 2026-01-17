"""
Partial Panel
"""

import qtawesome as qta
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from jdxi_editor.midi.data.digital.partial import DigitalPartial
from jdxi_editor.ui.style import JDXiStyle
from jdxi_editor.ui.widgets.switch.partial import PartialSwitch


class PartialsPanel(QWidget):
    """Panel containing all partial switches"""

    def __init__(self, parent: QWidget = None):
        """Initialize the PartialsPanel.

        :param parent: QWidget
        """
        super().__init__(parent)

        layout = QVBoxLayout()
        layout.setSpacing(3)  # Reduced spacing
        layout.setContentsMargins(5, 5, 5, 5)  # Reduced margins
        self.setLayout(layout)

        partial_layout = QHBoxLayout()
        partial_layout.setSpacing(8)  # Reduced spacing
        partial_layout.addStretch()

        # Create switches for each partial (not structure types)
        self.switches = {}
        for partial in DigitalPartial.get_partials():  # Only get actual partials
            group_box = QGroupBox(f"Partial {partial}")
            group_layout = QHBoxLayout()
            partial_icon = QLabel()
            qta_icon = qta.icon(
                f"mdi.numeric-{partial}-circle-outline", color=JDXiStyle.GREY
            )
            partial_icon_pixmap = qta_icon.pixmap(
                JDXiStyle.ICON_SIZE, JDXiStyle.ICON_SIZE
            )  # Set the desired size
            partial_icon.setPixmap(partial_icon_pixmap)
            group_layout.addWidget(partial_icon)
            switch = PartialSwitch(partial)
            self.switches[partial] = switch
            group_layout.addWidget(switch)
            group_layout.setSpacing(3)  # Reduced spacing
            group_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            group_box.setLayout(group_layout)
            partial_layout.addWidget(group_box)

        layout.addLayout(partial_layout)
        partial_layout.addStretch()
        # Style
        self.setStyleSheet(JDXiStyle.PARTIALS_PANEL)
