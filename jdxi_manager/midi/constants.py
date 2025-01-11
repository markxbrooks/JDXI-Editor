"""Constants for Roland JD-Xi MIDI protocol"""

from enum import Enum, auto

# SysEx constants
START_OF_SYSEX = 0xF0
END_OF_SYSEX = 0xF7

# Manufacturer constants
ROLAND_ID = 0x41
DEVICE_ID = 0x10
MODEL_ID_1 = 0x00
MODEL_ID_2 = 0x00
MODEL_ID = 0x00
JD_XI_ID = 0x0E

# Command constants
DT1_COMMAND_12 = 0x12  # Data transfer command

# Memory areas
DIGITAL_SYNTH_AREA = 0x19  # Base area for digital synths
DIGITAL_SYNTH_1 = 0x19     # Digital synth 1
DIGITAL_SYNTH_2 = 0x1A     # Digital synth 2
ANALOG_SYNTH_AREA = 0x18   # Analog synth
DRUM_KIT_AREA = 0x17       # Drum kit
EFFECTS_AREA = 0x16        # Effects
ARPEGGIO_AREA = 0x15       # Arpeggiator
VOCAL_FX_AREA = 0x14       # Vocal effects
SYSTEM_AREA = 0x01         # System settings

# Part numbers
DIGITAL_PART_1 = 0x01      # Digital synth 1 part
DIGITAL_PART_2 = 0x02      # Digital synth 2 part
ANALOG_PART = 0x00         # Analog synth part
DRUM_PART = 0x00          # Drum part
VOCAL_PART = 0x00         # Vocal part
SYSTEM_PART = 0x00        # System part

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
    SAW = 0x00         # Sawtooth wave
    SQUARE = 0x01      # Square wave
    PW_SQUARE = 0x02   # Pulse width square wave
    TRIANGLE = 0x03    # Triangle wave
    SINE = 0x04        # Sine wave
    NOISE = 0x05       # Noise
    SUPER_SAW = 0x06   # Super saw
    PCM = 0x07         # PCM waveform

class ArpeggioGroup(Enum):
    """Arpeggiator parameter groups"""
    COMMON = 0x00    # Common parameters
    PATTERN = 0x10   # Pattern parameters
    RHYTHM = 0x20    # Rhythm parameters
    NOTE = 0x30      # Note parameters

class DigitalGroup(Enum):
    """Digital synth parameter groups"""
    COMMON = 0x00   # Common parameters
    PARTIAL = 0x20  # Partial parameters
    LFO = 0x40     # LFO parameters
    ENV = 0x60     # Envelope parameters

class EffectGroup(Enum):
    """Effect parameter groups"""
    COMMON = 0x00   # Common parameters
    INSERT = 0x10   # Insert effect parameters
    REVERB = 0x20   # Reverb parameters
    DELAY = 0x30    # Delay parameters

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
        OSC_WAVE = 0x00       # Waveform selection
        OSC_PITCH = 0x01      # Pitch (-24 to +24 semitones)
        OSC_FINE = 0x02       # Fine tune (-50 to +50 cents)
        OSC_PWM = 0x03        # Pulse width (0-127)
        OSC_ENV_DEPTH = 0x04  # Pitch env depth
        OSC_PW_ENV = 0x05     # PW env depth
        
        # Filter parameters (0x0A-0x0F)
        FILTER_TYPE = 0x0A    # Filter type (LPF, HPF, BPF, PKG)
        FILTER_CUTOFF = 0x0B  # Cutoff frequency
        FILTER_RESO = 0x0C    # Resonance
        FILTER_ENV = 0x0D     # Filter env depth
        FILTER_KEY = 0x0E     # Key follow
        FILTER_VELO = 0x0F    # Velocity sensitivity
        
        # Amplifier parameters (0x15-0x1F)
        AMP_LEVEL = 0x15      # Level
        AMP_PAN = 0x16        # Pan
        AMP_VELO = 0x17       # Velocity sensitivity
        
        # LFO parameters (0x30-0x3F)
        LFO_WAVE = 0x30       # LFO waveform
        LFO_RATE = 0x31       # LFO rate
        LFO_FADE = 0x32       # Fade time
        LFO_PITCH = 0x33      # Pitch modulation
        LFO_FILTER = 0x34     # Filter modulation
        LFO_AMP = 0x35        # Amp modulation
        LFO_PW = 0x36         # PW modulation
        LFO_PHASE = 0x37      # Phase
        LFO_KEY = 0x38        # Key trigger
        
        # Envelope parameters (0x40-0x4F)
        ENV_ATTACK = 0x40     # Attack time
        ENV_DECAY = 0x41      # Decay time
        ENV_SUSTAIN = 0x42    # Sustain level
        ENV_RELEASE = 0x43    # Release time
        ENV_KEY = 0x44        # Key follow
        ENV_VELO = 0x45       # Velocity sensitivity

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

# Other constants as needed... 