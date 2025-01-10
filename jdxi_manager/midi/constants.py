"""Constants for Roland JD-Xi MIDI protocol"""

# SysEx message structure
START_OF_SYSEX = 0xF0
ROLAND_ID = 0x41
DEVICE_ID = 0x10
MODEL_ID_1 = 0x00
MODEL_ID_2 = 0x00
MODEL_ID = 0x00
JD_XI_ID = 0x0E
DT1_COMMAND_12 = 0x12
RQ1_COMMAND_11 = 0x11
END_OF_SYSEX = 0xF7

# Common
SUBGROUP_ZERO = 0x00

# Synth areas
DIGITAL_SYNTH_AREA = 0x19
ANALOG_SYNTH_AREA = 0x17
DRUM_KIT_AREA = 0x1A
EFFECTS_AREA = 0x18

# Part numbers
PART_1 = 0x01

# Parameter groups
OSC_PARAM_GROUP = 0x20
LFO_PARAM_GROUP = 0x15

# Waveform types
class Waveform:
    SAW = 0x00
    SQUARE = 0x01
    PULSE = 0x02
    TRIANGLE = 0x03
    SINE = 0x04
    NOISE = 0x05
    SUPER_SAW = 0x06
    PCM = 0x07

# Drum parameters
class DrumPad:
    PARAM_OFFSET = 0x10  # Each pad has 16 parameters
    LEVEL = 0x00
    PAN = 0x01
    PITCH = 0x02
    DECAY = 0x03

# Effects areas
class Effect:
    EFFECT1 = 0x00
    EFFECT2 = 0x01
    REVERB = 0x02
    DELAY = 0x03
    CHORUS = 0x04
    MASTER = 0x05

    # Power addresses
    REVERB_POWER = 0x08
    DELAY_POWER = 0x09
    CHORUS_POWER = 0x0A

    # Parameter offsets
    LEVEL = 0x00
    PARAM1 = 0x01
    PARAM2 = 0x02

    # Effect types
    THRU = 0x00
    DISTORTION = 0x01
    FUZZ = 0x02
    COMPRESSOR = 0x03
    BITCRUSHER = 0x04 

# Add enums for the different effect types
class EffectType:
    THRU = 0x00
    DISTORTION = 0x01
    FUZZ = 0x02
    COMPRESSOR = 0x03
    BITCRUSHER = 0x04
    FLANGER = 0x05
    PHASER = 0x06
    RING_MOD = 0x07
    SLICER = 0x08

# Add enums for reverb types
class ReverbType:
    ROOM1 = 0x00
    ROOM2 = 0x01
    STAGE1 = 0x02
    STAGE2 = 0x03
    HALL1 = 0x04
    HALL2 = 0x05 

# Add sync note values
class SyncNote:
    N_16 = 0x00
    N_12 = 0x01
    N_8 = 0x02
    N_4 = 0x03
    N_2 = 0x04
    N_1 = 0x05
    N_3_4 = 0x06
    N_2_3 = 0x07
    N_1_2 = 0x08
    N_3_8 = 0x09
    N_1_3 = 0x0A
    N_1_4 = 0x0B
    N_3_16 = 0x0C
    N_1_6 = 0x0D
    N_1_8 = 0x0E
    N_3_32 = 0x0F
    N_1_12 = 0x10
    N_1_16 = 0x11
    N_1_24 = 0x12
    N_1_32 = 0x13

# Add arpeggio grid values
class ArpeggioGrid:
    QUARTER = 0x00      # "1/4"
    EIGHTH = 0x01       # "1/8"
    EIGHTH_L = 0x02     # "1/8 L"
    EIGHTH_H = 0x03     # "1/8 H"
    TWELFTH = 0x04      # "1/12"
    SIXTEENTH = 0x05    # "1/16"
    SIXTEENTH_L = 0x06  # "1/16 L"
    SIXTEENTH_H = 0x07  # "1/16 H"
    TWENTY_FOURTH = 0x08 # "1/24"

# Add arpeggio duration values
class ArpeggioDuration:
    D_30 = 0x00  # "30%"
    D_40 = 0x01  # "40%"
    D_50 = 0x02  # "50%"
    D_60 = 0x03  # "60%"
    D_70 = 0x04  # "70%"
    D_80 = 0x05  # "80%"
    D_90 = 0x06  # "90%"
    D_100 = 0x07 # "100%"
    D_120 = 0x08 # "120%"
    FULL = 0x09  # "Full" 

# Add tone categories
class ToneCategory:
    NOT_ASSIGNED = 0x00
    KEYBOARD = 0x09
    BASS = 0x21
    LEAD = 0x34
    BRASS = 0x35
    STRINGS_PAD = 0x36
    FX_OTHER = 0x39
    SEQ = 0x40

# Add mute group values
class MuteGroup:
    OFF = 0x00
    # Groups 1-31
    GROUPS = range(1, 32)

# Add high frequency damping values
class HFDamp:
    HZ_200 = 0x00
    HZ_250 = 0x01
    HZ_315 = 0x02
    HZ_400 = 0x03
    HZ_500 = 0x04
    HZ_630 = 0x05
    HZ_800 = 0x06
    HZ_1000 = 0x07
    HZ_1250 = 0x08
    HZ_1600 = 0x09
    HZ_2000 = 0x0A
    HZ_2500 = 0x0B
    HZ_3150 = 0x0C
    HZ_4000 = 0x0D
    HZ_5000 = 0x0E
    HZ_6300 = 0x0F
    HZ_8000 = 0x10
    BYPASS = 0x11

# Add compressor ratio values
class CompressorRatio:
    R_1_1 = 0x00   # "1:1"
    R_2_1 = 0x01   # "2:1"
    R_3_1 = 0x02   # "3:1"
    R_4_1 = 0x03   # "4:1"
    R_5_1 = 0x04   # "5:1"
    R_6_1 = 0x05   # "6:1"
    R_7_1 = 0x06   # "7:1"
    R_8_1 = 0x07   # "8:1"
    R_9_1 = 0x08   # "9:1"
    R_10_1 = 0x09  # "10:1"
    R_20_1 = 0x0A  # "20:1"
    R_30_1 = 0x0B  # "30:1"
    R_40_1 = 0x0C  # "40:1"
    R_50_1 = 0x0D  # "50:1"
    R_60_1 = 0x0E  # "60:1"
    R_70_1 = 0x0F  # "70:1"
    R_80_1 = 0x10  # "80:1"
    R_90_1 = 0x11  # "90:1"
    R_100_1 = 0x12 # "100:1"
    R_INF = 0x13   # "inf:1"

# Add compressor attack/release times
class CompressorTime:
    # Attack times in ms
    ATTACK_TIMES = [
        0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.20, 0.30,
        0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.0, 2.0,
        3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 15.0,
        20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0
    ]
    
    # Release times in ms
    RELEASE_TIMES = [
        0.05, 0.07, 0.10, 0.50, 1, 5, 10, 17, 25, 50,
        75, 100, 200, 300, 400, 500, 600, 700, 800,
        900, 1000, 1200, 1500, 2000
    ]

# Add arpeggio motif types
class ArpeggioMotif:
    UP_L = 0x00      # "Up (L)"
    UP_LH = 0x01     # "Up (L&H)"
    UP_UNDER = 0x02  # "Up (_)"
    DOWN_L = 0x03    # "Down (L)"
    DOWN_LH = 0x04   # "Down (L&H)"
    DOWN_UNDER = 0x05  # "Down (_)"
    UPDOWN_L = 0x06  # "Up/Down (L)"
    UPDOWN_LH = 0x07 # "Up/Down (L&H)"
    UPDOWN_UNDER = 0x08  # "Up/Down (_)"
    RANDOM_L = 0x09  # "Random (L)"
    RANDOM_UNDER = 0x0A  # "Random (_)"
    PHRASE = 0x0B    # "Phrase"

# Add voice cutoff filter values
class VoiceCutoffFilter:
    BYPASS = 0x00
    HZ_1000 = 0x01
    HZ_1250 = 0x02
    HZ_1600 = 0x03
    HZ_2000 = 0x04
    HZ_2500 = 0x05
    HZ_3150 = 0x06
    HZ_4000 = 0x07
    HZ_5000 = 0x08
    HZ_6300 = 0x09
    HZ_8000 = 0x0A
    HZ_10000 = 0x0B
    HZ_12500 = 0x0C
    HZ_16000 = 0x0D 

# PCM Wave constants
class PCMWave:
    OFF = 0x000  # "--- OFF ---"
    
    # Synth waves
    CALC_SAW = 0x001
    DIST_SAW = 0x002
    GR300_SAW = 0x003
    LEAD_WAVE1 = 0x004
    LEAD_WAVE2 = 0x005
    UNISON_SAW = 0x006
    SAW_SUB = 0x007
    SQR_LEAD = 0x008
    SQR_LEAD_PLUS = 0x009
    FEEDBACK = 0x00A
    BAD_AXE = 0x00B
    CUTTING_LEAD = 0x00C
    DIST_TB_SQR = 0x00D
    SYNC_SWEEP = 0x00E
    SAW_SYNC = 0x00F
    
    # Bass waves
    UNISON_SYNC = 0x010
    SYNC_WAVE = 0x011
    CUTTERS = 0x012
    NASTY = 0x013
    BAGPIPE = 0x014
    WAVE_SCAN = 0x015
    WIRE_STRING = 0x016
    LEAD_WAVE3 = 0x017
    PWM_WAVE1 = 0x018
    PWM_WAVE2 = 0x019
    MIDI_CLAV = 0x01A
    HUGE_MIDI = 0x01B
    WOBBLE_BS1 = 0x01C
    WOBBLE_BS2 = 0x01D
    HOLLOW_BASS = 0x01E
    
    # Bell waves
    SYNTH_BASS = 0x01F
    SOLID_BASS = 0x020
    HOUSE_BASS = 0x021
    FM_BASS = 0x022
    FINE_WINE = 0x023
    BELL_WAVE1 = 0x024
    BELL_WAVE1_PLUS = 0x025
    BELL_WAVE2 = 0x026
    
    # Digital waves
    DIGI_WAVE1 = 0x027
    DIGI_WAVE2 = 0x028
    ORG_BELL = 0x029
    GAMELAN = 0x02A
    CRYSTAL = 0x02B
    FINGER_BELL = 0x02C
    
    # Voice waves
    DIPTHONG = 0x02D
    DIPTHONG_PLUS = 0x02E
    HOLLOW_WAVE1 = 0x02F
    HOLLOW_WAVE2 = 0x030
    HOLLOW_WAVE2_PLUS = 0x031
    HEAVEN = 0x032
    DOO = 0x033
    MMM_VOX = 0x034
    EEH_FORMANT = 0x035
    IIH_FORMANT = 0x036
    
    # More voice waves
    SYN_VOX1 = 0x037
    SYN_VOX2 = 0x038
    ORG_VOX = 0x039
    MALE_OOH = 0x03A
    LARGE_CHR1 = 0x03B
    LARGE_CHR2 = 0x03C
    FEMALE_OOH = 0x03D
    FEMALE_AAH = 0x03E
    ATMOSPHERIC = 0x03F

# Drum Wave constants
class DrumWave:
    OFF = 0x000  # "--- OFF ---"
    
    # Kick drums
    CR78_KICK = 0x001
    TR606_KICK = 0x002
    TR808_KICK1A = 0x003
    TR808_KICK1B = 0x004
    TR808_KICK1C = 0x005
    TR808_KICK2A = 0x006
    TR808_KICK2B = 0x007
    TR808_KICK2C = 0x008
    TR808_KICK3A = 0x009
    TR808_KICK3B = 0x00A
    TR808_KICK3C = 0x00B
    TR808_KICK4A = 0x00C
    TR808_KICK4B = 0x00D
    TR808_KICK4C = 0x00E
    TR808_KICK1_LP = 0x00F
    TR808_KICK2_LP = 0x010
    
    # Snare drums
    TR909_SNARE1A = 0x065
    TR909_SNARE1B = 0x066
    TR909_SNARE1C = 0x067
    TR909_SNARE1D = 0x068
    TR909_SNARE2A = 0x069
    TR909_SNARE2B = 0x06A
    TR909_SNARE2C = 0x06B
    TR909_SNARE2D = 0x06C
    TR909_SNARE3A = 0x06D
    TR909_SNARE3B = 0x06E
    TR909_SNARE3C = 0x06F
    TR909_SNARE3D = 0x070
    
    # Hi-hats
    TR808_CHH = 0x0D8
    TR909_CHH1 = 0x0D9
    TR909_CHH2 = 0x0DA
    TR909_CHH3 = 0x0DB
    TR909_CHH4 = 0x0DC
    TR707_CHH = 0x0DD
    TR626_CHH = 0x0DE
    
    # Cymbals
    TR909_CRASH = 0x100
    TR909_RIDE = 0x109
    TR707_CRASH = 0x103
    TR626_CRASH = 0x104
    CRASH_CYM1 = 0x105
    CRASH_CYM2 = 0x106
    
    # Percussion
    TR808_CLAP = 0x116
    TR909_CLAP1 = 0x11A
    TR909_CLAP2 = 0x11B
    TR909_CLAP3 = 0x11C
    TR707_CLAP = 0x11E
    TR626_CLAP = 0x11F
    
    # Effects
    WHITE_NOISE = 0x1A8
    PINK_NOISE = 0x1A9
    ATMOSPHERE = 0x1AA
    PERC_ORGAN1 = 0x1AB
    PERC_ORGAN2 = 0x1AC
    TB_BLIP = 0x1AD
    FLUTE_FX = 0x1AF
    STRINGS_HIT = 0x1B1
    SMEAR_HIT = 0x1B2
    ORCH_HIT = 0x1B4
    PUNCH_HIT = 0x1B5
    PHILLY_HIT = 0x1B6
    TAO_HIT = 0x1B8 

# Note names and octaves
class Note:
    NOTES = ['C ', 'C#', 'D ', 'Eb', 'E ', 'F ', 'F#', 'G ', 'G#', 'A ', 'Bb', 'B ']
    
    @staticmethod
    def get_note_name(value: int) -> str:
        """Convert MIDI note number to note name with octave
        
        Args:
            value: MIDI note number (0-127)
            
        Returns:
            Note name with octave (e.g. 'C 4', 'F#3')
        """
        if 0 <= value < 128:
            octave = (value // 12) - 1
            note = Note.NOTES[value % 12]
            return f"{note}{octave}"
        return ""

# Envelope section labels
class EnvelopeSection:
    PITCH = "PITCH ENV"
    TVF = "TVF ENV"  # Time Variant Filter
    TVA = "TVA ENV"  # Time Variant Amplifier

# Random pitch depth values (in cents)
class RandomPitchDepth:
    VALUES = [
        0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
        20, 30, 40, 50, 60, 70, 80, 90, 100,
        200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200
    ]

# Arpeggio key values
class ArpeggioKey:
    # Major keys
    C = 0x00
    DB = 0x01
    D = 0x02
    EB = 0x03
    E = 0x04
    F = 0x05
    FS = 0x06
    G = 0x07
    AB = 0x08
    A = 0x09
    BB = 0x0A
    B = 0x0B
    
    # Minor keys
    CM = 0x0C
    CSM = 0x0D
    DM = 0x0E
    DSM = 0x0F
    EM = 0x10
    FM = 0x11
    FSM = 0x12
    GM = 0x13
    GSM = 0x14
    AM = 0x15
    BBM = 0x16
    BM = 0x17

# Preset categories
class PresetCategory:
    # Digital synth presets
    STRINGS = [
        "JP8 Strings1", "Soft Pad 1", "JP8 Strings2", "JUNO Str 1",
        "Oct Strings", "Brite Str 1", "Boreal Pad", "JP8 Strings3"
    ]
    
    PADS = [
        "Hollow Pad 1", "LFO Pad 1", "Hybrid Str", "Awakening 1",
        "Cincosoft 1", "Bright Pad 1", "Analog Str 1", "Soft ResoPd1"
    ]
    
    BASS = [
        "Seq Bass 1", "Reso Bass 1", "TB Bass 1", "106 Bass 1",
        "FilterEnvBs1", "JUNO Sqr Bs1", "Reso Bass 2", "JUNO Bass"
    ]
    
    LEAD = [
        "PortaSaw Ld1", "Porta Lead 1", "Analog Tp 1", "Tri Lead 1",
        "Sine Lead 1", "Saw Buzz 1", "Buzz Saw Ld1", "Laser Lead 1"
    ]

    # Drum kit presets
    DRUM_KITS = [
        "TR-909 Kit 1", "TR-808 Kit 1", "707&727 Kit1", "CR-78 Kit 1",
        "TR-606 Kit 1", "TR-626 Kit 1", "EDM Kit 1", "Drum&Bs Kit1"
    ]

# Delay note values (in musical notation)
class DelayNote:
    VALUES = [
        "1/96", "1/64", "1/48", "1/32", "1/24", "3/64", "1/16", "1/12",
        "3/32", "1/8", "1/6", "3/16", "1/4", "1/3", "3/8", "1/2",
        "2/3", "3/4", "1", "4/3", "3/2", "2"
    ] 

# Add DRUM_PARTS to constants.py
DRUM_PARTS = {
    'kicks': [
        # TR-909 kicks
        "TR-909 Kick 1", "TR-909 Kick 2", "TR-909 Kick 3",
        "TR-909 Kick Long", "TR-909 Kick Short", "TR-909 Kick Attack",
        # TR-808 kicks
        "TR-808 Kick 1", "TR-808 Kick 2", "TR-808 Kick 3",
        "TR-808 Kick Long", "TR-808 Kick Short", "TR-808 Kick Sub",
        # TR-707/727 kicks
        "TR-707 Kick", "TR-707 Kick Long", "TR-707 Kick Short",
        "TR-727 Kick", "TR-727 Kick Long", "TR-727 Kick Short",
        # Other kicks
        "TR-606 Kick", "TR-626 Kick", "CR-78 Kick", "CR-78 Kick Long",
        # Modern kicks
        "House Kick 1", "House Kick 2", "Techno Kick 1", "Techno Kick 2",
        "EDM Kick 1", "EDM Kick 2", "Hip Hop Kick 1", "Hip Hop Kick 2"
    ],
    'snares': [
        # TR-909 snares
        "TR-909 Snare 1", "TR-909 Snare 2", "TR-909 Snare 3",
        "TR-909 Snare Rim", "TR-909 Snare Roll", "TR-909 Snare Tight",
        # TR-808 snares
        "TR-808 Snare 1", "TR-808 Snare 2", "TR-808 Snare 3",
        "TR-808 Snare Rim", "TR-808 Snare Long", "TR-808 Snare Tight",
        # TR-707/727 snares
        "TR-707 Snare", "TR-707 Snare Rim", "TR-707 Snare Roll",
        "TR-727 Snare", "TR-727 Snare Rim", "TR-727 Snare Roll",
        # Other snares
        "TR-606 Snare", "TR-626 Snare", "CR-78 Snare", "CR-78 Snare Rim",
        # Modern snares
        "House Snare 1", "House Snare 2", "Techno Snare 1", "Techno Snare 2",
        "EDM Snare 1", "EDM Snare 2", "Hip Hop Snare 1", "Hip Hop Snare 2"
    ],
    'hihats': [
        # TR-909 hihats
        "TR-909 HiHat Closed", "TR-909 HiHat Open",
        "TR-909 HiHat Half", "TR-909 HiHat Foot",
        "TR-909 HiHat Loose", "TR-909 HiHat Tight",
        # TR-808 hihats
        "TR-808 HiHat Closed", "TR-808 HiHat Open",
        "TR-808 HiHat Half", "TR-808 HiHat Foot",
        "TR-808 HiHat Loose", "TR-808 HiHat Tight",
        # TR-707/727 hihats
        "TR-707 HiHat Closed", "TR-707 HiHat Open", "TR-707 HiHat Half",
        "TR-727 HiHat Closed", "TR-727 HiHat Open", "TR-727 HiHat Half",
        # Other hihats
        "TR-606 HiHat Closed", "TR-606 HiHat Open",
        "CR-78 HiHat Closed", "CR-78 HiHat Open",
        # Modern hihats
        "House HiHat 1", "House HiHat 2", "Techno HiHat 1", "Techno HiHat 2"
    ],
    'cymbals': [
        # TR-909 cymbals
        "TR-909 Crash", "TR-909 Crash Long", "TR-909 Crash Short",
        "TR-909 Ride", "TR-909 Ride Bell", "TR-909 Ride Edge",
        # TR-808 cymbals
        "TR-808 Crash", "TR-808 Crash Long", "TR-808 Crash Short",
        "TR-808 Ride", "TR-808 Ride Bell", "TR-808 Ride Edge",
        # Other cymbals
        "TR-707 Crash", "TR-707 Ride", "TR-707 Ride Bell",
        "TR-626 Crash", "TR-626 Ride", "TR-626 Ride Bell",
        # Modern cymbals
        "House Crash", "House Ride", "Techno Crash", "Techno Ride",
        "EDM Crash", "EDM Ride", "Hip Hop Crash", "Hip Hop Ride"
    ],
    'toms': [
        # TR-909 toms
        "TR-909 Tom Low", "TR-909 Tom Mid", "TR-909 Tom High",
        "TR-909 Tom Floor", "TR-909 Tom Rim",
        # TR-808 toms
        "TR-808 Tom Low", "TR-808 Tom Mid", "TR-808 Tom High",
        "TR-808 Tom Floor", "TR-808 Tom Rim",
        # Other toms
        "TR-707 Tom Low", "TR-707 Tom Mid", "TR-707 Tom High",
        "TR-727 Tom Low", "TR-727 Tom Mid", "TR-727 Tom High",
        "TR-606 Tom Low", "TR-606 Tom High",
        # Modern toms
        "House Tom Low", "House Tom Mid", "House Tom High",
        "EDM Tom Low", "EDM Tom Mid", "EDM Tom High"
    ],
    'percussion': [
        # TR-909 percussion
        "TR-909 Clap", "TR-909 Rim", "TR-909 Maracas",
        "TR-909 Hand Clap", "TR-909 Tambourine",
        # TR-808 percussion
        "TR-808 Clap", "TR-808 Cowbell", "TR-808 Clave",
        "TR-808 Maracas", "TR-808 Conga High", "TR-808 Conga Mid",
        "TR-808 Conga Low", "TR-808 Timbale",
        # TR-707/727 percussion
        "TR-707 Clap", "TR-707 Tambourine", "TR-707 Cowbell",
        "TR-727 Agogo", "TR-727 Bongo High", "TR-727 Bongo Low",
        "TR-727 Whistle", "TR-727 Cabasa",
        # Latin percussion
        "Conga Open", "Conga Mute", "Conga Slap",
        "Bongo High", "Bongo Low", "Timbale High", "Timbale Low",
        "Agogo High", "Agogo Low", "Cabasa", "Maracas",
        "Guiro Short", "Guiro Long", "Claves", "Wood Block",
        # Modern percussion
        "House Clap", "House Snap", "House Tambourine",
        "Techno Clap", "Techno Perc", "Techno Noise",
        "EDM Clap", "EDM Snap", "EDM Impact",
        "Hip Hop Clap", "Hip Hop Snap", "Hip Hop Perc"
    ],
    'fx': [
        # Noise FX
        "White Noise Short", "White Noise Long",
        "Pink Noise Short", "Pink Noise Long",
        "Noise Sweep Up", "Noise Sweep Down",
        # Impact FX
        "Impact Hit", "Impact Boom", "Impact Crash",
        "Metal Hit", "Wood Hit", "Glass Hit",
        # Synth FX
        "Zap", "Laser", "Blip", "Bleep",
        "Synth Rise", "Synth Fall", "Synth Sweep",
        # Reverse FX
        "Reverse Cymbal", "Reverse Snare", "Reverse Clap",
        "Reverse Noise", "Reverse Impact", "Reverse Sweep",
        # Modern FX
        "EDM Rise", "EDM Fall", "EDM Impact",
        "House Noise", "House Rise", "House Fall",
        "Techno Noise", "Techno Rise", "Techno Fall"
    ]
} 

# Add these new instrument-related constants

# Digital Synth Oscillator Types
class DigitalOscType:
    SUPER_SAW = 0x00
    SUPER_SQUARE = 0x01
    SUPER_TRIANGLE = 0x02
    SUPER_SINE = 0x03
    NOISE = 0x04
    PCM_SYNTH = 0x05
    PCM_DRUM = 0x06
    EXTERNAL = 0x07

# Filter Types
class FilterType:
    LPF = 0x00    # Low Pass Filter
    HPF = 0x01    # High Pass Filter
    BPF = 0x02    # Band Pass Filter
    PKG = 0x03    # Peaking Filter
    OFF = 0x04    # Filter Off

# LFO Shapes
class LFOShape:
    TRIANGLE = 0x00
    SINE = 0x01
    SAWTOOTH = 0x02
    SQUARE = 0x03
    SAMPLE_HOLD = 0x04
    RANDOM = 0x05

# Modulation Destinations
class ModDest:
    PITCH = 0x00
    FILTER = 0x01
    AMP = 0x02
    PAN = 0x03
    LFO_RATE = 0x04
    LFO_DEPTH = 0x05

# PCM Categories (expand existing PCMWave)
class PCMCategory:
    SYNTH_LEAD = 0x00
    BASS = 0x01
    KEYBOARD = 0x02
    BELL = 0x03
    MALLET = 0x04
    PLUCKED = 0x05
    STRINGS = 0x06
    BRASS = 0x07
    WIND = 0x08
    VOX = 0x09
    PERCUSSION = 0x0A
    SOUND_FX = 0x0B
    DRUMS = 0x0C

# Drum Categories (expand existing DrumWave)
class DrumCategory:
    KICK = 0x00
    SNARE = 0x01
    HIHAT = 0x02
    CYMBAL = 0x03
    TOM = 0x04
    PERCUSSION = 0x05
    CLAP = 0x06
    FX = 0x07
    
    # Subcategories
    TR909 = 0x10
    TR808 = 0x11
    TR707 = 0x12
    TR727 = 0x13
    TR606 = 0x14
    CR78 = 0x15
    ACOUSTIC = 0x16
    ELECTRONIC = 0x17
    MODERN = 0x18

# Voice Modes
class VoiceMode:
    MONO = 0x00
    POLY = 0x01
    UNISON = 0x02
    LEGATO = 0x03

# Portamento Modes
class PortamentoMode:
    OFF = 0x00
    ON = 0x01
    AUTO = 0x02
    LEGATO = 0x03

# Key Ranges
class KeyRange:
    FULL = (0, 127)
    BASS = (24, 48)    # C1 to C3
    MID = (48, 72)     # C3 to C5
    HIGH = (72, 96)    # C5 to C7
    SPLIT_LOWER = (0, 60)   # Bottom to middle C
    SPLIT_UPPER = (60, 127) # Middle C to top 

# Add MIDI CC mappings

class MIDIMap:
    """MIDI Control Change (CC) mappings for the Roland JD-Xi
    
    Each CC number (0-127) controls a specific parameter. Values are also 0-127 unless noted.
    Some parameters use two CCs for fine control (MSB/LSB).
    
    MIDI Channel Assignments:
        Channel 1:  Digital Synth 1 (Program 1-128)
        Channel 2:  Digital Synth 2 (Program 1-128)
        Channel 3:  Analog Synth (Program 1-8)
        Channel 4:  External Input
        Channel 5:  Reserved
        Channel 6:  Reserved
        Channel 7:  Reserved
        Channel 8:  Reserved
        Channel 9:  Reserved
        Channel 10: Drums (Program 1-32)
        Channel 11: Reserved
        Channel 12: Reserved
        Channel 13: Reserved
        Channel 14: Reserved
        Channel 15: Reserved
        Channel 16: System/Global
        
    Channel Modes:
        - Each channel can be set to OMNI (receive all) or specific channel
        - Channels can be set to POLY or MONO mode
        - Local control can be enabled/disabled per channel
        
    Program Changes:
        Digital 1 & 2: Programs 1-128 select digital patches
        Analog: Programs 1-8 select analog patches
        Drums: Programs 1-32 select drum kits
        
    Bank Select:
        MSB (CC 0) and LSB (CC 32) can be used to access additional banks
        Digital: Bank 0-7 available
        Analog: Bank 0 only
        Drums: Bank 0-1 available
        
    Troubleshooting MIDI Communication:
        
        Common Issues:
        1. No MIDI Input/Output
           - Check USB/MIDI cable connections
           - Verify JD-Xi is in USB/MIDI mode (SHIFT + USB)
           - Confirm correct MIDI ports selected in software
           - Check MIDI channel assignments match
        
        2. Wrong Sounds/Parameters
           - Verify correct MIDI channel for target part
           - Check if Bank Select was sent before Program Change
           - Ensure parameter values are within valid ranges
           - Confirm MIDI message formatting is correct
        
        3. SysEx Issues
           - Enable SysEx in software MIDI settings
           - Check device ID matches (default: 0x10)
           - Verify checksum calculation
           - Allow sufficient time between SysEx messages
        
        4. NRPN Issues
           - Send all 4 messages in correct sequence
           - Match NRPN channel to target part
           - Verify MSB/LSB values are correct
           - Wait for processing between messages
        
        Debug Tips:
        - Use MIDI monitor software to verify messages
        - Check JD-Xi display for received messages
        - Send ALL_NOTES_OFF (CC 123) to reset stuck notes
        - Use RESET_ALL_CTRL (CC 121) to reset parameters
        - Try LOCAL_CONTROL OFF/ON to reset MIDI state
        
        Message Timing:
        - Allow 10ms between regular CC messages
        - Wait 50ms after Program Changes
        - Allow 100ms between SysEx messages
        - Maximum 1000 messages per second
        
        Valid Ranges:
        - CC values: 0-127
        - Program numbers: 1-128 (sent as 0-127)
        - Bank MSB: 0-7 (Digital), 0 (Analog/Drums)
        - Bank LSB: 0 (all parts)
        - SysEx messages: max 512 bytes
        
        Error Recovery:
        1. Send ALL_SOUND_OFF (CC 120)
        2. Send RESET_ALL_CTRL (CC 121)
        3. Send ALL_NOTES_OFF (CC 123)
        4. Send Program Change to reset patch
        5. If needed, power cycle JD-Xi
    """
    
    # Common MIDI CCs (0-127 unless noted)
    MODULATION = 0x01    # Modulation wheel (all channels)
    BREATH = 0x02        # Breath controller (all channels)
    VOLUME = 0x07        # Channel volume (all channels)
    PAN = 0x0A          # Pan position (-64 to +63, all channels)
    EXPRESSION = 0x0B    # Expression pedal (all channels)
    
    # Bank/Program Control
    BANK_SELECT_MSB = 0x00  # Bank select MSB (all channels)
    BANK_SELECT_LSB = 0x20  # Bank select LSB (all channels)
    
    # Channel Mode Messages
    ALL_SOUND_OFF = 0x78    # All sound off (immediate)
    RESET_ALL_CTRL = 0x79   # Reset all controllers
    LOCAL_CONTROL = 0x7A    # Local control on/off
    ALL_NOTES_OFF = 0x7B    # All notes off
    OMNI_OFF = 0x7C         # Omni mode off
    OMNI_ON = 0x7D         # Omni mode on
    MONO_ON = 0x7E         # Mono mode on
    POLY_ON = 0x7F         # Poly mode on

    class Digital:
        """Digital Synth CC Parameters
        
        Send on Channel 1 (Digital 1) or Channel 2 (Digital 2)
        Program Changes: 1-128
        Bank Select: MSB 0-7, LSB 0
        All values 0-127 unless noted
        """
        # ... rest of Digital class ...

    class Analog:
        """Analog Synth CC Parameters
        
        Send on Channel 3
        Program Changes: 1-8
        Bank Select: MSB 0, LSB 0
        All values 0-127 unless noted
        """
        # ... rest of Analog class ...

    class Drums:
        """Drum Kit CC Parameters
        
        Send on Channel 10
        Program Changes: 1-32
        Bank Select: MSB 0-1, LSB 0
        All values 0-127 unless noted
        Parameters affect currently selected drum pad
        
        Note Assignments:
            35-51: Standard GM Drum Map
            52-87: Extended Drum Sounds
            88-98: Percussion Sounds
        """
        # ... rest of Drums class ...

    class System:
        """System-wide CC Parameters
        
        Send on Channel 16
        No Program Changes
        All values 0-127 unless noted
        Affects entire synth globally
        
        System Exclusive Messages:
            Identity Request: F0 7E 10 06 01 F7
            Identity Reply: F0 7E 10 06 02 41 64 02 00 00 00 00 00 F7
            
        Bulk Dump Request:
            Digital: F0 41 10 00 00 64 11 10 00 00 00 00 xx F7
            Analog:  F0 41 10 00 00 64 11 20 00 00 00 00 xx F7
            Drums:   F0 41 10 00 00 64 11 30 00 00 00 00 xx F7
            Where xx is checksum
        """
        # ... rest of System class ...

    class NRPN:
        """Non-Registered Parameter Numbers
        
        Send on same channel as target part:
            Digital 1: Channel 1
            Digital 2: Channel 2
            Analog: Channel 3
            Drums: Channel 10
            
        Message Sequence:
            1. NRPN MSB (CC 99)
            2. NRPN LSB (CC 98)
            3. Data Entry MSB (CC 6)
            4. Data Entry LSB (CC 38)
            
        Example:
            To set Digital OSC1 wave on channel 1:
            CC 99 0    # NRPN MSB
            CC 98 0    # NRPN LSB
            CC 6  val  # Data MSB
            CC 38 0    # Data LSB
        """
        # ... rest of NRPN class ... 

# Digital Synth Partial Controls
class DigitalPartial:
    """Digital Synth Partial Parameters
    
    Each Digital Synth has 3 partials (1-3) that can be layered.
    Each partial has its own oscillator, filter, amp and envelope settings.
    
    Partial Structure:
        SINGLE: Only Partial 1 active
        LAYER: Multiple partials layered
        SPLIT: Partials split across keyboard range
    """
    
    # Partial Structure Types
    class Structure:
        SINGLE = 0x00      # Only Partial 1
        LAYER_1_2 = 0x01   # Layer Partial 1 & 2
        LAYER_2_3 = 0x02   # Layer Partial 2 & 3
        LAYER_1_3 = 0x03   # Layer Partial 1 & 3
        LAYER_ALL = 0x04   # Layer all Partials
        SPLIT_1_2 = 0x05   # Split between 1 & 2
        SPLIT_2_3 = 0x06   # Split between 2 & 3
        SPLIT_1_3 = 0x07   # Split between 1 & 3
    
    # Parameter offsets for each partial
    class Offset:
        PARTIAL_1 = 0x00
        PARTIAL_2 = 0x20
        PARTIAL_3 = 0x40
    
    # Common parameters per partial
    class Params:
        # Oscillator
        OSC_WAVE = 0x00    # Oscillator waveform
        OSC_PITCH = 0x01   # Coarse pitch (-24 to +24 semitones)
        OSC_FINE = 0x02    # Fine tune (-50 to +50 cents)
        OSC_PWM = 0x03     # Pulse width (0-127)
        
        # Filter
        FILTER_TYPE = 0x04  # Filter type (see FilterType)
        FILTER_CUTOFF = 0x05  # Cutoff frequency (0-127)
        FILTER_RESO = 0x06    # Resonance (0-127)
        FILTER_ENV = 0x07     # Envelope depth (-64 to +63)
        FILTER_KEY = 0x08     # Key follow (0-127)
        
        # Amplifier
        AMP_LEVEL = 0x09    # Level (0-127)
        AMP_PAN = 0x0A      # Pan position (-64 to +63)
        
        # LFO
        LFO_WAVE = 0x0B     # LFO waveform (see LFOShape)
        LFO_RATE = 0x0C     # LFO speed (0-127)
        LFO_PITCH = 0x0D    # Pitch mod depth (0-127)
        LFO_FILTER = 0x0E   # Filter mod depth (0-127)
        LFO_AMP = 0x0F      # Amp mod depth (0-127)
        
        # Envelope
        ENV_ATTACK = 0x10   # Attack time (0-127)
        ENV_DECAY = 0x11    # Decay time (0-127)
        ENV_SUSTAIN = 0x12  # Sustain level (0-127)
        ENV_RELEASE = 0x13  # Release time (0-127)

    # MIDI CC mappings for partial parameters
    class CC:
        """CC numbers for partial parameters
        
        Usage:
            To control a parameter for a specific partial,
            add the partial offset to the CC number:
            
            Partial 1 OSC WAVE = 0x20
            Partial 2 OSC WAVE = 0x40
            Partial 3 OSC WAVE = 0x60
        """
        # Structure
        PARTIAL_SW = 0x14      # Partial on/off
        STRUCTURE = 0x15       # Partial structure
        SPLIT_POINT = 0x16     # Split point for split modes
        
        # Oscillator
        OSC_WAVE = 0x20
        OSC_PITCH = 0x21
        OSC_FINE = 0x22
        OSC_PWM = 0x23
        
        # Filter  
        FILTER_TYPE = 0x24
        FILTER_CUTOFF = 0x25
        FILTER_RESO = 0x26
        FILTER_ENV = 0x27
        FILTER_KEY = 0x28
        
        # Amplifier
        AMP_LEVEL = 0x29
        AMP_PAN = 0x2A
        
        # LFO
        LFO_WAVE = 0x2B
        LFO_RATE = 0x2C
        LFO_PITCH = 0x2D
        LFO_FILTER = 0x2E
        LFO_AMP = 0x2F
        
        # Envelope
        ENV_ATTACK = 0x30
        ENV_DECAY = 0x31
        ENV_SUSTAIN = 0x32
        ENV_RELEASE = 0x33

    # NRPN mappings for partial parameters
    class NRPN:
        """NRPN numbers for partial parameters that need higher resolution
        
        Returns tuple of (MSB, LSB) values
        Add partial offset to MSB for specific partial:
            Partial 1: 0x00
            Partial 2: 0x20  
            Partial 3: 0x40
        """
        OSC_WAVE = (0x00, 0x00)
        FILTER_TYPE = (0x00, 0x01)
        LFO_WAVE = (0x00, 0x02)
        STRUCTURE = (0x00, 0x03) 