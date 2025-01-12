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

# Analog synth preset definitions
ANALOG_PRESETS = {
    "Init Patch": {
        # Oscillator 1
        0x16: 0,      # SAW wave
        0x17: 64,     # Pitch 0
        0x18: 64,     # Fine tune 0
        0x19: 64,     # PW 50%
        0x1A: 0,      # PWM depth 0
        0x1B: 64,     # Pitch env velo 0
        0x1C: 0,      # Pitch env attack 0
        0x1D: 64,     # Pitch env decay mid
        0x1E: 64,     # Pitch env depth 0
        0x1F: 0,      # Sub osc OFF
        
        # Filter
        0x20: 1,      # LPF type
        0x21: 127,    # Cutoff max
        0x22: 64,     # Keyfollow 0
        0x23: 0,      # Resonance 0
        0x24: 64,     # Filter env velo 0
        0x25: 0,      # Filter attack 0
        0x26: 64,     # Filter decay mid
        0x27: 64,     # Filter sustain mid
        0x28: 32,     # Filter release short
        0x29: 64,     # Filter env depth 0
        
        # Amp
        0x2A: 100,    # Level 100
        0x2B: 64,     # Amp keyfollow 0
        0x2C: 64,     # Amp velocity 0
        0x2D: 0,      # Amp attack 0
        0x2E: 64,     # Amp decay mid
        0x2F: 127,    # Amp sustain max
        0x30: 32,     # Amp release short
        
        # Performance
        0x31: 0,      # Portamento OFF
        0x32: 0,      # Porta time 0
        0x33: 0,      # Legato OFF
        0x34: 64,     # Octave 0
        0x35: 2,      # Bend range up 2
        0x36: 2,      # Bend range down 2
        
        # LFO
        0x0D: 0,      # Triangle wave
        0x0E: 64,     # Rate mid
        0x0F: 0,      # Fade time 0
        0x10: 0,      # Tempo sync OFF
        0x11: 11,     # Sync note 1/4
        0x12: 64,     # Pitch depth 0
        0x13: 64,     # Filter depth 0
        0x14: 64,     # Amp depth 0
        0x15: 0,      # Key trigger OFF
        
        # Modulation
        0x38: 64,     # Pitch mod 0
        0x39: 64,     # Filter mod 0
        0x3A: 64,     # Amp mod 0
        0x3B: 64,     # Rate mod 0
        
        # Mixer
        0x3C: 64,     # OSC Balance center
        0x3D: 0,      # Noise level 0
        0x3E: 0,      # Ring mod level 0
        0x3F: 0       # Cross mod depth 0
    },
    
    "Fat Bass": {
        0x16: 0,      # SAW wave
        0x17: 40,     # Pitch -24
        0x18: 64,     # Fine tune 0
        0x1F: 1,      # Sub osc OCT-1
        0x20: 1,      # LPF type
        0x21: 64,     # Cutoff mid
        0x23: 100,    # Resonance high
        0x24: 84,     # Filter env velo +20
        0x25: 0,      # Filter attack 0
        0x26: 64,     # Filter decay mid
        0x27: 0,      # Filter sustain 0
        0x29: 94,     # Filter env depth +30
        0x2A: 100,    # Level 100
        0x2D: 0,      # Amp attack 0
        0x2E: 64,     # Amp decay mid
        0x2F: 100,    # Amp sustain high
        0x30: 32      # Amp release short
    },
    
    "Lead Synth": {
        0x16: 0,      # SAW wave
        0x17: 76,     # Pitch +12
        0x18: 64,     # Fine tune 0
        0x20: 1,      # LPF type
        0x21: 100,    # Cutoff high
        0x23: 64,     # Resonance mid
        0x24: 84,     # Filter env velo +20
        0x25: 0,      # Filter attack 0
        0x26: 64,     # Filter decay mid
        0x27: 64,     # Filter sustain mid
        0x29: 74,     # Filter env depth +10
        0x2A: 100,    # Level 100
        0x2D: 0,      # Amp attack 0
        0x2E: 64,     # Amp decay mid
        0x2F: 100,    # Amp sustain high
        0x31: 1,      # Portamento ON
        0x32: 32      # Porta time short
    },
    
    "Pad": {
        0x16: 1,      # TRI wave
        0x17: 64,     # Pitch 0
        0x18: 64,     # Fine tune 0
        0x20: 1,      # LPF type
        0x21: 64,     # Cutoff mid
        0x23: 32,     # Resonance low
        0x25: 100,    # Filter attack long
        0x26: 100,    # Filter decay long
        0x27: 100,    # Filter sustain high
        0x28: 100,    # Filter release long
        0x2A: 100,    # Level 100
        0x2D: 100,    # Amp attack long
        0x2E: 100,    # Amp decay long
        0x2F: 100,    # Amp sustain high
        0x30: 100,    # Amp release long
        0x0D: 1,      # LFO: Sine wave
        0x0E: 32,     # LFO: Slow rate
        0x12: 68,     # LFO: Slight pitch mod
        0x14: 68      # LFO: Slight amp mod
    },
    
    "Acid Bass": {
        0x16: 0,      # SAW wave
        0x17: 52,     # Pitch -12
        0x18: 64,     # Fine tune 0
        0x20: 1,      # LPF type
        0x21: 70,     # Cutoff medium-high
        0x23: 115,    # High resonance
        0x24: 94,     # Filter env velo +30
        0x25: 0,      # Filter attack 0
        0x26: 40,     # Filter decay short-mid
        0x27: 0,      # Filter sustain 0
        0x29: 104,    # Filter env depth +40
        0x2A: 100,    # Level 100
        0x31: 1,      # Portamento ON
        0x32: 20      # Porta time very short
    },
    
    "Brass": {
        0x16: 0,      # SAW wave
        0x17: 64,     # Pitch 0
        0x18: 64,     # Fine tune 0
        0x20: 1,      # LPF type
        0x21: 84,     # Cutoff high-mid
        0x23: 40,     # Resonance low-mid
        0x24: 84,     # Filter env velo +20
        0x25: 20,     # Filter attack short
        0x26: 70,     # Filter decay medium-long
        0x27: 80,     # Filter sustain high
        0x29: 74,     # Filter env depth +10
        0x2A: 110,    # Level 110
        0x2D: 20,     # Amp attack short
        0x2E: 70,     # Amp decay medium-long
        0x2F: 100     # Amp sustain high
    },
    
    "PWM Strings": {
        0x16: 2,      # PW-SQR wave
        0x17: 64,     # Pitch 0
        0x18: 62,     # Fine tune slightly flat
        0x19: 80,     # PW wider
        0x1A: 30,     # PWM depth moderate
        0x20: 1,      # LPF type
        0x21: 70,     # Cutoff medium-high
        0x23: 30,     # Resonance low
        0x25: 80,     # Filter attack medium-long
        0x26: 90,     # Filter decay long
        0x27: 90,     # Filter sustain high
        0x2A: 100,    # Level 100
        0x2D: 60,     # Amp attack medium
        0x2E: 90,     # Amp decay long
        0x2F: 90,     # Amp sustain high
        0x0D: 1,      # LFO: Sine
        0x0E: 40,     # LFO: Medium-slow rate
        0x14: 70      # LFO: Moderate amp mod
    },
    
    "Pluck": {
        0x16: 0,      # SAW wave
        0x17: 64,     # Pitch 0
        0x18: 64,     # Fine tune 0
        0x20: 1,      # LPF type
        0x21: 90,     # Cutoff high
        0x23: 70,     # Resonance medium-high
        0x24: 94,     # Filter env velo +30
        0x25: 0,      # Filter attack 0
        0x26: 30,     # Filter decay short
        0x27: 0,      # Filter sustain 0
        0x29: 84,     # Filter env depth +20
        0x2A: 100,    # Level 100
        0x2D: 0,      # Amp attack 0
        0x2E: 30,     # Amp decay short
        0x2F: 0,      # Amp sustain 0
        0x30: 20      # Amp release short
    },
    
    "Wobble Bass": {
        0x16: 0,      # SAW wave
        0x17: 40,     # Pitch -24
        0x18: 64,     # Fine tune 0
        0x1F: 1,      # Sub osc OCT-1
        0x20: 1,      # LPF type
        0x21: 70,     # Cutoff medium-high
        0x23: 110,    # Resonance very high
        0x0D: 3,      # LFO: Square
        0x0E: 80,     # LFO: Medium-fast rate
        0x10: 1,      # Tempo sync ON
        0x11: 14,     # Sync note 1/8
        0x13: 100,    # Heavy filter mod
        0x2A: 110     # Level 110
    },
    
    "Ambient Sweep": {
        0x16: 1,      # TRI wave
        0x17: 64,     # Pitch 0
        0x18: 66,     # Fine tune slightly sharp
        0x20: 1,      # LPF type
        0x21: 50,     # Cutoff medium-low
        0x23: 60,     # Resonance medium
        0x25: 120,    # Filter attack very long
        0x26: 120,    # Filter decay very long
        0x27: 80,     # Filter sustain high
        0x2A: 90,     # Level 90
        0x2D: 120,    # Amp attack very long
        0x2E: 120,    # Amp decay very long
        0x2F: 80,     # Amp sustain high
        0x0D: 0,      # LFO: Triangle
        0x0E: 20,     # LFO: Very slow rate
        0x12: 74,     # Moderate pitch mod
        0x13: 74      # Moderate filter mod
    }
} 