from dataclasses import dataclass

from jdxi_editor.midi.data.address.address import CommandID, AddressMemoryAreaMSB, AddressOffsetSystemLMB, \
    AddressOffsetProgramLMB, ZERO_BYTE, AddressOffsetSystemUMB
from jdxi_editor.midi.message.roland import RolandSysEx


@dataclass
class ProgramCommonParameterMessage(RolandSysEx):
    """Program Common parameter message"""

    command: int = CommandID.DT1
    address_msb: int = AddressMemoryAreaMSB.PROGRAM  # 0x18: Program area
    address_umb: int = AddressOffsetSystemUMB.COMMON  # 0x00: Common section
    address_lmb: int = AddressOffsetSystemLMB.COMMON  # Always 0x00
    address_lsb: int = ZERO_BYTE  # Parameter number
    value: int = ZERO_BYTE  # Parameter value

    def __post_init__(self):
        """Set up address and data"""
        self.address = [
            self.address_msb,  # Program area (0x18)
            self.address_umb,  # Common section (0x00)
            self.address_lmb,  # Always 0x00
            self.address_lsb,  # Parameter number
        ]
        self.data = [self.value]
