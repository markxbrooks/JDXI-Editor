"""Data structures for JD-Xi Analog Synth parameters"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum

from ..midi.constants import (
    Waveform, RandomPitchDepth, SyncNote, Note,
    EnvelopeSection, PCMWave
)

# Keep AN dictionary for backwards compatibility
AN = {
    'osc1': {
        'wave': (0x00, 0, 7),
        'range': (0x01, -24, 24),
        'fine': (0x02, -50, 50),
        'detune': (0x03, 0, 127),
        'mod_depth': (0x04, 0, 127)
    },
    'osc2': {
        'wave': (0x10, 0, 7),
        'range': (0x11, -24, 24),
        'fine': (0x12, -50, 50),
        'detune': (0x13, 0, 127),
        'mod_depth': (0x14, 0, 127),
        'sync': (0x15, 0, 1)
    },
    'mixer': {
        'balance': (0x20, 0, 127),
        'noise': (0x21, 0, 127),
        'ring_mod': (0x22, 0, 127),
        'cross_mod': (0x23, 0, 127)
    },
    'filter': {
        'cutoff': (0x30, 0, 127),
        'resonance': (0x31, 0, 127),
        'key_follow': (0x32, 0, 127),
        'env_depth': (0x33, 0, 127),
        'lfo_depth': (0x34, 0, 127),
        'velocity': (0x35, 0, 127)
    },
    'amp': {
        'level': (0x40, 0, 127),
        'pan': (0x41, -64, 63),
        'portamento': (0x42, 0, 127),
        'legato': (0x43, 0, 1)
    },
    'lfo': {
        'wave': (0x50, 0, 7),
        'rate': (0x51, 0, 127),
        'sync': (0x52, 0, 1),
        'fade': (0x53, 0, 127),
        'delay': (0x54, 0, 127)
    },
    'env': {
        'attack': (0x60, 0, 127),
        'decay': (0x61, 0, 127),
        'sustain': (0x62, 0, 127),
        'release': (0x63, 0, 127)
    }
}

# New data structures follow...
class AnalogParameter(Enum):
    """Parameter addresses for analog synth"""
    # OSC 1 parameters
    OSC1_WAVE = 0x00
    OSC1_RANGE = 0x01
    OSC1_FINE = 0x02
    OSC1_DETUNE = 0x03
    OSC1_MOD_DEPTH = 0x04

    # OSC 2 parameters
    OSC2_WAVE = 0x10
    OSC2_RANGE = 0x11
    OSC2_FINE = 0x12
    OSC2_DETUNE = 0x13
    OSC2_MOD_DEPTH = 0x14
    OSC2_SYNC = 0x15

    # MIXER parameters
    OSC_BALANCE = 0x20
    NOISE_LEVEL = 0x21
    RING_MOD = 0x22
    CROSS_MOD = 0x23

    # FILTER parameters
    CUTOFF = 0x30
    RESONANCE = 0x31
    KEY_FOLLOW = 0x32
    ENV_DEPTH = 0x33
    LFO_DEPTH = 0x34
    VELOCITY_SENS = 0x35

    # AMP parameters
    LEVEL = 0x40
    PAN = 0x41
    PORTAMENTO = 0x42
    LEGATO = 0x43

    # LFO parameters
    LFO_WAVE = 0x50
    LFO_RATE = 0x51
    LFO_SYNC = 0x52
    LFO_FADE = 0x53
    LFO_DELAY = 0x54

    # ENVELOPE parameters
    ENV_ATTACK = 0x60
    ENV_DECAY = 0x61
    ENV_SUSTAIN = 0x62
    ENV_RELEASE = 0x63

@dataclass
class AnalogOscillator:
    """Oscillator settings"""
    wave: Waveform = Waveform.SAW
    range: int = 0  # -24 to +24 semitones
    fine: int = 0   # -50 to +50 cents
    detune: int = 0  # 0-127
    mod_depth: int = 0  # 0-127

@dataclass
class AnalogMixer:
    """Mixer settings"""
    osc_balance: int = 64  # 0-127 (OSC1/OSC2 balance)
    noise_level: int = 0   # 0-127
    ring_mod: int = 0      # 0-127
    cross_mod: int = 0     # 0-127

@dataclass
class AnalogFilter:
    """Filter settings"""
    cutoff: int = 127      # 0-127
    resonance: int = 0     # 0-127
    key_follow: int = 0    # 0-127
    env_depth: int = 0     # 0-127
    lfo_depth: int = 0     # 0-127
    velocity_sens: int = 0  # 0-127

@dataclass
class AnalogAmplifier:
    """Amplifier settings"""
    level: int = 127       # 0-127
    pan: int = 64         # 0-127 (center = 64)
    portamento: int = 0    # 0-127
    legato: bool = False   # True/False

@dataclass
class AnalogLFO:
    """LFO settings"""
    wave: Waveform = Waveform.TRIANGLE
    rate: int = 64        # 0-127
    sync: bool = False    # True/False
    fade: int = 0         # 0-127
    delay: int = 0        # 0-127

@dataclass
class AnalogEnvelope:
    """Envelope settings"""
    attack: int = 0    # 0-127
    decay: int = 0     # 0-127
    sustain: int = 127 # 0-127
    release: int = 0   # 0-127

@dataclass
class AnalogSynthPatch:
    """Complete analog synth patch"""
    name: str = "Init Patch"
    osc1: AnalogOscillator = field(default_factory=AnalogOscillator)
    osc2: AnalogOscillator = field(default_factory=AnalogOscillator)
    mixer: AnalogMixer = field(default_factory=AnalogMixer)
    filter: AnalogFilter = field(default_factory=AnalogFilter)
    amp: AnalogAmplifier = field(default_factory=AnalogAmplifier)
    lfo: AnalogLFO = field(default_factory=AnalogLFO)
    pitch_env: AnalogEnvelope = field(default_factory=AnalogEnvelope)
    filter_env: AnalogEnvelope = field(default_factory=AnalogEnvelope)
    amp_env: AnalogEnvelope = field(default_factory=AnalogEnvelope)

    def to_sysex(self) -> List[int]:
        """Convert patch to SysEx data"""
        data = []
        # Add parameter data in correct order
        # OSC1
        data.extend([
            self.osc1.wave.value,
            self.osc1.range + 64,  # Convert -24/+24 to 40-88
            self.osc1.fine + 64,   # Convert -50/+50 to 14-114
            self.osc1.detune,
            self.osc1.mod_depth
        ])
        # OSC2
        data.extend([
            self.osc2.wave.value,
            self.osc2.range + 64,
            self.osc2.fine + 64,
            self.osc2.detune,
            self.osc2.mod_depth
        ])
        # Continue with other sections...
        return data

    @classmethod
    def from_sysex(cls, data: List[int]) -> 'AnalogSynthPatch':
        """Create patch from SysEx data"""
        patch = cls()
        # Parse data and set parameters
        patch.osc1.wave = Waveform(data[0])
        patch.osc1.range = data[1] - 64
        patch.osc1.fine = data[2] - 64
        patch.osc1.detune = data[3]
        patch.osc1.mod_depth = data[4]
        # Continue parsing other sections...
        return patch 