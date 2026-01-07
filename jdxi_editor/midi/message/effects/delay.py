"""
DelayMessage
============

# Example usage:
# Set delay level
>>> msg = DelayMessage(param=Delay.LEVEL.value, value=100)  # Level 100

# Set reverb send level
>>> msg = DelayMessage(param=Delay.REVERB_SEND.value, value=64)  # Send to reverb

# Set delay parameter 1 to +5000
>>> msg = DelayMessage(
>>>     param=Delay.get_param_offset(1), value=5000  # Will be converted to 37768
>>> )
"""

from dataclasses import dataclass

from jdxi_editor.midi.data.address.address import (
    AddressOffsetProgramLMB,
    AddressStartMSB,
    CommandID,
)
from jdxi_editor.midi.data.address.sysex import ZERO_BYTE
from jdxi_editor.midi.message.roland import RolandSysEx
from jdxi_editor.midi.utils.byte import split_16bit_value_to_nibbles


@dataclass
class DelayMessage(RolandSysEx):
    """Program Delay parameter message"""

    command: int = CommandID.DT1
    msb: int = AddressStartMSB.PROGRAM  # 0x18: Program area
    umb: int = AddressOffsetProgramLMB.DELAY  # 0x06: Delay section
    lmb: int = ZERO_BYTE
    lsb: int = ZERO_BYTE
    value: int = ZERO_BYTE

    def __post_init__(self):
        super().__post_init__()

        if not isinstance(self.value, int):
            raise TypeError("DelayMessage.value must be an integer")

        if 0x04 <= self.lsb <= 0x60:
            # Convert signed value to unsigned offset for SysEx
            offset_value = self.value + 32768
            self.data = split_16bit_value_to_nibbles(offset_value)
        else:
            self.data = [self.value]
