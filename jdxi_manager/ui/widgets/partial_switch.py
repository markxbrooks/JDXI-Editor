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
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Enable switch
        self.enable_check = QCheckBox("ON")
        self.enable_check.stateChanged.connect(self._on_state_changed)
        layout.addWidget(self.enable_check)

        # Select switch
        self.select_check = QCheckBox("SEL")
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
                border-radius: 2px;
            }
            QCheckBox::indicator:checked {
                background: #CC3333;
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


class PartialsPanel(QGroupBox):
    """Panel containing all partial switches"""

    def __init__(self, parent=None):
        super().__init__("Partials", parent)

        layout = QVBoxLayout()
        layout.setSpacing(10)
        self.setLayout(layout)

        partial_layout = QHBoxLayout()
        partial_layout.setSpacing(10)
        self.setLayout(partial_layout)

        oscillator_hlayout = QHBoxLayout()
        for icon in [
            "mdi.directions-fork",
            "mdi.numeric-1-circle-outline",
            "mdi.numeric-2-circle-outline",
            "mdi.numeric-3-circle-outline",
            "mdi.call-merge",
        ]:
            oscillator_triangle_label = QLabel()
            icon = qta.icon(icon)
            pixmap = icon.pixmap(
                Style.ICON_SIZE, Style.ICON_SIZE
            )  # Set the desired size
            oscillator_triangle_label.setPixmap(pixmap)
            oscillator_triangle_label.setAlignment(Qt.AlignHCenter)
            oscillator_hlayout.addWidget(oscillator_triangle_label)
        layout.addLayout(oscillator_hlayout)

        # Create switches for each partial (not structure types)
        self.switches = {}
        for partial in DigitalPartial.get_partials():  # Only get actual partials
            switch = PartialSwitch(partial)
            self.switches[partial] = switch
            partial_layout.addWidget(switch)

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
