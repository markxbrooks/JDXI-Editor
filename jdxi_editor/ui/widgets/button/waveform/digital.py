from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget
from jdxi_editor.midi.wave.form import Waveform
from jdxi_editor.ui.widgets.button.waveform import WaveformButton


class DigitalWaveformButton(WaveformButton):
    """Button for selecting oscillator waveform"""

    waveform_selected = Signal(Waveform)  # Emits selected waveform

    def __init__(self, waveform: Waveform, style: str = "digital", parent: QWidget = None):
        """Initialize waveform button

        :param waveform: Waveform enum value
        :param style: str
        :param parent: Parent widget
        """
        super().__init__(parent)

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
                border: 1px solid #FF4444;
            }
            QPushButton:hover {
                background-color: #444444;
            }
        """
        )
