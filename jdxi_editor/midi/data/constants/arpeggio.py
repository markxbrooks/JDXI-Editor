"""
Arpeggiator MIDI Constants Module

This module defines MIDI constants, enumerations, and utility properties
for controlling the JD-Xi's arpeggiator via MIDI. It provides:

- MIDI parameter identifiers for arpeggiator settings
- Enumerations for arpeggiator grid, duration, octave range, and switch states
- Utility properties for retrieving display names and MIDI values

Constants:
----------
- `TEMPORARY_PROGRAM` – Address for temporary program storage
- `ARP_PART` – Identifier for the arpeggiator part
- `ARP_GROUP` – MIDI group for arpeggiator parameters

Classes:
--------
- `ArpParameter` – Enumeration of arpeggiator parameter IDs
- `ArpGrid` – Enumeration of arpeggiator grid values
- `ArpDuration` – Enumeration of arpeggiator note durations
- `ArpOctaveRange` – Enumeration of arpeggiator octave range values
- `ArpSwitch` – Enumeration of arpeggiator on/off states

Each enumeration provides display names for UI representation
and corresponding MIDI values for direct communication with the synthesizer.

This module is intended for precise and structured manipulation of the
JD-Xi’s arpeggiator functionality via MIDI messages.

"""

# Areas and Parts
TEMPORARY_PROGRAM = 0x18
ARP_PART = 0x00
ARP_GROUP = 0x40
