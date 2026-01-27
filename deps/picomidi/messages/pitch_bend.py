"""
Pitch Bend MIDI message constants.
"""


class PitchBend:
    """Pitch Bend MIDI message constants."""

    STATUS = 0xE0
    RANGE = 16383  # 14-bit maximum (0x3FFF)
    CENTER = 8192  # Center position of the pitch wheel (0x2000)
