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
received_bytes = b'\xf0\x41\x10\x12\x00\x01\x02\x03\x04\x05\xf7'  # Example received SysEx message
parsed_message = RolandSysEx.from_bytes(received_bytes)
print("Parsed Command:", parsed_message.command)
print("Parsed Address:", parsed_message.address)
print("Parsed Value:", parsed_message.value)

"""

from dataclasses import dataclass, field
from typing import List, Optional, Union

from decologr import Decologr as log
from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.address.address import (
    AddressStartMSB,
    CommandID,
    ModelID,
    RolandSysExAddress,
)
from jdxi_editor.midi.data.address.sysex import (
    END_OF_SYSEX,
    START_OF_SYSEX,
    ZERO_BYTE,
    RolandID,
)
from jdxi_editor.midi.message.sysex.offset import JDXiSysExMessageLayout
from picomidi import RolandSysExMessage
from picomidi.constant import Midi
from picomidi.core.bitmask import BitMask
from picomidi.utils.conversion import split_16bit_value_to_nibbles


@dataclass
class JDXiSysEx(RolandSysExMessage):
    """
    JD-Xi specialized class for Roland SysEx messages.

    Inherits from PicoMidi's generic RolandSysExMessage and adds
    JD-Xi specific features like address object handling,
    automatic value conversion, and JD-Xi validation.
    """

    # JD-Xi specific defaults
    device_id: int = RolandID.DEVICE_ID
    model_id: List[int] = field(
        default_factory=lambda: [
            ModelID.MODEL_ID_1,
            ModelID.MODEL_ID_2,
            ModelID.MODEL_ID_3,
            ModelID.MODEL_ID_4,
        ]
    )
    command: int = CommandID.DT1

    # --- JD-Xi specific address handling
    sysex_address: Optional[RolandSysExAddress] = None
    msb: int = Midi.VALUE.ZERO
    umb: int = Midi.VALUE.ZERO
    lmb: int = Midi.VALUE.ZERO
    lsb: int = Midi.VALUE.ZERO

    # --- JD-Xi specific value handling
    value: Union[int, List[int]] = Midi.VALUE.ZERO
    size: int = 1

    # --- JD-Xi specific attributes
    synth_type: Optional[int] = field(init=False, default=None)
    part: Optional[int] = field(init=False, default=None)

    dt1_command: int = CommandID.DT1
    rq1_command: int = CommandID.RQ1

    def __post_init__(self) -> None:
        """Initialize JD-Xi specific features, then call parent."""

        # Helper function to safely convert to int (handles enums, strings, etc.)
        def safe_int(value):
            if isinstance(value, int):
                return value
            # Handle enums - extract the actual value
            if hasattr(value, "value"):
                enum_value = value.value
                if isinstance(enum_value, int):
                    return enum_value
                try:
                    return int(enum_value)
                except (ValueError, TypeError):
                    return 0
            try:
                return int(float(value))  # Handle floats and strings
            except (ValueError, TypeError):
                return 0

        # Convert enum values to integers for parent class (do this first, BEFORE parent validation)
        self.device_id = safe_int(self.device_id)
        if isinstance(self.model_id, list) and len(self.model_id) > 0:
            self.model_id = [safe_int(b) for b in self.model_id]
        self.command = safe_int(self.command)

        # Handle sysex_address object (if provided, it overrides msb/umb/lmb/lsb)
        if self.sysex_address:
            self.msb = self.sysex_address.msb
            self.umb = self.sysex_address.umb
            self.lmb = self.sysex_address.lmb
            self.lsb = self.sysex_address.lsb

        # Build address list from individual bytes (only if address wasn't explicitly set)
        # If address was passed directly, use it; otherwise build from msb/umb/lmb/lsb
        if self.address == [0x00, 0x00, 0x00, 0x00]:  # Default value
            # Ensure all address bytes are integers
            self.address = [
                safe_int(self.msb),
                safe_int(self.umb),
                safe_int(self.lmb),
                safe_int(self.lsb),
            ]
        else:
            # Address was explicitly set, ensure all bytes are integers and update msb/umb/lmb/lsb
            self.address = [safe_int(b) for b in self.address]
            self.msb, self.umb, self.lmb, self.lsb = self.address

        # Handle value conversion (JD-Xi specific)
        # IMPORTANT: Convert data to integers BEFORE parent __post_init__ runs
        # Only convert if data wasn't explicitly set and value is provided
        if not self.data or self.data == []:
            if isinstance(self.value, int) and self.size == 4:
                self.data = split_16bit_value_to_nibbles(safe_int(self.value))
            elif isinstance(self.value, int):
                self.data = [safe_int(self.value)]
            elif isinstance(self.value, list):
                # Ensure all values in the list are integers
                self.data = [safe_int(v) for v in self.value]
            else:
                # Handle string, float, or other types
                try:
                    val_int = safe_int(self.value)
                    self.data = (
                        [val_int]
                        if self.size == 1
                        else split_16bit_value_to_nibbles(val_int)
                    )
                except (ValueError, TypeError):
                    self.data = [0]  # Fallback to 0

        # Ensure all data bytes are integers (in case data was set explicitly)
        # This MUST happen before parent __post_init__ runs
        if self.data:
            self.data = [safe_int(b) for b in self.data]

        # Call parent __post_init__ to validate message structure
        # At this point, self.address and self.data are guaranteed to be lists of integers
        super().__post_init__()

        # JD-Xi specific validation (merged from JDXiSysExOld)
        # Validate device ID (ensure it's an integer for formatting)
        device_id_int = safe_int(self.device_id)
        if not (0x00 <= device_id_int <= 0x1F or device_id_int == 0x7F):
            raise ValueError(f"Invalid device ID: {device_id_int:02X}")

        # Validate model ID matches JD-Xi (ensure all values are integers)
        expected_model_id = [
            ModelID.MODEL_ID_1,
            ModelID.MODEL_ID_2,
            ModelID.MODEL_ID_3,
            ModelID.MODEL_ID_4,
        ]
        # Convert both to integers for comparison and formatting
        model_id_ints = [safe_int(x) for x in self.model_id]
        expected_model_id_ints = [safe_int(x) for x in expected_model_id]
        if model_id_ints != expected_model_id_ints:
            raise ValueError(
                f"Invalid model ID: {[f'{safe_int(x):02X}' for x in model_id_ints]}"
            )

        # --- Validate address bytes (ensure all values are integers)
        address_ints = [safe_int(x) for x in self.address]
        if not all(ZERO_BYTE <= x <= BitMask.FULL_BYTE for x in address_ints):
            raise ValueError(
                f"Invalid address bytes: {[f'{safe_int(x):02X}' for x in address_ints]}"
            )

    def from_sysex_address(self, sysex_address: RolandSysExAddress) -> None:
        """
        Update address from RolandSysExAddress object.

        :param sysex_address: RolandSysExAddress
        :return: None
        """
        self.msb = sysex_address.msb
        self.umb = sysex_address.umb
        self.lmb = sysex_address.lmb
        self.lsb = sysex_address.lsb
        self.address = [self.msb, self.umb, self.lmb, self.lsb]

    def to_message_list(self) -> List[int]:
        """
        Convert to message list using parent implementation.

        Maintains backward compatibility with existing code that calls to_message_list().

        :return: List[int]
        """
        # Use parent's implementation which handles checksum correctly
        return super().to_list()

    def to_list(self) -> List[int]:
        """
        Alias for to_message_list() for compatibility with PicoMidi Message interface.

        :return: List[int]
        """
        return self.to_message_list()

    def to_bytes(self) -> bytes:
        """
        Convert message to bytes for sending.

        :return: bytes representation of the message
        """
        return bytes(self.to_list())

    @classmethod
    def from_bytes(cls, data: bytes) -> "JDXiSysEx":
        """
        Create message from received bytes with JD-Xi specific validation.

        :param data: Raw SysEx message bytes
        :return: Parsed JDXiSysEx instance
        :raises ValueError: If message format is invalid or not JD-Xi
        """
        if (
            len(data)
            < JDXi.Midi.SYSEX.PARAMETER.LENGTH.ONE_BYTE  # --- Minimum length: F0 + ID + dev + model(4) + cmd + addr(4) + sum + F7
            or data[JDXiSysExMessageLayout.START] != START_OF_SYSEX
            or data[JDXiSysExMessageLayout.ROLAND_ID] != RolandID.ROLAND_ID  # Roland ID
            or data[
                JDXiSysExMessageLayout.MODEL_ID.POS1 : JDXiSysExMessageLayout.COMMAND_ID
            ]
            != bytes(
                [
                    ModelID.MODEL_ID_1,
                    ModelID.MODEL_ID_2,
                    ModelID.MODEL_ID_3,
                    ModelID.MODEL_ID_4,
                ]
            )
        ):  # JD-Xi model ID
            raise ValueError("Invalid JD-Xi SysEx message")

        device_id = data[JDXiSysExMessageLayout.DEVICE_ID]
        command = data[JDXiSysExMessageLayout.COMMAND_ID]
        address = list(
            data[
                JDXiSysExMessageLayout.ADDRESS.MSB : JDXiSysExMessageLayout.TONE_NAME.START
            ]
        )
        message_data = list(
            data[
                JDXiSysExMessageLayout.TONE_NAME.START : JDXiSysExMessageLayout.CHECKSUM
            ]
        )  # Everything between address and checksum
        received_checksum = data[JDXiSysExMessageLayout.CHECKSUM]

        # Create message and verify checksum
        message = cls(
            device_id=device_id, command=command, address=address, data=message_data
        )

        if message.calculate_checksum() != received_checksum:
            raise ValueError("Invalid checksum")

        return message

    def construct_sysex(
        self,
        address: RolandSysExAddress,
        *data_bytes: Union[List[int], int],
        request: bool = False,
    ) -> List[int]:
        """
        Construct a SysEx message based on the provided address and data bytes.

        :param address: RolandSysExAddress
        :param data_bytes: list of data bytes
        :param request: bool is this a request?
        :return: None
        """
        log.message(f"address: {address} data_bytes: {data_bytes} request: {request}")

        # --- Handle address fields directly
        addr_list = [address.msb, address.umb, address.lmb, address.lsb]

        # --- Flatten and normalize data_bytes
        flat_data: List[int] = []
        for db in data_bytes:
            if isinstance(db, list):
                flat_data.extend(int(d, 16) if isinstance(d, str) else d for d in db)
            else:
                flat_data.append(int(db, 16) if isinstance(db, str) else db)

        if len(flat_data) == 1:
            self.parameter = []
            self.value = flat_data
        elif len(flat_data) >= 2 and len(flat_data) != 4:
            self.parameter = flat_data[:-1]
            self.value = [flat_data[-1]]
        elif len(flat_data) == 4:
            self.parameter = []
            self.value = flat_data
        else:
            raise ValueError("Invalid data_bytes length. Must be 1, 2+, or 4.")

        command = self.rq1_command if request else self.dt1_command

        if not all(isinstance(p, int) for p in self.parameter):
            raise TypeError("Parameter list must contain only integers.")
        if not all(isinstance(v, int) for v in self.value):
            raise TypeError("Value list must contain only integers.")
        if len(self.parameter) == 0 and len(self.value) == 0:
            raise ValueError("Both parameter and value cannot be empty.")

        required_values = {
            "manufacturer_id": self.manufacturer_id,
            "device_id": self.device_id,
            "model_id": self.model_id,
            "command": self.command,
            "address": addr_list,
            "parameter": self.parameter,
            "value": self.value,
        }

        for key, val in required_values.items():
            if val is None:
                raise ValueError(f"Missing required value: {key} cannot be None.")

        sysex_msg: List[Union[int, List[int]]] = (
            [START_OF_SYSEX, self.manufacturer_id, self.device_id]
            + list(self.model_id)
            + [command]
            + addr_list
            + self.parameter
            + self.value
        )

        sysex_msg.append(self.calculate_checksum())
        sysex_msg.append(END_OF_SYSEX)

        return sysex_msg


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

    def convert_value(self, value: int) -> list[int]:
        """
        Convert parameter value to data bytes

        :param value: int
        :return: list[int]
        """
        # Default implementation just returns single byte
        return [value]

    @classmethod
    def from_bytes(cls, data: bytes) -> JDXiSysEx:
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

    msb: int = 0x02  # System area


@dataclass
class ProgramMessage(ParameterMessage):
    """Program parameter message"""

    msb: int = 0x18  # Program area


# Update other message classes to inherit from ParameterMessage
@dataclass
class Effect1Message(ParameterMessage):
    """Effect 1 parameter message"""

    msb: int = 0x18  # Program area
    umb: int = 0x02  # Effect 1 section


@dataclass
class Effect2Message(ParameterMessage):
    """Effect 2 parameter message"""

    msb: int = 0x18  # Program area
    umb: int = 0x04  # Effect 2 section


@dataclass
class DelayMessage(ParameterMessage):
    """Delay parameter message"""

    msb: int = 0x18  # Program area
    umb: int = 0x06  # Delay section


@dataclass
class ReverbMessage(ParameterMessage):
    """Reverb parameter message"""

    msb: int = 0x18  # Program area
    umb: int = 0x08  # Reverb section


@dataclass
class PartMessage(ParameterMessage):
    """Program Part parameter message"""

    msb: int = 0x18  # Program area
    umb: int = 0x00  # Part section

    def convert_value(self, value: int) -> List[int]:
        """Convert parameter value based on parameter preset_type"""
        # Parameters that need special conversion
        if self.lsb == 0x0B:  # Part Coarse Tune
            return [value + 64]  # Convert -48/+48 to 16-112
        elif self.lsb == 0x0C:  # Part Fine Tune
            return [value + 64]  # Convert -50/+50 to 14-114
        elif self.lsb == 0x13:  # Part Cutoff Offset
            return [value + 64]  # Convert -64/+63 to 0-127
        elif self.lsb == 0x14:  # Part Resonance Offset
            return [value + 64]  # Convert -64/+63 to 0-127
        elif self.lsb == 0x15:  # Part Attack Time Offset
            return [value + 64]  # Convert -64/+63 to 0-127
        elif self.lsb == 0x16:  # Part Decay Time Offset
            return [value + 64]  # Convert -64/+63 to 0-127
        elif self.lsb == 0x17:  # Part Release Time Offset
            return [value + 64]  # Convert -64/+63 to 0-127
        elif self.lsb == 0x18:  # Part Vibrato Rate
            return [value + 64]  # Convert -64/+63 to 0-127
        elif self.lsb == 0x19:  # Part Vibrato Depth
            return [value + 64]  # Convert -64/+63 to 0-127
        elif self.lsb == 0x1A:  # Part Vibrato Delay
            return [value + 64]  # Convert -64/+63 to 0-127
        elif self.lsb == 0x1B:  # Part Octave Shift
            return [value + 64]  # Convert -3/+3 to 61-67
        elif self.lsb == 0x1C:  # Part Velocity Sens Offset
            return [value + 64]  # Convert -63/+63 to 1-127
        elif self.lsb == 0x11:  # Part Portamento Time (2 bytes)
            if value == 128:  # TONE setting
                return [0x00, 0x80]
            else:
                return [0x00, value & 0x7F]

        # Default handling for other parameters
        return super().convert_value(value)

    @classmethod
    def convert_data(cls, data: List[int]) -> int:
        """Convert data bytes back to parameter value"""
        param = cls.lsb if hasattr(cls, "param") else 0

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

    msb: int = 0x18  # Program area
    umb: int = 0x01  # Zone section

    def convert_value(self, value: int) -> List[int]:
        """Convert parameter value based on parameter preset_type"""
        # Parameters that need special conversion
        if self.lsb == 0x19:  # Zone Octave Shift
            return [value + 64]  # Convert -3/+3 to 61-67
        elif self.lsb == 0x03:  # Arpeggio Switch
            return [value & 0x01]  # Ensure boolean value

        # Default handling for other parameters
        return super().convert_value(value)

    @classmethod
    def convert_data(cls, data: List[int]) -> int:
        """Convert data bytes back to parameter value"""
        param = cls.lsb if hasattr(cls, "param") else 0

        # --- Parameters that need special conversion
        if param == 0x19:  # Zone Octave Shift
            return data[0] - 64  # Convert 61-67 to -3/+3
        elif param == 0x03:  # Arpeggio Switch
            return data[0] & 0x01  # Ensure boolean value

        # --- Default handling for other parameters
        return super().convert_data(data)


@dataclass
class ControllerMessage(ParameterMessage):
    """Program Controller parameter message"""

    msb: int = AddressStartMSB.TEMPORARY_PROGRAM  # Program area
    umb: int = 0x40  # Controller section

    def convert_value(self, value: int) -> List[int]:
        """
        Convert parameter value based on parameter preset_type

        :param value:
        :return: List[int]
        """
        # --- Parameters that need special conversion
        if self.lsb == 0x07:  # Arpeggio Octave Range
            return [value + 64]  # Convert -3/+3 to 61-67

        # --- Default handling for other parameters
        return super().convert_value(value)

    @classmethod
    def convert_data(cls, data: List[int]) -> int:
        """
        Convert data bytes back to parameter value

        :param data: List
        :return: int
        """
        param = cls.lsb if hasattr(cls, "param") else 0

        # --- Parameters that need special conversion
        if param == 0x07:  # Arpeggio Octave Range
            return data[0] - 64  # Convert 61-67 to -3/+3

        # --- Default handling for other parameters
        return super().convert_data(data)


@dataclass
class DigitalToneCommonMessage(ParameterMessage):
    """SuperNATURAL Synth Tone Common parameter message"""

    msb: int = AddressStartMSB.TEMPORARY_TONE  # Temporary area
    umb: int = ZERO_BYTE  # Common section

    def convert_value(self, value: int) -> List[int]:
        """
        Convert parameter value based on parameter preset_type

        :param value:
        :return: List[int]
        """
        # Parameters that need special conversion
        if self.lsb == 0x15:  # Octave Shift
            return [value + 64]  # Convert -3/+3 to 61-67

        # Default handling for other parameters
        return super().convert_value(value)

    @classmethod
    def convert_data(cls, data: List[int]) -> int:
        """
        Convert data bytes back to parameter value

        :param data: List
        :return: int
        """
        param = cls.lsb if hasattr(cls, "param") else 0

        # --- Parameters that need special conversion
        if param == 0x15:  # Octave Shift
            return data[0] - 64  # Convert 61-67 to -3/+3

        # --- Default handling for other parameters
        return super().convert_data(data)


@dataclass
class DigitalToneModifyMessage(ParameterMessage):
    """SuperNATURAL Synth Tone Modify parameter message"""

    msb: int = AddressStartMSB.TEMPORARY_TONE  # Temporary area
    umb: int = 0x50  # Modify section @@@ looks incorrect - should be lmb

    def convert_value(self, value: int) -> List[int]:
        """
        Convert parameter value based on parameter preset_type

        :param value:
        :return: List[int]
        """
        # No special conversion needed for modify parameters
        return super().convert_value(value)

    @classmethod
    def convert_data(cls, data: List[int]) -> int:
        """
        Convert data bytes back to parameter value

        :param data: List
        :return: int
        """
        # No special conversion needed for modify parameters
        return super().convert_data(data)


@dataclass
class DigitalTonePartialMessage(ParameterMessage):
    """SuperNATURAL Synth Tone Partial parameter message"""

    msb: int = AddressStartMSB.TEMPORARY_TONE  # Temporary area
    umb: int = 0x20  # Partial 1 section (0x20, 0x21, 0x22 for Partials 1-3)

    def convert_value(self, value: int) -> List[int]:
        """
        Convert parameter value based on parameter preset_type

        :param value:
        :return: List[int]
        """
        # Parameters that need special conversion
        if self.lsb == 0x00:  # OSC Wave
            return [value & 0x07]  # Ensure 3-bit value (0-7)
        elif self.lsb == 0x01:  # OSC Wave Variation
            return [value & 0x03]  # Ensure 2-bit value (0-2)

        # Default handling for other parameters
        return super().convert_value(value)

    @classmethod
    def convert_data(cls, data: List[int]) -> int:
        """
        Convert data bytes back to parameter value

        :param data: List
        :return: int
        """
        param = cls.lsb if hasattr(cls, "param") else 0

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

    msb: int = 0
    umb: int = 0
    lmb: int = 0
    lsb: int = 0
    value: int = 0

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
            self.msb,
            self.umb,
            self.lmb,
            self.lsb,
            self.value,
            ZERO_BYTE,  # Checksum placeholder
            END_OF_SYSEX,  # End of SysEx
        ]


@dataclass
class DrumKitCommonMessage(ParameterMessage):
    """Drum Kit Common parameter message"""

    msb: int = AddressStartMSB.TEMPORARY_TONE  # Temporary area
    umb: int = 0x10  # Drum Kit section
    lmb: int = 0x00  # Common area

    def convert_value(self, value: int) -> List[int]:
        """
        Convert parameter value based on parameter preset_type

        :param value:
        :return: List[int]
        """
        # No special conversion needed for drum kit common parameters
        return super().convert_value(value)

    @classmethod
    def convert_data(cls, data: List[int]) -> int:
        """
        Convert data bytes back to parameter value

        :param data: List
        :return: int
        """
        # No special conversion needed for drum kit common parameters
        return super().convert_data(data)


@dataclass
class DrumKitPartialMessage(ParameterMessage):
    """Drum Kit Partial parameter message"""

    msb: int = AddressStartMSB.TEMPORARY_TONE  # Temporary area
    umb: int = 0x10  # Drum Kit section
    lmb: int = 0x01  # Partial area

    def convert_value(self, value: int) -> List[int]:
        """
        Convert parameter value based on parameter preset_type

        :param value:
        :return: List[int]
        """
        # Parameters that need special conversion
        if self.lsb == 0x10:  # Fine Tune
            return [value + 64]  # Convert -50/+50 to 14-114
        elif self.lsb == 0x14:  # Alternate Pan
            return [value + 64]  # Convert L63-63R to 1-127

        # Default handling for other parameters
        return super().convert_value(value)

    @classmethod
    def convert_data(cls, data: List[int]) -> int:
        """
        Convert data bytes back to parameter value

        :param data: List
        :return: int
        """
        param = cls.lsb if hasattr(cls, "param") else 0

        # Parameters that need special conversion
        if param == 0x10:  # Fine Tune
            return data[0] - 64  # Convert 14-114 to -50/+50
        elif param == 0x14:  # Alternate Pan
            return data[0] - 64  # Convert 1-127 to L63-63R

        # Default handling for other parameters
        return super().convert_data(data)


def create_sysex_message(
    msb: int, umb: int, lmb: int, lsb: int, value: int
) -> JDXiSysEx:
    """Create address JD-Xi SysEx message with the given parameters"""
    return JDXiSysEx(
        command=CommandID.DT1,
        msb=msb,
        umb=umb,
        lmb=lmb,
        lsb=lsb,
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
            msb=AddressStartMSB.SYSTEM,  # Setup area 0x01
            umb=0x00,
            lmb=0x00,
            lsb=0x04,  # Bank MSB parameter
            value=bank_msb,
        ),
        # Bank Select LSB
        JDXiSysEx(
            command=CommandID.DT1,
            msb=AddressStartMSB.SYSTEM,  # Setup area
            umb=0x00,
            lmb=0x00,
            lsb=0x05,  # Bank LSB parameter
            value=bank_lsb,
        ),
        # Program Change
        JDXiSysEx(
            command=CommandID.DT1,
            msb=AddressStartMSB.SYSTEM,  # Setup area
            umb=0x00,
            lmb=0x00,
            lsb=0x06,  # Program number parameter
            value=program,
        ),
    ]


def create_patch_request_message(msb: int, umb: int = 0x00, size: int = 0) -> JDXiSysEx:
    """Create address message to request patch data"""
    return JDXiSysEx(
        command=CommandID.RQ1,  # Data request command
        msb=msb,
        umb=umb,
        lmb=0x00,
        lsb=0x00,
        data=[size] if size else [],  # Some requests need address size parameter
    )
