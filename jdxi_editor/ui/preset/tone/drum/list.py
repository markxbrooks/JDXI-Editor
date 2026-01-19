"""
JDXi Drum presets
"""


class JDXiPresetToneListDrum:
    """
    JDXi Preset lists as enumerated lists and for Program Changes
    """

    PROGRAM_CHANGE = [
        {
            "id": "001",
            "name": "TR-909 Kit 1",
            "category": "Classic Roland Drum Machines",
            "msb": "86",
            "lsb": "64",
            "pc": "1",
        },
        {
            "id": "002",
            "name": "TR-808 Kit 1",
            "category": "Classic Roland Drum Machines",
            "msb": "86",
            "lsb": "64",
            "pc": "2",
        },
        {
            "id": "003",
            "name": "707&727 Kit1",
            "category": "Classic Roland Drum Machines",
            "msb": "86",
            "lsb": "64",
            "pc": "3",
        },
        {
            "id": "004",
            "name": "CR-78 Kit 1",
            "category": "Classic Roland Drum Machines",
            "msb": "86",
            "lsb": "64",
            "pc": "4",
        },
        {
            "id": "005",
            "name": "TR-606 Kit 1",
            "category": "Classic Roland Drum Machines",
            "msb": "86",
            "lsb": "64",
            "pc": "5",
        },
        {
            "id": "006",
            "name": "TR-626 Kit 1",
            "category": "Classic Roland Drum Machines",
            "msb": "86",
            "lsb": "64",
            "pc": "6",
        },
        {
            "id": "007",
            "name": "EDM Kit 1",
            "category": "Electronic Dance Music (EDM) Styles",
            "msb": "86",
            "lsb": "64",
            "pc": "7",
        },
        {
            "id": "008",
            "name": "Drum&Bs Kit1",
            "category": "Electronic Dance Music (EDM) Styles",
            "msb": "86",
            "lsb": "64",
            "pc": "8",
        },
        {
            "id": "009",
            "name": "Techno Kit 1",
            "category": "Electronic Dance Music (EDM) Styles",
            "msb": "86",
            "lsb": "64",
            "pc": "9",
        },
        {
            "id": "010",
            "name": "House Kit 1",
            "category": "Electronic Dance Music (EDM) Styles",
            "msb": "86",
            "lsb": "64",
            "pc": "10",
        },
        {
            "id": "011",
            "name": "Hiphop Kit 1",
            "category": "Hip-Hop & R&B",
            "msb": "86",
            "lsb": "64",
            "pc": "11",
        },
        {
            "id": "012",
            "name": "R&B Kit 1",
            "category": "Hip-Hop & R&B",
            "msb": "86",
            "lsb": "64",
            "pc": "12",
        },
        {
            "id": "026",
            "name": "80's Kit 1",
            "category": "Decade-Based Kits",
            "msb": "86",
            "lsb": "64",
            "pc": "26",
        },
        {
            "id": "027",
            "name": "90's Kit 1",
            "category": "Decade-Based Kits",
            "msb": "86",
            "lsb": "64",
            "pc": "27",
        },
        {
            "id": "028",
            "name": "Noise Kit 1",
            "category": "Miscellaneous & Experimental",
            "msb": "86",
            "lsb": "64",
            "pc": "28",
        },
        {
            "id": "029",
            "name": "Pop Kit 1",
            "category": "Miscellaneous & Experimental",
            "msb": "86",
            "lsb": "64",
            "pc": "29",
        },
        {
            "id": "031",
            "name": "Rock Kit",
            "category": "Acoustic & Live Drum Styles",
            "msb": "86",
            "lsb": "64",
            "pc": "31",
        },
        {
            "id": "032",
            "name": "Jazz Kit",
            "category": "Acoustic & Live Drum Styles",
            "msb": "86",
            "lsb": "64",
            "pc": "32",
        },
        {
            "id": "033",
            "name": "Latin Kit",
            "category": "Acoustic & Live Drum Styles",
            "msb": "86",
            "lsb": "64",
            "pc": "33",
        },
    ]
    ENUMERATED = [
        "001: TR-909 Kit 1",
        "002: TR-808 Kit 1",
        "003: 707&727 Kit1",
        "004: CR-78 Kit 1",
        "005: TR-606 Kit 1",
        "006: TR-626 Kit 1",
        "007: EDM Kit 1",
        "008: Drum&Bs Kit1",
        "009: Techno Kit 1",
        "010: House Kit 1",
        "011: Hiphop Kit 1",
        "012: R&B Kit 1",
        "013: TR-909 Kit 2",
        "014: TR-909 Kit 3",
        "015: TR-808 Kit 2",
        "016: TR-808 Kit 3",
        "017: TR-808 Kit 4",
        "018: 808&909 Kit1",
        "019: 808&909 Kit2",
        "020: 707&727 Kit2",
        "021: 909&7*7 Kit1",
        "022: 808&7*7 Kit1",
        "023: EDM Kit 2",
        "024: Techno Kit 2",
        "025: Hiphop Kit 2",
        "026: 80's Kit 1",
        "027: 90's Kit 1",
        "028: Noise Kit 1",
        "029: Pop Kit 1",
        "030: Pop Kit 2",
        "031: Rock Kit",
        "032: Jazz Kit",
        "033: Latin Kit",
    ]
    CATEGORIES = {
        "Classic Roland": {
            "TR-808": {
                "description": "The legendary Roland TR-808 sound. Known for deep kick, snappy snare, and iconic cowbell.",
                "style": "Hip-Hop, Electronic, Pop",
                "era": "1980s",
            },
            "TR-909": {
                "description": "The Roland TR-909 kit. Punchy kick, crisp hi-hats, and powerful snare. House music staple.",
                "style": "House, Techno, Dance",
                "era": "1980s",
            },
            "CR-78": {
                "description": "The CompuRhythm CR-78. Warm, vintage sounds with unique character.",
                "style": "Pop, Electronic",
                "era": "1970s",
            },
            "TR-606": {
                "description": "The Drumatix TR-606. Sharp, tight sounds perfect for electronic music.",
                "style": "Electronic, Experimental",
                "era": "1980s",
            },
            "TR-707": {
                "description": "Digital drum sounds from the TR-707. Clean and punchy.",
                "style": "Pop, Dance",
                "era": "1980s",
            },
        },
        "Acoustic": {
            "ACOUSTIC": {
                "description": "Natural acoustic drum kit with studio-quality samples.",
                "style": "Rock, Pop, Jazz",
                "era": "Modern",
            },
            "JAZZ": {
                "description": "Classic jazz kit with brushes and warm tones.",
                "style": "Jazz, Blues",
                "era": "Classic",
            },
        },
        "Electronic": {
            "HOUSE": {
                "description": "Modern house music kit with tight kicks and crisp hats.",
                "style": "House, Dance",
                "era": "Modern",
            },
            "TECHNO": {
                "description": "Hard-hitting techno kit with industrial elements.",
                "style": "Techno, Industrial",
                "era": "Modern",
            },
            "ELECTRONIC": {
                "description": "Versatile electronic kit with modern production sounds.",
                "style": "Electronic, Pop",
                "era": "Modern",
            },
        },
        "Urban": {
            "HIP-HOP": {
                "description": "Contemporary hip-hop kit with deep kicks and sharp snares.",
                "style": "Hip-Hop, R&B",
                "era": "Modern",
            },
            "DANCE": {
                "description": "High-energy dance kit with punchy sounds.",
                "style": "Dance, Pop",
                "era": "Modern",
            },
        },
        "Band": {
            "ROCK": {
                "description": "Powerful rock kit with big room sound.",
                "style": "Rock, Alternative",
                "era": "Modern",
            }
        },
        "Special": {
            "PERCUSSION": {
                "description": "World percussion collection with various ethnic instruments.",
                "style": "World, Percussion",
                "era": "Various",
            },
            "SFX": {
                "description": "Sound effects and experimental percussion.",
                "style": "Experimental, Electronic",
                "era": "Modern",
            },
            "USER": {
                "description": "User-programmable kit for custom sounds.",
                "style": "Any",
                "era": "Custom",
            },
        },
    }
