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

from jdxi_editor.midi.data.address.address import CommandID, AddressMemoryAreaMSB, AddressOffsetTemporaryToneUMB, \
    AddressOffsetSuperNATURALLMB
from jdxi_editor.midi.message.roland import RolandSysEx


@dataclass
class DigitalToneMessage(RolandSysEx):
    """
    SuperNATURAL Synth Tone parameter message for JD-Xi.
    Defaults to TEMPORARY_TONE / Digital 1 / Common / Param 0x00
    """
    command: int = CommandID.DT1
    msb: int = AddressMemoryAreaMSB.TEMPORARY_TONE
    umb: int = AddressOffsetTemporaryToneUMB.TEMPORARY_DIGITAL_SYNTH_1_AREA  # Digital Tone 1
    lmb: int = AddressOffsetSuperNATURALLMB.PARTIAL_1  # Section (e.g., Common, Partial 1 etc. )
    lsb: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        super().__post_init__()  # Set address and data from RolandSysEx
