"""
DrumKitMessage
==============

# Example usage:
# Set kit name
msg = DrumKitMessage(
    section=DrumKitSection.COMMON.value,
    param=DrumKitCommon.NAME_1.value,
    value=0x41,  # 'A'
)

# Set pad parameter
msg = DrumKitMessage(
    section=DrumKitSection.get_pad_offset(36),  # Pad C1
    param=DrumPadParam.WAVE.value,
    value=1,  # Wave number
)
"""

from dataclasses import dataclass

from jdxi_editor.midi.data.address.address import CommandID
from jdxi_editor.midi.message.roland import RolandSysEx


@dataclass
class DrumKitMessage(RolandSysEx):
    """Drum Kit parameter message"""

    command: int = CommandID.DT1
    area: int = ProgramAreaParameter.TEMPORARY_TONE  # Temporary area
    tone_type: int = TemporaryParameter.DRUM_KIT_PART  # Drum Kit
    section: int = 0x00  # Section (Common or Pad offset)
    param: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        """Set up address and data"""
        self.address = [
            self.area,  # Temporary area (0x19)
            self.tone_type,  # Drum Kit (0x10)
            self.section,  # Section (Common/Pad offset)
            self.param,  # Parameter number
        ]
        self.data = [self.value]
