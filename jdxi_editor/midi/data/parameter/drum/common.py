"""
This module defines the `DrumCommonParameter` class, which represents
common parameters for drum tones in the JD-Xi synthesizer.

These parameters are shared across all partials within a drum kit
and include settings such as tone name, kit level, and various switches.

Classes:
    DrumCommonParameter(SynthParameter)
        Represents common drum parameters and provides methods
        for retrieving addresses, validating values, and formatting
        switch-based parameter values.
"""

from typing import Optional, Tuple

from picomidi.sysex.parameter.address import AddressParameter

from jdxi_editor.midi.parameter.spec import ParameterSpec


class DrumCommonParam(AddressParameter):
    """Common parameters for Digital/SuperNATURAL synth tones.
    These parameters are shared across all partials.
    """

    def __init__(
        self,
        address: int,
        min_val: int,
        max_val: int,
        display_min: Optional[int] = None,
        display_max: Optional[int] = None,
        description: Optional[str] = None,
    ):
        """
        Initialize the drum common parameter with address and value range.
        
        Accepts 6 arguments when unpacked from ParameterSpec tuple:
        (address, min_val, max_val, min_display, max_display, description)
        """
        super().__init__(address, min_val, max_val)
        self.address = address
        self.min_val = min_val
        self.max_val = max_val
        # Use description as tooltip if provided
        self.tooltip = description if description is not None else ""
        self.display_min = display_min if display_min is not None else min_val
        self.display_max = display_max if display_max is not None else max_val

    # Tone name parameters (12 ASCII characters)
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

    # Tone level
    KIT_LEVEL = ParameterSpec(
        0x0C,
        0,
        127,
        0,
        127,
        "Sets the volume of the drum kit.\nMEMO\nThe volume of each partial in the drum kit is specified by the TVA Level parameter (p. 24).\nThe volume of each waveform within a partial is set by the Wave Level parameter (p. 21).",
    )  # Overall tone level

    @property
    def display_name(self) -> str:
        """Get display name for the parameter"""
        address_to_name = {
            self.KIT_LEVEL[0]: "Kit level",
            # Add other mappings as needed
        }
        return address_to_name.get(self.address, self.name.replace("_", " ").title())

    def get_address_for_partial(self, partial_number: int = 0) -> Tuple[int, int]:
        """Get parameter area and address adjusted for partial number."""
        group_map = {0: 0x00}
        group = group_map.get(
            partial_number, 0x00
        )  # Default to 0x20 if partial_name is not 1, 2, or 3
        return group, 0x00

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
