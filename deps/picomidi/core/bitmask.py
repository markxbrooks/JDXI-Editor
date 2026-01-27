"""
BitMask values
"""


class BitMask:
    """Bit masks for various purposes"""

    LOW_1_BIT = 0x01  # Mask for only the lowest (1st) bit
    LOW_2_BITS = 0x03  # Mask for lowest 2 bits (0b00000011)
    LOW_4_BITS = 0x0F  # Mask for lowest 4 bits (a nibble), e.g. for MIDI Channels
    LOW_7_BITS = 0x7F  # MIDI data byte mask (7-bit, valid for MIDI)
    FULL_BYTE = 0xFF  # Full 8 bits — masks a whole byte
    HIGH_4_BITS = 0xF0  # High nibble mask
    WORD = 0xFFFF  # Word mask (16 bits, 2 bytes)
