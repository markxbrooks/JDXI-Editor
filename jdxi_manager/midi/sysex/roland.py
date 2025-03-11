"""
roland_sysex.py

This module provides a class for constructing and parsing Roland System Exclusive (SysEx) messages. The `RolandSysEx` class allows for easy creation of messages to be sent to Roland devices, as well as the ability to parse incoming SysEx messages.

Usage Example:

```python
from roland_sysex import RolandSysEx

# Creating a SysEx message
message = RolandSysEx(command=0x12, area=0x01, section=0x02, group=0x03, param=0x04, value=0x05)
message_bytes = message.to_bytes()
print("Generated SysEx Message (bytes):", message_bytes)

# Parsing a SysEx message from bytes
received_bytes = b'\xF0\x41\x10\x12\x00\x01\x02\x03\x04\x05\xF7'  # Example received SysEx message
parsed_message = RolandSysEx.from_bytes(received_bytes)
print("Parsed Command:", parsed_message.command)
print("Parsed Address:", parsed_message.address)
print("Parsed Value:", parsed_message.value)

"""

from dataclasses import dataclass
from typing import List

from jdxi_manager.midi.data.constants.sysex import DT1_COMMAND_12, JD_XI_ID_LIST
from jdxi_manager.midi.sysex.sysex import START_OF_SYSEX, END_OF_SYSEX, ROLAND_ID


@dataclass
class RolandSysEx:
    """Base class for Roland System Exclusive messages"""

    command: int = DT1_COMMAND_12  # Default to Data Set 1 (DT1)
    area: int = 0x00  # Memory area
    section: int = 0x00  # Section within area
    group: int = 0x00  # Group within section
    param: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value
    address: List[int] = None  # Full address bytes
    data: List[int] = None  # Data bytes

    def __post_init__(self):
        """Set up address and data if not provided"""
        if self.address is None:
            self.address = [self.area, self.section, self.group, self.param]
        if self.data is None:
            self.data = [self.value]

    def to_bytes(self) -> bytes:
        """Convert message to bytes for sending"""
        msg = [
            START_OF_SYSEX,
            ROLAND_ID,
            JD_XI_ID_LIST,
            self.command,
            *self.address,
            *self.data,
            END_OF_SYSEX,
        ]
        return bytes(msg)

    @classmethod
    def from_bytes(cls, data: bytes):
        """Create message from received bytes"""
        if (
            len(data) < 8
            or data[0] != START_OF_SYSEX
            or data[1] != ROLAND_ID
            or data[2] != JD_XI_ID_LIST
        ):
            raise ValueError("Invalid Roland SysEx message")

        command = data[3]
        address = list(data[4:8])
        value = list(data[8:-1])  # Everything between address and EOX

        return cls(
            command=command,
            area=address[0],
            section=address[1],
            group=address[2],
            param=address[3],
            address=address,
            data=value,
        )
