"""
Digital Synth MIDI Constants Module

This module defines MIDI constants, parameter groups, enumerations, and utility functions
for interacting with the JD-Xi's digital synthesizer engine via MIDI. It provides:

- MIDI parameter groups and mappings for digital synth sections
- Enumerations for oscillator waveforms, filter types, and filter slopes
- Value range constraints for filter, amplifier, and LFO parameters
- Utility functions for parameter validation

Constants:
----------
- `DIGITAL_SYNTH_1_AREA`, `DIGITAL_SYNTH_2_AREA` – MIDI addresses for digital synth sections
- `DIGITAL_PART_1` to `DIGITAL_PART_4` – Identifiers for digital synth parts
- Parameter groups (`OSC_1_GROUP`, `FILTER_GROUP`, `AMP_GROUP`, etc.)
- Filter, amplifier, and LFO value range mappings

Classes:
--------
- `Waveform` – Enumeration of digital oscillator waveforms
- `FilterMode` – Enumeration of digital filter types
- `FilterSlope` – Enumeration of filter slope options

Functions:
----------
- `validate_value(param: int, value: int) -> bool` – Validates parameter values against their expected ranges

This module facilitates MIDI communication with the JD-Xi's digital synth by providing structured
access to parameter values, ensuring accurate automation and control.

"""


from enum import Enum

from jdxi_editor.midi.data.constants.sysex import TEMPORARY_DIGITAL_SYNTH_1_AREA


DIGITAL_SYNTH_1_AREA = 0x19
DIGITAL_SYNTH_2_AREA = 0x1A

# Areas and Parts
DIGITAL_SYNTH_AREA = TEMPORARY_DIGITAL_SYNTH_1_AREA  # For backwards compatibility

DIGITAL_PART_1 = 0x01
DIGITAL_PART_2 = 0x02
DIGITAL_PART_3 = 0x03
DIGITAL_PART_4 = 0x04

PART_1 = DIGITAL_PART_1  # For backwards compatibility
PART_2 = DIGITAL_PART_2  # For backwards compatibility
PART_3 = DIGITAL_PART_3  # For backwards compatibility
PART_4 = DIGITAL_PART_4  # For backwards compatibility

# Parameter Groups
OSC_1_GROUP = 0x20      # Oscillator 1 parameters
OSC_2_GROUP = 0x21      # Oscillator 2 parameters
FILTER_GROUP = 0x22     # Filter parameters
AMP_GROUP = 0x23        # Amplifier parameters
LFO_1_GROUP = 0x24      # LFO 1 parameters
LFO_2_GROUP = 0x25      # LFO 2 parameters
EFFECTS_GROUP = 0x26    # Effects parameters

# Parameter Groups (alternative names)
OSC_PARAM_GROUP = OSC_1_GROUP  # For backwards compatibility
LFO_PARAM_GROUP = LFO_1_GROUP  # For backwards compatibility
ENV_PARAM_GROUP = 0x60         # Envelope parameters


class Waveform(Enum):
    """Digital oscillator waveform types"""
    SAW = 0x00
    SQUARE = 0x01
    PULSE = 0x02
    TRIANGLE = 0x03
    SINE = 0x04
    NOISE = 0x05
    SUPER_SAW = 0x06
    PCM = 0x07

    @property
    def display_name(self) -> str:
        """Get display name for waveform"""
        names = {
            0: "SAW",
            1: "SQR",
            2: "P.W",
            3: "TRI",
            4: "SINE",
            5: "NOISE",
            6: "S.SAW",
            7: "PCM"
        }
        return names.get(self.value, "???")

class FilterMode(Enum):
    """Filter mode types"""
    BYPASS = 0x00
    LPF = 0x01     # Low-pass filter
    HPF = 0x02     # High-pass filter
    BPF = 0x03     # Band-pass filter
    PKG = 0x04     # Peaking filter
    LPF2 = 0x05    # Low-pass filter 2
    LPF3 = 0x06    # Low-pass filter 3
    LPF4 = 0x07    # Low-pass filter 4

    @property
    def display_name(self) -> str:
        """Get display name for filter mode"""
        names = {
            0: "BYPASS",
            1: "LPF",
            2: "HPF",
            3: "BPF",
            4: "PKG",
            5: "LPF2",
            6: "LPF3",
            7: "LPF4"
        }
        return names.get(self.value, "???")

class FilterSlope(Enum):
    """Filter slope values"""
    DB_12 = 0x00  # -12 dB/octave
    DB_24 = 0x01  # -24 dB/octave

    @property
    def display_name(self) -> str:
        """Get display name for filter slope"""
        names = {
            0: "-12dB",
            1: "-24dB"
        }
        return names.get(self.value, "???")

# Parameter value ranges
FILTER_RANGES = {
    'cutoff': (0, 127),
    'resonance': (0, 127),
    'keyfollow': (-100, 100),  # Actual values: 54-74 mapped to -100 to +100
    'env_velocity': (-63, 63),  # Actual values: 1-127 mapped to -63 to +63
    'env_depth': (-63, 63)     # Actual values: 1-127 mapped to -63 to +63
}

AMP_RANGES = {
    'level': (0, 127),
    'velocity_sens': (-63, 63),  # Actual values: 1-127 mapped to -63 to +63
    'pan': (-64, 63)            # Actual values: 0-127 mapped to L64-63R
}

LFO_RANGES = {
    'rate': (0, 127),
    'fade_time': (0, 127),
    'pitch_depth': (-63, 63),   # Actual values: 1-127 mapped to -63 to +63
    'filter_depth': (-63, 63),  # Actual values: 1-127 mapped to -63 to +63
    'amp_depth': (-63, 63),     # Actual values: 1-127 mapped to -63 to +63
    'pan_depth': (-63, 63)      # Actual values: 1-127 mapped to -63 to +63
}

# Subgroups
SUBGROUP_ZERO = 0x00

def validate_value(param: int, value: int) -> bool:
    """Validate parameter value is within allowed range"""
    ranges = {
        # Tone name (0x00-0x0B): ASCII 32-127
        range(0x00, 0x0C): lambda v: 32 <= v <= 127,
        
        # Level: 0-127
        0x0C: lambda v: 0 <= v <= 127,
        
        # Switches: 0-1
        0x12: lambda v: v in (0, 1),  # Portamento
        0x14: lambda v: v in (0, 1),  # Mono
        
        # Portamento time: 0-127
        0x13: lambda v: 0 <= v <= 127,
        
        # Octave shift: 61-67 (-3 to +3)
        0x15: lambda v: 61 <= v <= 67,
        
        # Pitch bend ranges: 0-24
        0x16: lambda v: 0 <= v <= 24,
        0x17: lambda v: 0 <= v <= 24
    }
    
    # Find matching range
    for param_range, validator in ranges.items():
        if isinstance(param_range, range):
            if param in param_range:
                return validator(value)
        elif param == param_range:
            return validator(value)
            
    return True  # Allow other parameters to pass through