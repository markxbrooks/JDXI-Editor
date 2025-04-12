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

import logging
from enum import Enum
from typing import List, Optional
from dataclasses import dataclass

from jdxi_editor.midi.data.address.address import START_OF_SYSEX, END_OF_SYSEX, JD_XI_HEADER_LIST, \
    CommandID, AddressOffsetProgramLMB
from jdxi_editor.midi.message.midi import MidiMessage

# MIDI Constants
JD_XI_HEADER_BYTES = bytes(JD_XI_HEADER_LIST)


class SysexParameter(Enum):
    """SysEx Parameters for Roland JD-Xi"""

    DT1_COMMAND_12 = ("Data Set 1", CommandID.DT1)
    RQ1_COMMAND_11 = ("Data Request 1", CommandID.RQ1)

    PROGRAM_COMMON = ("PROGRAM_COMMON", AddressOffsetProgramLMB.COMMON)
    # TONE_1_LEVEL = ("TONE_1_LEVEL", UnknownToneAddress.TONE_1_LEVEL)
    # TONE_2_LEVEL = ("TONE_2_LEVEL", UnknownToneAddress.TONE_2_LEVEL)

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


@dataclass
class SysExMessage(MidiMessage):
    """Base class for MIDI System Exclusive (SysEx) messages."""
    start_of_sysex: int = START_OF_SYSEX  # Start of SysEx
    manufacturer_id: int = 0x41  # Manufacturer ID (e.g., [0x41] for Roland)
    device_id: int = 0x10  # Default device ID
    model_id: List[int] = None  # Model ID (4 bytes)
    command: int = 0x00  # SysEx command (DT1, RQ1, etc.)
    address: List[int] = None  # Address (4 bytes)
    data: List[int] = None  # Data payload
    end_of_sysex: int = END_OF_SYSEX  # End of SysEx

    def __post_init__(self):
        """Ensure proper initialization of address, model_id, and data fields."""
        if self.manufacturer_id is None:
            raise ValueError("manufacturer_id must be provided.")
        if self.model_id is None or len(self.model_id) != 4:
            raise ValueError("model_id must be a list of exactly 4 bytes.")
        if self.address is None:
            self.address = [0x00] * 4  # Default to an empty address
        if self.data is None:
            self.data = []

    def calculate_checksum(self) -> int:
        """Calculate Roland checksum: (128 - sum(bytes) & 0x7F)."""
        checksum_data = self.address + self.data
        return (128 - (sum(checksum_data) & 0x7F)) & 0x7F if checksum_data else 0

    def to_message_list(self) -> List[int]:
        """Convert the SysEx message to a list of integers."""
        msg = (
            [self.start_of_sysex]
            + [self.manufacturer_id]
            + [self.device_id]
            + self.model_id
            + [self.command]
            + self.address
            + self.data
        )
        if self.manufacturer_id == 0x41:  # Roland messages require checksum
            msg.append(self.calculate_checksum())
        msg.append(self.end_of_sysex)
        return msg

    @classmethod
    def from_bytes(cls, data: bytes):
        """Parse a received SysEx message into an instance."""
        if len(data) < 12:
            raise ValueError(f"Invalid SysEx message: too short ({len(data)} bytes)")
        if data[0] != 0xF0 or data[-1] != 0xF7:
            raise ValueError("Invalid SysEx message: missing start or end bytes")

        manufacturer_id = [data[1]]
        device_id = data[2]
        model_id = list(data[3:7])  # Extract model_id (4 bytes)
        command = data[7]
        address = list(data[8:12])  # Extract address (4 bytes)
        message_data = list(data[12:-2])  # Extract data before checksum and EOX

        return cls(
            manufacturer_id=data[1],
            device_id=device_id,
            model_id=model_id,
            command=command,
            address=address,
            data=message_data,
        )

