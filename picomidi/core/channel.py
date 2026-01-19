"""
MIDI Channel Handling

This module provides utilities for working with MIDI channels.
MIDI channels are 1-based in user-facing APIs but 0-based internally.
"""

from enum import IntEnum


class Channel(IntEnum):
    """
    MIDI channels (0-based for internal use, matching MIDI protocol).

    Note: Display values are 1-based (CH1 = 1, CH2 = 2, etc.)
    but internal values are 0-based (CH1 = 0, CH2 = 1, etc.)
    """

    CH1 = 0
    CH2 = 1
    CH3 = 2
    CH4 = 3
    CH5 = 4
    CH6 = 5
    CH7 = 6
    CH8 = 7
    CH9 = 8
    CH10 = 9
    CH11 = 10
    CH12 = 11
    CH13 = 12
    CH14 = 13
    CH15 = 14
    CH16 = 15

    @classmethod
    def from_display(cls, channel: int) -> "Channel":
        """
        Convert 1-based display channel to 0-based Channel enum.

        :param channel: Display channel number (1-16)
        :return: Channel enum value
        :raises ValueError: If channel is not 1-16
        """
        if not 1 <= channel <= 16:
            raise ValueError(f"Channel must be 1-16, got {channel}")
        return cls(channel - 1)

    def to_display(self) -> int:
        """
        Convert to 1-based display channel number.

        :return: Display channel number (1-16)
        """
        return self.value + 1

    @classmethod
    def all(cls) -> list["Channel"]:
        """Get all 16 MIDI channels."""
        return list(cls)
