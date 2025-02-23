"""Digital synth MIDI constants"""

from enum import Enum, IntEnum
from .sysex import TEMPORARY_DIGITAL_SYNTH_1_AREA

# Areas and Parts
DIGITAL_SYNTH_AREA = TEMPORARY_DIGITAL_SYNTH_1_AREA  # For backwards compatibility
DIGITAL_PART_1 = 0x01
DIGITAL_PART_2 = 0x02
PART_1 = DIGITAL_PART_1  # For backwards compatibility
PART_2 = DIGITAL_PART_2  # For backwards compatibility

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

# Wave Types (for backwards compatibility)
WAVE_SAW = 0x00
WAVE_SQUARE = 0x01
WAVE_PULSE = 0x02
WAVE_TRIANGLE = 0x03
WAVE_SINE = 0x04
WAVE_NOISE = 0x05
WAVE_SUPER_SAW = 0x06
WAVE_PCM = 0x07

# SuperNATURAL Synth Parameters
OSC_WAVE_PARAM = 0x00          # Oscillator wave (0-7)
OSC_VARIATION_PARAM = 0x01     # Wave variation (0-2)
OSC_PITCH_PARAM = 0x03         # Pitch (40-88 = -24 to +24)
OSC_DETUNE_PARAM = 0x04        # Detune (14-114 = -50 to +50)
OSC_PWM_DEPTH_PARAM = 0x05     # PW Mod depth (0-127)
OSC_PW_PARAM = 0x06            # Pulse width (0-127)
OSC_PITCH_ENV_A_PARAM = 0x07   # Pitch env attack (0-127)
OSC_PITCH_ENV_D_PARAM = 0x08   # Pitch env decay (0-127)
OSC_PITCH_ENV_DEPTH_PARAM = 0x09  # Pitch env depth (1-127 = -63 to +63)

# Filter Parameters
FILTER_MODE_PARAM = 0x0A        # Filter mode (0-7)
FILTER_SLOPE_PARAM = 0x0B       # Filter slope (0-1)
FILTER_CUTOFF_PARAM = 0x0C      # Cutoff frequency (0-127)
FILTER_KEYFOLLOW_PARAM = 0x0D   # Cutoff keyfollow (54-74 = -100 to +100)
FILTER_ENV_VELO_PARAM = 0x0E    # Env velocity sens (1-127 = -63 to +63)
FILTER_RESONANCE_PARAM = 0x0F   # Resonance (0-127)
FILTER_ENV_A_PARAM = 0x10       # Env attack time (0-127)
FILTER_ENV_D_PARAM = 0x11       # Env decay time (0-127)
FILTER_ENV_S_PARAM = 0x12       # Env sustain level (0-127)
FILTER_ENV_R_PARAM = 0x13       # Env release time (0-127)
FILTER_ENV_DEPTH_PARAM = 0x14   # Env depth (1-127 = -63 to +63)

class DigitalToneCC(IntEnum):
    """Digital synth CC parameters"""
    # Partial Parameters
    PARTIAL_1_SWITCH = 0x19    # Partial 1 on/off (0-1)
    PARTIAL_1_SELECT = 0x1A    # Partial 1 select (0-1)
    PARTIAL_2_SWITCH = 0x1B    # Partial 2 on/off (0-1)
    PARTIAL_2_SELECT = 0x1C    # Partial 2 select (0-1)
    PARTIAL_3_SWITCH = 0x1D    # Partial 3 on/off (0-1)
    PARTIAL_3_SELECT = 0x1E    # Partial 3 select (0-1)
    RING_SWITCH = 0x1F         # Ring modulation (0=OFF, 1=---, 2=ON)

    # Oscillator Parameters (per partial)
    OSC_WAVE = 0x00          # Oscillator wave (0-7)
    OSC_VARIATION = 0x01     # Wave variation (0-2)
    OSC_PITCH = 0x03         # Pitch (40-88 = -24 to +24)
    OSC_DETUNE = 0x04        # Detune (14-114 = -50 to +50)
    OSC_PWM_DEPTH = 0x05     # PW Mod depth (0-127)
    OSC_PW = 0x06            # Pulse width (0-127)
    OSC_PITCH_ENV_A = 0x07   # Pitch env attack (0-127)
    OSC_PITCH_ENV_D = 0x08   # Pitch env decay (0-127)
    OSC_PITCH_ENV_DEPTH = 0x09  # Pitch env depth (1-127 = -63 to +63)

    # Filter Parameters
    FILTER_MODE = 0x0A        # Filter mode (0-7)
    FILTER_SLOPE = 0x0B       # Filter slope (0-1)
    FILTER_CUTOFF = 0x0C      # Cutoff frequency (0-127)
    FILTER_KEYFOLLOW = 0x0D   # Cutoff keyfollow (54-74 = -100 to +100)
    FILTER_ENV_VELO = 0x0E    # Env velocity sens (1-127 = -63 to +63)
    FILTER_RESONANCE = 0x0F   # Resonance (0-127)
    FILTER_ENV_A = 0x10       # Env attack time (0-127)
    FILTER_ENV_D = 0x11       # Env decay time (0-127)
    FILTER_ENV_S = 0x12       # Env sustain level (0-127)
    FILTER_ENV_R = 0x13       # Env release time (0-127)
    FILTER_ENV_DEPTH = 0x14   # Env depth (1-127 = -63 to +63)

    # Amplifier Parameters
    AMP_LEVEL = 0x15         # Amp level (0-127)
    AMP_VELO_SENS = 0x16     # Level velocity sens (1-127 = -63 to +63)
    AMP_ENV_A = 0x17         # Env attack time (0-127)
    AMP_ENV_D = 0x18         # Env decay time (0-127)
    AMP_ENV_S = 0x19         # Env sustain level (0-127)
    AMP_ENV_R = 0x1A         # Env release time (0-127)
    AMP_PAN = 0x1B           # Pan position (0-127 = L64-63R)

    # LFO Parameters
    LFO_SHAPE = 0x1C         # LFO shape (0-5)
    LFO_RATE = 0x1D          # Rate (0-127)
    LFO_TEMPO_SYNC = 0x1E    # Tempo sync switch (0-1)
    LFO_SYNC_NOTE = 0x1F     # Tempo sync note (0-19)
    LFO_FADE_TIME = 0x20     # Fade time (0-127)
    LFO_KEY_TRIGGER = 0x21   # Key trigger (0-1)
    LFO_PITCH_DEPTH = 0x22   # Pitch depth (1-127 = -63 to +63)
    LFO_FILTER_DEPTH = 0x23  # Filter depth (1-127 = -63 to +63)
    LFO_AMP_DEPTH = 0x24     # Amp depth (1-127 = -63 to +63)
    LFO_PAN_DEPTH = 0x25     # Pan depth (1-127 = -63 to +63)

    # Effects Send Parameters
    REVERB_SEND = 0x40       # Reverb send level (0-127)
    DELAY_SEND = 0x41        # Delay send level (0-127)
    EFFECTS_SEND = 0x42      # Effects send level (0-127)

    # Aftertouch Parameters
    CUTOFF_AFTERTOUCH = 0x30  # Cutoff aftertouch sensitivity (1-127 = -63 to +63)
    LEVEL_AFTERTOUCH = 0x31   # Level aftertouch sensitivity (1-127 = -63 to +63)

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