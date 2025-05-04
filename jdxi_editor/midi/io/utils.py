"""
utility functions 

"""
from typing import List, Optional, Union

import mido
from black.lines import Callable

from jdxi_editor.log.error import log_error
from jdxi_editor.log.message import log_message
from jdxi_editor.midi.data.address.address import ModelID
from jdxi_editor.midi.data.address.sysex import RolandID

from jdxi_editor.midi.sysex.device import DeviceInfo


def format_midi_message_to_hex_string(message):
    """hexlify message"""
    formatted_message = " ".join([hex(x)[2:].upper().zfill(2) for x in message])
    return formatted_message


def construct_address(area, group, param, part):
    """Address construction
    :param area: int
    :param group: int
    :param param: int
    :param part: int
    :return: list
    """
    address = [area, part, group & 0xFF, param & 0xFF]
    return address


def increment_group(group, param):
    """Adjust group if param exceeds 127
    :param group: int
    :param param: int
    :return: int
    """
    if param > 127:
        group += 1
    return group


def nibble_data(data):
    """Sanitize the data by splitting bytes greater than 127 into 4-bit nibbles.
    :param data: list
    :return: list
    """
    sanitized_data = []
    for byte in data:
        if byte > 127:
            high_nibble = (byte >> 4) & 0x0F
            low_nibble = byte & 0x0F
            # Combine nibbles into valid data bytes (0-127)
            sanitized_data.append(high_nibble)
            sanitized_data.append(low_nibble)
        else:
            sanitized_data.append(byte)
    return sanitized_data


def rtmidi_to_mido(rtmidi_message: bytes) -> Union[bool, mido.Message]:
    """
    Convert an rtmidi message to address mido message.
    :param rtmidi_message: bytes
    :return: Union[bool, mido.Message]: mido message on success or False otherwise
    """
    try:
        return mido.Message.from_bytes(rtmidi_message)
    except ValueError as err:
        log_error(f"Failed to convert rtmidi message: {err}")
        return False


def convert_to_mido_message(message_content: List[int]) -> Optional[Union[mido.Message, List[mido.Message]]]:
    """
    Convert raw MIDI message content to a mido.Message object or a list of them.
    :param message_content: List[int] byte list
    :return: Optional[Union[mido.Message, List[mido.Message]] either a single mido message or a list of mido messages
    """
    if not message_content:
        return None
    status_byte = message_content[0]
    # SysEx
    try:
        if status_byte == 0xF0 and message_content[-1] == 0xF7:
            sysex_data = nibble_data(message_content[1:-1])
            if len(sysex_data) > 128:
                nibbles = [sysex_data[i:i + 4] for i in range(0, len(sysex_data), 4)]
                return [mido.Message("sysex", data=nibble) for nibble in nibbles]
            return mido.Message("sysex", data=sysex_data)
    except Exception as ex:
        log_error(f"Error {ex} occurred")
    # Program Change
    try:
        if 0xC0 <= status_byte <= 0xCF and len(message_content) >= 2:
            channel = status_byte & 0x0F
            program = message_content[1]
            return mido.Message("program_change", channel=channel, program=program)
    except Exception as ex:
        log_error(f"Error {ex} occurred")
    # Control Change
    try:
        if 0xB0 <= status_byte <= 0xBF and len(message_content) >= 3:
            channel = status_byte & 0x0F
            control = message_content[1]
            value = message_content[2]
            return mido.Message("control_change", channel=channel, control=control, value=value)
    except Exception as ex:
        log_error(f"Error {ex} occurred")

    log_message(f"Unhandled MIDI message: {message_content}")
    return None


def mido_message_data_to_byte_list(message: mido.Message) -> bytes:
    """
    mido message data to byte list
    :param message: mido.Message
    :return: bytes
    """
    hex_string = " ".join(f"{byte:02X}" for byte in message.data)

    message_byte_list = bytes(
        [0xF0] + [int(byte, 16) for byte in hex_string.split()] + [0xF7]
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
        log_message(device_info.to_string)
    device_id = device_info.device_id
    manufacturer_id = device_info.manufacturer
    version = message.data[9:12]  # Extract firmware version bytes

    version_str = ".".join(str(byte) for byte in version)
    if device_id == ModelID.DEVICE_ID:
        device_name = "JD-XI"
    else:
        device_name = "Unknown"
    if manufacturer_id[0] == RolandID.ROLAND_ID:
        manufacturer_name = "Roland"
    else:
        manufacturer_name = "Unknown"
    log_message(f"🏭 Manufacturer ID: \t{manufacturer_id}  \t{manufacturer_name}")
    log_message(f"🎹 Device ID: \t\t\t{hex(device_id)} \t{device_name}")
    log_message(f"🔄 Firmware Version: \t{version_str}")
    return {
        "device_id": device_id,
        "manufacturer_id": manufacturer_id,
        "firmware_version": version_str,
    }


def listen_midi(port_name: str, callback: Callable) -> None:
    """
    Function to listen for MIDI messages and call address callback.
    :param port_name: str midi port name
    :param callback: Callable function to call
    :return: None
    """
    with mido.open_input(port_name) as inport:
        log_message(f"Listening on port: {port_name}")
        for msg in inport:
            callback(msg)  # Call the provided callback function
