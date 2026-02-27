"""
Pitch Wheel Widget
"""

from picomidi.constant import Midi
from picomidi.core.bitmask import BitMask

from jdxi_editor.ui.widgets.wheel.wheel import WheelWidget


class PitchWheel(WheelWidget):
    """
    Pitch Bend Wheel
    """

    def __init__(
        self,
        label="Pitch",
        bidirectional=True,
        parent=None,
        midi_helper=None,
        channel=0,
    ):
        super().__init__(parent)
        self.bidirectional = bidirectional
        self.label = label
        self.parent = parent
        self.value = 0.0
        self.midi_helper = midi_helper  # RtMidiOut instance
        self.channel = channel  # MIDI channel (0–15)

    def set_value(self, value):
        """
        Set wheel value in the range -1.0 to 1.0 and send pitch bend.
        """
        self.value = max(-1.0, min(1.0, value))  # Clamp to [-1.0, 1.0]
        bend_value = int(
            (self.value + 1.0) * Midi.pitch_bend.CENTER
        )  # Convert to 0–16383
        bend_value = max(
            0, min(Midi.pitch_bend.RANGE, bend_value)
        )  # Clamp to [0, 16383]

        lsb = bend_value & BitMask.LOW_7_BITS
        msb = (bend_value >> 7) & BitMask.LOW_7_BITS
        for channel in [0, 1, 2]:
            status = Midi.pitch_bend.STATUS | (channel & Midi.channel.MASK)

            if self.midi_helper.midi_out:
                self.midi_helper.midi_out.send_message([status, lsb, msb])
