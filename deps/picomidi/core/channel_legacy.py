"""
Legacy MIDI channel utility constants.

This module is kept for backward compatibility.
New code should use picomidi.core.channel.Channel instead.
"""

from picomidi.core.bitmask import BitMask


class MidiChannel:
    """Utility Constants"""

    BINARY_TO_DISPLAY = 1  # Convert 0-based to 1-based channel
    DISPLAY_TO_BINARY = -1  # Convert 1-based to 0-based channel
    MASK = BitMask.LOW_4_BITS  # Mask for extracting channel from status byte
    NUMBER = 16  # Standard MIDI has 16 channels (0-15 or 1-16)
