"""
MIDI Control Change Message Module
==================================

This module defines the `ControlChangeMessage` class, which represents a MIDI Control Change (CC) message.
It extends the `ChannelMessage` class to handle messages used for real-time parameter adjustments in MIDI devices.

Classes:
    - ControlChangeMessage: Represents a MIDI Control Change message with controller and value parameters.

Features:
    - Inherits channel-based messaging from `ChannelMessage`.
    - Automatically assigns controller and value to data bytes.
    - Uses status byte `0xB0` for Control Change messages.

Usage Example:
    >>> msg = ControlChangeMessage(channel=1, controller=7, value=100)  # Volume control on channel 1
    >>> msg.to_list()
    [177, 7, 100]  # (0xB1 in hex: CC message for channel 1)
"""


from dataclasses import dataclass
from typing import List

from jdxi_editor.midi.data.control_change.drum import DrumKitCC
from jdxi_editor.midi.message.channel import ChannelMessage


from dataclasses import dataclass, field
from typing import List, Optional

from jdxi_editor.midi.message.midi import MidiMessage


@dataclass
class ControlChangeMessage(MidiMessage):
    """MIDI Control Change message"""

    channel: int
    controller: int
    value: int
    status: int = field(
        init=False, default=0xB0
    )  # Prevents status from being a required argument

    def __post_init__(self):
        if not (0 <= self.controller <= 127):
            raise ValueError(
                f"Controller number {self.controller} out of range (0-127)."
            )
        if not (0 <= self.value <= 127):
            raise ValueError(f"Control value {self.value} out of range (0-127).")

        self.data1 = self.controller  # Controller number
        self.data2 = self.value  # Control value

    def to_message_list(self) -> List[int]:
        """Convert Control Change message to a list of bytes for sending"""
        status_byte = self.status | (
            self.channel & 0x0F
        )  # Ensures correct channel encoding
        return [
            status_byte,
            self.data1 & 0x7F,
            self.data2 & 0x7F,
        ]  # Proper MIDI CC message


@dataclass
class DigitalToneCCMessage:
    """SuperNATURAL Synth Tone Control Change message"""

    channel: int = 0  # MIDI channel (0-15)
    cc: int = 0  # CC number
    value: int = 0  # CC value (0-127)
    is_nrpn: bool = False  # Whether this is an NRPN message

    def to_bytes(self) -> bytes:
        """Convert to MIDI message bytes"""
        if not self.is_nrpn:
            # Standard CC message
            return bytes(
                [
                    0xB0 | self.channel,  # Control Change status
                    self.cc,  # CC number
                    self.value,  # Value
                ]
            )
        else:
            # NRPN message sequence
            return bytes(
                [
                    0xB0 | self.channel,  # CC for NRPN MSB
                    0x63,  # NRPN MSB (99)
                    0x00,  # MSB value = 0
                    0xB0 | self.channel,  # CC for NRPN LSB
                    0x62,  # NRPN LSB (98)
                    self.cc,  # LSB value = parameter
                    0xB0 | self.channel,  # CC for Data Entry
                    0x06,  # Data Entry MSB
                    self.value,  # Value
                ]
            )

    @classmethod
    def from_bytes(cls, data: bytes):
        """Create message from MIDI bytes"""
        if len(data) == 3:
            # Standard CC message
            return cls(channel=data[0] & 0x0F, cc=data[1], value=data[2], is_nrpn=False)
        elif len(data) == 9:
            # NRPN message
            return cls(
                channel=data[0] & 0x0F,
                cc=data[5],  # NRPN parameter number
                value=data[8],  # NRPN value
                is_nrpn=True,
            )
        raise ValueError("Invalid CC message length")


@dataclass
class AnalogToneCCMessage:
    """Analog Synth Tone Control Change message"""

    channel: int = 0  # MIDI channel (0-15)
    cc: int = 0  # CC number
    value: int = 0  # CC value (0-127)
    is_nrpn: bool = False  # Whether this is an NRPN message

    def to_bytes(self) -> bytes:
        """Convert to MIDI message bytes"""
        if not self.is_nrpn:
            # Standard CC message
            return bytes(
                [
                    0xB0 | self.channel,  # Control Change status
                    self.cc,  # CC number
                    self.value,  # Value
                ]
            )
        else:
            # NRPN message sequence
            return bytes(
                [
                    0xB0 | self.channel,  # CC for NRPN MSB
                    0x63,  # NRPN MSB (99)
                    0x00,  # MSB value = 0
                    0xB0 | self.channel,  # CC for NRPN LSB
                    0x62,  # NRPN LSB (98)
                    self.cc,  # LSB value = parameter
                    0xB0 | self.channel,  # CC for Data Entry
                    0x06,  # Data Entry MSB
                    self.value,  # Value
                ]
            )

    @classmethod
    def from_bytes(cls, data: bytes):
        """Create message from MIDI bytes"""
        if len(data) == 3:
            # Standard CC message
            return cls(channel=data[0] & 0x0F, cc=data[1], value=data[2], is_nrpn=False)
        elif len(data) == 9:
            # NRPN message
            return cls(
                channel=data[0] & 0x0F,
                cc=data[5],  # NRPN parameter number
                value=data[8],  # NRPN value
                is_nrpn=True,
            )
        raise ValueError("Invalid CC message length")


@dataclass
class DrumKitCCMessage:
    """Drum Kit Control Change message"""

    channel: int = 0  # MIDI channel (0-15)
    msb: int = 0  # NRPN MSB value
    note: int = 36  # MIDI note number (36-72)
    value: int = 0  # CC value (0-127)

    def __post_init__(self):
        """Validate all parameters"""
        # Validate channel
        if not 0 <= self.channel <= 15:
            raise ValueError(f"Invalid MIDI channel: {self.channel}")

        # Validate MSB
        if not DrumKitCC.validate_msb(self.msb):
            raise ValueError(f"Invalid MSB value: {self.msb}")

        # Validate note
        if not DrumKitCC.validate_note(self.note):
            raise ValueError(f"Invalid drum note: {self.note}")

        # Validate value
        if not DrumKitCC.validate_value(self.value):
            raise ValueError(f"Invalid parameter value: {self.value}")

    def to_bytes(self) -> bytes:
        """Convert to MIDI message bytes"""
        # NRPN message sequence
        return bytes(
            [
                0xB0 | self.channel,  # CC for NRPN MSB
                0x63,  # NRPN MSB (99)
                self.msb,  # MSB value
                0xB0 | self.channel,  # CC for NRPN LSB
                0x62,  # NRPN LSB (98)
                self.note,  # LSB value = note number
                0xB0 | self.channel,  # CC for Data Entry
                0x06,  # Data Entry MSB
                self.value,  # Value
            ]
        )

    @classmethod
    def from_bytes(cls, data: bytes):
        """Create message from MIDI bytes"""
        if len(data) == 9:
            return cls(
                channel=data[0] & 0x0F,
                msb=data[2],  # MSB value
                note=data[5],  # Note number
                value=data[8],  # Parameter value
            )
        raise ValueError("Invalid CC message length")
