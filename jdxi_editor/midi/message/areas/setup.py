from dataclasses import dataclass

from jdxi_editor.midi.data.address.address import (
    CommandID,
    AddressStartMSB,
    ZERO_BYTE,
)
from jdxi_editor.midi.message.roland import RolandSysEx


@dataclass
class SetupMessage(RolandSysEx):
    """Setup parameter message"""

    command: int = CommandID.DT1
    msb: int = AddressStartMSB.SYSTEM  # 0x01: Setup area
    umb: int = ZERO_BYTE  # Always 0x00
    lmb: int = ZERO_BYTE  # Always 0x00
    lsb: int = ZERO_BYTE  # Parameter number
    value: int = ZERO_BYTE  # Parameter value

    def __post_init__(self):
        super().__post_init__()  # Set address and data from RolandSysEx
