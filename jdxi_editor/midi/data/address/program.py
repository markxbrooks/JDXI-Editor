from picomidi.constant import Midi

from jdxi_editor.midi.data.address.address import (
    JDXiSysExAddressStartMSB,
    RolandSysExAddress,
)


class ProgramCommonAddress(RolandSysExAddress):
    """
    A convenient subclass for the standard "Program Common" address in Roland SysEx messages.
    """

    def __init__(
        self,
        msb: int = JDXiSysExAddressStartMSB.TEMPORARY_PROGRAM,
        umb: int = Midi.VALUE.ZERO,
        lmb: int = Midi.VALUE.ZERO,
        lsb: int = Midi.VALUE.ZERO,
    ):
        super().__init__(msb, umb, lmb, lsb)
