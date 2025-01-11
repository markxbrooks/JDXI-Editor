from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, List

class DigitalParameter(Enum):
    """Digital synth parameters"""
    # Common parameters
    VOLUME = 0x00
    PAN = 0x01
    PORTAMENTO = 0x02
    PORTA_MODE = 0x03
    
    # Oscillator parameters
    OSC_WAVE = 0x20
    OSC_PITCH = 0x21
    OSC_FINE = 0x22
    OSC_PWM = 0x23
    
    # Filter parameters
    FILTER_TYPE = 0x30
    FILTER_CUTOFF = 0x31
    FILTER_RESONANCE = 0x32
    FILTER_ENV_DEPTH = 0x33
    FILTER_KEY_FOLLOW = 0x34
    
    # Amplifier parameters
    AMP_LEVEL = 0x40
    AMP_PAN = 0x41
    
    # LFO parameters
    LFO_WAVE = 0x50
    LFO_RATE = 0x51
    LFO_DEPTH = 0x52
    
    # Envelope parameters
    ENV_ATTACK = 0x60
    ENV_DECAY = 0x61
    ENV_SUSTAIN = 0x62
    ENV_RELEASE = 0x63

class DigitalPartial:
    """Digital synth partial parameters"""
    # Partial offsets
    PARTIAL_1 = 0x00
    PARTIAL_2 = 0x20
    PARTIAL_3 = 0x40
    
    # Structure types
    SINGLE = 0x00
    LAYER_1_2 = 0x01
    LAYER_2_3 = 0x02
    LAYER_1_3 = 0x03
    LAYER_ALL = 0x04
    SPLIT_1_2 = 0x05
    SPLIT_2_3 = 0x06
    SPLIT_1_3 = 0x07

class DigitalSynth:
    """Digital synth constants and presets"""
    # Basic waveforms
    WAVEFORMS = {
        "SAW": 0,
        "SQUARE": 1,
        "TRIANGLE": 2,
        "SINE": 3,
        "NOISE": 4,
        "SUPER_SAW": 5,
        "FEEDBACK_OSC": 6
    }
    
    # SuperNATURAL presets
    SN_PRESETS = [
        "001: JP8 Strings1",
        "002: JP8 Strings2",
        "003: JP8 Brass",
        "004: JP8 Organ",
        # ... add more presets
    ]

@dataclass
class DigitalPatch:
    """Digital synth patch data"""
    # Common parameters
    volume: int = 100
    pan: int = 64  # Center
    portamento: int = 0
    porta_mode: bool = False
    
    # Structure
    structure: int = DigitalPartial.SINGLE
    active_partials: List[bool] = None
    
    # Partial parameters
    partial_params: Dict[int, Dict[str, int]] = None
    
    def __post_init__(self):
        """Initialize default values"""
        if self.active_partials is None:
            self.active_partials = [True, False, False]  # Only Partial 1 active by default
            
        if self.partial_params is None:
            self.partial_params = {
                1: self._init_partial_params(),
                2: self._init_partial_params(),
                3: self._init_partial_params()
            }
    
    def _init_partial_params(self) -> Dict[str, int]:
        """Initialize parameters for a partial"""
        return {
            'wave': 0,  # SAW
            'pitch': 64,  # Center
            'fine': 64,  # Center
            'pwm': 0,
            'filter_type': 0,  # LPF
            'cutoff': 127,
            'resonance': 0,
            'env_depth': 64,  # Center
            'key_follow': 0,
            'level': 100,
            'pan': 64,  # Center
            'lfo_wave': 0,
            'lfo_rate': 64,
            'lfo_depth': 0
        } 