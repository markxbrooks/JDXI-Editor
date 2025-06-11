"""
ProgramZoneParameter
====================

Defines the ProgramZoneParameter class for managing common program-level
parameters in the JD-Xi synthesizer.

This class provides attributes and methods for handling program-wide settings,
such as program name, level, tempo, and vocal effects. It also includes
methods for retrieving display values, validating parameter values, and
handling partial-specific addressing.

Example usage:

# Create an instance for Program Level
program_level = ProgramCommonParameter(*ProgramCommonParameter.PROGRAM_LEVEL)

# Validate a value within range
validated_value = program_level.validate_value(100)

# Get the display name of a parameter
display_name = program_level.display_name  # "Program Level"

# Get display value range
display_range = program_level.get_display_value()  # (0, 127)

# Retrieve a parameter by name
param = ProgramCommonParameter.get_by_name("PROGRAM_TEMPO")
if param:
    print(param.name, param.min_val, param.max_val)

# Get switch text representation
switch_text = program_level.get_switch_text(1)  # "ON" or "---"
"""

from typing import Tuple, Optional

from jdxi_editor.midi.data.parameter.synth import AddressParameter


class AddressParameterProgramZone(AddressParameter):
    """Program Common parameters"""

    def __init__(
        self,
        address: int,
        min_val: Optional[int] = None,
        max_val: Optional[int] = None,
        display_min: Optional[int] = None,
        display_max: Optional[int] = None,
        partial_number: Optional[int] = 0,
    ):
        super().__init__(address, min_val, max_val)
        self.display_min = display_min if display_min is not None else min_val
        self.display_max = display_max if display_max is not None else max_val
        self.partial_number = partial_number

    ARPEGGIO_SWITCH = (0x03, 0, 1, 0, 1)  # Arpeggio OFF, ON
    ZONAL_OCTAVE_SHIFT = (0x19, 61, 67, -3, +3)  # Octave shift

    def get_display_value(self) -> Tuple[int, int]:
        """
        Get the display value range (min, max) for the parameter

        :return: Tuple[int, int] The display value range
        """
        if hasattr(self, "display_min") and hasattr(self, "display_max"):
            return self.display_min, self.display_max
        return self.min_val, self.max_val

    def get_address_for_partial(self, partial_number: int = 0) -> Tuple[int, int]:
        """
        Get parameter area and address adjusted for partial number.

        :param partial_number: int The partial number
        :return: Tuple[int, int] The parameter area and address
        """
        group_map = {0: 0x30, 1: 0x31, 2: 0x32, 3: 0x33}
        group = group_map.get(
            partial_number, 0x30
        )  # Default to 0x30 if partial_name is not 1, 2, or 3
        return group, self.address

    @property
    def is_switch(self) -> bool:
        """
        Returns True if parameter is address binary/enum switch

        :return: bool True if parameter is address binary/enum switch
        """
        return self in [self.ARPEGGIO_SWITCH]

    def get_switch_text(self, value: int) -> str:
        """
        Get display text for switch values

        :param value: int The value
        :return: str The display text
        """
        if self == self.ARPEGGIO_SWITCH:
            return ["OFF", "ON"][value]
        elif self.is_switch:
            return "ON" if value else "OFF"
        return str(value)

    def validate_value(self, value: int) -> int:
        """
        Validate and convert parameter value

        :param value: int The value
        :return: int The validated value
        """
        if not isinstance(value, int):
            raise ValueError(f"Value must be integer, got {type(value)}")

        # Regular range check
        if value < self.min_val or value > self.max_val:
            raise ValueError(
                f"Value {value} out of range for {self.name} "
                f"(valid range: {self.min_val}-{self.max_val})"
            )

        return value

    def set_partial_number(self, partial_number: int) -> Optional[int]:
        """
        Returns the partial number (1-4) if this is address partial parameter, None otherwise

        :param partial_number: int The partial number
        :return: Optional[int] The partial number
        """
        self.partial_number = partial_number

    def get_partial_number(self) -> Optional[int]:
        """
        Returns the partial number (1-4) if this is address partial parameter, None otherwise

        :return: Optional[int] The partial number
        """
        return self.partial_number

    @staticmethod
    def get_by_name(param_name: str) -> Optional[object]:
        """
        Get the Parameter by name.

        :param param_name: str The parameter name
        :return: Optional[object] The parameter
        Return the parameter member by name, or None if not found
        """
        return AddressParameterProgramZone.__members__.get(param_name, None)
