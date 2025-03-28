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
"""

from enum import Enum
from typing import Optional

from jdxi_editor.midi.data.constants.sysex import PROGRAM_GROUP


class SynthParameter(Enum):

    def __init__(self, address: int, min_val: int, max_val: int):
        self.address = address
        self.min_val = min_val
        self.max_val = max_val
        self.switches = []  # override in subclasses
        self.bipolar_parameters = []

    def __str__(self) -> str:
        return f"{self.name} (addr: {self.address:02X}, range: {self.min_val}-{self.max_val})"

    @property
    def is_switch(self) -> bool:
        """Returns True if parameter is address binary/enum switch"""
        return self.get_by_name(self.name) in self.switches
    
    @property
    def is_bipolar(self) -> bool:
        """Returns True if parameter is bipolar"""
        return self.get_by_name(self.name) in self.bipolar_parameters

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
        """
        :param partial_num: int
        :return: int default area
        to be subclassed
        """
        return PROGRAM_GROUP, 0x00

    def convert_from_midi(self, midi_value):
        pass
    
    def get_switch_text(self, value: int) -> str:
        """Get display text for switch values"""
        if self.is_switch:
            return "ON" if value else "OFF"
        return str(value)
    
    def get_nibbled_size(self) -> int:
        """Get the nibbled size for the parameter"""
        if self.max_val <= 127:
            return 1
        else:
            return 4  # dont know of any other sizes

    def convert_to_midi_test(self) -> int:
        """ convert to midi value"""
        return value

