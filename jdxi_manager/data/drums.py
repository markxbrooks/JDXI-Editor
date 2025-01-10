"""Data structures for JD-Xi Drum parameters"""

# Drum kit parameters
DR = {
    'common': {
        'level': (0x00, 0, 127),
        'pan': (0x01, -64, 63),
        'reverb_send': (0x02, 0, 127),
        'delay_send': (0x03, 0, 127),
        'fx_send': (0x04, 0, 127)
    },
    'pad': {
        'wave': (0x00, 0, 127),
        'level': (0x01, 0, 127),
        'pan': (0x02, -64, 63),
        'tune': (0x03, -50, 50),
        'decay': (0x04, 0, 127),
        'mute_group': (0x05, 0, 31),
        'velocity': (0x06, 0, 127),
        'filter': (0x07, 0, 127),
        'reverb_send': (0x08, 0, 127),
        'delay_send': (0x09, 0, 127),
        'fx_send': (0x0A, 0, 127)
    }
}

# Preset drum kits
DRUM_KITS = [
    # Factory presets
    "TR-909 Kit 1", "TR-909 Kit 2", "TR-909 Kit 3",
    "TR-808 Kit 1", "TR-808 Kit 2", "TR-808 Kit 3",
    "707&727 Kit1", "707&727 Kit2",
    "CR-78 Kit 1", "CR-78 Kit 2",
    "TR-606 Kit 1", "TR-606 Kit 2",
    "TR-626 Kit 1", "TR-626 Kit 2",
    
    # Genre kits
    "EDM Kit 1", "EDM Kit 2", "EDM Kit 3",
    "House Kit 1", "House Kit 2",
    "Techno Kit 1", "Techno Kit 2",
    "Hip Hop Kit 1", "Hip Hop Kit 2",
    "Drum&Bs Kit1", "Drum&Bs Kit2",
    "Jazz Kit 1", "Jazz Kit 2",
    "Rock Kit 1", "Rock Kit 2",
    
    # Special kits
    "Hybrid Kit 1", "Hybrid Kit 2",
    "FX Kit 1", "FX Kit 2",
    "Percussion Kit 1", "Percussion Kit 2"
]

# Individual drum parts/instruments
DRUM_PARTS = {
    'kicks': [
        # TR-909 kicks
        "TR-909 Kick 1", "TR-909 Kick 2", "TR-909 Kick 3",
        "TR-909 Kick Long", "TR-909 Kick Short",
        # TR-808 kicks
        "TR-808 Kick 1", "TR-808 Kick 2", "TR-808 Kick 3",
        "TR-808 Kick Long", "TR-808 Kick Short",
        # Other kicks
        "TR-707 Kick", "TR-727 Kick",
        "TR-606 Kick", "TR-626 Kick",
        "CR-78 Kick", "CR-78 Kick Long",
        # Modern kicks
        "EDM Kick 1", "EDM Kick 2",
        "House Kick 1", "House Kick 2",
        "Techno Kick 1", "Techno Kick 2"
    ],
    'snares': [
        # TR-909 snares
        "TR-909 Snare 1", "TR-909 Snare 2", "TR-909 Snare 3",
        "TR-909 Snare Rim", "TR-909 Snare Roll",
        # TR-808 snares
        "TR-808 Snare 1", "TR-808 Snare 2", "TR-808 Snare 3",
        "TR-808 Snare Rim", "TR-808 Snare Long",
        # Other snares
        "TR-707 Snare", "TR-727 Snare",
        "TR-606 Snare", "TR-626 Snare",
        "CR-78 Snare", "CR-78 Snare Rim",
        # Modern snares
        "EDM Snare 1", "EDM Snare 2",
        "House Snare 1", "House Snare 2",
        "Techno Snare 1", "Techno Snare 2"
    ],
    'hihats': [
        # TR-909 hihats
        "TR-909 HiHat Closed", "TR-909 HiHat Open",
        "TR-909 HiHat Half", "TR-909 HiHat Foot",
        # TR-808 hihats
        "TR-808 HiHat Closed", "TR-808 HiHat Open",
        "TR-808 HiHat Half", "TR-808 HiHat Foot",
        # Other hihats
        "TR-707 HiHat Closed", "TR-707 HiHat Open",
        "TR-727 HiHat Closed", "TR-727 HiHat Open",
        "TR-606 HiHat Closed", "TR-606 HiHat Open",
        "CR-78 HiHat Closed", "CR-78 HiHat Open",
        # Modern hihats
        "EDM HiHat 1", "EDM HiHat 2",
        "House HiHat 1", "House HiHat 2",
        "Techno HiHat 1", "Techno HiHat 2"
    ],
    'cymbals': [
        # TR-909 cymbals
        "TR-909 Crash", "TR-909 Crash Long",
        "TR-909 Ride", "TR-909 Ride Bell",
        # TR-808 cymbals
        "TR-808 Crash", "TR-808 Crash Long",
        "TR-808 Ride", "TR-808 Ride Bell",
        # Other cymbals
        "TR-707 Crash", "TR-707 Ride",
        "TR-727 Crash", "TR-727 Ride",
        "TR-626 Crash", "TR-626 Ride",
        # Modern cymbals
        "EDM Crash 1", "EDM Crash 2",
        "House Ride 1", "House Ride 2",
        "Techno Crash 1", "Techno Crash 2"
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
        "TR-606 Tom Low", "TR-606 Tom High",
        "CR-78 Tom Low", "CR-78 Tom High"
    ],
    'percussion': [
        # Classic percussion
        "TR-909 Clap", "TR-909 Rim", "TR-909 Maracas",
        "TR-808 Clap", "TR-808 Cowbell", "TR-808 Clave",
        "TR-808 Maracas", "TR-808 Conga High",
        "TR-707 Clap", "TR-707 Tambourine", "TR-707 Cowbell",
        "TR-727 Agogo", "TR-727 Bongo", "TR-727 Whistle",
        "CR-78 Tambourine", "CR-78 Guiro", "CR-78 Bongo",
        # Modern percussion
        "EDM Clap 1", "EDM Clap 2",
        "House Perc 1", "House Perc 2",
        "Techno Perc 1", "Techno Perc 2"
    ],
    'fx': [
        # Effect sounds
        "Noise Short", "Noise Long",
        "White Noise", "Pink Noise",
        "Zap 1", "Zap 2",
        "Sweep Up", "Sweep Down",
        "Metal Hit", "Wood Block",
        "Reverse Cymbal", "Reverse Snare",
        # Modern FX
        "EDM Impact 1", "EDM Impact 2",
        "House FX 1", "House FX 2",
        "Techno FX 1", "Techno FX 2"
    ]
}

# We can also add new data structures like we did for analog
class DrumPadSettings:
    """Settings for a single drum pad"""
    def __init__(self):
        self.wave = 0
        self.level = 100
        self.pan = 64
        self.tune = 0
        self.decay = 64
        self.mute_group = 0
        self.velocity = 100
        self.filter = 127
        self.reverb_send = 0
        self.delay_send = 0
        self.fx_send = 0

class DrumKitPatch:
    """Complete drum kit patch"""
    def __init__(self):
        self.name = "Init Kit"
        self.level = 100
        self.pan = 64
        self.reverb_send = 0
        self.delay_send = 0
        self.fx_send = 0
        self.pads = [DrumPadSettings() for _ in range(16)] 