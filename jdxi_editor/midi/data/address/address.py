"""
Parameter Address Map

Usage example:
==============

class ProgramAddress(Address):
    COMMON = 0x18
    DIGITAL_1 = 0x19

# Add an offset to a base address
addr_bytes = ProgramAddress.COMMON.add_offset((0x00, 0x20, 0x00))
print(addr_bytes)  # (0x18, 0x00, 0x20, 0x00)

# Get SysEx-ready address
sysex_address = ProgramAddress.COMMON.to_sysex_address((0x00, 0x20, 0x00))
print(sysex_address)  # b'\x18\x00\x20\x00'

# Lookup
found = ProgramAddress.get_parameter_by_address(0x19)
print(found)  # ProgramAddress.DIGITAL_1
"""

from enum import IntEnum, unique
from typing import Optional, Type, TypeVar, Union, Tuple, Dict, Any
import inspect
import json

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


class Address(IntEnum):
    """
    Base class for Roland-style hierarchical memory address enums (e.g., 0x18, 0x19, etc.)
    Includes lookup, offset arithmetic, and SysEx-ready address formatting.
    """

    @classmethod
    def get_parameter_by_address(cls: Type[T], address: int) -> Optional[T]:
        return next((param for param in cls if param.value == address), None)

    def add_offset(self, offset: Union[int, Tuple[int, int, int]]) -> Tuple[int, int, int, int]:
        """
        Returns the full 4-byte address by adding a 3-byte offset to the base address.
        The base address is assumed to be a single byte (e.g., 0x18).
        """
        base = self.value
        if isinstance(offset, int):
            offset_bytes = [(offset >> 16) & 0xFF, (offset >> 8) & 0xFF, offset & 0xFF]
        elif isinstance(offset, tuple) and len(offset) == 3:
            offset_bytes = list(offset)
        else:
            raise ValueError("Offset must be an int or a 3-byte tuple")
        if any(b > 0x7F for b in offset_bytes):
            raise ValueError("SysEx address bytes must be 7-bit (0x00 to 0x7F)")
        return (base, *offset_bytes)

    def to_sysex_address(self, offset: Union[int, Tuple[int, int, int]] = (0, 0, 0)) -> bytes:
        """
        Returns the full 4-byte address as a `bytes` object, suitable for SysEx messages.
        """
        return bytes(self.add_offset(offset))

    @classmethod
    def from_sysex_bytes(cls: Type[T], address: bytes) -> Optional[T]:
        if len(address) != 4:
            return None
        return cls.get_parameter_by_address(address[0])

    def __repr__(self):
        return f"<{self.__class__.__name__}.{self.name}: 0x{self.value:02X}>"


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
class CommandID(IntEnum):
    """ Roland Commands """
    DT1 = 0x12  # Data Set 1
    RQ1 = 0x11  # Data Request 1


@unique
class ResponseID(IntEnum):
    """ midi responses """
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


@unique
class AddressOffsetTemporaryToneUMB(Address):
    DIGITAL_PART_1 = 0x01
    DIGITAL_PART_2 = 0x21
    ANALOG_PART = 0x42
    DRUM_KIT_PART = 0x70

    
@unique
class AddressOffsetSystemLMB(Address):
    COMMON = 0x00
    CONTROLLER = 0x03


@unique
class AddressOffsetSuperNATURALLMB(Address):
    COMMON = 0x00
    PARTIAL_1 = 0x20
    PARTIAL_2 = 0x21
    PARTIAL_3 = 0x22
    TONE_MODIFY = 0x50


class AddressOffsetProgramLMB(Address):
    """ Program """
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


# Dynamically generate DRUM_KIT_PART_{1-72} = 0x2E to 0x76
drum_kit_partials = {f"DRUM_KIT_PART_{i}": 0x2E + (i - 1) for i in range(1, 73)}

# Merge generated drum kit parts into AddressOffsetProgramLMB

for name, value in drum_kit_partials.items():
    setattr(AddressOffsetProgramLMB, name, value)


def address_to_hex_string(address: Tuple[int, int, int, int]) -> str:
    return " ".join(f"{b:02X}" for b in address)


def parse_sysex_address_json(
    address: Tuple[int, int, int, int],
    base_classes: Tuple[Type[Any], ...]
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
            levels.append({
                "class": match["class"].__name__,
                "name": match["name"],
                "value": byte
            })
            # Narrow down the next base_classes if it's a known nested type
            # (This can be customized to follow a known nested order)
        else:
            levels.append({
                "class": "Unknown",
                "name": f"0x{byte:02X}",
                "value": byte
            })

    return {f"level_{i + 1}": level for i, level in enumerate(levels)}


def find_matching_symbol(
    value: int,
    base_classes: Tuple[Type[Any], ...]
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
        )
    )

    print(json.dumps(result, indent=2))