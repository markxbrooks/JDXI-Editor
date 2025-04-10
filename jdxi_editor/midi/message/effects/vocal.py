"""
VocalEffectMessage
==================

# Example usage:
# Set vocal effect level
msg = VocalEffectMessage(param=VocalEffect.LEVEL.value, value=100)  # Level 100

# Set auto pitch parameters
msg = VocalEffectMessage(param=VocalEffect.AUTO_PITCH_SW.value, value=1)  # ON

msg = VocalEffectMessage(param=VocalEffect.AUTO_PITCH_TYPE.value, value=0)  # SOFT

# Set vocoder parameters
msg = VocalEffectMessage(param=VocalEffect.VOCODER_SW.value, value=1)  # ON

msg = VocalEffectMessage(param=VocalEffect.VOCODER_ENV.value, value=1)  # SOFT
"""


from dataclasses import dataclass

from jdxi_editor.midi.data.address.address import CommandID, MemoryAreaAddress
from jdxi_editor.midi.message.roland import RolandSysEx


@dataclass
class VocalEffectMessage(RolandSysEx):
    """Program Vocal Effect parameter message"""

    command: int = CommandID.DT1
    area: int = MemoryAreaAddress.PROGRAM  # 0x18: Program area
    section: int = 0x01  # 0x01: Vocal Effect section
    group: int = 0x00  # Always 0x00
    param: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        """Set up address and data"""
        self.address = [
            self.area,  # Program area (0x18)
            self.section,  # Vocal Effect section (0x01)
            self.group,  # Always 0x00
            self.param,  # Parameter number
        ]
        self.data = [self.value]
