from dataclasses import dataclass
from enum import Enum


class EffectType(Enum):
    """Effect types available on JD-Xi"""
    THRU = 0x00
    DISTORTION = 0x01
    FUZZ = 0x02
    COMPRESSOR = 0x03
    BITCRUSHER = 0x04
    FLANGER = 0x05
    PHASER = 0x06
    RING_MOD = 0x07
    SLICER = 0x08


class EffectsCommonParameter(Enum):
    """Common parameters for Effects."""
    PROGRAM_EFFECT_1 = 0x02
    PROGRAM_EFFECT_2 = 0x04
    PROGRAM_DELAY = 0x06
    PROGRAM_REVERB = 0x08

    @property
    def address(self):
        return self.value  # Access Enum value correctly


class FX:
    """Effect parameter ranges and defaults"""
    RANGES = {
        # Common parameters
        'level': (0, 127),
        
        # Distortion parameters
        'dist_drive': (0, 127),
        'dist_tone': (0, 127),
        
        # Compressor parameters
        'comp_attack': (0, 127),
        'comp_release': (0, 127),
        'comp_threshold': (0, 127),
        'comp_ratio': (0, 127),
        
        # Bitcrusher parameters
        'bit_depth': (0, 127),
        'sample_rate': (0, 127),
        
        # Flanger parameters
        'flanger_rate': (0, 127),
        'flanger_depth': (0, 127),
        'flanger_feedback': (0, 127),
        
        # Phaser parameters
        'phaser_rate': (0, 127),
        'phaser_depth': (0, 127),
        'phaser_resonance': (0, 127),
        
        # Ring Modulator parameters
        'ring_freq': (0, 127),
        'ring_balance': (0, 127),
        
        # Slicer parameters
        'slicer_rate': (0, 127),
        'slicer_pattern': (0, 15)
    }
    
    DEFAULTS = {
        'level': 100,
        'dist_drive': 64,
        'dist_tone': 64,
        'comp_attack': 0,
        'comp_release': 50,
        'comp_threshold': 0,
        'comp_ratio': 0,
        'bit_depth': 127,
        'sample_rate': 127,
        'flanger_rate': 64,
        'flanger_depth': 64,
        'flanger_feedback': 64,
        'phaser_rate': 64,
        'phaser_depth': 64,
        'phaser_resonance': 64,
        'ring_freq': 64,
        'ring_balance': 64,
        'slicer_rate': 64,
        'slicer_pattern': 0
    }




@dataclass
class EffectPatch:
    """Effect patch data"""
    # Effect preset_type and common parameters
    type: EffectType = EffectType.THRU
    level: int = 100
    
    # Effect-specific parameters
    param1: int = 0
    param2: int = 0
    
    # Send levels
    reverb_send: int = 0
    delay_send: int = 0
    chorus_send: int = 0
    
    def validate_param(self, param: str, value: int) -> bool:
        """Validate parameter value is in range"""
        if param in FX.RANGES:
            min_val, max_val = FX.RANGES[param]
            return min_val <= value <= max_val
        return False 

@dataclass
class EffectParam:
    """Effect parameter definition"""
    name: str
    min_value: int = -20000
    max_value: int = 20000
    default: int = 0
    unit: str = ""

# EFX1 Parameters by preset_type
DISTORTION_PARAMS = [
    EffectParam("Drive", 0, 127, 64),
    EffectParam("Level", 0, 127, 100),
    EffectParam("Tone", -20000, 20000, 0, "Hz"),
]

FUZZ_PARAMS = [
    EffectParam("Drive", 0, 127, 64),
    EffectParam("Level", 0, 127, 100),
    EffectParam("Tone", -20000, 20000, 0, "Hz"),
]

COMPRESSOR_PARAMS = [
    EffectParam("Attack", 0, 127, 64, "ms"),
    EffectParam("Release", 0, 127, 64, "ms"),
    EffectParam("Threshold", -60, 0, -20, "dB"),
    EffectParam("Ratio", 1, 100, 4),
    EffectParam("Gain", -12, 12, 0, "dB"),
]

BITCRUSHER_PARAMS = [
    EffectParam("Bit Depth", 1, 16, 16, "bits"),
    EffectParam("Sample Rate", 1000, 48000, 48000, "Hz"),
    EffectParam("Drive", 0, 127, 64),
]

# EFX2 Parameters by preset_type
PHASER_PARAMS = [
    EffectParam("Rate", 0, 127, 64),
    EffectParam("Depth", 0, 127, 64),
    EffectParam("Manual", -20000, 20000, 0),
    EffectParam("Resonance", 0, 127, 64),
    EffectParam("Mix", 0, 100, 50, "%"),
]

FLANGER_PARAMS = [
    EffectParam("Rate", 0, 127, 64),
    EffectParam("Depth", 0, 127, 64),
    EffectParam("Manual", -20000, 20000, 0),
    EffectParam("Resonance", 0, 127, 64),
    EffectParam("Mix", 0, 100, 50, "%"),
]

DELAY_PARAMS = [
    EffectParam("Time", 1, 2000, 500, "ms"),
    EffectParam("Feedback", 0, 127, 64),
    EffectParam("High Damp", 0, 127, 64),
    EffectParam("Mix", 0, 100, 50, "%"),
]

CHORUS_PARAMS = [
    EffectParam("Rate", 0, 127, 64),
    EffectParam("Depth", 0, 127, 64),
    EffectParam("Pre-Delay", 0, 100, 0, "ms"),
    EffectParam("Mix", 0, 100, 50, "%"),
]

# Main Delay Parameters
MAIN_DELAY_PARAMS = [
    EffectParam("Time", 1, 2000, 500, "ms"),
    EffectParam("Feedback", 0, 127, 64),
    EffectParam("High Damp", 0, 127, 64),
    EffectParam("Low Damp", 0, 127, 64),
]

# Main Reverb Parameters
MAIN_REVERB_PARAMS = [
    EffectParam("Time", 0, 127, 64),
    EffectParam("Pre-Delay", 0, 100, 0, "ms"),
    EffectParam("High Damp", 0, 127, 64),
    EffectParam("Low Damp", 0, 127, 64),
    EffectParam("Density", 0, 127, 64),
]

# Parameter mappings
EFX1_PARAMS = {
    0: [],  # OFF
    1: DISTORTION_PARAMS,
    2: FUZZ_PARAMS,
    3: COMPRESSOR_PARAMS,
    4: BITCRUSHER_PARAMS,
}

EFX2_PARAMS = {
    0: [],  # OFF
    5: PHASER_PARAMS,
    6: FLANGER_PARAMS,
    7: DELAY_PARAMS,
    8: CHORUS_PARAMS,
} 