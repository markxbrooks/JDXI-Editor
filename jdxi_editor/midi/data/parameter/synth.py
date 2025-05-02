"""
SynthParameter Base Class
=========================
Module for representing and managing synthesizer parameters as enum values.

This module defines the `SynthParameter` enum, which models the various parameters
of address synthesizer with associated addresses and valid value ranges. It includes methods
for value validation, display name formatting, and lookups by address or name.

Classes:
    SynthParameter (Enum): Enum class representing synthesizer parameters with associated
                            addresses and valid value ranges. Provides methods for validating
                            parameter values, retrieving display names, and finding parameters
                            by their address or name.

Methods:
    display_name (property): Returns the display name of the parameter by formatting
                             the enum name with spaces and title casing.
    validate_value(value: int): Validates the provided value against the parameter's valid
                                range and returns the value if it is valid.
    get_name_by_address(address: int): Static method that returns the name of the parameter
                                       corresponding to address given address.
    get_by_name(param_name: str): Static method that returns the `SynthParameter` member
                                  corresponding to address given name.

# Example usage
value = 0x123
offset = create_offset(value)

print(offset)  # Output: (0x00, 0x01, 0x23)
"""

from enum import Enum
from typing import Optional, Tuple, T, Type


class AddressParameter(Enum):
    """
    Base class for synthesizer parameters with associated addresses and valid value ranges.
    """
    def __init__(self,
                 address: int,
                 min_val: int,
                 max_val: int):
        self.address = address
        self.min_val = min_val
        self.max_val = max_val
        self.switches = []  # override in subclasses
        self.bipolar_parameters = []

    def __str__(self) -> str:
        """
        Returns a string representation of the parameter.
        :return: str string representation
        """
        return f"{self.name} Address: 0x{self.address:02X}, Range: {self.min_val}-{self.max_val}"

    @classmethod
    def message_position(cls):
        """
        Returns the position of the message in the SysEx message.
        :return: int
        """
        return 11

    @classmethod
    def get_parameter_by_address(cls: Type[T], address: int) -> Optional[T]:
        """
        Get the parameter member by address.
        :param address: int
        :return: parameter member or None
        """
        return next((parameter for parameter in cls if parameter.sysex_address == address), None)

    @property
    def is_switch(self) -> bool:
        """
        Returns True if parameter is a switch (e.g. ON/OFF)
        :return: bool True if switch, False otherwise
        """
        return self.get_by_name(self.name) in self.switches

    @property
    def is_bipolar(self) -> bool:
        """
        Returns True if parameter is bipolar (e.g. -64 to +63)
        :return: bool True if bipolar, False otherwise
        """
        return self.name in getattr(self, "bipolar_parameters", [])

    @property
    def display_name(self) -> str:
        """
        Returns the display name of the parameter by formatting the enum name with spaces
        :return: str formatted display name
        """
        return self.name.replace("_", " ").title()

    def validate_value(self, value: int) -> int:
        """
        Validate the value against the parameter's valid range.
        :param value: int value to validate
        :return: int validated value
        """
        if not isinstance(value, int):
            raise ValueError(f"Value must be integer, got {type(value)}")

        if value < self.min_val or value > self.max_val:
            raise ValueError(
                f"Value {value} out of range for {self.name} "
                f"(valid range: {self.min_val}-{self.max_val})"
            )

        return value

    @staticmethod
    def get_name_by_address(address: int) -> Optional[str]:
        """
        Get the parameter name by address.
        :param address: int address of the parameter
        :return: str name of the parameter or None
        """
        for param in AddressParameter:
            if param.address == address:
                return param.name
        return None  # Return None if the address is not found

    @staticmethod
    def get_by_name(param_name: str) -> Optional[T]:
        """
        Get the parameter member by name.
        :param param_name: str name of the parameter
        :return: parameter member or None
        """
        # Return the parameter member by name, or None if not found
        return AddressParameter.__members__.get(param_name, None)

    def get_address_for_partial(self, partial_number: int = 0) -> Tuple[int, int]:
        """
        :param partial_number: int
        :return: int default area
        to be subclassed
        """
        return 0x00, 0x00

    def convert_to_midi(self, value: int) -> int:
        """
        Convert the value to MIDI range (0-127) for sending via MIDI.
        :param value: int value to convert
        :return: int MIDI value
        """
        if not isinstance(value, int):
            raise ValueError(f"Value must be an integer, got {type(value)}")

        if value < self.min_val or value > self.max_val:
            raise ValueError(
                f"Value {value} out of range for {self.name} (valid range: {self.min_val}-{self.max_val})"
            )

        if self.is_bipolar:
            # Map -max_val..+max_val to 0-127
            return int(((value - self.min_val) / (self.max_val - self.min_val)) * 127)

        return value

    def get_switch_text(self, value: int) -> str:
        """
        Get the text representation of the switch value.
        :param value: int value to convert
        :return: str text representation
        """
        if self.is_switch:
            return "ON" if value else "OFF"
        return str(value)

    def get_nibbled_size(self) -> int:
        """
        Get the nibbled size for the parameter

        :return: int size in nibbles
        """
        if self.max_val <= 127:
            return 1
        else:
            return 4  # I don't know of any other sizes
            
    def get_offset(self) -> tuple:
        """
        Return a 3-byte tuple representing the address offset (UMB, LMB, LSB)
        for use with Address.add_offset(). The upper middle byte (UMB) is fixed at 0x00.

        :return: tuple[int, int, int] A 3-byte offset.
        """
        value = self.address
        umb = 0x00  # Default Upper Middle Byte
        lmb = (value >> 8) & 0xFF  # Extract LMB
        lsb = value & 0xFF         # Extract LSB
        return umb, lmb, lsb

    @property
    def lsb(self) -> Optional[int]:
        """
        Return the least significant byte (LSB) of the address.
        :return: int LSB of the address
        """
        return self.address & 0xFF  # Extract LSB
