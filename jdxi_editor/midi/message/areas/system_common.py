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

from jdxi_editor.midi.data.address.address import (
    CommandID,
    AddressMemoryAreaMSB,
    AddressOffsetProgramLMB,
)
from jdxi_editor.midi.data.address.sysex import ZERO_BYTE
from jdxi_editor.midi.message.roland import RolandSysEx


@dataclass
class SystemCommonMessage(RolandSysEx):
    """System Common parameter message"""

    command: int = CommandID.DT1
    msb: int = AddressMemoryAreaMSB.SYSTEM  # 0x02: System area
    umb: int = AddressOffsetProgramLMB.TONE_COMMON  # 0x00: Common section
    lmb: int = ZERO_BYTE  # Always 0x00
    lsb: int = ZERO_BYTE  # Parameter number
    value: int = ZERO_BYTE  # Parameter value

    def __post_init__(self):
        super().__post_init__()  # Set address and data from RolandSysEx
