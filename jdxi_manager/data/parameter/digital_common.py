from enum import Enum
from typing import Optional, Tuple

from jdxi_manager.data.parameter.synth import SynthParameter


def parse_digital_common_parameters(data: list) -> dict:
    """
    Parses JD-Xi tone parameters from SysEx data, including Oscillator, Filter, and Amplifier parameters.

    Args:
        data (bytes): SysEx message containing tone parameters.

    Returns:
        dict: Parsed parameters.
    """

    # Function to safely retrieve values from `data`
    def safe_get(index, default=0):
        tone_name_length = 12
        index = index + tone_name_length # shift the index by 12 to account for the tone name
        return data[index] if index < len(data) else default

    parameters = {}

    # Mapping DigitalParameter Enum members to their respective positions in SysEx data
    for param in DigitalCommonParameter:
        # Use the parameter's address from the enum and fetch the value from the data
        parameters[param.name] = safe_get(param.address)

    return parameters


class DigitalCommonParameter(SynthParameter):
    """Common parameters for Digital/SuperNATURAL synth tones.
    These parameters are shared across all partials.
    """

    def __init__(self, address: int, min_val: int, max_val: int):
        super().__init__(address, min_val, max_val)
        self.address = address
        self.min_val = min_val
        self.max_val = max_val

    # Tone name parameters (12 ASCII characters)
    TONE_NAME_1 = (0x00, 32, 127)  # ASCII character 1
    TONE_NAME_2 = (0x01, 32, 127)  # ASCII character 2
    TONE_NAME_3 = (0x02, 32, 127)  # ASCII character 3
    TONE_NAME_4 = (0x03, 32, 127)  # ASCII character 4
    TONE_NAME_5 = (0x04, 32, 127)  # ASCII character 5
    TONE_NAME_6 = (0x05, 32, 127)  # ASCII character 6
    TONE_NAME_7 = (0x06, 32, 127)  # ASCII character 7
    TONE_NAME_8 = (0x07, 32, 127)  # ASCII character 8
    TONE_NAME_9 = (0x08, 32, 127)  # ASCII character 9
    TONE_NAME_10 = (0x09, 32, 127)  # ASCII character 10
    TONE_NAME_11 = (0x0A, 32, 127)  # ASCII character 11
    TONE_NAME_12 = (0x0B, 32, 127)  # ASCII character 12

    # Tone level
    TONE_LEVEL = (0x0C, 0, 127)  # Overall tone level

    # Performance parameters
    PORTAMENTO_SWITCH = (0x12, 0, 1)  # Portamento Switch (OFF, ON)
    PORTAMENTO_TIME = (0x13, 0, 127)  # Portamento Time (CC# 5)
    MONO_SWITCH = (0x14, 0, 1)  # Mono Switch (OFF, ON)
    OCTAVE_SHIFT = (0x15, 61, 67)  # Octave Shift (-3 to +3)
    PITCH_BEND_UP = (0x16, 0, 24)  # Pitch Bend Range Up (semitones)
    PITCH_BEND_DOWN = (0x17, 0, 24)  # Pitch Bend Range Down (semitones)

    # Partial switches
    PARTIAL1_SWITCH = (0x19, 0, 1)  # Partial 1 Switch (OFF, ON)
    PARTIAL1_SELECT = (0x1A, 0, 1)  # Partial 1 Select (OFF, ON)
    PARTIAL2_SWITCH = (0x1B, 0, 1)  # Partial 2 Switch (OFF, ON)
    PARTIAL2_SELECT = (0x1C, 0, 1)  # Partial 2 Select (OFF, ON)
    PARTIAL3_SWITCH = (0x1D, 0, 1)  # Partial 3 Switch (OFF, ON)
    PARTIAL3_SELECT = (0x1E, 0, 1)  # Partial 3 Select (OFF, ON)

    # Additional parameters
    RING_SWITCH = (0x1F, 0, 2)  # OFF(0), ---(1), ON(2)
    UNISON_SWITCH = (0x2E, 0, 1)  # OFF, ON
    PORTAMENTO_MODE = (0x31, 0, 1)  # NORMAL, LEGATO
    LEGATO_SWITCH = (0x32, 0, 1)  # OFF, ON
    ANALOG_FEEL = (0x34, 0, 127)  # Analog Feel amount
    WAVE_SHAPE = (0x35, 0, 127)  # Wave Shape amount
    TONE_CATEGORY = (0x36, 0, 127)  # Tone Category
    UNISON_SIZE = (0x3C, 0, 3)  # Unison voice count (2-5 voices)

    @property
    def display_name(self) -> str:
        """Get display name for the parameter"""
        return {
            self.RING_SWITCH: "Ring Mod",
            self.UNISON_SWITCH: "Unison",
            self.PORTAMENTO_MODE: "Porto Mode",
            self.LEGATO_SWITCH: "Legato",
            self.ANALOG_FEEL: "Analog Feel",
            self.WAVE_SHAPE: "Wave Shape",
            self.TONE_CATEGORY: "Category",
            self.UNISON_SIZE: "Uni Size",
        }.get(self, self.name.replace("_", " ").title())

    def get_address_for_partial(self, partial_num: int = 0) -> Tuple[int, int]:
        """Get parameter group and address adjusted for partial number."""
        group_map = {0: 0x00}
        group = group_map.get(partial_num, 0x00)  # Default to 0x20 if partial_name is not 1, 2, or 3
        return group, self.address

    @property
    def is_switch(self) -> bool:
        """Returns True if parameter is address binary/enum switch"""
        return self in [
            self.PORTAMENTO_SWITCH,
            self.MONO_SWITCH,
            self.PARTIAL1_SWITCH,
            self.PARTIAL1_SELECT,
            self.PARTIAL2_SWITCH,
            self.PARTIAL2_SELECT,
            self.PARTIAL3_SWITCH,
            self.PARTIAL3_SELECT,
            self.RING_SWITCH,
            self.UNISON_SWITCH,
            self.PORTAMENTO_MODE,
            self.LEGATO_SWITCH,
        ]

    def get_switch_text(self, value: int) -> str:
        """Get display text for switch values"""
        if self == self.RING_SWITCH:
            return ["OFF", "---", "ON"][value]
        elif self == self.PORTAMENTO_MODE:
            return ["NORMAL", "LEGATO"][value]
        elif self == self.UNISON_SIZE:
            return f"{value + 2} VOICE"  # 0=2 voices, 1=3 voices, etc.
        elif self.is_switch:
            return "ON" if value else "OFF"
        return str(value)

    def validate_value(self, value: int) -> int:
        """Validate and convert parameter value"""
        if not isinstance(value, int):
            raise ValueError(f"Value must be integer, got {type(value)}")

        # Special handling for ring switch
        if self == self.RING_SWITCH and value == 1:
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
        partial_params = {
            self.PARTIAL1_SWITCH: 1,
            self.PARTIAL1_SELECT: 1,
            self.PARTIAL2_SWITCH: 2,
            self.PARTIAL2_SELECT: 2,
            self.PARTIAL3_SWITCH: 3,
            self.PARTIAL3_SELECT: 3,
        }
        return partial_params.get(self)

    @staticmethod
    def get_by_name(param_name):
        """Get the Parameter by name."""
        # Return the parameter member by name, or None if not found
        return DigitalCommonParameter.__members__.get(param_name, None)
