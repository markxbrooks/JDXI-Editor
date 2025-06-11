"""
Module: VocalFXParameter
========================

This module defines the VocalFXParameter class, which represents various vocal effects parameters
in a synthesizer. These parameters control different aspects of vocal processing, including
level, pan, delay/reverb send levels, auto pitch settings, vocoder effects, and more.

The class provides methods to:

- Initialize vocal FX parameters with a given address, range, and optional display range.
- Validate and convert parameter values to the MIDI range (0-127).
- Define a variety of vocal effects parameters with specific ranges, including:
  - Level, pan, delay/reverb send levels, and output assignment
  - Auto pitch settings such as switch, type, scale, key, note, gender, octave, and balance
  - Vocoder parameters such as switch, envelope type, level, mic sensitivity, and mix level

The class also offers conversion utilities:
- Convert between MIDI values and display values.
- Handle special bipolar cases (e.g., pan, auto pitch gender).
- Retrieve the display value range or MIDI value range for parameters.

Parameters include:
- Level, pan, delay and reverb send levels, output assignment, and auto pitch settings
- Vocoder settings for on/off, envelope, level, mic sensitivity, synth level, and mic mix
- Auto pitch gender, octave, balance, and key/note configurations

The class also includes utility functions to get a parameter's address, range, display range,
and to convert between MIDI values and display values.

Usage example:
    # Initialize a VocalFXParameter object for the LEVEL parameter
    param = VocalFXParameter(address=0x00, min_val=0, max_val=127)

    # Access display range values
    print(param.display_min)  # Output: 0
    print(param.display_max)  # Output: 127

    # Validate a MIDI value
    midi_value = param.convert_to_midi(64)
"""

from typing import Optional, Tuple

from jdxi_editor.midi.data.parameter.synth import AddressParameter


class AddressParameterVocalFX(AddressParameter):
    """Vocal FX parameters"""

    def __init__(
            self,
            address: int,
            min_val: int,
            max_val: int,
            display_min: Optional[int] = None,
            display_max: Optional[int] = None,
            tooltip: Optional[str] = None,
    ):
        super().__init__(address, min_val, max_val)
        self.display_min = display_min if display_min is not None else min_val
        self.display_max = display_max if display_max is not None else max_val
        self.tooltip = tooltip

    LEVEL = (0x00, 0, 127, 0, 127, "Sets the level of the vocal FX.")  # Level (0-127)
    PAN = (0x01, -64, 63, -64, 63, "Sets the pan of the vocal FX.")  # Pan (-64 to +63, centered at 64)
    DELAY_SEND_LEVEL = (0x02, 0, 127, 0, 127, "Sets the level of the delay send.")  # Delay send level (0-127)
    REVERB_SEND_LEVEL = (0x03, 0, 127, 0, 127, "Sets the level of the reverb send.")  # Reverb send level (0-127)
    OUTPUT_ASSIGN = (0x04, 0, 4, 0, 4, "Sets the output assignment.")  # Output assignment (0-4)
    AUTO_PITCH_SWITCH = (0x05, 0, 1, 0, 1, "Sets the auto note on/off.")  # Auto Note on/off (0-1)
    AUTO_PITCH_TYPE = (0x06, 0, 3, 0, 3, "Sets the auto pitch preset_type.")  # Auto Pitch preset_type (0-3)
    AUTO_PITCH_SCALE = (0x07, 0, 1, 0, 1, "Sets the auto pitch scale.")  # Scale CHROMATIC, Maj(Min)
    AUTO_PITCH_KEY = (
        0x08,
        0,
        23, 0, 23,
        "Sets the auto pitch key.")  # Auto Pitch key (0-23) C, Db, D, Eb, E, F, F#, G, Ab, A, Bb, B, Cm, C#m, Dm, D#m, Em, Fm, F#m, Gm, G#m, Am, Bbm, Bm
    AUTO_PITCH_NOTE = (0x09, 0, 11, 0, 11, "Sets the auto pitch note.")  # Auto Pitch note (0-11)
    AUTO_PITCH_GENDER = (0x0A, -10, 10, -10, 10, "Sets the auto pitch gender.")  # Gender (-10 to +10, centered at 0)
    AUTO_PITCH_OCTAVE = (0x0B, -1, 1, -1, 1, "Sets the auto pitch octave.")  # Octave (-1 to +1: 0-2)
    AUTO_PITCH_BALANCE = (0x0C, 0, 100, 0, 100, "Sets the auto pitch balance.")  # Dry/Wet Balance (0-100)
    VOCODER_SWITCH = (0x0D, 0, 1, 0, 1, "Sets the vocoder on/off.")  # Vocoder on/off (0-1)
    VOCODER_ENVELOPE = (
    0x0E, 0, 2, 0, 2, "Sets the vocoder envelope preset_type.")  # Vocoder envelope preset_type (0-2)
    VOCODER_LEVEL = (0x0F, 0, 127, 0, 127, "Sets the vocoder level.")  # Vocoder level (0-127)
    VOCODER_MIC_SENS = (0x10, 0, 127, 0, 127, "Sets the vocoder mic sensitivity.")  # Vocoder mic sensitivity (0-127)
    VOCODER_SYNTH_LEVEL = (0x11, 0, 127, 0, 127, "Sets the vocoder synth level.")  # Vocoder synth level (0-127)
    VOCODER_MIC_MIX = (0x12, 0, 127, 0, 127, "Sets the vocoder mic mix level.")  # Vocoder mic mix level (0-127)
    VOCODER_MIC_HPF = (0x13, 0, 13, 0, 13, "Sets the vocoder mic HPF freq.")  # Vocoder mic HPF freq (0-13)

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
    def get_name_by_address(address: int) -> Optional[str]:
        """Return the parameter name for address given address.
        :param address: int The address
        :return: Optional[str] The parameter name
        """
        for param in AddressParameterVocalFX:
            if param.address == address:
                return param.name
        return None  # Return None if the address is not found

    @property
    def display_name(self) -> str:
        """Get display name for the parameter"""
        return self.name.replace("_", " ").title()

    @property
    def is_switch(self) -> bool:
        """Returns True if parameter is address binary/enum switch"""
        return self in [
            self.AUTO_PITCH_SWITCH,
            self.VOCODER_SWITCH,
        ]

    @staticmethod
    def get_address(param_name: str) -> Optional[int]:
        """
        Get the address of address parameter by name.

        :param param_name: str The parameter name
        :return: Optional[int] The address
        """
        param = AddressParameterVocalFX.get_by_name(param_name)
        if param:
            return param.value[0]
        return None

    @staticmethod
    def get_range(param_name: str) -> Tuple[int, int]:
        """
        Get the value range (min, max) of address parameter by name.

        :param param_name: str The parameter name
        :return: Tuple[int, int] The value range
        """
        param = AddressParameterVocalFX.get_by_name(param_name)
        if param:
            return param.value[1], param.value[2]
        return None, None

    @staticmethod
    def get_display_range(param_name: str) -> Tuple[int, int]:
        """
        Get the display value range (min, max) of address parameter by name.

        :param param_name: str The parameter name
        :return: Tuple[int, int] The display value range
        """
        param = AddressParameterVocalFX.get_by_name(param_name)
        if param:
            return param.display_min, param.display_max
        return None, None

    def get_display_value(self) -> Tuple[int, int]:
        """
        Get the display value range (min, max) for the parameter

        :return: Tuple[int, int] The display value range
        """
        if hasattr(self, "display_min") and hasattr(self, "display_max"):
            return self.display_min, self.display_max
        return self.min_val, self.max_val

    def convert_from_display(self, display_value: int) -> int:
        """
        Convert from display value to MIDI value (0-127)

        :param display_value: int The display value
        :return: int The MIDI value
        """
        # Handle bipolar parameters
        if self in [
            self.AUTO_PITCH_GENDER,
            self.PAN,
            self.AUTO_PITCH_BALANCE,
        ]:
            return display_value + 64  # -63 to +63 -> 0 to 127
        else:
            return display_value  # -63 to +63 -> 0 to 126

    @staticmethod
    def convert_to_display(
            value: int, min_val: int, max_val: int, display_min: int, display_max: int
    ) -> int:
        """
        Convert address value to address display value within address range.

        :param value: int The address value
        :param min_val: int The address minimum value
        :param max_val: int The address maximum value
        :param display_min: int The display minimum value
        :param display_max: int The display maximum value
        :return: int The display value
        """
        return int(
            (value - min_val) * (display_max - display_min) / (max_val - min_val)
            + display_min
        )

    def convert_to_midi(self, display_value: int) -> int:
        """
        Convert from display value to MIDI value

        :param display_value: int The display value
        :return: int The MIDI value
        """
        # Handle special bipolar cases first
        if self == AddressParameterVocalFX.PAN:
            return display_value + 64  # -63 to +63 -> 0 to 127
        elif self == AddressParameterVocalFX.AUTO_PITCH_GENDER:
            return display_value + 10  # -63 to +63 -> 0 to 127

        # For parameters with simple linear scaling
        if hasattr(self, "display_min") and hasattr(self, "display_max"):
            return int(
                self.min_val
                + (display_value - self.display_min)
                * (self.max_val - self.min_val)
                / (self.display_max - self.display_min)
            )
        return display_value

    def convert_from_midi(self, midi_value: int) -> int:
        """
        Convert from MIDI value to display value

        :param midi_value: int The MIDI value
        :return: int The display value
        """
        # Handle special bipolar cases first
        if self == AddressParameterVocalFX.PAN:
            return midi_value - 64  # 0 to 127 -> -63 to +63
        elif self == AddressParameterVocalFX.AUTO_PITCH_GENDER:
            return midi_value - 10  # 0 to 127 -> -63 to +63

        # For parameters with simple linear scaling
        if hasattr(self, "display_min") and hasattr(self, "display_max"):
            return int(
                self.display_min
                + (midi_value - self.min_val)
                * (self.display_max - self.display_min)
                / (self.max_val - self.min_val)
            )
        return midi_value

    @staticmethod
    def get_display_value_by_name(param_name: str, value: int) -> int:
        """
        Get the display value for address parameter by name and value.

        :param param_name: str The parameter name
        :param value: int The value
        :return: int The display value
        """
        param = AddressParameterVocalFX.get_by_name(param_name)
        if param:
            return param.convert_from_midi(value)
        return value

    @staticmethod
    def get_midi_range(param_name: str) -> Tuple[int, int]:
        """
        Get the MIDI value range (min, max) of address parameter by name.

        :param param_name: str The parameter name
        :return: Tuple[int, int] The MIDI value range
        """
        param = AddressParameterVocalFX.get_by_name(param_name)
        if param:
            return param.min_value, param.max_value

    @staticmethod
    def get_midi_value(param_name: str, value: int) -> Optional[int]:
        """
        Get the MIDI value for address parameter by name and value.

        :param param_name: str The parameter name
        :param value: int The value
        :return: Optional[int] The MIDI value
        """
        param = AddressParameterVocalFX.get_by_name(param_name)
        if param:
            return param.convert_to_midi(value)
        return None
