"""
Roland JD-Xi System Exclusive (SysEx) Message Module
====================================================

This module provides functionality for constructing, parsing, and handling
Roland JD-Xi SysEx messages. It includes support for both writing (DT1) and
reading (RQ1) parameter data, ensuring compliance with Roland's SysEx format.

Features:
---------
- Constructs valid SysEx messages for Roland JD-Xi.
- Supports both parameter write (DT1) and read (RQ1) operations.
- Computes and verifies Roland SysEx checksums.
- Allows dynamic configuration of MIDI parameters.
- Provides utilities to convert between byte sequences and structured data.

Classes:
--------
- `RolandSysEx`: Base class for handling Roland SysEx messages.
- `SysExParameter`: Enum for predefined SysEx parameters and command mappings.
- `SysExMessage`: Helper class for constructing and sending SysEx messages.

Usage Example:
--------------
```python
message = SysExMessage(area=0x19, synth_type=0x01, part=0x00, group=0x00, parameter=0x10, value=0x7F)
sysex_bytes = message.construct_sysex()
print(sysex_bytes)  # Outputs a valid SysEx message as a byte sequence
[0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x12, 0x19, 0x01, 0x00, 0x00, 0x10, 0x7F, 0x57, 0xF7]

"""

from enum import Enum
from typing import List, Optional

from jdxi_manager.midi.data.constants.sysex import (
    START_OF_SYSEX,
    END_OF_SYSEX,
    ROLAND_ID,
    MODEL_ID_1,
    MODEL_ID_2,
    TONE_1_LEVEL,
    TONE_2_LEVEL,
    MODEL_ID_3,
    MODEL_ID_4,
    DEVICE_ID,
    PROGRAM_COMMON,
    DT1_COMMAND_12,
    RQ1_COMMAND_11,
    JD_XI_HEADER_LIST,
)

# MIDI Constants
JD_XI_HEADER_BYTES = bytes(JD_XI_HEADER_LIST)


class SysexParameter(Enum):
    """SysEx Parameters for Roland JD-Xi"""

    JD_XI_HEADER_BYTES = JD_XI_HEADER_BYTES

    DT1_COMMAND_12 = ("Data Set 1", DT1_COMMAND_12)
    RQ1_COMMAND_11 = ("Data Request 1", RQ1_COMMAND_11)

    PROGRAM_COMMON = ("PROGRAM_COMMON", PROGRAM_COMMON)
    TONE_1_LEVEL = ("TONE_1_LEVEL", TONE_1_LEVEL)
    TONE_2_LEVEL = ("TONE_2_LEVEL", TONE_2_LEVEL)

    def __new__(cls, *args):
        if len(args) == 1:
            obj = object.__new__(cls)
            obj._value_ = args[0]
            obj.param_name = None
        elif len(args) == 2:
            param_name, value = args
            obj = object.__new__(cls)
            obj._value_ = value
            obj.param_name = param_name
        else:
            raise ValueError("Invalid number of arguments for SysexParameter Enum")
        return obj

    @classmethod
    def get_command_name(cls, command_type):
        """Retrieve the command name given a command type."""
        for item in cls:
            if hasattr(item, "param_name") and item.value == command_type:
                return item.param_name
        return None


class SysExMessage:
    """Helper class for constructing and sending Roland JD-Xi SysEx messages."""

    START_OF_SYSEX = START_OF_SYSEX
    ROLAND_ID = ROLAND_ID
    DEVICE_ID = DEVICE_ID
    MODEL_ID = [MODEL_ID_1, MODEL_ID_2, MODEL_ID_3, MODEL_ID_4]
    DT1_COMMAND = DT1_COMMAND_12  # Write command
    RQ1_COMMAND = RQ1_COMMAND_11  # Read command
    END_OF_SYSEX = END_OF_SYSEX

    def __init__(
        self,
        area=0x19,
        synth_type=0x01,
        part=0x00,
        group=0x00,
        parameter=0x00,
        value=0x00,
    ):
        self.area = area
        self.synth_type = synth_type
        self.part = part
        self.group = group
        self.parameter = [parameter] if isinstance(parameter, int) else parameter
        self.value = value if isinstance(value, list) else [value]

    @staticmethod
    def calculate_checksum(data):
        """Calculate Roland checksum for parameter messages."""
        return (128 - (sum(data) & 0x7F)) & 0x7F

    def construct_sysex(self, address, *data_bytes, request=False):
        """
        Construct a SysEx message with a checksum.

        :param address: Address bytes in hex string format.
        :param data_bytes: Data bytes in hex string format.
        :param request: SysEx command type (DT1 for write, RQ1 for read).
        :return: A complete SysEx message as a list of integers.
        """
        if not request:
            command = self.DT1_COMMAND  # Default to DT1 if not specified
        else:
            command = self.RQ1_COMMAND
        sysex_msg = (
            [self.START_OF_SYSEX, self.ROLAND_ID, self.DEVICE_ID]
            + [addr for addr in self.MODEL_ID]
            + [command]
            + [int(addr, 16) for addr in address]
            + ([int(byte, 16) for byte in data_bytes] if data_bytes else [])
        )

        # append checksum
        checksum = self.calculate_checksum(sysex_msg[8:])
        sysex_msg.append(checksum)

        sysex_msg.append(self.END_OF_SYSEX)
        return sysex_msg

    def construct_sysex_old(self, address: Optional[List[int]] = None, request=False):
        """Construct a SysEx message with a checksum."""
        if address is None:
            address = [self.area, self.synth_type, self.part, self.group]
        if len(address) != 4:
            raise ValueError("Address must be a list of 4 bytes.")

        command = self.RQ1_COMMAND if request else self.DT1_COMMAND
        sysex_msg = (
            [self.START_OF_SYSEX, self.ROLAND_ID, self.DEVICE_ID]
            + self.MODEL_ID
            + [command]
            + address
            + self.parameter
            + self.value
        )

        checksum = self.calculate_checksum(address + self.parameter + self.value)
        sysex_msg.append(checksum)
        sysex_msg.append(self.END_OF_SYSEX)

        return sysex_msg

    def to_bytes(self) -> bytes:
        """Convert message to bytes for sending."""
        return bytes(self.construct_sysex())

    @classmethod
    def from_bytes(cls, data: bytes):
        """Create a SysEx message instance from received bytes."""
        if len(data) < 8 or data[0] != cls.START_OF_SYSEX or data[1] != cls.ROLAND_ID:
            raise ValueError("Invalid Roland SysEx message")

        command = data[7]
        address = list(data[8:12])
        value = list(data[12:-2])  # Everything between address and checksum
        return cls(
            area=address[0],
            synth_type=address[1],
            part=address[2],
            group=address[3],
            parameter=value[:-1],
            value=value[-1],
        )
