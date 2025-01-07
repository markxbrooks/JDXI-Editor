# MIDI constants
ROL_ID = b'\x41'
JDXI_ID = b'\x00\x00\x00\x0E'
DR1 = b'\x11'
DT1 = b'\x12'
Xi_header = b'\xF0' + ROL_ID + b'[\x01-\x10]' + JDXI_ID + DT1

# Digital Synth 1 data
SN1 = {
    'type': 'SN1',
    'key': ['COM', 'P1', 'P2', 'P3', 'MOD'],
    'msb': '1920',
    'addr': [b'\x19\x20\x00\x00', b'\x19\x20\x20\x00', b'\x19\x20\x21\x00', 
            b'\x19\x20\x22\x00', b'\x19\x20\x50\x00'],
    'rqlen': [b'\x00\x00\x00\x40', b'\x00\x00\x00\x3D', b'\x00\x00\x00\x3D',
             b'\x00\x00\x00\x3D', b'\x00\x00\x00\x25'],
    'MIDIch': 0,
    'name': ['SN1 Name', '\x00', '\x00', '\x00', '\x00'],
    'filename': '',
    'fnprefix': 'JDXi-SN-',
    'filetype': 'Digital Synth Tone',
    'okedext': 'ds',
    'filelen': 354,
    'modified': 0,
    'titlestr': 'JDXi Manager - Digital Synth 1 Editor',
    'window': '',
    'geometry': '1150x740'
}

# Digital Synth 2 data
SN2 = {
    'type': 'SN2',
    'key': ['COM', 'P1', 'P2', 'P3', 'MOD'],
    'msb': '1921',
    'addr': [b'\x19\x21\x00\x00', b'\x19\x21\x20\x00', b'\x19\x21\x21\x00',
            b'\x19\x21\x22\x00', b'\x19\x21\x50\x00'],
    'MIDIch': 1,
    'name': ['SN2 Name', '\x00', '\x00', '\x00', '\x00'],
    'titlestr': 'JDXi Manager - Digital Synth 2 Editor',
}

# Placeholder for other data structures
AN = {}  # Analog synth data
DR = {}  # Drums data
FX = {}  # Effects data
ARP = {} # Arpeggio data
VFX = {} # Vocal FX data 

class ARP:
    PATTERNS = [
        "Up",
        "Down",
        "Up/Down",
        "Random",
        "Note Order",
        "Up x2",
        "Down x2",
        "Up&Down"
    ]
    
    NOTE_VALUES = [
        "1/32",
        "1/16T",
        "1/16",
        "1/8T",
        "1/8",
        "1/4T",
        "1/4",
        "1/2T",
        "1/2",
        "1/1T",
        "1/1"
    ] 

class FX:
    REVERB_TYPES = [
        "Room 1",
        "Room 2",
        "Stage 1",
        "Stage 2",
        "Hall 1",
        "Hall 2"
    ]
    
    DELAY_NOTES = [
        "1/32",
        "1/16T",
        "1/16",
        "1/8T",
        "1/8",
        "1/4T",
        "1/4",
        "1/2T",
        "1/2",
        "1/1T",
        "1/1"
    ]
    
    EFFECT_TYPES = [
        "Distortion",
        "Fuzz",
        "Compressor",
        "Bit Crusher",
        "Ring Mod",
        "Slicer",
        "Auto Pan",
        "Tremolo",
        "Phaser",
        "Flanger"
    ] 

class DigitalSynth:
    # SysEx header
    HEADER = bytes([
        0xF0, 0x41,       # SysEx start, Roland ID
        0x10,             # Device ID  
        0x00, 0x00, 0x00, # Model ID
        0x0E,             # JD-Xi ID
        0x19              # Digital Synth area
    ])
    
    # Parameter addresses
    SECTIONS = {
        'OSC': {
            'base': 0x20,
            'params': {
                'WAVE': 0x00,
                'RANGE': 0x01,
                'COLOR': 0x02,
                'TUNE': 0x03
            }
        },
        'FILTER': {
            'base': 0x21,
            'params': {
                'CUTOFF': 0x00,
                'RESONANCE': 0x01,
                'KEY_FOLLOW': 0x02,
                'ENV_DEPTH': 0x03
            }
        },
        'AMP': {
            'base': 0x22,
            'params': {
                'LEVEL': 0x00,
                'PAN': 0x01,
                'VELOCITY': 0x02
            }
        },
        'LFO': {
            'base': 0x26,
            'params': {
                'WAVE': 0x00,
                'RATE': 0x01,
                'FADE': 0x02,
                'PITCH_DEPTH': 0x03,
                'FILTER_DEPTH': 0x04,
                'AMP_DEPTH': 0x05
            }
        }
    }
    
    # Parameter ranges and conversions
    PARAM_INFO = {
        ('OSC', 'RANGE'): {'min': -24, 'max': 24, 'offset': 24},
        ('FILTER', 'KEY_FOLLOW'): {'min': -64, 'max': 63, 'offset': 64},
        ('AMP', 'PAN'): {'min': -64, 'max': 63, 'offset': 64}
    } 