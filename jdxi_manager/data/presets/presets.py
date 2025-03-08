# Digital synth preset names
from jdxi_manager.data.presets.data import DIGITAL_PRESETS

# Create address mapping of index to name for easier lookup
PRESET_MAP = {i: name for i, name in enumerate(DIGITAL_PRESETS)}

# Drum kit names
DRUM_KITS = [
    "TR-808", "TR-909", "CR-78", "TR-606", "TR-707", "ACOUSTIC", "JAZZ", "HOUSE",
    "TECHNO", "HIP-HOP", "DANCE", "ROCK", "ELECTRONIC", "PERCUSSION", "SFX", "USER"
]

# Drum address names
DRUM_PARTS = [
    "KICK", "SNARE", "CLOSED HAT", "OPEN HAT", "TOM/PERC 1", 
    "TOM/PERC 2", "CRASH/PERC 3", "RIDE/PERC 4"
]

# Preset Categories
PRESET_CATEGORIES = {
    'Strings & Pads': {
        'Strings': [
            '001: JP8 Strings1', '003: JP8 Strings2', '004: JUNO Str 1', 
            # ... rest of strings
        ],
        # ... rest of categories
    },
    # ... rest of main categories
}

# Flatten categories for easy lookup
PRESET_CATEGORY_MAP = {}
for main_category, subcategories in PRESET_CATEGORIES.items():
    for subcategory, presets in subcategories.items():
        for preset in presets:
            preset_number = int(preset.split(':')[0]) - 1  # Convert to 0-based index
            PRESET_CATEGORY_MAP[preset_number] = {
                'main_category': main_category,
                'subcategory': subcategory
            }

# Initial patches dictionary (example subset)
DIGITAL_PRESET_TONE_DICT = {
    1: {"Name": "JP8 Strings1", "Category": "Strings/Pad", "MSB": 95, "LSB": 64, "PC": 1},
    2: {"Name": "Soft Pad 1", "Category": "Strings/Pad", "MSB": 95, "LSB": 64, "PC": 2},
    3: {"Name": "JP8 Strings2", "Category": "Strings/Pad", "MSB": 95, "LSB": 64, "PC": 3},
    4: {"Name": "JUNO Str 1", "Category": "Strings/Pad", "MSB": 95, "LSB": 64, "PC": 4},
    5: {"Name": "Oct Strings", "Category": "Strings/Pad", "MSB": 95, "LSB": 64, "PC": 5},
    6: {"Name": "Brite Str 1", "Category": "Strings/Pad", "MSB": 95, "LSB": 64, "PC": 6},
    7: {"Name": "Boreal Pad", "Category": "Strings/Pad", "MSB": 95, "LSB": 64, "PC": 7},
    8: {"Name": "JP8 Strings3", "Category": "Strings/Pad", "MSB": 95, "LSB": 64, "PC": 8},
    9: {"Name": "JP8 Strings4", "Category": "Strings/Pad", "MSB": 95, "LSB": 64, "PC": 9},
    10: {"Name": "Hollow Pad 1", "Category": "Strings/Pad", "MSB": 95, "LSB": 64, "PC": 10},
    11: {"Name": "LFO Pad 1", "Category": "Strings/Pad", "MSB": 95, "LSB": 64, "PC": 11},
    12: {"Name": "Hybrid Str", "Category": "Strings/Pad", "MSB": 95, "LSB": 64, "PC": 12},
    13: {"Name": "Awakening 1", "Category": "Strings/Pad", "MSB": 95, "LSB": 64, "PC": 13},
    14: {"Name": "Cincosoft 1", "Category": "Strings/Pad", "MSB": 95, "LSB": 64, "PC": 14},
    15: {"Name": "Bright Pad 1", "Category": "Strings/Pad", "MSB": 95, "LSB": 64, "PC": 15},
    16: {"Name": "Analog Str 1", "Category": "Strings/Pad", "MSB": 95, "LSB": 64, "PC": 16},
    17: {"Name": "Soft ResoPd1", "Category": "Strings/Pad", "MSB": 95, "LSB": 64, "PC": 17},
    18: {"Name": "HPF Poly 1", "Category": "Strings/Pad", "MSB": 95, "LSB": 64, "PC": 18},
    19: {"Name": "BPF Poly", "Category": "Strings/Pad", "MSB": 95, "LSB": 64, "PC": 19},
    20: {"Name": "Sweep Pad 1", "Category": "Strings/Pad", "MSB": 95, "LSB": 64, "PC": 20},
    48: {"Name": "Super Saw 1", "Category": "Lead", "MSB": 95, "LSB": 64, "PC": 48},
    49: {"Name": "S-SawStacLd1", "Category": "Lead", "MSB": 95, "LSB": 64, "PC": 49},
    50: {"Name": "Tekno Lead 1", "Category": "Lead", "MSB": 95, "LSB": 64, "PC": 50},
    89: {"Name": "Seq Bass 1", "Category": "Bass", "MSB": 95, "LSB": 64, "PC": 89},
    90: {"Name": "Reso Bass 1", "Category": "Bass", "MSB": 95, "LSB": 64, "PC": 90},
    91: {"Name": "TB Bass 1", "Category": "Bass", "MSB": 95, "LSB": 64, "PC": 91},
    92: {"Name": "106 Bass 1", "Category": "Bass", "MSB": 95, "LSB": 64, "PC": 92},
    138: {"Name": "Low Bass 1", "Category": "Bass", "MSB": 95, "LSB": 65, "PC": 10},
    139: {"Name": "Low Bass 2", "Category": "Bass", "MSB": 95, "LSB": 65, "PC": 11},
    140: {"Name": "Kick Bass 1", "Category": "Bass", "MSB": 95, "LSB": 65, "PC": 12},
    141: {"Name": "SinDetuneBs1", "Category": "Bass", "MSB": 95, "LSB": 65, "PC": 13},
    142: {"Name": "Organ Bass 1", "Category": "Bass", "MSB": 95, "LSB": 65, "PC": 14},
    143: {"Name": "Growl Bass 1", "Category": "Bass", "MSB": 95, "LSB": 65, "PC": 15},
    144: {"Name": "Talking Bs 1", "Category": "Bass", "MSB": 95, "LSB": 65, "PC": 16},
    145: {"Name": "LFO Bass 1", "Category": "Bass", "MSB": 95, "LSB": 65, "PC": 17},
    146: {"Name": "LFO Bass 2", "Category": "Bass", "MSB": 95, "LSB": 65, "PC": 18},
    147: {"Name": "Crack Bass", "Category": "Bass", "MSB": 95, "LSB": 65, "PC": 19},
    148: {"Name": "Wobble Bs 1", "Category": "Bass", "MSB": 95, "LSB": 65, "PC": 20},
    149: {"Name": "Wobble Bs 2", "Category": "Bass", "MSB": 95, "LSB": 65, "PC": 21},
    150: {"Name": "Wobble Bs 3", "Category": "Bass", "MSB": 95, "LSB": 65, "PC": 22},
    151: {"Name": "Wobble Bs 4", "Category": "Bass", "MSB": 95, "LSB": 65, "PC": 23},
    152: {"Name": "SideChainBs1", "Category": "Bass", "MSB": 95, "LSB": 65, "PC": 24},
    153: {"Name": "SideChainBs2", "Category": "Bass", "MSB": 95, "LSB": 65, "PC": 25},
    154: {"Name": "House Bass 1", "Category": "Bass", "MSB": 95, "LSB": 65, "PC": 26},
    155: {"Name": "FM Bass", "Category": "Bass", "MSB": 95, "LSB": 65, "PC": 27},
    156: {"Name": "4Op FM Bass1", "Category": "Bass", "MSB": 95, "LSB": 65, "PC": 28},
    157: {"Name": "Ac. Bass", "Category": "Bass", "MSB": 95, "LSB": 65, "PC": 29},
    158: {"Name": "Fingerd Bs 1", "Category": "Bass", "MSB": 95, "LSB": 65, "PC": 30},
    159: {"Name": "Picked Bass", "Category": "Bass", "MSB": 95, "LSB": 65, "PC": 31},
    160: {"Name": "Fretless Bs", "Category": "Bass", "MSB": 95, "LSB": 65, "PC": 32},
    161: {"Name": "Slap Bass 1", "Category": "Bass", "MSB": 95, "LSB": 65, "PC": 33},
    162: {"Name": "JD Piano 1", "Category": "Keyboard", "MSB": 95, "LSB": 65, "PC": 34},
    163: {"Name": "E. Grand 1", "Category": "Keyboard", "MSB": 95, "LSB": 65, "PC": 35},
    164: {"Name": "Trem EP 1", "Category": "Keyboard", "MSB": 95, "LSB": 65, "PC": 36},
    165: {"Name": "FM E. Piano 1", "Category": "Keyboard", "MSB": 95, "LSB": 65, "PC": 37},
    166: {"Name": "FM E. Piano 2", "Category": "Keyboard", "MSB": 95, "LSB": 65, "PC": 38},
    167: {"Name": "Vib Wurly 1", "Category": "Keyboard", "MSB": 95, "LSB": 65, "PC": 39},
    168: {"Name": "Pulse Clav", "Category": "Keyboard", "MSB": 95, "LSB": 65, "PC": 40},
    169: {"Name": "Clav", "Category": "Keyboard", "MSB": 95, "LSB": 65, "PC": 41},
    170: {"Name": "70’s E. Organ", "Category": "Keyboard", "MSB": 95, "LSB": 65, "PC": 42},
    171: {"Name": "House Org 1", "Category": "Keyboard", "MSB": 95, "LSB": 65, "PC": 43},
    172: {"Name": "House Org 2", "Category": "Keyboard", "MSB": 95, "LSB": 65, "PC": 44},
    173: {"Name": "Bell 1", "Category": "Keyboard", "MSB": 95, "LSB": 65, "PC": 45},
    174: {"Name": "Bell 2", "Category": "Keyboard", "MSB": 95, "LSB": 65, "PC": 46},
    175: {"Name": "Organ Bell", "Category": "Keyboard", "MSB": 95, "LSB": 65, "PC": 47},
    176: {"Name": "Vibraphone 1", "Category": "Keyboard", "MSB": 95, "LSB": 65, "PC": 48},
    177: {"Name": "Steel Drum", "Category": "Keyboard", "MSB": 95, "LSB": 65, "PC": 49},
    178: {"Name": "Harp 1", "Category": "Keyboard", "MSB": 95, "LSB": 65, "PC": 50},
    179: {"Name": "Ac. Guitar", "Category": "Keyboard", "MSB": 95, "LSB": 65, "PC": 51},
    180: {"Name": "Bright Strat", "Category": "Keyboard", "MSB": 95, "LSB": 65, "PC": 52},
    181: {"Name": "Funk Guitar1", "Category": "Keyboard", "MSB": 95, "LSB": 65, "PC": 53},
    182: {"Name": "Jazz Guitar", "Category": "Keyboard", "MSB": 95, "LSB": 65, "PC": 54},
    183: {"Name": "Dist Guitar1", "Category": "Keyboard", "MSB": 95, "LSB": 65, "PC": 55},
    184: {"Name": "D. Mute Gtr1", "Category": "Keyboard", "MSB": 95, "LSB": 65, "PC": 56},
    185: {"Name": "E. Sitar", "Category": "Keyboard", "MSB": 95, "LSB": 65, "PC": 57},
    186: {"Name": "Sitar Drone", "Category": "Keyboard", "MSB": 95, "LSB": 65, "PC": 58},
    187: {"Name": "FX 1", "Category": "FX/Other", "MSB": 95, "LSB": 65, "PC": 59},
    188: {"Name": "FX 2", "Category": "FX/Other", "MSB": 95, "LSB": 65, "PC": 60},
    189: {"Name": "FX 3", "Category": "FX/Other", "MSB": 95, "LSB": 65, "PC": 61},
    190: {"Name": "Tuned Winds1", "Category": "FX/Other", "MSB": 95, "LSB": 65, "PC": 62},
    191: {"Name": "Bend Lead 1", "Category": "FX/Other", "MSB": 95, "LSB": 65, "PC": 63},
    192: {"Name": "RiSER 1", "Category": "FX/Other", "MSB": 95, "LSB": 65, "PC": 64},
    193: {"Name": "Rising SEQ 1", "Category": "FX/Other", "MSB": 95, "LSB": 65, "PC": 65},
    194: {"Name": "Scream Saw", "Category": "FX/Other", "MSB": 95, "LSB": 65, "PC": 66},
    195: {"Name": "Noise SEQ 1", "Category": "FX/Other", "MSB": 95, "LSB": 65, "PC": 67},
    196: {"Name": "Syn Vox 1", "Category": "FX/Other", "MSB": 95, "LSB": 65, "PC": 68},
    197: {"Name": "JD SoftVox", "Category": "FX/Other", "MSB": 95, "LSB": 65, "PC": 69},
    198: {"Name": "Vox Pad", "Category": "FX/Other", "MSB": 95, "LSB": 65, "PC": 70},
    199: {"Name": "VP-330 Chr", "Category": "FX/Other", "MSB": 95, "LSB": 65, "PC": 71},
    200: {"Name": "Orch Hit", "Category": "FX/Other", "MSB": 95, "LSB": 65, "PC": 72},
    201: {"Name": "Philly Hit", "Category": "FX/Other", "MSB": 95, "LSB": 65, "PC": 73},
    202: {"Name": "House Hit", "Category": "FX/Other", "MSB": 95, "LSB": 65, "PC": 74},
    203: {"Name": "O’Skool Hit1", "Category": "FX/Other", "MSB": 95, "LSB": 65, "PC": 75},
    204: {"Name": "Punch Hit", "Category": "FX/Other", "MSB": 95, "LSB": 65, "PC": 76},
    205: {"Name": "Tao Hit", "Category": "FX/Other", "MSB": 95, "LSB": 65, "PC": 77},
    206: {"Name": "SEQ Saw 1", "Category": "Seq", "MSB": 95, "LSB": 65, "PC": 78},
    207: {"Name": "SEQ Sqr", "Category": "Seq", "MSB": 95, "LSB": 65, "PC": 79},
    208: {"Name": "SEQ Tri 1", "Category": "Seq", "MSB": 95, "LSB": 65, "PC": 80},
    209: {"Name": "SEQ 1", "Category": "Seq", "MSB": 95, "LSB": 65, "PC": 81},
    210: {"Name": "SEQ 2", "Category": "Seq", "MSB": 95, "LSB": 65, "PC": 82},
    211: {"Name": "SEQ 3", "Category": "Seq", "MSB": 95, "LSB": 65, "PC": 83},
    212: {"Name": "SEQ 4", "Category": "Seq", "MSB": 95, "LSB": 65, "PC": 84},
    213: {"Name": "Sqr Reso Plk", "Category": "Seq", "MSB": 95, "LSB": 65, "PC": 85},
    214: {"Name": "Pluck Synth1", "Category": "Seq", "MSB": 95, "LSB": 65, "PC": 86},
    215: {"Name": "Paperclip 1", "Category": "Seq", "MSB": 95, "LSB": 65, "PC": 87},
    216: {"Name": "Sonar Pluck1", "Category": "Seq", "MSB": 95, "LSB": 65, "PC": 88},
    217: {"Name": "SqrTrapPlk 1", "Category": "Seq", "MSB": 95, "LSB": 65, "PC": 89},
    218: {"Name": "TB Saw Seq 1", "Category": "Seq", "MSB": 95, "LSB": 65, "PC": 90},
    219: {"Name": "TB Sqr Seq 1", "Category": "Seq", "MSB": 95, "LSB": 65, "PC": 91},
    220: {"Name": "JUNO Key", "Category": "Seq", "MSB": 95, "LSB": 65, "PC": 92},
    221: {"Name": "Analog Poly1", "Category": "Seq", "MSB": 95, "LSB": 65, "PC": 93},
    222: {"Name": "Analog Poly2", "Category": "Seq", "MSB": 95, "LSB": 65, "PC": 94},
    223: {"Name": "Analog Poly3", "Category": "Seq", "MSB": 95, "LSB": 65, "PC": 95},
    224: {"Name": "Analog Poly4", "Category": "Seq", "MSB": 95, "LSB": 65, "PC": 96},
    225: {"Name": "JUNO Octavr1", "Category": "Seq", "MSB": 95, "LSB": 65, "PC": 97},
    226: {"Name": "EDM Synth 1", "Category": "Seq", "MSB": 95, "LSB": 65, "PC": 98},
    227: {"Name": "Super Saw 2", "Category": "Seq", "MSB": 95, "LSB": 65, "PC": 99},
    228: {"Name": "S-Saw Poly", "Category": "Seq", "MSB": 95, "LSB": 65, "PC": 100},
    229: {"Name": "Trance Key 1", "Category": "Seq", "MSB": 95, "LSB": 65, "PC": 101},
    230: {"Name": "S-Saw Pad 1", "Category": "Seq", "MSB": 95, "LSB": 65, "PC": 102},
    231: {"Name": "7th Stac Syn", "Category": "Seq", "MSB": 95, "LSB": 65, "PC": 103},
    232: {"Name": "S-SawStc Syn", "Category": "Seq", "MSB": 95, "LSB": 65, "PC": 104},
    233: {"Name": "Trance Key 2", "Category": "Seq", "MSB": 95, "LSB": 65, "PC": 105},
    234: {"Name": "Analog Brass", "Category": "Brass", "MSB": 95, "LSB": 65, "PC": 106},
    235: {"Name": "Reso Brass", "Category": "Brass", "MSB": 95, "LSB": 65, "PC": 107},
    236: {"Name": "Soft Brass 1", "Category": "Brass", "MSB": 95, "LSB": 65, "PC": 108},
    237: {"Name": "FM Brass", "Category": "Brass", "MSB": 95, "LSB": 65, "PC": 109},
    238: {"Name": "Syn Brass 1", "Category": "Brass", "MSB": 95, "LSB": 65, "PC": 110},
    239: {"Name": "Syn Brass 2", "Category": "Brass", "MSB": 95, "LSB": 65, "PC": 111},
    240: {"Name": "JP8 Brass", "Category": "Brass", "MSB": 95, "LSB": 65, "PC": 112},
    241: {"Name": "Soft SynBrs1", "Category": "Brass", "MSB": 95, "LSB": 65, "PC": 113},
    242: {"Name": "Soft SynBrs2", "Category": "Brass", "MSB": 95, "LSB": 65, "PC": 114},
    243: {"Name": "EpicSlow Brs", "Category": "Brass", "MSB": 95, "LSB": 65, "PC": 115},
    244: {"Name": "JUNO Brass", "Category": "Brass", "MSB": 95, "LSB": 65, "PC": 116},
    245: {"Name": "Poly Brass", "Category": "Brass", "MSB": 95, "LSB": 65, "PC": 117},
    246: {"Name": "Voc:Ensemble", "Category": "FX/Other", "MSB": 95, "LSB": 65, "PC": 118},
    247: {"Name": "Voc:5thStack", "Category": "FX/Other", "MSB": 95, "LSB": 65, "PC": 119},
    248: {"Name": "Voc:Robot", "Category": "FX/Other", "MSB": 95, "LSB": 65, "PC": 120},
    249: {"Name": "Voc:Saw", "Category": "FX/Other", "MSB": 95, "LSB": 65, "PC": 121},
    250: {"Name": "Voc:Sqr", "Category": "FX/Other", "MSB": 95, "LSB": 65, "PC": 122},
    251: {"Name": "Voc:Rise Up", "Category": "FX/Other", "MSB": 95, "LSB": 65, "PC": 123},
    252: {"Name": "Voc:Auto Vib", "Category": "FX/Other", "MSB": 95, "LSB": 65, "PC": 124},
    253: {"Name": "Voc:PitchEnv", "Category": "FX/Other", "MSB": 95, "LSB": 65, "PC": 125},
    254: {"Name": "Voc:VP-330", "Category": "FX/Other", "MSB": 95, "LSB": 65, "PC": 126},
    255: {"Name": "Voc:Noise", "Category": "FX/Other", "MSB": 95, "LSB": 65, "PC": 127},
    256: {"Name": "Init Tone", "Category": "FX/Other", "MSB": 95, "LSB": 65, "PC": 128},
}

# Example usage:
# patch_number = 230
# print(f"Patch {patch_number}: {DIGITAL_PRESET_TONE_DICT[patch_number]}")


# Drum kit categories and descriptions
DRUM_CATEGORIES = {
    'Classic Roland': {
        'TR-808': {
            'description': 'The legendary Roland TR-808 sound. Known for deep kick, snappy snare, and iconic cowbell.',
            'style': 'Hip-Hop, Electronic, Pop',
            'era': '1980s'
        },
        'TR-909': {
            'description': 'The Roland TR-909 kit. Punchy kick, crisp hi-hats, and powerful snare. House music staple.',
            'style': 'House, Techno, Dance',
            'era': '1980s'
        },
        'CR-78': {
            'description': 'The CompuRhythm CR-78. Warm, vintage sounds with unique character.',
            'style': 'Pop, Electronic',
            'era': '1970s'
        },
        'TR-606': {
            'description': 'The Drumatix TR-606. Sharp, tight sounds perfect for electronic music.',
            'style': 'Electronic, Experimental',
            'era': '1980s'
        },
        'TR-707': {
            'description': 'Digital drum sounds from the TR-707. Clean and punchy.',
            'style': 'Pop, Dance',
            'era': '1980s'
        }
    },
    'Acoustic': {
        'ACOUSTIC': {
            'description': 'Natural acoustic drum kit with studio-quality samples.',
            'style': 'Rock, Pop, Jazz',
            'era': 'Modern'
        },
        'JAZZ': {
            'description': 'Classic jazz kit with brushes and warm tones.',
            'style': 'Jazz, Blues',
            'era': 'Classic'
        }
    },
    'Electronic': {
        'HOUSE': {
            'description': 'Modern house music kit with tight kicks and crisp hats.',
            'style': 'House, Dance',
            'era': 'Modern'
        },
        'TECHNO': {
            'description': 'Hard-hitting techno kit with industrial elements.',
            'style': 'Techno, Industrial',
            'era': 'Modern'
        },
        'ELECTRONIC': {
            'description': 'Versatile electronic kit with modern production sounds.',
            'style': 'Electronic, Pop',
            'era': 'Modern'
        }
    },
    'Urban': {
        'HIP-HOP': {
            'description': 'Contemporary hip-hop kit with deep kicks and sharp snares.',
            'style': 'Hip-Hop, R&B',
            'era': 'Modern'
        },
        'DANCE': {
            'description': 'High-energy dance kit with punchy sounds.',
            'style': 'Dance, Pop',
            'era': 'Modern'
        }
    },
    'Band': {
        'ROCK': {
            'description': 'Powerful rock kit with big room sound.',
            'style': 'Rock, Alternative',
            'era': 'Modern'
        }
    },
    'Special': {
        'PERCUSSION': {
            'description': 'World percussion collection with various ethnic instruments.',
            'style': 'World, Percussion',
            'era': 'Various'
        },
        'SFX': {
            'description': 'Sound effects and experimental percussion.',
            'style': 'Experimental, Electronic',
            'era': 'Modern'
        },
        'USER': {
            'description': 'User-programmable kit for custom sounds.',
            'style': 'Any',
            'era': 'Custom'
        }
    }
}

# Create address flat lookup for kit categories
DRUM_KIT_MAP = {
    kit_name: {
        'main_category': main_cat,
        'description': info['description'],
        'style': info['style'],
        'era': info['era']
    }
    for main_cat, subcats in DRUM_CATEGORIES.items()
    for kit_name, info in subcats.items()
}
PCM_WAVES = ['000: Off',
'001: Calc.Saw',     '002: DistSaw Wave', '003: GR-300 Saw',   '004: Lead Wave 1',  '005: Lead Wave 2',  '006: Unison Saw',   '007: Saw+Sub Wave',
'008: SqrLeadWave',  '009: SqrLeadWave+', '010: FeedbackWave', '011: Bad Axe',      '012: Cutting Lead', '013: DistTB Sqr',   '014: Sync Sweep',
'015: Saw Sync',     '016: Unison Sync+', '017: Sync Wave',    '018: Cutters',      '019: Nasty',        '020: Bagpipe Wave', '021: Wave Scan',
'022: Wire String',  '023: Lead Wave 3',  '024: PWM Wave 1',   '025: PWM Wave 2',   '026: MIDI Clav',    '027: Huge MIDI',    '028: Wobble Bs 1',
'029: Wobble Bs 2',  '030: Hollow Bass',  '031: SynBs Wave',   '032: Solid Bass',   '033: House Bass',   '034: 4OP FM Bass',  '035: Fine Wine',
'036: Bell Wave 1',  '037: Bell Wave 1+', '038: Bell Wave 2',  '039: Digi Wave 1',  '040: Digi Wave 2',  '041: Org Bell',     '042: Gamelan',
'043: Crystal',      '044: Finger Bell',  '045: DipthongWave', '046: DipthongWv +', '047: Hollo Wave1',  '048: Hollo Wave2',  '049: Hollo Wave2+',
'050: Heaven Wave',  '051: Doo',          '052: MMM Vox',      '053: Eeh Formant',  '054: Iih Formant',  '055: Syn Vox 1',    '056: Syn Vox 2',
'057: Org Vox',      '058: Male Ooh',     '059: LargeChrF 1',  '060: LargeChrF 2',  '061: Female Oohs',  '062: Female Aahs',  '063: Atmospheric',
'064: Air Pad 1',    '065: Air Pad 2',    '066: Air Pad 3',    '067: VP-330 Choir', '068: SynStrings 1', '069: SynStrings 2', '070: SynStrings 3',
'071: SynStrings 4', '072: SynStrings 5', '073: SynStrings 6', '074: Revalation',   '075: Alan\'s Pad',  '076: LFO Poly',     '077: Boreal Pad L',
'078: Boreal Pad R', '079: HPF Pad L',    '080: HPF Pad R',    '081: Sweep Pad',    '082: Chubby Ld',    '083: Fantasy Pad',  '084: Legend Pad',
'085: D-50 Stack',   '086: ChrdOfCnadaL', '087: ChrdOfCnadaR', '088: Fireflies',    '089: JazzyBubbles', '090: SynthFx 1',    '091: SynthFx 2',
'092: X-Mod Wave 1', '093: X-Mod Wave 2', '094: SynVox Noise', '095: Dentist Nz',   '096: Atmosphere',   '097: Anklungs',     '098: Xylo Seq',
'099: O\'Skool Hit', '100: Orch. Hit',    '101: Punch Hit',    '102: Philly Hit',   '103: ClassicHseHt', '104: Tao Hit',      '105: Smear Hit',
'106: 808 Kick 1Lp', '107: 808 Kick 2Lp', '108: 909 Kick Lp',  '109: JD Piano',     '110: E.Grand',      '111: Stage EP',     '112: Wurly',
'113: EP Hard',      '114: FM EP 1',      '115: FM EP 2',      '116: FM EP 3',      '117: Harpsi Wave',  '118: Clav Wave 1',  '119: Clav Wave 2',
'120: Vibe Wave',    '121: Organ Wave 1', '122: Organ Wave 2', '123: PercOrgan 1',  '124: PercOrgan 2',  '125: Vint.Organ',   '126: Harmonica',
'127: Ac. Guitar',   '128: Nylon Gtr',    '129: Brt Strat',    '130: Funk Guitar',  '131: Jazz Guitar',  '132: Dist Guitar',  '133: D.Mute Gtr',
'134: FatAc. Bass',  '135: Fingerd Bass', '136: Picked Bass',  '137: Fretless Bs',  '138: Slap Bass',    '139: Strings 1',    '140: Strings 2',
'141: Strings 3 L',  '142: Strings 3 R',  '143: Pizzagogo',    '144: Harp Harm',    '145: Harp Wave',    '146: PopBrsAtk',    '147: PopBrass',
'148: Tp Section',   '149: Studio Tp',    '150: Tp Vib Mari',  '151: Tp Hrmn Mt',   '152: FM Brass',     '153: Trombone',     '154: Wide Sax',
'155: Flute Wave',   '156: Flute Push',   '157: E.Sitar',      '158: Sitar Drone',  '159: Agogo',        '160: Steel Drums'
]

DRUM_WAVES = ['000: Off',
'001: 78 Kick P',    '002: 606 Kick P',   '003: 808 Kick 1aP', '004: 808 Kick 1bP', '005: 808 Kick 1cP', '006: 808 Kick 2aP', '007: 808 Kick 2bP',
'008: 808 Kick 2cP', '009: 808 Kick 3aP', '010: 808 Kick 3bP', '011: 808 Kick 3cP', '012: 808 Kick 4aP', '013: 808 Kick 4bP', '014: 808 Kick 4cP',
'015: 808 Kick 1Lp', '016: 808 Kick 2Lp', '017: 909 Kick 1aP', '018: 909 Kick 1bP', '019: 909 Kick 1cP', '020: 909 Kick 2bP', '021: 909 Kick 2cP',
'022: 909 Kick 3P',  '023: 909 Kick 4',   '024: 909 Kick 5',   '025: 909 Kick 6',   '026: 909 DstKickP', '027: 909 Kick Lp',  '028: 707 Kick 1 P',
'029: 707 Kick 2 P', '030: 626 Kick 1 P', '031: 626 Kick 2 P', '032: Analog Kick1', '033: Analog Kick2', '034: Analog Kick3', '035: Analog Kick4',
'036: Analog Kick5', '037: PlasticKick1', '038: PlasticKick2', '039: Synth Kick 1', '040: Synth Kick 2', '041: Synth Kick 3', '042: Synth Kick 4',
'043: Synth Kick 5', '044: Synth Kick 6', '045: Synth Kick 7', '046: Synth Kick 8', '047: Synth Kick 9', '048: Synth Kick10', '049: Synth Kick11',
'050: Synth Kick12', '051: Synth Kick13', '052: Synth Kick14', '053: Synth Kick15', '054: Vint Kick P',  '055: Jungle KickP', '056: HashKick 1 P',
'057: HashKick 2 P', '058: Lite Kick P',  '059: Dry Kick 1',   '060: Dry Kick 2',   '061: Tight Kick P', '062: Old Kick',     '063: Warm Kick P',
'064: Hush Kick P',  '065: Power Kick',   '066: Break Kick',   '067: Turbo Kick',   '068: TM-2 Kick 1',  '069: TM-2 Kick 2',  '070: PurePhatKckP',
'071: Bright KickP', '072: LoBit Kick1P', '073: LoBit Kick2P', '074: Dance Kick P', '075: Hip Kick P',   '076: HipHop Kick',  '077: Mix Kick 1',
'078: Mix Kick 2',   '079: Wide Kick P',  '080: LD Kick P',    '081: SF Kick 1 P',  '082: SF Kick 2 P',  '083: TY Kick P',    '084: WD Kick P',
'085: Reg.Kick P',   '086: Rock Kick P',  '087: Jz Dry Kick',  '088: Jazz Kick P',  '089: 78 Snr',       '090: 606 Snr 1 P',  '091: 606 Snr 2 P',
'092: 808 Snr 1a P', '093: 808 Snr 1b P', '094: 808 Snr 1c P', '095: 808 Snr 2a P', '096: 808 Snr 2b P', '097: 808 Snr 2c P', '098: 808 Snr 3a P',
'099: 808 Snr 3b P', '100: 808 Snr 3c P', '101: 909 Snr 1a P', '102: 909 Snr 1b P', '103: 909 Snr 1c P', '104: 909 Snr 1d P', '105: 909 Snr 2a P',
'106: 909 Snr 2b P', '107: 909 Snr 2c P', '108: 909 Snr 2d P', '109: 909 Snr 3a P', '110: 909 Snr 3b P', '111: 909 Snr 3c P', '112: 909 Snr 3d P',
'113: 909 DstSnr1P', '114: 909 DstSnr2P', '115: 909 DstSnr3P', '116: 707 Snr 1a P', '117: 707 Snr 2a P', '118: 707 Snr 1b P', '119: 707 Snr 2b P',
'120: 626 Snr 1',    '121: 626 Snr 2',    '122: 626 Snr 3',    '123: 626 Snr 1a P', '124: 626 Snr 3a P', '125: 626 Snr 1b P', '126: 626 Snr 2 P',
'127: 626 Snr 3b P', '128: Analog Snr 1', '129: Analog Snr 2', '130: Analog Snr 3', '131: Synth Snr 1',  '132: Synth Snr 2',  '133: 106 Snr',
'134: Sim Snare',    '135: Jungle Snr 1', '136: Jungle Snr 2', '137: Jungle Snr 3', '138: Lite Snare',   '139: Lo-Bit Snr1P', '140: Lo-Bit Snr2P',
'141: HphpJazzSnrP', '142: PurePhatSnrP', '143: DRDisco SnrP', '144: Ragga Snr',    '145: Lo-Fi Snare',  '146: drums_data Snare',     '147: DanceHallSnr',
'148: Break Snr',    '149: Piccolo SnrP', '150: TM-2 Snr 1',   '151: TM-2 Snr 2',   '152: WoodSnr RS',   '153: LD Snr',       '154: SF Snr P',
'155: TY Snr',       '156: WD Snr P',     '157: Tight Snr',    '158: Reg.Snr1 P',   '159: Reg.Snr2 P',   '160: Ballad Snr P', '161: Rock Snr1 P',
'162: Rock Snr2 P',  '163: LD Rim',       '164: SF Rim',       '165: TY Rim',       '166: WD Rim P',     '167: Jazz Snr P',   '168: Jazz Rim P',
'169: Jz BrshSlapP', '170: Jz BrshSwshP', '171: Swish&Trn P',  '172: 78 Rimshot',   '173: 808 RimshotP', '174: 909 RimshotP', '175: 707 Rimshot',
'176: 626 Rimshot',  '177: Vint Stick P', '178: Lo-Bit Stk P', '179: Hard Stick P', '180: Wild Stick P', '181: LD Cstick',    '182: TY Cstick',
'183: WD Cstick',    '184: 606 H.Tom P',  '185: 808 H.Tom P',  '186: 909 H.Tom P',  '187: 707 H.Tom P',  '188: 626 H.Tom 1',  '189: 626 H.Tom 2',
'190: SimV Tom 1 P', '191: LD H.Tom P',   '192: SF H.Tom P',   '193: TY H.Tom P',   '194: 808 M.Tom P',  '195: 909 M.Tom P',  '196: 707 M.Tom P',
'197: 626 M.Tom 1',  '198: 626 M.Tom 2',  '199: SimV Tom 2 P', '200: LD M.Tom P',   '201: SF M.Tom P',   '202: TY M.Tom P',   '203: 606 L.Tom P',
'204: 808 L.Tom P',  '205: 909 L.Tom P',  '206: 707 L.Tom P',  '207: 626 L.Tom 1',  '208: 626 L.Tom 2',  '209: SimV Tom 3 P', '210: SimV Tom 4 P',
'211: LD L.Tom P',   '212: SF L.Tom P',   '213: TY L.Tom P',   '214: 78 CHH',       '215: 606 CHH',      '216: 808 CHH',      '217: 909 CHH 1',
'218: 909 CHH 2',    '219: 909 CHH 3',    '220: 909 CHH 4',    '221: 707 CHH',      '222: 626 CHH',      '223: HipHop CHH',   '224: Lite CHH',
'225: Reg.CHH',      '226: Rock CHH',     '227: S13 CHH Tip',  '228: S14 CHH Tip',  '229: 606 C&OHH',    '230: 808 C&OHH S',  '231: 808 C&OHH L',
'232: Hip PHH',      '233: Reg.PHH',      '234: Rock PHH',     '235: S13 PHH',      '236: S14 PHH',      '237: 606 OHH',      '238: 808 OHH S',
'239: 808 OHH L',    '240: 909 OHH 1',    '241: 909 OHH 2',    '242: 909 OHH 3',    '243: 707 OHH',      '244: 626 OHH',      '245: HipHop OHH',
'246: Lite OHH',     '247: Reg.OHH',      '248: Rock OHH',     '249: S13 OHH Shft', '250: S14 OHH Shft', '251: 78 Cymbal',    '252: 606 Cymbal',
'253: 808 Cymbal 1', '254: 808 Cymbal 2', '255: 808 Cymbal 3', '256: 909 CrashCym', '257: 909 Rev Cym',  '258: MG Nz Cym',    '259: 707 CrashCym',
'260: 626 CrashCym', '261: Crash Cym 1',  '262: Crash Cym 2',  '263: Rock Crash 1', '264: Rock Crash 2', '265: P17 CrashTip', '266: S18 CrashTip',
'267: Z18kCrashSft', '268: Jazz Crash',   '269: 909 RideCym',  '270: 707 RideCym',  '271: 626 RideCym',  '272: Ride Cymbal',  '273: 626 ChinaCym',
'274: China Cymbal', '275: Splash Cym',   '276: 626 Cup',      '277: Rock Rd Cup',  '278: 808 ClapS1 P', '279: 808 ClapS2 P', '280: 808 ClapL1 P',
'281: 808 ClapL2 P', '282: 909 Clap 1 P', '283: 909 Clap 2 P', '284: 909 Clap 3 P', '285: 909 DstClapP', '286: 707 Clap P',   '287: 626 Clap',
'288: R8 Clap',      '289: Cheap Clap',   '290: Old Clap P',   '291: Hip Clap',     '292: Dist Clap',    '293: Hand Clap',    '294: Club Clap',
'295: Real Clap',    '296: Funk Clap',    '297: Bright Clap',  '298: TM-2 Clap',    '299: Amb Clap',     '300: Disc Clap',    '301: Claptail',
'302: Gospel Clap',  '303: 78 Tamb',      '304: 707 Tamb P',   '305: 626 Tamb',     '306: TM-2 Tamb',    '307: Tamborine 1',  '308: Tamborine 2',
'309: Tamborine 3',  '310: 808 CowbellP', '311: 707 Cowbell',  '312: 626 Cowbell',  '313: Cowbell Mute', '314: 78 H.Bongo P', '315: 727 H.Bongo',
'316: Bongo Hi Mt',  '317: Bongo Hi Slp', '318: Bongo Hi Op',  '319: 78 L.Bongo P', '320: 727 L.Bongo',  '321: Bongo Lo Op',  '322: Bongo Lo Slp',
'323: 808 H.CongaP', '324: 727 H.CngOpP', '325: 727 H.CngMtP', '326: 626 H.CngaOp', '327: 626 H.CngaMt', '328: Conga Hi Mt',  '329: Conga 2H Mt',
'330: Conga Hi Slp', '331: Conga 2H Slp', '332: Conga Hi Op',  '333: Conga 2H Op',  '334: 808 M.CongaP', '335: 78 L.Conga P', '336: 808 L.CongaP',
'337: 727 L.CongaP', '338: 626 L.Conga',  '339: Conga Lo Mt',  '340: Conga Lo Slp', '341: Conga Lo Op',  '342: Conga 2L Mt',  '343: Conga 2L Op',
'344: Conga Slp Op', '345: Conga Efx',    '346: Conga Thumb',  '347: 727 H.Timbal', '348: 626 H.Timbal', '349: 727 L.Timbal', '350: 626 L.Timbal',
'351: Timbale 1',    '352: Timbale 2',    '353: Timbale 3',    '354: Timbale 4',    '355: Timbles LoOp', '356: Timbles LoMt', '357: TimbalesHand',
'358: Timbales Rim', '359: TmbSideStick', '360: 727 H.Agogo',  '361: 626 H.Agogo',  '362: 727 L.Agogo',  '363: 626 L.Agogo',  '364: 727 Cabasa P',
'365: Cabasa Up',    '366: Cabasa Down',  '367: Cabasa Cut',   '368: 78 Maracas P', '369: 808 MaracasP', '370: 727 MaracasP', '371: Maracas',
'372: 727 WhistleS', '373: 727 WhistleL', '374: Whistle',      '375: 78 Guiro S',   '376: 78 Guiro L',   '377: Guiro',        '378: Guiro Long',
'379: 78 Claves P',  '380: 808 Claves P', '381: 626 Claves',   '382: Claves',       '383: Wood Block',   '384: Triangle',     '385: 78 MetalBt P',
'386: 727 StrChime', '387: 626 Shaker',   '388: Shaker',       '389: Finger Snap',  '390: Club FinSnap', '391: Snap',         '392: Group Snap',
'393: Op Pandeiro',  '394: Mt Pandeiro',  '395: PandeiroOp',   '396: PandeiroMt',   '397: PandeiroHit',  '398: PandeiroRim',  '399: PandeiroCrsh',
'400: PandeiroRoll', '401: 727 Quijada',  '402: TablaBayam 1', '403: TablaBayam 2', '404: TablaBayam 3', '405: TablaBayam 4', '406: TablaBayam 5',
'407: TablaBayam 6', '408: TablaBayam 7', '409: Udo',          '410: Udu Pot Hi',   '411: Udu Pot Slp',  '412: Scratch 1',    '413: Scratch 2',
'414: Scratch 3',    '415: Scratch 4',    '416: Scratch 5',    '417: Dance M',      '418: Ahh M',        '419: Let\'s Go M',  '420: Hah F',
'421: Yeah F',       '422: C\'mon Baby F','423: Wooh F',       '424: White Noise',  '425: Pink Noise',   '426: Atmosphere',   '427: PercOrgan 1',
'428: PercOrgan 2',  '429: TB Blip',      '430: D.Mute Gtr',   '431: Flute Fx',     '432: Pop Brs Atk',  '433: Strings Hit',  '434: Smear Hit',
'435: O\'Skool Hit', '436: Orch. Hit',    '437: Punch Hit',    '438: Philly Hit',   '439: ClassicHseHt', '440: Tao Hit',      '441: MG S Zap 1',
'442: MG S Zap 2',   '443: MG S Zap 3',   '444: SH2 S Zap 1',  '445: SH2 S Zap 2',  '446: SH2 S Zap 3',  '447: SH2 S Zap 4',  '448: SH2 S Zap 5',
'449: SH2 U Zap 1',  '450: SH2 U Zap 2',  '451: SH2 U Zap 3',  '452: SH2 U Zap 4',  '453: SH2 U Zap 5']