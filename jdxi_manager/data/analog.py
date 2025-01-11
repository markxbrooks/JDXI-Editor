"""Data structures for JD-Xi Analog Synth parameters"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, List

class AnalogParameter(Enum):
    """Analog synth parameters"""
    # Common parameters
    VOLUME = 0x00
    PAN = 0x01
    PORTAMENTO = 0x02
    
    # Oscillator parameters
    OSC_WAVE = 0x10
    OSC_PITCH = 0x11
    OSC_FINE = 0x12
    OSC_PWM = 0x13
    
    # Filter parameters
    FILTER_TYPE = 0x20
    FILTER_CUTOFF = 0x21
    FILTER_RESONANCE = 0x22
    FILTER_ENV_DEPTH = 0x23
    FILTER_KEY_FOLLOW = 0x24
    
    # Amplifier parameters
    AMP_LEVEL = 0x30
    AMP_PAN = 0x31
    
    # LFO parameters
    LFO_WAVE = 0x40
    LFO_RATE = 0x41
    LFO_DEPTH = 0x42
    LFO_RANDOM_PITCH = 0x43

@dataclass
class AnalogOscillator:
    """Analog oscillator settings"""
    wave: int = 0  # SAW
    pitch: int = 64  # Center
    fine: int = 64  # Center
    pwm: int = 0

@dataclass
class AnalogFilter:
    """Analog filter settings"""
    type: int = 0  # LPF
    cutoff: int = 127
    resonance: int = 0
    env_depth: int = 64  # Center
    key_follow: int = 0

@dataclass
class AnalogAmplifier:
    """Analog amplifier settings"""
    level: int = 100
    pan: int = 64  # Center

@dataclass
class AnalogLFO:
    """Analog LFO settings"""
    wave: int = 0  # Triangle
    rate: int = 64  # Medium
    depth: int = 0
    random_pitch: int = 0

@dataclass
class AnalogEnvelope:
    """Analog envelope settings"""
    attack: int = 0
    decay: int = 64
    sustain: int = 64
    release: int = 32

@dataclass
class AnalogSynthPatch:
    """Complete analog synth patch data"""
    # Common parameters
    volume: int = 100
    pan: int = 64  # Center
    portamento: int = 0
    
    # Section parameters
    oscillator: AnalogOscillator = None
    filter: AnalogFilter = None
    amplifier: AnalogAmplifier = None
    lfo: AnalogLFO = None
    envelope: AnalogEnvelope = None
    
    def __post_init__(self):
        """Initialize section parameters"""
        if self.oscillator is None:
            self.oscillator = AnalogOscillator()
        if self.filter is None:
            self.filter = AnalogFilter()
        if self.amplifier is None:
            self.amplifier = AnalogAmplifier()
        if self.lfo is None:
            self.lfo = AnalogLFO()
        if self.envelope is None:
            self.envelope = AnalogEnvelope()

    def validate_param(self, section: str, param: str, value: int) -> bool:
        """Validate parameter value is in range"""
        ranges = {
            'common': {
                'volume': (0, 127),
                'pan': (0, 127),
                'portamento': (0, 127)
            },
            'oscillator': {
                'wave': (0, 7),
                'pitch': (0, 127),
                'fine': (0, 127),
                'pwm': (0, 127)
            },
            'filter': {
                'type': (0, 3),
                'cutoff': (0, 127),
                'resonance': (0, 127),
                'env_depth': (0, 127),
                'key_follow': (0, 127)
            },
            'amplifier': {
                'level': (0, 127),
                'pan': (0, 127)
            },
            'lfo': {
                'wave': (0, 5),
                'rate': (0, 127),
                'depth': (0, 127),
                'random_pitch': (0, 127)
            },
            'envelope': {
                'attack': (0, 127),
                'decay': (0, 127),
                'sustain': (0, 127),
                'release': (0, 127)
            }
        }
        
        if section in ranges and param in ranges[section]:
            min_val, max_val = ranges[section][param]
            return min_val <= value <= max_val
        return False 