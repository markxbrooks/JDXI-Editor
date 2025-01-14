from dataclasses import dataclass
from enum import Enum, auto, IntEnum
from typing import Dict, List, Tuple, Optional
import logging
from jdxi_manager.midi.constants import (
    DIGITAL_SYNTH_AREA, PART_1, 
    OSC_1_GROUP, OSC_WAVE_PARAM,
    WAVE_SAW
)
from jdxi_manager.midi.constants.digital import (
    DIGITAL_SYNTH_AREA, PART_1, 
    OSC_1_GROUP, OSC_WAVE_PARAM,
    WAVE_SAW
)

class WaveGain(IntEnum):
    """Wave gain values in dB"""
    DB_MINUS_6 = 0  # -6 dB
    DB_0 = 1       #  0 dB
    DB_PLUS_6 = 2  # +6 dB
    DB_PLUS_12 = 3 # +12 dB

class OscWave(IntEnum):
    """Oscillator waveform types"""
    SAW = 0
    SQUARE = 1
    PW_SQUARE = 2  # Pulse Width Square
    TRIANGLE = 3
    SINE = 4
    NOISE = 5
    SUPER_SAW = 6
    PCM = 7

    @property
    def display_name(self) -> str:
        """Get display name for the waveform"""
        return {
            self.SAW: "SAW",
            self.SQUARE: "SQR",
            self.PW_SQUARE: "PWM",
            self.TRIANGLE: "TRI",
            self.SINE: "SINE",
            self.NOISE: "NOISE",
            self.SUPER_SAW: "S-SAW",
            self.PCM: "PCM"
        }[self]

    @property
    def description(self) -> str:
        """Get full description of the waveform"""
        return {
            self.SAW: "Sawtooth",
            self.SQUARE: "Square",
            self.PW_SQUARE: "Pulse Width Square",
            self.TRIANGLE: "Triangle",
            self.SINE: "Sine",
            self.NOISE: "Noise",
            self.SUPER_SAW: "Super Saw",
            self.PCM: "PCM Wave"
        }[self]

class FilterMode(IntEnum):
    """Filter mode types"""
    BYPASS = 0
    LPF = 1    # Low Pass Filter
    HPF = 2    # High Pass Filter
    BPF = 3    # Band Pass Filter
    PKG = 4    # Peak/Notch Filter
    LPF2 = 5   # -12dB/oct Low Pass
    LPF3 = 6   # -18dB/oct Low Pass
    LPF4 = 7   # -24dB/oct Low Pass

class FilterSlope(IntEnum):
    """Filter slope values"""
    DB_12 = 0  # -12 dB/octave
    DB_24 = 1  # -24 dB/octave

class LFOShape(IntEnum):
    """LFO waveform shapes"""
    TRIANGLE = 0
    SINE = 1
    SAW = 2
    SQUARE = 3
    SAMPLE_HOLD = 4  # S&H
    RANDOM = 5

class TempoSyncNote(IntEnum):
    """Tempo sync note values"""
    NOTE_16 = 0     # 16 bars
    NOTE_12 = 1     # 12 bars
    NOTE_8 = 2      # 8 bars
    NOTE_4 = 3      # 4 bars
    NOTE_2 = 4      # 2 bars
    NOTE_1 = 5      # 1 bar
    NOTE_3_4 = 6    # 3/4 (dotted half)
    NOTE_2_3 = 7    # 2/3 (triplet whole)
    NOTE_1_2 = 8    # 1/2 (half)
    NOTE_3_8 = 9    # 3/8 (dotted quarter)
    NOTE_1_3 = 10   # 1/3 (triplet half)
    NOTE_1_4 = 11   # 1/4 (quarter)
    NOTE_3_16 = 12  # 3/16 (dotted eighth)
    NOTE_1_6 = 13   # 1/6 (triplet quarter)
    NOTE_1_8 = 14   # 1/8 (eighth)
    NOTE_3_32 = 15  # 3/32 (dotted sixteenth)
    NOTE_1_12 = 16  # 1/12 (triplet eighth)
    NOTE_1_16 = 17  # 1/16 (sixteenth)
    NOTE_1_24 = 18  # 1/24 (triplet sixteenth)
    NOTE_1_32 = 19  # 1/32 (thirty-second)

class DigitalPartialOffset(IntEnum):
    """Offsets for each partial's parameters"""
    PARTIAL_1 = 0x00
    PARTIAL_2 = 0x40  # 64 bytes offset
    PARTIAL_3 = 0x80  # 128 bytes offset

class DigitalParameter(Enum):
    """Digital synth parameter addresses and valid ranges.
    
    Note: These addresses are for Partial 1. For other partials, add the appropriate
    offset from DigitalPartialOffset (0x40 for Partial 2, 0x80 for Partial 3).
    """
    def __init__(self, address: int, min_val: int, max_val: int):
        self.address = address
        self.min_val = min_val
        self.max_val = max_val

    # Oscillator parameters
    OSC_WAVE = (0x00, 0, 7)          # SAW(0), SQR(1), PW-SQR(2), TRI(3), SINE(4), NOISE(5), SUPER-SAW(6), PCM(7)
    OSC_COARSE = (0x03, 40, 88)      # -24 to +24 semitones (64 = center)
    OSC_FINE = (0x04, 14, 114)       # -50 to +50 cents (64 = center)

    # Filter parameters
    FILTER_CUTOFF = (0x0C, 0, 127)   # Cutoff frequency
    FILTER_RESONANCE = (0x0F, 0, 127) # Resonance/Q
    FILTER_ENV_ATTACK = (0x10, 0, 127)  # Filter envelope attack
    FILTER_ENV_DECAY = (0x11, 0, 127)   # Filter envelope decay
    FILTER_ENV_SUSTAIN = (0x12, 0, 127) # Filter envelope sustain
    FILTER_ENV_RELEASE = (0x13, 0, 127) # Filter envelope release

    # Amplifier parameters
    AMP_LEVEL = (0x15, 0, 127)       # Amplitude level
    AMP_ENV_ATTACK = (0x17, 0, 127)  # Amplitude envelope attack
    AMP_ENV_DECAY = (0x18, 0, 127)   # Amplitude envelope decay
    AMP_ENV_SUSTAIN = (0x19, 0, 127) # Amplitude envelope sustain
    AMP_ENV_RELEASE = (0x1A, 0, 127) # Amplitude envelope release

    # LFO parameters
    LFO_RATE = (0x1D, 0, 127)       # LFO speed
    LFO_DEPTH = (0x22, 1, 127)      # LFO pitch depth (-63 to +63)

    def get_display_value(self) -> Tuple[int, int]:
        """Returns the display range for this parameter (min, max)"""
        if self == self.OSC_COARSE:
            return (-24, 24)  # Semitones
        elif self == self.OSC_FINE:
            return (-50, 50)  # Cents
        elif self == self.LFO_DEPTH:
            return (-63, 63)  # Bipolar depth
        else:
            return (self.min_val, self.max_val)

    def convert_to_display(self, value: int) -> int:
        """Convert MIDI value to display value"""
        if self == self.OSC_COARSE:
            return value - 64  # Center at 0
        elif self == self.OSC_FINE:
            return value - 64  # Center at 0
        elif self == self.LFO_DEPTH:
            return value - 64  # Convert to -63/+63 range
        return value

    def convert_from_display(self, value: int) -> int:
        """Convert display value to MIDI value"""
        if self == self.OSC_COARSE:
            return value + 64  # Offset from center
        elif self == self.OSC_FINE:
            return value + 64  # Offset from center
        elif self == self.LFO_DEPTH:
            return value + 64  # Convert from -63/+63 range
        return value

    def get_address_for_partial(self, partial: int) -> int:
        """Get the actual parameter address for a specific partial (1-3)"""
        if partial not in [1, 2, 3]:
            raise ValueError("Partial must be 1, 2, or 3")
        offset = {
            1: DigitalPartialOffset.PARTIAL_1,
            2: DigitalPartialOffset.PARTIAL_2,
            3: DigitalPartialOffset.PARTIAL_3
        }[partial]
        return self.address + offset

    def __new__(cls, *args):
        obj = object.__new__(cls)
        obj._value_ = args[0]  # Set the enum value to just the address
        return obj

    def __str__(self) -> str:
        return f"{self.name} (addr: {self.address:02X}, range: {self.min_val}-{self.max_val})"

class DigitalPartial(IntEnum):
    """Digital synth partial numbers and structure types"""
    # Partial numbers
    PARTIAL_1 = 1
    PARTIAL_2 = 2
    PARTIAL_3 = 3

    # Structure types
    SINGLE = 0x00
    LAYER_1_2 = 0x01
    LAYER_2_3 = 0x02
    LAYER_1_3 = 0x03
    LAYER_ALL = 0x04
    SPLIT_1_2 = 0x05
    SPLIT_2_3 = 0x06
    SPLIT_1_3 = 0x07

    @property
    def switch_param(self) -> 'DigitalCommonParameter':
        """Get the switch parameter for this partial"""
        if self > 3:  # Structure types are > 3
            raise ValueError("Structure types don't have switch parameters")
        return {
            self.PARTIAL_1: DigitalCommonParameter.PARTIAL1_SWITCH,
            self.PARTIAL_2: DigitalCommonParameter.PARTIAL2_SWITCH,
            self.PARTIAL_3: DigitalCommonParameter.PARTIAL3_SWITCH
        }[self]

    @property
    def select_param(self) -> 'DigitalCommonParameter':
        """Get the select parameter for this partial"""
        if self > 3:  # Structure types are > 3
            raise ValueError("Structure types don't have select parameters")
        return {
            self.PARTIAL_1: DigitalCommonParameter.PARTIAL1_SELECT,
            self.PARTIAL_2: DigitalCommonParameter.PARTIAL2_SELECT,
            self.PARTIAL_3: DigitalCommonParameter.PARTIAL3_SELECT
        }[self]

    @property
    def is_partial(self) -> bool:
        """Returns True if this is a partial number (not a structure type)"""
        return 1 <= self <= 3

    @property
    def is_structure(self) -> bool:
        """Returns True if this is a structure type (not a partial number)"""
        return self <= 0x07 and not self.is_partial

    @classmethod
    def get_partials(cls) -> List['DigitalPartial']:
        """Get list of partial numbers (not structure types)"""
        return [cls.PARTIAL_1, cls.PARTIAL_2, cls.PARTIAL_3]

    @classmethod
    def get_structures(cls) -> List['DigitalPartial']:
        """Get list of structure types (not partial numbers)"""
        return [
            cls.SINGLE, cls.LAYER_1_2, cls.LAYER_2_3, cls.LAYER_1_3,
            cls.LAYER_ALL, cls.SPLIT_1_2, cls.SPLIT_2_3, cls.SPLIT_1_3
        ]

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

def validate_value(param: DigitalParameter, value: int) -> Optional[int]:
    """Validate and convert parameter value"""
    if not isinstance(value, int):
        raise ValueError(f"Value must be integer, got {type(value)}")
        
    # Check enum parameters
    if param == DigitalParameter.OSC_WAVE:
        if not isinstance(value, OscWave):
            try:
                value = OscWave(value).value
            except ValueError:
                raise ValueError(f"Invalid oscillator wave value: {value}")
            
    elif param == DigitalParameter.FILTER_MODE:
        if not isinstance(value, FilterMode):
            try:
                value = FilterMode(value).value
            except ValueError:
                raise ValueError(f"Invalid filter mode value: {value}")
            
    elif param == DigitalParameter.FILTER_SLOPE:
        if not isinstance(value, FilterSlope):
            try:
                value = FilterSlope(value).value
            except ValueError:
                raise ValueError(f"Invalid filter slope value: {value}")
            
    elif param in [DigitalParameter.LFO_SHAPE, DigitalParameter.MOD_LFO_SHAPE]:
        if not isinstance(value, LFOShape):
            try:
                value = LFOShape(value).value
            except ValueError:
                raise ValueError(f"Invalid LFO shape value: {value}")
            
    elif param in [DigitalParameter.LFO_TEMPO_NOTE, DigitalParameter.MOD_LFO_TEMPO_NOTE]:
        if not isinstance(value, TempoSyncNote):
            try:
                value = TempoSyncNote(value).value
            except ValueError:
                raise ValueError(f"Invalid tempo sync note value: {value}")
            
    elif param == DigitalParameter.WAVE_GAIN:
        if not isinstance(value, WaveGain):
            try:
                value = WaveGain(value).value
            except ValueError:
                raise ValueError(f"Invalid wave gain value: {value}")
    
    # Regular range check for non-bipolar parameters
    if value < param.min_val or value > param.max_val:
        raise ValueError(
            f"Value {value} out of range for {param.name} "
            f"(valid range: {param.min_val}-{param.max_val})"
        )
    
    return value

def send_digital_parameter(midi_helper, param: DigitalParameter, value: int, part: int = 1):
    """Send digital synth parameter change"""
    try:
        # Validate part number
        if part not in [1, 2]:
            raise ValueError("Part must be 1 or 2")
            
        # Validate and convert value
        midi_value = validate_value(param, value)
        
        # Convert part number to area
        area = 0x19 if part == 1 else 0x1A  # Digital 1 or 2
        
        midi_helper.send_parameter(
            area=area,
            part=0x01,
            group=0x00,
            param=param._value_,  # Use the enum value (address)
            value=midi_value
        )
        
        logging.debug(
            f"Sent digital parameter {param.name}: {value} "
            f"(MIDI value: {midi_value}) to part {part}"
        )
        
    except Exception as e:
        logging.error(f"Error sending digital parameter: {str(e)}")
        raise

def send_parameter(self, group: int, param: int, value: int) -> bool:
    """Send parameter change to synth
    
    Args:
        group: Parameter group (OSC, FILTER, etc)
        param: Parameter number
        value: Parameter value
        
    Returns:
        True if successful
    """
    try:
        if not self.midi_helper:
            logging.error("No MIDI helper available")
            return False
            
        return self.midi_helper.send_parameter(
            area=DIGITAL_SYNTH_AREA,  # 0x19 for Digital Synth 1
            part=PART_1,              # 0x01 for Part 1
            group=group,              # e.g. OSC_PARAM_GROUP
            param=param,              # Parameter number
            value=value               # Parameter value
        )
        
    except Exception as e:
        logging.error(f"Error sending digital parameter: {str(e)}")
        return False

def set_osc1_waveform(self, waveform: int) -> bool:
    """Set Oscillator 1 waveform
    
    Args:
        waveform: Waveform value (0=Saw, 1=Square, etc)
    """
    try:
        return self.midi_helper.send_parameter(
            area=DIGITAL_SYNTH_AREA,  # 0x19
            part=PART_1,              # 0x01
            group=OSC_1_GROUP,        # 0x20 - OSC 1
            param=OSC_WAVE_PARAM,     # 0x00 - Waveform
            value=waveform            # e.g. WAVE_SAW (0x00)
        )
    except Exception as e:
        logging.error(f"Error setting OSC1 waveform: {str(e)}")
        return False

class DigitalCommonParameter(Enum):
    """Common parameters for Digital/SuperNATURAL synth tones.
    These parameters are shared across all partials.
    """
    def __init__(self, address: int, min_val: int, max_val: int):
        self.address = address
        self.min_val = min_val
        self.max_val = max_val

    # Tone name parameters (12 ASCII characters)
    TONE_NAME_1 = (0x00, 32, 127)   # ASCII character 1
    TONE_NAME_2 = (0x01, 32, 127)   # ASCII character 2
    TONE_NAME_3 = (0x02, 32, 127)   # ASCII character 3
    TONE_NAME_4 = (0x03, 32, 127)   # ASCII character 4
    TONE_NAME_5 = (0x04, 32, 127)   # ASCII character 5
    TONE_NAME_6 = (0x05, 32, 127)   # ASCII character 6
    TONE_NAME_7 = (0x06, 32, 127)   # ASCII character 7
    TONE_NAME_8 = (0x07, 32, 127)   # ASCII character 8
    TONE_NAME_9 = (0x08, 32, 127)   # ASCII character 9
    TONE_NAME_10 = (0x09, 32, 127)  # ASCII character 10
    TONE_NAME_11 = (0x0A, 32, 127)  # ASCII character 11
    TONE_NAME_12 = (0x0B, 32, 127)  # ASCII character 12

    # Tone level
    TONE_LEVEL = (0x0C, 0, 127)     # Overall tone level

    # Performance parameters
    PORTAMENTO_SW = (0x12, 0, 1)     # Portamento Switch (OFF, ON)
    PORTAMENTO_TIME = (0x13, 0, 127)  # Portamento Time (CC# 5)
    MONO_SW = (0x14, 0, 1)           # Mono Switch (OFF, ON)
    OCTAVE_SHIFT = (0x15, 61, 67)    # Octave Shift (-3 to +3)
    PITCH_BEND_UP = (0x16, 0, 24)    # Pitch Bend Range Up (semitones)
    PITCH_BEND_DOWN = (0x17, 0, 24)  # Pitch Bend Range Down (semitones)

    # Partial switches
    PARTIAL1_SWITCH = (0x19, 0, 1)   # Partial 1 Switch (OFF, ON)
    PARTIAL1_SELECT = (0x1A, 0, 1)   # Partial 1 Select (OFF, ON)
    PARTIAL2_SWITCH = (0x1B, 0, 1)   # Partial 2 Switch (OFF, ON)
    PARTIAL2_SELECT = (0x1C, 0, 1)   # Partial 2 Select (OFF, ON)
    PARTIAL3_SWITCH = (0x1D, 0, 1)   # Partial 3 Switch (OFF, ON)
    PARTIAL3_SELECT = (0x1E, 0, 1)   # Partial 3 Select (OFF, ON)

    # Additional parameters
    RING_SWITCH = (0x1F, 0, 2)        # OFF(0), ---(1), ON(2)
    UNISON_SWITCH = (0x2E, 0, 1)      # OFF, ON
    PORTAMENTO_MODE = (0x31, 0, 1)    # NORMAL, LEGATO
    LEGATO_SWITCH = (0x32, 0, 1)      # OFF, ON
    ANALOG_FEEL = (0x34, 0, 127)      # Analog Feel amount
    WAVE_SHAPE = (0x35, 0, 127)       # Wave Shape amount
    TONE_CATEGORY = (0x36, 0, 127)    # Tone Category
    UNISON_SIZE = (0x3C, 0, 3)        # Unison voice count (2-5 voices)

    @property
    def display_name(self) -> str:
        """Get display name for the parameter"""
        return {
            self.RING_SWITCH: "Ring Mod",
            self.UNISON_SWITCH: "Unison",
            self.PORTAMENTO_MODE: "Porto Mode",
            self.LEGATO_SWITCH: "Legato",
            self.ANALOG_FEEL: "Analog Feel",
            self.WAVE_SHAPE: "Wave Shape",
            self.TONE_CATEGORY: "Category",
            self.UNISON_SIZE: "Uni Size"
        }.get(self, self.name.replace("_", " ").title())

    @property
    def is_switch(self) -> bool:
        """Returns True if parameter is a binary/enum switch"""
        return self in [
            self.PORTAMENTO_SW,
            self.MONO_SW,
            self.PARTIAL1_SWITCH,
            self.PARTIAL1_SELECT,
            self.PARTIAL2_SWITCH,
            self.PARTIAL2_SELECT,
            self.PARTIAL3_SWITCH,
            self.PARTIAL3_SELECT,
            self.RING_SWITCH,
            self.UNISON_SWITCH,
            self.PORTAMENTO_MODE,
            self.LEGATO_SWITCH
        ]

    def get_switch_text(self, value: int) -> str:
        """Get display text for switch values"""
        if self == self.RING_SWITCH:
            return ["OFF", "---", "ON"][value]
        elif self == self.PORTAMENTO_MODE:
            return ["NORMAL", "LEGATO"][value]
        elif self == self.UNISON_SIZE:
            return f"{value + 2} VOICE"  # 0=2 voices, 1=3 voices, etc.
        elif self.is_switch:
            return "ON" if value else "OFF"
        return str(value)

    def validate_value(self, value: int) -> int:
        """Validate and convert parameter value"""
        if not isinstance(value, int):
            raise ValueError(f"Value must be integer, got {type(value)}")

        # Special handling for ring switch
        if self == self.RING_SWITCH and value == 1:
            # Skip over the "---" value
            value = 2

        # Regular range check
        if value < self.min_val or value > self.max_val:
            raise ValueError(
                f"Value {value} out of range for {self.name} "
                f"(valid range: {self.min_val}-{self.max_val})"
            )

        return value

    def get_partial_number(self) -> Optional[int]:
        """Returns the partial number (1-3) if this is a partial parameter, None otherwise"""
        partial_params = {
            self.PARTIAL1_SWITCH: 1,
            self.PARTIAL1_SELECT: 1,
            self.PARTIAL2_SWITCH: 2,
            self.PARTIAL2_SELECT: 2,
            self.PARTIAL3_SWITCH: 3,
            self.PARTIAL3_SELECT: 3
        }
        return partial_params.get(self)

def set_tone_name(midi_helper, name: str) -> bool:
    """Set the tone name for a digital synth patch.
    
    Args:
        midi_helper: MIDI helper instance
        name: Name string (max 12 characters)
        
    Returns:
        True if successful
    """
    if len(name) > 12:
        logging.warning(f"Tone name '{name}' too long, truncating to 12 characters")
        name = name[:12]
    
    # Pad with spaces if shorter than 12 chars
    name = name.ljust(12)
    
    try:
        # Send each character as ASCII value
        for i, char in enumerate(name):
            param = getattr(DigitalCommonParameter, f'TONE_NAME_{i+1}')
            ascii_val = ord(char)
            
            # Validate ASCII range
            if ascii_val < 32 or ascii_val > 127:
                logging.warning(f"Invalid character '{char}' in tone name, using space")
                ascii_val = 32  # Space
                
            midi_helper.send_parameter(
                area=DIGITAL_SYNTH_AREA,
                part=PART_1,
                group=0x00,
                param=param.address,
                value=ascii_val
            )
            
        return True
        
    except Exception as e:
        logging.error(f"Error setting tone name: {str(e)}")
        return False

def set_partial_state(midi_helper, partial: DigitalPartial, enabled: bool = True, selected: bool = True) -> bool:
    """Set the state of a partial
    
    Args:
        midi_helper: MIDI helper instance
        partial: The partial to modify
        enabled: Whether the partial is enabled (ON/OFF)
        selected: Whether the partial is selected
        
    Returns:
        True if successful
    """
    try:
        # Send switch state
        success = midi_helper.send_parameter(
            area=DIGITAL_SYNTH_AREA,
            part=PART_1,
            group=0x00,
            param=partial.switch_param.address,
            value=1 if enabled else 0
        )
        if not success:
            return False

        # Send select state
        return midi_helper.send_parameter(
            area=DIGITAL_SYNTH_AREA,
            part=PART_1,
            group=0x00,
            param=partial.select_param.address,
            value=1 if selected else 0
        )

    except Exception as e:
        logging.error(f"Error setting partial {partial.name} state: {str(e)}")
        return False

def get_partial_state(midi_helper, partial: DigitalPartial) -> Tuple[bool, bool]:
    """Get the current state of a partial
    
    Args:
        midi_helper: MIDI helper instance
        partial: The partial to query
        
    Returns:
        Tuple of (enabled, selected)
    """
    try:
        # Get switch state
        switch_value = midi_helper.get_parameter(
            area=DIGITAL_SYNTH_AREA,
            part=PART_1,
            group=0x00,
            param=partial.switch_param.address
        )
        
        # Get select state
        select_value = midi_helper.get_parameter(
            area=DIGITAL_SYNTH_AREA,
            part=PART_1,
            group=0x00,
            param=partial.select_param.address
        )
        
        # Handle None returns (communication error)
        if switch_value is None or select_value is None:
            return (False, False)
            
        return (switch_value == 1, select_value == 1)
        
    except Exception as e:
        logging.error(f"Error getting partial {partial.name} state: {str(e)}")
        return (False, False)