from dataclasses import dataclass

from jdxi_editor.midi.data.address.parameter import CommandParameter, ProgramAreaParameter
from jdxi_editor.midi.message.roland import RolandSysEx


@dataclass
class ZoneMessage(RolandSysEx):
    """Program Zone parameter message"""

    command: int = CommandParameter.DT1
    area: int = ProgramAreaParameter.PROGRAM
    section: int = 0x01  # Zone section
