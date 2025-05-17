from dataclasses import dataclass

from jdxi_editor.midi.data.address.address import CommandID, AddressStartMSB
from jdxi_editor.midi.message.roland import RolandSysEx


@dataclass
class ZoneMessage(RolandSysEx):
    """Program Zone parameter message"""

    command: int = CommandID.DT1
    msb: int = AddressStartMSB.PROGRAM
    umb: int = 0x01  # Zone section
