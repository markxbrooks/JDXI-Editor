"""
utility functions

"""

from typing import Iterable, List, Optional, Union

import mido

from jdxi_editor.jdxi.sysex.offset import (
    JDXIControlChangeOffset,
    JDXIProgramChangeOffset,
    JDXiSysExOffset,
)
from jdxi_editor.log.logger import Logger as log
from jdxi_editor.midi.data.address.address import ModelID
from jdxi_editor.midi.data.address.sysex import RolandID
from jdxi_editor.midi.sysex.device import DeviceInfo
from picomidi.constant import Midi
from picomidi.core.bitmask import BitMask


def format_midi_message_to_hex_string(message: Iterable[int]) -> str:
    """
    Convert a list of MIDI byte values to a space-separated hex string.

    :param message: Iterable[int]
    :return: str A string like "F0 41 10 00 00 00 0E ... F7"
    """
    return " ".join([hex(x)[2:].upper().zfill(2) for x in message])


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

    :param message_content: List[int] byte list
    :return: Optional[Union[mido.Message, List[mido.Message]] either a single mido message or a list of mido messages
    """
    if not message_content:
        return None
    status_byte = message_content[JDXIProgramChangeOffset.STATUS_BYTE]
    # SysEx
    try:
        if (
            status_byte == Midi.SYSEX.START
            and message_content[JDXiSysExOffset.END] == Midi.SYSEX.END
        ):
            sysex_data = nibble_data(
                message_content[
                    JDXIProgramChangeOffset.PROGRAM_NUMBER : JDXIProgramChangeOffset.END
                ]
            )
            if len(sysex_data) > 128:
                nibbles = [sysex_data[i : i + 4] for i in range(0, len(sysex_data), 4)]
                return [mido.Message("sysex", data=nibble) for nibble in nibbles]
            return mido.Message("sysex", data=sysex_data)
    except Exception as ex:
        log.error(f"Error {ex} occurred")
    # Program Change
    try:
        if (
            Midi.PC.STATUS <= status_byte <= Midi.PC.MAX_STATUS
            and len(message_content) >= 2
        ):
            channel = status_byte & BitMask.LOW_4_BITS
            program = message_content[JDXIProgramChangeOffset.PROGRAM_NUMBER]
            return mido.Message("program_change", channel=channel, program=program)
    except Exception as ex:
        log.error(f"Error {ex} occurred")
    # Control Change
    try:
        if (
            Midi.CC.STATUS <= status_byte <= Midi.CC.MAX_STATUS
            and len(message_content) >= 3
        ):
            channel = status_byte & BitMask.LOW_4_BITS
            control = message_content[JDXIControlChangeOffset.CONTROL]
            value = message_content[JDXIControlChangeOffset.VALUE]
            return mido.Message(
                "control_change", channel=channel, control=control, value=value
            )
    except Exception as ex:
        log.error(f"Error {ex} occurred")

    log.message(f"Unhandled MIDI message: {message_content}")
    return None


def mido_message_data_to_byte_list(message: mido.Message) -> bytes:
    """
    mido message data to byte list

    :param message: mido.Message
    :return: bytes
    """
    hex_string = " ".join(f"{byte:02X}" for byte in message.data)

    message_byte_list = bytes(
        [Midi.SYSEX.START]
        + [int(byte, 16) for byte in hex_string.split()]
        + [Midi.SYSEX.END]
    )
    return message_byte_list


def handle_identity_request(message: mido.Message) -> dict:
    """
    Handles an incoming Identity Request

    :param message: mido.Message incoming response to identity request
    :return: dict device details
    """
    byte_list = mido_message_data_to_byte_list(message)
    device_info = DeviceInfo.from_identity_reply(byte_list)
    if device_info:
        log.message(device_info.to_string)
    device_id = device_info.device_id
    manufacturer_id = device_info.manufacturer
    version = message.data[
        JDXiSysExOffset.ADDRESS.UMB : JDXiSysExOffset.TONE_NAME.START
    ]  #  Extract firmware version bytes

    version_str = ".".join(str(byte) for byte in version)
    if device_id == ModelID.DEVICE_ID:
        device_name = "JD-Xi"
    else:
        device_name = "Unknown"
    if manufacturer_id[0] == RolandID.ROLAND_ID:
        manufacturer_name = "Roland"
    else:
        manufacturer_name = "Unknown"
    log.message(f"🏭 Manufacturer ID: \t{manufacturer_id}  \t{manufacturer_name}")
    log.message(f"🎹 Device ID: \t\t\t{hex(device_id)} \t{device_name}")
    log.message(f"🔄 Firmware Version: \t{version_str}")
    return {
        "device_id": device_id,
        "manufacturer_id": manufacturer_id,
        "firmware_version": version_str,
    }
