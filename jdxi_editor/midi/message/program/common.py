from dataclasses import dataclass

from jdxi_editor.midi.data.address.address import CommandID, MemoryAreaAddress
from jdxi_editor.midi.message.roland import RolandSysEx


@dataclass
class ProgramCommonParameterMessage(RolandSysEx):
    """Program Common parameter message"""

    command: int = CommandID.DT1
    area: int = MemoryAreaAddress.PROGRAM  # 0x18: Program area
    section: int = 0x00  # 0x00: Common section
    group: int = 0x00  # Always 0x00
    address_lsb: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        """Set up address and data"""
        self.address = [
            self.address_msb,  # Program area (0x18)
            self.section,  # Common section (0x00)
            self.group,  # Always 0x00
            self.param,  # Parameter number
        ]
        self.data = [self.value]
