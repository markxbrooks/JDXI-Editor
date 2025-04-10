"""
SystemCommonMessage
===================

# Example usage:
# Set master tune to +50 cents
msg = SystemCommonMessage(
    param=SystemCommon.MASTER_TUNE.value,
    value=1024 + (50 * 10),  # Convert +50.0 cents to 1524
)

# Set master key shift to -12 semitones
msg = SystemCommonMessage(
    param=SystemCommon.MASTER_KEY_SHIFT.value, value=52  # Convert -12 to 52 (64-12)
)

# Set program control channel to 1
msg = SystemCommonMessage(
    param=SystemCommon.PROGRAM_CTRL_CH.value, value=1  # Channel 1
)

# Enable program change reception
msg = SystemCommonMessage(param=SystemCommon.RX_PROGRAM_CHANGE.value, value=1)  # ON
"""

from dataclasses import dataclass

from jdxi_editor.midi.data.address.address import CommandID, MemoryAreaAddress, ProgramAddressGroup
from jdxi_editor.midi.message.roland import RolandSysEx


@dataclass
class SystemCommonMessage(RolandSysEx):
    """System Common parameter message"""

    command: int = CommandID.DT1
    area: int = MemoryAreaAddress.SYSTEM  # 0x02: System area
    section: int = ProgramAddressGroup.PROGRAM_COMMON  # 0x00: Common section
    group: int = 0x00  # Always 0x00
    param: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        """Set up address and data"""
        self.address = [
            self.area,  # System area (0x02)
            self.section,  # Common section (0x00)
            self.group,  # Always 0x00
            self.param,  # Parameter number
        ]
        self.data = [self.value]
