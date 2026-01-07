"""
Waveform Button
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QPushButton, QWidget

from jdxi_editor.midi.wave.form import Waveform


class WaveformButton(QPushButton):
    """Button for selecting oscillator waveform"""

    waveform_selected = Signal(Waveform)  # Emits selected waveform

    def __init__(
        self, waveform: Waveform, style: str = "digital", parent: QWidget = None
    ):
        """Initialize waveform button

        Args:
            waveform: Waveform enum value
            parent: Parent widget
        """
        super().__init__(parent)
        self.waveform = waveform
        self.setText(waveform.display_name)
        self.setCheckable(True)
        self.clicked.connect(self._on_clicked)

        # Style
        self.setMinimumWidth(60)

    def _on_clicked(self) -> None:
        """Handle button click"""
        if self.isChecked():
            self.waveform_selected.emit(self.waveform)

    def setValue(self, value: int) -> None:
        """Set the button's checked state based on a MIDI value."""
        try:
            selected_waveform = Waveform.from_midi_value(value)
            self.setChecked(selected_waveform == self.waveform)
        except ValueError:
            self.setChecked(False)
