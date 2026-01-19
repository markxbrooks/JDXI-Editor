"""
sysex utils:
# Get full address for Temporary Drum Kit (Offset from TEMP_TONE_BASE)
base = JDXiMemoryAddress.TEMP_TONE_BASE
drum_offset = (0x10, 0x00, 0x00)
drum_address = base.offset(drum_offset)

# Build a DT1 message to write data to it
data = [0x01, 0x02, 0x03]
sysex_msg = JDxiSysExBuilder.build_dt1(drum_address, data)
"""

from enum import Enum
from typing import List, Tuple


class JDXiAddress(Enum):
    """Base Addresses (4-byte addresses)"""

    SETUP = (0x01, 0x00, 0x00, 0x00)
    SYSTEM = (0x02, 0x00, 0x00, 0x00)
    TEMP_PROGRAM = (0x18, 0x00, 0x00, 0x00)
    TEMP_TONE_BASE = (0x19, 0x00, 0x00, 0x00)

    TEMP_TONE_PART1 = (0x19, 0x00, 0x00, 0x00)
    TEMP_TONE_PART2 = (0x19, 0x20, 0x00, 0x00)
    TEMP_TONE_ANALOG = (0x19, 0x40, 0x00, 0x00)
    TEMP_TONE_DRUMS = (0x19, 0x60, 0x00, 0x00)

    PROGRAM = (0x18, 0x00, 0x00, 0x00)

    def offset(self, offset: Tuple[int, int, int]) -> Tuple[int, int, int, int]:
        base = self.value
        full = [base[0], base[1] + offset[0], base[2] + offset[1], base[3] + offset[2]]
        return tuple(full)


# Address Offsets for Sub-sections
SYSTEM_OFFSETS = {
    "common": (0x00, 0x00, 0x00),
    "controller": (0x00, 0x03, 0x00),
}

TEMP_TONE_OFFSETS = {
    "supernatural": (0x01, 0x00, 0x00),
    "analog": (0x02, 0x00, 0x00),
    "drums": (0x10, 0x00, 0x00),
}

PROGRAM_OFFSETS = {
    "common": (0x00, 0x00, 0x00),
    "vocal_effect": (0x00, 0x01, 0x00),
    "effect_1": (0x00, 0x02, 0x00),
    "effect_2": (0x00, 0x04, 0x00),
    "delay": (0x00, 0x06, 0x00),
    "reverb": (0x00, 0x08, 0x00),
    "part_digital1": (0x00, 0x20, 0x00),
    "part_digital2": (0x00, 0x21, 0x00),
    "part_analog": (0x00, 0x22, 0x00),
    "part_drums": (0x00, 0x23, 0x00),
    "zone_digital1": (0x00, 0x30, 0x00),
    "zone_digital2": (0x00, 0x31, 0x00),
    "zone_analog": (0x00, 0x32, 0x00),
    "zone_drums": (0x00, 0x33, 0x00),
    "controller": (0x00, 0x40, 0x00),
}


class JDxiSysExBuilder:
    """JDxiSysExBuilder"""

    MODEL_ID = [0x00, 0x00, 0x00, 0x0E]

    @staticmethod
    def build_dt1(address: Tuple[int, int, int, int], data: List[int]) -> List[int]:
        return [
            0xF0,
            0x41,
            0x10,
            0x00,
            0x00,
            0x00,
            0x0E,
            0x12,  # DT1 command
            *address,
            *data,
            0xF7,
        ]
