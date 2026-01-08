"""
Base MIDI Message Class

This module provides the base class for all MIDI messages.
"""

from abc import ABC, abstractmethod
from typing import List


class Message(ABC):
    """
    Base class for all MIDI messages.

    All MIDI messages must implement methods to convert to bytes
    and to a list of integers for transmission.
    """

    @abstractmethod
    def to_bytes(self) -> bytes:
        """
        Convert message to bytes for transmission.

        :return: Bytes representation of the message
        """
        pass

    @abstractmethod
    def to_list(self) -> List[int]:
        """
        Convert message to list of integers.

        :return: List of byte values (0-255)
        """
        pass

    def to_hex_string(self, separator: str = " ") -> str:
        """
        Convert to hexadecimal string representation.

        :param separator: String to separate hex bytes
        :return: Hexadecimal string (e.g., "90 3C 7F")
        """
        return separator.join(f"{b:02X}" for b in self.to_list())

    def __repr__(self) -> str:
        """String representation of the message."""
        return f"{self.__class__.__name__}({self.to_hex_string()})"
