# cd /Users/brooks/projects/JDXI-Editor && uv run python -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
msgs = ["F0 41 10 00 00 00 0E 11 18 00 00 00 00 00 00 40 28 F7",
        "F0 41 10 00 00 00 0E 11 18 00 00 00 00 00 00 40 28 F7",
        'F0 41 10 00 00 00 0E 12 18 00 00 00 55 6E 6C 65 61 73 68 20 58 69 20 20 20 20 20 20 7F 03 06 0B 00 00 00 01 01 01 01 00 00 00 00 00 09 00 00 09 4E F7',
        'F0 41 10 00 00 00 0E 11 18 01 00 00 00 00 00 18 4F F7',
        "F0 41 10 00 00 00 0E 11 18 01 00 00 00 00 00 18 4F F7"
        ]
for msg_hex in msgs:
    msg = bytes.fromhex(msg_hex.replace(' ', ''))
    from jdxi_editor.midi.sysex.parser.sysex import JDXiSysExParser

    parser = JDXiSysExParser()
    parser.from_bytes(msg)
    result = parser.parse()
    import json

    print(json.dumps(result, indent=2, default=str))
""" 2>/dev/null || python3 -c """
"""# Fallback without uv
msg_hex = 'F0 41 10 00 00 00 0E 12 18 00 00 00 55 6E 6C 65 61 73 68 20 58 69 20 20 20 20 20 20 7F 03 06 0B 00 00 00 01 01 01 01 00 00 00 00 00 09 00 00 09 4E F7'
msg = bytes.fromhex(msg_hex.replace(' ', ''))
# Manual parse
print('=== Manual Parse ===')
print('Header:', msg[:7].hex(' '))
print('Command:', hex(msg[7]), '(0x12 = DT1 Data Set)')
print('Address:', msg[8:12].hex(' '), '(18 00 00 00 = TEMPORARY_PROGRAM COMMON)')
data = msg[12:-2]
cs = msg[-2]
print('Data length:', len(data))
print('TONE_NAME (0x00-0x0B):', bytes(data[0:12]).decode('ascii', errors='replace'), '=', [hex(b) for b in data[0:12]])
print('Offset 0x0C-0x15:', [hex(b) for b in data[12:22]])
print('Offset 0x16 PROGRAM_LEVEL:', data[0x16], '(0-127)')
print('Offset 0x17-0x1A PROGRAM_TEMPO (4-byte):', [hex(b) for b in data[0x17:0x1B]], '=', int.from_bytes(data[0x17:0x1B], 'big'))
print('Offset 0x1B VOCAL_EFFECT_NUMBER:', data[0x1B])
print('Offset 0x1C VOCAL_EFFECT:', data[0x1C], '(0=OFF,1=VOCODER,2=AUTO-PITCH)')
print('Offset 0x1D VOCAL_EFFECT_PART:', data[0x1D])
print('Offset 0x1E AUTO_NOTE_SWITCH:', data[0x1E])
print('Checksum:', hex(cs))"""
