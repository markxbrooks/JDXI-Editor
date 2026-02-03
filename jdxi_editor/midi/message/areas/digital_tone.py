"""
DigitalToneMessage
==================
# Example usage:
# Set common parameter
>>> msg = DigitalToneMessage(
...     command=CommandID.DT1,  # Digital 1
...     value=64,
... )
>>> print(msg)
DigitalToneMessage(start_of_sysex=240, manufacturer_id=<RolandID.ROLAND_ID: 65>, device_id=<RolandID.DEVICE_ID: 16>, model_id=[<ModelID.MODEL_ID_1: 0x00>, <ModelID.MODEL_ID_1: 0x00>, <ModelID.MODEL_ID_1: 0x00>, <ModelID.MODEL_ID_4: 0x0E>], command=<CommandID.DT1: 18>, address=[<AddressStartMSB.TEMPORARY_TONE: 0x19>, <AddressOffsetTemporaryToneUMB.DIGITAL_SYNTH_1: 0x01>, <AddressOffsetSuperNATURALLMB.PARTIAL_1: 0x20>, 0], data=[64], end_of_sysex=247, sysex_address=None, msb=<AddressStartMSB.TEMPORARY_TONE: 0x19>, umb=<AddressOffsetTemporaryToneUMB.DIGITAL_SYNTH_1: 0x01>, lmb=<AddressOffsetSuperNATURALLMB.PARTIAL_1: 0x20>, lsb=0, value=64, size=1, synth_type=None, part=None, dt1_command=<CommandID.DT1: 18>, rq1_command=<CommandID.RQ1: 17>)
"""

from dataclasses import dataclass

from jdxi_editor.midi.data.address.address import (
    CommandID,
    JDXiSysExAddressStartMSB,
    JDXiSysExOffsetSuperNATURALLMB,
    JDXiSysExOffsetTemporaryToneUMB,
)
from jdxi_editor.midi.message.roland import JDXiSysEx


@dataclass
class DigitalToneMessage(JDXiSysEx):
    """
    SuperNATURAL Synth Tone parameter message for JD-Xi.
    Defaults to TEMPORARY_TONE / Digital 1 / Common / Param 0x00
    """

    command: int = CommandID.DT1
    msb: int = JDXiSysExAddressStartMSB.TEMPORARY_TONE
    umb: int = JDXiSysExOffsetTemporaryToneUMB.DIGITAL_SYNTH_1  # Digital Tone 1
    lmb: int = (
        JDXiSysExOffsetSuperNATURALLMB.PARTIAL_1
    )  # Section (e.g., Common, Partial 1 etc. )
    lsb: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        super().__post_init__()  # Set address and data from RolandSysEx
