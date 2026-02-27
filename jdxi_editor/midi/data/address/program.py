from picomidi.constant import Midi

from jdxi_editor.midi.data.address.address import (
    JDXiSysExAddress,
    JDXiSysExAddressStartMSB,
)


class ProgramCommonAddress(JDXiSysExAddress):
    """
    A convenient subclass for the standard "Program Common" address in Roland SysEx messages.
    """

    def __init__(
        self,
        msb: int = JDXiSysExAddressStartMSB.TEMPORARY_PROGRAM,
        umb: int = Midi.value.ZERO,
        lmb: int = Midi.value.ZERO,
        lsb: int = Midi.value.ZERO,
    ):
        super().__init__(msb, umb, lmb, lsb)
