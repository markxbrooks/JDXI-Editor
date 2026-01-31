"""
ReverbMessage
=============

    Examples
    --------
# Set reverb level
>>> msg = ReverbMessage(param=Reverb.LEVEL.STATUS, value=100)  # Level 100

# Set reverb parameter 1 to +5000
>>> msg = ReverbMessage(
>>>     param=Reverb.get_param_offset(1), value=5000  # Will be converted to 37768
>>> )

"""

from dataclasses import dataclass

from picomidi.utils.conversion import split_16bit_value_to_nibbles

from jdxi_editor.midi.data import AddressParameterEffect
from jdxi_editor.midi.data.address.address import (
    AddressOffsetProgramLMB,
    AddressOffsetSystemLMB,
    AddressStartMSB,
    CommandID,
)
from jdxi_editor.midi.message.roland import JDXiSysEx


@dataclass
class ReverbMessage(JDXiSysEx):
    """Program Reverb parameter message"""

    command: int = CommandID.DT1
    msb: int = AddressStartMSB.TEMPORARY_PROGRAM  # 0x18: Program area
    umb: int = AddressOffsetSystemLMB.COMMON  # 0x00: Common section
    lmb: int = AddressOffsetProgramLMB.EFFECT_1  # Effect 1 = 0x02
    lsb: int = AddressParameterEffect.REVERB_LEVEL  # Parameter number 0x03
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        super().__post_init__()  # Set address and data from RolandSysEx
        # Handle 4-byte parameters
        if not isinstance(self.value, int):
            raise TypeError("ReverbMessage.value must be an integer")

        if 0x04 <= self.lsb <= 0x60:
            # Convert signed value to unsigned offset for SysEx
            offset_value = self.value + 32768
            self.data = split_16bit_value_to_nibbles(offset_value)
        else:
            self.data = [self.value]
