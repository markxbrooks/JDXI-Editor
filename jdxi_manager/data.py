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