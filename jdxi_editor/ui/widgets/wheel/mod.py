"""
Modulation Wheel
"""

from jdxi_editor.ui.widgets.wheel.pitch import WHEEL_CHANNELS
from jdxi_editor.ui.widgets.wheel.wheel import WheelWidget
from picomidi.constant import Midi

MODULATION_CC = 1


class ModWheel(WheelWidget):
    """
    Modulation Wheel (0.0-1.0, stays where it is left): dragging it sends CC 1;
    show_value() mirrors the JD-Xi's wheel without sending.
    """

    def __init__(
        self, label="Mod", bidirectional=False, parent=None, midi_helper=None, channel=0
    ):
        super().__init__(parent, bidirectional=bidirectional, label=label)
        self.midi_helper = midi_helper
        self.channel = channel  # MIDI channel (0-15)
        self.valueChanged.connect(self._send)

    def _send(self, value: float) -> None:
        if getattr(self.midi_helper, "midi_out", None) is None:
            return
        cc_value = int(round(max(0.0, min(1.0, value)) * Midi.value.max.SEVEN_BIT))
        for channel in WHEEL_CHANNELS:
            self.midi_helper.send_control_change(MODULATION_CC, cc_value, channel=channel)
