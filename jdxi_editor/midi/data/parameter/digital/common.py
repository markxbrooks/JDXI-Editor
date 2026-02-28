"""
Module: AddressParameterDigitalCommon

This module defines the AddressParameterDigitalCommon class, which represents common parameters
for Digital/SuperNATURAL synth tones. These parameters are shared across all partials and
define various synthesizer settings, such as tone name, tone level, performance parameters,
partial switches, and additional effects.

The class provides methods to:

- Retrieve a human-readable digital name for each parameter.
- Identify if a parameter is a switch (binary or enum).
- Get appropriate digital text for switch values.
- Validate and convert parameter values within their defined range.
- Retrieve the partial number (1-3) for partial-specific parameters.
- Get a parameter by its name.

Parameters include:
- Tone name parameters (12 ASCII characters)
- Tone level
- Performance parameters (e.g., Portamento switch, Mono switch)
- Partial switches (e.g., Partial 1 switch, Partial 2 switch)
- Additional effect parameters (e.g., Ring Mod, Unison, Analog Feel)

Usage example:
    # Initialize a parameter object
    param = AddressParameterDigitalCommon(address=0x00, min_val=0, max_val=127)

    # Get the digital name for the parameter
    print(param.display_name)

    # Validate and convert a value for the parameter
    valid_value = param.validate_value(64)

    # Get the switch text for a given value
    switch_text = param.get_switch_text(1)

"""

from typing import Optional

from picomidi.sysex.parameter.address import AddressParameter

from jdxi_editor.midi.data.address.address import JDXiSysExOffsetProgramLMB
from jdxi_editor.midi.data.address.address_map import address
from jdxi_editor.midi.parameter.spec import ParameterSpec


class DigitalCommonParam(AddressParameter):
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
        display_name: Optional[str] = None,
        options: Optional[list] = None,
        values: Optional[list] = None,
    ):
        """
        Initialize the digital common parameter with address and value range.

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
        self._display_name = display_name
        self.options = options
        self.values = values

    def get_tooltip(self) -> str:
        """Return tooltip string for UI. Base may return options list; we always return self.tooltip."""
        return self.tooltip if isinstance(self.tooltip, str) else ""

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
    TONE_LEVEL = ParameterSpec(
        0x0C, 0, 127, "Adjusts the overall volume of the tone", "Tone Level"
    )  # Overall tone level

    # Performance parameters
    PORTAMENTO_SWITCH = ParameterSpec(
        0x12,
        0,
        1,
        0,
        1,
        "Specifies whether the portamento effect will be applied (ON) or not applied (OFF)",
        "Portamento Switch",
    )  # Portamento Switch (OFF, ON)
    PORTAMENTO_TIME = ParameterSpec(
        0x13,
        0,
        127,
        description="Specifies the time taken for the pitch to change when playing portamento. Higher values \nlengthen the time over which the pitch will change to the next note.",
        display_name="Portamento Time",
    )  # Portamento Time (CC# 5)
    MONO_SWITCH = ParameterSpec(
        0x14,
        0,
        1,
        0,
        1,
        "Specifies whether notes will sound polyphonically (POLY) or monophonically (MONO)",
        "Mono Switch",
    )  # Mono Switch (OFF, ON)
    OCTAVE_SHIFT = ParameterSpec(
        0x15,
        61,
        67,
        61,
        67,
        "Specifies the octave of the tone",
        "Octave Shift",
        ["-3", "-2", "-1", "0", "+1", "+2", "+3"],
        [61, 62, 63, 64, 65, 66, 67],
    )  # Octave Shift (-3 to +3)
    PITCH_BEND_UP = ParameterSpec(
        0x16,
        0,
        24,
        0,
        24,
        "Specifies the amount of pitch change that occurs when the pitch bend/modulation lever is \nmoved all the way up.",
        "Pitch Bend Range Up",
    )  # Pitch Bend Range Up (semitones)
    PITCH_BEND_DOWN = ParameterSpec(
        0x17,
        0,
        24,
        0,
        24,
        "Specifies the amount of pitch change that occurs when the pitch bend/modulation lever is \nmoved all the way to the dowm.",
        "Pitch Bend Range Down",
    )  # Pitch Bend Range Down (semitones)

    # Partial switches
    PARTIAL1_SWITCH = ParameterSpec(
        0x19, 0, 1, 0, 24, "Partial 1 turn on (OFF, ON)", "Partial 1 Switch"
    )  # Partial 1 Switch (OFF, ON)
    PARTIAL1_SELECT = ParameterSpec(
        0x1A, 0, 1, 0, 1, "Partial 1 select and edit (OFF, ON)", "Partial 1 Select"
    )  # Partial 1 Select (OFF, ON)
    PARTIAL2_SWITCH = ParameterSpec(
        0x1B, 0, 1, 0, 24, "Partial 2 turn on (OFF, ON)", "Partial 2 Switch"
    )  # Partial 2 Switch (OFF, ON)
    PARTIAL2_SELECT = ParameterSpec(
        0x1C, 0, 1, 0, 1, "Partial 2 select and edit (OFF, ON)", "Partial 1 Select"
    )  # Partial 2 Select (OFF, ON)
    PARTIAL3_SWITCH = ParameterSpec(
        0x1D, 0, 1, 0, 1, "Partial 3 turn on (OFF, ON)", "Partial 3 Switch"
    )  # Partial 3 Switch (OFF, ON)
    PARTIAL3_SELECT = ParameterSpec(
        0x1E, 0, 1, "Partial 3 select and edit (OFF, ON)", "Partial 3 Select"
    )  # Partial 3 Select (OFF, ON)

    # Additional parameters
    RING_SWITCH = ParameterSpec(
        0x1F,
        0,
        2,
        0,
        2,
        "Turns ring modulator on/off. \nBy multiplying partial 1’s OSC and partial 2’s OSC, this creates a complex, metallic-sounding waveform like that of a bell. \nIf Ring Switch is turned on, the OSC Pulse Width Mod Depth, OSC Pulse Width, and SUPER SAW\nDetune of partial 1 and partial 2 cannot be used.\nIn addition, if an asymmetrical square wave is selected as the OSC waveform, the OSC variation\nwill be ignored, and there will be a slight difference in sound compared to the originally selected\n waveform (OFF, ON)",
        "Ring Switch",
    )  # OFF(0), ---(1), ON(2)
    UNISON_SWITCH = ParameterSpec(
        0x2E,
        0,
        1,
        0,
        21,
        "This layers a single sound.\nIf the Unison Switch is on, the number of notes layered on one key will change according to the\nnumber of keys you play.",
        "Unison Switch",
    )  # OFF, ON
    PORTAMENTO_MODE = ParameterSpec(
        0x31,
        0,
        1,
        0,
        1,
        "NORMAL: Portamento will always be applied.\nLEGATO: Portamento will be applied only when you play legato (i.e., when you press the next\nkey before releasing the previous key).",
        "Portamento Mode",
    )  # NORMAL, LEGATO
    LEGATO_SWITCH = ParameterSpec(
        0x32,
        0,
        1,
        0,
        1,
        "Specifies the time taken for the pitch to change when playing portamento. Higher values\nlengthen the time over which the pitch will change to the next note.",
        "Legato Switch",
    )  # OFF, ON
    ANALOG_FEEL = ParameterSpec(
        0x34,
        0,
        127,
        description="Use this to apply “1/f fluctuation,” a type of randomness or instability that is present in many\nnatural systems (such as a babbling brook or whispering breeze) and is perceived as pleasant by \nmany people.\nBy applying “1/f fluctuation” you can create the natural-sounding instability that is\ncharacteristic of an analog synthesizer.",
        display_name="Analog Feel",
    )  # Analog Feel amount
    WAVE_SHAPE = ParameterSpec(
        0x35,
        0,
        127,
        description="Partial 1 will be modulated by the pitch of partial 2. Higher values produce a greater effect.\nThis has no effect if the partial 1 waveform is PW-SQR or SP-SAW.",
        display_name="Wave Shape",
    )  # Wave Shape amount
    TONE_CATEGORY = ParameterSpec(
        0x36, 0, 127, 0, 127, "Selects the tone’s category." "Tone Category"
    )  # Tone Category
    UNISON_SIZE = ParameterSpec(
        0x3C,
        0,
        3,
        0,
        3,
        "Number of notes assigned to each key when the Unison Switch is on.\nkeys | notes\n1   | 8\n2   |4 notes\n3–4  |2 each\n5-8  | 1 each ",
        "Unison Size",
    )  # Unison voice count (2-5 voices)

    @property
    def display_name(self) -> str:
        """Get digital name for the parameter (from ParameterSpec or fallback)."""
        if getattr(self, "_display_name", None) is not None:
            return self._display_name
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
        """Get digital text for switch values"""
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
            raise ValueError(f"Value must be an integer, got {type(value)}")

        # Special cases mapping
        special_cases = {
            self.RING_SWITCH: lambda v: 2 if v == 1 else v  # Skip "---" value
        }

        # Apply special case transformation if applicable
        value = special_cases.get(self, lambda v: v)(value)

        # Regular range check
        if not (self.min_val <= value <= self.max_val):
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
        return DigitalCommonParam.__members__.get(param_name, None)

    def get_address_for_partial(self, partial_number: int = 0):
        return JDXiSysExOffsetProgramLMB.COMMON, 0x00
