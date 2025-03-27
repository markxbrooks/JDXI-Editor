from dataclasses import dataclass

from jdxi_editor.midi.data.constants.sysex import DT1_COMMAND_12, PROGRAM_AREA
from jdxi_editor.midi.message.roland import RolandSysEx


@dataclass
class ZoneMessage(RolandSysEx):
    """Program Zone parameter message"""

    command: int = DT1_COMMAND_12
    area: int = PROGRAM_AREA
    section: int = 0x01  # Zone section
