"""
Vocal FX MIDI Constants
"""
from jdxi_editor.midi.data.address.address import Address


class VocalAddress(Address):
    FX_AREA = 0x18
    FX_PART = 0x00
    FX_GROUP = 0x01  # Different area from arpeggiator
