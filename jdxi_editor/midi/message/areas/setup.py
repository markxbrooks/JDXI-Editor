from dataclasses import dataclass

from jdxi_editor.midi.data.constants.sysex import DT1_COMMAND_12, SETUP_AREA
from jdxi_editor.midi.message.roland import RolandSysEx


@dataclass
class SetupMessage(RolandSysEx):
    """Setup parameter message"""

    command: int = DT1_COMMAND_12
    area: int = SETUP_AREA  # 0x01: Setup area
    section: int = 0x00  # Always 0x00
    group: int = 0x00  # Always 0x00
    param: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        """Set up address and data"""
        self.address = [
            self.area,  # Setup area (0x01)
            self.section,  # Always 0x00
            self.group,  # Always 0x00
            self.param,  # Parameter number
        ]
        self.data = [self.value]
