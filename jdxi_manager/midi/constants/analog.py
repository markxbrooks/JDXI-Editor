"""Analog synth MIDI constants"""

from enum import Enum

# Areas and Parts
ANALOG_SYNTH_AREA = 0x01
ANALOG_PART = 0x00

# Analog Oscillator Parameters
ANALOG_OSC_WAVE = 0x16        # Waveform (0-2: SAW,TRI,PW-SQR)
ANALOG_OSC_COARSE = 0x17      # Pitch Coarse (40-88: -24 to +24)
ANALOG_OSC_FINE = 0x18        # Pitch Fine (14-114: -50 to +50)
ANALOG_OSC_PW = 0x19          # Pulse Width (0-127)
ANALOG_OSC_PWM = 0x1A         # PW Mod Depth (0-127)
ANALOG_OSC_PENV_VELO = 0x1B   # Pitch Env Velocity (1-127: -63 to +63)
ANALOG_OSC_PENV_A = 0x1C      # Pitch Env Attack (0-127)
ANALOG_OSC_PENV_D = 0x1D      # Pitch Env Decay (0-127)
ANALOG_OSC_PENV_DEPTH = 0x1E  # Pitch Env Depth (1-127: -63 to +63)
ANALOG_SUB_TYPE = 0x1F        # Sub Osc Type (0-2: OFF,OCT-1,OCT-2)

# Analog Synth Parameters
ANALOG_FILTER_CUTOFF = 0x21  # Filter cutoff frequency (0-127)
ANALOG_FILTER_RESONANCE = 0x23  # Filter resonance (0-127)
ANALOG_AMP_LEVEL = 0x2A  # Amplifier level (0-127)
ANALOG_LFO_SHAPE = 0x30  # LFO waveform shape (0-5)
ANALOG_LFO_RATE = 0x31  # LFO rate (0-127)

# Analog Synth Areas and Parts
ANALOG_SYNTH_AREA = 0x1B    # Analog synth area
ANALOG_PART = 0x01          # Analog synth part

# Analog Synth Parameter Groups
ANALOG_OSC_GROUP = 0x00     # Oscillator parameters
ANALOG_FILTER_GROUP = 0x01  # Filter parameters
ANALOG_AMP_GROUP = 0x02     # Amplifier parameters
ANALOG_LFO_GROUP = 0x03     # LFO parameters

# Analog LFO Parameters
ANALOG_LFO_SHAPE = 0x0D        # LFO Shape (0-5: TRI,SIN,SAW,SQR,S&H,RND)
ANALOG_LFO_RATE = 0x0E         # LFO Rate (0-127)
ANALOG_LFO_FADE = 0x0F         # LFO Fade Time (0-127)
ANALOG_LFO_SYNC = 0x10         # LFO Tempo Sync Switch (0-1)
ANALOG_LFO_SYNC_NOTE = 0x11    # LFO Tempo Sync Note (0-19)
ANALOG_LFO_PITCH = 0x12        # LFO Pitch Depth (1-127: -63 to +63)
ANALOG_LFO_FILTER = 0x13       # LFO Filter Depth (1-127: -63 to +63)
ANALOG_LFO_AMP = 0x14          # LFO Amp Depth (1-127: -63 to +63)
ANALOG_LFO_KEY_TRIG = 0x15     # LFO Key Trigger (0-1)

class AnalogToneCC:
    """Analog Synth Control Change parameters"""
    # Oscillator Parameters
    OSC_WAVE = 0x16        # Waveform (0-2: SAW,TRI,PW-SQR)
    OSC_COARSE = 0x17      # Pitch Coarse (40-88: -24 to +24)
    OSC_FINE = 0x18        # Pitch Fine (14-114: -50 to +50)
    OSC_PW = 0x19          # Pulse Width (0-127)
    OSC_PWM = 0x1A         # PW Mod Depth (0-127)
    OSC_PENV_VELO = 0x1B   # Pitch Env Velocity (1-127: -63 to +63)
    OSC_PENV_A = 0x1C      # Pitch Env Attack (0-127)
    OSC_PENV_D = 0x1D      # Pitch Env Decay (0-127)
    OSC_PENV_DEPTH = 0x1E  # Pitch Env Depth (1-127: -63 to +63)
    
    # Filter parameters
    FILTER_CUTOFF = 0x21   # Filter cutoff frequency (0-127)
    FILTER_RESO = 0x23     # Filter resonance (0-127)
    FILTER_ENV_A = 0x24    # Filter envelope attack (0-127)
    FILTER_ENV_D = 0x25    # Filter envelope decay (0-127)
    FILTER_ENV_S = 0x26    # Filter envelope sustain (0-127)
    FILTER_ENV_R = 0x27    # Filter envelope release (0-127)
    FILTER_ENV_DEPTH = 0x28 # Filter envelope depth (-63 to +63)
    
    # Amplifier parameters
    AMP_LEVEL = 0x2A       # Amplifier level (0-127)
    AMP_ENV_A = 0x2B       # Amplifier envelope attack (0-127)
    AMP_ENV_D = 0x2C       # Amplifier envelope decay (0-127)
    AMP_ENV_S = 0x2D       # Amplifier envelope sustain (0-127)
    AMP_ENV_R = 0x2E       # Amplifier envelope release (0-127)
    
    # LFO parameters
    LFO_SHAPE = 0x30       # LFO waveform shape (0-5)
    LFO_RATE = 0x31        # LFO rate (0-127)
    LFO_DEPTH = 0x32       # LFO depth (0-127)

class AnalogOscWave(Enum):
    """Analog oscillator waveform types"""
    SAW = 0
    TRIANGLE = 1
    PULSE = 2

    @staticmethod
    def get_display_name(value: int) -> str:
        """Get display name for waveform"""
        names = {
            0: "SAW",
            1: "TRI",
            2: "P.W"
        }
        return names.get(value, "???")

# Sub oscillator types  
class AnalogSubType(Enum):
    """Analog sub oscillator types"""
    OFF = 0
    OCT_DOWN_1 = 1  # -1 octave
    OCT_DOWN_2 = 2  # -2 octaves

    @staticmethod
    def get_display_name(value: int) -> str:
        """Get display name for sub oscillator type"""
        names = {
            0: "OFF",
            1: "-1 OCT",
            2: "-2 OCT"
        }
        return names.get(value, "???")

# Analog LFO Shape Values
class AnalogLFOShape(Enum):
    """Analog LFO waveform shapes"""
    TRIANGLE = 0    # Triangle wave
    SINE = 1        # Sine wave
    SAW = 2         # Sawtooth wave
    SQUARE = 3      # Square wave
    SAMPLE_HOLD = 4 # Sample & Hold
    RANDOM = 5      # Random

    @staticmethod
    def get_display_name(value: int) -> str:
        """Get display name for LFO shape"""
        names = {
            0: "TRI",
            1: "SIN", 
            2: "SAW",
            3: "SQR",
            4: "S&H",
            5: "RND"
        }
        return names.get(value, "???")

# Analog LFO Sync Note Values
ANALOG_LFO_SYNC_NOTES = [
    "16",    # 0
    "12",    # 1
    "8",     # 2
    "4",     # 3
    "2",     # 4
    "1",     # 5
    "3/4",   # 6
    "2/3",   # 7
    "1/2",   # 8
    "3/8",   # 9
    "1/3",   # 10
    "1/4",   # 11
    "3/16",  # 12
    "1/6",   # 13
    "1/8",   # 14
    "3/32",  # 15
    "1/12",  # 16
    "1/16",  # 17
    "1/24",  # 18
    "1/32"   # 19
]

# Parameter value ranges
ANALOG_LFO_RANGES = {
    'shape': (0, 5),
    'rate': (0, 127),
    'fade': (0, 127),
    'sync': (0, 1),
    'sync_note': (0, 19),
    'pitch': (-63, 63),
    'filter': (-63, 63),
    'amp': (-63, 63),
    'key_trig': (0, 1)
}
