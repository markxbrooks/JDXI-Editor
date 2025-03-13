"""
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
"""

from enum import Enum


class SynthParameter(Enum):

    def __init__(self, address: int, min_val: int, max_val: int):
        self.address = address
        self.min_val = min_val
        self.max_val = max_val

    @property
    def display_name(self) -> str:
        """Get display name for the parameter"""
        return self.name.replace("_", " ").title()

    def validate_value(self, value: int) -> int:
        """Validate and convert parameter value to MIDI range (0-127)"""
        if not isinstance(value, int):
            raise ValueError(f"Value must be integer, got {type(value)}")

        if value < self.min_val or value > self.max_val:
            raise ValueError(
                f"Value {value} out of range for {self.name} "
                f"(valid range: {self.min_val}-{self.max_val})"
            )

        return value

    @staticmethod
    def get_name_by_address(address: int):
        """Return the parameter name for address given address."""
        for param in SynthParameter:
            if param.address == address:
                return param.name
        return None  # Return None if the address is not found

    @staticmethod
    def get_by_name(param_name):
        """Get the AnalogParameter by name."""
        # Return the parameter member by name, or None if not found
        return SynthParameter.__members__.get(param_name, None)

    def get_address_for_partial(self, partial_num: int = 0):
        pass # implemented in subclasses

    def convert_from_midi(self, midi_value):
        pass
