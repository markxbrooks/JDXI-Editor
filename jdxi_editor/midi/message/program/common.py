from dataclasses import dataclass

from jdxi_editor.midi.data.address.address import CommandID, AddressMemoryAreaMSB, AddressOffsetSystemLMB, \
    AddressOffsetProgramLMB, AddressOffsetSystemUMB
from jdxi_editor.midi.data.address.sysex import ZERO_BYTE
from jdxi_editor.midi.message.roland import RolandSysEx


@dataclass
class ProgramCommonParameterMessage(RolandSysEx):
    """Program Common parameter message"""

    command: int = CommandID.DT1
    msb: int = AddressMemoryAreaMSB.PROGRAM  # 0x18: Program area
    umb: int = AddressOffsetSystemUMB.COMMON  # 0x00: Common section
    lmb: int = AddressOffsetSystemLMB.COMMON  # Always 0x00
    lsb: int = ZERO_BYTE  # Parameter number
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
