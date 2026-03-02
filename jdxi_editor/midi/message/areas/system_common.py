"""
SystemCommonMessage
===================

# Example usage:
# Set master tune to +50 cents
>>> from jdxi_editor.midi.data.parameter.system.common import SystemCommonParam
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

from picomidi.constant import Midi
from picomidi.utils.conversion import split_16bit_value_to_nibbles

from jdxi_editor.midi.data.address.address import (
    CommandID,
    JDXiSysExAddressStartMSB,
    JDXiSysExOffsetProgramLMB,
)
from jdxi_editor.midi.message.roland import JDXiSysEx


@dataclass
class SystemCommonMessage(JDXiSysEx):
    """System Common parameter message"""

    command: int = CommandID.DT1
    msb: int = JDXiSysExAddressStartMSB.SETUP  # 0x02: System area (02 00 00 00)
    umb: int = JDXiSysExOffsetProgramLMB.COMMON  # 0x00: Common section
    lmb: int = Midi.value.ZERO  # Always 0x00
    lsb: int = Midi.value.ZERO  # Parameter number
    value: int = Midi.value.ZERO  # Parameter value

    def __post_init__(self):
        # Master Tune (0x00) uses 4-byte encoding (nibbles) for values 24-2024
        # Convert value to nibbles BEFORE calling super() to avoid validation errors
        # Extract the actual address byte from lsb (handle tuple, enum, or int)
        if isinstance(self.lsb, tuple) and len(self.lsb) > 0:
            lsb_addr = self.lsb[0]  # AddressParameter tuple: (address, min, max)
        elif hasattr(self.lsb, "address"):
            lsb_addr = self.lsb.address
        else:
            lsb_addr = self.lsb

        if lsb_addr == 0x00 and isinstance(self.value, int):  # MASTER_TUNE parameter
            # Convert 16-bit value to 4 nibbles (4-bit values, 0-15 each)
            self.data = split_16bit_value_to_nibbles(self.value)
            self.size = 4

        # Call parent __post_init__ which will validate the message structure
        super().__post_init__()  # Set address and data from RolandSysEx
