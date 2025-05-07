from jdxi_editor.midi.data.address.address import (
    CommandID, JD_XI_MODEL_ID,
)
from jdxi_editor.midi.data.address.sysex import START_OF_SYSEX, END_OF_SYSEX, RolandID


def create_parameter_message(
    msb: int, umb: int, lmb: int, lsb: int, value: int
) -> bytes:
    """
    Create parameter change SysEx message
    :param msb: int
    :param umb: int
    :param lmb: int
    :param lsb: int
    :param value: int
    :return: bytes
    """
    message = [
        START_OF_SYSEX,  # F0
        RolandID.ROLAND_ID,  # 41
        RolandID.DEVICE_ID,  # 10
        *JD_XI_MODEL_ID,  # 00 00 00 0E
        CommandID.DT1,  # 12
        msb,  # 19 (Digital Synth)
        umb,  # 01 (Part 1)
        lmb,  # 20 (OSC)
        lsb,  # 00 (First parameter)
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
