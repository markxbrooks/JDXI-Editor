"""Analog synth MIDI constants"""

from enum import Enum, IntEnum
from .sysex import ANALOG_SYNTH_AREA  # Remove this import

# Areas and Parts
ANALOG_SYNTH_AREA = 0x19  # Changed from 0x1B to 0x19 @@ Incorrect!
ANALOG_PART = 0x42  # Changed from 0x00 to 0x42


# Control Change Parameters
class AnalogToneCC(IntEnum):
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

    # Oscillator Parameters
    OSC_WAVE = 0x16  # Waveform (0-2: SAW,TRI,PW-SQR)
    OSC_COARSE = 0x17  # Pitch Coarse (40-88: -24 to +24)
    OSC_FINE = 0x18  # Pitch Fine (14-114: -50 to +50)
    OSC_PW = 0x19  # Pulse Width (0-127)
    OSC_PWM = 0x1A  # PW Mod Depth (0-127)
    OSC_PENV_VELO = 0x1B  # Pitch Env Velocity (1-127: -63 to +63, 64=center)
    OSC_PENV_A = 0x1C  # Pitch Env Attack (0-127)
    OSC_PENV_D = 0x1D  # Pitch Env Decay (0-127)
    OSC_PENV_DEPTH = 0x1E  # Pitch Env Depth (1-127: -63 to +63, 64=center)
    SUB_TYPE = 0x1F  # Sub Oscillator Type (0-2: OFF,OCT-1,OCT-2)

    # Filter parameters
    FILTER_CUTOFF = 0x21  # Filter cutoff frequency (0-127)
    FILTER_RESO = 0x23  # Filter resonance (0-127)
    FILTER_ENV_A = 0x24  # Filter envelope attack (0-127)
    FILTER_ENV_D = 0x25  # Filter envelope decay (0-127)
    FILTER_ENV_S = 0x26  # Filter envelope sustain (0-127)
    FILTER_ENV_R = 0x27  # Filter envelope release (0-127)
    FILTER_ENV_DEPTH = 0x28  # Filter envelope depth (-63 to +63)

    # Amplifier parameters
    AMP_LEVEL = 0x2A  # Amplifier level (0-127)
    AMP_ENV_A = 0x2B  # Amplifier envelope attack (0-127) !!! Incorrect -> 2D
    AMP_ENV_D = 0x2C  # Amplifier envelope decay (0-127)
    AMP_ENV_S = 0x2D  # Amplifier envelope sustain (0-127)
    AMP_ENV_R = 0x2E  # Amplifier envelope release (0-127)

    # LFO parameters
    LFO_SHAPE = 0x0D  # LFO Shape (0-5: TRI,SIN,SAW,SQR,S&H,RND)
    LFO_RATE = 0x0E  # LFO Rate (0-127)
    LFO_FADE = 0x0F  # LFO Fade Time (0-127)
    LFO_SYNC = 0x10  # LFO Tempo Sync Switch (0-1)
    LFO_SYNC_NOTE = 0x11  # LFO Tempo Sync Note (0-19)
    LFO_PITCH = 0x12  # LFO Pitch Depth (1-127: -63 to +63)
    LFO_FILTER = 0x13  # LFO Filter Depth (1-127: -63 to +63)
    LFO_AMP = 0x14  # LFO Amp Depth (1-127: -63 to +63)
    LFO_KEY_TRIG = 0x15  # LFO Key Trigger (0-1)

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if param == 3:  # LFO Shape
            shapes = ["TRI", "SIN", "SAW", "SQR", "S&H", "RND"]
            return shapes[value]
        return str(value)


# Parameter Groups
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
        """Get display name for sub oscillator type"""
        names = {0x00: "OFF", 0x01: "-1 OCT", 0x02: "-2 OCT"}
        return names.get(self.value, "???")

    @property
    def midi_value(self) -> int:
        """Get MIDI value for sub oscillator type"""
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


class AnalogParameters(IntEnum):
    """Analog synth parameters"""

    # Oscillator
    OSC_WAVE = 0x00  # Oscillator waveform (0-3)
    OSC_MOD = 0x01  # Oscillator mod (0-127)
    OSC_PITCH = 0x02  # Oscillator pitch (-24 to +24)
    OSC_DETUNE = 0x03  # Oscillator detune (-50 to +50)
    OSC_LEVEL = 0x04  # Oscillator level (0-127)

    # Filter
    FILTER_TYPE = 0x10  # Filter type (0-3)
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
