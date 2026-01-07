from picomidi.constant import MidiConstant
from jdxi_editor.midi.data.address.address import RolandSysExAddress, AddressStartMSB


class ProgramCommonAddress(RolandSysExAddress):
    """
    A convenient subclass for the standard "Program Common" address in Roland SysEx messages.
    """

    def __init__(self,
                 msb: int = AddressStartMSB.TEMPORARY_PROGRAM,
                 umb: int = MidiConstant.ZERO_BYTE,
                 lmb: int = MidiConstant.ZERO_BYTE,
                 lsb: int = MidiConstant.ZERO_BYTE):
        super().__init__(msb, umb, lmb, lsb)