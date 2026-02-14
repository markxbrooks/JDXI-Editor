"""
ProgramCommonParameter
======================
Defines the ProgramCommonParameter class for managing common program-level
parameters in the JD-Xi synthesizer.

This class provides attributes and methods for handling program-wide settings,
such as program name, level, tempo, and vocal effects. It also includes
methods for retrieving digital values, validating parameter values, and
handling partial-specific addressing.

Example usage:

# Create an instance for Program Level
program_level = ProgramCommonParameter(*ProgramCommonParameter.PROGRAM_LEVEL)

# Validate a value within range
validated_value = program_level.validate_value(100)

# Get the digital name of a parameter
display_name = program_level.display_name  # "Program Level"

# Get digital value range
display_range = program_level.get_display_value()  # (0, 127)

# Retrieve a parameter by name
param = ProgramCommonParameter.get_by_name("PROGRAM_TEMPO")
if param:
    print(param.name, param.min_val, param.max_val)

# Get switch text representation
switch_text = program_level.get_switch_text(1)  # "ON" or "---"
"""

from typing import Optional, Tuple

from picomidi.sysex.parameter.address import AddressParameter

from jdxi_editor.midi.parameter.spec import ParameterSpec


class SystemCommonParam(AddressParameter):
    """Program Common parameters"""

    def __init__(
        self,
        address: int,
        min_val: Optional[int] = None,
        max_val: Optional[int] = None,
        display_min: Optional[int] = None,
        display_max: Optional[int] = None,
        tooltip: Optional[str] = None,
        display_name: Optional[str] = None,
        options: Optional[list] = None,
        values: Optional[list] = None
    ):
        super().__init__(address, min_val, max_val)
        self.display_min = display_min if display_min is not None else min_val
        self.display_max = display_max if display_max is not None else max_val
        self.tooltip = tooltip if tooltip is not None else ""
        self._display_name = display_name

    MASTER_TUNE = ParameterSpec(
        0x00, 24, 2024, -100, 100, "Master Tune"
    )  # Program Level (0-127)
    MASTER_KEY_SHIFT = ParameterSpec(
        0x04,
        40,
        88,
        -24,
        24,
        "Volume of the program",
    )  # Program Level (0-127)
    MASTER_LEVEL = ParameterSpec(
        0x05,
        0,
        127,
        0,
        127,
        "Volume of the program",
    )  # Program Level (0-127)

    def get_display_value(self) -> Tuple[int, int]:
        """Get the digital value range (min, max) for the parameter"""
        if hasattr(self, "display_min") and hasattr(self, "display_max"):
            return self.display_min, self.display_max
        return self.min_val, self.max_val

    @property
    def display_name(self) -> str:
        """Get digital name for the parameter (from ParameterSpec or fallback)."""
        if getattr(self, "_display_name", None) is not None:
            return self._display_name
        return {
            self.MASTER_LEVEL: "Master Level",
        }.get(self, self.name.replace("_", " ").title())

    def get_address_for_partial(self, partial_number: int = 0) -> Tuple[int, int]:
        """
        Get parameter area and address adjusted for partial number.

        :param partial_number: int The partial number
        :return: Tuple[int, int] The address
        """
        group_map = {0: 0x00}
        group = group_map.get(
            partial_number, 0x00
        )  # Default to 0x20 if partial_name is not 1, 2, or 3
        return group, self.address

    @property
    def is_switch(self) -> bool:
        """Returns True if parameter is address binary/enum switch"""
        return self in []

    def get_switch_text(self, value: int) -> str:
        """Get digital text for switch values
        :param value: int The value
        :return: str The digital text
        """
        if self.is_switch:
            return "ON" if value else "OFF"
        return str(value)

    def validate_value(self, value: int) -> int:
        """Validate and convert parameter value
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

    def get_partial_number(self) -> Optional[int]:
        """Returns the partial number (1-3) if this is address partial parameter, None otherwise"""
        partial_params = {}
        """
        {
            self.PARTIAL1_SWITCH: 1,
            self.PARTIAL1_SELECT: 1,
            self.PARTIAL2_SWITCH: 2,
            self.PARTIAL2_SELECT: 2,
            self.PARTIAL3_SWITCH: 3,
            self.PARTIAL3_SELECT: 3,
        }
        """
        return partial_params.get(self)

    @staticmethod
    def get_by_name(param_name: str) -> Optional[object]:
        """Get the Parameter by name.
        :param param_name: str The parameter name
        :return: Optional[object] The parameter
        Return the parameter member by name, or None if not found
        """

        return ProgramCommonParam.__members__.get(param_name, None)


class ProgramCommonParam(AddressParameter):
    """Program Common parameters"""

    def __init__(
        self,
        address: int,
        min_val: Optional[int] = None,
        max_val: Optional[int] = None,
        display_min: Optional[int] = None,
        display_max: Optional[int] = None,
        tooltip: Optional[str] = None,
        display_name: Optional[str] = None,
    ):
        super().__init__(address, min_val, max_val)
        self.display_min = display_min if display_min is not None else min_val
        self.display_max = display_max if display_max is not None else max_val
        self.tooltip = tooltip if tooltip is not None else ""
        self._display_name = display_name

    # Program name parameters (12 ASCII characters)
    TONE_NAME_1 = ParameterSpec(0x00, 32, 127)  # ASCII character 1
    TONE_NAME_2 = ParameterSpec(0x01, 32, 127)  # ASCII character 2
    TONE_NAME_3 = ParameterSpec(0x02, 32, 127)  # ASCII character 3
    TONE_NAME_4 = ParameterSpec(0x03, 32, 127)  # ASCII character 4
    TONE_NAME_5 = ParameterSpec(0x04, 32, 127)  # ASCII character 5
    TONE_NAME_6 = ParameterSpec(0x05, 32, 127)  # ASCII character 6
    TONE_NAME_7 = ParameterSpec(0x06, 32, 127)  # ASCII character 7
    TONE_NAME_8 = ParameterSpec(0x07, 32, 127)  # ASCII character 8
    TONE_NAME_9 = ParameterSpec(0x08, 32, 127)  # ASCII character 9
    TONE_NAME_10 = ParameterSpec(0x09, 32, 127)  # ASCII character 10
    TONE_NAME_11 = ParameterSpec(0x0A, 32, 127)  # ASCII character 11
    TONE_NAME_12 = ParameterSpec(0x0B, 32, 127)  # ASCII character 12

    PROGRAM_LEVEL = ParameterSpec(
        0x10,
        0,
        127,
        0,
        127,
        "Volume of the program",
    )  # Program Level (0-127)
    PROGRAM_TEMPO = ParameterSpec(
        0x11,
        500,
        30000,
        500,
        30000,
        """Tempo of the program
The Tempo knob adjusts the setting in a range from 60 to 240.
If the SYSTEM parameter Sync Mode is set to SLAVE, only “MIDI” can be selected.
(Since the tempo is synchronized to an external device, it’s not possible to change the tempo
from the JD-Xi.)""",
    )  # Program Tempo (500-30000: 5.00-300.00 BPM)
    VOCAL_EFFECT = ParameterSpec(
        0x16,
        0,
        2,
        0,
        2,
    )  # Vocal Effect (0: OFF, 1: VOCODER, 2: AUTO-PITCH)
    VOCAL_EFFECT_NUMBER = ParameterSpec(
        0x1C, 0, 20, 0, 20
    )  # Vocal Effect Number (0-20: 1-21)
    VOCAL_EFFECT_PART = ParameterSpec(
        0x1D, 0, 1, 0, 1
    )  # Vocal Effect Part (0: Part 1, 1: Part 2)
    AUTO_NOTE_SWITCH = ParameterSpec(
        0x1E, 0, 1, 0, 1
    )  # Auto Note Switch (0: OFF, 1: ON)

    def get_display_value(self) -> Tuple[int, int]:
        """Get the digital value range (min, max) for the parameter"""
        if hasattr(self, "display_min") and hasattr(self, "display_max"):
            return self.display_min, self.display_max
        return self.min_val, self.max_val

    @property
    def display_name(self) -> str:
        """Get digital name for the parameter (from ParameterSpec or fallback)."""
        if getattr(self, "_display_name", None) is not None:
            return self._display_name
        return {
            self.AUTO_NOTE_SWITCH: "Auto Note",
        }.get(self, self.name.replace("_", " ").title())

    def get_address_for_partial(self, partial_number: int = 0) -> Tuple[int, int]:
        """
        Get parameter area and address adjusted for partial number.

        :param partial_number: int The partial number
        :return: Tuple[int, int] The address
        """
        group_map = {0: 0x00}
        group = group_map.get(
            partial_number, 0x00
        )  # Default to 0x20 if partial_name is not 1, 2, or 3
        return group, self.address

    @property
    def is_switch(self) -> bool:
        """Returns True if parameter is address binary/enum switch"""
        return self in []

    def get_switch_text(self, value: int) -> str:
        """Get digital text for switch values
        :param value: int The value
        :return: str The digital text
        """
        if self == self.AUTO_NOTE_SWITCH:
            return ["OFF", "---", "ON"][value]
        elif self.is_switch:
            return "ON" if value else "OFF"
        return str(value)

    def validate_value(self, value: int) -> int:
        """Validate and convert parameter value
        :param value: int The value
        :return: int The validated value
        """
        if not isinstance(value, int):
            raise ValueError(f"Value must be integer, got {type(value)}")

        # Special handling for ring switch
        if self == self.AUTO_NOTE_SWITCH and value == 1:
            # Skip over the "---" value
            value = 2

        # Regular range check
        if value < self.min_val or value > self.max_val:
            raise ValueError(
                f"Value {value} out of range for {self.name} "
                f"(valid range: {self.min_val}-{self.max_val})"
            )

        return value

    def get_partial_number(self) -> Optional[int]:
        """Returns the partial number (1-3) if this is address partial parameter, None otherwise"""
        partial_params = {}
        """
        {
            self.PARTIAL1_SWITCH: 1,
            self.PARTIAL1_SELECT: 1,
            self.PARTIAL2_SWITCH: 2,
            self.PARTIAL2_SELECT: 2,
            self.PARTIAL3_SWITCH: 3,
            self.PARTIAL3_SELECT: 3,
        }
        """
        return partial_params.get(self)

    @staticmethod
    def get_by_name(param_name: str) -> Optional[object]:
        """Get the Parameter by name.
        :param param_name: str The parameter name
        :return: Optional[object] The parameter
        Return the parameter member by name, or None if not found
        """

        return ProgramCommonParam.__members__.get(param_name, None)
