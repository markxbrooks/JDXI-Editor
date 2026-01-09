"""
MIDI Identity Request Message Module

This module defines the `IdentityRequestMessage` class, which represents a MIDI Identity Request message.
MIDI Identity Request messages are used to query a device for its identity, typically to retrieve information such as its model or manufacturer.

Classes:
    - IdentityRequestMessage: Represents a MIDI Identity Request message used to query a device's identity.

Features:
    - Inherits from the base `Message` class, utilizing SysEx message structure.
    - Includes device identification information, such as device ID and fixed SysEx parameters.
    - Provides a method for converting the message into a list of bytes for sending via MIDI.

Constants Used:
    - START_OF_SYSEX: The start byte for a SysEx message.
    - ID_NUMBER, DEVICE, SUB_ID_1, SUB_ID_2: Fixed SysEx identifiers for the identity request.
    - END_OF_SYSEX: The end byte for a SysEx message.

Usage Example:
    >>> identity_msg = IdentityRequestMessage()
    >>> identity_msg.to_message_list()
    [0xF0, 0x7E, 0x00, 0x01, 0x02, 0xF7]

"""

from dataclasses import dataclass
from typing import List

from picomidi.constant import Midi

from jdxi_editor.jdxi.midi.constant import JDXiMidi
from jdxi_editor.midi.message.midi import MidiMessage


@dataclass
class IdentityRequestMessage(MidiMessage):
    """MIDI Identity Request message"""

    device_id: int = 0x10  # Default device ID

    def to_message_list(self) -> List[int]:
        """
        Convert to list of bytes for sending

        :return: list
        """
        return [
            Midi.SYSEX.START,
            JDXiMidi.DEVICE.ID_NUMBER,
            JDXiMidi.DEVICE.DEVICE_ID,
            JDXiMidi.DEVICE.SUB_ID_1_GENERAL_INFORMATION,
            JDXiMidi.DEVICE.SUB_ID_2_IDENTITY_REQUEST,
            Midi.SYSEX.END,
        ]
