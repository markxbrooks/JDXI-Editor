from typing import List

from jdxi_editor.midi.data.address.address import (
    ModelID,
    CommandID,
    MODEL_ID,
)
from jdxi_editor.midi.data.address.sysex import START_OF_SYSEX, END_OF_SYSEX, RolandID


def create_parameter_message(
    area: int, part: int, group: int, param: int, value: int
) -> bytes:
    """
    Create parameter change SysEx message
    :param area: int
    :param part: int
    :param group: int
    :param param: int
    :param value: int
    :return: bytes
    """
    message = [
        START_OF_SYSEX,  # F0
        RolandID.ROLAND_ID,  # 41
        RolandID.DEVICE_ID,  # 10
        *MODEL_ID,  # 00 00 00 0E
        CommandID.DT1,  # 12
        area,  # 19 (Digital Synth)
        part,  # 01 (Part 1)
        group,  # 20 (OSC)
        param,  # 00 (First parameter)
        value,  # 00 (SAW)
    ]

    # Calculate checksum (from area byte to value byte)
    checksum = 0
    for byte in message[8:]:  # Start from area byte
        checksum += byte
    checksum = (128 - (checksum % 128)) & 0x7F

    message.append(checksum)  # 46
    message.append(END_OF_SYSEX)  # F7

    return bytes(message)
