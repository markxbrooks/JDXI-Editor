"""
AnalogParameter: JD-Xi Digital Synthesizer Parameter Mapping
============================================================

This class defines digital synthesizer parameters for the Roland JD-Xi, mapping
various synthesis parameters to their corresponding memory addresses and valid
value ranges.

The parameters include:
- Oscillator settings (waveform, pitch, detune, envelope, etc.)
- Filter settings (cutoff, resonance, envelope, key follow, etc.)
- Amplitude settings (level, velocity, envelope, pan, etc.)
- LFO (Low-Frequency Oscillator) settings (waveform, rate, depth, sync, etc.)
- Modulation LFO settings (waveform, rate, depth, sync, etc.)
- Additional synthesis controls (aftertouch, wave gain, super saw detune, etc.)
- PCM wave settings (wave number, gain, high-pass filter cutoff, etc.)

Each parameter is stored as address tuple containing:
    (memory_address, min_value, max_value)

Attributes:
    - OSC_WAVE: Defines the oscillator waveform preset_type.
    - FILTER_CUTOFF: Controls the filter cutoff frequency.
    - AMP_LEVEL: Sets the overall amplitude level.
    - LFO_RATE: Adjusts the rate of the low-frequency oscillator.
    - MOD_LFO_PITCH_DEPTH: Modulates pitch using the secondary LFO.
    - (Other parameters follow address similar structure.)

Methods:
    __init__(self, address: int, min_val: int, max_val: int):
        Initializes address DigitalParameter instance with an address and value range.

Usage Example:
    filter_cutoff = DigitalParameter(0x0C, 0, 127)  # Filter Cutoff Frequency
    log.message(filter_cutoff.address)  # Output: 0x0C

This class helps structure and manage parameter mappings for JD-Xi SysEx processing.
"""

from typing import Optional, Tuple

from jdxi_editor.midi.data.parameter.digital.mapping import ENVELOPE_MAPPING
from jdxi_editor.midi.data.parameter.synth import AddressParameter


class AddressParameterAnalog(AddressParameter):
    """Analog synth parameters with area, address, and value range."""

    TONE_NAME_1 = (0x00, 32, 127)
    TONE_NAME_2 = (0x01, 32, 127)
    TONE_NAME_3 = (0x02, 32, 127)
    TONE_NAME_4 = (0x03, 32, 127)
    TONE_NAME_5 = (0x04, 32, 127)
    TONE_NAME_6 = (0x05, 32, 127)
    TONE_NAME_7 = (0x06, 32, 127)
    TONE_NAME_8 = (0x07, 32, 127)
    TONE_NAME_9 = (0x08, 32, 127)
    TONE_NAME_10 = (0x09, 32, 127)
    TONE_NAME_11 = (0x0A, 32, 127)
    TONE_NAME_12 = (0x0B, 32, 127)

    # LFO Parameters
    LFO_SHAPE = (0x0D, 0, 5, 0, 5, "Selects the LFO waveform.\n0: SINE, 1: TRIANGLE, 2: SQUARE, 3: SAWTOOTH, 4: RANDOM, 5: SAMPLE_AND_HOLD")
    LFO_RATE = (0x0E, 0, 127, 0, 127, "Sets the LFO rate in Hz.\n0: 0.01 Hz, 127: 10 Hz")  # 0-127
    LFO_FADE_TIME = (0x0F, 0, 127, 0, 127, "Sets the fade time for the LFO.\n0: 0 ms, 127: 1000 ms")  # 0-127
    LFO_TEMPO_SYNC_SWITCH = (0x10, 0, 1, 0, 1, "Enables or disables tempo sync for the LFO.\n0: OFF, 1: ON")
    LFO_TEMPO_SYNC_NOTE = (0x11, 0, 19, 0, 19, "Sets the tempo sync note value for the LFO.\n0: 1/4, 1: 1/8, 2: 1/16, ..., 19: 1/128")
    LFO_PITCH_DEPTH = (0x12, 1, 127, -63, 63, "Specifies how much the LFO will modulate the pitch.\n-63: -63, 0: 0, 63: +63")  # -63 - +63
    LFO_FILTER_DEPTH = (0x13, 1, 127, -63, 63, "Specifies how much the LFO will modulate the filter cutoff.\n-63: -63, 0: 0, 63: +63")  # -63 - +63
    LFO_AMP_DEPTH = (0x14, 1, 127, -63, 63, "Specifies how much the LFO will modulate the amplitude.\n-63: -63, 0: 0, 63: +63")  # -63 - +63
    LFO_KEY_TRIGGER = (0x15, 0, 1, 0, 1, "Enables or disables key trigger for the LFO.\n0: OFF, 1: ON")

    # Oscillator Parameters
    OSC_WAVEFORM = (0x16, 0, 2, 0, 2, "Selects the waveform; SAW, TRI, PW-SQR")  # 0: SQUARE, 1: SAWTOOTH, 2: SUPER_SAW
    OSC_PITCH_COARSE = (0x17, 40, 88, -24, 24, "Adjusts the pitch in semitone steps")  # -24 - +24
    OSC_PITCH_FINE = (0x18, 14, 114, -50, 50, "Adjusts the pitch in steps of one cent")  # -50 - +50

    # OSC_PITCH = (0x03, 40, 88)
    # OSC_DETUNE = (0x04, 14, 114)
    OSC_PULSE_WIDTH = (0x19, 0, 127, 0, 127, "Sets the pulse width of the square wave oscillator.\n0: 0%, 127: 100%")  # 0-127
    OSC_PULSE_WIDTH_MOD_DEPTH = (0x1A, 0, 127, 0, 127, "Sets the modulation depth for the pulse width.\n0: 0%, 127: 100%")  # 0-127
    OSC_PITCH_ENV_VELOCITY_SENSITIVITY = (0x1B, 1, 127, -63, 63, "Specifies how the pitch envelope depth will vary according to the strength with which you play the key")  # -63 - +63
    OSC_PITCH_ENV_ATTACK_TIME = (0x1C, 0, 127, 0, 127, "Attack time for pitch envelope")  # 0-127
    OSC_PITCH_ENV_DECAY_TIME = (0x1D, 0, 127, 0, 127, "Decay time for pitch envelope")  # 0-127
    OSC_PITCH_ENV_DEPTH = (0x1E, 1, 127, -63, 63, "Specifies how much the pitch envelope will affect the pitch")  # -63 - +63
    SUB_OSCILLATOR_TYPE = (0x1F, 0, 2, 0, 2, "Turns the sub-oscillator on/off.\nOFF: Sub-oscillator is off\nOCT-1: Turns on (mixes) a square wave one octave below.\nOCT-2: Turns on (mixes) a square wave two octaves below.")

    # Filter Parameters
    FILTER_MODE_SWITCH = (0x20, 0, 1, 0, 1, "Specifies whether to use the analog LPF or not use it (BYPASS).")  # BYPASS, LPF
    FILTER_CUTOFF = (0x21, 0, 127, 0, 127, "Specifies the cutoff frequency")  # 0-127
    FILTER_CUTOFF_KEYFOLLOW = (0x22, 54, 74, -100, 100, "Specifies how much the cutoff frequency will vary according to the key you play.\n-100: -100%, 0: 0%, 100: +100%")  # -100 - +100
    FILTER_RESONANCE = (0x23, 0, 127, 0, 127, "Specifies the resonance level of the filter.\n0: 0%, 127: 100%")  # 0-127
    FILTER_ENV_VELOCITY_SENSITIVITY = (0x24, 1, 127, -63, 63, "Specifies how the filter envelope depth will vary according to the strength with which you play the key.")  # -63 - +63
    FILTER_ENV_ATTACK_TIME = (0x25, 0, 127, 0, 127, "Attack time for filter envelope")  # 0-127
    FILTER_ENV_DECAY_TIME = (0x26, 0, 127, 0, 127, "Decay time for filter envelope")  # 0-127
    FILTER_ENV_SUSTAIN_LEVEL = (0x27, 0, 127, 0, 127, "Sustain level for filter envelope")  # 0-127
    FILTER_ENV_RELEASE_TIME = (0x28, 0, 127, 0, 127, "Release time for filter envelope")  # 0-127
    FILTER_ENV_DEPTH = (0x29, 1, 127, -63, 63, "Specifies the direction and depth to which the cutoff frequency will change.")  # -63 - +63

    # Amplitude Parameters
    AMP_LEVEL = (0x2A, 0, 127, 0, 127, "Sets the overall amplitude level.\n0: 0%, 127: 100%")  # 0-127
    AMP_LEVEL_KEYFOLLOW = (0x2B, 54, 74, -100, 100, "Specify this if you want to vary the volume according to the position of the key that you play.\nWith positive (“+”) settings the volume increases as you play upward from the C4 key (middle C);\n with negative (“-”) settings the volume decreases.\n\nHigher values will produce greater change")  # -100 - +100
    AMP_LEVEL_VELOCITY_SENSITIVITY = (0x2C, 1, 127, -63, 63, "Specifies how the volume will vary according to the strength with which you play the keyboard.")  # -63 - +63
    AMP_ENV_ATTACK_TIME = (0x2D, 0, 127, 0, 127, "Attack time for amplitude envelope")  # 0-127
    AMP_ENV_DECAY_TIME = (0x2E, 0, 127, 0, 127, "Decay time for amplitude envelope")  # 0-127
    AMP_ENV_SUSTAIN_LEVEL = (0x2F, 0, 127, 0, 127, "Sustain level for amplitude envelope")  # 0-127
    AMP_ENV_RELEASE_TIME = (0x30, 0, 127, 0, 127, "Release time for amplitude envelope")  # 0-127

    # Portamento and Other Parameters
    PORTAMENTO_SWITCH = (0x31, 0, 1, 0, 1, "Enables or disables portamento.\n0: OFF, 1: ON")
    PORTAMENTO_TIME = (0x32, 0, 127, 0, 127, "Sets the portamento time in milliseconds.\n0: 0 ms, 127: 1000 ms")  # 0-127
    LEGATO_SWITCH = (0x33, 0, 1, 0, 1, "Enables or disables legato mode.\n0: OFF, 1: ON")
    OCTAVE_SHIFT = (0x34, 61, 67, -3, 3, "Adjusts the octave shift.\n-3: -3 octaves, 0: 0 octaves, 3: +3 octaves")  # -3 - +3
    PITCH_BEND_UP = (0x35, 0, 24, 0, 24, "Sets the pitch bend range for upward bends.\n0: 0 semitones, 24: 2 octaves")  # 0-24
    PITCH_BEND_DOWN = (0x36, 0, 24, 0, 24, "Sets the pitch bend range for downward bends.\n0: 0 semitones, 24: 2 octaves")  # 0-24

    # LFO Modulation Control
    LFO_PITCH_MODULATION_CONTROL = (0x38, 1, 127, -63, 63, "Controls the modulation depth of the LFO on pitch.\n-63: -63, 0: 0, 63: +63")  # -63 - +63
    LFO_FILTER_MODULATION_CONTROL = (0x39, 1, 127, -63, 63, "Controls the modulation depth of the LFO on filter cutoff.\n-63: -63, 0: 0, 63: +63")  # -63 - +63
    LFO_AMP_MODULATION_CONTROL = (0x3A, 1, 127, -63, 63, "Controls the modulation depth of the LFO on amplitude.\n-63: -63, 0: 0, 63: +63")  # -63 - +63
    LFO_RATE_MODULATION_CONTROL = (0x3B, 1, 127, -63, 63, "Controls the modulation depth of the LFO rate.\n-63: -63, 0: 0, 63: +63")  # -63 - +63

    # Reserve
    # RESERVE_1 = (0x37, 0, 0)
    # RESERVE_2 = (0x3C, 0, 0)
    # RESERVE_3 = (0x3D, 0, 0)
    # RESERVE_4 = (0x3F, 0, 0)

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
        self.tooltip = tooltip if tooltip is not None else ""
        self.switches = [
            "FILTER_SWITCH",
            "PORTAMENTO_SWITCH",
            "LEGATO_SWITCH",
            "LFO_TEMPO_SYNC_SWITCH",
        ]
        self.bipolar_parameters = [
            "LFO_PITCH_DEPTH",
            "LFO_FILTER_DEPTH",
            "LFO_AMP_DEPTH",
            "FILTER_ENV_VELOCITY_SENSITIVITY",
            "AMP_LEVEL_VELOCITY_SENSITIVITY",
            "AMP_LEVEL_KEYFOLLOW",
            "OSC_PITCH_ENV_VELOCITY_SENSITIVITY",
            "OSC_PITCH_COARSE",
            "OSC_PITCH_FINE",
            "LFO_PITCH_MODULATION_CONTROL",
            "LFO_AMP_MODULATION_CONTROL",
            "LFO_FILTER_MODULATION_CONTROL",
            "LFO_RATE_MODULATION_CONTROL",
            "OSC_PITCH_ENV_DEPTH",
            "FILTER_ENV_DEPTH",
        ]

    def get_bipolar_parameters(self):
        return self.bipolar_parameters

    def validate_value(self, value: int) -> int:
        """Validate that the parameter value is within the allowed range."""
        if not isinstance(value, int):
            raise ValueError(f"Value must be an integer, got {type(value).__name__}")

        if not (self.min_val <= value <= self.max_val):
            raise ValueError(
                f"Value {value} out of range for {self.name} (valid range: {self.min_val}-{self.max_val})"
            )

        return value

    @staticmethod
    def get_by_name(param_name: str) -> Optional[object]:
        """
        Get the AnalogParameter by name.
        :param param_name: str The parameter name
        :return: Optional[object] The parameter
        """
        # Return the parameter member by name, or None if not found
        return AddressParameterAnalog.__members__.get(param_name, None)

    @staticmethod
    def get_name_by_address(address: int) -> Optional[str]:
        """
        Return the parameter name for address given address.
        :param address: int The address
        :return: Optional[str] The parameter name
        """
        for param in AddressParameterAnalog:
            if param.address == address:
                return param.name
        return None  # Return None if the address is not found

    @property
    def display_name(self) -> str:
        """Get display name for the parameter"""
        return self.name.replace("_", " ").title()

    @staticmethod
    def get_address(param_name: str) -> Optional[int]:
        """
        Get the address of address parameter by name.
        :param param_name: str The parameter name
        :return: Optional[int] The address
        """
        param = AddressParameterAnalog.get_by_name(param_name)
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
        param = AddressParameterAnalog.get_by_name(param_name)
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
        param = AddressParameterAnalog.get_by_name(param_name)
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

    def convert_to_midi(self, display_value: int) -> int:
        """
        Convert from display value to MIDI value
        :param display_value: int The display value
        :return: int The MIDI value
        """
        # Handle special bipolar cases first
        if self == AddressParameterAnalog.OSC_PITCH_FINE:
            return display_value + 64  # -63 to +63 -> 0 to 127
        elif self == AddressParameterAnalog.OSC_PITCH_COARSE:
            return display_value + 64  # -63 to +63 -> 0 to 127

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
        if self == AddressParameterAnalog.OSC_PITCH_FINE:
            return midi_value - 64  # 0 to 127 -> -63 to +63
        elif self == AddressParameterAnalog.OSC_PITCH_COARSE:
            return midi_value - 64  # 0 to 127 -> -63 to +63

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
        param = AddressParameterAnalog.get_by_name(param_name)
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
        param = AddressParameterAnalog.get_by_name(param_name)
        if param:
            return param.min_val, param.max_val

    @staticmethod
    def get_midi_value(param_name: str, value: int) -> Optional[int]:
        """
        Get the MIDI value for address parameter by name and value.
        :param param_name: str The parameter name
        :param value: int The value
        :return: Optional[int] The MIDI value
        """
        param = AddressParameterAnalog.get_by_name(param_name)
        if param:
            return param.convert_to_midi(value)
        return None

    def get_address_for_partial(self, partial_number: int = 0) -> Tuple[int, int]:
        """
        Get parameter area and address adjusted for partial number.
        :param partial_number: int The partial number
        :return: Tuple[int, int] The parameter area and address
        """
        group_map = {0: 0x00}
        group = group_map.get(
            partial_number, 0x00
        )  # Default to 0x20 if partial_name is not 1, 2, or 3
        return group, self.address

    def get_envelope_param_type(self):
        """
        Returns a envelope_param_type, if the parameter is part of an envelope,
        otherwise returns None.
        """
        return ENVELOPE_MAPPING.get(self.name)
