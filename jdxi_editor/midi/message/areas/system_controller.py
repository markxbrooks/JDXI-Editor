"""
SystemControllerMessage
=======================
# Example usage:
# Enable program change transmission
msg = SystemControllerMessage(
    param=SystemController.TX_PROGRAM_CHANGE.value, value=1  # ON
)

# Set keyboard velocity to REAL
msg = SystemControllerMessage(
    param=SystemController.KEYBOARD_VELOCITY.value, value=0  # REAL
)

# Set velocity curve to MEDIUM
msg = SystemControllerMessage(
    param=SystemController.VELOCITY_CURVE.value, value=1  # MEDIUM
)

# Set velocity offset to +5
msg = SystemControllerMessage(
    param=SystemController.VELOCITY_OFFSET.value, value=69  # Convert +5 to 69 (64+5)
)
"""

from dataclasses import dataclass

from jdxi_editor.midi.data.address.address import SystemAddressOffset
from jdxi_editor.midi.message.roland import RolandSysEx


@dataclass
class SystemControllerMessage(RolandSysEx):
    """System Controller parameter message"""

    command: int = CommandParameter.DT1
    area: int = ProgramAreaParameter.SETUP  # 0x02: Setup area
    section: int = SystemAddressOffset.SYSTEM_CONTROLLER  # 0x03: Controller section
    group: int = 0x00  # Always 0x00
    param: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        """Set up address and data"""
        self.address = [
            self.area,  # System area (0x02)
            self.section,  # Controller section (0x03)
            self.group,  # Always 0x00
            self.param,  # Parameter number
        ]
        self.data = [self.value]
