"""
roland_sysex.py
===============

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

import logging
from dataclasses import dataclass, field
from typing import List

from jdxi_editor.midi.data.address.address import (
    ModelID,
    CommandID,
    START_OF_SYSEX,
    END_OF_SYSEX,
    ZERO_BYTE,
    RolandID,
    AddressMemoryAreaMSB,
)
from jdxi_editor.midi.message.sysex import SysExMessage
from jdxi_editor.midi.utils.byte import split_value_to_nibbles


@dataclass
class RolandSysEx(SysExMessage):
    """Specialized class for Roland JD-Xi SysEx messages."""

    manufacturer_id: int = RolandID.ROLAND_ID
    device_id: int = RolandID.DEVICE_ID
    model_id: list[int] = field(
        default_factory=lambda: [
            ModelID.MODEL_ID_1,
            ModelID.MODEL_ID_2,
            ModelID.MODEL_ID_3,
            ModelID.MODEL_ID_4,
        ]
    )
    command: int = CommandID.DT1  # Default to Data Set 1 (DT1)
    address_msb: int = 0x00
    address_umb: int = 0x00
    address_lmb: int = 0x00
    address_lsb: int = 0x00
    value: int = 0x00
    size: int = 1

    # These attributes should not be set in `__init__`
    synth_type: int = field(init=False, default=None)
    part: int = field(init=False, default=None)

    dt1_command: int = CommandID.DT1  # Write command
    rq1_command: int = CommandID.RQ1  # Read command

    def __post_init__(self):
        """Initialize address and data based on parameters."""
        self.address = [
            self.address_msb,
            self.address_umb,
            self.address_lmb,
            self.address_lsb,
        ]
        if isinstance(self.value, int) and self.size == 4:
            self.data = split_value_to_nibbles(self.value)
        else:
            self.data = [self.value] if isinstance(self.value, int) else self.value

    def to_message_list(self) -> List[int]:
        """Convert the SysEx message to a list of integers."""
        msg = (
            [START_OF_SYSEX, self.manufacturer_id, self.device_id]
            + list(self.model_id)
            + [self.command]
            + self.address
            + self.data  # Directly append value (no extra list around it)
        )
        msg.append(self.calculate_checksum())
        msg.append(self.end_of_sysex)
        return msg

    def construct_sysex(self, address, *data_bytes, request=False):
        """Construct a SysEx message with a checksum and update instance variables."""
        logging.info(f"address: {address} data_bytes: {data_bytes} request: {request}")

        # Convert address and data_bytes from hex strings to integers if needed
        address = [int(a, 16) if isinstance(a, str) else a for a in address]
        data_bytes = [int(d, 16) if isinstance(d, str) else d for d in data_bytes]

        if len(address) != 4:
            raise ValueError(
                "Address must be a list of 4 bytes (area, synth_type, part, group)."
            )

        # Update instance variables
        self.address_msb, self.address_umb, self.address_lmb, self.address_lsb = address

        # Convert the value into nibbles (if it's 4 bytes long)
        if (
            isinstance(self.value, int) and 0 <= self.value <= 0xFFFFFFFF
        ):  # Check for 4-byte integer
            self.value = split_value_to_nibbles(self.value)  # @@@@

        # Determine parameter and value split
        if len(data_bytes) == 1:
            self.parameter = []
            self.value = data_bytes
        elif len(data_bytes) >= 2:
            self.parameter = data_bytes[:-1]
            self.value = [data_bytes[-1]]
        elif len(data_bytes) == 4:
            self.parameter = []
            self.value = data_bytes
        else:
            raise ValueError("Invalid data_bytes length. Must be 1, 2+, or 4.")

        command = self.rq1_command if request else self.dt1_command

        # **Validation 1: Ensure self.parameter and self.value are lists of integers**
        if not isinstance(self.parameter, list) or not all(
            isinstance(p, int) for p in self.parameter
        ):
            raise TypeError(
                f"Invalid parameter format: Expected list of integers, got {self.parameter}"
            )

        if not isinstance(self.value, list) or not all(
            isinstance(v, int) for v in self.value
        ):
            raise TypeError(
                f"Invalid value format: Expected list of integers, got {self.value}"
            )

        # **Validation 2: Ensure self.parameter and self.value are not empty if required**
        if len(self.parameter) == 0 and len(self.value) == 0:
            raise ValueError(
                "Both parameter and value cannot be empty. At least one must contain data."
            )

        required_values = {
            "manufacturer_id": self.manufacturer_id,
            "device_id": self.device_id,
            "model_id": self.model_id,
            "command": self.command,
            "address": address,
            "parameter": self.parameter,
            "value": self.value,
        }

        for key, value in required_values.items():
            if value is None:
                raise ValueError(f"Missing required value: {key} cannot be None.")

        # Construct SysEx message
        sysex_msg = (
            [START_OF_SYSEX, self.manufacturer_id, self.device_id]
            + list(self.model_id)
            + [command]
            + address
            + [self.parameter]
            + [self.value]
        )

        # Append checksum
        checksum = self.calculate_checksum()
        sysex_msg.append(checksum)
        sysex_msg.append(END_OF_SYSEX)

        return sysex_msg


@dataclass
class JDXiSysEx(RolandSysEx):
    """JD-Xi specific SysEx message"""

    model_id: List[int] = field(
        default_factory=lambda: [
            ModelID.MODEL_ID_1,
            ModelID.MODEL_ID_2,
            ModelID.MODEL_ID_3,
            ModelID.MODEL_ID_4,
        ]
    )  # JD-Xi model ID
    device_id: int = 0x10  # Default device ID
    command: int = CommandID.DT1  # Default to DT1 command
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
            RolandID.ROLAND_ID,  # Roland ID
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


@dataclass
class ParameterMessage(JDXiSysEx):
    """Base class for parameter messages"""

    command: int = CommandID.DT1

    def __post_init__(self):
        """Handle parameter value conversion"""
        super().__post_init__()

        # Convert parameter value if needed
        if hasattr(self, "convert_value"):
            self.data = self.convert_value(self.value)

    def convert_value(self, value: int) -> List[int]:
        """Convert parameter value to data bytes"""
        # Default implementation just returns single byte
        return [value]

    @classmethod
    def from_bytes(cls, data: bytes):
        """Create message from received bytes"""
        msg = super().from_bytes(data)

        # Convert data back to value if needed
        if hasattr(cls, "convert_data"):
            msg.value = cls.convert_data(msg.data)

        return msg

    @classmethod
    def convert_data(cls, data: List[int]) -> int:
        """Convert data bytes back to parameter value"""
        # Default implementation just returns first byte
        return data[0] if data else 0


@dataclass
class SystemMessage(ParameterMessage):
    """System parameter message"""

    address_msb: int = 0x02  # System area


@dataclass
class ProgramMessage(ParameterMessage):
    """Program parameter message"""

    address_msb: int = 0x18  # Program area


# Update other message classes to inherit from ParameterMessage
@dataclass
class Effect1Message(ParameterMessage):
    """Effect 1 parameter message"""

    address_msb: int = 0x18  # Program area
    address_umb: int = 0x02  # Effect 1 section


@dataclass
class Effect2Message(ParameterMessage):
    """Effect 2 parameter message"""

    address_msb: int = 0x18  # Program area
    address_umb: int = 0x04  # Effect 2 section


@dataclass
class DelayMessage(ParameterMessage):
    """Delay parameter message"""

    address_msb: int = 0x18  # Program area
    address_umb: int = 0x06  # Delay section


@dataclass
class ReverbMessage(ParameterMessage):
    """Reverb parameter message"""

    address_msb: int = 0x18  # Program area
    address_umb: int = 0x08  # Reverb section


@dataclass
class PartMessage(ParameterMessage):
    """Program Part parameter message"""

    address_msb: int = 0x18  # Program area
    address_umb: int = 0x00  # Part section

    def convert_value(self, value: int) -> List[int]:
        """Convert parameter value based on parameter preset_type"""
        # Parameters that need special conversion
        if self.address_lsb == 0x0B:  # Part Coarse Tune
            return [value + 64]  # Convert -48/+48 to 16-112
        elif self.address_lsb == 0x0C:  # Part Fine Tune
            return [value + 64]  # Convert -50/+50 to 14-114
        elif self.address_lsb == 0x13:  # Part Cutoff Offset
            return [value + 64]  # Convert -64/+63 to 0-127
        elif self.address_lsb == 0x14:  # Part Resonance Offset
            return [value + 64]  # Convert -64/+63 to 0-127
        elif self.address_lsb == 0x15:  # Part Attack Time Offset
            return [value + 64]  # Convert -64/+63 to 0-127
        elif self.address_lsb == 0x16:  # Part Decay Time Offset
            return [value + 64]  # Convert -64/+63 to 0-127
        elif self.address_lsb == 0x17:  # Part Release Time Offset
            return [value + 64]  # Convert -64/+63 to 0-127
        elif self.address_lsb == 0x18:  # Part Vibrato Rate
            return [value + 64]  # Convert -64/+63 to 0-127
        elif self.address_lsb == 0x19:  # Part Vibrato Depth
            return [value + 64]  # Convert -64/+63 to 0-127
        elif self.address_lsb == 0x1A:  # Part Vibrato Delay
            return [value + 64]  # Convert -64/+63 to 0-127
        elif self.address_lsb == 0x1B:  # Part Octave Shift
            return [value + 64]  # Convert -3/+3 to 61-67
        elif self.address_lsb == 0x1C:  # Part Velocity Sens Offset
            return [value + 64]  # Convert -63/+63 to 1-127
        elif self.address_lsb == 0x11:  # Part Portamento Time (2 bytes)
            if value == 128:  # TONE setting
                return [0x00, 0x80]
            else:
                return [0x00, value & 0x7F]

        # Default handling for other parameters
        return super().convert_value(value)

    @classmethod
    def convert_data(cls, data: List[int]) -> int:
        """Convert data bytes back to parameter value"""
        param = cls.address_lsb if hasattr(cls, "param") else 0

        # Parameters that need special conversion
        if param == 0x0B:  # Part Coarse Tune
            return data[0] - 64  # Convert 16-112 to -48/+48
        elif param == 0x0C:  # Part Fine Tune
            return data[0] - 64  # Convert 14-114 to -50/+50
        elif param in [0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1A]:
            return data[0] - 64  # Convert 0-127 to -64/+63
        elif param == 0x1B:  # Part Octave Shift
            return data[0] - 64  # Convert 61-67 to -3/+3
        elif param == 0x1C:  # Part Velocity Sens Offset
            return data[0] - 64  # Convert 1-127 to -63/+63
        elif param == 0x11:  # Part Portamento Time
            if data[1] & 0x80:  # TONE setting
                return 128
            else:
                return data[1] & 0x7F

        # Default handling for other parameters
        return super().convert_data(data)


@dataclass
class ZoneMessage(ParameterMessage):
    """Program Zone parameter message"""

    address_msb: int = 0x18  # Program area
    address_umb: int = 0x01  # Zone section

    def convert_value(self, value: int) -> List[int]:
        """Convert parameter value based on parameter preset_type"""
        # Parameters that need special conversion
        if self.address_lsb == 0x19:  # Zone Octave Shift
            return [value + 64]  # Convert -3/+3 to 61-67
        elif self.address_lsb == 0x03:  # Arpeggio Switch
            return [value & 0x01]  # Ensure boolean value

        # Default handling for other parameters
        return super().convert_value(value)

    @classmethod
    def convert_data(cls, data: List[int]) -> int:
        """Convert data bytes back to parameter value"""
        param = cls.address_lsb if hasattr(cls, "param") else 0

        # Parameters that need special conversion
        if param == 0x19:  # Zone Octave Shift
            return data[0] - 64  # Convert 61-67 to -3/+3
        elif param == 0x03:  # Arpeggio Switch
            return data[0] & 0x01  # Ensure boolean value

        # Default handling for other parameters
        return super().convert_data(data)


@dataclass
class ControllerMessage(ParameterMessage):
    """Program Controller parameter message"""

    address_msb: int = AddressMemoryAreaMSB.PROGRAM  # Program area
    address_umb: int = 0x40  # Controller section

    def convert_value(self, value: int) -> List[int]:
        """Convert parameter value based on parameter preset_type"""
        # Parameters that need special conversion
        if self.address_lsb == 0x07:  # Arpeggio Octave Range
            return [value + 64]  # Convert -3/+3 to 61-67

        # Default handling for other parameters
        return super().convert_value(value)

    @classmethod
    def convert_data(cls, data: List[int]) -> int:
        """Convert data bytes back to parameter value"""
        param = cls.address_lsb if hasattr(cls, "param") else 0

        # Parameters that need special conversion
        if param == 0x07:  # Arpeggio Octave Range
            return data[0] - 64  # Convert 61-67 to -3/+3

        # Default handling for other parameters
        return super().convert_data(data)


@dataclass
class DigitalToneCommonMessage(ParameterMessage):
    """SuperNATURAL Synth Tone Common parameter message"""

    address_msb: int = AddressMemoryAreaMSB.TEMPORARY_TONE  # Temporary area
    address_umb: int = ZERO_BYTE  # Common section

    def convert_value(self, value: int) -> List[int]:
        """Convert parameter value based on parameter preset_type"""
        # Parameters that need special conversion
        if self.address_lsb == 0x15:  # Octave Shift
            return [value + 64]  # Convert -3/+3 to 61-67

        # Default handling for other parameters
        return super().convert_value(value)

    @classmethod
    def convert_data(cls, data: List[int]) -> int:
        """Convert data bytes back to parameter value"""
        param = cls.address_lsb if hasattr(cls, "param") else 0

        # Parameters that need special conversion
        if param == 0x15:  # Octave Shift
            return data[0] - 64  # Convert 61-67 to -3/+3

        # Default handling for other parameters
        return super().convert_data(data)


@dataclass
class DigitalToneModifyMessage(ParameterMessage):
    """SuperNATURAL Synth Tone Modify parameter message"""

    address_msb: int = AddressMemoryAreaMSB.TEMPORARY_TONE  # Temporary area
    address_umb: int = 0x50  # Modify section @@@ looks incorrect - should be lmb

    def convert_value(self, value: int) -> List[int]:
        """Convert parameter value based on parameter preset_type"""
        # No special conversion needed for modify parameters
        return super().convert_value(value)

    @classmethod
    def convert_data(cls, data: List[int]) -> int:
        """Convert data bytes back to parameter value"""
        # No special conversion needed for modify parameters
        return super().convert_data(data)


@dataclass
class DigitalTonePartialMessage(ParameterMessage):
    """SuperNATURAL Synth Tone Partial parameter message"""

    address_msb: int = AddressMemoryAreaMSB.TEMPORARY_TONE  # Temporary area
    address_umb: int = 0x20  # Partial 1 section (0x20, 0x21, 0x22 for Partials 1-3)

    def convert_value(self, value: int) -> List[int]:
        """Convert parameter value based on parameter preset_type"""
        # Parameters that need special conversion
        if self.address_lsb == 0x00:  # OSC Wave
            return [value & 0x07]  # Ensure 3-bit value (0-7)
        elif self.address_lsb == 0x01:  # OSC Wave Variation
            return [value & 0x03]  # Ensure 2-bit value (0-2)

        # Default handling for other parameters
        return super().convert_value(value)

    @classmethod
    def convert_data(cls, data: List[int]) -> int:
        """Convert data bytes back to parameter value"""
        param = cls.address_lsb if hasattr(cls, "param") else 0

        # Parameters that need special conversion
        if param == 0x00:  # OSC Wave
            return data[0] & 0x07  # Extract 3-bit value
        elif param == 0x01:  # OSC Wave Variation
            return data[0] & 0x03  # Extract 2-bit value

        # Default handling for other parameters
        return super().convert_data(data)


@dataclass
class AnalogToneMessage(ParameterMessage):
    """Message for analog tone parameters"""

    address_msb: int
    address_umb: int
    address_lmb: int
    address_lsb: int
    value: int

    def to_message_list(self) -> List[int]:
        """Convert to SysEx message bytes"""
        return [
            START_OF_SYSEX,  # Start of SysEx
            RolandID.ROLAND_ID,  # Roland ID
            RolandID.DEVICE_ID,  # Device ID
            ModelID.MODEL_ID_1,
            ModelID.MODEL_ID_2,
            ModelID.MODEL_ID_3,
            ModelID.MODEL_ID_4,  # Model ID
            CommandID.DT1,  # DT1 Command
            self.address_msb,
            self.address_umb,
            self.address_lmb,
            self.address_lsb,
            self.value,
            ZERO_BYTE,  # Checksum placeholder
            END_OF_SYSEX,  # End of SysEx
        ]


@dataclass
class DrumKitCommonMessage(ParameterMessage):
    """Drum Kit Common parameter message"""

    address_msb: int = AddressMemoryAreaMSB.TEMPORARY_TONE  # Temporary area
    address_umb: int = 0x10  # Drum Kit section
    address_lmb: int = 0x00  # Common area

    def convert_value(self, value: int) -> List[int]:
        """Convert parameter value based on parameter preset_type"""
        # No special conversion needed for drum kit common parameters
        return super().convert_value(value)

    @classmethod
    def convert_data(cls, data: List[int]) -> int:
        """Convert data bytes back to parameter value"""
        # No special conversion needed for drum kit common parameters
        return super().convert_data(data)


@dataclass
class DrumKitPartialMessage(ParameterMessage):
    """Drum Kit Partial parameter message"""

    address_msb: int = AddressMemoryAreaMSB.TEMPORARY_TONE  # Temporary area
    address_umb: int = 0x10  # Drum Kit section
    address_lmb: int = 0x01  # Partial area

    def convert_value(self, value: int) -> List[int]:
        """Convert parameter value based on parameter preset_type"""
        # Parameters that need special conversion
        if self.address_lsb == 0x10:  # Fine Tune
            return [value + 64]  # Convert -50/+50 to 14-114
        elif self.address_lsb == 0x14:  # Alternate Pan
            return [value + 64]  # Convert L63-63R to 1-127

        # Default handling for other parameters
        return super().convert_value(value)

    @classmethod
    def convert_data(cls, data: List[int]) -> int:
        """Convert data bytes back to parameter value"""
        param = cls.address_lsb if hasattr(cls, "param") else 0

        # Parameters that need special conversion
        if param == 0x10:  # Fine Tune
            return data[0] - 64  # Convert 14-114 to -50/+50
        elif param == 0x14:  # Alternate Pan
            return data[0] - 64  # Convert 1-127 to L63-63R

        # Default handling for other parameters
        return super().convert_data(data)


def create_sysex_message(
    address_msb: int, address_umb: int, address_lmb: int, address_lsb: int, value: int
) -> JDXiSysEx:
    """Create address JD-Xi SysEx message with the given parameters"""
    return JDXiSysEx(
        command=CommandID.DT1,
        address_msb=address_msb,
        address_umb=address_umb,
        address_lmb=address_lmb,
        address_lsb=address_lsb,
        value=value,
    )


def create_patch_load_message(
    bank_msb: int, bank_lsb: int, program: int
) -> List[JDXiSysEx]:
    """Create messages to load address patch (bank select + program change)"""
    return [
        # Bank Select MSB
        JDXiSysEx(
            command=CommandID.DT1,
            address_msb=AddressMemoryAreaMSB.SYSTEM,  # Setup area 0x01
            address_umb=0x00,
            address_lmb=0x00,
            address_lsb=0x04,  # Bank MSB parameter
            value=bank_msb,
        ),
        # Bank Select LSB
        JDXiSysEx(
            command=CommandID.DT1,
            address_msb=AddressMemoryAreaMSB.SYSTEM,  # Setup area
            address_umb=0x00,
            address_lmb=0x00,
            address_lsb=0x05,  # Bank LSB parameter
            value=bank_lsb,
        ),
        # Program Change
        JDXiSysEx(
            command=CommandID.DT1,
            address_msb=AddressMemoryAreaMSB.SYSTEM,  # Setup area
            address_umb=0x00,
            address_lmb=0x00,
            address_lsb=0x06,  # Program number parameter
            value=program,
        ),
    ]


def create_patch_request_message(
    address_msb: int, address_umb: int = 0x00, size: int = 0
) -> JDXiSysEx:
    """Create address message to request patch data"""
    return JDXiSysEx(
        command=CommandID.RQ1,  # Data request command
        address_msb=address_msb,
        address_umb=address_umb,
        address_lmb=0x00,
        address_lsb=0x00,
        data=[size] if size else [],  # Some requests need address size parameter
    )
