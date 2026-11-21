"""
A rotary control for the JD-Xi faceplate.

The knob sends the same control change or NRPN as the editor slider that
owns the same parameter map.
"""

import threading

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QDial, QLabel, QVBoxLayout, QWidget

from jdxi_editor.midi.io.delay import send_with_delay
from jdxi_editor.midi.sysex.request.midi_requests import MidiRequests
from jdxi_editor.ui.widgets.midi.parameter_send import send_control_change_map, send_nrpn_map


class Rotary(QWidget):
    """A knob with the hardware name printed under it."""

    valueChanged = Signal(int)

    def __init__(self, label: str, tooltip: str = "", parent=None):
        super().__init__(parent)
        self.hardware_label = label
        self.setObjectName(f"rotary_{label}")
        self._dial = QDial()
        self._dial.setNotchesVisible(True)
        self._dial.setRange(0, 127)
        self._dial.setFixedSize(34, 34)
        self._dial.setWrapping(False)
        self._dial.valueChanged.connect(self.valueChanged.emit)
        caption = QLabel(label)
        caption.setObjectName(f"knob_{label}")
        caption.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        caption.setWordWrap(True)
        caption.setFixedWidth(46)
        if tooltip:
            self._dial.setToolTip(tooltip)
            caption.setToolTip(tooltip)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)
        layout.addWidget(self._dial, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(caption)

    def value(self) -> int:
        return self._dial.value()

    def setValue(self, value: int) -> None:
        self._dial.setValue(value)


class ControlChangeRotary(Rotary):
    """A knob that sends a control change from a partial map."""

    def __init__(self, midi_helper, label: str, nrpn_map: dict, channels=None, tooltip: str = ""):
        super().__init__(label, tooltip)
        self.midi_helper = midi_helper
        self.nrpn_map = nrpn_map
        self.channels = [0, 1, 2] if channels is None else channels
        self.valueChanged.connect(self._send)

    def _send(self, value: int) -> None:
        send_control_change_map(self.midi_helper, self.nrpn_map, value, self.channels)


class NRPNRotary(Rotary):
    """A knob that sends an NRPN from a partial map."""

    def __init__(
        self,
        midi_helper,
        label: str,
        nrpn_map: dict,
        nrpn_msb: int = 0,
        param_type: str = "nrpn",
        tooltip: str = "",
    ):
        super().__init__(label, tooltip)
        self.midi_helper = midi_helper
        self.nrpn_map = nrpn_map
        self.nrpn_msb = nrpn_msb
        self.param_type = param_type
        self.midi_requests = MidiRequests.PROGRAM_TONE_NAME_PARTIAL
        self.valueChanged.connect(self._send)

    def _send(self, value: int) -> None:
        send_nrpn_map(
            self.midi_helper,
            self.nrpn_map,
            value,
            self.nrpn_msb,
            self.param_type,
        )
        threading.Thread(
            target=send_with_delay,
            args=(self.midi_helper, self.midi_requests),
        ).start()
