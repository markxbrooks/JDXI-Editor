"""
Analog Synth MIDI Constants Module

This module defines MIDI constants, control change parameters, NRPN values,
and enumerations for the analog synthesizer section of the JD-Xi. It includes:

- MIDI control change (CC) and NRPN mappings for analog synth parameters
- Enumerations for waveform types, LFO shapes, filter types, and other synth parameters
- Utility functions for constructing and sending MIDI NRPN messages
- Display name mappings for user-friendly representation of values

These constants and utilities facilitate interaction with the JD-Xi analog synth
via MIDI, enabling precise parameter control and automation.

Classes:
--------
- `ControlChange`: Base class for synth CC parameters
- `AnalogControlChange`: Analog synth CC parameters and NRPN mappings
- `DigitalSynth1ControlChange`: Digital synth CC parameters (placeholder)
- `Waveform`: Enumeration of analog oscillator waveforms
- `SubOscType`: Enumeration of sub-oscillator types
- `LFOShape`: Enumeration of LFO waveform shapes
- `AnalogParameters`: Enumeration of analog synth parameters
- `OscillatorWave`: Enumeration of oscillator waveforms
- `FilterType`: Enumeration of filter types
- `LFOWave`: Enumeration of LFO waveforms

Functions:
----------
- `get_partial_cc(base_cc: int, partial: int) -> int`
- `send_nrpn(midi_out, msb: int, lsb: int, value: int)`

Usage:
------
This module is intended for use in MIDI-based applications interacting
with the JD-Xi synthesizer's analog engine.

"""
from dataclasses import dataclass
from enum import Enum, IntEnum

from jdxi_editor.midi.data.constants.sysex import DT1_COMMAND_12
from jdxi_editor.midi.data.parameter.synth import SynthParameter
from jdxi_editor.midi.message.roland import RolandSysEx

# Areas and Parts
ANALOG_SYNTH_AREA = 0x19  # Changed from 0x1B to 0x19
ANALOG_PART = 0x42  # Changed from 0x00 to 0x42


# Control Change Parameters
class ControlChange(IntEnum):
    """Base class for Synth Control Change parameters"""

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if param == 3:  # LFO Shape
            shapes = ["TRI", "SIN", "SAW", "SQR", "S&H", "RND"]
            return shapes[value]
        return str(value)


# Analog Control Change Parameters
class AnalogControlChange(ControlChange):
    """Analog synth CC parameters"""

    # Direct CC parameters
    CUTOFF_CC = 102  # Cutoff (0-127)
    RESONANCE_CC = 105  # Resonance (0-127)
    LEVEL_CC = 117  # Level (0-127)
    LFO_RATE_CC = 16  # LFO Rate (0-127)

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


# Digital Control Change Parameters
class DigitalSynth1ControlChange(ControlChange):
    """Analog synth CC parameters"""

    # Direct CC parameters
    CUTOFF_CC = 102  # Cutoff (0-127)
    RESONANCE_CC = 105  # Resonance (0-127)
    LEVEL_CC = 117  # Level (0-127)
    LFO_RATE_CC = 16  # LFO Rate (0-127)

    # NRPN parameters (MSB=0)
    NRPN_ENV = 124  # Envelope (0-127)
    NRPN_LFO_SHAPE = 3  # LFO Shape (0-5)
    NRPN_LFO_PITCH = 15  # LFO Pitch Depth (0-127)
    NRPN_LFO_FILTER = 18  # LFO Filter Depth (0-127)
    NRPN_LFO_AMP = 21  # LFO Amp Depth (0-127)
    NRPN_PW = 37  # Pulse Width (0-127)

    @staticmethod
    def get_value_for_partial(value: int, partial_number: int) -> str:
        """Convert raw value to display value"""
        return value + (partial_number - 1)

def get_partial_cc(base_cc: int, partial: int) -> int:
    """Get the CC number for a given partial (1-3) based on the base CC."""
    return base_cc + (partial - 1)

from mido import Message

def send_nrpn(midi_out, msb: int, lsb: int, value: int):
    """Send an NRPN message via MIDI."""
    midi_out.send(Message('control_change', control=99, value=msb))  # NRPN MSB
    midi_out.send(Message('control_change', control=98, value=lsb))  # NRPN LSB
    midi_out.send(Message('control_change', control=6, value=value))  # Data Entry MSB


ANALOG_OSC_GROUP = 0x00  # Oscillator parameters
ANALOG_FILTER_GROUP = 0x01  # Filter parameters
ANALOG_AMP_GROUP = 0x02  # Amplifier parameters
ANALOG_LFO_GROUP = 0x03  # LFO parameters


# Waveform
class Waveform(Enum):
    """Analog oscillator waveform types"""

    SAW = 0
    TRIANGLE = 1
    PULSE = 2  # Changed from SQUARE to PULSE to match JD-Xi terminology

    @property
    def display_name(self) -> str:
        """Get display name for waveform"""
        names = {0: "SAW", 1: "TRI", 2: "P.W"}  # Updated display name
        return names.get(self.value, "???")

    @property
    def midi_value(self) -> int:
        """Get MIDI value for waveform"""
        return self.value


class SubOscType(Enum):
    """Analog sub oscillator types"""

    OFF = 0x00  # Sub oscillator off
    OCT_DOWN_1 = 0x01  # -1 octave
    OCT_DOWN_2 = 0x02  # -2 octaves

    @property
    def display_name(self) -> str:
        """Get display name for sub oscillator preset_type"""
        names = {0x00: "OFF", 0x01: "-1 OCT", 0x02: "-2 OCT"}
        return names.get(self.value, "???")

    @property
    def midi_value(self) -> int:
        """Get MIDI value for sub oscillator preset_type"""
        return self.value


class LFOShape(Enum):
    """Analog LFO waveform shapes"""

    TRIANGLE = 0  # Triangle wave
    SINE = 1  # Sine wave
    SAW = 2  # Sawtooth wave
    SQUARE = 3  # Square wave
    SAMPLE_HOLD = 4  # Sample & Hold
    RANDOM = 5  # Random

    @property
    def display_name(self) -> str:
        """Get display name for LFO shape"""
        names = {0: "TRI", 1: "SIN", 2: "SAW", 3: "SQR", 4: "S&H", 5: "RND"}
        return names.get(self.value, "???")


# Parameter value ranges
LFO_RANGES = {
    "shape": (0, 5),
    "rate": (0, 127),
    "fade": (0, 127),
    "sync": (0, 1),
    "sync_note": (0, 19),
    "pitch": (-63, 63),
    "filter": (-63, 63),
    "amp": (-63, 63),
    "key_trig": (0, 1),
}

# LFO Sync Note Values
LFO_TEMPO_SYNC_NOTES = [
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


class AnalogParameters(IntEnum):
    """Analog synth parameters"""

    # Oscillator
    OSC_WAVE = 0x00  # Oscillator waveform (0-3)
    OSC_MOD = 0x01  # Oscillator mod (0-127)
    OSC_PITCH = 0x02  # Oscillator pitch (-24 to +24)
    OSC_DETUNE = 0x03  # Oscillator detune (-50 to +50)
    OSC_LEVEL = 0x04  # Oscillator level (0-127)

    # Filter
    FILTER_TYPE = 0x10  # Filter preset_type (0-3)
    FILTER_CUTOFF = 0x11  # Filter cutoff (0-127)
    FILTER_RESO = 0x12  # Filter resonance (0-127)
    FILTER_ENV = 0x13  # Filter envelope depth (-63 to +63)
    FILTER_KEY = 0x14  # Filter keyboard follow (0-127)

    # Amplifier
    AMP_LEVEL = 0x20  # Amplifier level (0-127)
    AMP_PAN = 0x21  # Amplifier pan (0-127, 64=center)

    # Envelopes
    FILTER_ATTACK = 0x30  # Filter envelope attack (0-127)
    FILTER_DECAY = 0x31  # Filter envelope decay (0-127)
    FILTER_SUSTAIN = 0x32  # Filter envelope sustain (0-127)
    FILTER_RELEASE = 0x33  # Filter envelope release (0-127)

    AMP_ATTACK = 0x34  # Amplifier envelope attack (0-127)
    AMP_DECAY = 0x35  # Amplifier envelope decay (0-127)
    AMP_SUSTAIN = 0x36  # Amplifier envelope sustain (0-127)
    AMP_RELEASE = 0x37  # Amplifier envelope release (0-127)

    # LFO
    LFO_WAVE = 0x40  # LFO waveform (0-3)
    LFO_RATE = 0x41  # LFO rate (0-127)
    LFO_FADE = 0x42  # LFO fade time (0-127)
    LFO_PITCH = 0x43  # LFO pitch depth (0-127)
    LFO_FILTER = 0x44  # LFO filter depth (0-127)
    LFO_AMP = 0x45  # LFO amplitude depth (0-127)

    # Effects sends
    DELAY_SEND = 0x50  # Delay send level (0-127)
    REVERB_SEND = 0x51  # Reverb send level (0-127)


class OscillatorWave(IntEnum):
    """Analog oscillator waveforms"""

    SAW = 0
    SQUARE = 1
    TRIANGLE = 2
    SINE = 3


class FilterType(IntEnum):
    """Analog filter types"""

    LPF = 0  # Low Pass Filter
    HPF = 1  # High Pass Filter
    BPF = 2  # Band Pass Filter
    PKG = 3  # Peaking Filter


class LFOWave(IntEnum):
    """Analog LFO waveforms"""

    TRIANGLE = 0
    SINE = 1
    SAW = 2
    SQUARE = 3


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
