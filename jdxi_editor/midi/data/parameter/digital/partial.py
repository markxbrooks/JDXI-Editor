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


from typing import Tuple, Optional

from jdxi_editor.midi.data.parameter.digital.mapping import ENVELOPE_MAPPING
from jdxi_editor.midi.data.parameter.synth import AddressParameter



def map_range(value, in_min=-100, in_max=100, out_min=54, out_max=74):
    return int(out_min + (value - in_min) * (out_max - out_min) / (in_max - in_min))


class AddressParameterDigitalPartial(AddressParameter):
    """Digital synth parameters with their addresses and value ranges"""

    def __init__(
        self,
        address: int,
        min_val: int,
        max_val: int,
        display_min: Optional[int] = None,
        display_max: Optional[int] = None,
    ):
        super().__init__(address, min_val, max_val)
        self.display_min = display_min if display_min is not None else min_val
        self.display_max = display_max if display_max is not None else max_val
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
            "FILTER_ENV_ATTACK_TIME": 64,
            "FILTER_ENV_DECAY_TIME": 64,
            "FILTER_ENV_SUSTAIN_LEVEL": 64,
            "FILTER_ENV_RELEASE_TIME": 64,
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
    OSC_WAVE = (0x00, 0, 7)  # Waveform preset_type
    OSC_WAVE_VARIATION = (0x01, 0, 2)  # Wave variation
    OSC_PITCH = (0x03, -24, 24)  # Coarse tune
    OSC_DETUNE = (0x04, -50, 50)  # Fine tune (-50 to +50)
    OSC_PULSE_WIDTH_MOD_DEPTH = (0x05, 0, 127)  # PWM Depth
    OSC_PULSE_WIDTH = (0x06, 0, 127)  # Pulse Width
    OSC_PITCH_ENV_ATTACK_TIME = (0x07, 0, 127)  # Pitch Envelope Attack
    OSC_PITCH_ENV_DECAY_TIME = (0x08, 0, 127)  # Pitch Envelope Decay
    OSC_PITCH_ENV_DEPTH = (0x09, -63, 63)  # Pitch Envelope Depth (-63 to +63)

    FILTER_MODE_SWITCH = (0x0A, 0, 7)  # Filter mode
    FILTER_SLOPE = (0x0B, 0, 1)  # Filter slope
    FILTER_CUTOFF = (0x0C, 0, 127, 0, 127)  # Cutoff frequency
    FILTER_CUTOFF_KEYFOLLOW = (0x0D, 54, 74, -100, 100)  # Key follow
    FILTER_ENV_VELOCITY_SENSITIVITY = (0x0E, 1, 127, -63, 63)  # Velocity sensitivity
    FILTER_RESONANCE = (0x0F, 0, 127)  # Resonance
    FILTER_ENV_ATTACK_TIME = (0x10, 0, 127)  # Filter envelope attack
    FILTER_ENV_DECAY_TIME = (0x11, 0, 127)  # Filter envelope decay
    FILTER_ENV_SUSTAIN_LEVEL = (0x12, 0, 127)  # Filter envelope sustain
    FILTER_ENV_RELEASE_TIME = (0x13, 0, 127)  # Filter envelope release
    FILTER_ENV_DEPTH = (0x14, 1, 127, -63, 63)  # Filter envelope depth

    # Amplitude parameters
    AMP_LEVEL = (0x15, 0, 127)  # Amplitude level
    AMP_VELOCITY = (0x16, -63, 63)  # Velocity sensitivity
    AMP_ENV_ATTACK_TIME = (0x17, 0, 127)  # Amplitude envelope attack
    AMP_ENV_DECAY_TIME = (0x18, 0, 127)  # Amplitude envelope decay
    AMP_ENV_SUSTAIN_LEVEL = (0x19, 0, 127)  # Amplitude envelope sustain
    AMP_ENV_RELEASE_TIME = (0x1A, 0, 127)  # Amplitude envelope release
    AMP_PAN = (0x1B, 0, 127, -64, 63)  # Pan position
    AMP_LEVEL_KEYFOLLOW = (0x1C, 54, 74, -100, 100)  # Key follow (-100 to +100)

    # LFO parameters
    LFO_SHAPE = (0x1C, 0, 5)  # LFO waveform
    LFO_RATE = (0x1D, 0, 127)  # LFO rate
    LFO_TEMPO_SYNC_SWITCH = (0x1E, 0, 1)  # Tempo sync switch
    LFO_TEMPO_SYNC_NOTE = (0x1F, 0, 19)  # Tempo sync note
    LFO_FADE_TIME = (0x20, 0, 127)  # Fade time
    LFO_KEY_TRIGGER = (0x21, 0, 1)  # Key trigger
    LFO_PITCH_DEPTH = (0x22, 1, 127, -63, 63)  # Pitch mod depth
    LFO_FILTER_DEPTH = (0x23, 1, 127, -63, 63)  # Filter mod depth
    LFO_AMP_DEPTH = (0x24, 1, 127, -63, 63)  # Amp mod depth
    LFO_PAN_DEPTH = (0x25, 1, 127, -63, 63)  # Pan mod depth

    # Modulation LFO parameters
    MOD_LFO_SHAPE = (0x26, 0, 5)  # Mod LFO waveform
    MOD_LFO_RATE = (0x27, 0, 127)  # Mod LFO rate
    MOD_LFO_TEMPO_SYNC_SWITCH = (0x28, 0, 1)  # Tempo sync switch
    MOD_LFO_TEMPO_SYNC_NOTE = (0x29, 0, 19)  # Tempo sync note
    OSC_PULSE_WIDTH_SHIFT = (0x2A, 0, 127)  # OSC Pulse Width Shift
    # 2B is reserved
    MOD_LFO_PITCH_DEPTH = (0x2C, 1, 127, -63, 63)  # Pitch mod depth
    MOD_LFO_FILTER_DEPTH = (0x2D, 1, 127, -63, 63)  # Filter mod depth
    MOD_LFO_AMP_DEPTH = (0x2E, 1, 127, -63, 63)  # Amp mod depth
    MOD_LFO_PAN = (0x2F, 1, 127, -63, 63)  # Pan mod depth
    MOD_LFO_RATE_CTRL = (0x3B, 1, 127, -63, 63)  # Rate control

    # Additional parameters
    CUTOFF_AFTERTOUCH = (0x30, 1, 127, -63, 63)  # Cutoff aftertouch
    LEVEL_AFTERTOUCH = (0x31, 1, 127, -63, 63)  # Level aftertouch
    WAVE_GAIN = (0x34, 0, 3)  # Wave gain
    HPF_CUTOFF = (0x39, 0, 127)  # HPF cutoff
    SUPER_SAW_DETUNE = (0x3A, 0, 127)  # Super saw detune

    PCM_WAVE_GAIN = (0x34, 0, 3)
    PCM_WAVE_NUMBER = (0x35, 0, 16384)

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
        """Get parameter area and address adjusted for partial number."""
        group_map = {1: 0x20, 2: 0x21, 3: 0x22}
        group = group_map.get(
            partial_number, 0x20
        )  # Default to 0x20 if partial_name is not 1, 2, or 3
        return group, self.address

    @staticmethod
    def get_by_name(param_name):
        """Get the DigitalParameter by name."""
        # Return the parameter member by name, or None if not found
        return AddressParameterDigitalPartial.__members__.get(param_name, None)

    def convert_value(self, value: int, reverse: bool = False) -> int:
        """Converts value in both directions based on CONVERSION_OFFSETS"""
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
        """Convert from display value to MIDI value"""
        return self.convert_value(slider_value)

    def convert_from_midi(self, midi_value: int) -> int:
        """Convert from MIDI value to display value"""
        return self.convert_value(midi_value, reverse=True)

    def get_envelope_param_type(self):
        """
        Returns a envelope_param_type, if the parameter is part of an envelope,
        otherwise returns None.
        """
        return ENVELOPE_MAPPING.get(self.name)
