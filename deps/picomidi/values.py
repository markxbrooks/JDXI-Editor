"""
Midi values classes
"""

class MinValues:
    """Minimum values"""

    SIGNED_SIXTEEN_BIT = 0x8000


class MaxValues:
    """Maximum unsigned constants for various bit-widths."""

    FOUR_BIT = 0x0F  # 15, 4-bit max (unsigned)
    SEVEN_BIT = 0x7F  # 127, 7-bit max (standard MIDI data byte)
    EIGHT_BIT = 0xFF  # 255, 8-bit max (unsigned)
    FOURTEEN_BIT = 0x3FFF  # 16383, 14-bit max (used in MIDI pitch bend)
    SIXTEEN_BIT = 0xFFFF  # 65535, unsigned 16-bit full range
    THIRTY_TWO_BIT = 0xFFFFFFFF  # 4294967295, max unsigned 32-bit
