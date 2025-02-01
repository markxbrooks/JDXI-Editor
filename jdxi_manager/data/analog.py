"""Data structures for JD-Xi Analog Synth parameters"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, List, ClassVar, Tuple
import logging

from jdxi_manager.midi.messages import AnalogToneMessage
from jdxi_manager.midi.constants import AnalogToneCC, ANALOG_SYNTH_AREA, ANALOG_PART

AN_PRESETS: Tuple[str, ...] = (
    # Bank 1 (1-7)
    '001: Toxic Bass 1',    '002: Sub Bass 1',    '003: Backwards 1',   '004: Fat as That1',
    '005: Saw+Sub Bs 1',    '006: Saw Bass 1',    '007: Pulse Bass 1',
    # Bank 2 (8-14)
    '008: ResoSaw Bs 1',    '009: ResoSaw Bs 2',  '010: AcidSaw SEQ1',  '011: Psy Bass 1',
    '012: Dist TB Bs 1',    '013: Sqr Bass 1',    '014: Tri Bass 1',
    # Bank 3 (15-21)
    '015: Snake Glide1',    '016: Soft Bass 1',   '017: Tear Drop 1',   '018: Slo worn 1',
    '019: Dist LFO Bs1',    '020: ResoPulseBs1',  '021: Squelchy 1',
    # Bank 4 (22-28)
    '022: DnB Wobbler1',    '023: OffBeat Wob1',  '024: Chilled Wob',   '025: Bouncy Bass1',
    '026: PulseOfLife1',    '027: PWM Base 1',    '028: Pumper Bass1',
    # Bank 5 (29-35)
    '029: ClickerBass1',    '030: Psy Bass 2',    '031: HooverSuprt1',  '032: Celoclip 1',
    '033: Tri Fall Bs1',    '034: 808 Bass 1',    '035: House Bass 1',
    # Bank 6 (36-42)
    '036: Psy Bass 3',      '037: Reel 1',        '038: PortaSaw Ld1',  '039: Porta Lead 1',
    '040: Analog Tp 1',     '041: Tri Lead 1',    '042: Sine Lead 1',
    # Bank 7 (43-49)
    '043: Saw Buzz 1',      '044: Buzz Saw Ld1',  '045: Laser Lead 1',  '046: Saw & Per 1',
    '047: Insect 1',        '048: Sqr SEQ 1',     '049: ZipPhase 1',
    # Bank 8 (50-56)
    '050: Stinger 1',       '051: 3 Oh 3',        '052: Sus Zap 1',     '053: Bowouch 1',
    '054: Resocut 1',       '055: LFO FX',        '056: Fall Synth 1',
    # Bank 9 (57-63)
    '057: Twister 1',       '058: Analog Kick1',  '059: Zippers 1',     '060: Zippers 2',
    '061: Zippers 3',       '062: Siren Hell 1',  '063: SirenFX/Mod1'
)

# Analog preset categories
AN_CATEGORIES = {
    'BASS': [
        '001: Toxic Bass 1', '002: Sub Bass 1', '005: Saw+Sub Bs 1', '006: Saw Bass 1',
        '007: Pulse Bass 1', '008: ResoSaw Bs 1', '009: ResoSaw Bs 2', '011: Psy Bass 1',
        '012: Dist TB Bs 1', '013: Sqr Bass 1', '014: Tri Bass 1', '025: Bouncy Bass1',
        '030: Psy Bass 2', '034: 808 Bass 1', '035: House Bass 1', '036: Psy Bass 3'
    ],
    'LEAD': [
        '038: PortaSaw Ld1', '039: Porta Lead 1', '040: Analog Tp 1', '041: Tri Lead 1',
        '042: Sine Lead 1', '043: Saw Buzz 1', '044: Buzz Saw Ld1', '045: Laser Lead 1'
    ],
    'FX': [
        '003: Backwards 1', '004: Fat as That1', '015: Snake Glide1', '017: Tear Drop 1',
        '018: Slo worn 1', '019: Dist LFO Bs1', '052: Sus Zap 1', '055: LFO FX',
        '059: Zippers 1', '060: Zippers 2', '061: Zippers 3', '062: Siren Hell 1',
        '063: SirenFX/Mod1'
    ],
    'WOBBLE': [
        '020: ResoPulseBs1', '021: Squelchy 1', '022: DnB Wobbler1', '023: OffBeat Wob1',
        '024: Chilled Wob'
    ],
    'OTHER': [
        '016: Soft Bass 1', '026: PulseOfLife1', '027: PWM Base 1', '028: Pumper Bass1',
        '029: ClickerBass1', '031: HooverSuprt1', '032: Celoclip 1', '033: Tri Fall Bs1',
        '037: Reel 1', '046: Saw & Per 1', '047: Insect 1', '048: Sqr SEQ 1',
        '049: ZipPhase 1', '050: Stinger 1', '051: 3 Oh 3', '053: Bowouch 1',
        '054: Resocut 1', '056: Fall Synth 1', '057: Twister 1', '058: Analog Kick1'
    ]
}

class AnalogParameter(Enum):
    """Analog synth parameters with group, address, and value range."""

    # LFO Parameters
    LFO_SHAPE = (0x0D, 0, 5)
    LFO_RATE = (0x0E, 0, 127)
    LFO_FADE_TIME = (0x0F, 0, 127)
    LFO_TEMPO_SYNC_SWITCH = (0x10, 0, 1)
    LFO_TEMPO_SYNC_NOTE = (0x11, 0, 19)
    LFO_PITCH_DEPTH = (0x12, 1, 127)
    LFO_FILTER_DEPTH = (0x13, 1, 127)
    LFO_AMP_DEPTH = (0x14, 1, 127)
    LFO_KEY_TRIGGER = (0x15, 0, 1)

    # Oscillator Parameters
    OSC_WAVEFORM = (0x16, 0, 2)
    OSC_PITCH_COARSE = (0x17, 40, 88)
    OSC_PITCH_FINE = (0x18, 14, 114)
    OSC_PULSE_WIDTH = (0x19, 0, 127)
    OSC_PULSE_WIDTH_MOD_DEPTH = (0x1A, 0, 127)
    OSC_PITCH_ENV_VELOCITY_SENS = (0x1B, 1, 127)
    OSC_PITCH_ENV_ATTACK_TIME = (0x1C, 0, 127)
    OSC_PITCH_ENV_DECAY = (0x1D, 0, 127)
    OSC_PITCH_ENV_DEPTH = (0x1E, 1, 127)
    SUB_OSCILLATOR_TYPE = (0x1F, 0, 2)

    # Filter Parameters
    FILTER_SWITCH = (0x20, 0, 1)
    FILTER_CUTOFF = (0x21, 0, 127)
    FILTER_CUTOFF_KEYFOLLOW = (0x22, 54, 74)
    FILTER_RESONANCE = (0x23, 0, 127)
    FILTER_ENV_VELOCITY_SENS = (0x24, 1, 127)
    FILTER_ENV_ATTACK_TIME = (0x25, 0, 127)
    FILTER_ENV_DECAY_TIME = (0x26, 0, 127)
    FILTER_ENV_SUSTAIN_LEVEL = (0x27, 0, 127)
    FILTER_ENV_RELEASE_TIME = (0x28, 0, 127)
    FILTER_ENV_DEPTH = (0x29, 1, 127)

    # Amplifier Parameters
    AMP_LEVEL = (0x2A, 0, 127)
    AMP_LEVEL_KEYFOLLOW = (0x2B, 54, 74)
    AMP_LEVEL_VELOCITY_SENS = (0x2C, 1, 127)
    AMP_ENV_ATTACK_TIME = (0x2D, 0, 127)
    AMP_ENV_DECAY_TIME = (0x2E, 0, 127)
    AMP_ENV_SUSTAIN_LEVEL = (0x2F, 0, 127)
    AMP_ENV_RELEASE_TIME = (0x30, 0, 127)

    # Portamento and Other Parameters
    PORTAMENTO_SWITCH = (0x31, 0, 1)
    PORTAMENTO_TIME = (0x32, 0, 127)
    LEGATO_SWITCH = (0x33, 0, 1)
    OCTAVE_SHIFT = (0x34, 61, 67)
    PITCH_BEND_RANGE_UP = (0x35, 0, 24)
    PITCH_BEND_RANGE_DOWN = (0x36, 0, 24)

    # LFO Modulation Control
    LFO_PITCH_MODULATION_CONTROL = (0x38, 1, 127)
    LFO_FILTER_MODULATION_CONTROL = (0x39, 1, 127)
    LFO_AMP_MODULATION_CONTROL = (0x3A, 1, 127)
    LFO_RATE_MODULATION_CONTROL = (0x3B, 1, 127)

    # Reserve
    RESERVE_1 = (0x37, 0, 0)
    RESERVE_2 = (0x3C, 0, 0)

    def __init__(self, address: int, min_val: int, max_val: int):
        self.address = address
        self.min_val = min_val
        self.max_val = max_val

    def validate_value(self, value: int) -> int:
        """Validate and convert parameter value to MIDI range (0-127)"""
        if not isinstance(value, int):
            raise ValueError(f"Value must be integer, got {type(value)}")

        if value < self.min_val or value > self.max_val:
            raise ValueError(
                f"Value {value} out of range for {self.name} "
                f"(valid range: {self.min_val}-{self.max_val})"
            )

        return value

    @property
    def display_name(self) -> str:
        """Get display name for the parameter"""
        return self.name.replace("_", " ").title()

    @property
    def is_switch(self) -> bool:
        """Returns True if parameter is a binary/enum switch"""
        return self in [
            self.LFO_TEMPO_SYNC_SWITCH,
            self.LFO_KEY_TRIGGER,
            self.PORTAMENTO_SWITCH,
            self.LEGATO_SWITCH,
        ]

    def get_switch_text(self, value: int) -> str:
        """Get display text for switch values"""
        if self.is_switch:
            return "ON" if value else "OFF"
        return str(value)

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

@dataclass
class AnalogTone:
    """Analog synth tone data and methods"""
    
    @staticmethod
    def send_init_data(midi_helper):
        """Send initialization data for analog synth parameters
        
        Args:
            midi_helper: MIDI helper instance for sending messages
        """
        try:
            # Send parameter request messages
            for param_group in [
                (0x00, 0x10),  # Common parameters
                (0x10, 0x10),  # Oscillator parameters  
                (0x20, 0x10),  # Filter parameters
                (0x30, 0x10),  # Amplifier parameters
                (0x40, 0x10)   # LFO parameters
            ]:
                start_addr, size = param_group
                midi_helper.send_parameter(
                    area=ANALOG_SYNTH_AREA,
                    part=ANALOG_PART,
                    group=0x00,  # Always 0 for analog synth
                    param=start_addr,
                    value=0  # Request current value
                )
                logging.debug(f"Requested analog params {start_addr:02X}-{start_addr+size-1:02X}")
            
        except Exception as e:
            logging.error(f"Error sending analog init data: {str(e)}")

    @staticmethod
    def validate_data_length(data):
        """Validate received data length
        
        Args:
            data: Received MIDI data
            
        Returns:
            bool: True if data length is valid
        """
        # Analog synth data should be 64 bytes
        return len(data) == 64

    @staticmethod
    def parse_data(data):
        """Parse received analog synth data
        
        Args:
            data: Raw MIDI data bytes
            
        Returns:
            dict: Parsed parameter values
        """
        if not AnalogTone.validate_data_length(data):
            raise ValueError(f"Invalid data length: {len(data)}")
            
        return {
            'osc_wave': data[ANALOG_OSC_WAVE],
            'osc_coarse': data[ANALOG_OSC_COARSE] - 64,  # Convert to -24/+24
            'osc_fine': data[ANALOG_OSC_FINE] - 64,      # Convert to -50/+50
            'osc_pw': data[ANALOG_OSC_PW],
            'osc_pwm': data[ANALOG_OSC_PWM],
            'osc_penv_velo': data[ANALOG_OSC_PENV_VELO] - 64,  # Convert to -63/+63
            'osc_penv_a': data[ANALOG_OSC_PENV_A],
            'osc_penv_d': data[ANALOG_OSC_PENV_D],
            'osc_penv_depth': data[ANALOG_OSC_PENV_DEPTH] - 64,  # Convert to -63/+63
            'sub_type': data[ANALOG_SUB_TYPE],
            'lfo_shape': data[ANALOG_LFO_SHAPE],
            'lfo_rate': data[ANALOG_LFO_RATE],
            'lfo_fade': data[ANALOG_LFO_FADE],
            'lfo_sync': data[ANALOG_LFO_SYNC],
            'lfo_sync_note': data[ANALOG_LFO_SYNC_NOTE],
            'lfo_pitch': data[ANALOG_LFO_PITCH] - 64,  # Convert to -63/+63
            'lfo_filter': data[ANALOG_LFO_FILTER] - 64,  # Convert to -63/+63
            'lfo_amp': data[ANALOG_LFO_AMP] - 64,  # Convert to -63/+63
            'lfo_key_trig': data[ANALOG_LFO_KEY_TRIG]
}


class AnalogCommonParameter(Enum):
    """Common parameters for Digital/SuperNATURAL synth tones.
    These parameters are shared across all partials.
    """

    # LFO Parameters
    LFO_SHAPE = (0x0D, 0, 5)  # TRI, SIN, SAW, SQR, S&H, RND
    LFO_RATE = (0x0E, 0, 127)
    LFO_FADE_TIME = (0x0F, 0, 127)
    LFO_TEMPO_SYNC_SWITCH = (0x10, 0, 1)  # OFF, ON
    LFO_TEMPO_SYNC_NOTE = (0x11, 0, 19)  # 16, 12, 8, 4, 2, 1, 3/4, 2/3, 1/2, etc.
    LFO_PITCH_DEPTH = (0x12, 1, 127)  # -63 to +63
    LFO_FILTER_DEPTH = (0x13, 1, 127)  # -63 to +63
    LFO_AMP_DEPTH = (0x14, 1, 127)  # -63 to +63
    LFO_KEY_TRIGGER = (0x15, 0, 1)  # OFF, ON

    # Oscillator Parameters
    OSC_WAVEFORM = (0x16, 0, 2)  # SAW, TRI, PW-SQR
    OSC_PITCH_COARSE = (0x17, 40, 88)  # -24 to +24
    OSC_PITCH_FINE = (0x18, 14, 114)  # -50 to +50
    OSC_PULSE_WIDTH = (0x19, 0, 127)
    OSC_PULSE_WIDTH_MOD_DEPTH = (0x1A, 0, 127)
    OSC_PITCH_ENV_VELOCITY_SENS = (0x1B, 1, 127)  # -63 to +63
    OSC_PITCH_ENV_ATTACK_TIME = (0x1C, 0, 127)
    OSC_PITCH_ENV_DECAY = (0x1D, 0, 127)
    OSC_PITCH_ENV_DEPTH = (0x1E, 1, 127)  # -63 to +63
    SUB_OSCILLATOR_TYPE = (0x1F, 0, 2)  # OFF, OCT-1, OCT-2

    # Filter Parameters
    FILTER_SWITCH = (0x20, 0, 1)  # BYPASS, LPF
    FILTER_CUTOFF = (0x21, 0, 127)
    FILTER_CUTOFF_KEYFOLLOW = (0x22, 54, 74)  # -100 to +100
    FILTER_RESONANCE = (0x23, 0, 127)
    FILTER_ENV_VELOCITY_SENS = (0x24, 1, 127)  # -63 to +63
    FILTER_ENV_ATTACK_TIME = (0x25, 0, 127)
    FILTER_ENV_DECAY_TIME = (0x26, 0, 127)
    FILTER_ENV_SUSTAIN_LEVEL = (0x27, 0, 127)
    FILTER_ENV_RELEASE_TIME = (0x28, 0, 127)
    FILTER_ENV_DEPTH = (0x29, 1, 127)  # -63 to +63

    # Amplifier Parameters
    AMP_LEVEL = (0x2A, 0, 127)
    AMP_LEVEL_KEYFOLLOW = (0x2B, 54, 74)  # -100 to +100
    AMP_LEVEL_VELOCITY_SENS = (0x2C, 1, 127)  # -63 to +63
    AMP_ENV_ATTACK_TIME = (0x2D, 0, 127)
    AMP_ENV_DECAY_TIME = (0x2E, 0, 127)
    AMP_ENV_SUSTAIN_LEVEL = (0x2F, 0, 127)
    AMP_ENV_RELEASE_TIME = (0x30, 0, 127)

    # Portamento and Other Parameters
    PORTAMENTO_SWITCH = (0x31, 0, 1)  # OFF, ON
    PORTAMENTO_TIME = (0x32, 0, 127)  # CC# 5
    LEGATO_SWITCH = (0x33, 0, 1)  # OFF, ON
    OCTAVE_SHIFT = (0x34, 61, 67)  # -3 to +3
    PITCH_BEND_RANGE_UP = (0x35, 0, 24)
    PITCH_BEND_RANGE_DOWN = (0x36, 0, 24)

    # LFO Modulation Control
    LFO_PITCH_MODULATION_CONTROL = (0x38, 1, 127)  # -63 to +63
    LFO_FILTER_MODULATION_CONTROL = (0x39, 1, 127)  # -63 to +63
    LFO_AMP_MODULATION_CONTROL = (0x3A, 1, 127)  # -63 to +63
    LFO_RATE_MODULATION_CONTROL = (0x3B, 1, 127)  # -63 to +63

    # Reserve
    RESERVE_1 = (0x37, 0, 0)  # Reserve
    RESERVE_2 = (0x3C, 0, 0)  # Reserve

    def __init__(self, address: int, min_val: int, max_val: int):
        self.address = address
        self.min_val = min_val
        self.max_val = max_val

    @property
    def display_name(self) -> str:
        """Get display name for the parameter"""
        return self.name.replace("_", " ").title()

    @property
    def is_switch(self) -> bool:
        """Returns True if parameter is a binary/enum switch"""
        return self in [
            self.LFO_TEMPO_SYNC_SWITCH,
            self.LFO_KEY_TRIGGER,
            self.PORTAMENTO_SWITCH,
            self.LEGATO_SWITCH,
        ]

    def get_switch_text(self, value: int) -> str:
        """Get display text for switch values"""
        if self.is_switch:
            return "ON" if value else "OFF"
        return str(value)

    def validate_value(self, value: int) -> int:
        """Validate and convert parameter value"""
        if not isinstance(value, int):
            raise ValueError(f"Value must be integer, got {type(value)}")

        if value < self.min_val or value > self.max_val:
            raise ValueError(
                f"Value {value} out of range for {self.name} "
                f"(valid range: {self.min_val}-{self.max_val})"
            )

        return value



