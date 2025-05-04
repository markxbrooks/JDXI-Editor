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

from jdxi_editor.midi.data.address.address import AddressOffsetSystemLMB, CommandID, AddressMemoryAreaMSB, \
    AddressOffsetTemporaryToneUMB
from jdxi_editor.midi.data.address.sysex import ZERO_BYTE
from jdxi_editor.midi.message.roland import RolandSysEx


@dataclass
class SystemControllerMessage(RolandSysEx):
    """System Controller parameter message"""

    command: int = CommandID.DT1
    msb: int = AddressMemoryAreaMSB.SETUP  # 0x02: Setup area
    umb: int = AddressOffsetTemporaryToneUMB.COMMON  # 0x03: Controller section
    lmb: int = AddressOffsetSystemLMB.CONTROLLER  # Always 0x00
    lsb: int = ZERO_BYTE  # Parameter number
    value: int = ZERO_BYTE  # Parameter value

    def __post_init__(self):
        super().__post_init__()  # Set address and data from RolandSysEx
