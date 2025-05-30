# Create address flat lookup for kit categories
# import json
# import pandas as pd
# from io import StringIO

PCM_WAVES = [
    "000: Off",
    "001: Calc.Saw",
    "002: DistSaw Wave",
    "003: GR-300 Saw",
    "004: Lead Wave 1",
    "005: Lead Wave 2",
    "006: Unison Saw",
    "007: Saw+Sub Wave",
    "008: SqrLeadWave",
    "009: SqrLeadWave+",
    "010: FeedbackWave",
    "011: Bad Axe",
    "012: Cutting Lead",
    "013: DistTB Sqr",
    "014: Sync Sweep",
    "015: Saw Sync",
    "016: Unison Sync+",
    "017: Sync Wave",
    "018: Cutters",
    "019: Nasty",
    "020: Bagpipe Wave",
    "021: Wave Scan",
    "022: Wire String",
    "023: Lead Wave 3",
    "024: PWM Wave 1",
    "025: PWM Wave 2",
    "026: MIDI Clav",
    "027: Huge MIDI",
    "028: Wobble Bs 1",
    "029: Wobble Bs 2",
    "030: Hollow Bass",
    "031: SynBs Wave",
    "032: Solid Bass",
    "033: House Bass",
    "034: 4OP FM Bass",
    "035: Fine Wine",
    "036: Bell Wave 1",
    "037: Bell Wave 1+",
    "038: Bell Wave 2",
    "039: Digi Wave 1",
    "040: Digi Wave 2",
    "041: Org Bell",
    "042: Gamelan",
    "043: Crystal",
    "044: Finger Bell",
    "045: DipthongWave",
    "046: DipthongWv +",
    "047: Hollo Wave1",
    "048: Hollo Wave2",
    "049: Hollo Wave2+",
    "050: Heaven Wave",
    "051: Doo",
    "052: MMM Vox",
    "053: Eeh Formant",
    "054: Iih Formant",
    "055: Syn Vox 1",
    "056: Syn Vox 2",
    "057: Org Vox",
    "058: Male Ooh",
    "059: LargeChrF 1",
    "060: LargeChrF 2",
    "061: Female Oohs",
    "062: Female Aahs",
    "063: Atmospheric",
    "064: Air Pad 1",
    "065: Air Pad 2",
    "066: Air Pad 3",
    "067: VP-330 Choir",
    "068: SynStrings 1",
    "069: SynStrings 2",
    "070: SynStrings 3",
    "071: SynStrings 4",
    "072: SynStrings 5",
    "073: SynStrings 6",
    "074: Revalation",
    "075: Alan's Pad",
    "076: LFO Poly",
    "077: Boreal Pad L",
    "078: Boreal Pad R",
    "079: HPF Pad L",
    "080: HPF Pad R",
    "081: Sweep Pad",
    "082: Chubby Ld",
    "083: Fantasy Pad",
    "084: Legend Pad",
    "085: D-50 Stack",
    "086: ChrdOfCnadaL",
    "087: ChrdOfCnadaR",
    "088: Fireflies",
    "089: JazzyBubbles",
    "090: SynthFx 1",
    "091: SynthFx 2",
    "092: X-Mod Wave 1",
    "093: X-Mod Wave 2",
    "094: SynVox Noise",
    "095: Dentist Nz",
    "096: Atmosphere",
    "097: Anklungs",
    "098: Xylo Seq",
    "099: O'Skool Hit",
    "100: Orch. Hit",
    "101: Punch Hit",
    "102: Philly Hit",
    "103: ClassicHseHt",
    "104: Tao Hit",
    "105: Smear Hit",
    "106: 808 Kick 1Lp",
    "107: 808 Kick 2Lp",
    "108: 909 Kick Lp",
    "109: JD Piano",
    "110: E.Grand",
    "111: Stage EP",
    "112: Wurly",
    "113: EP Hard",
    "114: FM EP 1",
    "115: FM EP 2",
    "116: FM EP 3",
    "117: Harpsi Wave",
    "118: Clav Wave 1",
    "119: Clav Wave 2",
    "120: Vibe Wave",
    "121: Organ Wave 1",
    "122: Organ Wave 2",
    "123: PercOrgan 1",
    "124: PercOrgan 2",
    "125: Vint.Organ",
    "126: Harmonica",
    "127: Ac. Guitar",
    "128: Nylon Gtr",
    "129: Brt Strat",
    "130: Funk Guitar",
    "131: Jazz Guitar",
    "132: Dist Guitar",
    "133: D.Mute Gtr",
    "134: FatAc. Bass",
    "135: Fingerd Bass",
    "136: Picked Bass",
    "137: Fretless Bs",
    "138: Slap Bass",
    "139: Strings 1",
    "140: Strings 2",
    "141: Strings 3 L",
    "142: Strings 3 R",
    "143: Pizzagogo",
    "144: Harp Harm",
    "145: Harp Wave",
    "146: PopBrsAtk",
    "147: PopBrass",
    "148: Tp Section",
    "149: Studio Tp",
    "150: Tp Vib Mari",
    "151: Tp Hrmn Mt",
    "152: FM Brass",
    "153: Trombone",
    "154: Wide Sax",
    "155: Flute Wave",
    "156: Flute Push",
    "157: E.Sitar",
    "158: Sitar Drone",
    "159: Agogo",
    "160: Steel Drums",
]

PCM_WAVES_CATEGORIZED = [
    {"Category": "None", "Wave Number": 0, "Wave Name": "Off"},
    {"Category": "Lead & Synth Waves", "Wave Number": 1, "Wave Name": "Calc.Saw"},
    {"Category": "Lead & Synth Waves", "Wave Number": 2, "Wave Name": "DistSaw Wave"},
    {"Category": "Lead & Synth Waves", "Wave Number": 3, "Wave Name": "GR-300 Saw"},
    {"Category": "Lead & Synth Waves", "Wave Number": 4, "Wave Name": "Lead Wave 1"},
    {"Category": "Lead & Synth Waves", "Wave Number": 5, "Wave Name": "Lead Wave 2"},
    {"Category": "Lead & Synth Waves", "Wave Number": 6, "Wave Name": "Unison Saw"},
    {"Category": "Lead & Synth Waves", "Wave Number": 7, "Wave Name": "Saw+Sub Wave"},
    {"Category": "Lead & Synth Waves", "Wave Number": 8, "Wave Name": "SqrLeadWave"},
    {"Category": "Lead & Synth Waves", "Wave Number": 9, "Wave Name": "SqrLeadWave+"},
    {"Category": "Lead & Synth Waves", "Wave Number": 10, "Wave Name": "FeedbackWave"},
    {"Category": "Lead & Synth Waves", "Wave Number": 11, "Wave Name": "Bad Axe"},
    {"Category": "Lead & Synth Waves", "Wave Number": 12, "Wave Name": "Cutting Lead"},
    {"Category": "Lead & Synth Waves", "Wave Number": 13, "Wave Name": "DistTB Sqr"},
    {"Category": "Lead & Synth Waves", "Wave Number": 14, "Wave Name": "Sync Sweep"},
    {"Category": "Lead & Synth Waves", "Wave Number": 15, "Wave Name": "Saw Sync"},
    {"Category": "Lead & Synth Waves", "Wave Number": 16, "Wave Name": "Unison Sync+"},
    {"Category": "Lead & Synth Waves", "Wave Number": 17, "Wave Name": "Sync Wave"},
    {"Category": "Lead & Synth Waves", "Wave Number": 18, "Wave Name": "Cutters"},
    {"Category": "Lead & Synth Waves", "Wave Number": 19, "Wave Name": "Nasty"},
    {"Category": "Lead & Synth Waves", "Wave Number": 20, "Wave Name": "Bagpipe Wave"},
    {"Category": "Lead & Synth Waves", "Wave Number": 21, "Wave Name": "Wave Scan"},
    {"Category": "Lead & Synth Waves", "Wave Number": 22, "Wave Name": "Wire String"},
    {"Category": "Lead & Synth Waves", "Wave Number": 23, "Wave Name": "Lead Wave 3"},
    {"Category": "Lead & Synth Waves", "Wave Number": 28, "Wave Name": "Wobble Bs 1"},
    {"Category": "Lead & Synth Waves", "Wave Number": 29, "Wave Name": "Wobble Bs 2"},
    {"Category": "Bass Waves", "Wave Number": 30, "Wave Name": "Hollow Bass"},
    {"Category": "Bass Waves", "Wave Number": 31, "Wave Name": "SynBs Wave"},
    {"Category": "Bass Waves", "Wave Number": 32, "Wave Name": "Solid Bass"},
    {"Category": "Bass Waves", "Wave Number": 33, "Wave Name": "House Bass"},
    {"Category": "Bass Waves", "Wave Number": 34, "Wave Name": "4OP FM Bass"},
    {"Category": "Bass Waves", "Wave Number": 35, "Wave Name": "Fine Wine"},
    {
        "Category": "Bell & Metallic Tones",
        "Wave Number": 36,
        "Wave Name": "Bell Wave 1",
    },
    {
        "Category": "Bell & Metallic Tones",
        "Wave Number": 37,
        "Wave Name": "Bell Wave 1+",
    },
    {
        "Category": "Bell & Metallic Tones",
        "Wave Number": 38,
        "Wave Name": "Bell Wave 2",
    },
    {
        "Category": "Bell & Metallic Tones",
        "Wave Number": 39,
        "Wave Name": "Digi Wave 1",
    },
    {
        "Category": "Bell & Metallic Tones",
        "Wave Number": 40,
        "Wave Name": "Digi Wave 2",
    },
    {"Category": "Bell & Metallic Tones", "Wave Number": 41, "Wave Name": "Org Bell"},
    {"Category": "Bell & Metallic Tones", "Wave Number": 42, "Wave Name": "Gamelan"},
    {"Category": "Bell & Metallic Tones", "Wave Number": 43, "Wave Name": "Crystal"},
    {
        "Category": "Bell & Metallic Tones",
        "Wave Number": 44,
        "Wave Name": "Finger Bell",
    },
    {
        "Category": "Formant & Vocal Waves",
        "Wave Number": 45,
        "Wave Name": "DipthongWave",
    },
    {
        "Category": "Formant & Vocal Waves",
        "Wave Number": 46,
        "Wave Name": "DipthongWv +",
    },
    {
        "Category": "Formant & Vocal Waves",
        "Wave Number": 47,
        "Wave Name": "Hollo Wave1",
    },
    {
        "Category": "Formant & Vocal Waves",
        "Wave Number": 48,
        "Wave Name": "Hollo Wave2",
    },
    {
        "Category": "Formant & Vocal Waves",
        "Wave Number": 49,
        "Wave Name": "Hollo Wave2+",
    },
    {
        "Category": "Formant & Vocal Waves",
        "Wave Number": 50,
        "Wave Name": "Heaven Wave",
    },
    {"Category": "Formant & Vocal Waves", "Wave Number": 51, "Wave Name": "Doo"},
    {"Category": "Formant & Vocal Waves", "Wave Number": 52, "Wave Name": "MMM Vox"},
    {
        "Category": "Formant & Vocal Waves",
        "Wave Number": 53,
        "Wave Name": "Eeh Formant",
    },
    {
        "Category": "Formant & Vocal Waves",
        "Wave Number": 54,
        "Wave Name": "Iih Formant",
    },
    {"Category": "Formant & Vocal Waves", "Wave Number": 55, "Wave Name": "Syn Vox 1"},
    {"Category": "Formant & Vocal Waves", "Wave Number": 56, "Wave Name": "Syn Vox 2"},
    {"Category": "Formant & Vocal Waves", "Wave Number": 57, "Wave Name": "Org Vox"},
    {"Category": "Formant & Vocal Waves", "Wave Number": 58, "Wave Name": "Male Ooh"},
    {
        "Category": "Formant & Vocal Waves",
        "Wave Number": 59,
        "Wave Name": "LargeChrF 1",
    },
    {
        "Category": "Formant & Vocal Waves",
        "Wave Number": 60,
        "Wave Name": "LargeChrF 2",
    },
    {
        "Category": "Formant & Vocal Waves",
        "Wave Number": 61,
        "Wave Name": "Female Oohs",
    },
    {
        "Category": "Formant & Vocal Waves",
        "Wave Number": 62,
        "Wave Name": "Female Aahs",
    },
    {
        "Category": "Pads & Atmospheric Sounds",
        "Wave Number": 63,
        "Wave Name": "Atmospheric",
    },
    {
        "Category": "Pads & Atmospheric Sounds",
        "Wave Number": 64,
        "Wave Name": "Air Pad 1",
    },
    {
        "Category": "Pads & Atmospheric Sounds",
        "Wave Number": 65,
        "Wave Name": "Air Pad 2",
    },
    {
        "Category": "Pads & Atmospheric Sounds",
        "Wave Number": 66,
        "Wave Name": "Air Pad 3",
    },
    {
        "Category": "Pads & Atmospheric Sounds",
        "Wave Number": 67,
        "Wave Name": "VP-330 Choir",
    },
    {
        "Category": "Pads & Atmospheric Sounds",
        "Wave Number": 68,
        "Wave Name": "SynStrings 1",
    },
    {
        "Category": "Pads & Atmospheric Sounds",
        "Wave Number": 69,
        "Wave Name": "SynStrings 2",
    },
    {
        "Category": "Pads & Atmospheric Sounds",
        "Wave Number": 70,
        "Wave Name": "SynStrings 3",
    },
    {
        "Category": "Pads & Atmospheric Sounds",
        "Wave Number": 71,
        "Wave Name": "SynStrings 4",
    },
    {
        "Category": "Pads & Atmospheric Sounds",
        "Wave Number": 72,
        "Wave Name": "SynStrings 5",
    },
    {
        "Category": "Pads & Atmospheric Sounds",
        "Wave Number": 73,
        "Wave Name": "SynStrings 6",
    },
    {
        "Category": "Pads & Atmospheric Sounds",
        "Wave Number": 74,
        "Wave Name": "Revalation",
    },
    {
        "Category": "Pads & Atmospheric Sounds",
        "Wave Number": 75,
        "Wave Name": "Alan's Pad",
    },
    {
        "Category": "Pads & Atmospheric Sounds",
        "Wave Number": 76,
        "Wave Name": "LFO Poly",
    },
    {
        "Category": "Pads & Atmospheric Sounds",
        "Wave Number": 77,
        "Wave Name": "Boreal Pad L",
    },
    {
        "Category": "Pads & Atmospheric Sounds",
        "Wave Number": 78,
        "Wave Name": "Boreal Pad R",
    },
    {
        "Category": "Pads & Atmospheric Sounds",
        "Wave Number": 79,
        "Wave Name": "HPF Pad L",
    },
    {
        "Category": "Pads & Atmospheric Sounds",
        "Wave Number": 80,
        "Wave Name": "HPF Pad R",
    },
    {
        "Category": "Pads & Atmospheric Sounds",
        "Wave Number": 81,
        "Wave Name": "Sweep Pad",
    },
    {
        "Category": "Pads & Atmospheric Sounds",
        "Wave Number": 82,
        "Wave Name": "Chubby Ld",
    },
    {
        "Category": "Pads & Atmospheric Sounds",
        "Wave Number": 83,
        "Wave Name": "Fantasy Pad",
    },
    {
        "Category": "Pads & Atmospheric Sounds",
        "Wave Number": 84,
        "Wave Name": "Legend Pad",
    },
    {
        "Category": "Pads & Atmospheric Sounds",
        "Wave Number": 85,
        "Wave Name": "D-50 Stack",
    },
    {
        "Category": "Pads & Atmospheric Sounds",
        "Wave Number": 86,
        "Wave Name": "ChrdOfCnadaL",
    },
    {
        "Category": "Pads & Atmospheric Sounds",
        "Wave Number": 87,
        "Wave Name": "ChrdOfCnadaR",
    },
    {
        "Category": "Pads & Atmospheric Sounds",
        "Wave Number": 88,
        "Wave Name": "Fireflies",
    },
    {
        "Category": "Pads & Atmospheric Sounds",
        "Wave Number": 89,
        "Wave Name": "JazzyBubbles",
    },
    {"Category": "FX & Noise", "Wave Number": 90, "Wave Name": "SynthFx 1"},
    {"Category": "FX & Noise", "Wave Number": 91, "Wave Name": "SynthFx 2"},
    {"Category": "FX & Noise", "Wave Number": 92, "Wave Name": "X-Mod Wave 1"},
    {"Category": "FX & Noise", "Wave Number": 93, "Wave Name": "X-Mod Wave 2"},
    {"Category": "FX & Noise", "Wave Number": 94, "Wave Name": "SynVox Noise"},
    {"Category": "FX & Noise", "Wave Number": 95, "Wave Name": "Dentist Nz"},
    {"Category": "FX & Noise", "Wave Number": 96, "Wave Name": "Atmosphere"},
    {
        "Category": "Hits & Percussive Sounds",
        "Wave Number": 97,
        "Wave Name": "Anklungs",
    },
    {
        "Category": "Hits & Percussive Sounds",
        "Wave Number": 98,
        "Wave Name": "Xylo Seq",
    },
    {
        "Category": "Hits & Percussive Sounds",
        "Wave Number": 99,
        "Wave Name": "O'Skool Hit",
    },
    {
        "Category": "Hits & Percussive Sounds",
        "Wave Number": 100,
        "Wave Name": "Orch. Hit",
    },
    {
        "Category": "Hits & Percussive Sounds",
        "Wave Number": 101,
        "Wave Name": "Punch Hit",
    },
    {
        "Category": "Hits & Percussive Sounds",
        "Wave Number": 102,
        "Wave Name": "Philly Hit",
    },
    {
        "Category": "Hits & Percussive Sounds",
        "Wave Number": 103,
        "Wave Name": "ClassicHseHt",
    },
    {
        "Category": "Hits & Percussive Sounds",
        "Wave Number": 104,
        "Wave Name": "Tao Hit",
    },
    {
        "Category": "Hits & Percussive Sounds",
        "Wave Number": 105,
        "Wave Name": "Smear Hit",
    },
    {"Category": "Drum & Kick Waves", "Wave Number": 106, "Wave Name": "808 Kick 1Lp"},
    {"Category": "Drum & Kick Waves", "Wave Number": 107, "Wave Name": "808 Kick 2Lp"},
    {"Category": "Drum & Kick Waves", "Wave Number": 108, "Wave Name": "909 Kick Lp"},
    {"Category": "Keyboard & Organ Waves", "Wave Number": 109, "Wave Name": "JD Piano"},
    {"Category": "Keyboard & Organ Waves", "Wave Number": 110, "Wave Name": "E.Grand"},
    {"Category": "Keyboard & Organ Waves", "Wave Number": 111, "Wave Name": "Stage EP"},
    {"Category": "Keyboard & Organ Waves", "Wave Number": 112, "Wave Name": "Wurly"},
    {"Category": "Keyboard & Organ Waves", "Wave Number": 113, "Wave Name": "EP Hard"},
    {"Category": "Keyboard & Organ Waves", "Wave Number": 114, "Wave Name": "FM EP 1"},
    {"Category": "Keyboard & Organ Waves", "Wave Number": 115, "Wave Name": "FM EP 2"},
    {"Category": "Keyboard & Organ Waves", "Wave Number": 116, "Wave Name": "FM EP 3"},
    {
        "Category": "Keyboard & Organ Waves",
        "Wave Number": 117,
        "Wave Name": "Harpsi Wave",
    },
    {
        "Category": "Keyboard & Organ Waves",
        "Wave Number": 118,
        "Wave Name": "Clav Wave 1",
    },
    {
        "Category": "Keyboard & Organ Waves",
        "Wave Number": 119,
        "Wave Name": "Clav Wave 2",
    },
    {
        "Category": "Keyboard & Organ Waves",
        "Wave Number": 120,
        "Wave Name": "Vibe Wave",
    },
    {
        "Category": "Keyboard & Organ Waves",
        "Wave Number": 121,
        "Wave Name": "Organ Wave 1",
    },
    {
        "Category": "Keyboard & Organ Waves",
        "Wave Number": 122,
        "Wave Name": "Organ Wave 2",
    },
    {
        "Category": "Keyboard & Organ Waves",
        "Wave Number": 123,
        "Wave Name": "PercOrgan 1",
    },
    {
        "Category": "Keyboard & Organ Waves",
        "Wave Number": 124,
        "Wave Name": "PercOrgan 2",
    },
    {
        "Category": "Keyboard & Organ Waves",
        "Wave Number": 125,
        "Wave Name": "Vint.Organ",
    },
    {
        "Category": "Keyboard & Organ Waves",
        "Wave Number": 126,
        "Wave Name": "Harmonica",
    },
    {
        "Category": "Guitar & Plucked Waves",
        "Wave Number": 127,
        "Wave Name": "Ac. Guitar",
    },
    {
        "Category": "Guitar & Plucked Waves",
        "Wave Number": 128,
        "Wave Name": "Nylon Gtr",
    },
    {
        "Category": "Guitar & Plucked Waves",
        "Wave Number": 129,
        "Wave Name": "Brt Strat",
    },
    {
        "Category": "Guitar & Plucked Waves",
        "Wave Number": 130,
        "Wave Name": "Funk Guitar",
    },
    {
        "Category": "Guitar & Plucked Waves",
        "Wave Number": 131,
        "Wave Name": "Jazz Guitar",
    },
    {
        "Category": "Guitar & Plucked Waves",
        "Wave Number": 132,
        "Wave Name": "Dist Guitar",
    },
    {
        "Category": "Guitar & Plucked Waves",
        "Wave Number": 133,
        "Wave Name": "D.Mute Gtr",
    },
    {
        "Category": "Bass Waves (Acoustic & Electric)",
        "Wave Number": 134,
        "Wave Name": "FatAc. Bass",
    },
    {
        "Category": "Bass Waves (Acoustic & Electric)",
        "Wave Number": 135,
        "Wave Name": "Fingerd Bass",
    },
    {
        "Category": "Bass Waves (Acoustic & Electric)",
        "Wave Number": 136,
        "Wave Name": "Picked Bass",
    },
    {
        "Category": "Bass Waves (Acoustic & Electric)",
        "Wave Number": 137,
        "Wave Name": "Fretless Bs",
    },
    {
        "Category": "Bass Waves (Acoustic & Electric)",
        "Wave Number": 138,
        "Wave Name": "Slap Bass",
    },
    {"Category": "Strings & Orchestral", "Wave Number": 139, "Wave Name": "Strings 1"},
    {"Category": "Strings & Orchestral", "Wave Number": 140, "Wave Name": "Strings 2"},
    {
        "Category": "Strings & Orchestral",
        "Wave Number": 141,
        "Wave Name": "Strings 3 L",
    },
    {
        "Category": "Strings & Orchestral",
        "Wave Number": 142,
        "Wave Name": "Strings 3 R",
    },
    {"Category": "Strings & Orchestral", "Wave Number": 143, "Wave Name": "Pizzagogo"},
    {"Category": "Strings & Orchestral", "Wave Number": 144, "Wave Name": "Harp Harm"},
    {"Category": "Strings & Orchestral", "Wave Number": 145, "Wave Name": "Harp Wave"},
    {"Category": "Brass & Winds", "Wave Number": 146, "Wave Name": "PopBrsAtk"},
    {"Category": "Brass & Winds", "Wave Number": 147, "Wave Name": "PopBrass"},
    {"Category": "Brass & Winds", "Wave Number": 148, "Wave Name": "Tp Section"},
    {"Category": "Brass & Winds", "Wave Number": 149, "Wave Name": "Studio Tp"},
    {"Category": "Brass & Winds", "Wave Number": 150, "Wave Name": "Tp Vib Mari"},
    {"Category": "Brass & Winds", "Wave Number": 151, "Wave Name": "Tp Hrmn Mt"},
    {"Category": "Brass & Winds", "Wave Number": 152, "Wave Name": "FM Brass"},
    {"Category": "Brass & Winds", "Wave Number": 153, "Wave Name": "Trombone"},
    {"Category": "Brass & Winds", "Wave Number": 154, "Wave Name": "Wide Sax"},
    {
        "Category": "Flutes & Ethnic Instruments",
        "Wave Number": 155,
        "Wave Name": "Flute Wave",
    },
    {
        "Category": "Flutes & Ethnic Instruments",
        "Wave Number": 156,
        "Wave Name": "Flute Push",
    },
    {
        "Category": "Flutes & Ethnic Instruments",
        "Wave Number": 157,
        "Wave Name": "E.Sitar",
    },
    {
        "Category": "Flutes & Ethnic Instruments",
        "Wave Number": 158,
        "Wave Name": "Sitar Drone",
    },
    {
        "Category": "Flutes & Ethnic Instruments",
        "Wave Number": 159,
        "Wave Name": "Agogo",
    },
    {
        "Category": "Flutes & Ethnic Instruments",
        "Wave Number": 160,
        "Wave Name": "Steel Drums",
    },
]

# Create a StringIO object from the CSV string
# sv_buffer = StringIO(PCM_WAVES_CATEGORIZED)

# Read the CSV data using pandas
# pcm_df = pd.read_csv(csv_buffer)

# Convert to JSON
# pcm_json = pcm_df.to_json(orient="records")

# print(pcm_json)
# with open("pcm_waves.json", "w") as f:
#    f.write(pcm_json)
