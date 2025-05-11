"""
Module for AnalogWaveformButton UI Component.

This module defines the `AnalogWaveformButton` class, a specialized button for selecting oscillator waveforms in the JD-Xi editor. It inherits from `WaveformButton` and emits a signal when a waveform is selected.

Features:
- Displays selectable waveform options with a styled QPushButton.
- Emits `waveform_selected` signal upon selection.
- Custom styling for default, checked, and hover states.
"""


from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget
from jdxi_editor.midi.wave.form import Waveform
from jdxi_editor.jdxi.style import JDXiStyle

from jdxi_editor.ui.widgets.button.waveform.waveform import WaveformButton


class AnalogWaveformButton(WaveformButton):
    """Button for selecting oscillator waveform"""

    waveform_selected = Signal(Waveform)  # Emits selected waveform

    def __init__(
        self, waveform: Waveform, style: str = "digital", parent: QWidget = None
    ):
        """Initialize waveform button

        :param waveform: Waveform enum value
        :param style: str
        :param parent: Parent widget
        """
        super().__init__(waveform, style, parent)

        # Style
        self.setMinimumWidth(60)
        self.setStyleSheet(JDXiStyle.BUTTON_WAVEFORM_ANALOG)
