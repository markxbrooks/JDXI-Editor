"""
DrumKitMessage
==============

# Example usage:
# Set kit name
>>> msg = DrumKitMessage(
>>>     section=DrumKitSection.COMMON.STATUS,
>>>     param=DrumKitCommon.NAME_1.STATUS,
>>>     value=0x41,  # 'A'
>>> )

# Set pad parameter
>>> msg = DrumKitMessage(
>>>     section=DrumKitSection.get_pad_offset(36),  # Pad C1
>>>     param=DrumPadParam.WAVE_SAW.STATUS,
>>>     value=1,  # Wave number
>>> )
"""

from dataclasses import dataclass

from jdxi_editor.midi.data.address.address import (
    JDXiSysExOffsetTemporaryToneUMB,
    JDXiSysExAddressStartMSB,
    CommandID,
)
from jdxi_editor.midi.message.roland import JDXiSysEx


@dataclass
class DrumKitMessage(JDXiSysEx):
    """Drum Kit parameter message"""

    command: int = CommandID.DT1
    msb: int = JDXiSysExAddressStartMSB.TEMPORARY_TONE  # Temporary area
    umb: int = JDXiSysExOffsetTemporaryToneUMB.DRUM_KIT  # Drum Kit
    lmb: int = 0x00  # Section (Common or Pad offset)
    lsb: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        super().__post_init__()
