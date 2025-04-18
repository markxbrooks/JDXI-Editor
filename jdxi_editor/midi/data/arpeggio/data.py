from enum import Enum

ARPEGGIO_GRID = [
    "1/4",
    "1/8",
    "1/8 L",
    "1/8 H",
    "1/12",
    "1/16",
    "1/16 L",
    "1/16 H",
    "1/24",
]
ARP_DURATION = ["30%", "40%", "50%", "60%", "70%", "80%", "90%", "100%", "120%", "Full"]
ARPEGGIO_MOTIF = [
    "Up  (L)",
    "Up  (L&H)",
    "Up  (_)",
    "Down  (L)",
    "Down  (L&H)",
    "Down  (_)",
    "Up/Down  (L)",
    "Up/Down  (L&H)",
    "Up/Down  (_)",
    "Random  (L)",
    "Random  (_)",
    "Phrase",
]
ARPEGGIO_MOTIF_NAME_LIST = [
    "UP/L",
    "UP/H",
    "UP/_",
    "dn/L",
    "dn/H",
    "dn/_",
    "Ud/L",
    "Ud/H",
    "Ud/_",
    "rn/L",
    "rn/_",
    "PHRASE",
]
ARPEGGIO_STYLE = [
    "001: Basic 1",
    "002: Basic 2",
    "003: Basic 3",
    "004: Basic 4",
    "005: Basic 5",
    "006: Basic 6",
    "007: Seq Ptn 1 (2)",
    "008: Seq Ptn 2 (2)",
    "009: Seq Ptn 3 (2)",
    "010: Seq Ptn 4 (2)",
    "011: Seq Ptn 5 (2)",
    "012: Seq Ptn 6 (3)",
    "013: Seq Ptn 7 (3)",
    "014: Seq Ptn 8 (3)",
    "015: Seq Ptn 9 (3)",
    "016: Seq Ptn 10 (3)",
    "017: Seq Ptn 11 (3)",
    "018: Seq Ptn 12 (3)",
    "019: Seq Ptn 13 (3)",
    "020: Seq Ptn 14 (3)",
    "021: Seq Ptn 15 (3)",
    "022: Seq Ptn 16 (3)",
    "023: Seq Ptn 17 (3)",
    "024: Seq Ptn 18 (4)",
    "025: Seq Ptn 19 (4)",
    "026: Seq Ptn 20 (4)",
    "027: Seq Ptn 21 (4)",
    "028: Seq Ptn 22 (4)",
    "029: Seq Ptn 23 (4)",
    "030: Seq Ptn 24 (4)",
    "031: Seq Ptn 25 (4)",
    "032: Seq Ptn 26 (4)",
    "033: Seq Ptn 27 (4)",
    "034: Seq Ptn 28 (4)",
    "035: Seq Ptn 29 (4)",
    "036: Seq Ptn 30 (5)",
    "037: Seq Ptn 31 (5)",
    "038: Seq Ptn 32 (6)",
    "039: Seq Ptn 33 (p)",
    "040: Seq Ptn 34 (p)",
    "041: Seq Ptn 35 (p)",
    "042: Seq Ptn 36 (p)",
    "043: Seq Ptn 37 (p)",
    "044: Seq Ptn 38 (p)",
    "045: Seq Ptn 39 (p)",
    "046: Seq Ptn 40 (p)",
    "047: Seq Ptn 41 (p)",
    "048: Seq Ptn 42 (p)",
    "049: Seq Ptn 43 (p)",
    "050: Seq Ptn 44 (p)",
    "051: Seq Ptn 45 (p)",
    "052: Seq Ptn 46 (p)",
    "053: Seq Ptn 47 (p)",
    "054: Seq Ptn 48 (p)",
    "055: Seq Ptn 49 (p)",
    "056: Seq Ptn 50 (p)",
    "057: Seq Ptn 51 (p)",
    "058: Seq Ptn 52 (p)",
    "059: Seq Ptn 53 (p)",
    "060: Seq Ptn 54 (p)",
    "061: Seq Ptn 55 (p)",
    "062: Seq Ptn 56 (p)",
    "063: Seq Ptn 57 (p)",
    "064: Seq Ptn 58 (p)",
    "065: Seq Ptn 59 (p)",
    "066: Seq Ptn 60 (p)",
    "067: Bassline 1 (1)",
    "068: Bassline 2 (1)",
    "069: Bassline 3 (1)",
    "070: Bassline 4 (1)",
    "071: Bassline 5 (1)",
    "072: Bassline 6 (1)",
    "073: Bassline 7 (1)",
    "074: Bassline 8 (1)",
    "075: Bassline 9 (1)",
    "076: Bassline 10 (2)",
    "077: Bassline 11 (2)",
    "078: Bassline 12 (2)",
    "079: Bassline 13 (2)",
    "080: Bassline 14 (2)",
    "081: Bassline 15 (2)",
    "082: Bassline 16 (3)",
    "083: Bassline 17 (3)",
    "084: Bassline 18 (3)",
    "085: Bassline 19 (3)",
    "086: Bassline 20 (3)",
    "087: Bassline 21 (3)",
    "088: Bassline 22 (p)",
    "089: Bassline 23 (p)",
    "090: Bassline 24 (p)",
    "091: Bassline 25 (p)",
    "092: Bassline 26 (p)",
    "093: Bassline 27 (p)",
    "094: Bassline 28 (p)",
    "095: Bassline 29 (p)",
    "096: Bassline 30 (p)",
    "097: Bassline 31 (p)",
    "098: Bassline 32 (p)",
    "099: Bassline 33 (p)",
    "100: Bassline 34 (p)",
    "101: Bassline 35 (p)",
    "102: Bassline 36 (p)",
    "103: Bassline 37 (p)",
    "104: Bassline 38 (p)",
    "105: Bassline 39 (p)",
    "106: Bassline 40 (p)",
    "107: Bassline 41 (p)",
    "108: Sliced 1",
    "109: Sliced 2",
    "110: Sliced 3",
    "111: Sliced 4",
    "112: Sliced 5",
    "113: Sliced 6",
    "114: Sliced 7",
    "115: Sliced 8",
    "116: Sliced 9",
    "117: Sliced 10",
    "118: Gtr Arp 1 (4)",
    "119: Gtr Arp 2 (5)",
    "120: Gtr Arp 3 (6)",
    "121: Gtr Backing 1",
    "122: Gtr Backing 2",
    "123: Key Backing 1",
    "124: Key Backing 2",
    "125: Key Backing 3 (1-3)",
    "126: 1/1 Note Trg (1)",
    "127: 1/2 Note Trg (1)",
    "128: 1/4 Note Trg (1)",
]


class ArpeggioStyle(Enum):
    BASIC_1 = 0
    names = {
        0: "001: Basic 1",
        1: "002: Basic 2",
        2: "003: Basic 3",
        3: "004: Basic 4",
        4: "005: Basic 5",
        5: "006: Basic 6",
        6: "007: Seq Ptn 1 (2)",
        7: "008: Seq Ptn 2 (2)",
        8: "009: Seq Ptn 3 (2)",
        9: "010: Seq Ptn 4 (2)",
        10: "011: Seq Ptn 5 (2)",
        11: "012: Seq Ptn 6 (3)",
        12: "013: Seq Ptn 7 (3)",
        13: "014: Seq Ptn 8 (3)",
        14: "015: Seq Ptn 9 (3)",
        15: "016: Seq Ptn 10 (3)",
        16: "017: Seq Ptn 11 (3)",
        17: "018: Seq Ptn 12 (3)",
        18: "019: Seq Ptn 13 (3)",
        19: "020: Seq Ptn 14 (3)",
        20: "021: Seq Ptn 15 (3)",
        21: "022: Seq Ptn 16 (3)",
        22: "023: Seq Ptn 17 (3)",
        23: "024: Seq Ptn 18 (4)",
        24: "025: Seq Ptn 19 (4)",
        25: "026: Seq Ptn 20 (4)",
        26: "027: Seq Ptn 21 (4)",
        27: "028: Seq Ptn 22 (4)",
        28: "029: Seq Ptn 23 (4)",
        29: "030: Seq Ptn 24 (4)",
        30: "031: Seq Ptn 25 (4)",
        31: "032: Seq Ptn 26 (4)",
        32: "033: Seq Ptn 27 (4)",
        33: "034: Seq Ptn 28 (4)",
        34: "035: Seq Ptn 29 (4)",
        35: "036: Seq Ptn 30 (5)",
        36: "037: Seq Ptn 31 (5)",
        37: "038: Seq Ptn 32 (6)",
        38: "039: Seq Ptn 33 (p)",
        39: "040: Seq Ptn 34 (p)",
        40: "041: Seq Ptn 35 (p)",
        41: "042: Seq Ptn 36 (p)",
        42: "043: Seq Ptn 37 (p)",
        43: "044: Seq Ptn 38 (p)",
        44: "045: Seq Ptn 39 (p)",
        45: "046: Seq Ptn 40 (p)",
        46: "047: Seq Ptn 41 (p)",
        47: "048: Seq Ptn 42 (p)",
        48: "049: Seq Ptn 43 (p)",
        49: "050: Seq Ptn 44 (p)",
        50: "051: Seq Ptn 45 (p)",
        51: "052: Seq Ptn 46 (p)",
        52: "053: Seq Ptn 47 (p)",
        53: "054: Seq Ptn 48 (p)",
        54: "055: Seq Ptn 49 (p)",
        55: "056: Seq Ptn 50 (p)",
        56: "057: Seq Ptn 51 (p)",
        57: "058: Seq Ptn 52 (p)",
        58: "059: Seq Ptn 53 (p)",
        59: "060: Seq Ptn 54 (p)",
        60: "061: Seq Ptn 55 (p)",
        61: "062: Seq Ptn 56 (p)",
        62: "063: Seq Ptn 57 (p)",
        63: "064: Seq Ptn 58 (p)",
        64: "065: Seq Ptn 59 (p)",
        65: "066: Seq Ptn 60 (p)",
        66: "067: Bassline 1 (1)",
        67: "068: Bassline 2 (1)",
        68: "069: Bassline 3 (1)",
        69: "070: Bassline 4 (1)",
        70: "071: Bassline 5 (1)",
        71: "072: Bassline 6 (1)",
        72: "073: Bassline 7 (1)",
        73: "074: Bassline 8 (1)",
        74: "075: Bassline 9 (1)",
        75: "076: Bassline 10 (2)",
        76: "077: Bassline 11 (2)",
        77: "078: Bassline 12 (2)",
        78: "079: Bassline 13 (2)",
        79: "080: Bassline 14 (2)",
        80: "081: Bassline 15 (2)",
        81: "082: Bassline 16 (3)",
        82: "083: Bassline 17 (3)",
        83: "084: Bassline 18 (3)",
        84: "085: Bassline 19 (3)",
        85: "086: Bassline 20 (3)",
        86: "087: Bassline 21 (3)",
        87: "088: Bassline 22 (p)",
        88: "089: Bassline 23 (p)",
        89: "090: Bassline 24 (p)",
        90: "091: Bassline 25 (p)",
        91: "092: Bassline 26 (p)",
        92: "093: Bassline 27 (p)",
        93: "094: Bassline 28 (p)",
        94: "095: Bassline 29 (p)",
        95: "096: Bassline 30 (p)",
        96: "097: Bassline 31 (p)",
        97: "098: Bassline 32 (p)",
        98: "099: Bassline 33 (p)",
        99: "100: Bassline 34 (p)",
        100: "101: Bassline 35 (p)",
        101: "102: Bassline 36 (p)",
        102: "103: Bassline 37 (p)",
        103: "104: Bassline 38 (p)",
        104: "105: Bassline 39 (p)",
        105: "106: Bassline 40 (p)",
        106: "107: Bassline 41 (p)",
        107: "108: Sliced 1",
        108: "109: Sliced 2",
        109: "110: Sliced 3",
        110: "111: Sliced 4",
        111: "112: Sliced 5",
        112: "113: Sliced 6",
        113: "114: Sliced 7",
        114: "115: Sliced 8",
        115: "116: Sliced 9",
        116: "117: Sliced 10",
        117: "118: Gtr Arp 1 (4)",
        118: "119: Gtr Arp 2 (5)",
        119: "120: Gtr Arp 3 (6)",
        120: "121: Gtr Backing 1",
        121: "122: Gtr Backing 2",
        122: "123: Key Backing 1",
        123: "124: Key Backing 2",
        124: "125: Key Backing 3 (1-3)",
        125: "126: 1/1 Note Trg (1)",
        126: "127: 1/2 Note Trg (1)",
        127: "128: 1/4 Note Trg (1)",
    }

    @property
    def display_name(self) -> str:
        """Get display name for grid value"""
        return self.name

    @property
    def midi_value(self) -> int:
        """Get MIDI value for grid"""
        return self.value


PATTERNS = ["UP", "DOWN", "UP/DOWN", "RANDOM", "NOTE ORDER", "CHORD", "USER"]
DURATIONS = [
    "1/4",
    "1/8",
    "1/8 Triplet",
    "1/16",
    "1/16 Triplet",
    "1/32",
    "1/32 Triplet",
]
OCTAVE_RANGES = [-4, -3, -2, -1, 0, 1, 2, 3, 4]
