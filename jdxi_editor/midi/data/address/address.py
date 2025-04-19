"""
Parameter Address Map

Usage example:
==============

class AddressMemoryAreaMSB(Address):
    PROGRAM = 0x18
    TEMPORARY_TONE = 0x19

# Add an offset to a base address
addr_bytes = AddressMemoryAreaMSB.PROGRAM.add_offset((0x00, 0x20, 0x00))
print(addr_bytes)  # (0x18, 0x00, 0x20, 0x00)

# Get SysEx-ready address
sysex_address = AddressMemoryAreaMSB.PROGRAM.to_sysex_address((0x00, 0x20, 0x00))
print(sysex_address)  # b'\x18\x00\x20\x00'

# Lookup
found = AddressMemoryAreaMSB.get_parameter_by_address(0x19)
print(found)  # ProgramAddress.TEMPORARY_TONE

SysExByte

# Example usage:
command = CommandID.DT1
print(f"Command: {command}, Value: {command.value}, Message Position: {command.message_position}")
"""

from enum import IntEnum, unique
from typing import Optional, Type, TypeVar, Union, Tuple, Dict, Any
import inspect

from jdxi_editor.log.message import log_parameter
from jdxi_editor.midi.data.address.sysexbyte import SysExByte
from jdxi_editor.midi.data.parameter.drum.addresses import DRUM_ADDRESS_MAP

# ==========================
# Miscellaneous Constants
# ==========================


START_OF_SYSEX = 0xF0
END_OF_SYSEX = 0xF7
ID_NUMBER = 0x7E
DEVICE_ID = 0x7F
SUB_ID_1 = 0x06
SUB_ID_2 = 0x01
ZERO_BYTE = 0x00


# ==========================
# Helpers
# ==========================


T = TypeVar("T", bound="Address")


class Address(SysExByte):
    """
    Base class for Roland-style hierarchical memory address enums (e.g., 0x18, 0x19, etc.)
    Includes lookup, offset arithmetic, and SysEx-ready address formatting.
    """

    def add_offset(
        self, address_offset: Union[int, Tuple[int, int, int]]
    ) -> tuple[int, Any]:
        """
        Returns the full 4-byte address by adding a 3-byte offset to the base address.
        The base address is assumed to be a single byte (e.g., 0x18).
        """
        base = self.value
        if isinstance(address_offset, int):
            offset_bytes = [(address_offset >> 16) & 0xFF, (address_offset >> 8) & 0xFF, address_offset & 0xFF]
        elif isinstance(address_offset, tuple) and len(address_offset) == 3:
            offset_bytes = list(address_offset)
        else:
            raise ValueError("Offset must be an int or a 3-byte tuple")
        if any(b > 0x7F for b in offset_bytes):
            raise ValueError("SysEx address bytes must be 7-bit (0x00 to 0x7F)")
        return base, *offset_bytes

    def to_sysex_address(
        self, address_offset: Union[int, Tuple[int, int, int]] = (0, 0, 0)
    ) -> bytes:
        """
        Returns the full 4-byte address as a `bytes` object, suitable for SysEx messages.
        """
        return bytes(self.add_offset(address_offset))

    @classmethod
    def from_sysex_bytes(cls: Type[T], address: bytes) -> Optional[T]:
        if len(address) != 4:
            return None
        return cls.get_parameter_by_address(address[0])

    def __repr__(self):
        return f"<{self.__class__.__name__}.{self.name}: 0x{self.value:02X}>"
    
    def __str__(self):
        return f"{self.__class__.__name__}.{self.name}: 0x{self.value:02X}"


def construct_address(base_address, address_umb, address_lmb, param):
    """Build a full SysEx address by combining a base address, static offsets, and a parameter offset."""
    log_parameter("base address:", base_address)
    log_parameter("address_umb:", address_umb)
    log_parameter("address_lmb:", address_lmb)
    log_parameter("parameter:", param)

    base_offset = (address_umb.value, address_lmb.value, 0x00)
    param_offset = param.get_offset()  # e.g., (0, 0, 3)

    final_offset = tuple(
        (bo + po) & 0x7F for bo, po in zip(base_offset, param_offset)
    )
    log_parameter("base offset:", base_offset)
    log_parameter("param offset:", param_offset)
    log_parameter("final offset:", final_offset)

    full_address = base_address.add_offset(final_offset)
    sysex_address = base_address.to_sysex_address(final_offset)

    log_parameter("sysex_address:", sysex_address)
    return base_address, full_address, final_offset


# Short maps
DIGITAL_PARTIAL_MAP = {i: 0x1F + i for i in range(1, 4)}  # 1: 0x20, 2: 0x21, 3: 0x22


# ==========================
# Roland IDs and Commands
# ==========================


@unique
class RolandID(IntEnum):
    ROLAND_ID = 0x41
    DEVICE_ID = 0x10


# ==========================
# JD-Xi SysEx Header
# ==========================


class ModelID(Address):
    ROLAND_ID = 0x41
    DEVICE_ID = 0x10
    # Model ID bytes
    MODEL_ID_1 = ZERO_BYTE  # Manufacturer ID extension
    MODEL_ID_2 = ZERO_BYTE  # Device family code MSB
    MODEL_ID_3 = ZERO_BYTE  # Device family code LSB
    MODEL_ID_4 = 0x0E  # JD-XI Product code


JD_XI_MODEL_ID = [
    ModelID.MODEL_ID_1,
    ModelID.MODEL_ID_2,
    ModelID.MODEL_ID_3,
    ModelID.MODEL_ID_4,
]

JD_XI_HEADER_LIST = [RolandID.ROLAND_ID, RolandID.DEVICE_ID, *JD_XI_MODEL_ID]


@unique
class CommandID(SysExByte):
    """Roland Commands"""

    DT1 = 0x12  # Data Set 1
    RQ1 = 0x11  # Data Request 1

    @classmethod
    def message_position(cls):
        """Return the fixed message position for command bytes."""
        return 7


@unique
class ResponseID(IntEnum):
    """midi responses"""

    ACK = 0x4F  # Acknowledge
    ERR = 0x4E  # Error


# ==========================
# Memory and Program Areas
# ==========================


@unique
class AddressMemoryAreaMSB(Address):
    SYSTEM = 0x01
    SETUP = 0x02
    PROGRAM = 0x18
    TEMPORARY_TONE = 0x19
    DRUM = 0x72
    EFFECTS_AREA = 0x16

    @classmethod
    def message_position(cls):
        """Return the fixed message position for command bytes."""
        return 8


@unique
class AddressOffsetTemporaryToneUMB(Address):
    DIGITAL_PART_1 = 0x01
    DIGITAL_PART_2 = 0x21
    ANALOG_PART = 0x42
    DRUM_KIT_PART = 0x70
    COMMON = 0x00

    @classmethod
    def message_position(cls):
        """Return the fixed message position for command bytes."""
        return 9


class AddressOffsetSystemUMB(Address):
    COMMON = 0x00

    @classmethod
    def message_position(cls):
        """Return the fixed message position for command bytes."""
        return 9


@unique
class AddressOffsetSystemLMB(Address):
    COMMON = 0x00
    CONTROLLER = 0x03

    @classmethod
    def message_position(cls):
        """Return the fixed message position for command bytes."""
        return 10


@unique
class AddressOffsetSuperNATURALLMB(Address):
    COMMON = 0x00
    PARTIAL_1 = 0x20
    PARTIAL_2 = 0x21
    PARTIAL_3 = 0x22
    TONE_MODIFY = 0x50

    @classmethod
    def message_position(cls):
        """Return the fixed message position for command bytes."""
        return 10


class AddressOffsetProgramLMB(Address):
    """Program"""

    COMMON = 0x00
    VOCAL_EFFECT = 0x01
    EFFECT_1 = 0x02
    EFFECT_2 = 0x04
    DELAY = 0x06
    REVERB = 0x08
    PART_DIGITAL_SYNTH_1 = 0x20
    PART_DIGITAL_SYNTH_2 = 0x21
    PART_ANALOG_SYNTH = 0x22
    PART_DRUM = 0x23
    ZONE_DIGITAL_SYNTH_1 = 0x30
    ZONE_DIGITAL_SYNTH_2 = 0x31
    ZONE_ANALOG_SYNTH = 0x32
    ZONE_DRUM = 0x33
    CONTROLLER = 0x40
    DRUM_DEFAULT_PARTIAL = DRUM_ADDRESS_MAP["BD1"]
    DIGITAL_DEFAULT_PARTIAL = DIGITAL_PARTIAL_MAP[1]
    DRUM_KIT_PART_1 = 0x2E
    DRUM_KIT_PART_2 = 0x30
    DRUM_KIT_PART_3 = 0x32
    DRUM_KIT_PART_4 = 0x34
    DRUM_KIT_PART_5 = 0x36
    DRUM_KIT_PART_6 = 0x38
    DRUM_KIT_PART_7 = 0x3A
    DRUM_KIT_PART_8 = 0x3C
    DRUM_KIT_PART_9 = 0x3E
    DRUM_KIT_PART_10 = 0x40
    DRUM_KIT_PART_11 = 0x42
    DRUM_KIT_PART_12 = 0x44
    DRUM_KIT_PART_13 = 0x46
    DRUM_KIT_PART_14 = 0x48
    DRUM_KIT_PART_15 = 0x4A
    DRUM_KIT_PART_16 = 0x4C
    DRUM_KIT_PART_17 = 0x4E
    DRUM_KIT_PART_18 = 0x50
    DRUM_KIT_PART_19 = 0x52
    DRUM_KIT_PART_20 = 0x54
    DRUM_KIT_PART_21 = 0x56
    DRUM_KIT_PART_22 = 0x58
    DRUM_KIT_PART_23 = 0x5A
    DRUM_KIT_PART_24 = 0x5C
    DRUM_KIT_PART_25 = 0x5E
    DRUM_KIT_PART_26 = 0x60
    DRUM_KIT_PART_27 = 0x62
    DRUM_KIT_PART_28 = 0x64
    DRUM_KIT_PART_29 = 0x66
    DRUM_KIT_PART_30 = 0x68
    DRUM_KIT_PART_31 = 0x6A
    DRUM_KIT_PART_32 = 0x6C
    DRUM_KIT_PART_33 = 0x6E
    DRUM_KIT_PART_34 = 0x70
    DRUM_KIT_PART_35 = 0x72
    DRUM_KIT_PART_36 = 0x74
    DRUM_KIT_PART_37 = 0x76

    @classmethod
    def message_position(cls):
        """Return the fixed message position for command bytes."""
        return 10


def address_to_hex_string(address: Tuple[int, int, int, int]) -> str:
    return " ".join(f"{b:02X}" for b in address)


def parse_sysex_address_json(
    address: Tuple[int, int, int, int], base_classes: Tuple[Type[Any], ...]
) -> Dict[str, Any]:
    """
    Parses a 4-byte SysEx address into a 4-level symbolic path as JSON.
    Supports both IntEnum subclasses and custom parameter classes with tuple values.
    """
    if len(address) != 4:
        return {}

    levels = []
    remaining = list(address)

    for i, byte in enumerate(remaining):
        match = find_matching_symbol(byte, base_classes)
        if match:
            levels.append(
                {"class": match["class"].__name__, "name": match["name"], "value": byte}
            )
            # Narrow down the next base_classes if it's a known nested type
            # (This can be customized to follow a known nested order)
        else:
            levels.append({"class": "Unknown", "name": f"0x{byte:02X}", "value": byte})

    return {f"level_{i + 1}": level for i, level in enumerate(levels)}


def find_matching_symbol(
    value: int, base_classes: Tuple[Type[Any], ...]
) -> Union[Dict[str, Any], None]:
    """
    Tries to find a matching member in any of the given base classes.
    Supports IntEnum and custom classes with tuple attributes.
    """
    for cls in base_classes:
        if issubclass(cls, IntEnum):
            for member in cls:
                if member.value == value:
                    return {"class": cls, "name": member.name}
        else:
            # Look for attributes that are (address, min, max) tuples
            for name, member in inspect.getmembers(cls):
                if not name.startswith("__") and isinstance(member, tuple):
                    if len(member) >= 1 and member[0] == value:
                        return {"class": cls, "name": name}
    return None


# 🧪 Test
if __name__ == "__main__":
    """
    from jdxi_editor.midi.data.address.address import (
        AddressMemoryAreaMSB,
        AddressOffsetTemporaryToneUMB,
        AddressOffsetProgramLMB,
        AddressOffsetSystemLMB,
        AddressOffsetSuperNATURALLMB,
    )
    """

    """

    test_address = (0x19, 0x01, 0x20, 0x00)
    from jdxi_editor.midi.data.parameter.digital.common import DigitalCommonParameter

    result = parse_sysex_address_json(
        test_address,
        (
            AddressMemoryAreaMSB,
            AddressOffsetTemporaryToneUMB,
            AddressOffsetSuperNATURALLMB,
            DigitalCommonParameter,
            AddressOffsetProgramLMB,
            AddressOffsetSystemLMB,
            AddressOffsetSuperNATURALLMB,
        ),
    )

    print(json.dumps(result, indent=2))"""


