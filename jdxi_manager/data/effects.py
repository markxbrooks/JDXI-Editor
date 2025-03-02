from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, List

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


class EffectParameter(Enum):
    """Effect parameters with address and value range"""

    # EFX1 Parameters
    EFX1_TYPE = (0x00, 0, 4)
    EFX1_LEVEL = (0x01, 0, 127)
    EFX1_DELAY_SEND_LEVEL = (0x02, 0, 127)
    EFX1_REVERB_SEND_LEVEL = (0x03, 0, 127)
    EFX1_OUTPUT_ASSIGN = (0x04, 0, 1)
    EFX1_PARAM_1 = (0x11, 12768, 52768)
    EFX1_PARAM_2 = (0x15, 12768, 52768)

    # EFX2 Parameters
    EFX2_TYPE = (0x00, 0, 8)
    EFX2_LEVEL = (0x01, 0, 127)
    EFX2_DELAY_SEND_LEVEL = (0x02, 0, 127)
    EFX2_REVERB_SEND_LEVEL = (0x03, 0, 127)
    EFX2_PARAM_1 = (0x11, 12768, 52768)
    EFX2_PARAM_2 = (0x15, 12768, 52768)

    FLANGER_RATE = (0x00, 0, 8) # Fixme: These Flanger values are placeholders
    FLANGER_DEPTH = (0x00, 0, 8)
    FLANGER_FEEDBACK = (0x00, 0, 8)
    FLANGER_MANUAL = (0x00, 0, 8)
    FLANGER_BALANCE = (0x00, 0, 8)

    # Delay Parameters
    DELAY_TYPE = (0x00, 0, 1)  # Assuming 0 for SINGLE, 1 for PAN
    DELAY_TIME = (0x01, 0, 2600)
    DELAY_TAP_TIME = (0x02, 0, 100)
    DELAY_FEEDBACK = (0x03, 0, 98)
    DELAY_HF_DAMP = (0x04, 200, 8000)
    DELAY_LEVEL = (0x05, 0, 127)
    DELAY_REV_SEND_LEVEL = (0x06, 0, 127)

    # Reverb Parameters
    REVERB_OFF_ON = (0x00, 0, 1)
    REVERB_TYPE = (0x00, 0, 5)  # Assuming 0 for ROOM1, 1 for ROOM2, etc.
    REVERB_TIME = (0x01, 0, 127)
    REVERB_HF_DAMP = (0x02, 200, 8000)
    REVERB_LEVEL = (0x03, 0, 127)
    REVERB_PARAM_1 = (0x04, 12768, 52768)
    REVERB_PARAM_2 = (0x07, 12768, 52768)

    # Common parameters
    TYPE = (0x00,)
    LEVEL = (0x01,)

    # Effect-specific parameters
    PARAM_1 = (0x02,)
    PARAM_2 = (0x03,)

    # Send levels
    REVERB_SEND = (0x04,)
    DELAY_SEND = (0x05,)
    CHORUS_SEND = (0x06,)

    @classmethod
    def get_address_by_name(cls, name):
        """Look up an effect parameter address by its name"""
        member = cls.__members__.get(name, None)
        return member.value[0] if member else None

    @classmethod
    def get_by_address(cls, address):
        """Look up an effect parameter by its address"""
        for param in cls:
            if isinstance(param.value, tuple) and param.value[0] == address:
                return param
        return None  # Return None if no match is found

    @classmethod
    def get_by_name(cls, name):
        """Look up an effect parameter by its name"""
        return cls.__members__.get(name, None)

    @classmethod
    def get_common_param_by_name(cls, name):
        """Look up an effect parameter's category using address dictionary mapping"""
        param_mapping = {
            EffectsCommonParameter.PROGRAM_EFFECT_1: {
                "EFX1_TYPE", "EFX1_LEVEL", "EFX1_DELAY_SEND_LEVEL",
                "EFX1_REVERB_SEND_LEVEL", "EFX1_OUTPUT_ASSIGN",
                "EFX1_PARAM_1", "EFX1_PARAM_2"
            },
            EffectsCommonParameter.PROGRAM_EFFECT_2: {
                "EFX2_TYPE", "EFX2_LEVEL", "EFX2_DELAY_SEND_LEVEL",
                "EFX2_REVERB_SEND_LEVEL", "EFX2_PARAM_1", "EFX2_PARAM_2"
            },
            EffectsCommonParameter.PROGRAM_DELAY: {
                "DELAY_TYPE", "DELAY_TIME", "DELAY_TAP_TIME",
                "DELAY_FEEDBACK", "DELAY_HF_DAMP", "DELAY_LEVEL",
                "DELAY_REV_SEND_LEVEL"
            },
            EffectsCommonParameter.PROGRAM_REVERB: {
                "REVERB_OFF_ON", "REVERB_TYPE", "REVERB_TIME", "REVERB_HF_DAMP",
                "REVERB_LEVEL", "REVERB_PARAM_1", "REVERB_PARAM_2"
            }
        }

        for category, parameters in param_mapping.items():
            if name in parameters:
                return category

        return None  # Return None if no match is found


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