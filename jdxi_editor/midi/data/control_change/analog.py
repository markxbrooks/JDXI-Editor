"""Analog Control Change"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Tuple

from picomidi.constant import Midi
from shiboken6.Shiboken import Object

from jdxi_editor.midi.data.control_change.base import ControlChange


class AnalogControlChange(ControlChange):
    """Analog synth CC parameters"""

    # Direct CC parameters
    CUTOFF = 102  # Cutoff (0-127)
    RESONANCE = 105  # Resonance (0-127)
    LEVEL = 117  # Level (0-127)
    LFO_RATE = 16  # LFO Rate (0-127)

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if param == 3:  # LFO Shape
            shapes = ["TRI", "SIN", "SAW", "SQR", "S&H", "RND"]
            return shapes[value]
        return str(value)


@dataclass(frozen=True)
class RPNValue:
    """Represents a MIDI RPN value with its MSB, LSB, and value range."""

    msb_lsb: Tuple[int, int]
    value_range: Tuple[int, int]

    def midi_bytes(self, value: int) -> list[int]:
        """Generate CC messages for this RPN and a given value."""
        msb, lsb = self.msb_lsb
        value = max(min(value, self.value_range[1]), self.value_range[0])
        return [
            (Midi.CC.STATUS, 101, msb),  # RPN MSB
            (Midi.CC.STATUS, 100, lsb),  # RPN LSB
            (Midi.CC.STATUS, 6, value >> 7),  # Data Entry MSB
            (Midi.CC.STATUS, 38, value & 0x7F),  # Data Entry LSB
        ]


class AnalogRPN(Enum):
    """Analog synth RPN parameters with their MSB, LSB, and value range."""

    ENVELOPE = RPNValue((0, 124), (0, 127))
    LFO_SHAPE = RPNValue((0, 3), (0, 5))
    LFO_PITCH_DEPTH = RPNValue((0, 15), (0, 127))
    LFO_FILTER_DEPTH = RPNValue((0, 18), (0, 127))
    LFO_AMP_DEPTH = RPNValue((0, 21), (0, 127))
    PULSE_WIDTH = RPNValue((0, 37), (0, 127))


@dataclass(frozen=True)
class PartialRPNValue:
    """Represents a MIDI RPN value with base MSB/LSB, value range, and partial."""

    base_msb_lsb: Tuple[int, int]
    value_range: Tuple[int, int]
    partial: int

    @property
    def msb_lsb(self) -> Tuple[int, int]:
        """Return the dynamically adjusted MSB/LSB based on the partial number."""
        msb, base_lsb = self.base_msb_lsb
        return msb, base_lsb + (self.partial - 1)

    def __post_init__(self) -> None:
        if not (1 <= self.partial <= 3):
            raise ValueError("Partial must be between 1 and 3.")

    def midi_bytes(self, value: int) -> list[tuple[Any, int, int]]:
        """Generate CC messages for this RPN and a given value."""
        msb, lsb = self.msb_lsb
        value = max(min(value, self.value_range[1]), self.value_range[0])
        return [
            (Midi.CC.STATUS, 101, msb),  # RPN MSB
            (Midi.CC.STATUS, 100, lsb),  # RPN LSB
            (Midi.CC.STATUS, 6, value >> 7),  # Data Entry MSB
            (Midi.CC.STATUS, 38, value & 0x7F),  # Data Entry LSB
        ]


@dataclass(frozen=True)
class PartialRPNValue:
    base_msb_lsb: Tuple[int, int]
    value_range: Tuple[int, int]
    partial: int

    @property
    def msb_lsb(self) -> Tuple[int, int]:
        msb, base_lsb = self.base_msb_lsb
        return (msb, base_lsb + (self.partial - 1))


def make_digital_rpn(partial: int) -> Object:
    """
    make_digital_rpn

    :param partial: int
    :return: Object
    """

    class DigitalPartialRPN(Enum):
        ENVELOPE = PartialRPNValue((0, 124), (0, 127), partial)
        LFO_SHAPE = PartialRPNValue((0, 3), (0, 5), partial)
        LFO_PITCH_DEPTH = PartialRPNValue((0, 15), (0, 127), partial)
        LFO_FILTER_DEPTH = PartialRPNValue((0, 18), (0, 127), partial)
        LFO_AMP_DEPTH = PartialRPNValue((0, 21), (0, 127), partial)

    return DigitalPartialRPN


DigitalRPN_Partial1 = make_digital_rpn(1)
DigitalRPN_Partial2 = make_digital_rpn(2)
DigitalRPN_Partial3 = make_digital_rpn(3)


# Not using drums (26 Partials) thankfully :-)

if __name__ == "__main__":
    # Example usage
    print(AnalogRPN.ENVELOPE.value.msb_lsb)  # (0, 124)
    print(DigitalRPN_Partial1.ENVELOPE.STATUS.msb_lsb)  # (0, 124)
    print(DigitalRPN_Partial2.ENVELOPE.STATUS.msb_lsb)  # (0, 125)
