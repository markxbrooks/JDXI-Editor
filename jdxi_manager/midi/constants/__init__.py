"""Constants for Roland JD-Xi MIDI protocol"""

from enum import auto
from dataclasses import dataclass

from jdxi_manager.midi.sysex.roland import RolandSysEx
from ...data.parameter.program_common import ProgramCommonParameter

# Memory Areas
PROGRAM_AREA = 0x18
DIGITAL_SYNTH_1_AREA = 0x19
DIGITAL_SYNTH_2_AREA = 0x1A
ANALOG_SYNTH_AREA = 0x1B
DRUM_KIT_AREA = 0x1C

MIDI_CHANNEL_DIGITAL1 = 0  # Corresponds to channel 1
MIDI_CHANNEL_DIGITAL2 = 1  # Corresponds to channel 2
MIDI_CHANNEL_ANALOG = 2  # Corresponds to channel 3
MIDI_CHANNEL_DRUMS = 9  # Corresponds to channel 10

# Import specific classes from analog
from .analog import (
    AnalogControlChange,
)

# Import other module constants as needed
from .digital import *
from .drums import *

# from .effects import *
from .vocal_fx import *

# Part Numbers (Legacy names)
PART_1 = 0x00  # Analog synth address
PART_2 = 0x01  # Digital synth 1 address
PART_3 = 0x02  # Digital synth 2 address
PART_4 = 0x03  # Drum address
PART_5 = 0x04  # Vocal FX address

# Part Numbers (New names)
ANALOG_PART = PART_1  # 0x00
DIGITAL_1_PART = PART_2  # 0x01
DIGITAL_2_PART = PART_3  # 0x02
DRUM_PART = PART_4  # 0x03
VOCAL_FX_PART = PART_5  # 0x04
# Part Groups
SUBGROUP_ZERO = 0x00  # Common parameters

# Oscillator Groups
OSC_1_GROUP = 0x20  # Oscillator 1 parameters
OSC_2_GROUP = 0x21  # Oscillator 2 parameters
OSC_COMMON = 0x22  # Common oscillator parameters
OSC_PARAM_GROUP = OSC_1_GROUP  # Legacy name for compatibility

# Filter/Amp Groups
FILTER_GROUP = 0x30  # Filter parameters
AMP_GROUP = 0x31  # Amplifier parameters

# Modulation Groups
LFO_1_GROUP = 0x40  # LFO 1 parameters
LFO_2_GROUP = 0x41  # LFO 2 parameters
ENV_1_GROUP = 0x42  # Envelope 1 parameters
ENV_2_GROUP = 0x43  # Envelope 2 parameters

# Effects Groups
FX_GROUP = 0x50  # Effects parameters
DELAY_GROUP = 0x51  # Delay parameters
REVERB_GROUP = 0x52  # Reverb parameters

# Bank Select Values
ANALOG_BANK_MSB = 0x5E  # 94 - Analog synth
DIGITAL_BANK_MSB = 0x5F  # 95 - Digital synth
DRUM_BANK_MSB = 0x56  # 86 - Drum kit

PRESET_BANK_LSB = 0x00  # 0 - Preset bank 1
PRESET_BANK_2_LSB = 0x01  # 1 - Preset bank 2 (Digital only)
USER_BANK_LSB = 0x10  # 16 - User bank

# MIDI Control Change messages
BANK_SELECT_MSB = 0x00  # CC 0
BANK_SELECT_LSB = 0x20  # CC 32
PROGRAM_CHANGE = 0xC0  # Program Change

# SysEx Headers
START_OF_SYSEX = 0xF0
END_OF_SYSEX = 0xF7
ROLAND_ID = 0x41
DEVICE_ID = 0x10

# Model ID bytes
MODEL_ID_1 = 0x00  # Manufacturer ID extension
MODEL_ID_2 = 0x00  # Device family code MSB
MODEL_ID_3 = 0x00  # Device family code LSB
MODEL_ID_4 = 0x0E  # Product code

# Full Model ID array
MODEL_ID = [MODEL_ID_1, MODEL_ID_2, MODEL_ID_3, MODEL_ID_4]

# Device Identification
JD_XI_HEADER = [
    ROLAND_ID,
    MODEL_ID_1,
    MODEL_ID_2,
    MODEL_ID_3,
    MODEL_ID_4,
]  # Complete device ID

# SysEx Commands
RQ1_COMMAND = 0x11  # Data Request 1
DT1_COMMAND = 0x12  # Data Set 1
RQ2_COMMAND = 0x41  # Data Request 2
DT2_COMMAND = 0x42  # Data Set 2
ERR_COMMAND = 0x4E  # Error
ACK_COMMAND = 0x4F  # Acknowledgment

# Roland Commands
DT1_COMMAND_12 = 0x12  # Data Set 1
RQ1_COMMAND_11 = 0x11  # Data Request 1

# Analog Filter Parameters
ANALOG_FILTER_SWITCH = 0x20  # Filter switch (0-1: BYPASS, LPF)
ANALOG_FILTER_CUTOFF = 0x21  # Filter cutoff frequency (0-127)
ANALOG_FILTER_KEYFOLLOW = 0x22  # Cutoff keyfollow (54-74: -100 to +100)
ANALOG_FILTER_RESONANCE = 0x23  # Filter resonance (0-127)
ANALOG_FILTER_ENV_VELO = 0x24  # Env velocity sens (1-127: -63 to +63)
ANALOG_FILTER_ENV_A = 0x25  # Filter env attack time (0-127)
ANALOG_FILTER_ENV_D = 0x26  # Filter env decay time (0-127)
ANALOG_FILTER_ENV_S = 0x27  # Filter env sustain level (0-127)
ANALOG_FILTER_ENV_R = 0x28  # Filter env release time (0-127)
ANALOG_FILTER_ENV_DEPTH = 0x29  # Filter env depth (1-127: -63 to +63)

# Filter Modes
FILTER_MODE_BYPASS = 0x00  # Bypass filter
FILTER_MODE_LPF = 0x01  # Low-pass filter

# Oscillator Parameters
OSC_WAVE_PARAM = 0x00  # Waveform selection
OSC_RANGE_PARAM = 0x01  # Octave range
OSC_COARSE_PARAM = 0x02  # Coarse tune
OSC_FINE_PARAM = 0x03  # Fine tune
OSC_PW_PARAM = 0x04  # Pulse width
OSC_PWM_PARAM = 0x05  # PWM depth
OSC_SYNC_PARAM = 0x06  # Oscillator sync
OSC_RING_PARAM = 0x07  # Ring modulation

# Oscillator Waveforms
OSC_WAVE_SAW = 0x00  # Sawtooth
OSC_WAVE_SQUARE = 0x01  # Square
OSC_WAVE_TRIANGLE = 0x02  # Triangle
OSC_WAVE_SINE = 0x03  # Sine
OSC_WAVE_NOISE = 0x04  # Noise
OSC_WAVE_SUPER_SAW = 0x05  # Super saw
OSC_WAVE_PCM = 0x06  # PCM waveform

# Legacy Waveform Constants (for backward compatibility)
WAVE_SAW = OSC_WAVE_SAW  # Sawtooth
WAVE_SQUARE = OSC_WAVE_SQUARE  # Square
WAVE_PULSE = OSC_WAVE_SQUARE  # Pulse (same as square)
WAVE_TRIANGLE = OSC_WAVE_TRIANGLE  # Triangle
WAVE_SINE = OSC_WAVE_SINE  # Sine
WAVE_NOISE = OSC_WAVE_NOISE  # Noise
WAVE_SUPER_SAW = OSC_WAVE_SUPER_SAW  # Super saw
WAVE_PCM = OSC_WAVE_PCM  # PCM waveform

# Oscillator Ranges
OSC_RANGE_16 = 0x00  # 16'
OSC_RANGE_8 = 0x01  # 8'
OSC_RANGE_4 = 0x02  # 4'
OSC_RANGE_2 = 0x03  # 2'

# Legacy Range Constants
RANGE_16 = OSC_RANGE_16  # 16'
RANGE_8 = OSC_RANGE_8  # 8'
RANGE_4 = OSC_RANGE_4  # 4'
RANGE_2 = OSC_RANGE_2  # 2'

# Parameter Ranges
OSC_COARSE_RANGE = (-24, 24)  # Semitones
OSC_FINE_RANGE = (-50, 50)  # Cents
OSC_PW_RANGE = (0, 127)  # Pulse width
OSC_PWM_RANGE = (0, 127)  # PWM depth
OSC_SYNC_RANGE = (0, 1)  # Off/On
OSC_RING_RANGE = (0, 1)  # Off/On


class DrumKitCC:
    """Drum Kit Control Change parameters"""

    # MSB values for NRPN parameters
    LEVEL_MSB = 0x1A  # Level
    PAN_MSB = 0x1C  # Pan
    TUNE_MSB = 0x1E  # Tune
    DECAY_MSB = 0x20  # Decay
    CUTOFF_MSB = 0x22  # Cutoff Frequency
    RESONANCE_MSB = 0x24  # Resonance
    FX1_SEND_MSB = 0x26  # Effect 1 Send Level
    FX2_SEND_MSB = 0x28  # Effect 2 Send Level
    DELAY_SEND_MSB = 0x2A  # Delay Send Level
    REVERB_SEND_MSB = 0x2C  # Reverb Send Level

    # Value ranges
    LEVEL_RANGE = (0, 127)
    PAN_RANGE = (0, 127)  # 0=Left, 64=Center, 127=Right
    TUNE_RANGE = (0, 127)  # 64=Original pitch
    DECAY_RANGE = (0, 127)
    CUTOFF_RANGE = (0, 127)
    RESONANCE_RANGE = (0, 127)
    SEND_RANGE = (0, 127)

    @staticmethod
    def validate_msb(msb: int) -> bool:
        """Validate MSB value"""
        return msb in [
            DrumKitCC.LEVEL_MSB,
            DrumKitCC.PAN_MSB,
            DrumKitCC.TUNE_MSB,
            DrumKitCC.DECAY_MSB,
            DrumKitCC.CUTOFF_MSB,
            DrumKitCC.RESONANCE_MSB,
            DrumKitCC.FX1_SEND_MSB,
            DrumKitCC.FX2_SEND_MSB,
            DrumKitCC.DELAY_SEND_MSB,
            DrumKitCC.REVERB_SEND_MSB,
        ]

    @staticmethod
    def validate_note(note: int) -> bool:
        """Validate drum note number"""
        return 36 <= note <= 72  # C2 to C5

    @staticmethod
    def validate_value(value: int) -> bool:
        """Validate parameter value"""
        return 0 <= value <= 127


class AnalogToneCC:
    """Analog Synth Control Change parameters"""

    # Common Parameters
    LEVEL_MSB = 0x10  # Level
    PAN_MSB = 0x11  # Pan
    PORTAMENTO_MSB = 0x12  # Portamento time

    # Oscillator Parameters
    OSC_WAVE_MSB = 0x20  # Waveform
    OSC_RANGE_MSB = 0x21  # Octave range
    OSC_COARSE_MSB = 0x22  # Coarse tune
    OSC_FINE_MSB = 0x23  # Fine tune
    OSC_PW_MSB = 0x24  # Pulse width

    # Filter Parameters
    FILT_TYPE_MSB = 0x30  # Filter preset_type
    FILT_CUTOFF_MSB = 0x31  # Cutoff frequency
    FILT_RESO_MSB = 0x32  # Resonance
    FILT_ENV_MSB = 0x33  # Envelope depth
    FILT_KEY_MSB = 0x34  # Key follow

    # Envelope Parameters
    FILT_A_MSB = 0x40  # Filter Attack
    FILT_D_MSB = 0x41  # Filter Decay
    FILT_S_MSB = 0x42  # Filter Sustain
    FILT_R_MSB = 0x43  # Filter Release

    AMP_A_MSB = 0x50  # Amp Attack
    AMP_D_MSB = 0x51  # Amp Decay
    AMP_S_MSB = 0x52  # Amp Sustain
    AMP_R_MSB = 0x53  # Amp Release

    # LFO Parameters
    LFO_WAVE_MSB = 0x60  # LFO Waveform
    LFO_RATE_MSB = 0x61  # LFO Rate
    LFO_DEPTH_MSB = 0x62  # LFO Depth
    LFO_DEST_MSB = 0x63  # LFO Destination

    # Value ranges
    LEVEL_RANGE = (0, 127)
    PAN_RANGE = (0, 127)  # 0=Left, 64=Center, 127=Right
    PORTA_RANGE = (0, 127)
    WAVE_RANGE = (0, 6)  # See OSC_WAVE_* constants
    RANGE_RANGE = (0, 3)  # See OSC_RANGE_* constants
    COARSE_RANGE = (40, 88)  # -24 to +24 semitones
    FINE_RANGE = (14, 114)  # -50 to +50 cents
    PW_RANGE = (0, 127)
    FILTER_RANGE = (0, 127)
    ENV_RANGE = (0, 127)
    LFO_RANGE = (0, 127)

    @staticmethod
    def validate_msb(msb: int) -> bool:
        """Validate MSB value"""
        return msb in [
            AnalogControlChange.LEVEL_MSB,
            AnalogControlChange.PAN_MSB,
            AnalogControlChange.PORTAMENTO_MSB,
            AnalogControlChange.OSC_WAVE_MSB,
            AnalogControlChange.OSC_RANGE_MSB,
            AnalogControlChange.OSC_COARSE_MSB,
            AnalogControlChange.OSC_FINE_MSB,
            AnalogControlChange.OSC_PW_MSB,
            AnalogControlChange.FILT_TYPE_MSB,
            AnalogControlChange.FILT_CUTOFF_MSB,
            AnalogControlChange.FILT_RESO_MSB,
            AnalogControlChange.FILT_ENV_MSB,
            AnalogControlChange.FILT_KEY_MSB,
            AnalogControlChange.FILT_A_MSB,
            AnalogControlChange.FILT_D_MSB,
            AnalogControlChange.FILT_S_MSB,
            AnalogControlChange.FILT_R_MSB,
            AnalogControlChange.AMP_A_MSB,
            AnalogControlChange.AMP_D_MSB,
            AnalogControlChange.AMP_S_MSB,
            AnalogControlChange.AMP_R_MSB,
            AnalogControlChange.LFO_WAVE_MSB,
            AnalogControlChange.LFO_RATE_MSB,
            AnalogControlChange.LFO_DEPTH_MSB,
            AnalogControlChange.LFO_DEST_MSB,
        ]

    @staticmethod
    def validate_value(msb: int, value: int) -> bool:
        """Validate parameter value based on MSB"""
        if msb == AnalogControlChange.OSC_WAVE_MSB:
            return 0 <= value <= 6
        elif msb == AnalogControlChange.OSC_RANGE_MSB:
            return 0 <= value <= 3
        elif msb == AnalogControlChange.OSC_COARSE_MSB:
            return 40 <= value <= 88
        elif msb == AnalogControlChange.OSC_FINE_MSB:
            return 14 <= value <= 114
        else:
            return 0 <= value <= 127


class Waveform(Enum):
    """Waveform types available on the JD-Xi"""

    SAW = auto()  # Sawtooth wave
    SQUARE = auto()  # Square wave
    TRIANGLE = auto()  # Triangle wave
    SINE = auto()  # Sine wave
    NOISE = auto()  # Noise
    SUPER_SAW = auto()  # Super saw
    PCM = auto()  # PCM waveform

    @property
    def display_name(self) -> str:
        """Get display name for waveform"""
        return self.name.replace("_", " ").title()

    @property
    def midi_value(self) -> int:
        """Get MIDI value for waveform"""
        return {
            Waveform.SAW: OSC_WAVE_SAW,
            Waveform.SQUARE: OSC_WAVE_SQUARE,
            Waveform.TRIANGLE: OSC_WAVE_TRIANGLE,
            Waveform.SINE: OSC_WAVE_SINE,
            Waveform.NOISE: OSC_WAVE_NOISE,
            Waveform.SUPER_SAW: OSC_WAVE_SUPER_SAW,
            Waveform.PCM: OSC_WAVE_PCM,
        }[self]

    @classmethod
    def from_midi_value(cls, value: int) -> "Waveform":
        """Create Waveform from MIDI value"""
        for waveform in cls:
            if waveform.midi_value == value:
                return waveform
        raise ValueError(f"Invalid waveform value: {value}")

# Analog LFO Sync Note Values
ANALOG_LFO_SYNC_NOTES = [
    "16",  # 0
    "12",  # 1
    "8",  # 2
    "4",  # 3
    "2",  # 4
    "1",  # 5
    "3/4",  # 6
    "2/3",  # 7
    "1/2",  # 8
    "3/8",  # 9
    "1/3",  # 10
    "1/4",  # 11
    "3/16",  # 12
    "1/6",  # 13
    "1/8",  # 14
    "3/32",  # 15
    "1/12",  # 16
    "1/16",  # 17
    "1/24",  # 18
    "1/32",  # 19
]

# JD-Xi Memory Map Areas
SETUP_AREA = 0x01  # 01 00 00 00: Setup
SYSTEM_AREA = 0x02  # 02 00 00 00: System

# Synth Areas
DIGITAL_SYNTH_1 = 0x19  # 19 00 00 00: Digital Synth Part 1
DIGITAL_SYNTH_2 = 0x19  # 19 20 00 00: Digital Synth Part 2
ANALOG_SYNTH = 0x19  # 19 40 00 00: Analog Synth Part
DRUM_KIT = 0x19  # 19 60 00 00: Drums Part

# Part Offsets
DIGITAL_PART_1 = 0x01  # Digital Synth 1 offset
DIGITAL_PART_2 = 0x02  # Digital Synth 2 offset

# Roland Device IDs
ROLAND_ID = 0x41
MODEL_ID_1 = 0x00
MODEL_ID_2 = 0x00
MODEL_ID_3 = 0x00



# Memory areas
COMMON_AREA = 0x00

# Part numbers
PART_1 = 0x01  # Part 1

# Parameter Groups
OSC_1_GROUP = 0x20  # Oscillator 1 parameters
PARTIAL_GROUP = 0x24  # Partial parameters

# Digital Synth Parameters
# Partial Parameters (0x19-0x1F)
PARTIAL_1_SWITCH = 0x19  # Partial 1 on/off (0-1)
PARTIAL_1_SELECT = 0x1A  # Partial 1 select (0-1)
PARTIAL_2_SWITCH = 0x1B  # Partial 2 on/off (0-1)
PARTIAL_2_SELECT = 0x1C  # Partial 2 select (0-1)
PARTIAL_3_SWITCH = 0x1D  # Partial 3 on/off (0-1)
PARTIAL_3_SELECT = 0x1E  # Partial 3 select (0-1)
RING_SWITCH = 0x1F  # Ring modulation (0=OFF, 1=---, 2=ON)

# Effects Parameters (0x40-0x4F)
REVERB_SEND_PARAM = 0x40  # Reverb send level (0-127)
DELAY_SEND_PARAM = 0x41  # Delay send level (0-127)
EFFECTS_SEND_PARAM = 0x42  # Effects send level (0-127)


# Effects Types
class EffectType(Enum):
    """Effect types for JD-Xi"""

    # Reverb Types (0-7)
    ROOM1 = 0
    ROOM2 = 1
    STAGE1 = 2
    STAGE2 = 3
    HALL1 = 4
    HALL2 = 5
    PLATE = 6
    SPRING = 7

    # Delay Types (0-4)
    STEREO = 0
    PANNING = 1
    MONO = 2
    TAPE_ECHO = 3
    MOD_DELAY = 4

    # FX Types (0-12)
    DISTORTION = 0
    FUZZ = 1
    COMPRESSOR = 2
    BITCRUSHER = 3
    EQUALIZER = 4
    PHASER = 5
    FLANGER = 6
    CHORUS = 7
    TREMOLO = 8
    AUTOPAN = 9
    SLICER = 10
    RING_MOD = 11
    ISOLATOR = 12

    @staticmethod
    def get_display_name(value: int, effect_type: str) -> str:
        """Get display name for effect preset_type"""
        names = {
            "reverb": {
                0: "Room 1",
                1: "Room 2",
                2: "Stage 1",
                3: "Stage 2",
                4: "Hall 1",
                5: "Hall 2",
                6: "Plate",
                7: "Spring",
            },
            "delay": {
                0: "Stereo",
                1: "Panning",
                2: "Mono",
                3: "Tape Echo",
                4: "Mod Delay",
            },
            "fx": {
                0: "Distortion",
                1: "Fuzz",
                2: "Compressor",
                3: "Bitcrusher",
                4: "Equalizer",
                5: "Phaser",
                6: "Flanger",
                7: "Chorus",
                8: "Tremolo",
                9: "Auto Pan",
                10: "Slicer",
                11: "Ring Mod",
                12: "Isolator",
            },
        }
        return names.get(effect_type, {}).get(value, "???")


DIGITAL_SYNTH_1 = 0x19  # Digital synth 1 area
DIGITAL_SYNTH_2 = 0x1A  # Digital synth 2 area
ANALOG_SYNTH_AREA = 0x18  # Analog synth area
DRUM_KIT_AREA = 0x17  # Drum kit area
EFFECTS_AREA = 0x16  # Effects area
ARPEGGIO_AREA = 0x15  # Arpeggiator area
VOCAL_FX_AREA = 0x14  # Vocal effects area
SYSTEM_AREA = 0x01  # System settings area

# Part numbers
DIGITAL_PART_1 = 0x01  # Digital synth 1 address
DIGITAL_PART_2 = 0x02  # Digital synth 2 address
ANALOG_PART = 0x00  # Analog synth address
DRUM_PART = 0x00  # Drum address
VOCAL_PART = 0x00  # Vocal address
SYSTEM_PART = 0x00  # System address

# Parameter groups
PROGRAM_GROUP = 0x00
COMMON_GROUP = 0x10
PARTIAL_GROUP = 0x20
EFFECTS_GROUP = 0x30


class DrumPad(Enum):
    """Drum pad numbers and parameters"""

    # Pad numbers
    PAD_1 = 0x00
    PAD_2 = 0x01
    PAD_3 = 0x02
    PAD_4 = 0x03
    PAD_5 = 0x04
    PAD_6 = 0x05
    PAD_7 = 0x06
    PAD_8 = 0x07
    PAD_9 = 0x08
    PAD_10 = 0x09
    PAD_11 = 0x0A
    PAD_12 = 0x0B
    PAD_13 = 0x0C
    PAD_14 = 0x0D
    PAD_15 = 0x0E
    PAD_16 = 0x0F

    # Pad parameters
    WAVE = 0x00
    LEVEL = 0x01
    PAN = 0x02
    TUNE = 0x03
    DECAY = 0x04
    MUTE_GROUP = 0x05
    REVERB_SEND = 0x06
    DELAY_SEND = 0x07
    FX_SEND = 0x08


# Digital synth parameter offsets
OSC_PARAM_GROUP = 0x20
LFO_PARAM_GROUP = 0x40
ENV_PARAM_GROUP = 0x60

# Subgroups
SUBGROUP_ZERO = 0x00


class Waveform(Enum):
    """Waveform types available on JD-Xi"""

    SAW = 0x00  # Sawtooth wave
    SQUARE = 0x01  # Square wave
    PW_SQUARE = 0x02  # Pulse width square wave
    TRIANGLE = 0x03  # Triangle wave
    SINE = 0x04  # Sine wave
    NOISE = 0x05  # Noise
    SUPER_SAW = 0x06  # Super saw
    PCM = 0x07  # PCM waveform


class ArpeggioGroup(Enum):
    """Arpeggiator parameter groups"""

    COMMON = 0x00  # Common parameters
    PATTERN = 0x10  # Pattern parameters
    RHYTHM = 0x20  # Rhythm parameters
    NOTE = 0x30  # Note parameters


class DigitalGroup(Enum):
    """Digital synth parameter groups"""

    COMMON = 0x00  # Common parameters
    PARTIAL = 0x20  # Partial parameters
    LFO = 0x40  # LFO parameters
    ENV = 0x60  # Envelope parameters


class EffectGroup(Enum):
    """Effect parameter groups"""

    COMMON = 0x00  # Common parameters
    INSERT = 0x10  # Insert effect parameters
    REVERB = 0x20  # Reverb parameters
    DELAY = 0x30  # Delay parameters


class FilterMode(Enum):
    """Filter modes available on JD-Xi"""

    BYPASS = 0x00
    LPF = 0x01  # Low Pass Filter
    HPF = 0x02  # High Pass Filter
    BPF = 0x03  # Band Pass Filter
    PKG = 0x04  # Peaking Filter
    LPF2 = 0x05  # Low Pass Filter 2
    LPF3 = 0x06  # Low Pass Filter 3
    LPF4 = 0x07  # Low Pass Filter 4


class DigitalPartial:
    """Digital synth partial constants"""

    class Offset(Enum):
        """Partial parameter offsets"""

        PARTIAL_1 = 0x00
        PARTIAL_2 = 0x20  # Offset between partials
        PARTIAL_3 = 0x40

    class CC(Enum):
        """Control change numbers for partial parameters"""

        # Oscillator parameters (0x00-0x09)
        OSC_WAVE = (
            0x00  # Wave (0-7: SAW, SQR, PW-SQR, TRI, SINE, NOISE, SUPER-SAW, PCM)
        )
        OSC_VARIATION = 0x01  # Wave Variation (0-2: A, B, C)
        OSC_RESERVE = 0x02  # Reserved
        OSC_PITCH = 0x03  # Pitch (40-88: -24 to +24)
        OSC_DETUNE = 0x04  # Detune (14-114: -50 to +50)
        OSC_PWM_DEPTH = 0x05  # Pulse Width Mod Depth (0-127)
        OSC_PW = 0x06  # Pulse Width (0-127)
        OSC_PITCH_A = 0x07  # Pitch Env Attack Time (0-127)
        OSC_PITCH_D = 0x08  # Pitch Env Decay (0-127)
        OSC_PITCH_DEPTH = 0x09  # Pitch Env Depth (1-127)

        # Filter parameters (0x0A-0x14)
        FILTER_MODE = (
            0x0A  # Filter mode (0-7: BYPASS, LPF, HPF, BPF, PKG, LPF2, LPF3, LPF4)
        )
        FILTER_SLOPE = 0x0B  # Filter slope (0-1: -12dB, -24dB)
        FILTER_CUTOFF = 0x0C  # Filter cutoff frequency (0-127)
        FILTER_CUTOFF_KEYFOLLOW = 0x0D  # Cutoff keyfollow (54-74: -100 to +100)
        FILTER_VELO = 0x0E  # Env velocity sensitivity (1-127: -63 to +63)
        FILTER_RESO = 0x0F  # Resonance (0-127)
        FILTER_ATTACK = 0x10  # Env attack time (0-127)
        FILTER_DECAY = 0x11  # Env decay time (0-127)
        FILTER_SUSTAIN = 0x12  # Env sustain level (0-127)
        FILTER_RELEASE = 0x13  # Env release time (0-127)
        FILTER_ENV_DEPTH = 0x14  # Env depth (1-127: -63 to +63)

        # Amplifier parameters (0x15-0x1B)
        AMP_LEVEL = 0x15  # Level (0-127)
        AMP_VELO = 0x16  # Level Velocity Sensitivity (1-127: -63 to +63)
        AMP_ATTACK = 0x17  # Env Attack Time (0-127)
        AMP_DECAY = 0x18  # Env Decay Time (0-127)
        AMP_SUSTAIN = 0x19  # Env Sustain Level (0-127)
        AMP_RELEASE = 0x1A  # Env Release Time (0-127)
        AMP_PAN = 0x1B  # Pan (0-127: L64-63R)

        # LFO parameters (0x1C-0x25)
        LFO_SHAPE = 0x1C  # LFO Shape (0-5: TRI, SIN, SAW, SQR, S&H, RND)
        LFO_RATE = 0x1D  # Rate (0-127)
        LFO_SYNC_SW = 0x1E  # Tempo Sync Switch (0-1: OFF, ON)
        LFO_SYNC_NOTE = 0x1F  # Tempo Sync Note (0-19: 16,12,8,4,2,1,3/4,...)
        LFO_FADE = 0x20  # Fade Time (0-127)
        LFO_KEY_TRIG = 0x21  # Key Trigger (0-1: OFF, ON)
        LFO_PITCH = 0x22  # Pitch Depth (1-127: -63 to +63)
        LFO_FILTER = 0x23  # Filter Depth (1-127: -63 to +63)
        LFO_AMP = 0x24  # Amp Depth (1-127: -63 to +63)
        LFO_PAN = 0x25  # Pan Depth (1-127: -63 to +63)

        # Envelope parameters (0x40-0x4F)
        ENV_ATTACK = 0x40  # Attack time
        ENV_DECAY = 0x41  # Decay time
        ENV_SUSTAIN = 0x42  # Sustain level
        ENV_RELEASE = 0x43  # Release time
        ENV_KEY = 0x44  # Key follow
        ENV_VELO = 0x45  # Velocity sensitivity

        # Oscillator parameters (0x34-0x3C)
        OSC_GAIN = 0x34  # Wave Gain (0-3: -6, 0, +6, +12 dB)
        OSC_WAVE_NUM = 0x35  # Wave Number (0-16384: OFF, 1-16384)
        HPF_CUTOFF = 0x39  # HPF Cutoff (0-127)
        SUPER_SAW = 0x3A  # Super Saw Detune (0-127)
        MOD_LFO_RATE = 0x3B  # Modulation LFO Rate Control (1-127: -63 to +63)
        AMP_KEYFOLLOW = 0x3C  # AMP Level Keyfollow (54-74: -100 to +100)

        # Aftertouch parameters (0x30-0x31)
        CUTOFF_AFTERTOUCH = 0x30  # Cutoff Aftertouch Sensitivity (1-127: -63 to +63)
        LEVEL_AFTERTOUCH = 0x31  # Level Aftertouch Sensitivity (1-127: -63 to +63)


class EffectType(Enum):
    """Effect types and parameters"""

    # Effect types
    THRU = 0x00
    DISTORTION = 0x01
    FUZZ = 0x02
    COMPRESSOR = 0x03
    BITCRUSHER = 0x04
    FLANGER = 0x05
    PHASER = 0x06
    RING_MOD = 0x07
    SLICER = 0x08

    # Common parameters
    LEVEL = 0x00
    MIX = 0x01

    # Effect-specific parameters
    DRIVE = 0x10
    TONE = 0x11
    ATTACK = 0x12
    RELEASE = 0x13
    THRESHOLD = 0x14
    RATIO = 0x15
    BIT_DEPTH = 0x16
    RATE = 0x17
    DEPTH = 0x18
    FEEDBACK = 0x19
    FREQUENCY = 0x1A
    BALANCE = 0x1B
    PATTERN = 0x1C

    # Send levels
    REVERB_SEND = 0x20
    DELAY_SEND = 0x21
    CHORUS_SEND = 0x22

    # Reverb parameters
    REVERB_TYPE = 0x30
    REVERB_TIME = 0x31
    REVERB_PRE_DELAY = 0x32

    # Delay parameters
    DELAY_TIME = 0x40
    DELAY_FEEDBACK = 0x41
    DELAY_HF_DAMP = 0x42

    # Chorus parameters
    CHORUS_RATE = 0x50
    CHORUS_DEPTH = 0x51
    CHORUS_FEEDBACK = 0x52


class VocalFX(Enum):
    """Vocal effects types and parameters"""

    # Effect types
    VOCODER = 0x00
    AUTO_PITCH = 0x01
    HARMONIST = 0x02

    # Common parameters
    LEVEL = 0x00
    PAN = 0x01
    REVERB_SEND = 0x02
    DELAY_SEND = 0x03

    # Vocoder parameters
    MIC_SENS = 0x10
    CARRIER_MIX = 0x11
    FORMANT = 0x12
    CUTOFF = 0x13
    RESONANCE = 0x14

    # Auto-Pitch parameters
    SCALE = 0x20
    KEY = 0x21
    GENDER = 0x22
    BALANCE = 0x23

    # Harmonist parameters
    HARMONY_1 = 0x30
    HARMONY_2 = 0x31
    HARMONY_3 = 0x32
    DETUNE = 0x33


class VoiceCutoffFilter(Enum):
    """Voice cutoff filter types"""

    THRU = 0x00
    LPF = 0x01
    HPF = 0x02
    BPF = 0x03


class VoiceScale(Enum):
    """Voice scale types"""

    CHROMATIC = 0x00
    MAJOR = 0x01
    MINOR = 0x02
    BLUES = 0x03
    INDIAN = 0x04


class VoiceKey(Enum):
    """Voice keys"""

    C = 0x00
    Db = 0x01
    D = 0x02
    Eb = 0x03
    E = 0x04
    F = 0x05
    Gb = 0x06
    G = 0x07
    Ab = 0x08
    A = 0x09
    Bb = 0x0A
    B = 0x0B


class ArpGrid(Enum):
    """Arpeggio grid values"""

    GRID_4 = 0  # 04_
    GRID_8 = 1  # 08_
    GRID_8L = 2  # 08L
    GRID_8H = 3  # 08H
    GRID_8T = 4  # 08t
    GRID_16 = 5  # 16_
    GRID_16L = 6  # 16L
    GRID_16H = 7  # 16H
    GRID_16T = 8  # 16t


class ArpDuration(Enum):
    """Arpeggio duration values"""

    DUR_30 = 0  # 30%
    DUR_40 = 1  # 40%
    DUR_50 = 2  # 50%
    DUR_60 = 3  # 60%
    DUR_70 = 4  # 70%
    DUR_80 = 5  # 80%
    DUR_90 = 6  # 90%
    DUR_100 = 7  # 100%
    DUR_120 = 8  # 120%
    DUR_FULL = 9  # FULL


class ArpMotif(Enum):
    """Arpeggio motif values"""

    UP_L = 0  # UP/L
    UP_H = 1  # UP/H
    UP_NORM = 2  # UP/_
    DOWN_L = 3  # dn/L
    DOWN_H = 4  # dn/H
    DOWN_NORM = 5  # dn/_
    UP_DOWN_L = 6  # Ud/L
    UP_DOWN_H = 7  # Ud/H
    UP_DOWN_NORM = 8  # Ud/_
    RANDOM_L = 9  # rn/L
    RANDOM_NORM = 10  # rn/_
    PHRASE = 11  # PHRASE


class ArpParameters(Enum):
    """Arpeggiator parameters"""

    GRID = 0x01  # Grid (0-8)
    DURATION = 0x02  # Duration (0-9)
    SWITCH = 0x03  # On/Off (0-1)
    STYLE = 0x05  # Style (0-127)
    MOTIF = 0x06  # Motif (0-11)
    OCTAVE = 0x07  # Octave Range (61-67: -3 to +3)
    ACCENT = 0x09  # Accent Rate (0-100)
    VELOCITY = 0x0A  # Velocity (0-127, 0=REAL)


# SuperNATURAL presets for each address
DIGITAL_SN_PRESETS = [
    "001: JP8 Strings1",
    "002: Soft Pad 1",
    "003: JP8 Strings2",
    "004: JUNO Str 1",
    "005: Oct Strings",
    "006: Brite Str 1",
    "007: Boreal Pad",
    "008: JP8 Strings3",
    "009: JP8 Strings4",
    "010: Hollow Pad 1",
    "011: LFO Pad 1",
    "012: Hybrid Str",
    "013: Awakening 1",
    "014: Cincosoft 1",
    "015: Bright Pad 1",
    "016: Analog Str 1",
    "017: Soft ResoPd1",
    "018: HPF Poly 1",
    "019: BPF Poly",
    "020: Sweep Pad 1",
    "021: Soft Pad 2",
    "022: Sweep JD 1",
    "023: FltSweep Pd1",
    "024: HPF Pad",
    "025: HPF SweepPd1",
    "026: KOff Pad",
    "027: Sweep Pad 2",
    "028: TrnsSweepPad",
    "029: Revalation 1",
    "030: LFO CarvePd1",
    "031: RETROX 139 1",
    "032: LFO ResoPad1",
    "033: PLS Pad 1",
    "034: PLS Pad 2",
    "035: Trip 2 Mars1",
    "036: Reso S&H Pd1",
    "037: SideChainPd1",
    "038: PXZoon 1",
    "039: Psychoscilo1",
    "040: Fantasy 1",
    "041: D-50 Stack 1",
    "042: Organ Pad",
    "043: Bell Pad",
    "044: Dreaming 1",
    "045: Syn Sniper 1",
    "046: Strings 1",
    "047: D-50 Pizz 1",
    "048: Super Saw 1",
    "049: S-SawStacLd1",
    "050: Tekno Lead 1",
    "051: Tekno Lead 2",
    "052: Tekno Lead 3",
    "053: OSC-SyncLd 1",
    "054: WaveShapeLd1",
    "055: JD RingMod 1",
    "056: Buzz Lead 1",
    "057: Buzz Lead 2",
    "058: SawBuzz Ld 1",
    "059: Sqr Buzz Ld1",
    "060: Tekno Lead 4",
    "061: Dist Flt TB1",
    "062: Dist TB Sqr1",
    "063: Glideator 1",
    "064: Vintager 1",
    "065: Hover Lead 1",
    "066: Saw Lead 1",
    "067: Saw+Tri Lead",
    "068: PortaSaw Ld1",
    "069: Reso Saw Ld",
    "070: SawTrap Ld 1",
    "071: Fat GR Lead",
    "072: Pulstar Ld",
    "073: Slow Lead",
    "074: AnaVox Lead",
    "075: Square Ld 1",
    "076: Square Ld 2",
    "077: Sqr Lead 1",
    "078: Sqr Trap Ld1",
    "079: Sine Lead 1",
    "080: Tri Lead",
    "081: Tri Stac Ld1",
    "082: 5th SawLead1",
    "083: Sweet 5th 1",
    "084: 4th Syn Lead",
    "085: Maj Stack Ld",
    "086: MinStack Ld1",
    "087: Chubby Lead1",
    "088: CuttingLead1",
    "089: Seq Bass 1",
    "090: Reso Bass 1",
    "091: TB Bass 1",
    "092: 106 Bass 1",
    "093: FilterEnvBs1",
    "094: JUNO Sqr Bs1",
    "095: Reso Bass 2",
    "096: JUNO Bass",
    "097: MG Bass 1",
    "098: 106 Bass 3",
    "099: Reso Bass 3",
    "100: Detune Bs 1",
    "101: MKS-50 Bass1",
    "102: Sweep Bass",
    "103: MG Bass 2",
    "104: MG Bass 3",
    "105: ResRubber Bs",
    "106: R&B Bass 1",
    "107: Reso Bass 4",
    "108: Wide Bass 1",
    "109: Chow Bass 1",
    "110: Chow Bass 2",
    "111: SqrFilterBs1",
    "112: Reso Bass 5",
    "113: Syn Bass 1",
    "114: ResoSawSynBs",
    "115: Filter Bass1",
    "116: SeqFltEnvBs",
    "117: DnB Bass 1",
    "118: UnisonSynBs1",
    "119: Modular Bs",
    "120: Monster Bs 1",
    "121: Monster Bs 2",
    "122: Monster Bs 3",
    "123: Monster Bs 4",
    "124: Square Bs 1",
    "125: 106 Bass 2",
    "126: 5th Stac Bs1",
    "127: SqrStacSynBs",
    "128: MC-202 Bs",
    "129: TB Bass 2",
    "130: Square Bs 2",
    "131: SH-101 Bs",
    "132: R&B Bass 2",
    "133: MG Bass 4",
    "134: Seq Bass 2",
    "135: Tri Bass 1",
    "136: BPF Syn Bs 2",
    "137: BPF Syn Bs 1",
    "138: Low Bass 1",
    "139: Low Bass 2",
    "140: Kick Bass 1",
    "141: SinDetuneBs1",
    "142: Organ Bass 1",
    "143: Growl Bass 1",
    "144: Talking Bs 1",
    "145: LFO Bass 1",
    "146: LFO Bass 2",
    "147: Crack Bass",
    "148: Wobble Bs 1",
    "149: Wobble Bs 2",
    "150: Wobble Bs 3",
    "151: Wobble Bs 4",
    "152: SideChainBs1",
    "153: SideChainBs2",
    "154: House Bass 1",
    "155: FM Bass",
    "156: 4Op FM Bass1",
    "157: Ac. Bass",
    "158: Fingerd Bs 1",
    "159: Picked Bass",
    "160: Fretless Bs",
    "161: Slap Bass 1",
    "162: JD Piano 1",
    "163: E. Grand 1",
    "164: Trem EP 1",
    "165: FM E.Piano 1",
    "166: FM E.Piano 2",
    "167: Vib Wurly 1",
    "168: Pulse Clav",
    "169: Clav",
    "170: 70's E.Organ",
    "171: House Org 1",
    "172: House Org 2",
    "173: Bell 1",
    "174: Bell 2",
    "175: Organ Bell",
    "176: Vibraphone 1",
    "177: Steel Drum",
    "178: Harp 1",
    "179: Ac. Guitar",
    "180: Bright Strat",
    "181: Funk Guitar1",
    "182: Jazz Guitar",
    "183: Dist Guitar1",
    "184: D. Mute Gtr1",
    "185: E. Sitar",
    "186: Sitar Drone",
    "187: FX 1",
    "188: FX 2",
    "189: FX 3",
    "190: Tuned Winds1",
    "191: Bend Lead 1",
    "192: RiSER 1",
    "193: Rising SEQ 1",
    "194: Scream Saw",
    "195: Noise SEQ 1",
    "196: Syn Vox 1",
    "197: JD SoftVox",
    "198: Vox Pad",
    "199: VP-330 Chr",
    "200: Orch Hit",
    "201: Philly Hit",
    "202: House Hit",
    "203: O'Skool Hit1",
    "204: Punch Hit",
    "205: Tao Hit",
    "206: SEQ Saw 1",
    "207: SEQ Sqr",
    "208: SEQ Tri 1",
    "209: SEQ 1",
    "210: SEQ 2",
    "211: SEQ 3",
    "212: SEQ 4",
    "213: Sqr Reso Plk",
    "214: Pluck Synth1",
    "215: Paperclip 1",
    "216: Sonar Pluck1",
    "217: SqrTrapPlk 1",
    "218: TB Saw Seq 1",
    "219: TB Sqr Seq 1",
    "220: JUNO Key",
    "221: Analog Poly1",
    "222: Analog Poly2",
    "223: Analog Poly3",
    "224: Analog Poly4",
    "225: JUNO Octavr1",
    "226: EDM Synth 1",
    "227: Super Saw 2",
    "228: S-Saw Poly",
    "229: Trance Key 1",
    "230: S-Saw Pad 1",
    "231: 7th Stac Syn",
    "232: S-SawStc Syn",
    "233: Trance Key 2",
    "234: Analog Brass",
    "235: Reso Brass",
    "236: Soft Brass 1",
    "237: FM Brass",
    "238: Syn Brass 1",
    "239: Syn Brass 2",
    "240: JP8 Brass",
    "241: Soft SynBrs1",
    "242: Soft SynBrs2",
    "243: EpicSlow Brs",
    "244: JUNO Brass",
    "245: Poly Brass",
    "246: Voc:Ensemble",
    "247: Voc:5thStack",
    "248: Voc:Robot",
    "249: Voc:Saw",
    "250: Voc:Sqr",
    "251: Voc:Rise Up",
    "252: Voc:Auto Vib",
    "253: Voc:PitchEnv",
    "254: Voc:VP-330",
    "255: Voc:Noise",
]

DRUM_SN_PRESETS = [
    "001: Studio Standard",
    "002: Studio Rock",
    "003: Studio Jazz",
    "004: Studio Dance",
    "005: Studio R&B",
    "006: Studio Latin",
    "007: Power Kit",
    "008: Rock Kit",
    "009: Jazz Kit",
    "010: Brush Kit",
    "011: Orchestra Kit",
    "012: Dance Kit",
    "013: House Kit",
    "014: Hip Hop Kit",
    "015: R&B Kit",
    "016: Latin Kit",
    "017: World Kit",
    "018: Electronic Kit",
    "019: TR-808 Kit",
    "020: TR-909 Kit",
    "021: CR-78 Kit",
    "022: TR-606 Kit",
    "023: TR-707 Kit",
    "024: TR-727 Kit",
    "025: Percussion Kit",
    "026: SFX Kit",
    "027: User Kit 1",
    "028: User Kit 2",
    "029: User Kit 3",
    "030: User Kit 4",
]


class AnalogLFO(Enum):
    """LFO shape values"""

    TRIANGLE = 0
    SINE = 1
    SAW = 2
    SQUARE = 3
    SAMPLE_HOLD = 4
    RANDOM = 5


class AnalogLFOSync(Enum):
    """LFO tempo sync note values"""

    NOTE_16 = 0  # 16 bars
    NOTE_12 = 1  # 12 bars
    NOTE_8 = 2  # 8 bars
    NOTE_4 = 3  # 4 bars
    NOTE_2 = 4  # 2 bars
    NOTE_1 = 5  # 1 bar
    NOTE_3_4 = 6  # 3/4
    NOTE_2_3 = 7  # 2/3
    NOTE_1_2 = 8  # 1/2
    NOTE_3_8 = 9  # 3/8
    NOTE_1_3 = 10  # 1/3
    NOTE_1_4 = 11  # 1/4
    NOTE_3_16 = 12  # 3/16
    NOTE_1_6 = 13  # 1/6
    NOTE_1_8 = 14  # 1/8
    NOTE_3_32 = 15  # 3/32
    NOTE_1_12 = 16  # 1/12
    NOTE_1_16 = 17  # 1/16
    NOTE_1_24 = 18  # 1/24
    NOTE_1_32 = 19  # 1/32


class AnalogOscWaveform(Enum):
    """Analog oscillator waveform types"""

    SAW = 0
    TRIANGLE = 1
    PW_SQUARE = 2


class AnalogSubOscType(Enum):
    """Analog sub oscillator types"""

    OFF = 0
    TYPE_1 = 1
    TYPE_2 = 2


class AnalogFilterType(Enum):
    """Analog filter types"""

    BYPASS = 0
    LPF = 1


class AnalogParameter(Enum):
    """Analog synth parameter addresses and ranges"""

    # Oscillator parameters (0x16-0x1F)
    OSC1_WAVE = 0x16  # OSC Waveform (0-2: SAW, TRI, PW-SQR)
    OSC1_PITCH = 0x17  # OSC Pitch Coarse (40-88: maps to -24 - +24)
    OSC1_FINE = 0x18  # OSC Pitch Fine (14-114: maps to -50 - +50)
    OSC1_PW = 0x19  # OSC Pulse Width (0-127)
    OSC1_PWM = 0x1A  # OSC Pulse Width Mod Depth (0-127)
    OSC_PITCH_VELO = 0x1B  # OSC Pitch Env Velocity Sens (1-127: maps to -63 - +63)
    OSC_PITCH_ATK = 0x1C  # OSC Pitch Env Attack Time (0-127)
    OSC_PITCH_DEC = 0x1D  # OSC Pitch Env Decay (0-127)
    OSC_PITCH_DEPTH = 0x1E  # OSC Pitch Env Depth (1-127: maps to -63 - +63)
    SUB_OSC_TYPE = 0x1F  # Sub Oscillator Type (0-2: OFF, OCT-1, OCT-2)

    @staticmethod
    def validate_value(param: int, value: int) -> bool:
        """Validate parameter value is within allowed range based on MIDI spec"""
        ranges = {
            0x16: (0, 2),  # OSC Waveform: 3-bit value (0-2)
            0x17: (40, 88),  # OSC Pitch Coarse: 7-bit value (40-88)
            0x18: (14, 114),  # OSC Pitch Fine: 7-bit value (14-114)
            0x19: (0, 127),  # OSC Pulse Width: 7-bit value (0-127)
            0x1A: (0, 127),  # PWM Depth: 7-bit value (0-127)
            0x1B: (1, 127),  # Pitch Env Velocity: 7-bit value (1-127)
            0x1C: (0, 127),  # Pitch Env Attack: 7-bit value (0-127)
            0x1D: (0, 127),  # Pitch Env Decay: 7-bit value (0-127)
            0x1E: (1, 127),  # Pitch Env Depth: 7-bit value (1-127)
            0x1F: (0, 2),  # Sub OSC Type: 2-bit value (0-2)
        }

        if param in ranges:
            min_val, max_val = ranges[param]
            return min_val <= value <= max_val
        return True  # Allow other parameters to pass through

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw MIDI value to display value based on parameter preset_type"""
        display_maps = {
            0x16: ["SAW", "TRI", "PW-SQR"],  # Direct mapping for waveforms
            0x17: lambda x: f"{x - 64:+d}",  # -24 to +24 (centered at 64)
            0x18: lambda x: f"{x - 64:+d}",  # -50 to +50 (centered at 64)
            0x1B: lambda x: f"{x - 64:+d}",  # -63 to +63 (centered at 64)
            0x1E: lambda x: f"{x - 64:+d}",  # -63 to +63 (centered at 64)
            0x1F: ["OFF", "OCT-1", "OCT-2"],  # Direct mapping for sub osc preset_type
        }

        if param in display_maps:
            mapper = display_maps[param]
            if isinstance(mapper, list):
                return mapper[value] if 0 <= value < len(mapper) else str(value)
            elif callable(mapper):
                return mapper(value)
        return str(value)


# System Area Structure (0x02)
SYSTEM_COMMON = 0x00  # 00 00 00: System Common parameters
SYSTEM_CONTROLLER = 0x03  # 00 03 00: System Controller parameters


# System Common Parameters (0x02 00)
class SystemCommon(Enum):
    """System Common parameters"""

    MASTER_TUNE = 0x00  # Master Tune (24-2024: -100.0 to +100.0 cents)
    MASTER_KEY_SHIFT = 0x04  # Master Key Shift (40-88: -24 to +24 semitones)
    MASTER_LEVEL = 0x05  # Master Level (0-127)

    # Reserved space (0x06-0x10)

    PROGRAM_CTRL_CH = 0x11  # Program Control Channel (0-16: 1-16, OFF)

    # Reserved space (0x12-0x28)

    RX_PROGRAM_CHANGE = 0x29  # Receive Program Change (0: OFF, 1: ON)
    RX_BANK_SELECT = 0x2A  # Receive Bank Select (0: OFF, 1: ON)

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if param == 0x00:  # Master Tune
            cents = (value - 1024) / 10  # Convert 24-2024 to -100.0/+100.0
            return f"{cents:+.1f} cents"
        elif param == 0x04:  # Master Key Shift
            semitones = value - 64  # Convert 40-88 to -24/+24
            return f"{semitones:+d} st"
        elif param == 0x11:  # Program Control Channel
            return "OFF" if value == 0 else str(value)
        elif param in (0x29, 0x2A):  # Switches
            return "ON" if value else "OFF"
        return str(value)


@dataclass
class SystemCommonMessage(RolandSysEx):
    """System Common parameter message"""

    command: int = DT1_COMMAND_12
    area: int = SYSTEM_AREA  # 0x02: System area
    section: int = SYSTEM_COMMON  # 0x00: Common section
    group: int = 0x00  # Always 0x00
    param: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        """Set up address and data"""
        self.address = [
            self.area,  # System area (0x02)
            self.section,  # Common section (0x00)
            self.group,  # Always 0x00
            self.param,  # Parameter number
        ]
        self.data = [self.value]


# Example usage:
# Set master tune to +50 cents
msg = SystemCommonMessage(
    param=SystemCommon.MASTER_TUNE.value,
    value=1024 + (50 * 10),  # Convert +50.0 cents to 1524
)

# Set master key shift to -12 semitones
msg = SystemCommonMessage(
    param=SystemCommon.MASTER_KEY_SHIFT.value, value=52  # Convert -12 to 52 (64-12)
)

# Set program control channel to 1
msg = SystemCommonMessage(
    param=SystemCommon.PROGRAM_CTRL_CH.value, value=1  # Channel 1
)

# Enable program change reception
msg = SystemCommonMessage(param=SystemCommon.RX_PROGRAM_CHANGE.value, value=1)  # ON


# System Controller Parameters (0x02 03)
class SystemController(Enum):
    """System Controller parameters"""

    TX_PROGRAM_CHANGE = 0x00  # Transmit Program Change (0: OFF, 1: ON)
    TX_BANK_SELECT = 0x01  # Transmit Bank Select (0: OFF, 1: ON)
    KEYBOARD_VELOCITY = 0x02  # Keyboard Velocity (0: REAL, 1-127: Fixed)
    VELOCITY_CURVE = 0x03  # Keyboard Velocity Curve (0: LIGHT, 1: MEDIUM, 2: HEAVY)
    VELOCITY_OFFSET = 0x04  # Keyboard Velocity Curve Offset (54-73: -10 to +9)

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if param in (0x00, 0x01):  # Switches
            return "ON" if value else "OFF"
        elif param == 0x02:  # Keyboard velocity
            return "REAL" if value == 0 else str(value)
        elif param == 0x03:  # Velocity curve
            return ["LIGHT", "MEDIUM", "HEAVY"][value]
        elif param == 0x04:  # Velocity offset
            return f"{value - 64:+d}"  # Convert 54-73 to -10/+9
        return str(value)


@dataclass
class SystemControllerMessage(RolandSysEx):
    """System Controller parameter message"""

    command: int = DT1_COMMAND_12
    area: int = SYSTEM_AREA  # 0x02: System area
    section: int = SYSTEM_CONTROLLER  # 0x03: Controller section
    group: int = 0x00  # Always 0x00
    param: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        """Set up address and data"""
        self.address = [
            self.area,  # System area (0x02)
            self.section,  # Controller section (0x03)
            self.group,  # Always 0x00
            self.param,  # Parameter number
        ]
        self.data = [self.value]


# Example usage:
# Enable program change transmission
msg = SystemControllerMessage(
    param=SystemController.TX_PROGRAM_CHANGE.value, value=1  # ON
)

# Set keyboard velocity to REAL
msg = SystemControllerMessage(
    param=SystemController.KEYBOARD_VELOCITY.value, value=0  # REAL
)

# Set velocity curve to MEDIUM
msg = SystemControllerMessage(
    param=SystemController.VELOCITY_CURVE.value, value=1  # MEDIUM
)

# Set velocity offset to +5
msg = SystemControllerMessage(
    param=SystemController.VELOCITY_OFFSET.value, value=69  # Convert +5 to 69 (64+5)
)

# Temporary Tone Areas (0x19)
TEMP_DIGITAL_TONE = 0x01  # 01 00 00: Temporary SuperNATURAL Synth Tone
TEMP_ANALOG_TONE = 0x02  # 02 00 00: Temporary Analog Synth Tone
TEMP_DRUM_KIT = 0x10  # 10 00 00: Temporary Drum Kit

# Update our existing address offsets
DIGITAL_PART_1 = 0x01  # Digital Synth 1 (SuperNATURAL)
DIGITAL_PART_2 = 0x02  # Digital Synth 2 (SuperNATURAL)
ANALOG_PART = 0x02  # Analog Synth
DRUM_PART = 0x10  # Drum Kit


# Parameter Groups
class ToneGroup(Enum):
    """Tone parameter groups"""

    COMMON = 0x00  # Common parameters
    OSC = 0x01  # Oscillator parameters
    FILTER = 0x02  # Filter parameters
    AMP = 0x03  # Amplifier parameters
    LFO = 0x04  # LFO parameters
    EFFECTS = 0x05  # Effects parameters


# Program Area Structure (0x18)
class ProgramArea(Enum):
    """Program memory areas"""

    COMMON = 0x00  # 00 00 00: Program Common
    VOCAL_FX = 0x01  # 00 01 00: Program Vocal Effect
    EFFECT_1 = 0x02  # 00 02 00: Program Effect 1
    EFFECT_2 = 0x04  # 00 04 00: Program Effect 2
    DELAY = 0x06  # 00 06 00: Program Delay
    REVERB = 0x08  # 00 08 00: Program Reverb

    # Program Parts
    DIGITAL_1_PART = 0x20  # 00 20 00: Digital Synth Part 1
    DIGITAL_2_PART = 0x21  # 00 21 00: Digital Synth Part 2
    ANALOG_PART = 0x22  # 00 22 00: Analog Synth Part
    DRUMS_PART = 0x23  # 00 23 00: Drums Part

    # Program Zones
    DIGITAL_1_ZONE = 0x30  # 00 30 00: Digital Synth Zone 1
    DIGITAL_2_ZONE = 0x31  # 00 31 00: Digital Synth Zone 2
    ANALOG_ZONE = 0x32  # 00 32 00: Analog Synth Zone
    DRUMS_ZONE = 0x33  # 00 33 00: Drums Zone

    CONTROLLER = 0x40  # 00 40 00: Program Controller


# SuperNATURAL Synth Tone Structure (0x19 01/02)
class DigitalToneSection(Enum):
    """SuperNATURAL Synth Tone sections"""

    COMMON = 0x00  # 00 00 00: Common parameters
    PARTIAL_1 = 0x20  # 00 20 00: Partial 1
    PARTIAL_2 = 0x21  # 00 21 00: Partial 2
    PARTIAL_3 = 0x22  # 00 22 00: Partial 3
    MODIFY = 0x50  # 00 50 00: Tone Modify parameters


@dataclass
class DigitalToneMessage(RolandSysEx):
    """SuperNATURAL Synth Tone parameter message"""

    command: int = DT1_COMMAND_12
    area: int = 0x19  # Temporary area
    tone_type: int = 0x01  # Digital tone (0x01 or 0x02)
    section: int = 0x00  # Section from DigitalToneSection
    param: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        """Set up address and data"""
        self.address = [
            self.area,  # Temporary area (0x19)
            self.tone_type,  # Digital 1 or 2 (0x01/0x02)
            self.section,  # Section (Common/Partial/Modify)
            self.param,  # Parameter number
        ]
        self.data = [self.value]


# Example usage:
# Set common parameter
msg = DigitalToneMessage(
    tone_type=TEMP_DIGITAL_TONE,  # Digital 1
    section=DigitalToneSection.COMMON.value,
    param=0x00,  # Common parameter
    value=64,
)

# Set partial parameter
msg = DigitalToneMessage(
    tone_type=TEMP_DIGITAL_TONE,  # Digital 1
    section=DigitalToneSection.PARTIAL_1.value,
    param=0x00,  # Partial parameter
    value=64,
)

# Set modify parameter
msg = DigitalToneMessage(
    tone_type=TEMP_DIGITAL_TONE,  # Digital 1
    section=DigitalToneSection.MODIFY.value,
    param=0x00,  # Modify parameter
    value=64,
)


class DigitalToneCommon:
    """SuperNATURAL Synth Tone Common parameters"""

    # Tone name (12 characters)
    NAME_1 = 0x00  # Character 1 (ASCII 32-127)
    NAME_2 = 0x01  # Character 2
    NAME_3 = 0x02  # Character 3
    NAME_4 = 0x03  # Character 4
    NAME_5 = 0x04  # Character 5
    NAME_6 = 0x05  # Character 6
    NAME_7 = 0x06  # Character 7
    NAME_8 = 0x07  # Character 8
    NAME_9 = 0x08  # Character 9
    NAME_10 = 0x09  # Character 10
    NAME_11 = 0x0A  # Character 11
    NAME_12 = 0x0B  # Character 12

    # Basic parameters
    LEVEL = 0x0C  # Tone Level (0-127)
    PORTAMENTO_SW = 0x12  # Portamento Switch (0-1)
    PORTA_TIME = 0x13  # Portamento Time (0-127)
    MONO_SW = 0x14  # Mono Switch (0-1)
    OCTAVE = 0x15  # Octave Shift (-3/+3)
    BEND_UP = 0x16  # Pitch Bend Range Up (0-24)
    BEND_DOWN = 0x17  # Pitch Bend Range Down (0-24)

    # Partial switches
    PART1_SW = 0x19  # Partial 1 Switch (0-1)
    PART1_SEL = 0x1A  # Partial 1 Select (0-1)
    PART2_SW = 0x1B  # Partial 2 Switch (0-1)
    PART2_SEL = 0x1C  # Partial 2 Select (0-1)
    PART3_SW = 0x1D  # Partial 3 Switch (0-1)
    PART3_SEL = 0x1E  # Partial 3 Select (0-1)

    # Advanced parameters
    RING_SW = 0x1F  # Ring Switch (0: OFF, 1: ---, 2: ON)
    UNISON_SW = 0x2E  # Unison Switch (0-1)
    PORTA_MODE = 0x31  # Portamento Mode (0: NORMAL, 1: LEGATO)
    LEGATO_SW = 0x32  # Legato Switch (0-1)
    ANALOG_FEEL = 0x34  # Analog Feel (0-127)
    WAVE_SHAPE = 0x35  # Wave Shape (0-127)
    CATEGORY = 0x36  # Tone Category (0-127)
    UNISON_SIZE = 0x3C  # Unison Size (0-3: 2,4,6,8 voices)

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if 0x00 <= param <= 0x0B:  # Name characters
            return chr(value) if 32 <= value <= 127 else "?"
        elif param == 0x15:  # Octave shift
            return f"{value - 64:+d}"  # Convert 61-67 to -3/+3
        elif param in (
            0x12,
            0x14,
            0x19,
            0x1A,
            0x1B,
            0x1C,
            0x1D,
            0x1E,
            0x2E,
            0x32,
        ):  # Switches
            return "ON" if value else "OFF"
        elif param == 0x1F:  # Ring switch
            return ["OFF", "---", "ON"][value]
        elif param == 0x31:  # Portamento mode
            return "LEGATO" if value else "NORMAL"
        elif param == 0x3C:  # Unison size
            return str([2, 4, 6, 8][value])  # Convert 0-3 to actual voice count
        return str(value)


class DigitalTonePartial(Enum):
    """Partial parameters for SuperNATURAL Synth Tone"""

    WAVE = 0x00  # Wave number (0-255)
    LEVEL = 0x01  # Partial level (0-127)
    COARSE = 0x02  # Coarse tune (-24 to +24)
    FINE = 0x03  # Fine tune (-50 to +50)
    DETUNE = 0x04  # Detune (-50 to +50)
    ATTACK = 0x05  # Attack time (0-127)
    DECAY = 0x06  # Decay time (0-127)
    SUSTAIN = 0x07  # Sustain level (0-127)
    RELEASE = 0x08  # Release time (0-127)
    PAN = 0x09  # Pan position (-64 to +63)
    FILTER_TYPE = 0x0A  # Filter preset_type (0: OFF, 1: LPF, 2: HPF)
    CUTOFF = 0x0B  # Filter cutoff (0-127)
    RESONANCE = 0x0C  # Filter resonance (0-127)
    ENV_DEPTH = 0x0D  # Filter envelope depth (-63 to +63)
    ENV_VELOCITY = 0x0E  # Filter envelope velocity (-63 to +63)
    ENV_ATTACK = 0x0F  # Filter envelope attack (0-127)
    ENV_DECAY = 0x10  # Filter envelope decay (0-127)
    ENV_SUSTAIN = 0x11  # Filter envelope sustain (0-127)
    ENV_RELEASE = 0x12  # Filter envelope release (0-127)


class DigitalToneModify:
    """SuperNATURAL Synth Tone Modify parameters"""

    ATTACK_SENS = 0x01  # Attack Time Interval Sens (0-127)
    RELEASE_SENS = 0x02  # Release Time Interval Sens (0-127)
    PORTA_SENS = 0x03  # Portamento Time Interval Sens (0-127)
    ENV_LOOP_MODE = 0x04  # Envelope Loop Mode (0-2)
    ENV_LOOP_SYNC = 0x05  # Envelope Loop Sync Note (0-19)
    CHROM_PORTA = 0x06  # Chromatic Portamento (0-1)

    # Envelope Loop Mode values
    LOOP_OFF = 0  # OFF
    LOOP_FREE = 1  # FREE-RUN
    LOOP_SYNC = 2  # TEMPO-SYNC

    # Sync note values (for ENV_LOOP_SYNC)
    SYNC_16 = 0  # 16
    SYNC_12 = 1  # 12
    SYNC_8 = 2  # 8
    SYNC_4 = 3  # 4
    SYNC_2 = 4  # 2
    SYNC_1 = 5  # 1
    SYNC_3_4 = 6  # 3/4
    SYNC_2_3 = 7  # 2/3
    SYNC_1_2 = 8  # 1/2
    SYNC_3_8 = 9  # 3/8
    SYNC_1_3 = 10  # 1/3
    SYNC_1_4 = 11  # 1/4
    SYNC_3_16 = 12  # 3/16
    SYNC_1_6 = 13  # 1/6
    SYNC_1_8 = 14  # 1/8
    SYNC_3_32 = 15  # 3/32
    SYNC_1_12 = 16  # 1/12
    SYNC_1_16 = 17  # 1/16
    SYNC_1_24 = 18  # 1/24
    SYNC_1_32 = 19  # 1/32

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if param == 0x04:  # Envelope Loop Mode
            return ["OFF", "FREE-RUN", "TEMPO-SYNC"][value]
        elif param == 0x05:  # Envelope Loop Sync Note
            notes = [
                "16",
                "12",
                "8",
                "4",
                "2",
                "1",
                "3/4",
                "2/3",
                "1/2",
                "3/8",
                "1/3",
                "1/4",
                "3/16",
                "1/6",
                "1/8",
                "3/32",
                "1/12",
                "1/16",
                "1/24",
                "1/32",
            ]
            return notes[value] if 0 <= value <= 19 else str(value)
        elif param == 0x06:  # Chromatic Portamento
            return "ON" if value else "OFF"
        return str(value)


class EffectType(Enum):
    """Effect types and parameters"""

    # Effect types
    THRU = 0x00
    DISTORTION = 0x01
    FUZZ = 0x02
    COMPRESSOR = 0x03
    BITCRUSHER = 0x04
    FLANGER = 0x05
    PHASER = 0x06
    RING_MOD = 0x07
    SLICER = 0x08

    # Common parameters
    LEVEL = 0x00
    MIX = 0x01

    # Effect-specific parameters
    DRIVE = 0x10
    TONE = 0x11
    ATTACK = 0x12
    RELEASE = 0x13
    THRESHOLD = 0x14
    RATIO = 0x15
    BIT_DEPTH = 0x16
    RATE = 0x17
    DEPTH = 0x18
    FEEDBACK = 0x19
    FREQUENCY = 0x1A
    BALANCE = 0x1B
    PATTERN = 0x1C

    # Send levels
    REVERB_SEND = 0x20
    DELAY_SEND = 0x21
    CHORUS_SEND = 0x22

    # Reverb parameters
    REVERB_TYPE = 0x30
    REVERB_TIME = 0x31
    REVERB_PRE_DELAY = 0x32

    # Delay parameters
    DELAY_TIME = 0x40
    DELAY_FEEDBACK = 0x41
    DELAY_HF_DAMP = 0x42

    # Chorus parameters
    CHORUS_RATE = 0x50
    CHORUS_DEPTH = 0x51
    CHORUS_FEEDBACK = 0x52


class VocalFX(Enum):
    """Vocal effects types and parameters"""

    # Effect types
    VOCODER = 0x00
    AUTO_PITCH = 0x01
    HARMONIST = 0x02

    # Common parameters
    LEVEL = 0x00
    PAN = 0x01
    REVERB_SEND = 0x02
    DELAY_SEND = 0x03

    # Vocoder parameters
    MIC_SENS = 0x10
    CARRIER_MIX = 0x11
    FORMANT = 0x12
    CUTOFF = 0x13
    RESONANCE = 0x14

    # Auto-Pitch parameters
    SCALE = 0x20
    KEY = 0x21
    GENDER = 0x22
    BALANCE = 0x23

    # Harmonist parameters
    HARMONY_1 = 0x30
    HARMONY_2 = 0x31
    HARMONY_3 = 0x32
    DETUNE = 0x33


class VoiceCutoffFilter(Enum):
    """Voice cutoff filter types"""

    THRU = 0x00
    LPF = 0x01
    HPF = 0x02
    BPF = 0x03


class VoiceScale(Enum):
    """Voice scale types"""

    CHROMATIC = 0x00
    MAJOR = 0x01
    MINOR = 0x02
    BLUES = 0x03
    INDIAN = 0x04


class VoiceKey(Enum):
    """Voice keys"""

    C = 0x00
    Db = 0x01
    D = 0x02
    Eb = 0x03
    E = 0x04
    F = 0x05
    Gb = 0x06
    G = 0x07
    Ab = 0x08
    A = 0x09
    Bb = 0x0A
    B = 0x0B


class ArpGrid(Enum):
    """Arpeggio grid values"""

    GRID_4 = 0  # 04_
    GRID_8 = 1  # 08_
    GRID_8L = 2  # 08L
    GRID_8H = 3  # 08H
    GRID_8T = 4  # 08t
    GRID_16 = 5  # 16_
    GRID_16L = 6  # 16L
    GRID_16H = 7  # 16H
    GRID_16T = 8  # 16t


class ArpDuration(Enum):
    """Arpeggio duration values"""

    DUR_30 = 0  # 30%
    DUR_40 = 1  # 40%
    DUR_50 = 2  # 50%
    DUR_60 = 3  # 60%
    DUR_70 = 4  # 70%
    DUR_80 = 5  # 80%
    DUR_90 = 6  # 90%
    DUR_100 = 7  # 100%
    DUR_120 = 8  # 120%
    DUR_FULL = 9  # FULL


class ArpMotif(Enum):
    """Arpeggio motif values"""

    UP_L = 0  # UP/L
    UP_H = 1  # UP/H
    UP_NORM = 2  # UP/_
    DOWN_L = 3  # dn/L
    DOWN_H = 4  # dn/H
    DOWN_NORM = 5  # dn/_
    UP_DOWN_L = 6  # Ud/L
    UP_DOWN_H = 7  # Ud/H
    UP_DOWN_NORM = 8  # Ud/_
    RANDOM_L = 9  # rn/L
    RANDOM_NORM = 10  # rn/_
    PHRASE = 11  # PHRASE


class ArpParameters(Enum):
    """Arpeggiator parameters"""

    GRID = 0x01  # Grid (0-8)
    DURATION = 0x02  # Duration (0-9)
    SWITCH = 0x03  # On/Off (0-1)
    STYLE = 0x05  # Style (0-127)
    MOTIF = 0x06  # Motif (0-11)
    OCTAVE = 0x07  # Octave Range (61-67: -3 to +3)
    ACCENT = 0x09  # Accent Rate (0-100)
    VELOCITY = 0x0A  # Velocity (0-127, 0=REAL)


# SuperNATURAL presets for each address
DIGITAL_SN_PRESETS = [
    "001: JP8 Strings1",
    "002: Soft Pad 1",
    "003: JP8 Strings2",
    "004: JUNO Str 1",
    "005: Oct Strings",
    "006: Brite Str 1",
    "007: Boreal Pad",
    "008: JP8 Strings3",
    "009: JP8 Strings4",
    "010: Hollow Pad 1",
    "011: LFO Pad 1",
    "012: Hybrid Str",
    "013: Awakening 1",
    "014: Cincosoft 1",
    "015: Bright Pad 1",
    "016: Analog Str 1",
    "017: Soft ResoPd1",
    "018: HPF Poly 1",
    "019: BPF Poly",
    "020: Sweep Pad 1",
    "021: Soft Pad 2",
    "022: Sweep JD 1",
    "023: FltSweep Pd1",
    "024: HPF Pad",
    "025: HPF SweepPd1",
    "026: KOff Pad",
    "027: Sweep Pad 2",
    "028: TrnsSweepPad",
    "029: Revalation 1",
    "030: LFO CarvePd1",
    "031: RETROX 139 1",
    "032: LFO ResoPad1",
    "033: PLS Pad 1",
    "034: PLS Pad 2",
    "035: Trip 2 Mars1",
    "036: Reso S&H Pd1",
    "037: SideChainPd1",
    "038: PXZoon 1",
    "039: Psychoscilo1",
    "040: Fantasy 1",
    "041: D-50 Stack 1",
    "042: Organ Pad",
    "043: Bell Pad",
    "044: Dreaming 1",
    "045: Syn Sniper 1",
    "046: Strings 1",
    "047: D-50 Pizz 1",
    "048: Super Saw 1",
    "049: S-SawStacLd1",
    "050: Tekno Lead 1",
    "051: Tekno Lead 2",
    "052: Tekno Lead 3",
    "053: OSC-SyncLd 1",
    "054: WaveShapeLd1",
    "055: JD RingMod 1",
    "056: Buzz Lead 1",
    "057: Buzz Lead 2",
    "058: SawBuzz Ld 1",
    "059: Sqr Buzz Ld1",
    "060: Tekno Lead 4",
    "061: Dist Flt TB1",
    "062: Dist TB Sqr1",
    "063: Glideator 1",
    "064: Vintager 1",
    "065: Hover Lead 1",
    "066: Saw Lead 1",
    "067: Saw+Tri Lead",
    "068: PortaSaw Ld1",
    "069: Reso Saw Ld",
    "070: SawTrap Ld 1",
    "071: Fat GR Lead",
    "072: Pulstar Ld",
    "073: Slow Lead",
    "074: AnaVox Lead",
    "075: Square Ld 1",
    "076: Square Ld 2",
    "077: Sqr Lead 1",
    "078: Sqr Trap Ld1",
    "079: Sine Lead 1",
    "080: Tri Lead",
    "081: Tri Stac Ld1",
    "082: 5th SawLead1",
    "083: Sweet 5th 1",
    "084: 4th Syn Lead",
    "085: Maj Stack Ld",
    "086: MinStack Ld1",
    "087: Chubby Lead1",
    "088: CuttingLead1",
    "089: Seq Bass 1",
    "090: Reso Bass 1",
    "091: TB Bass 1",
    "092: 106 Bass 1",
    "093: FilterEnvBs1",
    "094: JUNO Sqr Bs1",
    "095: Reso Bass 2",
    "096: JUNO Bass",
    "097: MG Bass 1",
    "098: 106 Bass 3",
    "099: Reso Bass 3",
    "100: Detune Bs 1",
    "101: MKS-50 Bass1",
    "102: Sweep Bass",
    "103: MG Bass 2",
    "104: MG Bass 3",
    "105: ResRubber Bs",
    "106: R&B Bass 1",
    "107: Reso Bass 4",
    "108: Wide Bass 1",
    "109: Chow Bass 1",
    "110: Chow Bass 2",
    "111: SqrFilterBs1",
    "112: Reso Bass 5",
    "113: Syn Bass 1",
    "114: ResoSawSynBs",
    "115: Filter Bass1",
    "116: SeqFltEnvBs",
    "117: DnB Bass 1",
    "118: UnisonSynBs1",
    "119: Modular Bs",
    "120: Monster Bs 1",
    "121: Monster Bs 2",
    "122: Monster Bs 3",
    "123: Monster Bs 4",
    "124: Square Bs 1",
    "125: 106 Bass 2",
    "126: 5th Stac Bs1",
    "127: SqrStacSynBs",
    "128: MC-202 Bs",
    "129: TB Bass 2",
    "130: Square Bs 2",
    "131: SH-101 Bs",
    "132: R&B Bass 2",
    "133: MG Bass 4",
    "134: Seq Bass 2",
    "135: Tri Bass 1",
    "136: BPF Syn Bs 2",
    "137: BPF Syn Bs 1",
    "138: Low Bass 1",
    "139: Low Bass 2",
    "140: Kick Bass 1",
    "141: SinDetuneBs1",
    "142: Organ Bass 1",
    "143: Growl Bass 1",
    "144: Talking Bs 1",
    "145: LFO Bass 1",
    "146: LFO Bass 2",
    "147: Crack Bass",
    "148: Wobble Bs 1",
    "149: Wobble Bs 2",
    "150: Wobble Bs 3",
    "151: Wobble Bs 4",
    "152: SideChainBs1",
    "153: SideChainBs2",
    "154: House Bass 1",
    "155: FM Bass",
    "156: 4Op FM Bass1",
    "157: Ac. Bass",
    "158: Fingerd Bs 1",
    "159: Picked Bass",
    "160: Fretless Bs",
    "161: Slap Bass 1",
    "162: JD Piano 1",
    "163: E. Grand 1",
    "164: Trem EP 1",
    "165: FM E.Piano 1",
    "166: FM E.Piano 2",
    "167: Vib Wurly 1",
    "168: Pulse Clav",
    "169: Clav",
    "170: 70's E.Organ",
    "171: House Org 1",
    "172: House Org 2",
    "173: Bell 1",
    "174: Bell 2",
    "175: Organ Bell",
    "176: Vibraphone 1",
    "177: Steel Drum",
    "178: Harp 1",
    "179: Ac. Guitar",
    "180: Bright Strat",
    "181: Funk Guitar1",
    "182: Jazz Guitar",
    "183: Dist Guitar1",
    "184: D. Mute Gtr1",
    "185: E. Sitar",
    "186: Sitar Drone",
    "187: FX 1",
    "188: FX 2",
    "189: FX 3",
    "190: Tuned Winds1",
    "191: Bend Lead 1",
    "192: RiSER 1",
    "193: Rising SEQ 1",
    "194: Scream Saw",
    "195: Noise SEQ 1",
    "196: Syn Vox 1",
    "197: JD SoftVox",
    "198: Vox Pad",
    "199: VP-330 Chr",
    "200: Orch Hit",
    "201: Philly Hit",
    "202: House Hit",
    "203: O'Skool Hit1",
    "204: Punch Hit",
    "205: Tao Hit",
    "206: SEQ Saw 1",
    "207: SEQ Sqr",
    "208: SEQ Tri 1",
    "209: SEQ 1",
    "210: SEQ 2",
    "211: SEQ 3",
    "212: SEQ 4",
    "213: Sqr Reso Plk",
    "214: Pluck Synth1",
    "215: Paperclip 1",
    "216: Sonar Pluck1",
    "217: SqrTrapPlk 1",
    "218: TB Saw Seq 1",
    "219: TB Sqr Seq 1",
    "220: JUNO Key",
    "221: Analog Poly1",
    "222: Analog Poly2",
    "223: Analog Poly3",
    "224: Analog Poly4",
    "225: JUNO Octavr1",
    "226: EDM Synth 1",
    "227: Super Saw 2",
    "228: S-Saw Poly",
    "229: Trance Key 1",
    "230: S-Saw Pad 1",
    "231: 7th Stac Syn",
    "232: S-SawStc Syn",
    "233: Trance Key 2",
    "234: Analog Brass",
    "235: Reso Brass",
    "236: Soft Brass 1",
    "237: FM Brass",
    "238: Syn Brass 1",
    "239: Syn Brass 2",
    "240: JP8 Brass",
    "241: Soft SynBrs1",
    "242: Soft SynBrs2",
    "243: EpicSlow Brs",
    "244: JUNO Brass",
    "245: Poly Brass",
    "246: Voc:Ensemble",
    "247: Voc:5thStack",
    "248: Voc:Robot",
    "249: Voc:Saw",
    "250: Voc:Sqr",
    "251: Voc:Rise Up",
    "252: Voc:Auto Vib",
    "253: Voc:PitchEnv",
    "254: Voc:VP-330",
    "255: Voc:Noise",
]

DRUM_SN_PRESETS = [
    "001: Studio Standard",
    "002: Studio Rock",
    "003: Studio Jazz",
    "004: Studio Dance",
    "005: Studio R&B",
    "006: Studio Latin",
    "007: Power Kit",
    "008: Rock Kit",
    "009: Jazz Kit",
    "010: Brush Kit",
    "011: Orchestra Kit",
    "012: Dance Kit",
    "013: House Kit",
    "014: Hip Hop Kit",
    "015: R&B Kit",
    "016: Latin Kit",
    "017: World Kit",
    "018: Electronic Kit",
    "019: TR-808 Kit",
    "020: TR-909 Kit",
    "021: CR-78 Kit",
    "022: TR-606 Kit",
    "023: TR-707 Kit",
    "024: TR-727 Kit",
    "025: Percussion Kit",
    "026: SFX Kit",
    "027: User Kit 1",
    "028: User Kit 2",
    "029: User Kit 3",
    "030: User Kit 4",
]


class AnalogLFO(Enum):
    """LFO shape values"""

    TRIANGLE = 0
    SINE = 1
    SAW = 2
    SQUARE = 3
    SAMPLE_HOLD = 4
    RANDOM = 5


class AnalogLFOSync(Enum):
    """LFO tempo sync note values"""

    NOTE_16 = 0  # 16 bars
    NOTE_12 = 1  # 12 bars
    NOTE_8 = 2  # 8 bars
    NOTE_4 = 3  # 4 bars
    NOTE_2 = 4  # 2 bars
    NOTE_1 = 5  # 1 bar
    NOTE_3_4 = 6  # 3/4
    NOTE_2_3 = 7  # 2/3
    NOTE_1_2 = 8  # 1/2
    NOTE_3_8 = 9  # 3/8
    NOTE_1_3 = 10  # 1/3
    NOTE_1_4 = 11  # 1/4
    NOTE_3_16 = 12  # 3/16
    NOTE_1_6 = 13  # 1/6
    NOTE_1_8 = 14  # 1/8
    NOTE_3_32 = 15  # 3/32
    NOTE_1_12 = 16  # 1/12
    NOTE_1_16 = 17  # 1/16
    NOTE_1_24 = 18  # 1/24
    NOTE_1_32 = 19  # 1/32


class AnalogOscWaveform(Enum):
    """Analog oscillator waveform types"""

    SAW = 0
    TRIANGLE = 1
    PW_SQUARE = 2


class AnalogSubOscType(Enum):
    """Analog sub oscillator types"""

    OFF = 0
    TYPE_1 = 1
    TYPE_2 = 2


class AnalogFilterType(Enum):
    """Analog filter types"""

    BYPASS = 0
    LPF = 1


class AnalogParameter(Enum):
    """Analog synth parameter addresses and ranges"""

    # Oscillator parameters (0x16-0x1F)
    OSC1_WAVE = 0x16  # OSC Waveform (0-2: SAW, TRI, PW-SQR)
    OSC1_PITCH = 0x17  # OSC Pitch Coarse (40-88: maps to -24 - +24)
    OSC1_FINE = 0x18  # OSC Pitch Fine (14-114: maps to -50 - +50)
    OSC1_PW = 0x19  # OSC Pulse Width (0-127)
    OSC1_PWM = 0x1A  # OSC Pulse Width Mod Depth (0-127)
    OSC_PITCH_VELO = 0x1B  # OSC Pitch Env Velocity Sens (1-127: maps to -63 - +63)
    OSC_PITCH_ATK = 0x1C  # OSC Pitch Env Attack Time (0-127)
    OSC_PITCH_DEC = 0x1D  # OSC Pitch Env Decay (0-127)
    OSC_PITCH_DEPTH = 0x1E  # OSC Pitch Env Depth (1-127: maps to -63 - +63)
    SUB_OSC_TYPE = 0x1F  # Sub Oscillator Type (0-2: OFF, OCT-1, OCT-2)

    @staticmethod
    def validate_value(param: int, value: int) -> bool:
        """Validate parameter value is within allowed range based on MIDI spec"""
        ranges = {
            0x16: (0, 2),  # OSC Waveform: 3-bit value (0-2)
            0x17: (40, 88),  # OSC Pitch Coarse: 7-bit value (40-88)
            0x18: (14, 114),  # OSC Pitch Fine: 7-bit value (14-114)
            0x19: (0, 127),  # OSC Pulse Width: 7-bit value (0-127)
            0x1A: (0, 127),  # PWM Depth: 7-bit value (0-127)
            0x1B: (1, 127),  # Pitch Env Velocity: 7-bit value (1-127)
            0x1C: (0, 127),  # Pitch Env Attack: 7-bit value (0-127)
            0x1D: (0, 127),  # Pitch Env Decay: 7-bit value (0-127)
            0x1E: (1, 127),  # Pitch Env Depth: 7-bit value (1-127)
            0x1F: (0, 2),  # Sub OSC Type: 2-bit value (0-2)
        }

        if param in ranges:
            min_val, max_val = ranges[param]
            return min_val <= value <= max_val
        return True  # Allow other parameters to pass through

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw MIDI value to display value based on parameter preset_type"""
        display_maps = {
            0x16: ["SAW", "TRI", "PW-SQR"],  # Direct mapping for waveforms
            0x17: lambda x: f"{x - 64:+d}",  # -24 to +24 (centered at 64)
            0x18: lambda x: f"{x - 64:+d}",  # -50 to +50 (centered at 64)
            0x1B: lambda x: f"{x - 64:+d}",  # -63 to +63 (centered at 64)
            0x1E: lambda x: f"{x - 64:+d}",  # -63 to +63 (centered at 64)
            0x1F: ["OFF", "OCT-1", "OCT-2"],  # Direct mapping for sub osc preset_type
        }

        if param in display_maps:
            mapper = display_maps[param]
            if isinstance(mapper, list):
                return mapper[value] if 0 <= value < len(mapper) else str(value)
            elif callable(mapper):
                return mapper(value)
        return str(value)


class DigitalParameter(Enum):
    """Digital synth parameter addresses and ranges"""

    # Tone name parameters (0x00-0x0B)
    TONE_NAME_1 = 0x00  # ASCII 32-127
    TONE_NAME_2 = 0x01
    TONE_NAME_3 = 0x02
    TONE_NAME_4 = 0x03
    TONE_NAME_5 = 0x04
    TONE_NAME_6 = 0x05
    TONE_NAME_7 = 0x06
    TONE_NAME_8 = 0x07
    TONE_NAME_9 = 0x08
    TONE_NAME_10 = 0x09
    TONE_NAME_11 = 0x0A
    TONE_NAME_12 = 0x0B

    # Common parameters (0x0C-0x18)
    TONE_LEVEL = 0x0C  # 0-127
    PORTAMENTO_SW = 0x12  # 0-1 (OFF/ON)
    PORTAMENTO_TIME = 0x13  # 0-127
    MONO_SW = 0x14  # 0-1 (OFF/ON)
    OCTAVE_SHIFT = 0x15  # 61-67 (-3 to +3)
    BEND_RANGE_UP = 0x16  # 0-24 semitones
    BEND_RANGE_DOWN = 0x17  # 0-24 semitones

    # Partial parameters (0x20-0x2F)
    PARTIAL_SWITCH = 0x20  # 0-1 (OFF/ON)
    PARTIAL_LEVEL = 0x21  # 0-127
    PARTIAL_COARSE = 0x22  # 40-88 (-24 to +24)
    PARTIAL_FINE = 0x23  # 14-114 (-50 to +50)
    WAVE_SHAPE = 0x24  # 0-127
    PULSE_WIDTH = 0x25  # 0-127
    PWM_DEPTH = 0x26  # 0-127
    SUPER_SAW_DEPTH = 0x27  # 0-127
    FILTER_TYPE = 0x28  # 0-3 (OFF,LPF,BPF,HPF)
    CUTOFF = 0x29  # 0-127
    RESONANCE = 0x2A  # 0-127
    FILTER_ENV = 0x2B  # 1-127 (-63 to +63)
    FILTER_KEY = 0x2C  # 0-127
    AMP_ENV = 0x2D  # 0-127
    PAN = 0x2E  # 0-127 (L64-63R)
    RING_SW = 0x1F  # 0-2 (OFF, ---, ON)

    # Partial switches (0x19-0x1E)
    PARTIAL1_SWITCH = 0x19  # 0-1 (OFF/ON)
    PARTIAL1_SELECT = 0x1A  # 0-1 (OFF/ON)
    PARTIAL2_SWITCH = 0x1B  # 0-1 (OFF/ON)
    PARTIAL2_SELECT = 0x1C  # 0-1 (OFF/ON)
    PARTIAL3_SWITCH = 0x1D  # 0-1 (OFF/ON)
    PARTIAL3_SELECT = 0x1E  # 0-1 (OFF/ON)

    # Additional common parameters (0x2E-0x3C)
    UNISON_SW = 0x2E  # 0-1 (OFF/ON)
    PORTAMENTO_MODE = 0x31  # 0-1 (NORMAL/LEGATO)
    LEGATO_SW = 0x32  # 0-1 (OFF/ON)
    ANALOG_FEEL = 0x34  # 0-127
    WAVE_SHAPE_COMMON = 0x35  # 0-127 (renamed from WAVE_SHAPE)
    TONE_CATEGORY = 0x36  # 0-127
    UNISON_SIZE = 0x3C  # 0-3 (2,4,6,8 voices)

    # Modify parameters (0x01-0x06)
    ATTACK_TIME_SENS = 0x01  # 0-127
    RELEASE_TIME_SENS = 0x02  # 0-127
    PORTA_TIME_SENS = 0x03  # 0-127
    ENV_LOOP_MODE = 0x04  # 0-2 (OFF, FREE-RUN, TEMPO-SYNC)
    ENV_LOOP_SYNC = 0x05  # 0-19 (sync note values)
    CHROM_PORTA = 0x06  # 0-1 (OFF/ON)

    # Partial oscillator parameters (0x00-0x09)
    OSC_WAVE = 0x00  # 0-7 (SAW, SQR, PW-SQR, TRI, SINE, NOISE, SUPER-SAW, PCM)
    OSC_VARIATION = 0x01  # 0-2 (A, B, C)
    OSC_PITCH = 0x03  # 40-88 (-24 to +24)
    OSC_DETUNE = 0x04  # 14-114 (-50 to +50)
    OSC_PWM_DEPTH = 0x05  # 0-127
    OSC_PW = 0x06  # 0-127
    OSC_PITCH_ATK = 0x07  # 0-127
    OSC_PITCH_DEC = 0x08  # 0-127
    OSC_PITCH_DEPTH = 0x09  # 1-127 (-63 to +63)

    # Filter parameters (0x0A-0x14)
    FILTER_MODE = 0x0A  # 0-7 (BYPASS, LPF, HPF, BPF, PKG, LPF2, LPF3, LPF4)
    FILTER_SLOPE = 0x0B  # 0-1 (-12, -24 dB)
    FILTER_CUTOFF = 0x0C  # 0-127
    FILTER_KEYFOLLOW = 0x0D  # 54-74 (-100 to +100)
    FILTER_ENV_VELO = 0x0E  # 1-127 (-63 to +63)
    FILTER_RESONANCE = 0x0F  # 0-127
    FILTER_ENV_ATK = 0x10  # 0-127
    FILTER_ENV_DEC = 0x11  # 0-127
    FILTER_ENV_SUS = 0x12  # 0-127
    FILTER_ENV_REL = 0x13  # 0-127
    FILTER_ENV_DEPTH = 0x14  # 1-127 (-63 to +63)

    # Amplifier parameters (0x15-0x1B)
    AMP_LEVEL = 0x15  # 0-127
    AMP_VELO_SENS = 0x16  # 1-127 (-63 to +63)
    AMP_ENV_ATK = 0x17  # 0-127
    AMP_ENV_DEC = 0x18  # 0-127
    AMP_ENV_SUS = 0x19  # 0-127
    AMP_ENV_REL = 0x1A  # 0-127
    AMP_PAN = 0x1B  # 0-127 (L64-63R)

    # LFO parameters (0x1C-0x25)
    LFO_SHAPE = 0x1C  # 0-5 (TRI, SIN, SAW, SQR, S&H, RND)
    LFO_RATE = 0x1D  # 0-127
    LFO_SYNC_SW = 0x1E  # 0-1 (OFF/ON)
    LFO_SYNC_NOTE = 0x1F  # 0-19 (sync note values)
    LFO_FADE = 0x20  # 0-127
    LFO_KEY_TRIG = 0x21  # 0-1 (OFF/ON)
    LFO_PITCH_DEPTH = 0x22  # 1-127 (-63 to +63)
    LFO_FILTER_DEPTH = 0x23  # 1-127 (-63 to +63)
    LFO_AMP_DEPTH = 0x24  # 1-127 (-63 to +63)
    LFO_PAN_DEPTH = 0x25  # 1-127 (-63 to +63)

    # Modulation LFO parameters (0x26-0x2F)
    MOD_LFO_SHAPE = 0x26  # 0-5 (TRI, SIN, SAW, SQR, S&H, RND)
    MOD_LFO_RATE = 0x27  # 0-127
    MOD_LFO_SYNC_SW = 0x28  # 0-1 (OFF/ON)
    MOD_LFO_SYNC_NOTE = 0x29  # 0-19 (sync note values)
    OSC_PW_SHIFT = 0x2A  # 0-127
    MOD_LFO_PITCH = 0x2C  # 1-127 (-63 to +63)
    MOD_LFO_FILTER = 0x2D  # 1-127 (-63 to +63)
    MOD_LFO_AMP = 0x2E  # 1-127 (-63 to +63)
    MOD_LFO_PAN = 0x2F  # 1-127 (-63 to +63)

    # Aftertouch parameters (0x30-0x31)
    CUTOFF_AFTERTOUCH = 0x30  # 1-127 (-63 to +63)
    LEVEL_AFTERTOUCH = 0x31  # 1-127 (-63 to +63)

    # Additional oscillator parameters (0x34-0x35)
    WAVE_GAIN = 0x34  # 0-3 (-6, 0, +6, +12 dB)
    WAVE_NUMBER = 0x35  # 0-16384 (OFF, 1-16384)

    # Filter and modulation parameters (0x39-0x3C)
    HPF_CUTOFF = 0x39  # 0-127
    SUPER_SAW_DETUNE = 0x3A  # 0-127
    MOD_LFO_RATE_CTRL = 0x3B  # 1-127 (-63 to +63)
    AMP_LEVEL_KEYFOLLOW = 0x3C  # 54-74 (-100 to +100)

    @staticmethod
    def validate_value(param: int, value: int) -> bool:
        """Validate parameter value is within allowed range"""
        ranges = {
            # Tone name (0x00-0x0B): ASCII 32-127
            range(0x00, 0x0C): lambda v: 32 <= v <= 127,
            # Level: 0-127
            0x0C: lambda v: 0 <= v <= 127,
            # Switches: 0-1
            0x12: lambda v: v in (0, 1),  # Portamento
            0x14: lambda v: v in (0, 1),  # Mono
            # Portamento time: 0-127
            0x13: lambda v: 0 <= v <= 127,
            # Octave shift: 61-67 (-3 to +3)
            0x15: lambda v: 61 <= v <= 67,
            # Pitch bend ranges: 0-24
            0x16: lambda v: 0 <= v <= 24,
            0x17: lambda v: 0 <= v <= 24,
        }

        # Find matching range
        for param_range, validator in ranges.items():
            if isinstance(param_range, range):
                if param in param_range:
                    return validator(value)
            elif param == param_range:
                return validator(value)

        return True  # Allow other parameters to pass through

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if 0x00 <= param <= 0x0B:  # Tone name
            return chr(value)
        elif param == 0x15:  # Octave shift
            return f"{value - 64:+d}"  # Convert to -3 to +3
        elif param in (
            0x12,
            0x14,
            0x20,
            0x2F,
            0x19,
            0x1A,
            0x1B,
            0x1C,
            0x1D,
            0x1E,
        ):  # All switches
            return "ON" if value else "OFF"
        elif param == 0x22:  # Coarse tune
            return f"{value - 64:+d}"  # Convert to -24/+24
        elif param == 0x23:  # Fine tune
            return f"{value - 64:+d}"  # Convert to -50/+50
        elif param == 0x28:  # Filter preset_type
            return ["OFF", "LPF", "BPF", "HPF"][value]
        elif param == 0x2B:  # Filter env
            return f"{value - 64:+d}"  # Convert to -63/+63
        elif param == 0x2E:  # Pan
            if value < 64:
                return f"L{64 - value}"
            elif value > 64:
                return f"{value - 64}R"
            return "C"
        elif param == 0x1F:  # Ring switch
            return ["OFF", "---", "ON"][value]
        elif param in (0x2E, 0x32):  # Unison and Legato switches
            return "ON" if value else "OFF"
        elif param == 0x31:  # Portamento mode
            return "LEGATO" if value else "NORMAL"
        elif param == 0x3C:  # Unison size
            return str([2, 4, 6, 8][value])  # Convert 0-3 to actual voice count
        elif param == 0x04:  # Envelope loop mode
            return ["OFF", "FREE-RUN", "TEMPO-SYNC"][value]
        elif param == 0x05:  # Envelope loop sync note
            return [
                "16",
                "12",
                "8",
                "4",
                "2",
                "1",
                "3/4",
                "2/3",
                "1/2",
                "3/8",
                "1/3",
                "1/4",
                "3/16",
                "1/6",
                "1/8",
                "3/32",
                "1/12",
                "1/16",
                "1/24",
                "1/32",
            ][value]
        elif param in (0x22, 0x23, 0x24, 0x25):  # LFO depths
            return f"{value - 64:+d}"  # Convert to -63/+63
        elif param == 0x26:  # Mod LFO shape
            return ["TRI", "SIN", "SAW", "SQR", "S&H", "RND"][value]
        elif param == 0x29:  # Mod LFO sync note
            return [
                "16",
                "12",
                "8",
                "4",
                "2",
                "1",
                "3/4",
                "2/3",
                "1/2",
                "3/8",
                "1/3",
                "1/4",
                "3/16",
                "1/6",
                "1/8",
                "3/32",
                "1/12",
                "1/16",
                "1/24",
                "1/32",
            ][value]
        elif param in (0x2C, 0x2D, 0x2E, 0x2F):  # Mod LFO depths
            return f"{value - 64:+d}"  # Convert to -63/+63
        elif param in (0x30, 0x31):  # Aftertouch sensitivities
            return f"{value - 64:+d}"  # Convert to -63/+63
        elif param == 0x34:  # Wave gain
            return ["-6dB", "0dB", "+6dB", "+12dB"][value]
        elif param == 0x35:  # Wave number
            return "OFF" if value == 0 else str(value)
        elif param == 0x3B:  # Mod LFO rate control
            return f"{value - 64:+d}"  # Convert to -63/+63
        elif param == 0x3C:  # Amp level keyfollow
            return f"{((value - 54) * 200 / 20) - 100:+.0f}"  # Convert to -100/+100
        return str(value)


# System Area Structure (0x02)
SYSTEM_COMMON = 0x00  # 00 00 00: System Common parameters
SYSTEM_CONTROLLER = 0x03  # 00 03 00: System Controller parameters


# System Common Parameters (0x02 00)
class SystemCommon(Enum):
    """System Common parameters"""

    MASTER_TUNE = 0x00  # Master Tune (24-2024: -100.0 to +100.0 cents)
    MASTER_KEY_SHIFT = 0x04  # Master Key Shift (40-88: -24 to +24 semitones)
    MASTER_LEVEL = 0x05  # Master Level (0-127)

    # Reserved space (0x06-0x10)

    PROGRAM_CTRL_CH = 0x11  # Program Control Channel (0-16: 1-16, OFF)

    # Reserved space (0x12-0x28)

    RX_PROGRAM_CHANGE = 0x29  # Receive Program Change (0: OFF, 1: ON)
    RX_BANK_SELECT = 0x2A  # Receive Bank Select (0: OFF, 1: ON)

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if param == 0x00:  # Master Tune
            cents = (value - 1024) / 10  # Convert 24-2024 to -100.0/+100.0
            return f"{cents:+.1f} cents"
        elif param == 0x04:  # Master Key Shift
            semitones = value - 64  # Convert 40-88 to -24/+24
            return f"{semitones:+d} st"
        elif param == 0x11:  # Program Control Channel
            return "OFF" if value == 0 else str(value)
        elif param in (0x29, 0x2A):  # Switches
            return "ON" if value else "OFF"
        return str(value)


@dataclass
class SystemCommonMessage(RolandSysEx):
    """System Common parameter message"""

    command: int = DT1_COMMAND_12
    area: int = SYSTEM_AREA  # 0x02: System area
    section: int = SYSTEM_COMMON  # 0x00: Common section
    group: int = 0x00  # Always 0x00
    param: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        """Set up address and data"""
        self.address = [
            self.area,  # System area (0x02)
            self.section,  # Common section (0x00)
            self.group,  # Always 0x00
            self.param,  # Parameter number
        ]
        self.data = [self.value]


# Example usage:
# Set master tune to +50 cents
msg = SystemCommonMessage(
    param=SystemCommon.MASTER_TUNE.value,
    value=1024 + (50 * 10),  # Convert +50.0 cents to 1524
)

# Set master key shift to -12 semitones
msg = SystemCommonMessage(
    param=SystemCommon.MASTER_KEY_SHIFT.value, value=52  # Convert -12 to 52 (64-12)
)

# Set program control channel to 1
msg = SystemCommonMessage(
    param=SystemCommon.PROGRAM_CTRL_CH.value, value=1  # Channel 1
)

# Enable program change reception
msg = SystemCommonMessage(param=SystemCommon.RX_PROGRAM_CHANGE.value, value=1)  # ON


# System Controller Parameters (0x02 03)
class SystemController(Enum):
    """System Controller parameters"""

    TX_PROGRAM_CHANGE = 0x00  # Transmit Program Change (0: OFF, 1: ON)
    TX_BANK_SELECT = 0x01  # Transmit Bank Select (0: OFF, 1: ON)
    KEYBOARD_VELOCITY = 0x02  # Keyboard Velocity (0: REAL, 1-127: Fixed)
    VELOCITY_CURVE = 0x03  # Keyboard Velocity Curve (0: LIGHT, 1: MEDIUM, 2: HEAVY)
    VELOCITY_OFFSET = 0x04  # Keyboard Velocity Curve Offset (54-73: -10 to +9)

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if param in (0x00, 0x01):  # Switches
            return "ON" if value else "OFF"
        elif param == 0x02:  # Keyboard velocity
            return "REAL" if value == 0 else str(value)
        elif param == 0x03:  # Velocity curve
            return ["LIGHT", "MEDIUM", "HEAVY"][value]
        elif param == 0x04:  # Velocity offset
            return f"{value - 64:+d}"  # Convert 54-73 to -10/+9
        return str(value)


@dataclass
class SystemControllerMessage(RolandSysEx):
    """System Controller parameter message"""

    command: int = DT1_COMMAND_12
    area: int = SYSTEM_AREA  # 0x02: System area
    section: int = SYSTEM_CONTROLLER  # 0x03: Controller section
    group: int = 0x00  # Always 0x00
    param: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        """Set up address and data"""
        self.address = [
            self.area,  # System area (0x02)
            self.section,  # Controller section (0x03)
            self.group,  # Always 0x00
            self.param,  # Parameter number
        ]
        self.data = [self.value]


# Example usage:
# Enable program change transmission
msg = SystemControllerMessage(
    param=SystemController.TX_PROGRAM_CHANGE.value, value=1  # ON
)

# Set keyboard velocity to REAL
msg = SystemControllerMessage(
    param=SystemController.KEYBOARD_VELOCITY.value, value=0  # REAL
)

# Set velocity curve to MEDIUM
msg = SystemControllerMessage(
    param=SystemController.VELOCITY_CURVE.value, value=1  # MEDIUM
)

# Set velocity offset to +5
msg = SystemControllerMessage(
    param=SystemController.VELOCITY_OFFSET.value, value=69  # Convert +5 to 69 (64+5)
)

# Temporary Tone Areas (0x19)
TEMP_DIGITAL_TONE = 0x01  # 01 00 00: Temporary SuperNATURAL Synth Tone
TEMP_ANALOG_TONE = 0x02  # 02 00 00: Temporary Analog Synth Tone
TEMP_DRUM_KIT = 0x10  # 10 00 00: Temporary Drum Kit

# Update our existing address offsets
DIGITAL_PART_1 = 0x01  # Digital Synth 1 (SuperNATURAL)
DIGITAL_PART_2 = 0x02  # Digital Synth 2 (SuperNATURAL)
ANALOG_PART = 0x02  # Analog Synth
DRUM_PART = 0x10  # Drum Kit


# Parameter Groups
class ToneGroup(Enum):
    """Tone parameter groups"""

    COMMON = 0x00  # Common parameters
    OSC = 0x01  # Oscillator parameters
    FILTER = 0x02  # Filter parameters
    AMP = 0x03  # Amplifier parameters
    LFO = 0x04  # LFO parameters
    EFFECTS = 0x05  # Effects parameters


# Program Area Structure (0x18)
class ProgramArea(Enum):
    """Program memory areas"""

    COMMON = 0x00  # 00 00 00: Program Common
    VOCAL_FX = 0x01  # 00 01 00: Program Vocal Effect
    EFFECT_1 = 0x02  # 00 02 00: Program Effect 1
    EFFECT_2 = 0x04  # 00 04 00: Program Effect 2
    DELAY = 0x06  # 00 06 00: Program Delay
    REVERB = 0x08  # 00 08 00: Program Reverb

    # Program Parts
    DIGITAL_1_PART = 0x20  # 00 20 00: Digital Synth Part 1
    DIGITAL_2_PART = 0x21  # 00 21 00: Digital Synth Part 2
    ANALOG_PART = 0x22  # 00 22 00: Analog Synth Part
    DRUMS_PART = 0x23  # 00 23 00: Drums Part

    # Program Zones
    DIGITAL_1_ZONE = 0x30  # 00 30 00: Digital Synth Zone 1
    DIGITAL_2_ZONE = 0x31  # 00 31 00: Digital Synth Zone 2
    ANALOG_ZONE = 0x32  # 00 32 00: Analog Synth Zone
    DRUMS_ZONE = 0x33  # 00 33 00: Drums Zone

    CONTROLLER = 0x40  # 00 40 00: Program Controller


# SuperNATURAL Synth Tone Structure (0x19 01/02)
class DigitalToneSection(Enum):
    """SuperNATURAL Synth Tone sections"""

    COMMON = 0x00  # 00 00 00: Common parameters
    PARTIAL_1 = 0x20  # 00 20 00: Partial 1
    PARTIAL_2 = 0x21  # 00 21 00: Partial 2
    PARTIAL_3 = 0x22  # 00 22 00: Partial 3
    MODIFY = 0x50  # 00 50 00: Tone Modify parameters


@dataclass
class DigitalToneMessage(RolandSysEx):
    """SuperNATURAL Synth Tone parameter message"""

    command: int = DT1_COMMAND_12
    area: int = 0x19  # Temporary area
    tone_type: int = 0x01  # Digital tone (0x01 or 0x02)
    section: int = 0x00  # Section from DigitalToneSection
    param: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        """Set up address and data"""
        self.address = [
            self.area,  # Temporary area (0x19)
            self.tone_type,  # Digital 1 or 2 (0x01/0x02)
            self.section,  # Section (Common/Partial/Modify)
            self.param,  # Parameter number
        ]
        self.data = [self.value]


# Example usage:
# Set common parameter
msg = DigitalToneMessage(
    tone_type=TEMP_DIGITAL_TONE,  # Digital 1
    section=DigitalToneSection.COMMON.value,
    param=0x00,  # Common parameter
    value=64,
)

# Set partial parameter
msg = DigitalToneMessage(
    tone_type=TEMP_DIGITAL_TONE,  # Digital 1
    section=DigitalToneSection.PARTIAL_1.value,
    param=0x00,  # Partial parameter
    value=64,
)

# Set modify parameter
msg = DigitalToneMessage(
    tone_type=TEMP_DIGITAL_TONE,  # Digital 1
    section=DigitalToneSection.MODIFY.value,
    param=0x00,  # Modify parameter
    value=64,
)


class DigitalToneCommon:
    """SuperNATURAL Synth Tone Common parameters"""

    # Tone name (12 characters)
    NAME_1 = 0x00  # Character 1 (ASCII 32-127)
    NAME_2 = 0x01  # Character 2
    NAME_3 = 0x02  # Character 3
    NAME_4 = 0x03  # Character 4
    NAME_5 = 0x04  # Character 5
    NAME_6 = 0x05  # Character 6
    NAME_7 = 0x06  # Character 7
    NAME_8 = 0x07  # Character 8
    NAME_9 = 0x08  # Character 9
    NAME_10 = 0x09  # Character 10
    NAME_11 = 0x0A  # Character 11
    NAME_12 = 0x0B  # Character 12

    # Basic parameters
    LEVEL = 0x0C  # Tone Level (0-127)
    PORTAMENTO_SW = 0x12  # Portamento Switch (0-1)
    PORTA_TIME = 0x13  # Portamento Time (0-127)
    MONO_SW = 0x14  # Mono Switch (0-1)
    OCTAVE = 0x15  # Octave Shift (-3/+3)
    BEND_UP = 0x16  # Pitch Bend Range Up (0-24)
    BEND_DOWN = 0x17  # Pitch Bend Range Down (0-24)

    # Partial switches
    PART1_SW = 0x19  # Partial 1 Switch (0-1)
    PART1_SEL = 0x1A  # Partial 1 Select (0-1)
    PART2_SW = 0x1B  # Partial 2 Switch (0-1)
    PART2_SEL = 0x1C  # Partial 2 Select (0-1)
    PART3_SW = 0x1D  # Partial 3 Switch (0-1)
    PART3_SEL = 0x1E  # Partial 3 Select (0-1)

    # Advanced parameters
    RING_SW = 0x1F  # Ring Switch (0: OFF, 1: ---, 2: ON)
    UNISON_SW = 0x2E  # Unison Switch (0-1)
    PORTA_MODE = 0x31  # Portamento Mode (0: NORMAL, 1: LEGATO)
    LEGATO_SW = 0x32  # Legato Switch (0-1)
    ANALOG_FEEL = 0x34  # Analog Feel (0-127)
    WAVE_SHAPE = 0x35  # Wave Shape (0-127)
    CATEGORY = 0x36  # Tone Category (0-127)
    UNISON_SIZE = 0x3C  # Unison Size (0-3: 2,4,6,8 voices)

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if 0x00 <= param <= 0x0B:  # Name characters
            return chr(value) if 32 <= value <= 127 else "?"
        elif param == 0x15:  # Octave shift
            return f"{value - 64:+d}"  # Convert 61-67 to -3/+3
        elif param in (
            0x12,
            0x14,
            0x19,
            0x1A,
            0x1B,
            0x1C,
            0x1D,
            0x1E,
            0x2E,
            0x32,
        ):  # Switches
            return "ON" if value else "OFF"
        elif param == 0x1F:  # Ring switch
            return ["OFF", "---", "ON"][value]
        elif param == 0x31:  # Portamento mode
            return "LEGATO" if value else "NORMAL"
        elif param == 0x3C:  # Unison size
            return str([2, 4, 6, 8][value])  # Convert 0-3 to actual voice count
        return str(value)


class DigitalTonePartial(Enum):
    """Partial parameters for SuperNATURAL Synth Tone"""

    WAVE = 0x00  # Wave number (0-255)
    LEVEL = 0x01  # Partial level (0-127)
    COARSE = 0x02  # Coarse tune (-24 to +24)
    FINE = 0x03  # Fine tune (-50 to +50)
    DETUNE = 0x04  # Detune (-50 to +50)
    ATTACK = 0x05  # Attack time (0-127)
    DECAY = 0x06  # Decay time (0-127)
    SUSTAIN = 0x07  # Sustain level (0-127)
    RELEASE = 0x08  # Release time (0-127)
    PAN = 0x09  # Pan position (-64 to +63)
    FILTER_TYPE = 0x0A  # Filter preset_type (0: OFF, 1: LPF, 2: HPF)
    CUTOFF = 0x0B  # Filter cutoff (0-127)
    RESONANCE = 0x0C  # Filter resonance (0-127)
    ENV_DEPTH = 0x0D  # Filter envelope depth (-63 to +63)
    ENV_VELOCITY = 0x0E  # Filter envelope velocity (-63 to +63)
    ENV_ATTACK = 0x0F  # Filter envelope attack (0-127)
    ENV_DECAY = 0x10  # Filter envelope decay (0-127)
    ENV_SUSTAIN = 0x11  # Filter envelope sustain (0-127)
    ENV_RELEASE = 0x12  # Filter envelope release (0-127)


class DigitalToneModify:
    """SuperNATURAL Synth Tone Modify parameters"""

    ATTACK_SENS = 0x01  # Attack Time Interval Sens (0-127)
    RELEASE_SENS = 0x02  # Release Time Interval Sens (0-127)
    PORTA_SENS = 0x03  # Portamento Time Interval Sens (0-127)
    ENV_LOOP_MODE = 0x04  # Envelope Loop Mode (0-2)
    ENV_LOOP_SYNC = 0x05  # Envelope Loop Sync Note (0-19)
    CHROM_PORTA = 0x06  # Chromatic Portamento (0-1)

    # Envelope Loop Mode values
    LOOP_OFF = 0  # OFF
    LOOP_FREE = 1  # FREE-RUN
    LOOP_SYNC = 2  # TEMPO-SYNC

    # Sync note values (for ENV_LOOP_SYNC)
    SYNC_16 = 0  # 16
    SYNC_12 = 1  # 12
    SYNC_8 = 2  # 8
    SYNC_4 = 3  # 4
    SYNC_2 = 4  # 2
    SYNC_1 = 5  # 1
    SYNC_3_4 = 6  # 3/4
    SYNC_2_3 = 7  # 2/3
    SYNC_1_2 = 8  # 1/2
    SYNC_3_8 = 9  # 3/8
    SYNC_1_3 = 10  # 1/3
    SYNC_1_4 = 11  # 1/4
    SYNC_3_16 = 12  # 3/16
    SYNC_1_6 = 13  # 1/6
    SYNC_1_8 = 14  # 1/8
    SYNC_3_32 = 15  # 3/32
    SYNC_1_12 = 16  # 1/12
    SYNC_1_16 = 17  # 1/16
    SYNC_1_24 = 18  # 1/24
    SYNC_1_32 = 19  # 1/32

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if param == 0x04:  # Envelope Loop Mode
            return ["OFF", "FREE-RUN", "TEMPO-SYNC"][value]
        elif param == 0x05:  # Envelope Loop Sync Note
            notes = [
                "16",
                "12",
                "8",
                "4",
                "2",
                "1",
                "3/4",
                "2/3",
                "1/2",
                "3/8",
                "1/3",
                "1/4",
                "3/16",
                "1/6",
                "1/8",
                "3/32",
                "1/12",
                "1/16",
                "1/24",
                "1/32",
            ]
            return notes[value] if 0 <= value <= 19 else str(value)
        elif param == 0x06:  # Chromatic Portamento
            return "ON" if value else "OFF"
        return str(value)


class EffectType(Enum):
    """Effect types and parameters"""

    # Effect types
    THRU = 0x00
    DISTORTION = 0x01
    FUZZ = 0x02
    COMPRESSOR = 0x03
    BITCRUSHER = 0x04
    FLANGER = 0x05
    PHASER = 0x06
    RING_MOD = 0x07
    SLICER = 0x08

    # Common parameters
    LEVEL = 0x00
    MIX = 0x01

    # Effect-specific parameters
    DRIVE = 0x10
    TONE = 0x11
    ATTACK = 0x12
    RELEASE = 0x13
    THRESHOLD = 0x14
    RATIO = 0x15
    BIT_DEPTH = 0x16
    RATE = 0x17
    DEPTH = 0x18
    FEEDBACK = 0x19
    FREQUENCY = 0x1A
    BALANCE = 0x1B
    PATTERN = 0x1C

    # Send levels
    REVERB_SEND = 0x20
    DELAY_SEND = 0x21
    CHORUS_SEND = 0x22

    # Reverb parameters
    REVERB_TYPE = 0x30
    REVERB_TIME = 0x31
    REVERB_PRE_DELAY = 0x32

    # Delay parameters
    DELAY_TIME = 0x40
    DELAY_FEEDBACK = 0x41
    DELAY_HF_DAMP = 0x42

    # Chorus parameters
    CHORUS_RATE = 0x50
    CHORUS_DEPTH = 0x51
    CHORUS_FEEDBACK = 0x52


class VocalFX(Enum):
    """Vocal effects types and parameters"""

    # Effect types
    VOCODER = 0x00
    AUTO_PITCH = 0x01
    HARMONIST = 0x02

    # Common parameters
    LEVEL = 0x00
    PAN = 0x01
    REVERB_SEND = 0x02
    DELAY_SEND = 0x03

    # Vocoder parameters
    MIC_SENS = 0x10
    CARRIER_MIX = 0x11
    FORMANT = 0x12
    CUTOFF = 0x13
    RESONANCE = 0x14

    # Auto-Pitch parameters
    SCALE = 0x20
    KEY = 0x21
    GENDER = 0x22
    BALANCE = 0x23

    # Harmonist parameters
    HARMONY_1 = 0x30
    HARMONY_2 = 0x31
    HARMONY_3 = 0x32
    DETUNE = 0x33


class VoiceCutoffFilter(Enum):
    """Voice cutoff filter types"""

    THRU = 0x00
    LPF = 0x01
    HPF = 0x02
    BPF = 0x03


class VoiceScale(Enum):
    """Voice scale types"""

    CHROMATIC = 0x00
    MAJOR = 0x01
    MINOR = 0x02
    BLUES = 0x03
    INDIAN = 0x04


class VoiceKey(Enum):
    """Voice keys"""

    C = 0x00
    Db = 0x01
    D = 0x02
    Eb = 0x03
    E = 0x04
    F = 0x05
    Gb = 0x06
    G = 0x07
    Ab = 0x08
    A = 0x09
    Bb = 0x0A
    B = 0x0B


class ArpGrid(Enum):
    """Arpeggio grid values"""

    GRID_4 = 0  # 04_
    GRID_8 = 1  # 08_
    GRID_8L = 2  # 08L
    GRID_8H = 3  # 08H
    GRID_8T = 4  # 08t
    GRID_16 = 5  # 16_
    GRID_16L = 6  # 16L
    GRID_16H = 7  # 16H
    GRID_16T = 8  # 16t


class ArpDuration(Enum):
    """Arpeggio duration values"""

    DUR_30 = 0  # 30%
    DUR_40 = 1  # 40%
    DUR_50 = 2  # 50%
    DUR_60 = 3  # 60%
    DUR_70 = 4  # 70%
    DUR_80 = 5  # 80%
    DUR_90 = 6  # 90%
    DUR_100 = 7  # 100%
    DUR_120 = 8  # 120%
    DUR_FULL = 9  # FULL


class ArpMotif(Enum):
    """Arpeggio motif values"""

    UP_L = 0  # UP/L
    UP_H = 1  # UP/H
    UP_NORM = 2  # UP/_
    DOWN_L = 3  # dn/L
    DOWN_H = 4  # dn/H
    DOWN_NORM = 5  # dn/_
    UP_DOWN_L = 6  # Ud/L
    UP_DOWN_H = 7  # Ud/H
    UP_DOWN_NORM = 8  # Ud/_
    RANDOM_L = 9  # rn/L
    RANDOM_NORM = 10  # rn/_
    PHRASE = 11  # PHRASE


class ArpParameters(Enum):
    """Arpeggiator parameters"""

    GRID = 0x01  # Grid (0-8)
    DURATION = 0x02  # Duration (0-9)
    SWITCH = 0x03  # On/Off (0-1)
    STYLE = 0x05  # Style (0-127)
    MOTIF = 0x06  # Motif (0-11)
    OCTAVE = 0x07  # Octave Range (61-67: -3 to +3)
    ACCENT = 0x09  # Accent Rate (0-100)
    VELOCITY = 0x0A  # Velocity (0-127, 0=REAL)


# SuperNATURAL presets for each address
DIGITAL_SN_PRESETS = [
    "001: JP8 Strings1",
    "002: Soft Pad 1",
    "003: JP8 Strings2",
    "004: JUNO Str 1",
    "005: Oct Strings",
    "006: Brite Str 1",
    "007: Boreal Pad",
    "008: JP8 Strings3",
    "009: JP8 Strings4",
    "010: Hollow Pad 1",
    "011: LFO Pad 1",
    "012: Hybrid Str",
    "013: Awakening 1",
    "014: Cincosoft 1",
    "015: Bright Pad 1",
    "016: Analog Str 1",
    "017: Soft ResoPd1",
    "018: HPF Poly 1",
    "019: BPF Poly",
    "020: Sweep Pad 1",
    "021: Soft Pad 2",
    "022: Sweep JD 1",
    "023: FltSweep Pd1",
    "024: HPF Pad",
    "025: HPF SweepPd1",
    "026: KOff Pad",
    "027: Sweep Pad 2",
    "028: TrnsSweepPad",
    "029: Revalation 1",
    "030: LFO CarvePd1",
    "031: RETROX 139 1",
    "032: LFO ResoPad1",
    "033: PLS Pad 1",
    "034: PLS Pad 2",
    "035: Trip 2 Mars1",
    "036: Reso S&H Pd1",
    "037: SideChainPd1",
    "038: PXZoon 1",
    "039: Psychoscilo1",
    "040: Fantasy 1",
    "041: D-50 Stack 1",
    "042: Organ Pad",
    "043: Bell Pad",
    "044: Dreaming 1",
    "045: Syn Sniper 1",
    "046: Strings 1",
    "047: D-50 Pizz 1",
    "048: Super Saw 1",
    "049: S-SawStacLd1",
    "050: Tekno Lead 1",
    "051: Tekno Lead 2",
    "052: Tekno Lead 3",
    "053: OSC-SyncLd 1",
    "054: WaveShapeLd1",
    "055: JD RingMod 1",
    "056: Buzz Lead 1",
    "057: Buzz Lead 2",
    "058: SawBuzz Ld 1",
    "059: Sqr Buzz Ld1",
    "060: Tekno Lead 4",
    "061: Dist Flt TB1",
    "062: Dist TB Sqr1",
    "063: Glideator 1",
    "064: Vintager 1",
    "065: Hover Lead 1",
    "066: Saw Lead 1",
    "067: Saw+Tri Lead",
    "068: PortaSaw Ld1",
    "069: Reso Saw Ld",
    "070: SawTrap Ld 1",
    "071: Fat GR Lead",
    "072: Pulstar Ld",
    "073: Slow Lead",
    "074: AnaVox Lead",
    "075: Square Ld 1",
    "076: Square Ld 2",
    "077: Sqr Lead 1",
    "078: Sqr Trap Ld1",
    "079: Sine Lead 1",
    "080: Tri Lead",
    "081: Tri Stac Ld1",
    "082: 5th SawLead1",
    "083: Sweet 5th 1",
    "084: 4th Syn Lead",
    "085: Maj Stack Ld",
    "086: MinStack Ld1",
    "087: Chubby Lead1",
    "088: CuttingLead1",
    "089: Seq Bass 1",
    "090: Reso Bass 1",
    "091: TB Bass 1",
    "092: 106 Bass 1",
    "093: FilterEnvBs1",
    "094: JUNO Sqr Bs1",
    "095: Reso Bass 2",
    "096: JUNO Bass",
    "097: MG Bass 1",
    "098: 106 Bass 3",
    "099: Reso Bass 3",
    "100: Detune Bs 1",
    "101: MKS-50 Bass1",
    "102: Sweep Bass",
    "103: MG Bass 2",
    "104: MG Bass 3",
    "105: ResRubber Bs",
    "106: R&B Bass 1",
    "107: Reso Bass 4",
    "108: Wide Bass 1",
    "109: Chow Bass 1",
    "110: Chow Bass 2",
    "111: SqrFilterBs1",
    "112: Reso Bass 5",
    "113: Syn Bass 1",
    "114: ResoSawSynBs",
    "115: Filter Bass1",
    "116: SeqFltEnvBs",
    "117: DnB Bass 1",
    "118: UnisonSynBs1",
    "119: Modular Bs",
    "120: Monster Bs 1",
    "121: Monster Bs 2",
    "122: Monster Bs 3",
    "123: Monster Bs 4",
    "124: Square Bs 1",
    "125: 106 Bass 2",
    "126: 5th Stac Bs1",
    "127: SqrStacSynBs",
    "128: MC-202 Bs",
    "129: TB Bass 2",
    "130: Square Bs 2",
    "131: SH-101 Bs",
    "132: R&B Bass 2",
    "133: MG Bass 4",
    "134: Seq Bass 2",
    "135: Tri Bass 1",
    "136: BPF Syn Bs 2",
    "137: BPF Syn Bs 1",
    "138: Low Bass 1",
    "139: Low Bass 2",
    "140: Kick Bass 1",
    "141: SinDetuneBs1",
    "142: Organ Bass 1",
    "143: Growl Bass 1",
    "144: Talking Bs 1",
    "145: LFO Bass 1",
    "146: LFO Bass 2",
    "147: Crack Bass",
    "148: Wobble Bs 1",
    "149: Wobble Bs 2",
    "150: Wobble Bs 3",
    "151: Wobble Bs 4",
    "152: SideChainBs1",
    "153: SideChainBs2",
    "154: House Bass 1",
    "155: FM Bass",
    "156: 4Op FM Bass1",
    "157: Ac. Bass",
    "158: Fingerd Bs 1",
    "159: Picked Bass",
    "160: Fretless Bs",
    "161: Slap Bass 1",
    "162: JD Piano 1",
    "163: E. Grand 1",
    "164: Trem EP 1",
    "165: FM E.Piano 1",
    "166: FM E.Piano 2",
    "167: Vib Wurly 1",
    "168: Pulse Clav",
    "169: Clav",
    "170: 70's E.Organ",
    "171: House Org 1",
    "172: House Org 2",
    "173: Bell 1",
    "174: Bell 2",
    "175: Organ Bell",
    "176: Vibraphone 1",
    "177: Steel Drum",
    "178: Harp 1",
    "179: Ac. Guitar",
    "180: Bright Strat",
    "181: Funk Guitar1",
    "182: Jazz Guitar",
    "183: Dist Guitar1",
    "184: D. Mute Gtr1",
    "185: E. Sitar",
    "186: Sitar Drone",
    "187: FX 1",
    "188: FX 2",
    "189: FX 3",
    "190: Tuned Winds1",
    "191: Bend Lead 1",
    "192: RiSER 1",
    "193: Rising SEQ 1",
    "194: Scream Saw",
    "195: Noise SEQ 1",
    "196: Syn Vox 1",
    "197: JD SoftVox",
    "198: Vox Pad",
    "199: VP-330 Chr",
    "200: Orch Hit",
    "201: Philly Hit",
    "202: House Hit",
    "203: O'Skool Hit1",
    "204: Punch Hit",
    "205: Tao Hit",
    "206: SEQ Saw 1",
    "207: SEQ Sqr",
    "208: SEQ Tri 1",
    "209: SEQ 1",
    "210: SEQ 2",
    "211: SEQ 3",
    "212: SEQ 4",
    "213: Sqr Reso Plk",
    "214: Pluck Synth1",
    "215: Paperclip 1",
    "216: Sonar Pluck1",
    "217: SqrTrapPlk 1",
    "218: TB Saw Seq 1",
    "219: TB Sqr Seq 1",
    "220: JUNO Key",
    "221: Analog Poly1",
    "222: Analog Poly2",
    "223: Analog Poly3",
    "224: Analog Poly4",
    "225: JUNO Octavr1",
    "226: EDM Synth 1",
    "227: Super Saw 2",
    "228: S-Saw Poly",
    "229: Trance Key 1",
    "230: S-Saw Pad 1",
    "231: 7th Stac Syn",
    "232: S-SawStc Syn",
    "233: Trance Key 2",
    "234: Analog Brass",
    "235: Reso Brass",
    "236: Soft Brass 1",
    "237: FM Brass",
    "238: Syn Brass 1",
    "239: Syn Brass 2",
    "240: JP8 Brass",
    "241: Soft SynBrs1",
    "242: Soft SynBrs2",
    "243: EpicSlow Brs",
    "244: JUNO Brass",
    "245: Poly Brass",
    "246: Voc:Ensemble",
    "247: Voc:5thStack",
    "248: Voc:Robot",
    "249: Voc:Saw",
    "250: Voc:Sqr",
    "251: Voc:Rise Up",
    "252: Voc:Auto Vib",
    "253: Voc:PitchEnv",
    "254: Voc:VP-330",
    "255: Voc:Noise",
]

DRUM_SN_PRESETS = [
    "001: Studio Standard",
    "002: Studio Rock",
    "003: Studio Jazz",
    "004: Studio Dance",
    "005: Studio R&B",
    "006: Studio Latin",
    "007: Power Kit",
    "008: Rock Kit",
    "009: Jazz Kit",
    "010: Brush Kit",
    "011: Orchestra Kit",
    "012: Dance Kit",
    "013: House Kit",
    "014: Hip Hop Kit",
    "015: R&B Kit",
    "016: Latin Kit",
    "017: World Kit",
    "018: Electronic Kit",
    "019: TR-808 Kit",
    "020: TR-909 Kit",
    "021: CR-78 Kit",
    "022: TR-606 Kit",
    "023: TR-707 Kit",
    "024: TR-727 Kit",
    "025: Percussion Kit",
    "026: SFX Kit",
    "027: User Kit 1",
    "028: User Kit 2",
    "029: User Kit 3",
    "030: User Kit 4",
]


class AnalogLFO(Enum):
    """LFO shape values"""

    TRIANGLE = 0
    SINE = 1
    SAW = 2
    SQUARE = 3
    SAMPLE_HOLD = 4
    RANDOM = 5


class AnalogLFOSync(Enum):
    """LFO tempo sync note values"""

    NOTE_16 = 0  # 16 bars
    NOTE_12 = 1  # 12 bars
    NOTE_8 = 2  # 8 bars
    NOTE_4 = 3  # 4 bars
    NOTE_2 = 4  # 2 bars
    NOTE_1 = 5  # 1 bar
    NOTE_3_4 = 6  # 3/4
    NOTE_2_3 = 7  # 2/3
    NOTE_1_2 = 8  # 1/2
    NOTE_3_8 = 9  # 3/8
    NOTE_1_3 = 10  # 1/3
    NOTE_1_4 = 11  # 1/4
    NOTE_3_16 = 12  # 3/16
    NOTE_1_6 = 13  # 1/6
    NOTE_1_8 = 14  # 1/8
    NOTE_3_32 = 15  # 3/32
    NOTE_1_12 = 16  # 1/12
    NOTE_1_16 = 17  # 1/16
    NOTE_1_24 = 18  # 1/24
    NOTE_1_32 = 19  # 1/32


class AnalogOscWaveform(Enum):
    """Analog oscillator waveform types"""

    SAW = 0
    TRIANGLE = 1
    PW_SQUARE = 2


class AnalogSubOscType(Enum):
    """Analog sub oscillator types"""

    OFF = 0
    TYPE_1 = 1
    TYPE_2 = 2


class AnalogFilterType(Enum):
    """Analog filter types"""

    BYPASS = 0
    LPF = 1


class AnalogParameter(Enum):
    """Analog synth parameter addresses and ranges"""

    # Oscillator parameters (0x16-0x1F)
    OSC1_WAVE = 0x16  # OSC Waveform (0-2: SAW, TRI, PW-SQR)
    OSC1_PITCH = 0x17  # OSC Pitch Coarse (40-88: maps to -24 - +24)
    OSC1_FINE = 0x18  # OSC Pitch Fine (14-114: maps to -50 - +50)
    OSC1_PW = 0x19  # OSC Pulse Width (0-127)
    OSC1_PWM = 0x1A  # OSC Pulse Width Mod Depth (0-127)
    OSC_PITCH_VELO = 0x1B  # OSC Pitch Env Velocity Sens (1-127: maps to -63 - +63)
    OSC_PITCH_ATK = 0x1C  # OSC Pitch Env Attack Time (0-127)
    OSC_PITCH_DEC = 0x1D  # OSC Pitch Env Decay (0-127)
    OSC_PITCH_DEPTH = 0x1E  # OSC Pitch Env Depth (1-127: maps to -63 - +63)
    SUB_OSC_TYPE = 0x1F  # Sub Oscillator Type (0-2: OFF, OCT-1, OCT-2)

    @staticmethod
    def validate_value(param: int, value: int) -> bool:
        """Validate parameter value is within allowed range based on MIDI spec"""
        ranges = {
            0x16: (0, 2),  # OSC Waveform: 3-bit value (0-2)
            0x17: (40, 88),  # OSC Pitch Coarse: 7-bit value (40-88)
            0x18: (14, 114),  # OSC Pitch Fine: 7-bit value (14-114)
            0x19: (0, 127),  # OSC Pulse Width: 7-bit value (0-127)
            0x1A: (0, 127),  # PWM Depth: 7-bit value (0-127)
            0x1B: (1, 127),  # Pitch Env Velocity: 7-bit value (1-127)
            0x1C: (0, 127),  # Pitch Env Attack: 7-bit value (0-127)
            0x1D: (0, 127),  # Pitch Env Decay: 7-bit value (0-127)
            0x1E: (1, 127),  # Pitch Env Depth: 7-bit value (1-127)
            0x1F: (0, 2),  # Sub OSC Type: 2-bit value (0-2)
        }

        if param in ranges:
            min_val, max_val = ranges[param]
            return min_val <= value <= max_val
        return True  # Allow other parameters to pass through

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw MIDI value to display value based on parameter preset_type"""
        display_maps = {
            0x16: ["SAW", "TRI", "PW-SQR"],  # Direct mapping for waveforms
            0x17: lambda x: f"{x - 64:+d}",  # -24 to +24 (centered at 64)
            0x18: lambda x: f"{x - 64:+d}",  # -50 to +50 (centered at 64)
            0x1B: lambda x: f"{x - 64:+d}",  # -63 to +63 (centered at 64)
            0x1E: lambda x: f"{x - 64:+d}",  # -63 to +63 (centered at 64)
            0x1F: ["OFF", "OCT-1", "OCT-2"],  # Direct mapping for sub osc preset_type
        }

        if param in display_maps:
            mapper = display_maps[param]
            if isinstance(mapper, list):
                return mapper[value] if 0 <= value < len(mapper) else str(value)
            elif callable(mapper):
                return mapper(value)
        return str(value)


class DigitalParameter(Enum):
    """Digital synth parameter addresses and ranges"""

    # Tone name parameters (0x00-0x0B)
    TONE_NAME_1 = 0x00  # ASCII 32-127
    TONE_NAME_2 = 0x01
    TONE_NAME_3 = 0x02
    TONE_NAME_4 = 0x03
    TONE_NAME_5 = 0x04
    TONE_NAME_6 = 0x05
    TONE_NAME_7 = 0x06
    TONE_NAME_8 = 0x07
    TONE_NAME_9 = 0x08
    TONE_NAME_10 = 0x09
    TONE_NAME_11 = 0x0A
    TONE_NAME_12 = 0x0B

    # Common parameters (0x0C-0x18)
    TONE_LEVEL = 0x0C  # 0-127
    PORTAMENTO_SW = 0x12  # 0-1 (OFF/ON)
    PORTAMENTO_TIME = 0x13  # 0-127
    MONO_SW = 0x14  # 0-1 (OFF/ON)
    OCTAVE_SHIFT = 0x15  # 61-67 (-3 to +3)
    BEND_RANGE_UP = 0x16  # 0-24 semitones
    BEND_RANGE_DOWN = 0x17  # 0-24 semitones

    # Partial parameters (0x20-0x2F)
    PARTIAL_SWITCH = 0x20  # 0-1 (OFF/ON)
    PARTIAL_LEVEL = 0x21  # 0-127
    PARTIAL_COARSE = 0x22  # 40-88 (-24 to +24)
    PARTIAL_FINE = 0x23  # 14-114 (-50 to +50)
    WAVE_SHAPE = 0x24  # 0-127
    PULSE_WIDTH = 0x25  # 0-127
    PWM_DEPTH = 0x26  # 0-127
    SUPER_SAW_DEPTH = 0x27  # 0-127
    FILTER_TYPE = 0x28  # 0-3 (OFF,LPF,BPF,HPF)
    CUTOFF = 0x29  # 0-127
    RESONANCE = 0x2A  # 0-127
    FILTER_ENV = 0x2B  # 1-127 (-63 to +63)
    FILTER_KEY = 0x2C  # 0-127
    AMP_ENV = 0x2D  # 0-127
    PAN = 0x2E  # 0-127 (L64-63R)
    RING_SW = 0x1F  # 0-2 (OFF, ---, ON)

    # Partial switches (0x19-0x1E)
    PARTIAL1_SWITCH = 0x19  # 0-1 (OFF/ON)
    PARTIAL1_SELECT = 0x1A  # 0-1 (OFF/ON)
    PARTIAL2_SWITCH = 0x1B  # 0-1 (OFF/ON)
    PARTIAL2_SELECT = 0x1C  # 0-1 (OFF/ON)
    PARTIAL3_SWITCH = 0x1D  # 0-1 (OFF/ON)
    PARTIAL3_SELECT = 0x1E  # 0-1 (OFF/ON)

    # Additional common parameters (0x2E-0x3C)
    UNISON_SW = 0x2E  # 0-1 (OFF/ON)
    PORTAMENTO_MODE = 0x31  # 0-1 (NORMAL/LEGATO)
    LEGATO_SW = 0x32  # 0-1 (OFF/ON)
    ANALOG_FEEL = 0x34  # 0-127
    WAVE_SHAPE_COMMON = 0x35  # 0-127 (renamed from WAVE_SHAPE)
    TONE_CATEGORY = 0x36  # 0-127
    UNISON_SIZE = 0x3C  # 0-3 (2,4,6,8 voices)

    # Modify parameters (0x01-0x06)
    ATTACK_TIME_SENS = 0x01  # 0-127
    RELEASE_TIME_SENS = 0x02  # 0-127
    PORTA_TIME_SENS = 0x03  # 0-127
    ENV_LOOP_MODE = 0x04  # 0-2 (OFF, FREE-RUN, TEMPO-SYNC)
    ENV_LOOP_SYNC = 0x05  # 0-19 (sync note values)
    CHROM_PORTA = 0x06  # 0-1 (OFF/ON)

    # Partial oscillator parameters (0x00-0x09)
    OSC_WAVE = 0x00  # 0-7 (SAW, SQR, PW-SQR, TRI, SINE, NOISE, SUPER-SAW, PCM)
    OSC_VARIATION = 0x01  # 0-2 (A, B, C)
    OSC_PITCH = 0x03  # 40-88 (-24 to +24)
    OSC_DETUNE = 0x04  # 14-114 (-50 to +50)
    OSC_PWM_DEPTH = 0x05  # 0-127
    OSC_PW = 0x06  # 0-127
    OSC_PITCH_ATK = 0x07  # 0-127
    OSC_PITCH_DEC = 0x08  # 0-127
    OSC_PITCH_DEPTH = 0x09  # 1-127 (-63 to +63)

    # Filter parameters (0x0A-0x14)
    FILTER_MODE = 0x0A  # 0-7 (BYPASS, LPF, HPF, BPF, PKG, LPF2, LPF3, LPF4)
    FILTER_SLOPE = 0x0B  # 0-1 (-12, -24 dB)
    FILTER_CUTOFF = 0x0C  # 0-127
    FILTER_KEYFOLLOW = 0x0D  # 54-74 (-100 to +100)
    FILTER_ENV_VELO = 0x0E  # 1-127 (-63 to +63)
    FILTER_RESONANCE = 0x0F  # 0-127
    FILTER_ENV_ATK = 0x10  # 0-127
    FILTER_ENV_DEC = 0x11  # 0-127
    FILTER_ENV_SUS = 0x12  # 0-127
    FILTER_ENV_REL = 0x13  # 0-127
    FILTER_ENV_DEPTH = 0x14  # 1-127 (-63 to +63)

    # Amplifier parameters (0x15-0x1B)
    AMP_LEVEL = 0x15  # 0-127
    AMP_VELO_SENS = 0x16  # 1-127 (-63 to +63)
    AMP_ENV_ATK = 0x17  # 0-127
    AMP_ENV_DEC = 0x18  # 0-127
    AMP_ENV_SUS = 0x19  # 0-127
    AMP_ENV_REL = 0x1A  # 0-127
    AMP_PAN = 0x1B  # 0-127 (L64-63R)

    # LFO parameters (0x1C-0x25)
    LFO_SHAPE = 0x1C  # 0-5 (TRI, SIN, SAW, SQR, S&H, RND)
    LFO_RATE = 0x1D  # 0-127
    LFO_SYNC_SW = 0x1E  # 0-1 (OFF/ON)
    LFO_SYNC_NOTE = 0x1F  # 0-19 (sync note values)
    LFO_FADE = 0x20  # 0-127
    LFO_KEY_TRIG = 0x21  # 0-1 (OFF/ON)
    LFO_PITCH_DEPTH = 0x22  # 1-127 (-63 to +63)
    LFO_FILTER_DEPTH = 0x23  # 1-127 (-63 to +63)
    LFO_AMP_DEPTH = 0x24  # 1-127 (-63 to +63)
    LFO_PAN_DEPTH = 0x25  # 1-127 (-63 to +63)

    # Modulation LFO parameters (0x26-0x2F)
    MOD_LFO_SHAPE = 0x26  # 0-5 (TRI, SIN, SAW, SQR, S&H, RND)
    MOD_LFO_RATE = 0x27  # 0-127
    MOD_LFO_SYNC_SW = 0x28  # 0-1 (OFF/ON)
    MOD_LFO_SYNC_NOTE = 0x29  # 0-19 (sync note values)
    OSC_PW_SHIFT = 0x2A  # 0-127
    MOD_LFO_PITCH = 0x2C  # 1-127 (-63 to +63)
    MOD_LFO_FILTER = 0x2D  # 1-127 (-63 to +63)
    MOD_LFO_AMP = 0x2E  # 1-127 (-63 to +63)
    MOD_LFO_PAN = 0x2F  # 1-127 (-63 to +63)

    # Aftertouch parameters (0x30-0x31)
    CUTOFF_AFTERTOUCH = 0x30  # 1-127 (-63 to +63)
    LEVEL_AFTERTOUCH = 0x31  # 1-127 (-63 to +63)

    # Additional oscillator parameters (0x34-0x35)
    WAVE_GAIN = 0x34  # 0-3 (-6, 0, +6, +12 dB)
    WAVE_NUMBER = 0x35  # 0-16384 (OFF, 1-16384)

    # Filter and modulation parameters (0x39-0x3C)
    HPF_CUTOFF = 0x39  # 0-127
    SUPER_SAW_DETUNE = 0x3A  # 0-127
    MOD_LFO_RATE_CTRL = 0x3B  # 1-127 (-63 to +63)
    AMP_LEVEL_KEYFOLLOW = 0x3C  # 54-74 (-100 to +100)

    @staticmethod
    def validate_value(param: int, value: int) -> bool:
        """Validate parameter value is within allowed range"""
        ranges = {
            # Tone name (0x00-0x0B): ASCII 32-127
            range(0x00, 0x0C): lambda v: 32 <= v <= 127,
            # Level: 0-127
            0x0C: lambda v: 0 <= v <= 127,
            # Switches: 0-1
            0x12: lambda v: v in (0, 1),  # Portamento
            0x14: lambda v: v in (0, 1),  # Mono
            # Portamento time: 0-127
            0x13: lambda v: 0 <= v <= 127,
            # Octave shift: 61-67 (-3 to +3)
            0x15: lambda v: 61 <= v <= 67,
            # Pitch bend ranges: 0-24
            0x16: lambda v: 0 <= v <= 24,
            0x17: lambda v: 0 <= v <= 24,
        }

        # Find matching range
        for param_range, validator in ranges.items():
            if isinstance(param_range, range):
                if param in param_range:
                    return validator(value)
            elif param == param_range:
                return validator(value)

        return True  # Allow other parameters to pass through

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if 0x00 <= param <= 0x0B:  # Tone name
            return chr(value)
        elif param == 0x15:  # Octave shift
            return f"{value - 64:+d}"  # Convert to -3 to +3
        elif param in (
            0x12,
            0x14,
            0x20,
            0x2F,
            0x19,
            0x1A,
            0x1B,
            0x1C,
            0x1D,
            0x1E,
        ):  # All switches
            return "ON" if value else "OFF"
        elif param == 0x22:  # Coarse tune
            return f"{value - 64:+d}"  # Convert to -24/+24
        elif param == 0x23:  # Fine tune
            return f"{value - 64:+d}"  # Convert to -50/+50
        elif param == 0x28:  # Filter preset_type
            return ["OFF", "LPF", "BPF", "HPF"][value]
        elif param == 0x2B:  # Filter env
            return f"{value - 64:+d}"  # Convert to -63/+63
        elif param == 0x2E:  # Pan
            if value < 64:
                return f"L{64 - value}"
            elif value > 64:
                return f"{value - 64}R"
            return "C"
        elif param == 0x1F:  # Ring switch
            return ["OFF", "---", "ON"][value]
        elif param in (0x2E, 0x32):  # Unison and Legato switches
            return "ON" if value else "OFF"
        elif param == 0x31:  # Portamento mode
            return "LEGATO" if value else "NORMAL"
        elif param == 0x3C:  # Unison size
            return str([2, 4, 6, 8][value])  # Convert 0-3 to actual voice count
        elif param == 0x04:  # Envelope loop mode
            return ["OFF", "FREE-RUN", "TEMPO-SYNC"][value]
        elif param == 0x05:  # Envelope loop sync note
            return [
                "16",
                "12",
                "8",
                "4",
                "2",
                "1",
                "3/4",
                "2/3",
                "1/2",
                "3/8",
                "1/3",
                "1/4",
                "3/16",
                "1/6",
                "1/8",
                "3/32",
                "1/12",
                "1/16",
                "1/24",
                "1/32",
            ][value]
        elif param in (0x22, 0x23, 0x24, 0x25):  # LFO depths
            return f"{value - 64:+d}"  # Convert to -63/+63
        elif param == 0x26:  # Mod LFO shape
            return ["TRI", "SIN", "SAW", "SQR", "S&H", "RND"][value]
        elif param == 0x29:  # Mod LFO sync note
            return [
                "16",
                "12",
                "8",
                "4",
                "2",
                "1",
                "3/4",
                "2/3",
                "1/2",
                "3/8",
                "1/3",
                "1/4",
                "3/16",
                "1/6",
                "1/8",
                "3/32",
                "1/12",
                "1/16",
                "1/24",
                "1/32",
            ][value]
        elif param in (0x2C, 0x2D, 0x2E, 0x2F):  # Mod LFO depths
            return f"{value - 64:+d}"  # Convert to -63/+63
        elif param in (0x30, 0x31):  # Aftertouch sensitivities
            return f"{value - 64:+d}"  # Convert to -63/+63
        elif param == 0x34:  # Wave gain
            return ["-6dB", "0dB", "+6dB", "+12dB"][value]
        elif param == 0x35:  # Wave number
            return "OFF" if value == 0 else str(value)
        elif param == 0x3B:  # Mod LFO rate control
            return f"{value - 64:+d}"  # Convert to -63/+63
        elif param == 0x3C:  # Amp level keyfollow
            return f"{((value - 54) * 200 / 20) - 100:+.0f}"  # Convert to -100/+100
        return str(value)


# System Area Structure (0x02)
SYSTEM_COMMON = 0x00  # 00 00 00: System Common parameters
SYSTEM_CONTROLLER = 0x03  # 00 03 00: System Controller parameters


# System Common Parameters (0x02 00)
class SystemCommon(Enum):
    """System Common parameters"""

    MASTER_TUNE = 0x00  # Master Tune (24-2024: -100.0 to +100.0 cents)
    MASTER_KEY_SHIFT = 0x04  # Master Key Shift (40-88: -24 to +24 semitones)
    MASTER_LEVEL = 0x05  # Master Level (0-127)

    # Reserved space (0x06-0x10)

    PROGRAM_CTRL_CH = 0x11  # Program Control Channel (0-16: 1-16, OFF)

    # Reserved space (0x12-0x28)

    RX_PROGRAM_CHANGE = 0x29  # Receive Program Change (0: OFF, 1: ON)
    RX_BANK_SELECT = 0x2A  # Receive Bank Select (0: OFF, 1: ON)

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if param == 0x00:  # Master Tune
            cents = (value - 1024) / 10  # Convert 24-2024 to -100.0/+100.0
            return f"{cents:+.1f} cents"
        elif param == 0x04:  # Master Key Shift
            semitones = value - 64  # Convert 40-88 to -24/+24
            return f"{semitones:+d} st"
        elif param == 0x11:  # Program Control Channel
            return "OFF" if value == 0 else str(value)
        elif param in (0x29, 0x2A):  # Switches
            return "ON" if value else "OFF"
        return str(value)


@dataclass
class SystemCommonMessage(RolandSysEx):
    """System Common parameter message"""

    command: int = DT1_COMMAND_12
    area: int = SYSTEM_AREA  # 0x02: System area
    section: int = SYSTEM_COMMON  # 0x00: Common section
    group: int = 0x00  # Always 0x00
    param: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        """Set up address and data"""
        self.address = [
            self.area,  # System area (0x02)
            self.section,  # Common section (0x00)
            self.group,  # Always 0x00
            self.param,  # Parameter number
        ]
        self.data = [self.value]


# Example usage:
# Set master tune to +50 cents
msg = SystemCommonMessage(
    param=SystemCommon.MASTER_TUNE.value,
    value=1024 + (50 * 10),  # Convert +50.0 cents to 1524
)

# Set master key shift to -12 semitones
msg = SystemCommonMessage(
    param=SystemCommon.MASTER_KEY_SHIFT.value, value=52  # Convert -12 to 52 (64-12)
)

# Set program control channel to 1
msg = SystemCommonMessage(
    param=SystemCommon.PROGRAM_CTRL_CH.value, value=1  # Channel 1
)

# Enable program change reception
msg = SystemCommonMessage(param=SystemCommon.RX_PROGRAM_CHANGE.value, value=1)  # ON


# System Controller Parameters (0x02 03)
class SystemController(Enum):
    """System Controller parameters"""

    TX_PROGRAM_CHANGE = 0x00  # Transmit Program Change (0: OFF, 1: ON)
    TX_BANK_SELECT = 0x01  # Transmit Bank Select (0: OFF, 1: ON)
    KEYBOARD_VELOCITY = 0x02  # Keyboard Velocity (0: REAL, 1-127: Fixed)
    VELOCITY_CURVE = 0x03  # Keyboard Velocity Curve (0: LIGHT, 1: MEDIUM, 2: HEAVY)
    VELOCITY_OFFSET = 0x04  # Keyboard Velocity Curve Offset (54-73: -10 to +9)

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if param in (0x00, 0x01):  # Switches
            return "ON" if value else "OFF"
        elif param == 0x02:  # Keyboard velocity
            return "REAL" if value == 0 else str(value)
        elif param == 0x03:  # Velocity curve
            return ["LIGHT", "MEDIUM", "HEAVY"][value]
        elif param == 0x04:  # Velocity offset
            return f"{value - 64:+d}"  # Convert 54-73 to -10/+9
        return str(value)


@dataclass
class SystemControllerMessage(RolandSysEx):
    """System Controller parameter message"""

    command: int = DT1_COMMAND_12
    area: int = SYSTEM_AREA  # 0x02: System area
    section: int = SYSTEM_CONTROLLER  # 0x03: Controller section
    group: int = 0x00  # Always 0x00
    param: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        """Set up address and data"""
        self.address = [
            self.area,  # System area (0x02)
            self.section,  # Controller section (0x03)
            self.group,  # Always 0x00
            self.param,  # Parameter number
        ]
        self.data = [self.value]


# Example usage:
# Enable program change transmission
msg = SystemControllerMessage(
    param=SystemController.TX_PROGRAM_CHANGE.value, value=1  # ON
)

# Set keyboard velocity to REAL
msg = SystemControllerMessage(
    param=SystemController.KEYBOARD_VELOCITY.value, value=0  # REAL
)

# Set velocity curve to MEDIUM
msg = SystemControllerMessage(
    param=SystemController.VELOCITY_CURVE.value, value=1  # MEDIUM
)

# Set velocity offset to +5
msg = SystemControllerMessage(
    param=SystemController.VELOCITY_OFFSET.value, value=69  # Convert +5 to 69 (64+5)
)

# Temporary Tone Areas (0x19)
TEMP_DIGITAL_TONE = 0x01  # 01 00 00: Temporary SuperNATURAL Synth Tone
TEMP_ANALOG_TONE = 0x02  # 02 00 00: Temporary Analog Synth Tone
TEMP_DRUM_KIT = 0x10  # 10 00 00: Temporary Drum Kit

# Update our existing address offsets
DIGITAL_PART_1 = 0x01  # Digital Synth 1 (SuperNATURAL)
DIGITAL_PART_2 = 0x02  # Digital Synth 2 (SuperNATURAL)
ANALOG_PART = 0x02  # Analog Synth
DRUM_PART = 0x10  # Drum Kit


# Parameter Groups
class ToneGroup(Enum):
    """Tone parameter groups"""

    COMMON = 0x00  # Common parameters
    OSC = 0x01  # Oscillator parameters
    FILTER = 0x02  # Filter parameters
    AMP = 0x03  # Amplifier parameters
    LFO = 0x04  # LFO parameters
    EFFECTS = 0x05  # Effects parameters


# Program Area Structure (0x18)
class ProgramArea(Enum):
    """Program memory areas"""

    COMMON = 0x00  # 00 00 00: Program Common
    VOCAL_FX = 0x01  # 00 01 00: Program Vocal Effect
    EFFECT_1 = 0x02  # 00 02 00: Program Effect 1
    EFFECT_2 = 0x04  # 00 04 00: Program Effect 2
    DELAY = 0x06  # 00 06 00: Program Delay
    REVERB = 0x08  # 00 08 00: Program Reverb

    # Program Parts
    DIGITAL_1_PART = 0x20  # 00 20 00: Digital Synth Part 1
    DIGITAL_2_PART = 0x21  # 00 21 00: Digital Synth Part 2
    ANALOG_PART = 0x22  # 00 22 00: Analog Synth Part
    DRUMS_PART = 0x23  # 00 23 00: Drums Part

    # Program Zones
    DIGITAL_1_ZONE = 0x30  # 00 30 00: Digital Synth Zone 1
    DIGITAL_2_ZONE = 0x31  # 00 31 00: Digital Synth Zone 2
    ANALOG_ZONE = 0x32  # 00 32 00: Analog Synth Zone
    DRUMS_ZONE = 0x33  # 00 33 00: Drums Zone

    CONTROLLER = 0x40  # 00 40 00: Program Controller


# SuperNATURAL Synth Tone Structure (0x19 01/02)
class DigitalToneSection(Enum):
    """SuperNATURAL Synth Tone sections"""

    COMMON = 0x00  # 00 00 00: Common parameters
    PARTIAL_1 = 0x20  # 00 20 00: Partial 1
    PARTIAL_2 = 0x21  # 00 21 00: Partial 2
    PARTIAL_3 = 0x22  # 00 22 00: Partial 3
    MODIFY = 0x50  # 00 50 00: Tone Modify parameters


@dataclass
class DigitalToneMessage(RolandSysEx):
    """SuperNATURAL Synth Tone parameter message"""

    command: int = DT1_COMMAND_12
    area: int = 0x19  # Temporary area
    tone_type: int = 0x01  # Digital tone (0x01 or 0x02)
    section: int = 0x00  # Section from DigitalToneSection
    param: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        """Set up address and data"""
        self.address = [
            self.area,  # Temporary area (0x19)
            self.tone_type,  # Digital 1 or 2 (0x01/0x02)
            self.section,  # Section (Common/Partial/Modify)
            self.param,  # Parameter number
        ]
        self.data = [self.value]


# Example usage:
# Set common parameter
msg = DigitalToneMessage(
    tone_type=TEMP_DIGITAL_TONE,  # Digital 1
    section=DigitalToneSection.COMMON.value,
    param=0x00,  # Common parameter
    value=64,
)

# Set partial parameter
msg = DigitalToneMessage(
    tone_type=TEMP_DIGITAL_TONE,  # Digital 1
    section=DigitalToneSection.PARTIAL_1.value,
    param=0x00,  # Partial parameter
    value=64,
)

# Set modify parameter
msg = DigitalToneMessage(
    tone_type=TEMP_DIGITAL_TONE,  # Digital 1
    section=DigitalToneSection.MODIFY.value,
    param=0x00,  # Modify parameter
    value=64,
)


class DigitalToneCommon:
    """SuperNATURAL Synth Tone Common parameters"""

    # Tone name (12 characters)
    NAME_1 = 0x00  # Character 1 (ASCII 32-127)
    NAME_2 = 0x01  # Character 2
    NAME_3 = 0x02  # Character 3
    NAME_4 = 0x03  # Character 4
    NAME_5 = 0x04  # Character 5
    NAME_6 = 0x05  # Character 6
    NAME_7 = 0x06  # Character 7
    NAME_8 = 0x07  # Character 8
    NAME_9 = 0x08  # Character 9
    NAME_10 = 0x09  # Character 10
    NAME_11 = 0x0A  # Character 11
    NAME_12 = 0x0B  # Character 12

    # Basic parameters
    LEVEL = 0x0C  # Tone Level (0-127)
    PORTAMENTO_SW = 0x12  # Portamento Switch (0-1)
    PORTA_TIME = 0x13  # Portamento Time (0-127)
    MONO_SW = 0x14  # Mono Switch (0-1)
    OCTAVE = 0x15  # Octave Shift (-3/+3)
    BEND_UP = 0x16  # Pitch Bend Range Up (0-24)
    BEND_DOWN = 0x17  # Pitch Bend Range Down (0-24)

    # Partial switches
    PART1_SW = 0x19  # Partial 1 Switch (0-1)
    PART1_SEL = 0x1A  # Partial 1 Select (0-1)
    PART2_SW = 0x1B  # Partial 2 Switch (0-1)
    PART2_SEL = 0x1C  # Partial 2 Select (0-1)
    PART3_SW = 0x1D  # Partial 3 Switch (0-1)
    PART3_SEL = 0x1E  # Partial 3 Select (0-1)

    # Advanced parameters
    RING_SW = 0x1F  # Ring Switch (0: OFF, 1: ---, 2: ON)
    UNISON_SW = 0x2E  # Unison Switch (0-1)
    PORTA_MODE = 0x31  # Portamento Mode (0: NORMAL, 1: LEGATO)
    LEGATO_SW = 0x32  # Legato Switch (0-1)
    ANALOG_FEEL = 0x34  # Analog Feel (0-127)
    WAVE_SHAPE = 0x35  # Wave Shape (0-127)
    CATEGORY = 0x36  # Tone Category (0-127)
    UNISON_SIZE = 0x3C  # Unison Size (0-3: 2,4,6,8 voices)

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if 0x00 <= param <= 0x0B:  # Name characters
            return chr(value) if 32 <= value <= 127 else "?"
        elif param == 0x15:  # Octave shift
            return f"{value - 64:+d}"  # Convert 61-67 to -3/+3
        elif param in (
            0x12,
            0x14,
            0x19,
            0x1A,
            0x1B,
            0x1C,
            0x1D,
            0x1E,
            0x2E,
            0x32,
        ):  # Switches
            return "ON" if value else "OFF"
        elif param == 0x1F:  # Ring switch
            return ["OFF", "---", "ON"][value]
        elif param == 0x31:  # Portamento mode
            return "LEGATO" if value else "NORMAL"
        elif param == 0x3C:  # Unison size
            return str([2, 4, 6, 8][value])  # Convert 0-3 to actual voice count
        return str(value)


class DigitalTonePartial(Enum):
    """Partial parameters for SuperNATURAL Synth Tone"""

    WAVE = 0x00  # Wave number (0-255)
    LEVEL = 0x01  # Partial level (0-127)
    COARSE = 0x02  # Coarse tune (-24 to +24)
    FINE = 0x03  # Fine tune (-50 to +50)
    DETUNE = 0x04  # Detune (-50 to +50)
    ATTACK = 0x05  # Attack time (0-127)
    DECAY = 0x06  # Decay time (0-127)
    SUSTAIN = 0x07  # Sustain level (0-127)
    RELEASE = 0x08  # Release time (0-127)
    PAN = 0x09  # Pan position (-64 to +63)
    FILTER_TYPE = 0x0A  # Filter preset_type (0: OFF, 1: LPF, 2: HPF)
    CUTOFF = 0x0B  # Filter cutoff (0-127)
    RESONANCE = 0x0C  # Filter resonance (0-127)
    ENV_DEPTH = 0x0D  # Filter envelope depth (-63 to +63)
    ENV_VELOCITY = 0x0E  # Filter envelope velocity (-63 to +63)
    ENV_ATTACK = 0x0F  # Filter envelope attack (0-127)
    ENV_DECAY = 0x10  # Filter envelope decay (0-127)
    ENV_SUSTAIN = 0x11  # Filter envelope sustain (0-127)
    ENV_RELEASE = 0x12  # Filter envelope release (0-127)


class DigitalToneModify(Enum):
    """Modify parameters for SuperNATURAL Synth Tone"""

    RING_SYNC = 0x00  # Ring/Sync switch (0: OFF, 1: RING, 2: SYNC)
    RING_OSC = 0x01  # Ring modulator oscillator (1-3)
    SYNC_OSC = 0x02  # Sync oscillator (1-3)
    UNISON = 0x03  # Unison switch (0: OFF, 1: ON)
    UNI_SIZE = 0x04  # Unison size (0: 2, 1: 4, 2: 6, 3: 8)
    UNI_DETUNE = 0x05  # Unison detune (0-127)
    LFO_SHAPE = 0x06  # LFO waveform (0: TRI, 1: SIN, 2: SAW, 3: SQR, 4: S&H, 5: RND)
    LFO_RATE = 0x07  # LFO rate (0-127)
    LFO_DEPTH = 0x08  # LFO depth (0-127)
    LFO_MOD_DEST = (
        0x09  # LFO modulation destination (0: PITCH, 1: FILTER, 2: AMP, 3: PAN)
    )
    PITCH_ENV_A = 0x0A  # Pitch envelope attack (0-127)
    PITCH_ENV_D = 0x0B  # Pitch envelope decay (0-127)
    PITCH_ENV_DEPTH = 0x0C  # Pitch envelope depth (-63 to +63)

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if param == 0x00:  # Ring/Sync
            return ["OFF", "RING", "SYNC"][value]
        elif param in (0x01, 0x02):  # Oscillator selection
            return f"OSC {value + 1}"
        elif param == 0x04:  # Unison size
            return str([2, 4, 6, 8][value])
        elif param == 0x06:  # LFO shape
            return ["TRI", "SIN", "SAW", "SQR", "S&H", "RND"][value]
        elif param == 0x09:  # LFO destination
            return ["PITCH", "FILTER", "AMP", "PAN"][value]
        elif param == 0x0C:  # Pitch envelope depth
            return f"{value - 64:+d}"
        return str(value)

    # Analog Synth Tone Parameters (0x19 02)


class AnalogToneParam(Enum):
    """Analog Synth Tone parameters"""

    # Common parameters (0x00-0x0F)
    NAME_1 = 0x00  # Character 1 of name (ASCII)
    NAME_2 = 0x01  # Character 2 of name
    NAME_3 = 0x02  # Character 3 of name
    NAME_4 = 0x03  # Character 4 of name
    NAME_5 = 0x04  # Character 5 of name
    NAME_6 = 0x05  # Character 6 of name
    NAME_7 = 0x06  # Character 7 of name
    NAME_8 = 0x07  # Character 8 of name
    NAME_9 = 0x08  # Character 9 of name
    NAME_10 = 0x09  # Character 10 of name
    NAME_11 = 0x0A  # Character 11 of name
    NAME_12 = 0x0B  # Character 12 of name
    CATEGORY = 0x0C  # Tone category
    LEVEL = 0x0D  # Tone level (0-127)
    PAN = 0x0E  # Pan position (-64 to +63)
    PORTAMENTO = 0x0F  # Portamento switch (0: OFF, 1: ON)

    # Oscillator parameters (0x10-0x1F)
    OSC_WAVE = 0x10  # Oscillator waveform (0: SAW, 1: SQUARE, 2: TRIANGLE)
    OSC_PITCH = 0x11  # Oscillator pitch (-24 to +24)
    OSC_DETUNE = 0x12  # Oscillator detune (-50 to +50)
    OSC_MOD_DEPTH = 0x13  # Oscillator modulation depth (-63 to +63)

    # Filter parameters (0x20-0x2F)
    FILTER_TYPE = 0x20  # Filter preset_type (0: LPF, 1: HPF)
    FILTER_CUTOFF = 0x21  # Filter cutoff frequency (0-127)
    FILTER_RESO = 0x22  # Filter resonance (0-127)
    FILTER_ENV = 0x23  # Filter envelope depth (-63 to +63)
    FILTER_KEY = 0x24  # Filter keyboard follow (-100 to +100)

    # Amplifier parameters (0x30-0x3F)
    AMP_ATTACK = 0x30  # Amplifier attack time (0-127)
    AMP_DECAY = 0x31  # Amplifier decay time (0-127)
    AMP_SUSTAIN = 0x32  # Amplifier sustain level (0-127)
    AMP_RELEASE = 0x33  # Amplifier release time (0-127)

    # LFO parameters (0x40-0x4F)
    LFO_WAVE = 0x40  # LFO waveform (0: TRI, 1: SIN, 2: SAW, 3: SQR, 4: S&H, 5: RND)
    LFO_RATE = 0x41  # LFO rate (0-127)
    LFO_FADE = 0x42  # LFO fade time (0-127)
    LFO_PITCH = 0x43  # LFO pitch modulation depth (-63 to +63)
    LFO_FILTER = 0x44  # LFO filter modulation depth (-63 to +63)
    LFO_AMP = 0x45  # LFO amplitude modulation depth (-63 to +63)

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if 0x00 <= param <= 0x0B:  # Name characters
            return chr(value)
        elif param == 0x0F:  # Portamento switch
            return "ON" if value else "OFF"
        elif param == 0x10:  # OSC wave
            return ["SAW", "SQUARE", "TRIANGLE"][value]
        elif param == 0x11:  # OSC pitch
            return f"{value - 64:+d}"  # Convert to -24/+24
        elif param == 0x12:  # OSC detune
            return f"{value - 64:+d}"  # Convert to -50/+50
        elif param == 0x13:  # OSC mod depth
            return f"{value - 64:+d}"  # Convert to -63/+63
        elif param == 0x20:  # Filter preset_type
            return ["LPF", "HPF"][value]
        elif param == 0x23:  # Filter envelope
            return f"{value - 64:+d}"  # Convert to -63/+63
        elif param == 0x24:  # Filter key follow
            return f"{((value - 64) * 200 / 64):+.0f}"  # Convert to -100/+100
        elif param == 0x0E:  # Pan
            if value < 64:
                return f"L{64 - value}"
            elif value > 64:
                return f"R{value - 64}"
            return "C"
        elif param == 0x40:  # LFO wave
            return ["TRI", "SIN", "SAW", "SQR", "S&H", "RND"][value]
        elif param in (0x43, 0x44, 0x45):  # LFO depths
            return f"{value - 64:+d}"  # Convert to -63/+63
        return str(value)


@dataclass
class AnalogToneMessage(RolandSysEx):
    """Analog Synth Tone parameter message"""

    command: int = DT1_COMMAND_12
    area: int = 0x19  # Temporary area
    tone_type: int = 0x02  # Analog tone
    group: int = 0x00  # Always 0x00 for analog
    param: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        """Set up address and data"""
        self.address = [
            self.area,  # Temporary area (0x19)
            self.tone_type,  # Analog tone (0x02)
            self.group,  # Always 0x00
            self.param,  # Parameter number
        ]
        self.data = [self.value]

    # Drum Kit Structure (0x19 10)


class DrumKitSection(Enum):
    """Drum Kit sections"""

    COMMON = 0x00  # 00 00 00: Common parameters
    PAD_36 = 0x2E  # 00 2E 00: Pad 36 (C1)
    PAD_37 = 0x30  # 00 30 00: Pad 37 (C#1)
    PAD_38 = 0x32  # 00 32 00: Pad 38 (D1)
    # ... continue for all pads
    PAD_72 = 0x76  # 00 76 00: Pad 72 (C4)

    @staticmethod
    def get_pad_offset(note: int) -> int:
        """Get pad offset from MIDI note number"""
        if 36 <= note <= 72:
            return 0x2E + ((note - 36) * 2)
        return 0x00


class Waveform(Enum):
    """Waveform types available on the JD-Xi"""

    SAW = auto()  # Sawtooth wave
    SQUARE = auto()  # Square wave
    TRIANGLE = auto()  # Triangle wave
    SINE = auto()  # Sine wave
    NOISE = auto()  # Noise
    SUPER_SAW = auto()  # Super saw
    PCM = auto()  # PCM waveform

    @property
    def display_name(self) -> str:
        """Get display name for waveform"""
        names = {
            Waveform.SAW: "SAW",
            Waveform.SQUARE: "SQR",
            Waveform.TRIANGLE: "TRI",
            Waveform.SINE: "SIN",
            Waveform.NOISE: "NOISE",
            Waveform.SUPER_SAW: "S.SAW",
            Waveform.PCM: "PCM",
        }
        return names[self]

    @property
    def midi_value(self) -> int:
        """Get MIDI value for waveform"""
        values = {
            Waveform.SAW: OSC_WAVE_SAW,
            Waveform.SQUARE: OSC_WAVE_SQUARE,
            Waveform.TRIANGLE: OSC_WAVE_TRIANGLE,
            Waveform.SINE: OSC_WAVE_SINE,
            Waveform.NOISE: OSC_WAVE_NOISE,
            Waveform.SUPER_SAW: OSC_WAVE_SUPER_SAW,
            Waveform.PCM: OSC_WAVE_PCM,
        }
        return values[self]

    @classmethod
    def from_midi_value(cls, value: int) -> "Waveform":
        """Create Waveform from MIDI value"""
        for waveform in cls:
            if waveform.midi_value == value:
                return waveform
        raise ValueError(f"Invalid waveform value: {value}")


class DrumKitCommon(Enum):
    """Common parameters for Drum Kit"""

    NAME_1 = 0x00  # Character 1 of name (ASCII)
    NAME_2 = 0x01  # Character 2 of name
    NAME_3 = 0x02  # Character 3 of name
    NAME_4 = 0x03  # Character 4 of name
    NAME_5 = 0x04  # Character 5 of name
    NAME_6 = 0x05  # Character 6 of name
    NAME_7 = 0x06  # Character 7 of name
    NAME_8 = 0x07  # Character 8 of name
    NAME_9 = 0x08  # Character 9 of name
    NAME_10 = 0x09  # Character 10 of name
    NAME_11 = 0x0A  # Character 11 of name
    NAME_12 = 0x0B  # Character 12 of name
    CATEGORY = 0x0C  # Kit category
    LEVEL = 0x0D  # Kit level (0-127)


class DrumPadParam(Enum):
    """Parameters for each drum pad"""

    WAVE = 0x00  # Wave number (0-127, 0=OFF)
    LEVEL = 0x01  # Level (0-127)
    PAN = 0x02  # Pan (-64 to +63)
    TUNE = 0x03  # Tune (-64 to +63)
    DECAY = 0x04  # Decay time (0-127)
    MUTE_GROUP = 0x05  # Mute area (0-31, 0=OFF)
    OUTPUT_EFX = 0x06  # Output/EFX select (0-3)
    REVERB_SEND = 0x07  # Reverb send level (0-127)
    DELAY_SEND = 0x08  # Delay send level (0-127)

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if param == 0x00:  # Wave
            return "OFF" if value == 0 else str(value)
        elif param == 0x02:  # Pan
            if value < 64:
                return f"L{64 - value}"
            elif value > 64:
                return f"R{value - 64}"
            return "C"
        elif param in (0x03,):  # Tune
            return f"{value - 64:+d}"
        elif param == 0x05:  # Mute area
            return "OFF" if value == 0 else str(value)
        elif param == 0x06:  # Output/EFX
            return ["OUTPUT", "EFX1", "EFX2", "DLY"][value]
        return str(value)


@dataclass
class DrumKitMessage(RolandSysEx):
    """Drum Kit parameter message"""

    command: int = DT1_COMMAND_12
    area: int = 0x19  # Temporary area
    tone_type: int = 0x10  # Drum Kit
    section: int = 0x00  # Section (Common or Pad offset)
    param: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        """Set up address and data"""
        self.address = [
            self.area,  # Temporary area (0x19)
            self.tone_type,  # Drum Kit (0x10)
            self.section,  # Section (Common/Pad offset)
            self.param,  # Parameter number
        ]
        self.data = [self.value]


# Example usage:
# Set kit name
msg = DrumKitMessage(
    section=DrumKitSection.COMMON.value,
    param=DrumKitCommon.NAME_1.value,
    value=0x41,  # 'A'
)

# Set pad parameter
msg = DrumKitMessage(
    section=DrumKitSection.get_pad_offset(36),  # Pad C1
    param=DrumPadParam.WAVE.value,
    value=1,  # Wave number
)


# Setup Area Structure (0x01)
class SetupParam(Enum):
    """Setup parameters"""

    # Reserved space (0x00-0x03)
    RESERVED_1 = 0x00  # Reserved
    RESERVED_2 = 0x01  # Reserved
    RESERVED_3 = 0x02  # Reserved
    RESERVED_4 = 0x03  # Reserved

    # Program selection (0x04-0x06)
    BANK_MSB = 0x04  # Program Bank Select MSB (CC#0) (0-127)
    BANK_LSB = 0x05  # Program Bank Select LSB (CC#32) (0-127)
    PROGRAM = 0x06  # Program Change Number (0-127)

    # More reserved space (0x07-0x3A)
    # Total size: 0x3B bytes


@dataclass
class SetupMessage(RolandSysEx):
    """Setup parameter message"""

    command: int = DT1_COMMAND_12
    area: int = SETUP_AREA  # 0x01: Setup area
    section: int = 0x00  # Always 0x00
    group: int = 0x00  # Always 0x00
    param: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        """Set up address and data"""
        self.address = [
            self.area,  # Setup area (0x01)
            self.section,  # Always 0x00
            self.group,  # Always 0x00
            self.param,  # Parameter number
        ]
        self.data = [self.value]


# Example usage:
# Change program bank MSB
msg = SetupMessage(param=SetupParam.BANK_MSB.value, value=0)  # Bank 0

# Change program bank LSB
msg = SetupMessage(param=SetupParam.BANK_LSB.value, value=0)  # Bank 0

# Change program number
msg = SetupMessage(param=SetupParam.PROGRAM.value, value=0)  # Program 1


# Program Common Parameters (0x18 00)


@dataclass
class ProgramCommonParameterMessage(RolandSysEx):
    """Program Common parameter message"""

    command: int = DT1_COMMAND_12
    area: int = PROGRAM_AREA  # 0x18: Program area
    section: int = 0x00  # 0x00: Common section
    group: int = 0x00  # Always 0x00
    param: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        """Set up address and data"""
        self.address = [
            self.area,  # Program area (0x18)
            self.section,  # Common section (0x00)
            self.group,  # Always 0x00
            self.param,  # Parameter number
        ]
        self.data = [self.value]


# Example usage:
# Set program name character
msg = ProgramCommonParameterMessage(
    param=ProgramCommonParameter.NAME_1.value, value=ord("A")  # ASCII 'A'
)

# Set program level
msg = ProgramCommonParameterMessage(param=ProgramCommonParameter.PROGRAM_LEVEL.value, value=100)  # Level 100

# Set program tempo to 120.00 BPM
msg = ProgramCommonParameterMessage(param=ProgramCommonParameter.PROGRAM_TEMPO.value, value=12000)  # 120.00 BPM

# Set vocal effect to VOCODER
msg = ProgramCommonParameterMessage(param=ProgramCommonParameter.VOCAL_EFFECT.value, value=1)  # VOCODER

# Set vocal effect number
msg = ProgramCommonParameterMessage(
    param=ProgramCommonParameter.VOCAL_EFFECT_NUMBER.value, value=0  # Vocal Effect 1
)

# Enable auto note
msg = ProgramCommonParameterMessage(param=ProgramCommonParameter.AUTO_NOTE_SWITCH.value, value=1)  # ON


# Program Vocal Effect Parameters (0x18 01)
class VocalEffect(Enum):
    """Program Vocal Effect parameters"""

    LEVEL = 0x00  # Level (0-127)
    PAN = 0x01  # Pan (0-127: L64-63R)
    DELAY_SEND = 0x02  # Delay Send Level (0-127)
    REVERB_SEND = 0x03  # Reverb Send Level (0-127)
    OUTPUT_ASSIGN = 0x04  # Output Assign (0: EFX1, 1: EFX2, 2: DLY, 3: REV, 4: DIR)

    # Auto Pitch parameters
    AUTO_PITCH_SW = 0x05  # Auto Pitch Switch (0: OFF, 1: ON)
    AUTO_PITCH_TYPE = 0x06  # Type (0: SOFT, 1: HARD, 2: ELECTRIC1, 3: ELECTRIC2)
    AUTO_PITCH_SCALE = 0x07  # Scale (0: CHROMATIC, 1: Maj(Min))
    AUTO_PITCH_KEY = 0x08  # Key (0-23: C-Bm)
    AUTO_PITCH_NOTE = 0x09  # Note (0-11: C-B)
    AUTO_PITCH_GENDER = 0x0A  # Gender (-10 to +10)
    AUTO_PITCH_OCTAVE = 0x0B  # Octave (-1 to +1)
    AUTO_PITCH_BAL = 0x0C  # Balance (0-100: D100:0W - D0:100W)

    # Vocoder parameters
    VOCODER_SW = 0x0D  # Vocoder Switch (0: OFF, 1: ON)
    VOCODER_ENV = 0x0E  # Envelope (0: SHARP, 1: SOFT, 2: LONG)
    VOCODER_PARAM = 0x0F  # Parameter (0-127)
    VOCODER_MIC_SENS = 0x10  # Mic Sensitivity (0-127)
    VOCODER_SYNTH_LVL = 0x11  # Synth Level (0-127)
    VOCODER_MIC_MIX = 0x12  # Mic Mix Level (0-127)
    VOCODER_MIC_HPF = 0x13  # Mic HPF (0: BYPASS, 1-13: 1000-16000Hz)

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if param == 0x01:  # Pan
            if value < 64:
                return f"L{64 - value}"
            elif value > 64:
                return f"R{value - 64}"
            return "C"
        elif param == 0x04:  # Output Assign
            return ["EFX1", "EFX2", "DLY", "REV", "DIR"][value]
        elif param in (0x05, 0x0D):  # Switches
            return "ON" if value else "OFF"
        elif param == 0x06:  # Auto Pitch Type
            return ["SOFT", "HARD", "ELECTRIC1", "ELECTRIC2"][value]
        elif param == 0x07:  # Auto Pitch Scale
            return ["CHROMATIC", "Maj(Min)"][value]
        elif param == 0x08:  # Auto Pitch Key
            keys = [
                "C",
                "Db",
                "D",
                "Eb",
                "E",
                "F",
                "F#",
                "G",
                "Ab",
                "A",
                "Bb",
                "B",
                "Cm",
                "C#m",
                "Dm",
                "D#m",
                "Em",
                "Fm",
                "F#m",
                "Gm",
                "G#m",
                "Am",
                "Bbm",
                "Bm",
            ]
            return keys[value]
        elif param == 0x09:  # Auto Pitch Note
            notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
            return notes[value]
        elif param == 0x0A:  # Auto Pitch Gender
            return f"{value - 10:+d}"  # Convert 0-20 to -10/+10
        elif param == 0x0B:  # Auto Pitch Octave
            return f"{value - 1:+d}"  # Convert 0-2 to -1/+1
        elif param == 0x0C:  # Auto Pitch Balance
            return f"D{100 - value}:W{value}"  # Convert 0-100 to ratio
        elif param == 0x0E:  # Vocoder Envelope
            return ["SHARP", "SOFT", "LONG"][value]
        elif param == 0x13:  # Vocoder Mic HPF
            if value == 0:
                return "BYPASS"
            freqs = [
                1000,
                1250,
                1600,
                2000,
                2500,
                3150,
                4000,
                5000,
                6300,
                8000,
                10000,
                12500,
                16000,
            ]
            return f"{freqs[value - 1]}Hz"
        return str(value)


@dataclass
class VocalEffectMessage(RolandSysEx):
    """Program Vocal Effect parameter message"""

    command: int = DT1_COMMAND_12
    area: int = PROGRAM_AREA  # 0x18: Program area
    section: int = 0x01  # 0x01: Vocal Effect section
    group: int = 0x00  # Always 0x00
    param: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        """Set up address and data"""
        self.address = [
            self.area,  # Program area (0x18)
            self.section,  # Vocal Effect section (0x01)
            self.group,  # Always 0x00
            self.param,  # Parameter number
        ]
        self.data = [self.value]


# Example usage:
# Set vocal effect level
msg = VocalEffectMessage(param=VocalEffect.LEVEL.value, value=100)  # Level 100

# Set auto pitch parameters
msg = VocalEffectMessage(param=VocalEffect.AUTO_PITCH_SW.value, value=1)  # ON

msg = VocalEffectMessage(param=VocalEffect.AUTO_PITCH_TYPE.value, value=0)  # SOFT

# Set vocoder parameters
msg = VocalEffectMessage(param=VocalEffect.VOCODER_SW.value, value=1)  # ON

msg = VocalEffectMessage(param=VocalEffect.VOCODER_ENV.value, value=1)  # SOFT


# Program Effect 1 Parameters (0x18 02)
class Effect1(Enum):
    """Program Effect 1 parameters"""

    TYPE = 0x00  # Effect preset_type (0-4)
    LEVEL = 0x01  # Effect level (0-127)
    DELAY_SEND = 0x02  # Delay send level (0-127)
    REVERB_SEND = 0x03  # Reverb send level (0-127)
    OUTPUT_ASSIGN = 0x04  # Output assign (0: DIR, 1: EFX2)

    # Parameters start at 0x11 and go up to 0x10D
    # Each parameter is 4 bytes (12768-52768: -20000 to +20000)
    PARAM_1 = 0x11  # Parameter 1
    PARAM_2 = 0x15  # Parameter 2
    # ... continue for all 32 parameters
    PARAM_32 = 0x10D  # Parameter 32

    @staticmethod
    def get_param_offset(param_num: int) -> int:
        """Get parameter offset from parameter number (1-32)"""
        if 1 <= param_num <= 32:
            return 0x11 + ((param_num - 1) * 4)
        return 0x00

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if param == 0x00:  # Effect preset_type
            return ["OFF", "DISTORTION", "FUZZ", "COMPRESSOR", "BITCRUSHER"][value]
        elif param == 0x04:  # Output assign
            return ["DIR", "EFX2"][value]
        elif 0x11 <= param <= 0x10D:  # Effect parameters
            return f"{value - 32768:+d}"  # Convert 12768-52768 to -20000/+20000
        return str(value)


@dataclass
class Effect1Message(RolandSysEx):
    """Program Effect 1 parameter message"""

    command: int = DT1_COMMAND_12
    area: int = PROGRAM_AREA  # 0x18: Program area
    section: int = 0x02  # 0x02: Effect 1 section
    group: int = 0x00  # Always 0x00
    param: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        """Set up address and data"""
        self.address = [
            self.area,  # Program area (0x18)
            self.section,  # Effect 1 section (0x02)
            self.group,  # Always 0x00
            self.param,  # Parameter number
        ]
        # Handle 4-byte parameters
        if 0x11 <= self.param <= 0x10D:
            # Convert -20000/+20000 to 12768-52768
            value = self.value + 32768
            self.data = [
                (value >> 24) & 0x0F,  # High nibble
                (value >> 16) & 0x0F,
                (value >> 8) & 0x0F,
                value & 0x0F,  # Low nibble
            ]
        else:
            self.data = [self.value]


# Example usage:
# Set effect preset_type
msg = Effect1Message(param=Effect1.TYPE.value, value=1)  # DISTORTION

# Set effect level
msg = Effect1Message(param=Effect1.LEVEL.value, value=100)  # Level 100

# Set effect parameter 1 to +5000
msg = Effect1Message(
    param=Effect1.get_param_offset(1), value=5000  # Will be converted to 37768
)

# Set output to EFX2
msg = Effect1Message(param=Effect1.OUTPUT_ASSIGN.value, value=1)  # EFX2


# Program Effect 2 Parameters (0x18 04)
class Effect2(Enum):
    """Program Effect 2 parameters"""

    TYPE = 0x00  # Effect preset_type (0, 5-8: OFF, PHASER, FLANGER, DELAY, CHORUS)
    LEVEL = 0x01  # Effect level (0-127)
    DELAY_SEND = 0x02  # Delay send level (0-127)
    REVERB_SEND = 0x03  # Reverb send level (0-127)

    # Reserved (0x04-0x10)

    # Parameters start at 0x11 and go up to 0x10D
    # Each parameter is 4 bytes (12768-52768: -20000 to +20000)
    PARAM_1 = 0x11  # Parameter 1
    PARAM_2 = 0x15  # Parameter 2
    # ... continue for all 32 parameters
    PARAM_32 = 0x10D  # Parameter 32

    @staticmethod
    def get_param_offset(param_num: int) -> int:
        """Get parameter offset from parameter number (1-32)"""
        if 1 <= param_num <= 32:
            return 0x11 + ((param_num - 1) * 4)
        return 0x00

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if param == 0x00:  # Effect preset_type
            if value == 0:
                return "OFF"
            types = ["OFF", "PHASER", "FLANGER", "DELAY", "CHORUS"]
            return types[value - 4] if 5 <= value <= 8 else str(value)
        elif 0x11 <= param <= 0x10D:  # Effect parameters
            return f"{value - 32768:+d}"  # Convert 12768-52768 to -20000/+20000
        return str(value)


@dataclass
class Effect2Message(RolandSysEx):
    """Program Effect 2 parameter message"""

    command: int = DT1_COMMAND_12
    area: int = PROGRAM_AREA  # 0x18: Program area
    section: int = 0x04  # 0x04: Effect 2 section
    group: int = 0x00  # Always 0x00
    param: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        """Set up address and data"""
        self.address = [
            self.area,  # Program area (0x18)
            self.section,  # Effect 2 section (0x04)
            self.group,  # Always 0x00
            self.param,  # Parameter number
        ]
        # Handle 4-byte parameters
        if 0x11 <= self.param <= 0x10D:
            # Convert -20000/+20000 to 12768-52768
            value = self.value + 32768
            self.data = [
                (value >> 24) & 0x0F,  # High nibble
                (value >> 16) & 0x0F,
                (value >> 8) & 0x0F,
                value & 0x0F,  # Low nibble
            ]
        else:
            self.data = [self.value]


# Example usage:
# Set effect preset_type
msg = Effect2Message(param=Effect2.TYPE.value, value=5)  # PHASER

# Set effect level
msg = Effect2Message(param=Effect2.LEVEL.value, value=100)  # Level 100

# Set effect parameter 1 to +5000
msg = Effect2Message(
    param=Effect2.get_param_offset(1), value=5000  # Will be converted to 37768
)

# Set send levels
msg = Effect2Message(param=Effect2.DELAY_SEND.value, value=64)  # Send to delay

msg = Effect2Message(param=Effect2.REVERB_SEND.value, value=64)  # Send to reverb


# Program Delay Parameters (0x18 06)
class Delay(Enum):
    """Program Delay parameters"""

    # Reserved (0x00)
    LEVEL = 0x01  # Delay Level (0-127)
    # Reserved (0x02)
    REVERB_SEND = 0x03  # Delay Reverb Send Level (0-127)

    # Parameters start at 0x04 and go up to 0x60
    # Each parameter is 4 bytes (12768-52768: -20000 to +20000)
    PARAM_1 = 0x04  # Parameter 1
    PARAM_2 = 0x08  # Parameter 2
    # ... continue for all 24 parameters
    PARAM_24 = 0x60  # Parameter 24

    @staticmethod
    def get_param_offset(param_num: int) -> int:
        """Get parameter offset from parameter number (1-24)"""
        if 1 <= param_num <= 24:
            return 0x04 + ((param_num - 1) * 4)
        return 0x00

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if 0x04 <= param <= 0x60:  # Effect parameters
            return f"{value - 32768:+d}"  # Convert 12768-52768 to -20000/+20000
        return str(value)


@dataclass
class DelayMessage(RolandSysEx):
    """Program Delay parameter message"""

    command: int = DT1_COMMAND_12
    area: int = PROGRAM_AREA  # 0x18: Program area
    section: int = 0x06  # 0x06: Delay section
    group: int = 0x00  # Always 0x00
    param: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        """Set up address and data"""
        self.address = [
            self.area,  # Program area (0x18)
            self.section,  # Delay section (0x06)
            self.group,  # Always 0x00
            self.param,  # Parameter number
        ]
        # Handle 4-byte parameters
        if 0x04 <= self.param <= 0x60:
            # Convert -20000/+20000 to 12768-52768
            value = self.value + 32768
            self.data = [
                (value >> 24) & 0x0F,  # High nibble
                (value >> 16) & 0x0F,
                (value >> 8) & 0x0F,
                value & 0x0F,  # Low nibble
            ]
        else:
            self.data = [self.value]


# Example usage:
# Set delay level
msg = DelayMessage(param=Delay.LEVEL.value, value=100)  # Level 100

# Set reverb send level
msg = DelayMessage(param=Delay.REVERB_SEND.value, value=64)  # Send to reverb

# Set delay parameter 1 to +5000
msg = DelayMessage(
    param=Delay.get_param_offset(1), value=5000  # Will be converted to 37768
)


# Program Reverb Parameters (0x18 08)
class Reverb(Enum):
    """Program Reverb parameters"""

    # Reserved (0x00)
    LEVEL = 0x01  # Reverb Level (0-127)
    # Reserved (0x02)

    # Parameters start at 0x03 and go up to 0x5F
    # Each parameter is 4 bytes (12768-52768: -20000 to +20000)
    PARAM_1 = 0x03  # Parameter 1
    PARAM_2 = 0x07  # Parameter 2
    # ... continue for all 24 parameters
    PARAM_24 = 0x5F  # Parameter 24

    @staticmethod
    def get_param_offset(param_num: int) -> int:
        """Get parameter offset from parameter number (1-24)"""
        if 1 <= param_num <= 24:
            return 0x03 + ((param_num - 1) * 4)
        return 0x00

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if 0x03 <= param <= 0x5F:  # Effect parameters
            return f"{value - 32768:+d}"  # Convert 12768-52768 to -20000/+20000
        return str(value)


@dataclass
class ReverbMessage(RolandSysEx):
    """Program Reverb parameter message"""

    command: int = DT1_COMMAND_12
    area: int = PROGRAM_AREA  # 0x18: Program area
    section: int = 0x08  # 0x08: Reverb section
    group: int = 0x00  # Always 0x00
    param: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        """Set up address and data"""
        self.address = [
            self.area,  # Program area (0x18)
            self.section,  # Reverb section (0x08)
            self.group,  # Always 0x00
            self.param,  # Parameter number
        ]
        # Handle 4-byte parameters
        if 0x03 <= self.param <= 0x5F:
            # Convert -20000/+20000 to 12768-52768
            value = self.value + 32768
            self.data = [
                (value >> 24) & 0x0F,  # High nibble
                (value >> 16) & 0x0F,
                (value >> 8) & 0x0F,
                value & 0x0F,  # Low nibble
            ]
        else:
            self.data = [self.value]


# Example usage:
# Set reverb level
msg = ReverbMessage(param=Reverb.LEVEL.value, value=100)  # Level 100

# Set reverb parameter 1 to +5000
msg = ReverbMessage(
    param=Reverb.get_param_offset(1), value=5000  # Will be converted to 37768
)


class Zone:
    """Program Zone parameters"""

    ARPEGGIO_SWITCH = 0x03  # Arpeggio Switch (0-1)
    OCTAVE_SHIFT = 0x19  # Zone Octave Shift (-3/+3)


@dataclass
class ZoneMessage(RolandSysEx):
    """Program Zone parameter message"""

    command: int = DT1_COMMAND_12
    area: int = PROGRAM_AREA
    section: int = 0x01  # Zone section


class Controller:
    """Program Controller parameters"""

    # Arpeggio parameters
    ARP_GRID = 0x01  # Arpeggio Grid (0-8)
    ARP_DURATION = 0x02  # Arpeggio Duration (0-9)
    ARP_SWITCH = 0x03  # Arpeggio Switch (0-1)
    ARP_STYLE = 0x05  # Arpeggio Style (0-127)
    ARP_MOTIF = 0x06  # Arpeggio Motif (0-11)
    ARP_OCTAVE = 0x07  # Arpeggio Octave Range (-3/+3)
    ARP_ACCENT = 0x09  # Arpeggio Accent Rate (0-100)
    ARP_VELOCITY = 0x0A  # Arpeggio Velocity (0-127, 0=REAL)

    # Grid values
    GRID_4 = 0  # 04_
    GRID_8 = 1  # 08_
    GRID_8L = 2  # 08L
    GRID_8H = 3  # 08H
    GRID_8T = 4  # 08t
    GRID_16 = 5  # 16_
    GRID_16L = 6  # 16L
    GRID_16H = 7  # 16H
    GRID_16T = 8  # 16t

    # Duration values
    DUR_30 = 0  # 30%
    DUR_40 = 1  # 40%
    DUR_50 = 2  # 50%
    DUR_60 = 3  # 60%
    DUR_70 = 4  # 70%
    DUR_80 = 5  # 80%
    DUR_90 = 6  # 90%
    DUR_100 = 7  # 100%
    DUR_120 = 8  # 120%
    DUR_FULL = 9  # FULL

    # Motif values
    MOTIF_UP_L = 0  # UP/L
    MOTIF_UP_H = 1  # UP/H
    MOTIF_UP = 2  # UP/_
    MOTIF_DN_L = 3  # dn/L
    MOTIF_DN_H = 4  # dn/H
    MOTIF_DN = 5  # dn/_
    MOTIF_UD_L = 6  # Ud/L
    MOTIF_UD_H = 7  # Ud/H
    MOTIF_UD = 8  # Ud/_
    MOTIF_RN_L = 9  # rn/L
    MOTIF_RN = 10  # rn/_
    MOTIF_PHRASE = 11  # PHRASE

    @staticmethod
    def get_grid_name(value: int) -> str:
        """Get grid name from value"""
        names = ["04_", "08_", "08L", "08H", "08t", "16_", "16L", "16H", "16t"]
        return names[value] if 0 <= value <= 8 else str(value)

    @staticmethod
    def get_duration_name(value: int) -> str:
        """Get duration name from value"""
        names = ["30", "40", "50", "60", "70", "80", "90", "100", "120", "FUL"]
        return names[value] if 0 <= value <= 9 else str(value)

    @staticmethod
    def get_motif_name(value: int) -> str:
        """Get motif name from value"""
        names = [
            "UP/L",
            "UP/H",
            "UP/_",
            "dn/L",
            "dn/H",
            "dn/_",
            "Ud/L",
            "Ud/H",
            "Ud/_",
            "rn/L",
            "rn/_",
            "PHRASE",
        ]
        return names[value] if 0 <= value <= 11 else str(value)

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if param == 0x01:  # Grid
            return Controller.get_grid_name(value)
        elif param == 0x02:  # Duration
            return Controller.get_duration_name(value)
        elif param == 0x03:  # Switch
            return "ON" if value else "OFF"
        elif param == 0x05:  # Style
            return str(value + 1)  # Convert 0-127 to 1-128
        elif param == 0x06:  # Motif
            return Controller.get_motif_name(value)
        elif param == 0x07:  # Octave Range
            return f"{value - 64:+d}"  # Convert 61-67 to -3/+3
        elif param == 0x09:  # Accent Rate
            return f"{value}%"
        elif param == 0x0A:  # Velocity
            return "REAL" if value == 0 else str(value)
        return str(value)


class DigitalTonePartial:
    """SuperNATURAL Synth Tone Partial parameters"""

    # Oscillator parameters
    OSC_WAVE = 0x00  # OSC Wave (0-7)
    OSC_VARIATION = 0x01  # OSC Wave Variation (0-2)
    OSC_PITCH = 0x03  # OSC Pitch (-24/+24)
    OSC_DETUNE = 0x04  # OSC Detune (-50/+50)
    OSC_PWM_DEPTH = 0x05  # OSC Pulse Width Mod Depth (0-127)
    OSC_PW = 0x06  # OSC Pulse Width (0-127)
    OSC_PW_SHIFT = 0x2A  # OSC Pulse Width Shift (0-127)

    # Pitch envelope
    PITCH_ENV_ATK = 0x07  # OSC Pitch Env Attack Time (0-127)
    PITCH_ENV_DCY = 0x08  # OSC Pitch Env Decay (0-127)
    PITCH_ENV_DEPTH = 0x09  # OSC Pitch Env Depth (-63/+63)

    # Filter parameters
    FILTER_MODE = 0x0A  # Filter Mode (0-7)
    FILTER_SLOPE = 0x0B  # Filter Slope (0-1)
    FILTER_CUTOFF = 0x0C  # Filter Cutoff (0-127)
    FILTER_KF = 0x0D  # Filter Cutoff Keyfollow (-100/+100)
    FILTER_VEL = 0x0E  # Filter Env Velocity Sens (-63/+63)
    FILTER_RES = 0x0F  # Filter Resonance (0-127)
    HPF_CUTOFF = 0x39  # HPF Cutoff (0-127)

    # Filter envelope
    FILTER_ENV_ATK = 0x10  # Filter Env Attack Time (0-127)
    FILTER_ENV_DCY = 0x11  # Filter Env Decay Time (0-127)
    FILTER_ENV_SUS = 0x12  # Filter Env Sustain Level (0-127)
    FILTER_ENV_REL = 0x13  # Filter Env Release Time (0-127)
    FILTER_ENV_DEPTH = 0x14  # Filter Env Depth (-63/+63)

    # Amplifier parameters
    AMP_LEVEL = 0x15  # AMP Level (0-127)
    AMP_VEL = 0x16  # AMP Level Velocity Sens (-63/+63)
    AMP_KF = 0x3C  # AMP Level Keyfollow (-100/+100)

    # Amplifier envelope
    AMP_ENV_ATK = 0x17  # AMP Env Attack Time (0-127)
    AMP_ENV_DCY = 0x18  # AMP Env Decay Time (0-127)
    AMP_ENV_SUS = 0x19  # AMP Env Sustain Level (0-127)
    AMP_ENV_REL = 0x1A  # AMP Env Release Time (0-127)
    AMP_PAN = 0x1B  # AMP Pan (L64-63R)

    # LFO parameters
    LFO_SHAPE = 0x1C  # LFO Shape (0-5)
    LFO_RATE = 0x1D  # LFO Rate (0-127)
    LFO_SYNC = 0x1E  # LFO Tempo Sync Switch (0-1)
    LFO_NOTE = 0x1F  # LFO Tempo Sync Note (0-19)
    LFO_FADE = 0x20  # LFO Fade Time (0-127)
    LFO_KEYTRIG = 0x21  # LFO Key Trigger (0-1)

    # LFO depths
    LFO_PITCH = 0x22  # LFO Pitch Depth (-63/+63)
    LFO_FILTER = 0x23  # LFO Filter Depth (-63/+63)
    LFO_AMP = 0x24  # LFO Amp Depth (-63/+63)
    LFO_PAN = 0x25  # LFO Pan Depth (-63/+63)

    # Modulation LFO
    MOD_LFO_SHAPE = 0x26  # Mod LFO Shape (0-5)
    MOD_LFO_RATE = 0x27  # Mod LFO Rate (0-127)
    MOD_LFO_SYNC = 0x28  # Mod LFO Tempo Sync Switch (0-1)
    MOD_LFO_NOTE = 0x29  # Mod LFO Tempo Sync Note (0-19)
    MOD_LFO_RATE_CTRL = 0x3B  # Mod LFO Rate Control (-63/+63)

    # Modulation depths
    MOD_LFO_PITCH = 0x2C  # Mod LFO Pitch Depth (-63/+63)
    MOD_LFO_FILTER = 0x2D  # Mod LFO Filter Depth (-63/+63)
    MOD_LFO_AMP = 0x2E  # Mod LFO Amp Depth (-63/+63)
    MOD_LFO_PAN = 0x2F  # Mod LFO Pan Depth (-63/+63)

    # Aftertouch sensitivities
    AT_CUTOFF = 0x30  # Cutoff Aftertouch Sens (-63/+63)
    AT_LEVEL = 0x31  # Level Aftertouch Sens (-63/+63)

    # Wave parameters
    WAVE_GAIN = 0x34  # Wave Gain (-6/0/+6/+12 dB)
    WAVE_NUMBER = 0x35  # Wave Number (0=OFF, 1-16384)
    SUPER_SAW = 0x3A  # Super Saw Detune (0-127)

    # Filter modes
    FILTER_BYPASS = 0  # Bypass
    FILTER_LPF = 1  # Low Pass Filter
    FILTER_HPF = 2  # High Pass Filter
    FILTER_BPF = 3  # Band Pass Filter
    FILTER_PKG = 4  # Peak/Gain
    FILTER_LPF2 = 5  # Low Pass Filter 2
    FILTER_LPF3 = 6  # Low Pass Filter 3
    FILTER_LPF4 = 7  # Low Pass Filter 4

    # LFO shapes
    LFO_TRI = 0  # Triangle
    LFO_SIN = 1  # Sine
    LFO_SAW = 2  # Sawtooth
    LFO_SQR = 3  # Square
    LFO_SH = 4  # Sample & Hold
    LFO_RND = 5  # Random

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if param == 0x00:  # Wave preset_type
            return DigitalTonePartial.get_wave_name(value)
        elif param == 0x01:  # Wave variation
            return DigitalTonePartial.get_variation_name(value)
        elif param == 0x03:  # OSC Pitch
            return f"{value - 64:+d}"  # Convert 40-88 to -24/+24
        elif param == 0x04:  # OSC Detune
            return f"{value - 64:+d}"  # Convert 14-114 to -50/+50
        elif param == 0x09:  # Pitch Env Depth
            return f"{value - 64:+d}"  # Convert 1-127 to -63/+63
        elif param == 0x0A:  # Filter Mode
            modes = ["BYPASS", "LPF", "HPF", "BPF", "PKG", "LPF2", "LPF3", "LPF4"]
            return modes[value]
        elif param == 0x0B:  # Filter Slope
            return "-12dB" if value == 0 else "-24dB"
        elif param == 0x0D:  # Filter Keyfollow
            return f"{((value - 54) * 200 / 20) - 100:+.0f}"  # Convert to -100/+100
        elif param == 0x0E:  # Filter Velocity Sens
            return f"{value - 64:+d}"  # Convert 1-127 to -63/+63
        elif param == 0x14:  # Filter Env Depth
            return f"{value - 64:+d}"  # Convert 1-127 to -63/+63
        elif param == 0x16:  # Amp Velocity Sens
            return f"{value - 64:+d}"  # Convert 1-127 to -63/+63
        elif param == 0x1B:  # Pan
            if value < 64:
                return f"L{64 - value}"
            elif value > 64:
                return f"{value - 64}R"
            return "C"
        elif param in [0x1C, 0x26]:  # LFO Shapes
            shapes = ["TRI", "SIN", "SAW", "SQR", "S&H", "RND"]
            return shapes[value]
        elif param in [0x1E, 0x21, 0x28]:  # Switches
            return "ON" if value else "OFF"
        elif param in [0x1F, 0x29]:  # Sync Notes
            notes = [
                "16",
                "12",
                "8",
                "4",
                "2",
                "1",
                "3/4",
                "2/3",
                "1/2",
                "3/8",
                "1/3",
                "1/4",
                "3/16",
                "1/6",
                "1/8",
                "3/32",
                "1/12",
                "1/16",
                "1/24",
                "1/32",
            ]
            return notes[value]
        elif param in [
            0x22,
            0x23,
            0x24,
            0x25,  # LFO depths
            0x2C,
            0x2D,
            0x2E,
            0x2F,  # Mod LFO depths
            0x30,
            0x31,
            0x3B,
        ]:  # Aftertouch and Rate Control
            return f"{value - 64:+d}"  # Convert 1-127 to -63/+63
        elif param == 0x34:  # Wave Gain
            gains = ["-6dB", "0dB", "+6dB", "+12dB"]
            return gains[value]
        elif param == 0x35:  # Wave Number
            return "OFF" if value == 0 else str(value)
        elif param == 0x3C:  # Amp Level Keyfollow
            return f"{((value - 54) * 200 / 20) - 100:+.0f}"  # Convert to -100/+100
        return str(value)


class AnalogTone:
    """Analog Synth Tone parameters"""

    # Tone name (12 characters)
    NAME_1 = 0x00  # Character 1 (ASCII 32-127)
    NAME_2 = 0x01  # Character 2
    NAME_3 = 0x02  # Character 3
    NAME_4 = 0x03  # Character 4
    NAME_5 = 0x04  # Character 5
    NAME_6 = 0x05  # Character 6
    NAME_7 = 0x06  # Character 7
    NAME_8 = 0x07  # Character 8
    NAME_9 = 0x08  # Character 9
    NAME_10 = 0x09  # Character 10
    NAME_11 = 0x0A  # Character 11
    NAME_12 = 0x0B  # Character 12

    # LFO parameters
    LFO_SHAPE = 0x0D  # LFO Shape (0-5)
    LFO_RATE = 0x0E  # LFO Rate (0-127)
    LFO_FADE = 0x0F  # LFO Fade Time (0-127)
    LFO_SYNC = 0x10  # LFO Tempo Sync Switch (0-1)
    LFO_NOTE = 0x11  # LFO Tempo Sync Note (0-19)
    LFO_PITCH = 0x12  # LFO Pitch Depth (-63/+63)
    LFO_FILTER = 0x13  # LFO Filter Depth (-63/+63)
    LFO_AMP = 0x14  # LFO Amp Depth (-63/+63)
    LFO_KEYTRIG = 0x15  # LFO Key Trigger (0-1)

    # Oscillator parameters
    OSC_WAVE = 0x16  # OSC Waveform (0-2)
    OSC_COARSE = 0x17  # OSC Pitch Coarse (-24/+24)
    OSC_FINE = 0x18  # OSC Pitch Fine (-50/+50)
    OSC_PW = 0x19  # OSC Pulse Width (0-127)
    OSC_PWM = 0x1A  # OSC Pulse Width Mod Depth (0-127)
    OSC_PITCH_VEL = 0x1B  # OSC Pitch Env Velocity Sens (-63/+63)
    OSC_PITCH_ATK = 0x1C  # OSC Pitch Env Attack Time (0-127)
    OSC_PITCH_DCY = 0x1D  # OSC Pitch Env Decay (0-127)
    OSC_PITCH_DEPTH = 0x1E  # OSC Pitch Env Depth (-63/+63)
    SUB_OSC = 0x1F  # Sub Oscillator Type (0-2)

    # Filter parameters
    FILTER_SW = 0x20  # Filter Switch (0-1)
    FILTER_CUTOFF = 0x21  # Filter Cutoff (0-127)
    FILTER_KF = 0x22  # Filter Cutoff Keyfollow (-100/+100)
    FILTER_RES = 0x23  # Filter Resonance (0-127)
    FILTER_VEL = 0x24  # Filter Env Velocity Sens (-63/+63)
    FILTER_ATK = 0x25  # Filter Env Attack Time (0-127)
    FILTER_DCY = 0x26  # Filter Env Decay Time (0-127)
    FILTER_SUS = 0x27  # Filter Env Sustain Level (0-127)
    FILTER_REL = 0x28  # Filter Env Release Time (0-127)
    FILTER_DEPTH = 0x29  # Filter Env Depth (-63/+63)

    # Amplifier parameters
    AMP_LEVEL = 0x2A  # AMP Level (0-127)
    AMP_KF = 0x2B  # AMP Level Keyfollow (-100/+100)
    AMP_VEL = 0x2C  # AMP Level Velocity Sens (-63/+63)
    AMP_ATK = 0x2D  # AMP Env Attack Time (0-127)
    AMP_DCY = 0x2E  # AMP Env Decay Time (0-127)
    AMP_SUS = 0x2F  # AMP Env Sustain Level (0-127)
    AMP_REL = 0x30  # AMP Env Release Time (0-127)

    # Performance parameters
    PORTA_SW = 0x31  # Portamento Switch (0-1)
    PORTA_TIME = 0x32  # Portamento Time (0-127)
    LEGATO_SW = 0x33  # Legato Switch (0-1)
    OCTAVE = 0x34  # Octave Shift (-3/+3)
    BEND_UP = 0x35  # Pitch Bend Range Up (0-24)
    BEND_DOWN = 0x36  # Pitch Bend Range Down (0-24)

    # Modulation controls
    MOD_PITCH = 0x38  # LFO Pitch Modulation Control (-63/+63)
    MOD_FILTER = 0x39  # LFO Filter Modulation Control (-63/+63)
    MOD_AMP = 0x3A  # LFO Amp Modulation Control (-63/+63)
    MOD_RATE = 0x3B  # LFO Rate Modulation Control (-63/+63)

    # LFO shapes
    LFO_TRI = 0  # Triangle
    LFO_SIN = 1  # Sine
    LFO_SAW = 2  # Sawtooth
    LFO_SQR = 3  # Square
    LFO_SH = 4  # Sample & Hold
    LFO_RND = 5  # Random

    # Oscillator waveforms
    WAVE_SAW = 0  # Sawtooth
    WAVE_TRI = 1  # Triangle
    WAVE_PW = 2  # Pulse Width Square

    # Sub oscillator types
    SUB_OFF = 0  # Off
    SUB_OCT1 = 1  # -1 Octave
    SUB_OCT2 = 2  # -2 Octaves

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if 0x00 <= param <= 0x0B:  # Name characters
            return chr(value) if 32 <= value <= 127 else "?"
        elif param == 0x0D:  # LFO Shape
            shapes = ["TRI", "SIN", "SAW", "SQR", "S&H", "RND"]
            return shapes[value]
        elif param == 0x10:  # LFO Sync
            return "ON" if value else "OFF"
        elif param == 0x11:  # LFO Note
            notes = [
                "16",
                "12",
                "8",
                "4",
                "2",
                "1",
                "3/4",
                "2/3",
                "1/2",
                "3/8",
                "1/3",
                "1/4",
                "3/16",
                "1/6",
                "1/8",
                "3/32",
                "1/12",
                "1/16",
                "1/24",
                "1/32",
            ]
            return notes[value]
        elif param == 0x16:  # OSC Wave
            waves = ["SAW", "TRI", "PW-SQR"]
            return waves[value]
        elif param == 0x17:  # OSC Coarse
            return f"{value - 64:+d}"  # Convert 40-88 to -24/+24
        elif param == 0x18:  # OSC Fine
            return f"{value - 64:+d}"  # Convert 14-114 to -50/+50
        elif param in [0x1B, 0x1E]:  # Pitch Env parameters
            return f"{value - 64:+d}"  # Convert 1-127 to -63/+63
        elif param == 0x1F:  # Sub OSC
            return ["OFF", "OCT-1", "OCT-2"][value]
        elif param == 0x20:  # Filter Switch
            return ["BYPASS", "LPF"][value]
        elif param == 0x22:  # Filter Keyfollow
            return f"{((value - 54) * 200 / 20) - 100:+.0f}"  # Convert to -100/+100
        elif param in [0x24, 0x29]:  # Filter Env parameters
            return f"{value - 64:+d}"  # Convert 1-127 to -63/+63
        elif param == 0x2B:  # Amp Keyfollow
            return f"{((value - 54) * 200 / 20) - 100:+.0f}"  # Convert to -100/+100
        elif param == 0x2C:  # Amp Velocity
            return f"{value - 64:+d}"  # Convert 1-127 to -63/+63
        elif param in [0x31, 0x33]:  # Switches
            return "ON" if value else "OFF"
        elif param == 0x34:  # Octave
            return f"{value - 64:+d}"  # Convert 61-67 to -3/+3
        elif param in [0x38, 0x39, 0x3A, 0x3B]:  # Modulation controls
            return f"{value - 64:+d}"  # Convert 1-127 to -63/+63
        return str(value)


class DrumKitCommon:
    """Drum Kit Common parameters"""

    # Kit name (12 characters)
    NAME_1 = 0x00  # Character 1 (ASCII 32-127)
    NAME_2 = 0x01  # Character 2
    NAME_3 = 0x02  # Character 3
    NAME_4 = 0x03  # Character 4
    NAME_5 = 0x04  # Character 5
    NAME_6 = 0x05  # Character 6
    NAME_7 = 0x06  # Character 7
    NAME_8 = 0x07  # Character 8
    NAME_9 = 0x08  # Character 9
    NAME_10 = 0x09  # Character 10
    NAME_11 = 0x0A  # Character 11
    NAME_12 = 0x0B  # Character 12

    # Kit parameters
    LEVEL = 0x0C  # Kit Level (0-127)

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if 0x00 <= param <= 0x0B:  # Name characters
            return chr(value) if 32 <= value <= 127 else "?"
        return str(value)


class DrumKitPartial:
    """Drum Kit Partial parameters"""

    # Partial name (12 characters)
    NAME_1 = 0x00  # Character 1 (ASCII 32-127)
    NAME_2 = 0x01  # Character 2
    NAME_3 = 0x02  # Character 3
    NAME_4 = 0x03  # Character 4
    NAME_5 = 0x04  # Character 5
    NAME_6 = 0x05  # Character 6
    NAME_7 = 0x06  # Character 7
    NAME_8 = 0x07  # Character 8
    NAME_9 = 0x08  # Character 9
    NAME_10 = 0x09  # Character 10
    NAME_11 = 0x0A  # Character 11
    NAME_12 = 0x0B  # Character 12

    # Basic parameters
    ASSIGN_TYPE = 0x0C  # Assign Type (0: MULTI, 1: SINGLE)
    MUTE_GROUP = 0x0D  # Mute Group (0: OFF, 1-31)
    LEVEL = 0x0E  # Partial Level (0-127)
    COARSE = 0x0F  # Coarse Tune (C-1 to G9)
    FINE = 0x10  # Fine Tune (-50/+50)
    RANDOM_PITCH = 0x11  # Random Pitch Depth (0-30)
    PAN = 0x12  # Pan (L64-63R)
    RANDOM_PAN = 0x13  # Random Pan Depth (0-63)
    ALT_PAN = 0x14  # Alternate Pan Depth (L63-63R)
    ENV_MODE = 0x15  # Envelope Mode (0: NO-SUS, 1: SUSTAIN)

    # Output settings
    OUTPUT_LEVEL = 0x16  # Output Level (0-127)
    CHORUS_SEND = 0x19  # Chorus Send Level (0-127)
    REVERB_SEND = 0x1A  # Reverb Send Level (0-127)
    OUTPUT_ASSIGN = 0x1B  # Output Assign (0-4: EFX1,EFX2,DLY,REV,DIR)

    # Performance settings
    BEND_RANGE = 0x1C  # Pitch Bend Range (0-48)
    RX_EXPRESSION = 0x1D  # Receive Expression (0-1)
    RX_HOLD = 0x1E  # Receive Hold-1 (0-1)

    # Wave Mix Table (WMT) settings
    WMT_VEL_CTRL = 0x20  # WMT Velocity Control (0: OFF, 1: ON, 2: RANDOM)

    # Random pitch depth values
    RANDOM_PITCH_VALUES = [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        20,
        30,
        40,
        50,
        60,
        70,
        80,
        90,
        100,
        200,
        300,
        400,
        500,
        600,
        700,
        800,
        900,
        1000,
        1100,
        1200,
    ]

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if 0x00 <= param <= 0x0B:  # Name characters
            return chr(value) if 32 <= value <= 127 else "?"
        elif param == 0x0C:  # Assign Type
            return "SINGLE" if value else "MULTI"
        elif param == 0x0D:  # Mute Group
            return "OFF" if value == 0 else str(value)
        elif param == 0x0F:  # Coarse Tune
            notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
            octave = (value // 12) - 1  # C-1 to G9
            note = notes[value % 12]
            return f"{note}{octave}"
        elif param == 0x10:  # Fine Tune
            return f"{value - 64:+d}"  # Convert 14-114 to -50/+50
        elif param == 0x11:  # Random Pitch
            return str(DrumKitPartial.RANDOM_PITCH_VALUES[value])
        elif param == 0x12:  # Pan
            if value < 64:
                return f"L{64 - value}"
            elif value > 64:
                return f"{value - 64}R"
            return "C"
        elif param == 0x14:  # Alternate Pan
            return f"{value - 64:+d}"  # Convert 1-127 to L63-63R
        elif param == 0x15:  # Envelope Mode
            return "SUSTAIN" if value else "NO-SUS"
        elif param == 0x1B:  # Output Assign
            return ["EFX1", "EFX2", "DLY", "REV", "DIR"][value]
        elif param in [0x1D, 0x1E]:  # Switches
            return "ON" if value else "OFF"
        elif param == 0x20:  # WMT Velocity Control
            return ["OFF", "ON", "RANDOM"][value]
        return str(value)


class DigitalToneCC:
    """SuperNATURAL Synth Tone Control Change parameters"""

    # Direct CC parameters (per partial)
    CUTOFF_1 = 102  # Cutoff Partial 1 (0-127)
    CUTOFF_2 = 103  # Cutoff Partial 2 (0-127)
    CUTOFF_3 = 104  # Cutoff Partial 3 (0-127)

    RESONANCE_1 = 105  # Resonance Partial 1 (0-127)
    RESONANCE_2 = 106  # Resonance Partial 2 (0-127)
    RESONANCE_3 = 107  # Resonance Partial 3 (0-127)

    LEVEL_1 = 117  # Level Partial 1 (0-127)
    LEVEL_2 = 118  # Level Partial 2 (0-127)
    LEVEL_3 = 119  # Level Partial 3 (0-127)

    LFO_RATE_1 = 16  # LFO Rate Partial 1 (0-127)
    LFO_RATE_2 = 17  # LFO Rate Partial 2 (0-127)
    LFO_RATE_3 = 18  # LFO Rate Partial 3 (0-127)

    # NRPN parameters (MSB=0)
    NRPN_ENV_1 = 124  # Envelope Partial 1 (0-127)
    NRPN_ENV_2 = 125  # Envelope Partial 2 (0-127)
    NRPN_ENV_3 = 126  # Envelope Partial 3 (0-127)

    NRPN_LFO_SHAPE_1 = 3  # LFO Shape Partial 1 (0-5)
    NRPN_LFO_SHAPE_2 = 4  # LFO Shape Partial 2 (0-5)
    NRPN_LFO_SHAPE_3 = 5  # LFO Shape Partial 3 (0-5)

    NRPN_LFO_PITCH_1 = 15  # LFO Pitch Depth Partial 1 (0-127)
    NRPN_LFO_PITCH_2 = 16  # LFO Pitch Depth Partial 2 (0-127)
    NRPN_LFO_PITCH_3 = 17  # LFO Pitch Depth Partial 3 (0-127)

    NRPN_LFO_FILTER_1 = 18  # LFO Filter Depth Partial 1 (0-127)
    NRPN_LFO_FILTER_2 = 19  # LFO Filter Depth Partial 2 (0-127)
    NRPN_LFO_FILTER_3 = 20  # LFO Filter Depth Partial 3 (0-127)

    NRPN_LFO_AMP_1 = 21  # LFO Amp Depth Partial 1 (0-127)
    NRPN_LFO_AMP_2 = 22  # LFO Amp Depth Partial 2 (0-127)
    NRPN_LFO_AMP_3 = 23  # LFO Amp Depth Partial 3 (0-127)

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if param in [3, 4, 5]:  # LFO Shape
            shapes = ["TRI", "SIN", "SAW", "SQR", "S&H", "RND"]
            return shapes[value]
        return str(value)


class AnalogToneCC:
    """Analog Synth Tone Control Change parameters"""

    # Direct CC parameters
    CUTOFF = 102  # Cutoff (0-127)
    RESONANCE = 105  # Resonance (0-127)
    LEVEL = 117  # Level (0-127)
    LFO_RATE = 16  # LFO Rate (0-127)

    # NRPN parameters (MSB=0)
    NRPN_ENV = 124  # Envelope (0-127)
    NRPN_LFO_SHAPE = 3  # LFO Shape (0-5)
    NRPN_LFO_PITCH = 15  # LFO Pitch Depth (0-127)
    NRPN_LFO_FILTER = 18  # LFO Filter Depth (0-127)
    NRPN_LFO_AMP = 21  # LFO Amp Depth (0-127)
    NRPN_PW = 37  # Pulse Width (0-127)

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if param == 3:  # LFO Shape
            shapes = ["TRI", "SIN", "SAW", "SQR", "S&H", "RND"]
            return shapes[value]
        return str(value)


class DrumKitCC:
    """Drum Kit Control Change parameters"""

    # NRPN MSB values
    MSB_LEVEL = 64  # Level MSB
    MSB_CUTOFF = 89  # Cutoff MSB
    MSB_RESONANCE = 92  # Resonance MSB
    MSB_ENVELOPE = 119  # Envelope MSB

    # Parameter ranges
    MIN_NOTE = 36  # Lowest drum note (C1)
    MAX_NOTE = 72  # Highest drum note (C4)
    MIN_VALUE = 0  # Minimum parameter value
    MAX_VALUE = 127  # Maximum parameter value

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        return str(value)

    @staticmethod
    def validate_note(note: int) -> bool:
        """Validate note is within drum kit range"""
        return DrumKitCC.MIN_NOTE <= note <= DrumKitCC.MAX_NOTE

    @staticmethod
    def validate_msb(msb: int) -> bool:
        """Validate MSB value is valid"""
        return msb in [
            DrumKitCC.MSB_LEVEL,
            DrumKitCC.MSB_CUTOFF,
            DrumKitCC.MSB_RESONANCE,
            DrumKitCC.MSB_ENVELOPE,
        ]

    @staticmethod
    def validate_value(value: int) -> bool:
        """Validate parameter value is within range"""
        return DrumKitCC.MIN_VALUE <= value <= DrumKitCC.MAX_VALUE


# Bank Select MSB/LSB values
BANK_MSB = 0x55  # 85 (0x55) for all JD-Xi banks
BANK_LSB = {
    "USER_E": 0x00,  # User Bank E (001-064)
    "USER_F": 0x00,  # User Bank F (065-128)
    "USER_G": 0x01,  # User Bank G (001-064)
    "USER_H": 0x01,  # User Bank H (065-128)
    "PRESET_A": 0x40,  # Preset Bank A (001-064) [64 decimal]
    "PRESET_B": 0x40,  # Preset Bank B (065-128)
    "PRESET_C": 0x41,  # Preset Bank C (001-064) [65 decimal]
    "PRESET_D": 0x41,  # Preset Bank D (065-128)
    "EXTRA_S": 0x60,  # Extra Bank S (001-064) [96 decimal]
    # ... other extra banks
    "EXTRA_Z": 0x67,  # Extra Bank Z (001-064) [103 decimal]
}

# Bank Select MSB values for different synth types
ANALOG_BANK_MSB = 0x5E  # 94 (0x5E) for Analog synth
DIGITAL_BANK_MSB = 0x5F  # 95 (0x5F) for Digital synth (SuperNATURAL)
DRUM_BANK_MSB = 0x56  # 86 (0x56) for Drum kits

# Bank Select LSB values
PRESET_BANK_LSB = 0x40  # 64 (0x40) for preset bank
PRESET_BANK_2_LSB = 0x41  # 65 (0x41) for second preset bank (Digital only)

# Digital Synth Parameters
DIGITAL_SYNTH_1_AREA = 0x19
PART_1 = 0x01
OSC_PARAM_GROUP = 0x20

# Waveforms
WAVE_SAW = 0x00
WAVE_SQUARE = 0x01
WAVE_PULSE = 0x02
WAVE_TRIANGLE = 0x03
WAVE_SINE = 0x04
WAVE_NOISE = 0x05
WAVE_SUPER_SAW = 0x06
WAVE_PCM = 0x07

# Memory Areas
PROGRAM_AREA = 0x18
DIGITAL_SYNTH_1_AREA = 0x19
DIGITAL_SYNTH_2_AREA = 0x1A
ANALOG_SYNTH_AREA = 0x1B
DRUM_KIT_AREA = 0x1C

# Part Numbers
PART_1 = 0x01
PART_2 = 0x02
PART_3 = 0x03
PART_4 = 0x04

# Parameter Groups
OSC_1_GROUP = 0x20  # Oscillator 1 parameters
OSC_2_GROUP = 0x21  # Oscillator 2 parameters
FILTER_GROUP = 0x22  # Filter parameters
AMP_GROUP = 0x23  # Amplifier parameters
LFO_1_GROUP = 0x24  # LFO 1 parameters
LFO_2_GROUP = 0x25  # LFO 2 parameters
EFFECTS_GROUP = 0x26  # Effects parameters

# Parameter Numbers
OSC_WAVE_PARAM = 0x00  # Oscillator waveform parameter

# SuperNATURAL Synth Tone Parameters
OSC_WAVE_PARAM = 0x00  # Oscillator wave (0-7)
OSC_VARIATION_PARAM = 0x01  # Wave variation (0-2)
OSC_PITCH_PARAM = 0x03  # Pitch (40-88 = -24 to +24)
OSC_DETUNE_PARAM = 0x04  # Detune (14-114 = -50 to +50)
OSC_PWM_DEPTH_PARAM = 0x05  # PW Mod depth (0-127)
OSC_PW_PARAM = 0x06  # Pulse width (0-127)
OSC_PITCH_ENV_A_PARAM = 0x07  # Pitch env attack (0-127)
OSC_PITCH_ENV_D_PARAM = 0x08  # Pitch env decay (0-127)
OSC_PITCH_ENV_DEPTH_PARAM = 0x09  # Pitch env depth (1-127 = -63 to +63)

# Filter Parameters
FILTER_MODE_PARAM = 0x0A  # Filter mode (0-7)
FILTER_SLOPE_PARAM = 0x0B  # Filter slope (0-1)
FILTER_CUTOFF_PARAM = 0x0C  # Cutoff frequency (0-127)
FILTER_KEYFOLLOW_PARAM = 0x0D  # Cutoff keyfollow (54-74 = -100 to +100)
FILTER_ENV_VELO_PARAM = 0x0E  # Env velocity sens (1-127 = -63 to +63)
FILTER_RESONANCE_PARAM = 0x0F  # Resonance (0-127)
FILTER_ENV_A_PARAM = 0x10  # Env attack time (0-127)
FILTER_ENV_D_PARAM = 0x11  # Env decay time (0-127)
FILTER_ENV_S_PARAM = 0x12  # Env sustain level (0-127)
FILTER_ENV_R_PARAM = 0x13  # Env release time (0-127)
FILTER_ENV_DEPTH_PARAM = 0x14  # Env depth (1-127 = -63 to +63)

# Filter Mode Values
FILTER_MODE_BYPASS = 0x00
FILTER_MODE_LPF = 0x01
FILTER_MODE_HPF = 0x02
FILTER_MODE_BPF = 0x03
FILTER_MODE_PKG = 0x04
FILTER_MODE_LPF2 = 0x05
FILTER_MODE_LPF3 = 0x06
FILTER_MODE_LPF4 = 0x07

# Filter Slope Values
FILTER_SLOPE_12DB = 0x00  # -12 dB
FILTER_SLOPE_24DB = 0x01  # -24 dB

# Amplifier Parameters
AMP_LEVEL_PARAM = 0x15  # Amp level (0-127)
AMP_VELO_SENS_PARAM = 0x16  # Level velocity sens (1-127 = -63 to +63)
AMP_ENV_A_PARAM = 0x17  # Env attack time (0-127)
AMP_ENV_D_PARAM = 0x18  # Env decay time (0-127)
AMP_ENV_S_PARAM = 0x19  # Env sustain level (0-127)
AMP_ENV_R_PARAM = 0x1A  # Env release time (0-127)
AMP_PAN_PARAM = 0x1B  # Pan position (0-127 = L64-63R)

# LFO Parameters
LFO_SHAPE_PARAM = 0x1C  # LFO shape (0-5)
LFO_RATE_PARAM = 0x1D  # Rate (0-127)
LFO_TEMPO_SYNC_PARAM = 0x1E  # Tempo sync switch (0-1)
LFO_SYNC_NOTE_PARAM = 0x1F  # Tempo sync note (0-19)
LFO_FADE_TIME_PARAM = 0x20  # Fade time (0-127)
LFO_KEY_TRIGGER_PARAM = 0x21  # Key trigger (0-1)
LFO_PITCH_DEPTH_PARAM = 0x22  # Pitch depth (1-127 = -63 to +63)
LFO_FILTER_DEPTH_PARAM = 0x23  # Filter depth (1-127 = -63 to +63)
LFO_AMP_DEPTH_PARAM = 0x24  # Amp depth (1-127 = -63 to +63)
LFO_PAN_DEPTH_PARAM = 0x25  # Pan depth (1-127 = -63 to +63)

# Aftertouch Parameters
CUTOFF_AFTERTOUCH_PARAM = 0x30  # Cutoff aftertouch sensitivity (1-127 = -63 to +63)
LEVEL_AFTERTOUCH_PARAM = 0x31  # Level aftertouch sensitivity (1-127 = -63 to +63)


# LFO Shape Values
class LFOShape(Enum):
    """LFO waveform shapes"""

    TRIANGLE = 0x00  # Triangle wave
    SINE = 0x01  # Sine wave
    SAW = 0x02  # Sawtooth wave
    SQUARE = 0x03  # Square wave
    SAMPLE_HOLD = 0x04  # Sample & Hold
    RANDOM = 0x05  # Random

    @staticmethod
    def get_display_name(value: int) -> str:
        """Get display name for LFO shape"""
        names = {0: "TRI", 1: "SIN", 2: "SAW", 3: "SQR", 4: "S&H", 5: "RND"}
        return names.get(value, "???")


# LFO Sync Note Values
class LFOSyncNote(Enum):
    """LFO sync note values"""

    BAR_16 = 0  # 16 bars
    BAR_12 = 1  # 12 bars
    BAR_8 = 2  # 8 bars
    BAR_4 = 3  # 4 bars
    BAR_2 = 4  # 2 bars
    BAR_1 = 5  # 1 bar
    BAR_3_4 = 6  # 3/4 bar
    BAR_2_3 = 7  # 2/3 bar
    BAR_1_2 = 8  # 1/2 bar
    BAR_3_8 = 9  # 3/8 bar
    BAR_1_3 = 10  # 1/3 bar
    BAR_1_4 = 11  # 1/4 bar
    BAR_3_16 = 12  # 3/16 bar
    BAR_1_6 = 13  # 1/6 bar
    BAR_1_8 = 14  # 1/8 bar
    BAR_3_32 = 15  # 3/32 bar
    BAR_1_12 = 16  # 1/12 bar
    BAR_1_16 = 17  # 1/16 bar
    BAR_1_24 = 18  # 1/24 bar
    BAR_1_32 = 19  # 1/32 bar

    @staticmethod
    def get_display_name(value: int) -> str:
        """Get display name for sync note value"""
        names = {
            0: "16",
            1: "12",
            2: "8",
            3: "4",
            4: "2",
            5: "1",
            6: "3/4",
            7: "2/3",
            8: "1/2",
            9: "3/8",
            10: "1/3",
            11: "1/4",
            12: "3/16",
            13: "1/6",
            14: "1/8",
            15: "3/32",
            16: "1/12",
            17: "1/16",
            18: "1/24",
            19: "1/32",
        }
        return names.get(value, "???")

    @staticmethod
    def get_all_display_names() -> list:
        """Get list of all display names in order"""
        return [LFOSyncNote.get_display_name(i) for i in range(20)]


# LFO Shape Values
LFO_SHAPE_TRI = 0x00  # Triangle
LFO_SHAPE_SIN = 0x01  # Sine
LFO_SHAPE_SAW = 0x02  # Sawtooth
LFO_SHAPE_SQR = 0x03  # Square
LFO_SHAPE_SH = 0x04  # Sample & Hold
LFO_SHAPE_RND = 0x05  # Random

# LFO Sync Note Values
LFO_SYNC_NOTES = [
    "16",  # 0
    "12",  # 1
    "8",  # 2
    "4",  # 3
    "2",  # 4
    "1",  # 5
    "3/4",  # 6
    "2/3",  # 7
    "1/2",  # 8
    "3/8",  # 9
    "1/3",  # 10
    "1/4",  # 11
    "3/16",  # 12
    "1/6",  # 13
    "1/8",  # 14
    "3/32",  # 15
    "1/12",  # 16
    "1/16",  # 17
    "1/24",  # 18
    "1/32",  # 19
]
