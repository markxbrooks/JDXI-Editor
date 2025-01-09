# Digital synth preset names
DIGITAL_PRESETS = [
    '001: JP8 Strings1', '002: Soft Pad 1',   '003: JP8 Strings2', '004: JUNO Str 1',
    '005: Oct Strings',  '006: Brite Str 1',  '007: Boreal Pad',   '008: JP8 Strings3',
    '009: JP8 Strings4', '010: Hollow Pad 1', '011: LFO Pad 1',    '012: Hybrid Str',
    # ... (add all presets)
]

# Create a mapping of index to name for easier lookup
PRESET_MAP = {i: name for i, name in enumerate(DIGITAL_PRESETS)}

# Drum kit names
DRUM_KITS = [
    "TR-808", "TR-909", "CR-78", "TR-606", "TR-707", "ACOUSTIC", "JAZZ", "HOUSE",
    "TECHNO", "HIP-HOP", "DANCE", "ROCK", "ELECTRONIC", "PERCUSSION", "SFX", "USER"
]

# Drum part names
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

# Create a flat lookup for kit categories
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