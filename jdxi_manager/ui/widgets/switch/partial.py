from functools import partial

from PySide6.QtGui import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QCheckBox,
    QGroupBox,
    QLabel,
)
from PySide6.QtCore import Signal
import qtawesome as qta
from jdxi_manager.data.digital import DigitalPartial
from jdxi_manager.ui.style import Style


class PartialSwitch(QWidget):
    """Widget for controlling a single partial's state"""

    stateChanged = Signal(DigitalPartial, bool, bool)  # partial, enabled, selected

    def __init__(self, partial: DigitalPartial, parent=None):
        super().__init__(parent)
        self.partial = partial

        layout = QHBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Enable switch
        self.enable_check = QCheckBox("ON")
        self.enable_check.stateChanged.connect(self._on_state_changed)
        layout.addWidget(self.enable_check)

        # Select switch
        self.select_check = QCheckBox("Selected")
        self.select_check.stateChanged.connect(self._on_state_changed)
        layout.addWidget(self.select_check)

        # Style
        self.setStyleSheet(
            """
            QCheckBox {
                color: #CCCCCC;
                font-size: 10px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                background: #333333;
                border: 1px solid #555555;
                border-radius: 8px;
            }
            QCheckBox::indicator:checked {
                background: #666666;
                border-color: #FF4444;
            }
        """
        )

    def _on_state_changed(self, _):
        """Handle checkbox state changes"""
        self.stateChanged.emit(
            self.partial, self.enable_check.isChecked(), self.select_check.isChecked()
        )

    def setState(self, enabled: bool, selected: bool):
        """Set the partial state"""
        self.enable_check.setChecked(enabled)
        self.select_check.setChecked(selected)


class PartialsPanel(QWidget):
    """Panel containing all partial switches"""

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()
        layout.setSpacing(10)
        self.setLayout(layout)

        partial_layout = QHBoxLayout()
        partial_layout.setSpacing(40)
        self.setLayout(partial_layout)

        # Create switches for each partial (not structure types)
        self.switches = {}
        for partial in DigitalPartial.get_partials():  # Only get actual partials
            group_box = QGroupBox(f"Partial {partial}")
            group_layout = QHBoxLayout()
            partial_icon = QLabel()
            qta_icon = qta.icon(f"mdi.numeric-{partial}-circle-outline", color="#666666")
            partial_icon_pixmap = qta_icon.pixmap(Style.ICON_SIZE, Style.ICON_SIZE)  # Set the desired size
            partial_icon.setPixmap(partial_icon_pixmap)
            group_layout.addWidget(partial_icon)
            switch = PartialSwitch(partial)
            self.switches[partial] = switch 
            group_layout.addWidget(switch)
            group_layout.setSpacing(40)
            group_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            group_box.setLayout(group_layout)
            partial_layout.addWidget(group_box)

        layout.addLayout(partial_layout)
        # Style
        self.setStyleSheet(
            """
            QGroupBox {
                color: #CCCCCC;
                font-size: 12px;
                border: 1px solid #444444;
                border-radius: 3px;
                margin-top: 1.5ex;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
                background-color: #2D2D2D;
            }
        """
        )
