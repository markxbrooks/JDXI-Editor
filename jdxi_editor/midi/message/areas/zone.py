from dataclasses import dataclass

from jdxi_editor.midi.data.address.address import CommandID, MemoryAreaAddress
from jdxi_editor.midi.message.roland import RolandSysEx


@dataclass
class ZoneMessage(RolandSysEx):
    """Program Zone parameter message"""

    command: int = CommandID.DT1
    area: int = MemoryAreaAddress.PROGRAM
    section: int = 0x01  # Zone section
