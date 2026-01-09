"""
MIDI and JD-Xi Constant definitions

This module provides:
- MidiConstant: Standard MIDI protocol constants (status bytes, channels, values, etc.)
- JDXiConstant: JD-Xi-specific constants (SysEx addresses, bank mappings, etc.)
"""

from picomidi import BitMask


class JDXiUI:
    """JDXi UI related constants"""
    # ============================================================================
    # JD-Xi UI Constants
    # ============================================================================
    TIMER_INTERVAL = 10
    FILTER_PLOT_DEPTH = 1.0
    CHECKED = 2


class JDXiDevice:
    # ============================================================================
    # Roland SysEx Header
    # ============================================================================
    ROLAND_ID = [
        0x41,
        0x10,
        0x00,
    ]  # Manufacturer ID, Device ID, Model ID (JD-Xi = 0x0E)
    JD_XI_MODEL_ID = 0x0E

    # SysEx Identity Request/Reply
    ID_NUMBER = 0x7E  # Non-realtime ID (0x7E) or realtime (0x7F), depending on context
    DEVICE_ID = 0x7F  # 'All Call' for all devices
    SUB_ID_1_GENERAL_INFORMATION = 0x06
    SUB_ID_2_IDENTITY_REQUEST = 0x01
    SUB_ID_2_IDENTITY_REPLY = 0x02
    

class JDXiSysExLength:
    """Sysex Length"""
    ONE_BYTE = 15
    FOUR_BYTE = 18


class JDXiSysEx:
    """ Sysex related constants"""
    LENGTH = JDXiSysExLength
    LENGTH_FOUR_BYTE_DATA = 18


class JDXiProgramChange:
    """JDXi Program change bank values"""
    BANK_A_AND_C_AND_E_AND_G = 0
    BANK_B_AND_D_AND_F_AND_H = 64


class JDXiCCBankSelect:
    """
    Represents the Bank Select values for the Roland JD-Xi synthesizer.

    # Note: JD-Xi uses CC#85 for Bank Select MSB instead of standard CC#0
    - MSB (Most Significant Byte): CC#85 (non-standard)
    - LSB (Least Significant Byte): Specific values for bank selection.
    """
    MSB = 85

    class LSB:
        """LSB values for Bank selection."""
        BANK_E_AND_F = 0
        BANK_G_AND_H = 1
        BANK_A_AND_B = 64  # ROM banks
        BANK_C_AND_D = 65  # ROM banks


class JDXiControlChange:
    """JD-Xi Bank Select LSB values
    Note: JD-Xi uses CC#85 for Bank Select MSB instead of standard CC#0"""
    BANK_SELECT = JDXiCCBankSelect
    

class JDXiMidi:
    """JD-Xi-specific MIDI and SysEx constants."""
    CC = JDXiControlChange
    PC = JDXiProgramChange
    SYSEX = JDXiSysEx
    DEVICE = JDXiDevice
    UI = JDXiUI

    OCTAVE_CENTER_VALUE = 0x40  # for octave up/down buttons
