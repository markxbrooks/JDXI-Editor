from dataclasses import dataclass
from enum import Enum, auto, IntEnum
from typing import Dict, List, Tuple, Optional
import logging
from jdxi_manager.midi.constants import (
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

class DigitalParameter(Enum):
    """Digital synth parameter addresses and valid ranges"""
    def __init__(self, address: int, min_val: int, max_val: int):
        self.address = address
        self.min_val = min_val
        self.max_val = max_val

    # Define enum values with their (address, min, max) tuples
    OSC_WAVE = (0x00, 0, 7)          # SAW, SQR, PW-SQR, TRI, SINE, NOISE, SUPER-SAW, PCM
    OSC_VARIATION = (0x01, 0, 2)      # A, B, C
    OSC_PITCH = (0x03, 40, 88)        # -24 to +24 (64 = center)
    OSC_DETUNE = (0x04, 14, 114)      # -50 to +50 (64 = center)
    OSC_PW_MOD_DEPTH = (0x05, 0, 127) # Full range
    OSC_PW = (0x06, 0, 127)          # Full range

    def __new__(cls, *args):
        obj = object.__new__(cls)
        obj._value_ = args[0]  # Set the enum value to just the address
        return obj

    def __str__(self) -> str:
        return f"{self.name} (addr: {self.address:02X}, range: {self.min_val}-{self.max_val})"

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