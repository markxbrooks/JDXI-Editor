from dataclasses import dataclass

from jdxi_editor.midi.data.address.address import AddressStartMSB, CommandID
from jdxi_editor.midi.message.roland import JDXiSysEx


@dataclass
class ZoneMessage(JDXiSysEx):
    """Program Zone parameter message"""

    command: int = CommandID.DT1
    msb: int = AddressStartMSB.PROGRAM
    umb: int = 0x01  # Zone section
