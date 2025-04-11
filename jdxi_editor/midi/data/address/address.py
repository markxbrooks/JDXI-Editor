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
from typing import Optional, Type, TypeVar, Union, Tuple
import inspect

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
PLACEHOLDER_BYTE = 0x00


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

        return (base, *offset_bytes)

    def to_sysex_address(self, offset: Union[int, Tuple[int, int, int]] = (0, 0, 0)) -> bytes:
        """
        Returns the full 4-byte address as a `bytes` object, suitable for SysEx messages.
        """
        return bytes(self.add_offset(offset))

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
    MODEL_ID_1 = 0x00  # Manufacturer ID extension
    MODEL_ID_2 = 0x00  # Device family code MSB
    MODEL_ID_3 = 0x00  # Device family code LSB
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
class MemoryAreaAddress(Address):
    SYSTEM = 0x01
    SETUP = 0x02
    PROGRAM = 0x18
    TEMPORARY_TONE = 0x19
    DRUM = 0x72
    EFFECTS_AREA = 0x16


@unique
class SystemAddressOffset(Address):
    COMMON = 0x00
    CONTROLLER = 0x03


@unique
class SuperNATURALAddressOffset(Address):
    COMMON = 0x00
    PARTIAL_1 = 0x20
    PARTIAL_2 = 0x21
    PARTIAL_3 = 0x22
    TONE_MODIFY = 0x50


@unique
class TemporaryToneAddressOffset(Address):
    DIGITAL_PART_1 = 0x01
    DIGITAL_PART_2 = 0x21
    ANALOG_PART = 0x42
    DRUM_KIT_PART = 0x70


@unique
class ProgramAddressOffset(Address):
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


@unique
class ProgramAddressGroup(Address):
    PROGRAM_COMMON = 0x00
    DRUM_DEFAULT_PARTIAL = DRUM_ADDRESS_MAP["BD1"]
    DIGITAL_DEFAULT_PARTIAL = DIGITAL_PARTIAL_MAP[1]


@unique
class DrumKitAddressOffset(IntEnum):
    """ Drum Kit """
    COMMON = 0x00
    PARTIAL_1 = 0x20
    PARTIAL_2 = 0x21
    PARTIAL_3 = 0x22
    TONE_MODIFY = 0x50


# Dynamically generate DRUM_KIT_PART_{1-72} = 0x2E to 0x76
drum_kit_partials = {f"DRUM_KIT_PART_{i}": 0x2E + (i - 1) for i in range(1, 73)}

# Merge generated drum kit parts into TonePartialParameter
for name, value in drum_kit_partials.items():
    setattr(DrumKitAddressOffset, name, value)


@unique
class UnknownToneAddress(Address):  # I'm not convinced these are real
    TONE_1_LEVEL = 0x10
    TONE_2_LEVEL = 0x11


def address_to_hex_string(address: Tuple[int, int, int, int]) -> str:
    return " ".join(f"{b:02X}" for b in address)


def parse_sysex_address(address: Tuple[int, int, int, int], base_classes: Tuple[Type[IntEnum], ...]) -> Optional[str]:
    """
    Parses a 4-byte SysEx address and returns the symbolic parameter name path if found.

    :param address: A 4-byte address tuple (A1, A2, A3, A4)
    :param base_classes: A tuple of base IntEnum classes (e.g., (JdxiMemoryArea, ProgramParameter, ...))
    :return: A string path like "JdxiMemoryArea.PROGRAM -> ProgramParameter.COMMON", or None
    """
    if len(address) != 4:
        return None

    for base_class in base_classes:
        for member in base_class:
            if isinstance(member.value, int) and address[0] == member.value:
                remaining = address[1:]
                nested_path = find_nested_parameter_path(remaining, base_class)
                if nested_path:
                    return f"{base_class.__name__}.{member.name} -> {nested_path}"
                else:
                    return f"{base_class.__name__}.{member.name}"

    return None


def find_nested_parameter_path(remaining_address: Tuple[int, int, int], parent_class: Type[IntEnum]) -> Optional[str]:
    """
    Searches for a matching nested class that corresponds to the remaining address bytes.

    :param remaining_address: Remaining 3 bytes of the address
    :param parent_class: The class to search related nested classes
    :return: Matching path string or None
    """
    for _, obj in inspect.getmembers(__import__(__name__)):
        if inspect.isclass(obj) and issubclass(obj, IntEnum) and obj is not parent_class:
            for member in obj:
                if isinstance(member.value, int):
                    # Compare against full 3-byte value
                    if member.value == int.from_bytes(remaining_address, "big"):
                        return f"{obj.__name__}.{member.name}"
    return None

if __name__ == "__main__":
    result = parse_sysex_address((0x19, 0x01, 0x20, 0x09), (MemoryAreaAddress, SystemAddressOffset, SuperNATURALAddressOffset, TemporaryToneAddressOffset, ProgramAddressOffset ))
    print(result)  # "MemoryAreaAddress.PROGRAM -> ProgramParameter.COMMON"