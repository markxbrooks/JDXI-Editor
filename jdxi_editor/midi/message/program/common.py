from dataclasses import dataclass

from jdxi_editor.midi.data.address.address import (
    CommandID,
    JDXiSysExAddressStartMSB,
    JDXiSysExOffsetSystemLMB,
    JDXiSysExOffsetSystemUMB,
)
from jdxi_editor.midi.data.address.sysex import ZERO_BYTE
from jdxi_editor.midi.message.roland import JDXiSysEx


@dataclass
class ProgramCommonParameterMessage(JDXiSysEx):
    """Program Common parameter message"""

    command: int = CommandID.DT1
    msb: int = JDXiSysExAddressStartMSB.PROGRAM  # 0x18: Program area
    umb: int = JDXiSysExOffsetSystemUMB.COMMON  # 0x00: Common section
    lmb: int = JDXiSysExOffsetSystemLMB.COMMON  # Always 0x00
    lsb: int = ZERO_BYTE  # Parameter number
    value: int = ZERO_BYTE  # Parameter value

    def __post_init__(self):
        """Set up address and data"""
        self.address = [
            self.msb,  # Program area (0x18)
            self.umb,  # Common section (0x00)
            self.lmb,  # Always 0x00
            self.lsb,  # Parameter number
        ]
        self.data = [self.value]
