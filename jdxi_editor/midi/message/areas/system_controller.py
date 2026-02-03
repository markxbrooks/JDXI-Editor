"""
SystemControllerMessage
=======================
# Example usage:
# Enable program change transmission
>>> msg = SystemControllerMessage(
>>>     param=SystemController.TX_PROGRAM_CHANGE.STATUS, value=1  # ON
>>> )

# Set keyboard velocity to REAL
>>> msg = SystemControllerMessage(
>>>     param=SystemController.KEYBOARD_VELOCITY.STATUS, value=0  # REAL
>>> )

# Set velocity curve to MEDIUM
>>> msg = SystemControllerMessage(
>>>     param=SystemController.VELOCITY_CURVE.STATUS, value=1  # MEDIUM
>>> )

# Set velocity offset to +5
>>> msg = SystemControllerMessage(
>>>     param=SystemController.VELOCITY_OFFSET.STATUS, value=69  # Convert +5 to 69 (64+5)
>>> )
"""

from dataclasses import dataclass

from jdxi_editor.midi.data.address.address import (
    CommandID,
    JDXiSysExAddressStartMSB,
    JDXiSysExOffsetSystemLMB,
    JDXiSysExOffsetTemporaryToneUMB,
)
from jdxi_editor.midi.data.address.sysex import ZERO_BYTE
from jdxi_editor.midi.message.roland import JDXiSysEx


@dataclass
class SystemControllerMessage(JDXiSysEx):
    """System Controller parameter message"""

    command: int = CommandID.DT1
    msb: int = JDXiSysExAddressStartMSB.SETUP  # 0x02: Setup area
    umb: int = JDXiSysExOffsetTemporaryToneUMB.COMMON  # 0x03: Controller section
    lmb: int = JDXiSysExOffsetSystemLMB.CONTROLLER  # Always 0x00
    lsb: int = ZERO_BYTE  # Parameter number
    value: int = ZERO_BYTE  # Parameter value

    def __post_init__(self):
        super().__post_init__()  # Set address and data from RolandSysEx
