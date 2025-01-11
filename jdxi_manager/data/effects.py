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

class EffectParameter(Enum):
    """Effect parameters"""
    # Common parameters
    TYPE = 0x00
    LEVEL = 0x01
    
    # Effect-specific parameters
    PARAM_1 = 0x02
    PARAM_2 = 0x03
    
    # Send levels
    REVERB_SEND = 0x04
    DELAY_SEND = 0x05
    CHORUS_SEND = 0x06

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
    # Effect type and common parameters
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