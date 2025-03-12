from typing import List

from jdxi_manager.midi.data.constants import SETUP_AREA, START_OF_SYSEX, ROLAND_ID, DEVICE_ID, MODEL_ID, DT1_COMMAND, \
    END_OF_SYSEX
from jdxi_manager.midi.data.constants.sysex import DT1_COMMAND_12, RQ1_COMMAND_11
from jdxi_manager.midi.sysex.jdxi import JDXiSysEx


def create_sysex_message(
    area: int, section: int, group: int, param: int, value: int
) -> JDXiSysEx:
    """Create address JD-Xi SysEx message with the given parameters"""
    return JDXiSysEx(
        command=DT1_COMMAND_12,
        area=area,
        section=section,
        group=group,
        param=param,
        value=value,
    )


def create_patch_load_message(
    bank_msb: int, bank_lsb: int, program: int
) -> List[JDXiSysEx]:
    """Create messages to load address patch (bank select + program change)"""
    return [
        # Bank Select MSB
        JDXiSysEx(
            command=DT1_COMMAND_12,
            area=SETUP_AREA,  # Setup area 0x01
            section=0x00,
            group=0x00,
            param=0x04,  # Bank MSB parameter
            value=bank_msb,
        ),
        # Bank Select LSB
        JDXiSysEx(
            command=DT1_COMMAND_12,
            area=0x01,  # Setup area
            section=0x00,
            group=0x00,
            param=0x05,  # Bank LSB parameter
            value=bank_lsb,
        ),
        # Program Change
        JDXiSysEx(
            command=DT1_COMMAND_12,
            area=0x01,  # Setup area
            section=0x00,
            group=0x00,
            param=0x06,  # Program number parameter
            value=program,
        ),
    ]


def create_patch_save_message(
    source_area: int,
    dest_area: int,
    source_section: int = 0x00,
    dest_section: int = 0x00,
) -> JDXiSysEx:
    """Create address message to save patch data from temporary to permanent memory"""
    return JDXiSysEx(
        command=DT1_COMMAND_12,
        area=dest_area,  # Destination area (permanent memory)
        section=dest_section,
        group=0x00,
        param=0x00,
        data=[  # Source address
            source_area,  # Source area (temporary memory)
            source_section,
            0x00,  # Always 0x00
            0x00,  # Start from beginning
        ],
    )


def create_patch_request_message(
    area: int, section: int = 0x00, size: int = 0
) -> JDXiSysEx:
    """Create address message to request patch data"""
    return JDXiSysEx(
        command=RQ1_COMMAND_11,  # Data request command
        area=area,
        section=section,
        group=0x00,
        param=0x00,
        data=[size] if size else [],  # Some requests need address size parameter
    )


def create_parameter_message(
    area: int, part: int, group: int, param: int, value: int
) -> bytes:
    """Create parameter change SysEx message"""
    message = [
        START_OF_SYSEX,  # F0
        ROLAND_ID,  # 41
        DEVICE_ID,  # 10
        *MODEL_ID,  # 00 00 00 0E
        DT1_COMMAND,  # 12
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
