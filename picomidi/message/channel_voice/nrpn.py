"""
Non-Registered Parameter Number (NRPN) Message

NRPN messages are sequences of Control Change messages used to set
14-bit parameter values for manufacturer-specific parameters. The sequence is:
1. CC#99 (NRPN MSB) - parameter MSB
2. CC#98 (NRPN LSB) - parameter LSB
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
class NRPN(Message):
    """
    Non-Registered Parameter Number (NRPN) message.

    NRPN messages are sent as a sequence of Control Change messages:
    1. CC#99 (NRPN MSB) with parameter MSB
    2. CC#98 (NRPN LSB) with parameter LSB
    3. CC#6 (Data Entry MSB) with value MSB
    4. CC#38 (Data Entry LSB) with value LSB (for 14-bit values)

    Optionally, NRPN can be nulled after sending by sending CC#99=127, CC#98=127.

    :param channel: MIDI channel (0-15)
    :param parameter: NRPN parameter number (0-16383)
    :param value: Parameter value (0-16383 for 14-bit, 0-127 for 7-bit)
    :param use_14bit: If True, send 14-bit value (MSB + LSB). If False, send only MSB (7-bit)
    :param null_after: If True, send null NRPN (CC#99=127, CC#98=127) after data entry
    """

    channel: Channel
    parameter: int  # 0-16383
    value: int  # 0-16383 for 14-bit, 0-127 for 7-bit
    use_14bit: bool = True
    null_after: bool = True

    def __post_init__(self):
        """Validate NRPN parameter and value ranges."""
        if not validate_14bit_value(self.parameter):
            raise ValueError(
                f"NRPN parameter must be between 0 and 16383, got {self.parameter}"
            )
        if self.use_14bit:
            if not validate_14bit_value(self.value):
                raise ValueError(
                    f"NRPN value must be between 0 and 16383, got {self.value}"
                )
        else:
            if not 0 <= self.value <= Midi.VALUES.MAX.SEVEN_BIT:
                raise ValueError(
                    f"NRPN value must be between 0 and {Midi.VALUES.MAX.SEVEN_BIT}, got {self.value}"
                )

    def to_bytes(self) -> bytes:
        """Convert NRPN to bytes (sequence of Control Change messages)."""
        return bytes(self.to_list())

    def to_list(self) -> List[int]:
        """
        Convert NRPN to a sequence of Control Change messages.

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
            # NRPN MSB
            status,
            99,
            param_msb,
            # NRPN LSB
            status,
            98,
            param_lsb,
            # Data Entry MSB
            status,
            6,
            value_msb,
        ]

        # Data Entry LSB (only for 14-bit values)
        if self.use_14bit:
            messages.extend([status, 38, value_lsb])

        # Optional null NRPN (prevents stuck parameters)
        if self.null_after:
            messages.extend(
                [
                    status,
                    99,
                    127,  # NRPN MSB null
                    status,
                    98,
                    127,  # NRPN LSB null
                ]
            )

        return messages

    def to_messages(self) -> List[List[int]]:
        """
        Convert NRPN to a list of separate Control Change messages.

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
            [status, 99, param_msb],  # NRPN MSB
            [status, 98, param_lsb],  # NRPN LSB
            [status, 6, value_msb],  # Data Entry MSB
        ]

        if self.use_14bit:
            messages.append([status, 38, value_lsb])  # Data Entry LSB

        if self.null_after:
            messages.extend(
                [
                    [status, 99, 127],  # NRPN MSB null
                    [status, 98, 127],  # NRPN LSB null
                ]
            )

        return messages

    def __repr__(self) -> str:
        bit_mode = "14-bit" if self.use_14bit else "7-bit"
        null_str = "with null" if self.null_after else "no null"
        return f"NRPN(channel={self.channel.to_display()}, parameter={self.parameter}, value={self.value}, {bit_mode}, {null_str})"
