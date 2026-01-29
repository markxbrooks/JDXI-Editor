"""
DigitalPartialParameter: JD-Xi Digital Synthesizer Parameter Mapping
====================================================================

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
    print(filter_cutoff.address)  # Output: 0x0C

This class helps structure and manage parameter mappings for JD-Xi SysEx processing.
"""

from typing import Optional, Tuple

from jdxi_editor.midi.data.parameter.digital.mapping import ENVELOPE_MAPPING
from jdxi_editor.midi.parameter.spec import ParameterSpec
from picomidi.sysex.parameter.address import AddressParameter
from picomidi.sysex.parameter.map import map_range


class DigitalPartialParam(AddressParameter):
    """Digital synth parameters with their addresses and value ranges"""

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
        self.tooltip = tooltip if tooltip is not None else None
        self.bipolar_parameters = [
            # Oscillator parameters
            "OSC_PITCH",
            "OSC_DETUNE",
            "OSC_PITCH_ENV_DEPTH",
            # Filter parameters
            "FILTER_CUTOFF_KEYFOLLOW",
            "FILTER_ENV_VELOCITY_SENSITIVITY",
            "FILTER_ENV_DEPTH",
            # Amplitude parameters
            "AMP_VELOCITY",
            "AMP_PAN",
            "AMP_LEVEL_KEYFOLLOW",
            # LFO parameters
            "LFO_PITCH_DEPTH",
            "LFO_FILTER_DEPTH",
            "LFO_AMP_DEPTH",
            "LFO_PAN_DEPTH",
            # Mod LFO parameters
            "MOD_LFO_PITCH_DEPTH",
            "MOD_LFO_FILTER_DEPTH",
            "MOD_LFO_AMP_DEPTH",
            "MOD_LFO_PAN",
            "MOD_LFO_RATE_CTRL",
            "CUTOFF_AFTERTOUCH",
            "LEVEL_AFTERTOUCH",
        ]
        # Centralized conversion offsets
        self.CONVERSION_OFFSETS = {
            "OSC_DETUNE": 64,
            "OSC_PITCH_ENV_DEPTH": 64,
            "AMP_PAN": 64,
            "FILTER_CUTOFF_KEYFOLLOW": "map_range",
            "AMP_LEVEL_KEYFOLLOW": "map_range",
            "OSC_PITCH": 64,
            "FILTER_ENV_VELOCITY_SENSITIVITY": 64,
            "FILTER_ENV_DEPTH": 64,
            "LFO_PITCH_DEPTH": 64,
            "LFO_FILTER_DEPTH": 64,
            "LFO_AMP_DEPTH": 64,
            "LFO_PAN_DEPTH": 64,
            "MOD_LFO_PITCH_DEPTH": 64,
            "MOD_LFO_FILTER_DEPTH": 64,
            "MOD_LFO_AMP_DEPTH": 64,
            "MOD_LFO_PAN": 64,
            "MOD_LFO_RATE_CTRL": 64,
            "CUTOFF_AFTERTOUCH": 64,
            "LEVEL_AFTERTOUCH": 64,
        }

    def get_display_value(self) -> Tuple[int, int]:
        """Get the display range for the parameter"""
        return self.display_min, self.display_max

    # Oscillator parameters
    OSC_WAVE = ParameterSpec(
        0x00,
        0,
        7,
        0,
        7,
        "Waveform of the Oscillator; Select from classic waveforms: SAW, SQR, TRI, SINE, NOISE, SUPER SAW or PCM. \nEach offers unique harmonic content for shaping tone and texture",
    )  # Waveform preset_type
    OSC_WAVE_VARIATION = ParameterSpec(
        0x01,
        0,
        2,
        0,
        2,
        "You can select variations of the currently selected WAVE",
    )  # Wave variation
    OSC_PITCH = ParameterSpec(
        0x03,
        -24,
        24,
        -24,
        24,
        "Adjusts the pitch in semitone steps",
    )  # Coarse tune
    OSC_DETUNE = ParameterSpec(
        0x04,
        -50,
        50,
        -50,
        50,
        "Adjusts the pitch in steps of one cent",
    )  # Fine tune (-50 to +50)
    OSC_PULSE_WIDTH_MOD_DEPTH = ParameterSpec(
        0x05,
        0,
        127,
        0,
        127,
        "Specifies the amount (depth) of LFO that is applied to PW (Pulse Width). \nIf the OSC Wave has selected (PW-SQR), you can use this slider to specify the amount of LFO modulation applied to PW (pulse width).",
    )  # PWM Depth
    OSC_PULSE_WIDTH = ParameterSpec(
        0x06,
        0,
        127,
        0,
        127,
        "Sets the pulse width when PW-SQR is selected. \nSmaller values narrow the waveform; higher values widen it, shaping the tone",
    )  # Pulse Width
    OSC_PITCH_ENV_ATTACK_TIME = ParameterSpec(
        0x07,
        0,
        127,
        0,
        127,
        "Specifies the attack time of the pitch envelope. \nThis specifies the time from the moment you press the key until the pitch reaches its highest (or lowest) point",
    )  # Pitch Envelope Attack
    OSC_PITCH_ENV_DECAY_TIME = ParameterSpec(
        0x08,
        0,
        127,
        0,
        127,
        "Specifies the decay time of the pitch envelope. \nThis specifies the time from the moment the pitch reaches its highest \n(or lowest) point until it returns to the pitch of the key you pressed",
    )  # Pitch Envelope Decay
    OSC_PITCH_ENV_DEPTH = ParameterSpec(
        0x09,
        -63,
        63,
        -63,
        63,
        "This specifies how much the pitch envelope will affect the pitch\nNegative values will invert the shape of the envelope",
    )  # Pitch Envelope Depth (-63 to +63)

    FILTER_MODE_SWITCH = ParameterSpec(
        0x0A,
        0,
        7,
        0,
        7,
        "Selects the type of filter; \nBYPASS, LPF1, LPF2, LPF3, LPF4, HPF, BPF, PKG",
    )  # Filter mode
    FILTER_SLOPE = ParameterSpec(
        0x0B,
        0,
        1,
        0,
        1,
        "Selects the slope (steepness) of the filter. -12, -24 [dB]",
    )  # Filter slope
    FILTER_CUTOFF = ParameterSpec(
        0x0C,
        0,
        127,
        0,
        127,
        "Specifies the cutoff frequency",
    )  # Cutoff frequency
    FILTER_CUTOFF_KEYFOLLOW = ParameterSpec(
        0x0D,
        54,
        74,
        -100,
        100,
        "Specifies how you can make the filter cutoff frequency, \nto vary according to the key you play",
    )  # Key follow
    FILTER_ENV_VELOCITY_SENSITIVITY = ParameterSpec(
        0x0E,
        1,
        127,
        -63,
        63,
        "Specifies how you can make the filter envelope depth vary, \naccording to the strength with which you play the key",
    )  # Velocity sensitivity
    FILTER_RESONANCE = ParameterSpec(
        0x0F,
        0,
        127,
        0,
        127,
        "Emphasizes the sound in the region of the filter cutoff frequency",
    )  # Resonance
    FILTER_ENV_ATTACK_TIME = ParameterSpec(
        0x10,
        0,
        127,
        0,
        127,
        "Specifies the time from the moment you press the key until\n the cutoff frequency reaches its highest (or lowest) point",
    )  # Filter envelope attack
    FILTER_ENV_DECAY_TIME = ParameterSpec(
        0x11,
        0,
        127,
        0,
        127,
        "Specifies the time from when the cutoff frequency reaches its\n highest (or lowest) point, until it decays to the sustain level",
    )  # Filter envelope decay
    FILTER_ENV_SUSTAIN_LEVEL = ParameterSpec(
        0x12,
        0,
        127,
        0,
        127,
        "Specifies the cutoff frequency that will be maintained\n from when the decay time has elapsed until you release the key",
    )  # Filter envelope sustain
    FILTER_ENV_RELEASE_TIME = ParameterSpec(
        0x13,
        0,
        127,
        0,
        127,
        "Specifies the time from when you release the key until\n the cutoff frequency reaches its minimum value",
    )  # Filter envelope release
    FILTER_ENV_DEPTH = ParameterSpec(
        0x14,
        1,
        127,
        -63,
        63,
        "Specifies the direction and depth to which the cutoff frequency will change",
    )  # Filter envelope depth

    # Amplitude parameters
    AMP_LEVEL = ParameterSpec(0x15, 0, 127, 0, 127, "Partial volume")  # Amplitude level
    AMP_VELOCITY = ParameterSpec(
        0x16,
        -63,
        63,
        -63,
        63,
        "Specifies how the volume will vary according to the strength with which you play the keyboard.",
    )  # Velocity sensitivity
    AMP_ENV_ATTACK_TIME = ParameterSpec(
        0x17,
        0,
        127,
        0,
        127,
        "Specifies the time from the \nmoment you press the key until \n the maximum volume is reached.",
    )  # Amplitude envelope attack
    AMP_ENV_DECAY_TIME = ParameterSpec(
        0x18,
        0,
        127,
        0,
        127,
        "Specifies the time from when the\nmaximum volume is reached, until\nit decays to the sustain level.",
    )  # Amplitude envelope decay
    AMP_ENV_SUSTAIN_LEVEL = ParameterSpec(
        0x19,
        0,
        127,
        0,
        127,
        "Specifies the volume level that\nwill be maintained from when\nthe attack and decay times have\nelapsed until you release the key",
    )  # Amplitude envelope sustain
    AMP_ENV_RELEASE_TIME = ParameterSpec(
        0x1A,
        0,
        127,
        0,
        127,
        "Specifies the time from when you\nrelease the key until the volume\nreaches its minimum value.",
    )  # Amplitude envelope release
    AMP_PAN = ParameterSpec(
        0x1B,
        0,
        127,
        -64,
        63,
        "Specifies the stereo position of the partial; Left-Right",
    )  # Pan position
    AMP_LEVEL_KEYFOLLOW = ParameterSpec(
        0x1C,
        54,
        74,
        -100,
        100,
        "Specify this if you want to vary the volume according to the position of the key that you play.\nWith positive (“+”) settings the volume increases as you play upward from the C4 key (middle C);\n with negative (“-”) settings the volume decreases.\nHigher values will produce greater change.",
    )  # Key follow (-100 to +100)

    # LFO parameters
    LFO_SHAPE = ParameterSpec(
        0x1C,
        0,
        5,
        0,
        5,
        "Selects the LFO waveform; Trangle, Sine, Sawtooth, Square, \nSample and Hold (The LFO value will change once each cycle.), Random wave",
    )  # LFO waveform
    LFO_RATE = ParameterSpec(
        0x1D,
        0,
        127,
        0,
        127,
        "Specifies the LFO rate when LFO Tempo Sync Sw is OFF",
    )  # LFO rate
    LFO_TEMPO_SYNC_SWITCH = ParameterSpec(
        0x1E,
        0,
        1,
        0,
        1,
        "If this is ON, the LFO rate can be specified as a note value relative to the tempo",
    )  # Tempo sync switch
    LFO_TEMPO_SYNC_NOTE = ParameterSpec(
        0x1F,
        0,
        19,
        0,
        19,
        "Specifies the LFO rate when LFO Tempo Sync Sw is ON. \n16, 12, 8, 4, 2, 1, 3/4,\n2/3, 1/2, 3/8, 1/3, 1/4,\n3/16, 1/6, 1/8, 3/32,\n1/12, 1/16, 1/24, 1/32",
    )  # Tempo sync note
    LFO_FADE_TIME = ParameterSpec(
        0x20,
        0,
        127,
        0,
        127,
        "Specifies the time from when the partial sounds until the LFO reaches its maximum amplitude",
    )  # Fade time
    LFO_KEY_TRIGGER = ParameterSpec(
        0x21,
        0,
        1,
        0,
        1,
        "If this is on, the LFO cycle will be restarted when you press a key",
    )  # Key trigger
    LFO_PITCH_DEPTH = ParameterSpec(
        0x22,
        1,
        127,
        -63,
        63,
        "Allows the LFO to modulate the pitch, producing a vibrato effect",
    )  # Pitch mod depth
    LFO_FILTER_DEPTH = ParameterSpec(
        0x23,
        1,
        127,
        -63,
        63,
        "Allows the LFO to modulate the FILTER CUTOFF (cutoff frequency), producing a wah effect",
    )  # Filter mod depth
    LFO_AMP_DEPTH = ParameterSpec(
        0x24,
        1,
        127,
        -63,
        63,
        "Allows the LFO to modulate the AMP LEVEL (volume), producing a tremolo effect",
    )  # Amp mod depth
    LFO_PAN_DEPTH = ParameterSpec(
        0x25,
        1,
        127,
        -63,
        63,
        "Allows the LFO to modulate the PAN (stereo position), producing an auto panning effect",
    )  # Pan mod depth

    # Modulation LFO parameters
    MOD_LFO_SHAPE = ParameterSpec(
        0x26,
        0,
        5,
        0,
        5,
        "Selects the MODULATION LFO waveform.\n Trangle, Sine, Sawtooth, Square, \nSample and Hold (The LFO value will change once each cycle.), Random wave. \nThere is an LFO that is always applied to the partial, \nand a MODULATION LFO for applying modulation with the modulation\ncontroller (CC01).",
    )  # Mod LFO waveform
    MOD_LFO_RATE = ParameterSpec(
        0x27,
        0,
        127,
        0,
        127,
        "Specifies the LFO rate when ModLFO TempoSyncSw is OFF.",
    )  # Mod LFO rate
    MOD_LFO_TEMPO_SYNC_SWITCH = ParameterSpec(
        0x28,
        0,
        1,
        0,
        1,
        "If this is ON, the LFO rate can be specified as a note value relative to the tempo",
    )  # Tempo sync switch
    MOD_LFO_TEMPO_SYNC_NOTE = ParameterSpec(
        0x29,
        0,
        19,
        0,
        19,
        "Specifies the LFO rate when ModLFO TempoSyncSw is ON",
    )  # Tempo sync note
    OSC_PULSE_WIDTH_SHIFT = ParameterSpec(
        0x2A,
        0,
        127,
        0,
        127,
        "Shifts the range of change. Normally, you can leave this at 127.\n * If the Ring Switch is on, this has no effect on partials 1 and 2.",
    )  # OSC Pulse Width Shift
    # 2B is reserved
    MOD_LFO_PITCH_DEPTH = ParameterSpec(
        0x2C,
        1,
        127,
        -63,
        63,
        "Allows the LFO to modulate the pitch, producing a vibrato effect.",
    )  # Pitch mod depth
    MOD_LFO_FILTER_DEPTH = ParameterSpec(
        0x2D,
        1,
        127,
        -63,
        63,
        "Allows the LFO to modulate the FILTER CUTOFF (cutoff frequency), producing a wah effect.",
    )  # Filter mod depth
    MOD_LFO_AMP_DEPTH = ParameterSpec(
        0x2E,
        1,
        127,
        -63,
        63,
        "Allows the LFO to modulate the AMP LEVEL (volume), producing a tremolo effect.",
    )  # Amp mod depth
    MOD_LFO_PAN = ParameterSpec(
        0x2F,
        1,
        127,
        -63,
        63,
        "Allows the LFO to modulate the pan (stereo position), producing an auto panning effect.",
    )  # Pan mod depth
    MOD_LFO_RATE_CTRL = ParameterSpec(
        0x3B,
        1,
        127,
        -63,
        63,
        "Make these settings if you want to change the Modulation LFO Rate when the modulation lever\nis operated.\n Specify a positive (“+”) setting if you want ModLFO Rate to become faster when you increase\nthe modulation controller (CC01) value; \nspecify a negative (“-”) setting if you want it to become slower.",
    )  # Rate control

    # Additional parameters
    CUTOFF_AFTERTOUCH = ParameterSpec(
        0x30,
        1,
        127,
        -63,
        63,
        "Specifies how aftertouch pressure will affect the cutoff frequency",
    )  # Cutoff aftertouch
    LEVEL_AFTERTOUCH = ParameterSpec(
        0x31,
        1,
        127,
        -63,
        63,
        "Specifies how aftertouch pressure affects the volume",
    )  # Level aftertouch
    HPF_CUTOFF = ParameterSpec(
        0x39,
        0,
        127,
        0,
        127,
        "Specifies the cutoff frequency of an independent -6 dB high-pass filter",
    )  # HPF cutoff
    SUPER_SAW_DETUNE = ParameterSpec(
        0x3A,
        0,
        127,
        0,
        127,
        "Specifies the amount of pitch difference between the seven sawtooth waves layered within a single oscillator.\n * Lower values will produce a more subtle detune effect, similar to a single sawtooth wave.\n* Higher values will increase the pitch difference",
    )  # Super saw detune

    PCM_WAVE_GAIN = ParameterSpec(
        0x34,
        0,
        3,
        0,
        3,
        "Sets the gain for PCM waveforms; 0dB, -6dB, +6dB, +12dB",
    )  # PCM Wave Gain
    PCM_WAVE_NUMBER = ParameterSpec(
        0x35,
        0,
        16384,
        0,
        16384,
        "Selects the PCM waveform; 0-16383 * This is valid only if PCM is selected for OSC Wave.",
    )  # PCM Wave Number

    @property
    def display_name(self) -> str:
        """Get display name for the parameter"""
        return {self.OSC_WAVE_VARIATION: "Variation"}.get(
            self, self.name.replace("_", " ").title()
        )

    def get_switch_text(self, value: int) -> str:
        """Get display text for switch values"""
        if self == self.OSC_WAVE_VARIATION:
            return ["A", "B", "C"][value]
        elif self == self.FILTER_MODE_SWITCH:
            return ["BYPASS", "LPF", "HPF", "BPF", "PKG", "LPF2", "LPF3", "LPF4"][value]
        elif self == self.FILTER_SLOPE:
            return ["-12dB", "-24dB"][value]
        elif self == self.MOD_LFO_SHAPE:
            return ["TRI", "SIN", "SAW", "SQR", "S&H", "RND"][value]
        elif self == self.MOD_LFO_TEMPO_SYNC_SWITCH:
            return "ON" if value else "OFF"
        elif self == self.LFO_SHAPE:
            return ["TRI", "SIN", "SAW", "SQR", "S&H", "RND"][value]
        elif self in [self.LFO_TEMPO_SYNC_SWITCH, self.LFO_KEY_TRIGGER]:
            return "ON" if value else "OFF"
        elif self == self.PCM_WAVE_GAIN:
            return f"{[-6, 0, 6, 12][value]:+d}dB"
        return str(value)

    def validate_value(self, value: int) -> int:
        """Validate and convert parameter value to MIDI range (0-127)."""
        if not isinstance(value, int):
            raise ValueError(f"Value must be an integer, got {type(value)}")

        conversion = self.CONVERSION_OFFSETS.get(self.name)

        if conversion == "map_range":
            value = map_range(
                value, -100, 100, 0, 127
            )  # Normalize -100 to 100 into 0 to 127
        elif isinstance(conversion, int):
            value += conversion  # Apply offset (e.g., +64 or -64)

        # Ensure value is within MIDI range
        value = max(0, min(127, value))

        return value

    def get_address_for_partial(self, partial_number: int) -> Tuple[int, int]:
        """
        Get parameter area and address adjusted for partial number.

        :param partial_number: int The partial number
        :return: Tuple[int, int] The (group, address) tuple
        """
        group_map = {1: 0x20, 2: 0x21, 3: 0x22}
        group = group_map.get(
            partial_number, 0x20
        )  # Default to 0x20 if partial_name is not 1, 2, or 3
        return group, self.address

    @staticmethod
    def get_by_name(param_name: str) -> Optional[object]:
        """
        Get the DigitalParameter by name.

        :param param_name: str The parameter name
        :return: Optional[AddressParameterDigitalPartial] The parameter
        Return the parameter member by name, or None if not found
        """
        return DigitalPartialParam.__members__.get(param_name, None)

    def convert_value(self, value: int, reverse: bool = False) -> int:
        """
        Converts value in both directions based on CONVERSION_OFFSETS

        :param value: int The value
        :param reverse: bool The reverse flag
        :return: int The converted value
        """
        if value is None:
            return
        conversion = self.CONVERSION_OFFSETS.get(self.name)

        if conversion == "map_range":
            return (
                map_range(value, 54, 74, -100, 100)
                if reverse
                else map_range(value, -100, 100, 54, 74)
            )

        if isinstance(conversion, int):
            return value - conversion if reverse else value + conversion

        return value  # Default case: return as is

    def convert_to_midi(self, slider_value: int) -> int:
        """
        Convert from display value to MIDI value

        :param slider_value: int The display value
        :return: int The MIDI value
        """
        return self.convert_value(slider_value)

    def convert_from_midi(self, midi_value: int) -> int:
        """
        Convert from MIDI value to display value

        :param midi_value: int The MIDI value
        :return: int The display value
        """
        return self.convert_value(midi_value, reverse=True)

    def get_envelope_param_type(self):
        """
        Returns a envelope_param_type, if the parameter is part of an envelope,
        otherwise returns None.

        :return: Optional[str] The envelope parameter type
        """
        return ENVELOPE_MAPPING.get(self.name)
