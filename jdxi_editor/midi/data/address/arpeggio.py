"""
Arpeggiator Areas and Parts
"""


from jdxi_editor.midi.data.address.parameter import Parameter


class ArpeggioParameter(Parameter):
    TEMPORARY_PROGRAM = 0x18
    ARP_PART = 0x00
    ARP_GROUP = 0x40
