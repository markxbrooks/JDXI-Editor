"""
utility functions

"""

from typing import Iterable, List, Optional, Union

import mido

from decologr import Decologr as log
from jdxi_editor.jdxi.midi.message.sysex.offset import (
    JDXIControlChangeOffset,
    JDXIProgramChangeOffset,
    JDXiSysExMessageLayout,
)
from jdxi_editor.midi.data.address.address import ModelID
from jdxi_editor.midi.data.address.sysex import RolandID
from jdxi_editor.midi.sysex.device import DeviceInfo
from picomidi.constant import Midi
from picomidi.core.bitmask import BitMask


def increment_if_lsb_exceeds_7bit(msb: int, lsb: int) -> int:
    """
    Increments the MSB if the LSB exceeds 7-bit maximum (127).

    :param msb: Most significant byte (int)
    :param lsb: Least significant byte (int)
    :return: Adjusted MSB (int)
    """
    if not (0 <= msb <= Midi.VALUE.MAX.EIGHT_BIT):  # 255
        raise ValueError("MSB must be an 8-bit value (0–255).")

    if lsb > BitMask.LOW_7_BITS:  # 127
        msb += 1

    return msb


def nibble_data(data: list[int]) -> list[int]:
    """
    Ensures all values in the data list are 7-bit safe (0–127).
    Bytes > 127 are split into two 4-bit nibbles.
    :param data: List of integer byte values (0–255)
    :return: List of 7-bit-safe integers (0–127)
    """
    nibbled_data = []
    for byte in data:
        if byte > Midi.VALUE.MAX.SEVEN_BIT:  # 127
            high_nibble = (byte >> 4) & BitMask.LOW_4_BITS
            low_nibble = byte & BitMask.LOW_4_BITS
            # Combine nibbles into valid data bytes (0-127)
            nibbled_data.append(high_nibble)
            nibbled_data.append(low_nibble)
        else:
            nibbled_data.append(byte)
    return nibbled_data


def rtmidi_to_mido(byte_message: bytes) -> Union[bool, mido.Message]:
    """
    Convert an rtmidi message to address mido message.

    :param byte_message: bytes
    :return: Union[bool, mido.Message]: mido message on success or False otherwise
    """
    try:
        return mido.Message.from_bytes(byte_message)
    except ValueError as err:
        log.error(f"Failed to convert rtmidi message: {err}")
        return False


def convert_to_mido_message(
    message_content: List[int],
) -> Optional[Union[mido.Message, List[mido.Message]]]:
    """
    Convert raw MIDI message content to a mido.Message object or a list of them.

    .. deprecated::
        This function is deprecated. Use JDXiSysExParser.convert_to_mido_message() instead.
        This function is kept for backward compatibility and delegates to the parser.

    :param message_content: List[int] byte list
    :return: Optional[Union[mido.Message, List[mido.Message]]] either a single mido message or a list of mido messages
    """
    from jdxi_editor.midi.sysex.parser.sysex import JDXiSysExParser

    parser = JDXiSysExParser()
    return parser.convert_to_mido_message(message_content)


def mido_message_data_to_byte_list(message: mido.Message) -> bytes:
    """
    mido message data to byte list

    :param message: mido.Message
    :return: bytes
    """
    # Safely convert to int for formatting
    hex_string = " ".join(
        f"{int(byte) if not isinstance(byte, int) else byte:02X}"
        for byte in message.data
    )

    message_byte_list = bytes(
        [Midi.SYSEX.START]
        + [int(byte, 16) for byte in hex_string.split()]
        + [Midi.SYSEX.END]
    )
    return message_byte_list


def handle_identity_request(message: mido.Message) -> dict:
    """
    Handles an incoming Identity Request/Reply message.

    .. deprecated::
        This function is deprecated. Use JDXiSysExParser.parse_identity_request() instead.
        This function is kept for backward compatibility and delegates to the parser.

    :param message: mido.Message incoming response to identity request
    :return: dict device details
    """
    from jdxi_editor.midi.sysex.parser.sysex import JDXiSysExParser

    parser = JDXiSysExParser()
    return parser.parse_identity_request(message)
