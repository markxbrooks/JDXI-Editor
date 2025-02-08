"""

AnalogWaveformButton

"""

from PySide6.QtCore import Signal
from jdxi_manager.midi.constants import Waveform

from jdxi_manager.ui.widgets import WaveformButton


class AnalogWaveformButton(WaveformButton):
    """Button for selecting oscillator waveform"""

    waveform_selected = Signal(Waveform)  # Emits selected waveform

    def __init__(self, waveform: Waveform, style="digital", parent=None):
        """Initialize waveform button

        Args:
            waveform: Waveform enum value
            parent: Parent widget
        """
        super().__init__(waveform, style, parent)
        self.waveform = waveform
        self.setText(waveform.display_name)
        self.setCheckable(True)
        self.clicked.connect(self._on_clicked)

        # Style
        self.setMinimumWidth(60)
        self.setStyleSheet(
            """
            QPushButton {
                background-color: #222222;
                color: #CCCCCC;
                border: 1px solid #666666;
                border-radius: 3px;
                padding: 5px;
            }
            QPushButton:checked {
                background-color: #333333;
                color: white;
                border: 1px solid #00A0E9;
            }
            QPushButton:hover {
                background-color: #444444;
            }
        """
        )
