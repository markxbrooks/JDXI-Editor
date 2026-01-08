"""
Control Change MIDI message constants.
"""

from picomidi.cc.bank import BankSelect
from picomidi.cc.nrpn import NonRegisteredParameterNumber
from picomidi.cc.rpn import RegisteredParameterNumber


class ControlChange:
    """Standard MIDI Control Change controller numbers."""

    STATUS = 0xB0
    MAX_STATUS = 0xBF
    BANK = BankSelect
    RPN = RegisteredParameterNumber
    NRPN = NonRegisteredParameterNumber
