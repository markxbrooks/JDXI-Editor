"""
SystemCommonMessage
===================

# Example usage:
# Set master tune to +50 cents
>>> msg = SystemCommonMessage(
...     lsb=SystemCommonParam.MASTER_TUNE.value,
...     value=1024 + (50 * 10),  # Convert +50.0 cents to 1524
... )

# Set master key shift to -12 semitones
>>> msg = SystemCommonMessage(
...     lsb=SystemCommonParam.MASTER_KEY_SHIFT.value, value=52  # Convert -12 to 52 (64-12)
... )

# Set program control channel to 1
>>> msg = SystemCommonMessage(
...     lsb=SystemCommonParam.PROGRAM_CTRL_CH.value, value=1  # Channel 1
... )

# Enable program change reception
>>> msg = SystemCommonMessage(lsb=SystemCommonParam.RX_PROGRAM_CHANGE.value, value=1)  # ON
"""

from dataclasses import dataclass

from jdxi_editor.midi.data.parameter.system.common import SystemCommonParam
from picomidi.constant import Midi

from jdxi_editor.midi.data.address.address import (
    AddressOffsetProgramLMB,
    AddressStartMSB,
    CommandID,
)
from jdxi_editor.midi.message.roland import RolandSysEx


@dataclass
class SystemCommonMessage(RolandSysEx):
    """System Common parameter message"""

    command: int = CommandID.DT1
    msb: int = AddressStartMSB.SYSTEM  # 0x02: System area
    umb: int = AddressOffsetProgramLMB.COMMON  # 0x00: Common section
    lmb: int = Midi.VALUE.ZERO  # Always 0x00
    lsb: int = Midi.VALUE.ZERO  # Parameter number
    value: int = Midi.VALUE.ZERO  # Parameter value

    def __post_init__(self):
        super().__post_init__()  # Set address and data from RolandSysEx
