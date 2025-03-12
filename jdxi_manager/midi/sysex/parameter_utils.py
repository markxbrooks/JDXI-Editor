from typing import List

from jdxi_manager.midi.data.constants.sysex import START_OF_SYSEX, ROLAND_ID, DEVICE_ID, MODEL_ID, \
    END_OF_SYSEX
from jdxi_manager.midi.data.constants.sysex import DT1_COMMAND_12


def create_parameter_message(
    area: int, part: int, group: int, param: int, value: int
) -> bytes:
    """Create parameter change SysEx message"""
    message = [
        START_OF_SYSEX,  # F0
        ROLAND_ID,  # 41
        DEVICE_ID,  # 10
        *MODEL_ID,  # 00 00 00 0E
        DT1_COMMAND_12,  # 12
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
