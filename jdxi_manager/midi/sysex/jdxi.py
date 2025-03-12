from dataclasses import dataclass, field
from typing import List

from jdxi_manager.midi.data.constants import START_OF_SYSEX, ROLAND_ID, END_OF_SYSEX
from jdxi_manager.midi.data.constants.sysex import DT1_COMMAND_12
from jdxi_manager.midi.sysex.roland import RolandSysEx


@dataclass
class JDXiSysEx(RolandSysEx):
    """JD-Xi specific SysEx message"""

    model_id: List[int] = field(
        default_factory=lambda: [0x00, 0x00, 0x00, 0x0E]
    )  # JD-Xi model ID
    device_id: int = 0x10  # Default device ID
    command: int = DT1_COMMAND_12  # Default to DT1 command
    address: List[int] = field(
        default_factory=lambda: [0x00, 0x00, 0x00, 0x00]
    )  # 4-byte address
    data: List[int] = field(default_factory=list)  # Data bytes

    def __post_init__(self):
        """Validate message components"""
        # Validate device ID
        if not 0x00 <= self.device_id <= 0x1F and self.device_id != 0x7F:
            raise ValueError(f"Invalid device ID: {self.device_id:02X}")

        # Validate model ID
        if len(self.model_id) != 4:
            raise ValueError("Model ID must be 4 bytes")
        if self.model_id != [0x00, 0x00, 0x00, 0x0E]:
            raise ValueError(f"Invalid model ID: {[f'{x:02X}' for x in self.model_id]}")

        # Validate address
        if len(self.address) != 4:
            raise ValueError("Address must be 4 bytes")
        if not all(0x00 <= x <= 0xFF for x in self.address):
            raise ValueError(
                f"Invalid address bytes: {[f'{x:02X}' for x in self.address]}"
            )

    def to_bytes(self) -> bytes:
        """Convert message to bytes for sending"""
        msg = [
            START_OF_SYSEX,  # Start of SysEx
            ROLAND_ID,  # Roland ID
            self.device_id,  # Device ID
            *self.model_id,  # Model ID (4 bytes)
            self.command,  # Command ID
            *self.address,  # Address (4 bytes)
            *self.data,  # Data bytes
            self.calculate_checksum(),  # Checksum
            END_OF_SYSEX,  # End of SysEx
        ]
        return bytes(msg)

    def calculate_checksum(self) -> int:
        """Calculate Roland checksum for the message"""
        # Checksum = 128 - (sum of address and data bytes % 128)
        checksum = sum(self.address) + sum(self.data)
        return (128 - (checksum % 128)) & 0x7F

    @classmethod
    def from_bytes(cls, data: bytes):
        """Create message from received bytes"""
        if (
            len(data)
            < 12  # Minimum length: F0 + ID + dev + model(4) + cmd + addr(4) + sum + F7
            or data[0] != 0xF0
            or data[1] != 0x41  # Roland ID
            or data[3:7] != bytes([0x00, 0x00, 0x00, 0x0E])
        ):  # JD-Xi model ID
            raise ValueError("Invalid JD-Xi SysEx message")

        device_id = data[2]
        command = data[7]
        address = list(data[8:12])
        message_data = list(data[12:-2])  # Everything between address and checksum
        received_checksum = data[-2]

        # Create message and verify checksum
        message = cls(
            device_id=device_id, command=command, address=address, data=message_data
        )

        if message.calculate_checksum() != received_checksum:
            raise ValueError("Invalid checksum")

        return message
