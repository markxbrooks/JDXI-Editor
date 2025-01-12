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
RQ1_COMMAND_11 = 0x11  # Data Request 1

# Memory areas
DIGITAL_SYNTH_AREA = 0x19  # Base area for digital synths
DIGITAL_SYNTH_1 = 0x19     # Digital synth 1 area
DIGITAL_SYNTH_2 = 0x1A     # Digital synth 2 area
ANALOG_SYNTH_AREA = 0x18   # Analog synth area
DRUM_KIT_AREA = 0x17       # Drum kit area
EFFECTS_AREA = 0x16        # Effects area
ARPEGGIO_AREA = 0x15       # Arpeggiator area
VOCAL_FX_AREA = 0x14       # Vocal effects area
SYSTEM_AREA = 0x01         # System settings area

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

class FilterMode(Enum):
    """Filter modes available on JD-Xi"""
    BYPASS = 0x00
    LPF = 0x01    # Low Pass Filter
    HPF = 0x02    # High Pass Filter
    BPF = 0x03    # Band Pass Filter
    PKG = 0x04    # Peaking Filter
    LPF2 = 0x05   # Low Pass Filter 2
    LPF3 = 0x06   # Low Pass Filter 3
    LPF4 = 0x07   # Low Pass Filter 4

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
        OSC_WAVE = 0x00       # Wave (0-7: SAW, SQR, PW-SQR, TRI, SINE, NOISE, SUPER-SAW, PCM)
        OSC_VARIATION = 0x01  # Wave Variation (0-2: A, B, C)
        OSC_RESERVE = 0x02    # Reserved
        OSC_PITCH = 0x03      # Pitch (40-88: -24 to +24)
        OSC_DETUNE = 0x04     # Detune (14-114: -50 to +50)
        OSC_PWM_DEPTH = 0x05  # Pulse Width Mod Depth (0-127)
        OSC_PW = 0x06        # Pulse Width (0-127)
        OSC_PITCH_A = 0x07   # Pitch Env Attack Time (0-127)
        OSC_PITCH_D = 0x08   # Pitch Env Decay (0-127)
        OSC_PITCH_DEPTH = 0x09 # Pitch Env Depth (1-127)
        
        # Filter parameters (0x0A-0x14)
        FILTER_MODE = 0x0A     # Filter mode (0-7: BYPASS, LPF, HPF, BPF, PKG, LPF2, LPF3, LPF4)
        FILTER_SLOPE = 0x0B    # Filter slope (0-1: -12dB, -24dB)
        FILTER_CUTOFF = 0x0C   # Filter cutoff frequency (0-127)
        FILTER_KEYFOLLOW = 0x0D # Cutoff keyfollow (54-74: -100 to +100)
        FILTER_VELO = 0x0E     # Env velocity sensitivity (1-127: -63 to +63)
        FILTER_RESO = 0x0F     # Resonance (0-127)
        FILTER_ATTACK = 0x10   # Env attack time (0-127)
        FILTER_DECAY = 0x11    # Env decay time (0-127)
        FILTER_SUSTAIN = 0x12  # Env sustain level (0-127)
        FILTER_RELEASE = 0x13  # Env release time (0-127)
        FILTER_ENV_DEPTH = 0x14 # Env depth (1-127: -63 to +63)
        
        # Amplifier parameters (0x15-0x1B)
        AMP_LEVEL = 0x15      # Level (0-127)
        AMP_VELO = 0x16       # Level Velocity Sensitivity (1-127: -63 to +63)
        AMP_ATTACK = 0x17     # Env Attack Time (0-127)
        AMP_DECAY = 0x18      # Env Decay Time (0-127)
        AMP_SUSTAIN = 0x19    # Env Sustain Level (0-127)
        AMP_RELEASE = 0x1A    # Env Release Time (0-127)
        AMP_PAN = 0x1B        # Pan (0-127: L64-63R)
        
        # LFO parameters (0x1C-0x25)
        LFO_SHAPE = 0x1C      # LFO Shape (0-5: TRI, SIN, SAW, SQR, S&H, RND)
        LFO_RATE = 0x1D       # Rate (0-127)
        LFO_SYNC_SW = 0x1E    # Tempo Sync Switch (0-1: OFF, ON)
        LFO_SYNC_NOTE = 0x1F  # Tempo Sync Note (0-19: 16,12,8,4,2,1,3/4,...)
        LFO_FADE = 0x20       # Fade Time (0-127)
        LFO_KEY_TRIG = 0x21   # Key Trigger (0-1: OFF, ON)
        LFO_PITCH = 0x22      # Pitch Depth (1-127: -63 to +63)
        LFO_FILTER = 0x23     # Filter Depth (1-127: -63 to +63)
        LFO_AMP = 0x24        # Amp Depth (1-127: -63 to +63)
        LFO_PAN = 0x25        # Pan Depth (1-127: -63 to +63)
        
        # Envelope parameters (0x40-0x4F)
        ENV_ATTACK = 0x40     # Attack time
        ENV_DECAY = 0x41      # Decay time
        ENV_SUSTAIN = 0x42    # Sustain level
        ENV_RELEASE = 0x43    # Release time
        ENV_KEY = 0x44        # Key follow
        ENV_VELO = 0x45       # Velocity sensitivity
        
        # Oscillator parameters (0x34-0x3C)
        OSC_GAIN = 0x34       # Wave Gain (0-3: -6, 0, +6, +12 dB)
        OSC_WAVE_NUM = 0x35   # Wave Number (0-16384: OFF, 1-16384)
        HPF_CUTOFF = 0x39     # HPF Cutoff (0-127)
        SUPER_SAW = 0x3A      # Super Saw Detune (0-127)
        MOD_LFO_RATE = 0x3B   # Modulation LFO Rate Control (1-127: -63 to +63)
        AMP_KEYFOLLOW = 0x3C  # AMP Level Keyfollow (54-74: -100 to +100)
        
        # Aftertouch parameters (0x30-0x31)
        CUTOFF_AFTERTOUCH = 0x30  # Cutoff Aftertouch Sensitivity (1-127: -63 to +63)
        LEVEL_AFTERTOUCH = 0x31   # Level Aftertouch Sensitivity (1-127: -63 to +63)

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
    GRID_4 = 0     # 04_
    GRID_8 = 1     # 08_
    GRID_8L = 2    # 08L
    GRID_8H = 3    # 08H
    GRID_8T = 4    # 08t
    GRID_16 = 5    # 16_
    GRID_16L = 6   # 16L
    GRID_16H = 7   # 16H
    GRID_16T = 8   # 16t

class ArpDuration(Enum):
    """Arpeggio duration values"""
    DUR_30 = 0     # 30%
    DUR_40 = 1     # 40%
    DUR_50 = 2     # 50%
    DUR_60 = 3     # 60%
    DUR_70 = 4     # 70%
    DUR_80 = 5     # 80%
    DUR_90 = 6     # 90%
    DUR_100 = 7    # 100%
    DUR_120 = 8    # 120%
    DUR_FULL = 9   # FULL

class ArpMotif(Enum):
    """Arpeggio motif values"""
    UP_L = 0       # UP/L
    UP_H = 1       # UP/H
    UP_NORM = 2    # UP/_
    DOWN_L = 3     # dn/L
    DOWN_H = 4     # dn/H
    DOWN_NORM = 5  # dn/_
    UP_DOWN_L = 6  # Ud/L
    UP_DOWN_H = 7  # Ud/H
    UP_DOWN_NORM = 8  # Ud/_
    RANDOM_L = 9   # rn/L
    RANDOM_NORM = 10  # rn/_
    PHRASE = 11    # PHRASE

class ArpParameters(Enum):
    """Arpeggiator parameters"""
    GRID = 0x01        # Grid (0-8)
    DURATION = 0x02    # Duration (0-9)
    SWITCH = 0x03      # On/Off (0-1)
    STYLE = 0x05       # Style (0-127)
    MOTIF = 0x06       # Motif (0-11)
    OCTAVE = 0x07      # Octave Range (61-67: -3 to +3)
    ACCENT = 0x09      # Accent Rate (0-100)
    VELOCITY = 0x0A    # Velocity (0-127, 0=REAL)

# SuperNATURAL presets for each part
DIGITAL_SN_PRESETS = [
    '001: JP8 Strings1', '002: Soft Pad 1',   '003: JP8 Strings2', '004: JUNO Str 1',   '005: Oct Strings',  '006: Brite Str 1',  '007: Boreal Pad',
    '008: JP8 Strings3', '009: JP8 Strings4', '010: Hollow Pad 1', '011: LFO Pad 1',    '012: Hybrid Str',   '013: Awakening 1',  '014: Cincosoft 1',
    '015: Bright Pad 1', '016: Analog Str 1', '017: Soft ResoPd1', '018: HPF Poly 1',   '019: BPF Poly',     '020: Sweep Pad 1',  '021: Soft Pad 2',
    '022: Sweep JD 1',   '023: FltSweep Pd1', '024: HPF Pad',      '025: HPF SweepPd1', '026: KOff Pad',     '027: Sweep Pad 2',  '028: TrnsSweepPad',
    '029: Revalation 1', '030: LFO CarvePd1', '031: RETROX 139 1', '032: LFO ResoPad1', '033: PLS Pad 1',    '034: PLS Pad 2',    '035: Trip 2 Mars1',
    '036: Reso S&H Pd1', '037: SideChainPd1', '038: PXZoon 1',     '039: Psychoscilo1', '040: Fantasy 1',    '041: D-50 Stack 1', '042: Organ Pad',
    '043: Bell Pad',     '044: Dreaming 1',   '045: Syn Sniper 1', '046: Strings 1',    '047: D-50 Pizz 1',  '048: Super Saw 1',  '049: S-SawStacLd1',
    '050: Tekno Lead 1', '051: Tekno Lead 2', '052: Tekno Lead 3', '053: OSC-SyncLd 1', '054: WaveShapeLd1', '055: JD RingMod 1', '056: Buzz Lead 1',
    '057: Buzz Lead 2',  '058: SawBuzz Ld 1', '059: Sqr Buzz Ld1', '060: Tekno Lead 4', '061: Dist Flt TB1', '062: Dist TB Sqr1', '063: Glideator 1',
    '064: Vintager 1',   '065: Hover Lead 1', '066: Saw Lead 1',   '067: Saw+Tri Lead', '068: PortaSaw Ld1', '069: Reso Saw Ld',  '070: SawTrap Ld 1',
    '071: Fat GR Lead',  '072: Pulstar Ld',   '073: Slow Lead',    '074: AnaVox Lead',  '075: Square Ld 1',  '076: Square Ld 2',  '077: Sqr Lead 1',
    '078: Sqr Trap Ld1', '079: Sine Lead 1',  '080: Tri Lead',     '081: Tri Stac Ld1', '082: 5th SawLead1', '083: Sweet 5th 1',  '084: 4th Syn Lead',
    '085: Maj Stack Ld', '086: MinStack Ld1', '087: Chubby Lead1', '088: CuttingLead1', '089: Seq Bass 1',   '090: Reso Bass 1',  '091: TB Bass 1',
    '092: 106 Bass 1',   '093: FilterEnvBs1', '094: JUNO Sqr Bs1', '095: Reso Bass 2',  '096: JUNO Bass',    '097: MG Bass 1',    '098: 106 Bass 3',
    '099: Reso Bass 3',  '100: Detune Bs 1',  '101: MKS-50 Bass1', '102: Sweep Bass',   '103: MG Bass 2',    '104: MG Bass 3',    '105: ResRubber Bs',
    '106: R&B Bass 1',   '107: Reso Bass 4',  '108: Wide Bass 1',  '109: Chow Bass 1',  '110: Chow Bass 2',  '111: SqrFilterBs1', '112: Reso Bass 5',
    '113: Syn Bass 1',   '114: ResoSawSynBs', '115: Filter Bass1', '116: SeqFltEnvBs',  '117: DnB Bass 1',   '118: UnisonSynBs1', '119: Modular Bs',
    '120: Monster Bs 1', '121: Monster Bs 2', '122: Monster Bs 3', '123: Monster Bs 4', '124: Square Bs 1',  '125: 106 Bass 2',   '126: 5th Stac Bs1',
    '127: SqrStacSynBs', '128: MC-202 Bs',    '129: TB Bass 2',    '130: Square Bs 2',  '131: SH-101 Bs',    '132: R&B Bass 2',   '133: MG Bass 4',
    '134: Seq Bass 2',   '135: Tri Bass 1',   '136: BPF Syn Bs 2', '137: BPF Syn Bs 1', '138: Low Bass 1',   '139: Low Bass 2',   '140: Kick Bass 1',
    '141: SinDetuneBs1', '142: Organ Bass 1', '143: Growl Bass 1', '144: Talking Bs 1', '145: LFO Bass 1',   '146: LFO Bass 2',   '147: Crack Bass',
    '148: Wobble Bs 1',  '149: Wobble Bs 2',  '150: Wobble Bs 3',  '151: Wobble Bs 4',  '152: SideChainBs1', '153: SideChainBs2', '154: House Bass 1',
    '155: FM Bass',      '156: 4Op FM Bass1', '157: Ac. Bass',     '158: Fingerd Bs 1', '159: Picked Bass',  '160: Fretless Bs',  '161: Slap Bass 1',
    '162: JD Piano 1',   '163: E. Grand 1',   '164: Trem EP 1',    '165: FM E.Piano 1', '166: FM E.Piano 2', '167: Vib Wurly 1',  '168: Pulse Clav',
    '169: Clav',         '170: 70\'s E.Organ','171: House Org 1',  '172: House Org 2',  '173: Bell 1',       '174: Bell 2',       '175: Organ Bell',
    '176: Vibraphone 1', '177: Steel Drum',   '178: Harp 1',       '179: Ac. Guitar',   '180: Bright Strat', '181: Funk Guitar1', '182: Jazz Guitar',
    '183: Dist Guitar1', '184: D. Mute Gtr1', '185: E. Sitar',     '186: Sitar Drone',  '187: FX 1',         '188: FX 2',         '189: FX 3',
    '190: Tuned Winds1', '191: Bend Lead 1',  '192: RiSER 1',      '193: Rising SEQ 1', '194: Scream Saw',   '195: Noise SEQ 1',  '196: Syn Vox 1',
    '197: JD SoftVox',   '198: Vox Pad',      '199: VP-330 Chr',   '200: Orch Hit',     '201: Philly Hit',   '202: House Hit',    '203: O\'Skool Hit1',
    '204: Punch Hit',    '205: Tao Hit',      '206: SEQ Saw 1',    '207: SEQ Sqr',      '208: SEQ Tri 1',    '209: SEQ 1',        '210: SEQ 2',
    '211: SEQ 3',        '212: SEQ 4',        '213: Sqr Reso Plk', '214: Pluck Synth1', '215: Paperclip 1',  '216: Sonar Pluck1', '217: SqrTrapPlk 1',
    '218: TB Saw Seq 1', '219: TB Sqr Seq 1', '220: JUNO Key',     '221: Analog Poly1', '222: Analog Poly2', '223: Analog Poly3', '224: Analog Poly4',
    '225: JUNO Octavr1', '226: EDM Synth 1',  '227: Super Saw 2',  '228: S-Saw Poly',   '229: Trance Key 1', '230: S-Saw Pad 1',  '231: 7th Stac Syn',
    '232: S-SawStc Syn', '233: Trance Key 2', '234: Analog Brass', '235: Reso Brass',   '236: Soft Brass 1', '237: FM Brass',     '238: Syn Brass 1',
    '239: Syn Brass 2',  '240: JP8 Brass',    '241: Soft SynBrs1', '242: Soft SynBrs2', '243: EpicSlow Brs', '244: JUNO Brass',   '245: Poly Brass',
    '246: Voc:Ensemble', '247: Voc:5thStack', '248: Voc:Robot',    '249: Voc:Saw',      '250: Voc:Sqr',      '251: Voc:Rise Up',  '252: Voc:Auto Vib',
    '253: Voc:PitchEnv', '254: Voc:VP-330',   '255: Voc:Noise'
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
    "030: User Kit 4"
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
    NOTE_16 = 0     # 16 bars
    NOTE_12 = 1     # 12 bars
    NOTE_8 = 2      # 8 bars
    NOTE_4 = 3      # 4 bars
    NOTE_2 = 4      # 2 bars
    NOTE_1 = 5      # 1 bar
    NOTE_3_4 = 6    # 3/4
    NOTE_2_3 = 7    # 2/3
    NOTE_1_2 = 8    # 1/2
    NOTE_3_8 = 9    # 3/8
    NOTE_1_3 = 10   # 1/3
    NOTE_1_4 = 11   # 1/4
    NOTE_3_16 = 12  # 3/16
    NOTE_1_6 = 13   # 1/6
    NOTE_1_8 = 14   # 1/8
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
    OSC1_WAVE = 0x16        # OSC Waveform (0-2: SAW, TRI, PW-SQR)
    OSC1_PITCH = 0x17       # OSC Pitch Coarse (40-88: maps to -24 - +24)
    OSC1_FINE = 0x18        # OSC Pitch Fine (14-114: maps to -50 - +50)
    OSC1_PW = 0x19          # OSC Pulse Width (0-127)
    OSC1_PWM = 0x1A         # OSC Pulse Width Mod Depth (0-127)
    OSC_PITCH_VELO = 0x1B   # OSC Pitch Env Velocity Sens (1-127: maps to -63 - +63)
    OSC_PITCH_ATK = 0x1C    # OSC Pitch Env Attack Time (0-127)
    OSC_PITCH_DEC = 0x1D    # OSC Pitch Env Decay (0-127)
    OSC_PITCH_DEPTH = 0x1E  # OSC Pitch Env Depth (1-127: maps to -63 - +63)
    SUB_OSC_TYPE = 0x1F     # Sub Oscillator Type (0-2: OFF, OCT-1, OCT-2)

    @staticmethod
    def validate_value(param: int, value: int) -> bool:
        """Validate parameter value is within allowed range based on MIDI spec"""
        ranges = {
            0x16: (0, 2),       # OSC Waveform: 3-bit value (0-2)
            0x17: (40, 88),     # OSC Pitch Coarse: 7-bit value (40-88)
            0x18: (14, 114),    # OSC Pitch Fine: 7-bit value (14-114)
            0x19: (0, 127),     # OSC Pulse Width: 7-bit value (0-127)
            0x1A: (0, 127),     # PWM Depth: 7-bit value (0-127)
            0x1B: (1, 127),     # Pitch Env Velocity: 7-bit value (1-127)
            0x1C: (0, 127),     # Pitch Env Attack: 7-bit value (0-127)
            0x1D: (0, 127),     # Pitch Env Decay: 7-bit value (0-127)
            0x1E: (1, 127),     # Pitch Env Depth: 7-bit value (1-127)
            0x1F: (0, 2),       # Sub OSC Type: 2-bit value (0-2)
        }
        
        if param in ranges:
            min_val, max_val = ranges[param]
            return min_val <= value <= max_val
        return True  # Allow other parameters to pass through

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw MIDI value to display value based on parameter type"""
        display_maps = {
            0x16: ['SAW', 'TRI', 'PW-SQR'],           # Direct mapping for waveforms
            0x17: lambda x: f"{x - 64:+d}",           # -24 to +24 (centered at 64)
            0x18: lambda x: f"{x - 64:+d}",           # -50 to +50 (centered at 64)
            0x1B: lambda x: f"{x - 64:+d}",           # -63 to +63 (centered at 64)
            0x1E: lambda x: f"{x - 64:+d}",           # -63 to +63 (centered at 64)
            0x1F: ['OFF', 'OCT-1', 'OCT-2']          # Direct mapping for sub osc type
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
    TONE_NAME_1 = 0x00    # ASCII 32-127
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
    TONE_LEVEL = 0x0C      # 0-127
    PORTAMENTO_SW = 0x12   # 0-1 (OFF/ON)
    PORTAMENTO_TIME = 0x13 # 0-127
    MONO_SW = 0x14        # 0-1 (OFF/ON)
    OCTAVE_SHIFT = 0x15   # 61-67 (-3 to +3)
    BEND_RANGE_UP = 0x16  # 0-24 semitones
    BEND_RANGE_DOWN = 0x17 # 0-24 semitones
    
    # Partial parameters (0x20-0x2F)
    PARTIAL_SWITCH = 0x20  # 0-1 (OFF/ON)
    PARTIAL_LEVEL = 0x21   # 0-127
    PARTIAL_COARSE = 0x22  # 40-88 (-24 to +24)
    PARTIAL_FINE = 0x23    # 14-114 (-50 to +50)
    WAVE_SHAPE = 0x24      # 0-127
    PULSE_WIDTH = 0x25     # 0-127
    PWM_DEPTH = 0x26       # 0-127
    SUPER_SAW_DEPTH = 0x27 # 0-127
    FILTER_TYPE = 0x28     # 0-3 (OFF,LPF,BPF,HPF)
    CUTOFF = 0x29          # 0-127
    RESONANCE = 0x2A       # 0-127
    FILTER_ENV = 0x2B      # 1-127 (-63 to +63)
    FILTER_KEY = 0x2C      # 0-127
    AMP_ENV = 0x2D         # 0-127
    PAN = 0x2E             # 0-127 (L64-63R)
    RING_SW = 0x1F         # 0-2 (OFF, ---, ON)
    
    # Partial switches (0x19-0x1E)
    PARTIAL1_SWITCH = 0x19  # 0-1 (OFF/ON)
    PARTIAL1_SELECT = 0x1A  # 0-1 (OFF/ON)
    PARTIAL2_SWITCH = 0x1B  # 0-1 (OFF/ON)
    PARTIAL2_SELECT = 0x1C  # 0-1 (OFF/ON)
    PARTIAL3_SWITCH = 0x1D  # 0-1 (OFF/ON)
    PARTIAL3_SELECT = 0x1E  # 0-1 (OFF/ON)

    # Additional common parameters (0x2E-0x3C)
    UNISON_SW = 0x2E        # 0-1 (OFF/ON)
    PORTAMENTO_MODE = 0x31  # 0-1 (NORMAL/LEGATO)
    LEGATO_SW = 0x32       # 0-1 (OFF/ON)
    ANALOG_FEEL = 0x34     # 0-127
    WAVE_SHAPE_COMMON = 0x35      # 0-127 (renamed from WAVE_SHAPE)
    TONE_CATEGORY = 0x36   # 0-127
    UNISON_SIZE = 0x3C     # 0-3 (2,4,6,8 voices)

    # Modify parameters (0x01-0x06)
    ATTACK_TIME_SENS = 0x01    # 0-127
    RELEASE_TIME_SENS = 0x02   # 0-127
    PORTA_TIME_SENS = 0x03     # 0-127
    ENV_LOOP_MODE = 0x04       # 0-2 (OFF, FREE-RUN, TEMPO-SYNC)
    ENV_LOOP_SYNC = 0x05       # 0-19 (sync note values)
    CHROM_PORTA = 0x06         # 0-1 (OFF/ON)

    # Partial oscillator parameters (0x00-0x09)
    OSC_WAVE = 0x00         # 0-7 (SAW, SQR, PW-SQR, TRI, SINE, NOISE, SUPER-SAW, PCM)
    OSC_VARIATION = 0x01    # 0-2 (A, B, C)
    OSC_PITCH = 0x03        # 40-88 (-24 to +24)
    OSC_DETUNE = 0x04       # 14-114 (-50 to +50)
    OSC_PWM_DEPTH = 0x05    # 0-127
    OSC_PW = 0x06          # 0-127
    OSC_PITCH_ATK = 0x07   # 0-127
    OSC_PITCH_DEC = 0x08   # 0-127
    OSC_PITCH_DEPTH = 0x09  # 1-127 (-63 to +63)

    # Filter parameters (0x0A-0x14)
    FILTER_MODE = 0x0A       # 0-7 (BYPASS, LPF, HPF, BPF, PKG, LPF2, LPF3, LPF4)
    FILTER_SLOPE = 0x0B      # 0-1 (-12, -24 dB)
    FILTER_CUTOFF = 0x0C     # 0-127
    FILTER_KEYFOLLOW = 0x0D  # 54-74 (-100 to +100)
    FILTER_ENV_VELO = 0x0E   # 1-127 (-63 to +63)
    FILTER_RESONANCE = 0x0F  # 0-127
    FILTER_ENV_ATK = 0x10    # 0-127
    FILTER_ENV_DEC = 0x11    # 0-127
    FILTER_ENV_SUS = 0x12    # 0-127
    FILTER_ENV_REL = 0x13    # 0-127
    FILTER_ENV_DEPTH = 0x14  # 1-127 (-63 to +63)

    # Amplifier parameters (0x15-0x1B)
    AMP_LEVEL = 0x15         # 0-127
    AMP_VELO_SENS = 0x16     # 1-127 (-63 to +63)
    AMP_ENV_ATK = 0x17       # 0-127
    AMP_ENV_DEC = 0x18       # 0-127
    AMP_ENV_SUS = 0x19       # 0-127
    AMP_ENV_REL = 0x1A       # 0-127
    AMP_PAN = 0x1B          # 0-127 (L64-63R)

    # LFO parameters (0x1C-0x25)
    LFO_SHAPE = 0x1C        # 0-5 (TRI, SIN, SAW, SQR, S&H, RND)
    LFO_RATE = 0x1D        # 0-127
    LFO_SYNC_SW = 0x1E     # 0-1 (OFF/ON)
    LFO_SYNC_NOTE = 0x1F   # 0-19 (sync note values)
    LFO_FADE = 0x20        # 0-127
    LFO_KEY_TRIG = 0x21    # 0-1 (OFF/ON)
    LFO_PITCH_DEPTH = 0x22 # 1-127 (-63 to +63)
    LFO_FILTER_DEPTH = 0x23 # 1-127 (-63 to +63)
    LFO_AMP_DEPTH = 0x24   # 1-127 (-63 to +63)
    LFO_PAN_DEPTH = 0x25   # 1-127 (-63 to +63)

    # Modulation LFO parameters (0x26-0x2F)
    MOD_LFO_SHAPE = 0x26     # 0-5 (TRI, SIN, SAW, SQR, S&H, RND)
    MOD_LFO_RATE = 0x27      # 0-127
    MOD_LFO_SYNC_SW = 0x28   # 0-1 (OFF/ON)
    MOD_LFO_SYNC_NOTE = 0x29 # 0-19 (sync note values)
    OSC_PW_SHIFT = 0x2A      # 0-127
    MOD_LFO_PITCH = 0x2C     # 1-127 (-63 to +63)
    MOD_LFO_FILTER = 0x2D    # 1-127 (-63 to +63)
    MOD_LFO_AMP = 0x2E       # 1-127 (-63 to +63)
    MOD_LFO_PAN = 0x2F       # 1-127 (-63 to +63)

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
            0x17: lambda v: 0 <= v <= 24
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
        elif param in (0x12, 0x14, 0x20, 0x2F, 
                     0x19, 0x1A, 0x1B, 0x1C, 0x1D, 0x1E):  # All switches
            return "ON" if value else "OFF"
        elif param == 0x22:  # Coarse tune
            return f"{value - 64:+d}"  # Convert to -24/+24
        elif param == 0x23:  # Fine tune
            return f"{value - 64:+d}"  # Convert to -50/+50
        elif param == 0x28:  # Filter type
            return ['OFF', 'LPF', 'BPF', 'HPF'][value]
        elif param == 0x2B:  # Filter env
            return f"{value - 64:+d}"  # Convert to -63/+63
        elif param == 0x2E:  # Pan
            if value < 64:
                return f"L{64 - value}"
            elif value > 64:
                return f"{value - 64}R"
            return "C"
        elif param == 0x1F:  # Ring switch
            return ['OFF', '---', 'ON'][value]
        elif param in (0x2E, 0x32):  # Unison and Legato switches
            return "ON" if value else "OFF"
        elif param == 0x31:  # Portamento mode
            return "LEGATO" if value else "NORMAL"
        elif param == 0x3C:  # Unison size
            return str([2, 4, 6, 8][value])  # Convert 0-3 to actual voice count
        elif param == 0x04:  # Envelope loop mode
            return ['OFF', 'FREE-RUN', 'TEMPO-SYNC'][value]
        elif param == 0x05:  # Envelope loop sync note
            return ['16', '12', '8', '4', '2', '1', '3/4', '2/3', '1/2',
                   '3/8', '1/3', '1/4', '3/16', '1/6', '1/8', '3/32',
                   '1/12', '1/16', '1/24', '1/32'][value]
        elif param == 0x06:  # Chromatic portamento
            return "ON" if value else "OFF"
        elif param == 0x00:  # OSC wave type
            return ['SAW', 'SQR', 'PW-SQR', 'TRI', 'SINE', 'NOISE', 'SUPER-SAW', 'PCM'][value]
        elif param == 0x01:  # OSC variation
            return ['A', 'B', 'C'][value]
        elif param == 0x03:  # OSC pitch
            return f"{value - 64:+d}"  # Convert to -24/+24
        elif param == 0x04:  # OSC detune
            return f"{value - 64:+d}"  # Convert to -50/+50
        elif param == 0x09:  # OSC pitch env depth
            return f"{value - 64:+d}"  # Convert to -63/+63
        elif param == 0x0A:  # Filter mode
            return ['BYPASS', 'LPF', 'HPF', 'BPF', 'PKG', 'LPF2', 'LPF3', 'LPF4'][value]
        elif param == 0x0B:  # Filter slope
            return '-24dB' if value else '-12dB'
        elif param == 0x0D:  # Filter keyfollow
            return f"{((value - 54) * 200 / 20) - 100:+.0f}"  # Convert to -100/+100
        elif param in (0x0E, 0x14):  # Bipolar values
            return f"{value - 64:+d}"  # Convert to -63/+63
        elif param == 0x16:  # Amp velocity sens
            return f"{value - 64:+d}"  # Convert to -63/+63
        elif param == 0x1B:  # Pan
            if value < 64:
                return f"L{64 - value}"
            elif value > 64:
                return f"{value - 64}R"
            return "C"
        elif param == 0x1C:  # LFO shape
            return ['TRI', 'SIN', 'SAW', 'SQR', 'S&H', 'RND'][value]
        elif param == 0x1F:  # LFO sync note
            return ['16', '12', '8', '4', '2', '1', '3/4', '2/3', '1/2',
                   '3/8', '1/3', '1/4', '3/16', '1/6', '1/8', '3/32',
                   '1/12', '1/16', '1/24', '1/32'][value]
        elif param in (0x22, 0x23, 0x24, 0x25):  # LFO depths
            return f"{value - 64:+d}"  # Convert to -63/+63
        elif param == 0x26:  # Mod LFO shape
            return ['TRI', 'SIN', 'SAW', 'SQR', 'S&H', 'RND'][value]
        elif param == 0x29:  # Mod LFO sync note
            return ['16', '12', '8', '4', '2', '1', '3/4', '2/3', '1/2',
                   '3/8', '1/3', '1/4', '3/16', '1/6', '1/8', '3/32',
                   '1/12', '1/16', '1/24', '1/32'][value]
        elif param in (0x2C, 0x2D, 0x2E, 0x2F):  # Mod LFO depths
            return f"{value - 64:+d}"  # Convert to -63/+63
        return str(value)

# Other constants as needed... 