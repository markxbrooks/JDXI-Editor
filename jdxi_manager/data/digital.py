from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, List, Tuple

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
    
    # PCM Wave list
    PCM_WAVES = [
        "Saw",
        "Square",
        "Triangle",
        "Sine",
        "Super Saw",
        "Noise",
        "PCM Piano",
        "PCM E.Piano",
        "PCM Clav",
        "PCM Vibes",
        "PCM Strings",
        "PCM Brass",
        "PCM A.Bass",
        "PCM Bass",
        "PCM Bell",
        "PCM Synth"
    ]

# Digital synth preset names
DIGITAL_PRESETS: Tuple[str, ...] = (
    # Bank 1 (1-16)
    '001: Init Tone',      '002: Saw Lead',      '003: Square Lead',    '004: Sine Lead',
    '005: Brass',          '006: Strings',        '007: Bell',           '008: EP',
    '009: Bass',           '010: Sub Bass',       '011: Kick',           '012: Snare',
    '013: Hi-Hat',         '014: Cymbal',         '015: Tom',            '016: Perc',
    
    # Bank 2 (17-32)
    '017: Pad',            '018: Sweep',          '019: Noise',          '020: FX',
    '021: Pluck',          '022: Guitar',         '023: Piano',          '024: Organ',
    '025: Synth Bass',     '026: Acid Bass',      '027: Wobble Bass',    '028: FM Bass',
    '029: Voice',          '030: Vocoder',        '031: Choir',          '032: Atmosphere',
    
    # Bank 3 (33-48)
    '033: Lead Sync',      '034: Unison Lead',    '035: Stack Lead',     '036: PWM Lead',
    '037: Dist Lead',      '038: Filter Lead',    '039: Mod Lead',       '040: Seq Lead',
    '041: Brass Sect',     '042: Strings Ens',    '043: Orchestra',      '044: Pizzicato',
    '045: Mallet',         '046: Crystal',        '047: Metallic',       '048: Kalimba',
    
    # Bank 4 (49-64)
    '049: E.Piano 1',      '050: E.Piano 2',      '051: Clav',           '052: Harpsichord',
    '053: Vibraphone',     '054: Marimba',        '055: Xylophone',      '056: Glocken',
    '057: Nylon Gtr',      '058: Steel Gtr',      '059: Jazz Gtr',       '060: Clean Gtr',
    '061: Muted Gtr',      '062: Overdrive',      '063: Dist Gtr',       '064: Power Gtr'
)

# Digital preset categories
DIGITAL_CATEGORIES = {
    'LEAD': [
        '002: Saw Lead', '003: Square Lead', '004: Sine Lead', '033: Lead Sync',
        '034: Unison Lead', '035: Stack Lead', '036: PWM Lead', '037: Dist Lead',
        '038: Filter Lead', '039: Mod Lead', '040: Seq Lead'
    ],
    'BASS': [
        '009: Bass', '010: Sub Bass', '025: Synth Bass', '026: Acid Bass',
        '027: Wobble Bass', '028: FM Bass'
    ],
    'KEYS': [
        '008: EP', '023: Piano', '024: Organ', '049: E.Piano 1', '050: E.Piano 2',
        '051: Clav', '052: Harpsichord'
    ],
    'ORCHESTRAL': [
        '006: Strings', '041: Brass Sect', '042: Strings Ens', '043: Orchestra',
        '044: Pizzicato'
    ],
    'PERCUSSION': [
        '007: Bell', '011: Kick', '012: Snare', '013: Hi-Hat', '014: Cymbal',
        '015: Tom', '016: Perc', '045: Mallet', '046: Crystal', '053: Vibraphone',
        '054: Marimba', '055: Xylophone', '056: Glocken'
    ],
    'GUITAR': [
        '022: Guitar', '057: Nylon Gtr', '058: Steel Gtr', '059: Jazz Gtr',
        '060: Clean Gtr', '061: Muted Gtr', '062: Overdrive', '063: Dist Gtr',
        '064: Power Gtr'
    ],
    'PAD/ATMOS': [
        '017: Pad', '018: Sweep', '019: Noise', '020: FX', '029: Voice',
        '030: Vocoder', '031: Choir', '032: Atmosphere'
    ],
    'OTHER': [
        '001: Init Tone', '005: Brass', '021: Pluck', '047: Metallic', '048: Kalimba'
    ]
}

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