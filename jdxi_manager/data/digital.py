from dataclasses import dataclass
from enum import Enum, auto, IntEnum
from typing import Dict, List, Tuple, Optional
import logging
from jdxi_manager.midi.constants import (
    DIGITAL_SYNTH_AREA,
    PART_1,
    PART_2,
    OSC_1_GROUP,
    OSC_WAVE_PARAM,
    WAVE_SAW,
)
from jdxi_manager.midi.constants.digital import (
    DIGITAL_SYNTH_AREA,
    PART_1,
    PART_2,
    OSC_1_GROUP,
    OSC_WAVE_PARAM,
    WAVE_SAW,
)

# MIDI Constants for Digital Synth
# DIGITAL_SYNTH_AREA = 0x19  # Digital Synth 1 area

# Parameter Groups
OSC_GROUP = 0x20  # Oscillator parameters
FILTER_GROUP = 0x21  # Filter parameters
AMP_GROUP = 0x22  # Amplifier parameters
LFO_GROUP = 0x23  # LFO parameters
MOD_LFO_GROUP = 0x24  # Modulation LFO parameters


class WaveGain(IntEnum):
    """Wave gain values in dB"""

    DB_MINUS_6 = 0  # -6 dB
    DB_0 = 1  #  0 dB
    DB_PLUS_6 = 2  # +6 dB
    DB_PLUS_12 = 3  # +12 dB


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
            self.PCM: "PCM",
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
            self.PCM: "PCM Wave",
        }[self]


class FilterMode(IntEnum):
    """Filter mode types"""

    BYPASS = 0
    LPF = 1  # Low Pass Filter
    HPF = 2  # High Pass Filter
    BPF = 3  # Band Pass Filter
    PKG = 4  # Peak/Notch Filter
    LPF2 = 5  # -12dB/oct Low Pass
    LPF3 = 6  # -18dB/oct Low Pass
    LPF4 = 7  # -24dB/oct Low Pass


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

    NOTE_16 = 0  # 16 bars
    NOTE_12 = 1  # 12 bars
    NOTE_8 = 2  # 8 bars
    NOTE_4 = 3  # 4 bars
    NOTE_2 = 4  # 2 bars
    NOTE_1 = 5  # 1 bar
    NOTE_3_4 = 6  # 3/4 (dotted half)
    NOTE_2_3 = 7  # 2/3 (triplet whole)
    NOTE_1_2 = 8  # 1/2 (half)
    NOTE_3_8 = 9  # 3/8 (dotted quarter)
    NOTE_1_3 = 10  # 1/3 (triplet half)
    NOTE_1_4 = 11  # 1/4 (quarter)
    NOTE_3_16 = 12  # 3/16 (dotted eighth)
    NOTE_1_6 = 13  # 1/6 (triplet quarter)
    NOTE_1_8 = 14  # 1/8 (eighth)
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
    """Digital synth parameters with their addresses and value ranges"""

    # Oscillator parameters
    OSC_WAVE = (0x20, 0x00, 0, 7)  # Waveform type
    OSC_WAVE_VAR = (0x20, 0x01, 0, 2)  # Wave variation
    OSC_PITCH = (0x20, 0x02, -24, 24)  # Coarse tune
    OSC_DETUNE = (0x20, 0x03, -50, 50)  # Fine tune
    OSC_PW = (0x20, 0x05, 0, 127)  # Pulse Width
    OSC_PWM_DEPTH = (0x20, 0x06, 0, 127)  # PWM Depth
    OSC_PITCH_ATTACK = (0x20, 0x07, 0, 127)  # Pitch Envelope Attack
    OSC_PITCH_DECAY = (0x20, 0x08, 0, 127)  # Pitch Envelope Decay
    OSC_PITCH_DEPTH = (0x20, 0x09, -63, 63)  # Pitch Envelope Depth

    # Filter parameters - Changed group from 0x01 to 0x21
    FILTER_MODE = (0x21, 0x00, 0, 7)  # Filter mode
    FILTER_SLOPE = (0x21, 0x01, 0, 1)  # Filter slope
    FILTER_CUTOFF = (0x21, 0x02, 0, 127)  # Cutoff frequency
    FILTER_RESONANCE = (0x21, 0x03, 0, 127)  # Resonance
    FILTER_KEYFOLLOW = (0x21, 0x04, -100, 100)  # Key follow
    FILTER_VELOCITY = (0x21, 0x05, -63, 63)  # Velocity sensitivity
    FILTER_ENV_ATTACK = (0x21, 0x06, 0, 127)  # Filter envelope attack
    FILTER_ENV_DECAY = (0x21, 0x07, 0, 127)  # Filter envelope decay
    FILTER_ENV_SUSTAIN = (0x21, 0x08, 0, 127)  # Filter envelope sustain
    FILTER_ENV_RELEASE = (0x21, 0x09, 0, 127)  # Filter envelope release
    FILTER_ENV_DEPTH = (0x21, 0x0A, -63, 63)  # Filter envelope depth

    # Amplifier parameters - Changed group from 0x22 to 0x20
    AMP_LEVEL = (0x20, 0x15, 0, 127)  # Amplitude level
    AMP_VELOCITY = (0x20, 0x16, -63, 63)  # Velocity sensitivity
    AMP_ENV_ATTACK = (0x20, 0x17, 0, 127)  # Amplitude envelope attack
    AMP_ENV_DECAY = (0x20, 0x18, 0, 127)  # Amplitude envelope decay
    AMP_ENV_SUSTAIN = (0x20, 0x19, 0, 127)  # Amplitude envelope sustain
    AMP_ENV_RELEASE = (0x20, 0x1A, 0, 127)  # Amplitude envelope release
    AMP_PAN = (0x20, 0x1B, -64, 63)  # Pan position
    AMP_KEYFOLLOW = (0x20, 0x1C, -100, 100)  # Key follow (-100 to +100)

    # LFO parameters
    LFO_SHAPE = (0x23, 0x00, 0, 5)  # LFO waveform
    LFO_RATE = (0x23, 0x01, 0, 127)  # LFO rate
    LFO_SYNC = (0x23, 0x02, 0, 1)  # Tempo sync switch
    LFO_NOTE = (0x23, 0x03, 0, 19)  # Tempo sync note
    LFO_FADE = (0x23, 0x04, 0, 127)  # Fade time
    LFO_TRIGGER = (0x23, 0x05, 0, 1)  # Key trigger
    LFO_PITCH = (0x23, 0x06, -63, 63)  # Pitch mod depth
    LFO_FILTER = (0x23, 0x07, -63, 63)  # Filter mod depth
    LFO_AMP = (0x23, 0x08, -63, 63)  # Amp mod depth
    LFO_PAN = (0x23, 0x09, -63, 63)  # Pan mod depth

    # Modulation LFO parameters
    MOD_LFO_SHAPE = (0x24, 0x00, 0, 5)  # Mod LFO waveform
    MOD_LFO_RATE = (0x24, 0x01, 0, 127)  # Mod LFO rate
    MOD_LFO_SYNC = (0x24, 0x02, 0, 1)  # Tempo sync switch
    MOD_LFO_NOTE = (0x24, 0x03, 0, 19)  # Tempo sync note
    MOD_LFO_PITCH = (0x24, 0x04, -63, 63)  # Pitch mod depth
    MOD_LFO_FILTER = (0x24, 0x05, -63, 63)  # Filter mod depth
    MOD_LFO_AMP = (0x24, 0x06, -63, 63)  # Amp mod depth
    MOD_LFO_PAN = (0x24, 0x07, -63, 63)  # Pan mod depth
    MOD_LFO_RATE_CTRL = (0x24, 0x08, -63, 63)  # Rate control

    # Additional parameters
    CUTOFF_AFTERTOUCH = (0x25, 0x00, -63, 63)  # Cutoff aftertouch
    LEVEL_AFTERTOUCH = (0x25, 0x01, -63, 63)  # Level aftertouch
    WAVE_GAIN = (0x25, 0x02, 0, 3)  # Wave gain
    HPF_CUTOFF = (0x25, 0x03, 0, 127)  # HPF cutoff
    SUPER_SAW_DETUNE = (0x25, 0x04, 0, 127)  # Super saw detune

    # Wave Number parameters
    WAVE_NUMBER_1 = (0x26, 0x00, 0, 15)  # Most significant 4 bits
    WAVE_NUMBER_2 = (0x26, 0x01, 0, 15)  # Next 4 bits
    WAVE_NUMBER_3 = (0x26, 0x02, 0, 15)  # Next 4 bits
    WAVE_NUMBER_4 = (0x26, 0x03, 0, 15)  # Least significant 4 bits

    def __init__(self, group: int, address: int, min_val: int, max_val: int):
        self.group = group
        self.address = address
        self.min_val = min_val
        self.max_val = max_val

    def validate_value(self, value: int) -> int:
        """Validate and convert parameter value to MIDI range (0-127)"""
        if not isinstance(value, int):
            raise ValueError(f"Value must be integer, got {type(value)}")

        # Convert bipolar values to MIDI range
        if self in [
            # Oscillator parameters
            self.OSC_PITCH,
            self.OSC_DETUNE,
            self.OSC_PITCH_DEPTH,
            # Filter parameters
            self.FILTER_KEYFOLLOW,
            self.FILTER_VELOCITY,
            self.FILTER_ENV_DEPTH,
            # Amplifier parameters
            self.AMP_VELOCITY,
            self.AMP_PAN,
            self.AMP_KEYFOLLOW,
            # LFO parameters
            self.LFO_PITCH,
            self.LFO_FILTER,
            self.LFO_AMP,
            self.LFO_PAN,
            # Mod LFO parameters
            self.MOD_LFO_PITCH,
            self.MOD_LFO_FILTER,
            self.MOD_LFO_AMP,
            self.MOD_LFO_PAN,
            self.MOD_LFO_RATE_CTRL,
        ]:
            # Convert from display range to MIDI range
            if self == self.AMP_PAN:
                value = value + 64  # -64 to +63 -> 0 to 127
            elif self in [self.FILTER_KEYFOLLOW, self.AMP_KEYFOLLOW]:
                value = value + 100  # -100 to +100 -> 0 to 200
                value = (value * 127) // 200  # Scale to MIDI range
            elif self == self.OSC_PITCH:
                value = value + 64  # -24 to +24 -> 40 to 88
            elif self == self.OSC_DETUNE:
                value = value + 64  # -50 to +50 -> 14 to 114
            elif self == self.OSC_PITCH_DEPTH:
                value = value + 64  # -63 to +63 -> 0 to 127
            elif self in [
                self.LFO_PITCH,
                self.LFO_FILTER,
                self.LFO_AMP,
                self.LFO_PAN,
                self.MOD_LFO_PITCH,
                self.MOD_LFO_FILTER,
                self.MOD_LFO_AMP,
                self.MOD_LFO_PAN,
                self.MOD_LFO_RATE_CTRL,
            ]:
                value = value + 64  # -63 to +63 -> 0 to 127
            else:
                value = value + 63  # -63 to +63 -> 0 to 126

        # Ensure value is in valid MIDI range
        if value < 0 or value > 127:
            raise ValueError(
                f"MIDI value {value} out of range for {self.name} " f"(must be 0-127)"
            )

        return value

    def convert_from_display(self, display_value: int) -> int:
        """Convert from display value to MIDI value (0-127)"""
        # Handle bipolar parameters
        if self in [
            # Oscillator parameters
            self.OSC_PITCH,
            self.OSC_DETUNE,
            # Filter parameters
            self.FILTER_KEYFOLLOW,
            self.FILTER_VELOCITY,
            self.FILTER_ENV_DEPTH,
            # Amplifier parameters
            self.AMP_VELOCITY,
            self.AMP_PAN,
            self.AMP_KEYFOLLOW,
            # LFO parameters
            self.LFO_PITCH,
            self.LFO_FILTER,
            self.LFO_AMP,
            self.LFO_PAN,
            # Mod LFO parameters
            self.MOD_LFO_PITCH,
            self.MOD_LFO_FILTER,
            self.MOD_LFO_AMP,
            self.MOD_LFO_PAN,
            self.MOD_LFO_RATE_CTRL,
        ]:
            # Convert from display range to MIDI range
            if self == self.AMP_PAN:
                return display_value + 64  # -64 to +63 -> 0 to 127
            elif self in [self.FILTER_KEYFOLLOW, self.AMP_KEYFOLLOW]:
                return display_value + 100  # -100 to +100 -> 0 to 200
            elif self == self.OSC_PITCH:
                return display_value + 64  # -24 to +24 -> 40 to 88
            elif self == self.OSC_DETUNE:
                return display_value + 64  # -50 to +50 -> 14 to 114
            elif self in [
                self.LFO_PITCH,
                self.LFO_FILTER,
                self.LFO_AMP,
                self.LFO_PAN,
                self.MOD_LFO_PITCH,
                self.MOD_LFO_FILTER,
                self.MOD_LFO_AMP,
                self.MOD_LFO_PAN,
                self.MOD_LFO_RATE_CTRL,
            ]:
                return display_value + 64  # -63 to +63 -> 0 to 127
            else:
                return display_value + 63  # -63 to +63 -> 0 to 126

        return display_value

    def get_address_for_partial(self, partial_num: int) -> Tuple[int, int]:
        """Get parameter group and address adjusted for partial number"""
        group = self.group  # Base group already includes 0x20 for Osc1

        # Add partial offset (0x20 for partial 2, 0x40 for partial 3)
        if partial_num == 2:
            group += 0x20
        elif partial_num == 3:
            group += 0x40

        return (group, self.address)

    def __new__(cls, *args):
        obj = object.__new__(cls)
        obj._value_ = args  # Store all values
        return obj

    def __str__(self) -> str:
        return f"{self.name} (addr: {self.address:02X}, range: {self.min_val}-{self.max_val})"

    @property
    def display_name(self) -> str:
        """Get display name for the parameter"""
        return {self.OSC_WAVE_VAR: "Variation"}.get(
            self, self.name.replace("_", " ").title()
        )

    def get_switch_text(self, value: int) -> str:
        """Get display text for switch values"""
        if self == self.OSC_WAVE_VAR:
            return ["A", "B", "C"][value]
        elif self == self.FILTER_MODE:
            return ["BYPASS", "LPF", "HPF", "BPF", "PKG", "LPF2", "LPF3", "LPF4"][value]
        elif self == self.FILTER_SLOPE:
            return ["-12dB", "-24dB"][value]
        elif self == self.MOD_LFO_SHAPE:
            return ["TRI", "SIN", "SAW", "SQR", "S&H", "RND"][value]
        elif self == self.MOD_LFO_SYNC:
            return "ON" if value else "OFF"
        elif self == self.LFO_SHAPE:
            return ["TRI", "SIN", "SAW", "SQR", "S&H", "RND"][value]
        elif self in [self.LFO_SYNC, self.LFO_TRIGGER]:
            return "ON" if value else "OFF"
        elif self == self.WAVE_GAIN:
            return f"{[-6, 0, 6, 12][value]:+d}dB"
        return str(value)

    def get_wave_number(self, midi_helper) -> Optional[int]:
        """Get the full 16-bit wave number value"""
        try:
            # Get all 4 bytes
            b1 = midi_helper.get_parameter(self.WAVE_NUMBER_1)
            b2 = midi_helper.get_parameter(self.WAVE_NUMBER_2)
            b3 = midi_helper.get_parameter(self.WAVE_NUMBER_3)
            b4 = midi_helper.get_parameter(self.WAVE_NUMBER_4)

            if None in (b1, b2, b3, b4):
                return None

            # Combine into 16-bit value
            return (b1 << 12) | (b2 << 8) | (b3 << 4) | b4

        except Exception as e:
            logging.error(f"Error getting wave number: {str(e)}")
            return None

    def set_wave_number(self, midi_helper, value: int) -> bool:
        """Set the 16-bit wave number value

        Args:
            midi_helper: MIDI helper instance
            value: Wave number (0-16384)

        Returns:
            True if successful
        """
        try:
            if not 0 <= value <= 16384:
                raise ValueError(f"Wave number {value} out of range (0-16384)")

            # Split into 4-bit chunks
            b1 = (value >> 12) & 0x0F  # Most significant 4 bits
            b2 = (value >> 8) & 0x0F  # Next 4 bits
            b3 = (value >> 4) & 0x0F  # Next 4 bits
            b4 = value & 0x0F  # Least significant 4 bits

            # Send all 4 bytes
            success = all(
                [
                    midi_helper.send_parameter(self.WAVE_NUMBER_1, b1),
                    midi_helper.send_parameter(self.WAVE_NUMBER_2, b2),
                    midi_helper.send_parameter(self.WAVE_NUMBER_3, b3),
                    midi_helper.send_parameter(self.WAVE_NUMBER_4, b4),
                ]
            )

            return success

        except Exception as e:
            logging.error(f"Error setting wave number: {str(e)}")
            return False


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
    def switch_param(self) -> "DigitalCommonParameter":
        """Get the switch parameter for this partial"""
        if self > 3:  # Structure types are > 3
            raise ValueError("Structure types don't have switch parameters")
        return {
            self.PARTIAL_1: DigitalCommonParameter.PARTIAL1_SWITCH,
            self.PARTIAL_2: DigitalCommonParameter.PARTIAL2_SWITCH,
            self.PARTIAL_3: DigitalCommonParameter.PARTIAL3_SWITCH,
        }[self]

    @property
    def select_param(self) -> "DigitalCommonParameter":
        """Get the select parameter for this partial"""
        if self > 3:  # Structure types are > 3
            raise ValueError("Structure types don't have select parameters")
        return {
            self.PARTIAL_1: DigitalCommonParameter.PARTIAL1_SELECT,
            self.PARTIAL_2: DigitalCommonParameter.PARTIAL2_SELECT,
            self.PARTIAL_3: DigitalCommonParameter.PARTIAL3_SELECT,
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
    def get_partials(cls) -> List["DigitalPartial"]:
        """Get list of partial numbers (not structure types)"""
        return [cls.PARTIAL_1, cls.PARTIAL_2, cls.PARTIAL_3]

    @classmethod
    def get_structures(cls) -> List["DigitalPartial"]:
        """Get list of structure types (not partial numbers)"""
        return [
            cls.SINGLE,
            cls.LAYER_1_2,
            cls.LAYER_2_3,
            cls.LAYER_1_3,
            cls.LAYER_ALL,
            cls.SPLIT_1_2,
            cls.SPLIT_2_3,
            cls.SPLIT_1_3,
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
        "FEEDBACK_OSC": 6,
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
        "PCM Synth",
    ]


# Digital synth preset names
DIGITAL_PRESETS: Tuple[str, ...] = (
    # Bank 1 (1-16)
    "001: Init Tone",
    "002: Saw Lead",
    "003: Square Lead",
    "004: Sine Lead",
    "005: Brass",
    "006: Strings",
    "007: Bell",
    "008: EP",
    "009: Bass",
    "010: Sub Bass",
    "011: Kick",
    "012: Snare",
    "013: Hi-Hat",
    "014: Cymbal",
    "015: Tom",
    "016: Perc",
    # Bank 2 (17-32)
    "017: Pad",
    "018: Sweep",
    "019: Noise",
    "020: FX",
    "021: Pluck",
    "022: Guitar",
    "023: Piano",
    "024: Organ",
    "025: Synth Bass",
    "026: Acid Bass",
    "027: Wobble Bass",
    "028: FM Bass",
    "029: Voice",
    "030: Vocoder",
    "031: Choir",
    "032: Atmosphere",
    # Bank 3 (33-48)
    "033: Lead Sync",
    "034: Unison Lead",
    "035: Stack Lead",
    "036: PWM Lead",
    "037: Dist Lead",
    "038: Filter Lead",
    "039: Mod Lead",
    "040: Seq Lead",
    "041: Brass Sect",
    "042: Strings Ens",
    "043: Orchestra",
    "044: Pizzicato",
    "045: Mallet",
    "046: Crystal",
    "047: Metallic",
    "048: Kalimba",
    # Bank 4 (49-64)
    "049: E.Piano 1",
    "050: E.Piano 2",
    "051: Clav",
    "052: Harpsichord",
    "053: Vibraphone",
    "054: Marimba",
    "055: Xylophone",
    "056: Glocken",
    "057: Nylon Gtr",
    "058: Steel Gtr",
    "059: Jazz Gtr",
    "060: Clean Gtr",
    "061: Muted Gtr",
    "062: Overdrive",
    "063: Dist Gtr",
    "064: Power Gtr",
)

# Digital preset categories
DIGITAL_CATEGORIES = {
    "LEAD": [
        "002: Saw Lead",
        "003: Square Lead",
        "004: Sine Lead",
        "033: Lead Sync",
        "034: Unison Lead",
        "035: Stack Lead",
        "036: PWM Lead",
        "037: Dist Lead",
        "038: Filter Lead",
        "039: Mod Lead",
        "040: Seq Lead",
    ],
    "BASS": [
        "009: Bass",
        "010: Sub Bass",
        "025: Synth Bass",
        "026: Acid Bass",
        "027: Wobble Bass",
        "028: FM Bass",
    ],
    "KEYS": [
        "008: EP",
        "023: Piano",
        "024: Organ",
        "049: E.Piano 1",
        "050: E.Piano 2",
        "051: Clav",
        "052: Harpsichord",
    ],
    "ORCHESTRAL": [
        "006: Strings",
        "041: Brass Sect",
        "042: Strings Ens",
        "043: Orchestra",
        "044: Pizzicato",
    ],
    "PERCUSSION": [
        "007: Bell",
        "011: Kick",
        "012: Snare",
        "013: Hi-Hat",
        "014: Cymbal",
        "015: Tom",
        "016: Perc",
        "045: Mallet",
        "046: Crystal",
        "053: Vibraphone",
        "054: Marimba",
        "055: Xylophone",
        "056: Glocken",
    ],
    "GUITAR": [
        "022: Guitar",
        "057: Nylon Gtr",
        "058: Steel Gtr",
        "059: Jazz Gtr",
        "060: Clean Gtr",
        "061: Muted Gtr",
        "062: Overdrive",
        "063: Dist Gtr",
        "064: Power Gtr",
    ],
    "PAD/ATMOS": [
        "017: Pad",
        "018: Sweep",
        "019: Noise",
        "020: FX",
        "029: Voice",
        "030: Vocoder",
        "031: Choir",
        "032: Atmosphere",
    ],
    "OTHER": [
        "001: Init Tone",
        "005: Brass",
        "021: Pluck",
        "047: Metallic",
        "048: Kalimba",
    ],
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
            self.active_partials = [
                True,
                False,
                False,
            ]  # Only Partial 1 active by default

        if self.partial_params is None:
            self.partial_params = {
                1: self._init_partial_params(),
                2: self._init_partial_params(),
                3: self._init_partial_params(),
            }

    def _init_partial_params(self) -> Dict[str, int]:
        """Initialize parameters for a partial"""
        return {
            "wave": 0,  # SAW
            "pitch": 64,  # Center
            "fine": 64,  # Center
            "pwm": 0,
            "filter_type": 0,  # LPF
            "cutoff": 127,
            "resonance": 0,
            "env_depth": 64,  # Center
            "key_follow": 0,
            "level": 100,
            "pan": 64,  # Center
            "lfo_wave": 0,
            "lfo_rate": 64,
            "lfo_depth": 0,
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

    elif param in [
        DigitalParameter.LFO_TEMPO_NOTE,
        DigitalParameter.MOD_LFO_TEMPO_NOTE,
    ]:
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


def send_digital_parameter(
    midi_helper, param: DigitalParameter, value: int, part: int = 1
):
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
            value=midi_value,
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
            part=PART_1,  # 0x01 for Part 1
            group=group,  # e.g. OSC_PARAM_GROUP
            param=param,  # Parameter number
            value=value,  # Parameter value
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
            part=PART_1,  # 0x01
            group=OSC_1_GROUP,  # 0x20 - OSC 1
            param=OSC_WAVE_PARAM,  # 0x00 - Waveform
            value=waveform,  # e.g. WAVE_SAW (0x00)
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
    TONE_NAME_1 = (0x00, 32, 127)  # ASCII character 1
    TONE_NAME_2 = (0x01, 32, 127)  # ASCII character 2
    TONE_NAME_3 = (0x02, 32, 127)  # ASCII character 3
    TONE_NAME_4 = (0x03, 32, 127)  # ASCII character 4
    TONE_NAME_5 = (0x04, 32, 127)  # ASCII character 5
    TONE_NAME_6 = (0x05, 32, 127)  # ASCII character 6
    TONE_NAME_7 = (0x06, 32, 127)  # ASCII character 7
    TONE_NAME_8 = (0x07, 32, 127)  # ASCII character 8
    TONE_NAME_9 = (0x08, 32, 127)  # ASCII character 9
    TONE_NAME_10 = (0x09, 32, 127)  # ASCII character 10
    TONE_NAME_11 = (0x0A, 32, 127)  # ASCII character 11
    TONE_NAME_12 = (0x0B, 32, 127)  # ASCII character 12

    # Tone level
    TONE_LEVEL = (0x0C, 0, 127)  # Overall tone level

    # Performance parameters
    PORTAMENTO_SW = (0x12, 0, 1)  # Portamento Switch (OFF, ON)
    PORTAMENTO_TIME = (0x13, 0, 127)  # Portamento Time (CC# 5)
    MONO_SW = (0x14, 0, 1)  # Mono Switch (OFF, ON)
    OCTAVE_SHIFT = (0x15, 61, 67)  # Octave Shift (-3 to +3)
    PITCH_BEND_UP = (0x16, 0, 24)  # Pitch Bend Range Up (semitones)
    PITCH_BEND_DOWN = (0x17, 0, 24)  # Pitch Bend Range Down (semitones)

    # Partial switches
    PARTIAL1_SWITCH = (0x19, 0, 1)  # Partial 1 Switch (OFF, ON)
    PARTIAL1_SELECT = (0x1A, 0, 1)  # Partial 1 Select (OFF, ON)
    PARTIAL2_SWITCH = (0x1B, 0, 1)  # Partial 2 Switch (OFF, ON)
    PARTIAL2_SELECT = (0x1C, 0, 1)  # Partial 2 Select (OFF, ON)
    PARTIAL3_SWITCH = (0x1D, 0, 1)  # Partial 3 Switch (OFF, ON)
    PARTIAL3_SELECT = (0x1E, 0, 1)  # Partial 3 Select (OFF, ON)

    # Additional parameters
    RING_SWITCH = (0x1F, 0, 2)  # OFF(0), ---(1), ON(2)
    UNISON_SWITCH = (0x2E, 0, 1)  # OFF, ON
    PORTAMENTO_MODE = (0x31, 0, 1)  # NORMAL, LEGATO
    LEGATO_SWITCH = (0x32, 0, 1)  # OFF, ON
    ANALOG_FEEL = (0x34, 0, 127)  # Analog Feel amount
    WAVE_SHAPE = (0x35, 0, 127)  # Wave Shape amount
    TONE_CATEGORY = (0x36, 0, 127)  # Tone Category
    UNISON_SIZE = (0x3C, 0, 3)  # Unison voice count (2-5 voices)

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
            self.UNISON_SIZE: "Uni Size",
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
            self.LEGATO_SWITCH,
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
            self.PARTIAL3_SELECT: 3,
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
            param = getattr(DigitalCommonParameter, f"TONE_NAME_{i+1}")
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
                value=ascii_val,
            )

        return True

    except Exception as e:
        logging.error(f"Error setting tone name: {str(e)}")
        return False


def set_partial_state(
    midi_helper, partial: DigitalPartial, enabled: bool = True, selected: bool = True
) -> bool:
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
            value=1 if enabled else 0,
        )
        if not success:
            return False

        # Send select state
        return midi_helper.send_parameter(
            area=DIGITAL_SYNTH_AREA,
            part=PART_1,
            group=0x00,
            param=partial.select_param.address,
            value=1 if selected else 0,
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
            param=partial.switch_param.address,
        )

        # Get select state
        select_value = midi_helper.get_parameter(
            area=DIGITAL_SYNTH_AREA,
            part=PART_1,
            group=0x00,
            param=partial.select_param.address,
        )

        # Handle None returns (communication error)
        if switch_value is None or select_value is None:
            return (False, False)

        return (switch_value == 1, select_value == 1)

    except Exception as e:
        logging.error(f"Error getting partial {partial.name} state: {str(e)}")
        return (False, False)
