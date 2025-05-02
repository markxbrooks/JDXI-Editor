"""
utility functions 

"""
import logging
from typing import Any, List, Optional, Union

import mido

from jdxi_editor.globals import logger
from jdxi_editor.log.message import log_message
from jdxi_editor.midi.data.address.address import ModelID
from jdxi_editor.midi.data.address.sysex import RolandID

from jdxi_editor.midi.message.sysex import SysexParameter
from jdxi_editor.midi.sysex.device import DeviceInfo


def format_midi_message_to_hex_string(message):
    """hexlify message"""
    formatted_message = " ".join([hex(x)[2:].upper().zfill(2) for x in message])
    return formatted_message


def construct_address(area, group, param, part):
    """Address construction"""
    address = [area, part, group & 0xFF, param & 0xFF]
    return address


def increment_group(group, param):
    """Adjust group if param exceeds 127"""
    if param > 127:
        group += 1
    return group


def nibble_data(data):
    """Sanitize the data by splitting bytes greater than 127 into 4-bit nibbles."""
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


def extract_command_info(message: Any) -> None:
    """Extracts and logs command type and address offset."""
    try:
        command_type = message.data[6]
        address_offset = "".join(f"{byte:02X}" for byte in message.data[7:11])
        command_name = SysexParameter.get_command_name(command_type)

        logger.debug(
            "Command: %s (0x%02X), Address Offset: %s",
            command_name,
            command_type,
            address_offset,
        )
    except Exception as ex:
        log_message(f"Unable to extract command or parameter address due to {ex}", level=logging.ERROR)


def rtmidi_to_mido(rtmidi_message):
    """Convert an rtmidi message to address mido message."""
    try:
        return mido.Message.from_bytes(rtmidi_message)
    except ValueError as err:
        log_message(f"Failed to convert rtmidi message: {err}", level=logging.ERROR)
        return None


def convert_to_mido_message(message_content: List[int]) -> Optional[Union[mido.Message, List[mido.Message]]]:
    """Convert raw MIDI message content to a mido.Message object or a list of them."""
    if not message_content:
        return None

    status_byte = message_content[0]

    try:
        # SysEx
        if status_byte == 0xF0 and message_content[-1] == 0xF7:
            sys_ex_data = nibble_data(message_content[1:-1])
            if len(sys_ex_data) > 128:
                nibbles = [sys_ex_data[i:i + 4] for i in range(0, len(sys_ex_data), 4)]
                return [mido.Message("sysex", data=nibble) for nibble in nibbles]
            return mido.Message("sysex", data=sys_ex_data)
    except Exception as ex:
        log_message(f"Error {ex} occurred", level=logging.ERROR)
    try:
        # Program Change
        if 0xC0 <= status_byte <= 0xCF and len(message_content) >= 2:
            channel = status_byte & 0x0F
            program = message_content[1]
            return mido.Message("program_change", channel=channel, program=program)
    except Exception as ex:
        log_message(f"Error {ex} occurred", level=logging.ERROR)

    try:
        # Control Change
        if 0xB0 <= status_byte <= 0xBF and len(message_content) >= 3:
            channel = status_byte & 0x0F
            control = message_content[1]
            value = message_content[2]
            return mido.Message("control_change", channel=channel, control=control, value=value)
    except Exception as ex:
        log_message(f"Error {ex} occurred", level=logging.ERROR)

    # Other (not yet implemented)
    log_message(f"Unhandled MIDI message: {message_content}")
    return None


def mido_message_data_to_byte_list(message):
    """mido message data to byte list"""
    hex_string = " ".join(f"{byte:02X}" for byte in message.data)
    log_message(f"converting ({len(message.data)} bytes)")

    # Reconstruct SysEx message bytes
    message_byte_list = bytes(
        [0xF0] + [int(byte, 16) for byte in hex_string.split()] + [0xF7]
    )
    return message_byte_list


def handle_identity_request(message):
    """Handles an incoming Identity Request and sends an Identity Reply."""
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


def listen_midi(port_name, callback):
    """
    Function to listen for MIDI messages and call address callback.
    """
    with mido.open_input(port_name) as inport:
        log_message(f"Listening on port: {port_name}")
        for msg in inport:
            callback(msg)  # Call the provided callback function
