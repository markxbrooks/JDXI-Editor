"""
ReverbMessage
=============

# Example usage:
# Set reverb level
msg = ReverbMessage(param=Reverb.LEVEL.value, value=100)  # Level 100

# Set reverb parameter 1 to +5000
msg = ReverbMessage(
    param=Reverb.get_param_offset(1), value=5000  # Will be converted to 37768
)

"""

from dataclasses import dataclass

from jdxi_editor.midi.data.address.address import CommandID, MemoryAreaAddress
from jdxi_editor.midi.message.roland import RolandSysEx


@dataclass
class ReverbMessage(RolandSysEx):
    """Program Reverb parameter message"""

    command: int = CommandID.DT1
    area: int = MemoryAreaAddress.PROGRAM  # 0x18: Program area
    section: int = ProgramParameter.REVERB  # 0x08: Reverb section
    group: int = 0x00  # Always 0x00
    param: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        """Set up address and data"""
        self.address = [
            self.address_msb,  # Program area (0x18)
            self.section,  # Reverb section (0x08)
            self.group,  # Always 0x00
            self.param,  # Parameter number
        ]
        # Handle 4-byte parameters
        if 0x03 <= self.param <= 0x5F:
            # Convert -20000/+20000 to 12768-52768
            value = self.value + 32768
            self.data = [
                (value >> 24) & 0x0F,  # High nibble
                (value >> 16) & 0x0F,
                (value >> 8) & 0x0F,
                value & 0x0F,  # Low nibble
            ]
        else:
            self.data = [self.value]
