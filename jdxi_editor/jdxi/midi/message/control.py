"""
JDXI Control Change values
"""

from jdxi_editor.jdxi.midi.message.bank import JDXiCCBankSelect


class JDXiControlChange:
    """JD-Xi Bank Select LSB values
    Note: JD-Xi uses CC#85 for Bank Select MSB instead of standard CC#0"""
    BANK_SELECT = JDXiCCBankSelect
