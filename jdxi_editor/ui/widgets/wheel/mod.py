"""
Modulation Wheel
"""

from jdxi_editor.ui.widgets.wheel.wheel import WheelWidget
from picomidi.constant import Midi
from picomidi.core.bitmask import BitMask


class ModWheel(WheelWidget):
    """
    Modulation Wheel
    """

    def __init__(
        self, label="Mod", bidirectional=True, parent=None, midi_helper=None, channel=0
    ):
        super().__init__(parent)
        self.label = label
        self.bidirectional = bidirectional
        self.parent = parent
        self.value = 0.0
        self.midi_helper = midi_helper  # RtMidiOut instance
        self.channel = channel  # MIDI channel (0–15)

    def set_value(self, value):
        """
        Set modulation wheel value (0.0 to 1.0) and send MIDI CC1.
        """
        self.value = max(0.0, min(1.0, value))  # Clamp between 0 and 1
        cc_value = int(self.value * Midi.VALUE.MAX.SEVEN_BIT)

        status = Midi.CC.STATUS | (self.channel & BitMask.LOW_4_BITS)
        cc_number = 1  # Modulation wheel

        if self.midi_helper.midi_out:
            self.midi_helper.midi_out.send_message([status, cc_number, cc_value])
            for channel in [0, 1, 2]:
                self.midi_helper.send_control_change(
                    cc_number, cc_value, channel=channel
                )
