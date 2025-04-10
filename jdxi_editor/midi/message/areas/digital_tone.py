"""
DigitalToneMessage
==================
# Example usage:
# Set common parameter
msg = DigitalToneMessage(
    tone_type=TEMP_DIGITAL_TONE,  # Digital 1
    section=DigitalToneSection.COMMON.value,
    param=0x00,  # Common parameter
    value=64,
)

# Set partial parameter
msg = DigitalToneMessage(
    tone_type=TEMP_DIGITAL_TONE,  # Digital 1
    section=DigitalToneSection.PARTIAL_1.value,
    param=0x00,  # Partial parameter
    value=64,
)

# Set modify parameter
msg = DigitalToneMessage(
    tone_type=TEMP_DIGITAL_TONE,  # Digital 1
    section=DigitalToneSection.MODIFY.value,
    param=0x00,  # Modify parameter
    value=64,
)
"""

from dataclasses import dataclass

from jdxi_editor.midi.data.address.parameter import CommandParameter
from jdxi_editor.midi.message.roland import RolandSysEx


@dataclass
class DigitalToneMessage(RolandSysEx):
    """SuperNATURAL Synth Tone parameter message"""

    command: int = CommandParameter.DT1
    area: int = ProgramAreaParameter.DIGITAL_1  # Temporary area
    tone_type: int = 0x01  # Digital tone (0x01 or 0x02)
    section: int = 0x00  # Section from DigitalToneSection
    param: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        """Set up address and data"""
        self.address = [
            self.area,  # Temporary area (0x19)
            self.tone_type,  # Digital 1 or 2 (0x01/0x02)
            self.section,  # Section (Common/Partial/Modify)
            self.param,  # Parameter number
        ]
        self.data = [self.value]
