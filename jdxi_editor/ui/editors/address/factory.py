from jdxi_editor.midi.data.address.address import (
    JDXiSysExOffsetProgramLMB,
    JDXiSysExOffsetTemporaryToneUMB,
    JDXiSysExAddressStartMSB,
    RolandSysExAddress,
)
from jdxi_editor.midi.data.address.arpeggio import ArpeggioAddress
from jdxi_editor.midi.data.address.sysex import ZERO_BYTE


def create_vocal_fx_address():
    """Create Vocal Fx Address"""
    address = RolandSysExAddress(
        JDXiSysExAddressStartMSB.TEMPORARY_PROGRAM,
        JDXiSysExOffsetTemporaryToneUMB.COMMON,
        JDXiSysExOffsetProgramLMB.VOCAL_EFFECT,
        ZERO_BYTE,
    )
    return address


def create_arp_address():
    """Create Arp Address"""
    address = RolandSysExAddress(
        msb=ArpeggioAddress.TEMPORARY_PROGRAM,
        umb=ArpeggioAddress.ARP_PART,
        lmb=ArpeggioAddress.ARP_GROUP,
        lsb=ZERO_BYTE,
    )
    return address
