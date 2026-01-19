"""
Roland System Exclusive (SysEx) Message

This module provides a generic class for constructing and parsing
Roland System Exclusive messages. Roland SysEx messages follow
a standard format:

F0 41 [device_id] [model_id(4)] [command] [address(4)] [data...] [checksum] F7

Where:
- F0: Start of SysEx
- 41: Roland manufacturer ID
- device_id: Device ID (0x10-0x1F, or 0x7F for all devices)
- model_id: 4-byte model identifier
- command: Command type (DT1=0x12 for data set, RQ1=0x11 for request)
- address: 4-byte parameter address (MSB, UMB, LMB, LSB)
- data: Variable-length data payload
- checksum: Roland checksum (calculated from address + data)
- F7: End of SysEx
"""

from dataclasses import dataclass, field
from typing import List, Optional

from picomidi.constant import Midi
from picomidi.message.base import Message
from picomidi.sysex.conversion import calculate_checksum


@dataclass
class RolandSysExMessage(Message):
    """
    Generic Roland System Exclusive message.

    This class provides a generic implementation for Roland SysEx messages
    that can be used with any Roland device. Device-specific subclasses
    should inherit from this and provide default values for model_id,
    device_id, etc.

    Example:
        >>> msg = RolandSysExMessage(
        ...     device_id=0x10,
        ...     model_id=[0x00, 0x00, 0x00, 0x0E],
        ...     command=0x12,  # DT1
        ...     address=[0x18, 0x00, 0x00, 0x10],
        ...     data=[0x7F]
        ... )
        >>> bytes_list = msg.to_list()
        >>> bytes_list
        [240, 65, 16, 0, 0, 0, 14, 18, 24, 0, 0, 16, 127, ...]
    """

    manufacturer_id: int = 0x41  # Roland manufacturer ID
    device_id: int = 0x10  # Default device ID (can be overridden)
    model_id: List[int] = field(default_factory=lambda: [0x00, 0x00, 0x00, 0x00])
    command: int = 0x12  # DT1 command (data set)
    address: List[int] = field(default_factory=lambda: [0x00, 0x00, 0x00, 0x00])
    data: List[int] = field(default_factory=list)

    def __post_init__(self):
        """
        Validate and normalize message components.

        :raises ValueError: If message structure is invalid
        """
        # Helper to safely convert to int for validation and formatting
        def safe_int_for_validation(val):
            if isinstance(val, int):
                return val
            if hasattr(val, 'value'):  # Handle enums
                enum_val = val.value
                return int(enum_val) if not isinstance(enum_val, int) else enum_val
            try:
                return int(float(val))  # Handle floats and strings
            except (ValueError, TypeError):
                return 0
        
        # Validate manufacturer ID (safely convert for formatting)
        manufacturer_id_int = safe_int_for_validation(self.manufacturer_id)
        if manufacturer_id_int != 0x41:
            raise ValueError(
                f"Roland manufacturer ID must be 0x41, got 0x{manufacturer_id_int:02X}"
            )

        # Validate device ID (0x10-0x1F or 0x7F for all devices) - safely convert for comparison and formatting
        device_id_int = safe_int_for_validation(self.device_id)
        if not (0x10 <= device_id_int <= 0x1F or device_id_int == 0x7F):
            raise ValueError(
                f"Device ID must be 0x10-0x1F or 0x7F, got 0x{device_id_int:02X}"
            )

        # Validate model ID (must be 4 bytes)
        if len(self.model_id) != 4:
            raise ValueError(
                f"Model ID must be exactly 4 bytes, got {len(self.model_id)} bytes"
            )
        # Safely validate and convert model ID bytes
        def safe_validate_byte(byte):
            if isinstance(byte, int):
                return 0 <= byte <= 0x7F
            try:
                byte_int = int(float(byte)) if not isinstance(byte, int) else byte
                return 0 <= byte_int <= 0x7F
            except (ValueError, TypeError):
                return False
        
        if any(not safe_validate_byte(byte) for byte in self.model_id):
            raise ValueError("Model ID bytes must be 0-127 (7-bit safe)")
        
        # Convert model ID bytes to integers if they aren't already
        self.model_id = [
            int(float(b)) if not isinstance(b, int) else b
            for b in self.model_id
        ]

        # Validate address (must be 4 bytes)
        if len(self.address) != 4:
            raise ValueError(
                f"Address must be exactly 4 bytes, got {len(self.address)} bytes"
            )
        # Safely validate and convert address bytes
        def safe_validate_byte(byte):
            if isinstance(byte, int):
                return 0 <= byte <= 0x7F
            try:
                byte_int = int(float(byte)) if not isinstance(byte, int) else byte
                return 0 <= byte_int <= 0x7F
            except (ValueError, TypeError):
                return False
        
        if any(not safe_validate_byte(byte) for byte in self.address):
            raise ValueError("Address bytes must be 0-127 (7-bit safe)")
        
        # Convert address bytes to integers if they aren't already
        self.address = [
            int(float(b)) if not isinstance(b, int) else b
            for b in self.address
        ]

        # Validate data bytes (must be 7-bit safe)
        # Safely convert and validate each byte
        def safe_validate_byte(byte):
            if isinstance(byte, int):
                return 0 <= byte <= 0x7F
            # Try to convert to int for validation
            try:
                byte_int = int(float(byte)) if not isinstance(byte, int) else byte
                return 0 <= byte_int <= 0x7F
            except (ValueError, TypeError):
                return False
        
        if any(not safe_validate_byte(byte) for byte in self.data):
            raise ValueError("Data bytes must be 0-127 (7-bit safe)")
        
        # Convert data bytes to integers if they aren't already
        self.data = [
            int(float(b)) if not isinstance(b, int) else b
            for b in self.data
        ]

        # Validate command
        if not (0 <= self.command <= 0x7F):
            raise ValueError(f"Command must be 0-127, got {self.command}")

    def calculate_checksum(self) -> int:
        """
        Calculate Roland checksum for the message.

        Roland checksum formula: (128 - (sum of address + data bytes & 0x7F)) & 0x7F
        This ensures the checksum is always a valid 7-bit MIDI value (0-127).

        :return: Checksum value (0-127)
        """
        # Helper to safely convert to int
        def safe_int(val):
            if isinstance(val, int):
                return val
            if hasattr(val, 'value'):  # Handle enums
                enum_val = val.value
                return int(enum_val) if not isinstance(enum_val, int) else enum_val
            try:
                return int(float(val))  # Handle floats and strings
            except (ValueError, TypeError):
                return 0
        
        # Ensure all values are integers before calculating checksum
        checksum_data = [safe_int(b) for b in (self.address + self.data)]
        return calculate_checksum(checksum_data)

    def to_list(self) -> List[int]:
        """
        Convert the SysEx message to a list of integers.

        Format: [F0, 41, device_id, model_id(4), command, address(4), data..., checksum, F7]

        :return: List of byte values (0-255)
        """
        # Helper to safely convert to int
        def safe_int(val):
            if isinstance(val, int):
                return val
            if hasattr(val, 'value'):  # Handle enums
                enum_val = val.value
                return int(enum_val) if not isinstance(enum_val, int) else enum_val
            try:
                return int(float(val))  # Handle floats and strings
            except (ValueError, TypeError):
                return 0
        
        msg = [
            Midi.SYSEX.START,  # F0
            safe_int(self.manufacturer_id),  # 0x41 (Roland)
            safe_int(self.device_id),
        ]
        msg.extend([safe_int(b) for b in self.model_id])  # 4 bytes
        msg.append(safe_int(self.command))
        msg.extend([safe_int(b) for b in self.address])  # 4 bytes
        msg.extend([safe_int(b) for b in self.data])  # Ensure all data bytes are integers
        msg.append(self.calculate_checksum())
        msg.append(Midi.SYSEX.END)  # F7
        return msg

    def to_bytes(self) -> bytes:
        """
        Convert message to bytes for transmission.

        :return: Bytes representation of the message
        """
        return bytes(self.to_list())

    @classmethod
    def from_bytes(cls, data: bytes) -> "RolandSysExMessage":
        """
        Parse a received Roland SysEx message from bytes.

        :param data: Raw SysEx message bytes
        :return: Parsed RolandSysExMessage instance
        :raises ValueError: If message format is invalid
        """
        if len(data) < 13:  # Minimum: F0 + 41 + dev + model(4) + cmd + addr(4) + chk + F7
            raise ValueError(
                f"Message too short: expected at least 13 bytes, got {len(data)}"
            )

        if data[0] != Midi.SYSEX.START:
            raise ValueError(f"Invalid start byte: expected 0xF0, got 0x{data[0]:02X}")

        if data[-1] != Midi.SYSEX.END:
            raise ValueError(f"Invalid end byte: expected 0xF7, got 0x{data[-1]:02X}")

        manufacturer_id = data[1]
        if manufacturer_id != 0x41:
            raise ValueError(
                f"Not a Roland message: manufacturer ID 0x{manufacturer_id:02X}"
            )

        device_id = data[2]
        model_id = list(data[3:7])  # 4 bytes
        command = data[7]
        address = list(data[8:12])  # 4 bytes
        checksum_byte = data[-2]  # Second-to-last byte
        data_bytes = list(data[12:-2])  # Everything between address and checksum

        # Create message instance
        message = cls(
            manufacturer_id=manufacturer_id,
            device_id=device_id,
            model_id=model_id,
            command=command,
            address=address,
            data=data_bytes,
        )

        # Verify checksum
        calculated_checksum = message.calculate_checksum()
        if calculated_checksum != checksum_byte:
            raise ValueError(
                f"Checksum mismatch: calculated 0x{calculated_checksum:02X}, "
                f"received 0x{checksum_byte:02X}"
            )

        return message

    def __repr__(self) -> str:
        """String representation of the message."""
        return (
            f"RolandSysExMessage("
            f"device_id=0x{self.device_id:02X}, "
            f"model_id=[{', '.join(f'0x{b:02X}' for b in self.model_id)}], "
            f"command=0x{self.command:02X}, "
            f"address=[{', '.join(f'0x{b:02X}' for b in self.address)}], "
            f"data={self.data})"
        )
