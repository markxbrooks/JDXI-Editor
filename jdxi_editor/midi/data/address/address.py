"""
Parameter Address Map

Example Usage:
--------------

>>> class AddressMemoryAreaMSB(Address):
...    PROGRAM = 0x18
...    TEMPORARY_TONE = 0x19
... # Add an offset to a base address
... addr_bytes = AddressMemoryAreaMSB.PROGRAM.add_offset((0x00, 0x20, 0x00))
... print(addr_bytes)  # (0x18, 0x00, 0x20, 0x00)
... # Get SysEx-ready address
... sysex_address = AddressMemoryAreaMSB.PROGRAM.to_sysex_address((0x00, 0x20, 0x00))
... print(sysex_address)  # b'\x18\x00\x20\x00'
... # Lookup
... found = AddressMemoryAreaMSB.get_parameter_by_address(0x19)
... print(found)  # ProgramAddress.TEMPORARY_TONE

SysExByte

Example usage:
--------------
>>> command = CommandID.DT1
... print(f"Command: {command}, Value: {command.value}, Message Position: {command.message_position}")
"""

from __future__ import annotations
from enum import unique, IntEnum
from typing import Optional, Type, Union, Tuple, Any, TypeVar, List

from jdxi_editor.jdxi.sysex.bitmask import BitMask
from jdxi_editor.midi.data.address.sysex import ZERO_BYTE
from jdxi_editor.midi.data.address.sysex_byte import SysExByte
from jdxi_editor.midi.data.parameter.drum.addresses import DRUM_ADDRESS_MAP

T = TypeVar("T", bound="Address")
DIGITAL_PARTIAL_MAP = {i: 0x1F + i for i in range(1, 4)}  # 1: 0x20, 2: 0x21, 3: 0x22


@unique
class RolandID(IntEnum):
    """Roland IDs"""

    ROLAND_ID = 0x41
    DEVICE_ID = 0x10


@unique
class ResponseID(IntEnum):
    """Midi responses"""

    ACK = 0x4F  # Acknowledge
    ERR = 0x4E  # Error


class Address(SysExByte):
    """
    Base class for Roland-style hierarchical memory address enums (e.g., 0x18, 0x19, etc.)
    Includes lookup, offset arithmetic, and SysEx-ready address formatting.
    """

    def add_offset(
        self, address_offset: Union[int, Tuple[int, ...]]
    ) -> tuple[int, Any]:
        """
        Returns the full 4-byte address by adding a 3-byte offset to the base address.
        The base address is assumed to be a single byte (e.g., 0x18).
        :param address_offset: Union[int, Tuple[int, int, int]] The address offset
        :return: tuple[int, Any] The full 4-byte address
        """
        base = self.value
        if isinstance(address_offset, int):
            offset_bytes = [
                (address_offset >> 16) & BitMask.FULL_BYTE,
                (address_offset >> 8) & BitMask.FULL_BYTE,
                address_offset & BitMask.FULL_BYTE,
            ]
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

        :param address_offset: Union[int, Tuple[int, int, int]] The address offset
        :return: bytes The full 4-byte address
        """
        return bytes(self.add_offset(address_offset))

    @classmethod
    def from_sysex_bytes(cls: Type[T], address: bytes) -> Optional[T]:
        """
        Create an Address object from a 4-byte SysEx address.

        :param address: bytes The 4-byte SysEx address
        :return: Optional[T] The Address object
        """
        if len(address) != 4:
            return None
        return cls.get_parameter_by_address(address[0])

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}.{self.name}: 0x{self.value:02X}>"

    def __str__(self) -> str:
        return f"{self.__class__.__name__}.{self.name}: 0x{self.value:02X}"


class RolandSysExAddress:
    """
    Represents a full 4-byte SysEx address (MSB, UMB, LMB, LSB), with support for
    address arithmetic, formatting, and conversion to/from SysEx message bytes.
    :param msb: int The MSB
    :param umb: int The UMB
    :param lmb: int The LMB
    :param lsb: int The LSB
    """

    def __init__(self, msb: int, umb: int, lmb: int, lsb: int):
        self.msb = msb
        self.umb = umb
        self.lmb = lmb
        self.lsb = lsb

    @classmethod
    def from_bytes(cls, b: bytes) -> Optional[RolandSysExAddress]:
        """
        Create a RolandSysExAddress object from a 4-byte bytes object.

        :param b: bytes The 4-byte bytes object
        :return: Optional[RolandSysExAddress] The RolandSysExAddress object
        """
        if len(b) != 4:
            return None
        return cls(*b)

    def to_list(self) -> List[int]:
        """
        Convert the RolandSysExAddress object to a list of integers.

        :return: List[int] The list of integers
        """
        return [self.msb, self.umb, self.lmb, self.lsb]

    def to_bytes(self) -> bytes:
        """
        Convert the RolandSysExAddress object to a 4-byte bytes object.

        :return: bytes The 4-byte bytes object
        """
        return bytes([self.msb, self.umb, self.lmb, self.lsb])

    def add_offset(
        self, offset: Union[int, tuple[int, int, int]]
    ) -> RolandSysExAddress:
        """
        Adds a 3-byte offset to the lower three bytes (UMB, LMB, LSB).
        MSB remains unchanged.
        :param offset: Union[int, tuple[int, int, int]] The offset
        :return: RolandSysExAddress The RolandSysExAddress object
        """
        if isinstance(offset, int):
            offset_bytes = [(offset >> 16) & 0x7F, (offset >> 8) & BitMask.LOW_7_BITS, offset & BitMask.LOW_7_BITS]
        elif isinstance(offset, tuple) and len(offset) == 3:
            offset_bytes = list(offset)
        else:
            raise ValueError("Offset must be an int or a 3-byte tuple")

        new_umb = (self.umb + offset_bytes[0]) & BitMask.LOW_7_BITS
        new_lmb = (self.lmb + offset_bytes[1]) & BitMask.LOW_7_BITS
        new_lsb = (self.lsb + offset_bytes[2]) & BitMask.LOW_7_BITS
        return RolandSysExAddress(self.msb, new_umb, new_lmb, new_lsb)

    def __repr__(self) -> str:
        """
        Return a string representation of the RolandSysExAddress object.

        :return: str The string representation
        """
        return (
            f"<{self.__class__.__name__}(msb=0x{int(self.msb):02X}, umb=0x{int(self.umb):02X}, "
            f"lmb=0x{int(self.lmb):02X}, lsb=0x{int(self.lsb):02X})>"
        )

    def __str__(self):
        """
        Return a string representation of the RolandSysExAddress object.

        :return: str The string representation
        """
        return f"0x{int(self.msb):02X} 0x{int(self.umb):02X} 0x{int(self.lmb):02X} 0x{int(self.lsb):02X}"

    def __eq__(self, other: object) -> bool:
        """
        Check if the RolandSysExAddress object is equal to another object.

        :param other: object The other object
        :return: bool True if the objects are equal, False otherwise
        """
        if not isinstance(other, RolandSysExAddress):
            return NotImplemented
        return self.to_bytes() == other.to_bytes()

    def __hash__(self) -> int:
        """
        Return the hash of the RolandSysExAddress object.

        :return: int The hash of the RolandSysExAddress object
        """
        return hash(self.to_bytes())

    def copy(self) -> RolandSysExAddress:
        return RolandSysExAddress(self.msb, self.umb, self.lsb, self.lsb)




# ==========================
# JD-Xi SysEx Header
# ==========================


class ModelID(Address):
    """
    Model ID
    """

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
    def message_position(cls) -> int:
        """Return the fixed message position for command bytes."""
        return 7


# ==========================
# Memory and Program Areas
# ==========================


@unique
class AddressStartMSB(Address):
    """
    Memory and Program Areas
    """

    SYSTEM = 0x01
    SETUP = 0x02
    TEMPORARY_PROGRAM = 0x18
    TEMPORARY_TONE = 0x19

    @classmethod
    def message_position(cls) -> int:
        """Return the fixed message position for command bytes."""
        return 8


@unique
class AddressOffsetTemporaryToneUMB(Address):
    """
    Address Offset Temporary Tone UMB
    """

    DIGITAL_SYNTH_1 = 0x01  # Avoiding "Part" because of Partials
    DIGITAL_SYNTH_2 = 0x21
    ANALOG_SYNTH = 0x42
    DRUM_KIT = 0x70
    COMMON = 0x00

    @classmethod
    def message_position(cls) -> int:
        """Return the fixed message position for command bytes."""
        return 9


class AddressOffsetSystemUMB(Address):
    """
    Address Offset System UMB
    """

    COMMON = 0x00

    @classmethod
    def message_position(cls) -> int:
        """Return the fixed message position for command bytes."""
        return 9


@unique
class AddressOffsetSystemLMB(Address):
    """
    Address Offset System LMB
    """

    COMMON = 0x00
    CONTROLLER = 0x03

    @classmethod
    def message_position(cls) -> int:
        """Return the fixed message position for command bytes."""
        return 10


@unique
class AddressOffsetSuperNATURALLMB(Address):
    """
    Address Offset SuperNATURAL LMB
    """

    COMMON = 0x00
    PARTIAL_1 = 0x20
    PARTIAL_2 = 0x21
    PARTIAL_3 = 0x22
    MODIFY = 0x50

    @classmethod
    def message_position(cls) -> int:
        """Return the fixed message position for command bytes."""
        return 10

    @classmethod
    def digital_partial_offset(cls, partial_number: int) -> int:
        """Return the LMB offset for the given drum partial (0–37)."""
        base_address = DIGITAL_PARTIAL_MAP.get(partial_number, 0x00)
        return base_address


class AddressOffsetAnalogLMB(Address):
    """
    Analog Synth Tone
    """
    COMMON = 0x00


class AddressOffsetProgramLMB(Address):
    """
    Address Offset Program LMB
    """

    COMMON = 0x00
    VOCAL_EFFECT = 0x01
    EFFECT_1 = 0x02
    EFFECT_2 = 0x04
    DELAY = 0x06
    REVERB = 0x08
    PART_DIGITAL_SYNTH_1 = 0x20
    PART_DIGITAL_SYNTH_2 = 0x21
    PART_ANALOG = 0x22
    PART_DRUM = 0x23
    ZONE_DIGITAL_SYNTH_1 = 0x30
    ZONE_DIGITAL_SYNTH_2 = 0x31
    ZONE_ANALOG = 0x32
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
        """
        Return the fixed message position for command bytes.

        :return: int The fixed message position
        """
        return 10

    @classmethod
    def drum_partial_offset(cls, partial_number: int) -> int:
        """
        Return the LMB offset for the given drum partial (0–37).

        :param partial_number: int The partial number
        :return: int The LMB offset
        """
        base_address = 0x00
        step = 0x2E
        return base_address + (step * partial_number)


class AddressOffsetDrumKitLMB(Address):
    """
    Address Offset Program LMB
    """

    COMMON = 0x00
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
    def message_position(cls) -> int:
        """
        Return the fixed message position for command bytes.

        :return: int The fixed message position
        """
        return 10

    @classmethod
    def drum_partial_offset(cls, partial_number: int) -> int:
        """
        Return the LMB offset for the given drum partial (0–37).

        :param partial_number: int The partial number
        :return: int The LMB offset
        """
        base_address = 0x00
        step = 0x2E
        return base_address + (step * partial_number)

