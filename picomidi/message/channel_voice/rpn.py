"""
Registered Parameter Number (RPN) Message

RPN messages are sequences of Control Change messages used to set
14-bit parameter values. The sequence is:
1. CC#101 (RPN MSB) - parameter MSB
2. CC#100 (RPN LSB) - parameter LSB
3. CC#6 (Data Entry MSB) - value MSB
4. CC#38 (Data Entry LSB) - value LSB (optional for 7-bit values)
"""

from dataclasses import dataclass
from typing import List

from picomidi.constant import Midi
from picomidi.core.bitmask import BitMask
from picomidi.core.channel import Channel
from picomidi.core.status import Status
from picomidi.core.types import ControlValue
from picomidi.message.base import Message
from picomidi.utils.validation import validate_14bit_value


@dataclass(frozen=True)
class RPN(Message):
    """
    Registered Parameter Number (RPN) message.

    RPN messages are sent as a sequence of Control Change messages:
    1. CC#101 (RPN MSB) with parameter MSB
    2. CC#100 (RPN LSB) with parameter LSB
    3. CC#6 (Data Entry MSB) with value MSB
    4. CC#38 (Data Entry LSB) with value LSB (for 14-bit values)

    :param channel: MIDI channel (0-15)
    :param parameter: RPN parameter number (0-16383)
    :param value: Parameter value (0-16383 for 14-bit, 0-127 for 7-bit)
    :param use_14bit: If True, send 14-bit value (MSB + LSB). If False, send only MSB (7-bit)
    """

    channel: Channel
    parameter: int  # 0-16383
    value: int  # 0-16383 for 14-bit, 0-127 for 7-bit
    use_14bit: bool = True

    def __post_init__(self):
        """Validate RPN parameter and value ranges."""
        if not validate_14bit_value(self.parameter):
            raise ValueError(
                f"RPN parameter must be between 0 and 16383, got {self.parameter}"
            )
        if self.use_14bit:
            if not validate_14bit_value(self.value):
                raise ValueError(
                    f"RPN value must be between 0 and 16383, got {self.value}"
                )
        else:
            if not 0 <= self.value <= Midi.VALUES.MAX.SEVEN_BIT:
                raise ValueError(
                    f"RPN value must be between 0 and {Midi.VALUES.MAX.SEVEN_BIT}, got {self.value}"
                )

    def to_bytes(self) -> bytes:
        """Convert RPN to bytes (sequence of Control Change messages)."""
        return bytes(self.to_list())

    def to_list(self) -> List[int]:
        """
        Convert RPN to a sequence of Control Change messages.

        Returns a flat list of bytes representing the sequence of CC messages.
        Note: This returns all bytes in sequence. For separate messages, use to_messages().
        """
        # Split parameter into MSB/LSB
        param_msb = (self.parameter >> 7) & BitMask.LOW_7_BITS
        param_lsb = self.parameter & BitMask.LOW_7_BITS

        # Split value into MSB/LSB
        if self.use_14bit:
            value_msb = (self.value >> 7) & BitMask.LOW_7_BITS
            value_lsb = self.value & BitMask.LOW_7_BITS
        else:
            value_msb = self.value & BitMask.LOW_7_BITS
            value_lsb = 0

        # Build sequence of Control Change messages
        status = Status.make_channel_voice(Status.CONTROL_CHANGE, self.channel.value)

        messages = [
            # RPN MSB
            status,
            101,
            param_msb,
            # RPN LSB
            status,
            100,
            param_lsb,
            # Data Entry MSB
            status,
            6,
            value_msb,
        ]

        # Data Entry LSB (only for 14-bit values)
        if self.use_14bit:
            messages.extend([status, 38, value_lsb])

        return messages

    def to_messages(self) -> List[List[int]]:
        """
        Convert RPN to a list of separate Control Change messages.

        :return: List of Control Change messages, each as [status, controller, value]
        """
        param_msb = (self.parameter >> 7) & BitMask.LOW_7_BITS
        param_lsb = self.parameter & BitMask.LOW_7_BITS

        if self.use_14bit:
            value_msb = (self.value >> 7) & BitMask.LOW_7_BITS
            value_lsb = self.value & BitMask.LOW_7_BITS
        else:
            value_msb = self.value & BitMask.LOW_7_BITS
            value_lsb = 0

        status = Status.make_channel_voice(Status.CONTROL_CHANGE, self.channel.value)

        messages = [
            [status, 101, param_msb],  # RPN MSB
            [status, 100, param_lsb],  # RPN LSB
            [status, 6, value_msb],  # Data Entry MSB
        ]

        if self.use_14bit:
            messages.append([status, 38, value_lsb])  # Data Entry LSB

        return messages

    def __repr__(self) -> str:
        bit_mode = "14-bit" if self.use_14bit else "7-bit"
        return f"RPN(channel={self.channel.to_display()}, parameter={self.parameter}, value={self.value}, {bit_mode})"
