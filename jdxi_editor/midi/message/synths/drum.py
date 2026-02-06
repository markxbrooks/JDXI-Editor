"""
DrumKitMessage
==============

# Example usage:
>>> msg = DrumKitMessage(
...      value=0x41,  # 'A'
... )
"""

from dataclasses import dataclass

from jdxi_editor.midi.data.address.address import (
    CommandID,
    JDXiSysExAddressStartMSB,
    JDXiSysExOffsetTemporaryToneUMB,
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
