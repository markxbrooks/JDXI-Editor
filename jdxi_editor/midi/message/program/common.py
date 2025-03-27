from dataclasses import dataclass

from jdxi_editor.midi.data.constants.sysex import DT1_COMMAND_12, PROGRAM_AREA
from jdxi_editor.midi.message.roland import RolandSysEx


@dataclass
class ProgramCommonParameterMessage(RolandSysEx):
    """Program Common parameter message"""

    command: int = DT1_COMMAND_12
    area: int = PROGRAM_AREA  # 0x18: Program area
    section: int = 0x00  # 0x00: Common section
    group: int = 0x00  # Always 0x00
    param: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        """Set up address and data"""
        self.address = [
            self.area,  # Program area (0x18)
            self.section,  # Common section (0x00)
            self.group,  # Always 0x00
            self.param,  # Parameter number
        ]
        self.data = [self.value]
