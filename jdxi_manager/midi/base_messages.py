from dataclasses import dataclass
from typing import List

from jdxi_manager.midi.sysex import (START_OF_SYSEX, END_OF_SYSEX, 
                                   ROLAND_ID, JD_XI_ID)

@dataclass
class RolandSysEx:
    """Base class for Roland System Exclusive messages"""
    command: int = 0x12  # Default to Data Set 1 (DT1)
    area: int = 0x00     # Memory area
    section: int = 0x00  # Section within area
    group: int = 0x00    # Group within section
    param: int = 0x00    # Parameter number
    value: int = 0x00    # Parameter value
    address: List[int] = None  # Full address bytes
    data: List[int] = None     # Data bytes

    def __post_init__(self):
        """Set up address and data if not provided"""
        if self.address is None:
            self.address = [
                self.area,
                self.section,
                self.group,
                self.param
            ]
        if self.data is None:
            self.data = [self.value]

    def to_bytes(self) -> bytes:
        """Convert message to bytes for sending"""
        msg = [
            START_OF_SYSEX,
            ROLAND_ID,
            JD_XI_ID,
            self.command,
            *self.address,
            *self.data,
            END_OF_SYSEX
        ]
        return bytes(msg)

    @classmethod
    def from_bytes(cls, data: bytes):
        """Create message from received bytes"""
        if (len(data) < 8 or
            data[0] != START_OF_SYSEX or
            data[1] != ROLAND_ID or
            data[2] != JD_XI_ID):
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
            data=value
        ) 