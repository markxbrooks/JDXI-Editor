"""
SystemControllerMessage
=======================
# Example usage:
# Enable program change transmission
>>> msg = SystemControllerMessage()
>>> msg.to_bytes().hex()
'f041100000000e1202000300007bf7'
>>> msg.to_list()
[240, 65, <RolandID.DEVICE_ID: 16>, 0, 0, 0, 14, <CommandID.DT1: 18>, <JDXiSysExAddressStartMSB.SETUP: 2>, <JDXiSysExOffsetTemporaryToneUMB.COMMON: 0>, <JDXiSysExOffsetSystemLMB.CONTROLLER: 3>, 0, 0, 123, 247]
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
