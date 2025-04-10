"""
Arpeggiator Areas and Parts
"""


from jdxi_editor.midi.data.address.address import Address

ARP_GROUP = 0x40

class ArpeggioAddress(Address):
    TEMPORARY_PROGRAM = 0x18
    ARP_PART = 0x00
    ARP_GROUP = 0x40

# ArpeggioParameter.TEMPORARY_PROGRAM
# ArpeggioParameter.ARP_PART
# ArpeggioParameter.ARP_GROUP