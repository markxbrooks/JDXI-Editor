"""
Pitch Wheel Widget
"""

from jdxi_editor.ui.widgets.wheel.wheel import WheelWidget
from picomidi.constant import Midi
from picomidi.core.bitmask import BitMask

# The synth parts the wheel bends (Digital 1, Digital 2, Analog: channels 1-3)
WHEEL_CHANNELS = (0, 1, 2)


def bend_from_value(value: float) -> int:
    """-1.0..1.0 to the 14-bit pitch bend (0..16383, centre 8192)."""
    bend = int(round((max(-1.0, min(1.0, value)) + 1.0) * Midi.pitch_bend.CENTER))
    return max(0, min(Midi.pitch_bend.RANGE, bend))


def value_from_pitch(pitch: int) -> float:
    """mido's pitch (-8192..8191) to the wheel's -1.0..1.0."""
    return max(-1.0, min(1.0, pitch / 8192))


class PitchWheel(WheelWidget):
    """
    Pitch Bend Wheel: dragging it (and its return to the centre) sends pitch
    bend; show_value() mirrors the JD-Xi's wheel without sending.
    """

    def __init__(
        self,
        label="Pitch",
        bidirectional=True,
        parent=None,
        midi_helper=None,
        channel=0,
    ):
        super().__init__(parent, bidirectional=bidirectional, label=label)
        self.midi_helper = midi_helper
        self.channel = channel  # MIDI channel (0-15)
        self.valueChanged.connect(self._send)

    def _send(self, value: float) -> None:
        out = getattr(self.midi_helper, "midi_out", None)
        if out is None:
            return
        bend = bend_from_value(value)
        lsb = bend & BitMask.LOW_7_BITS
        msb = (bend >> 7) & BitMask.LOW_7_BITS
        for channel in WHEEL_CHANNELS:
            status = Midi.pitch_bend.STATUS | (channel & Midi.channel.MASK)
            self.midi_helper.send_raw_message([status, lsb, msb])
