"""
MIDI and JD-Xi Constant definitions

This module provides:
- MidiConstant: Standard MIDI protocol constants (status bytes, channels, values, etc.)
- JDXiConstant: JD-Xi-specific constants (SysEx addresses, bank mappings, etc.)
"""

from picomidi import BitMask


class JDXiConstant:
    """JD-Xi-specific MIDI and SysEx constants."""

    # ============================================================================
    # JD-Xi Bank Select (Non-Standard)
    # ============================================================================
    # Note: JD-Xi uses CC#85 for Bank Select MSB instead of standard CC#0
    CONTROL_CHANGE_BANK_SELECT_MSB = 85  # CC#85: JD-Xi Bank Select MSB (non-standard)

    # JD-Xi Bank Select LSB values
    CONTROL_CHANGE_BANK_SELECT_LSB_BANK_E_AND_F = 0
    CONTROL_CHANGE_BANK_SELECT_LSB_BANK_G_AND_H = 1
    CONTROL_CHANGE_BANK_SELECT_LSB_BANK_A_AND_B = 64  # ROM banks
    CONTROL_CHANGE_BANK_SELECT_LSB_BANK_C_AND_D = 65  # ROM banks

    # JD-Xi Program Change bank values
    PROGRAM_CHANGE_BANK_A_AND_C_AND_E_AND_G = 0
    PROGRAM_CHANGE_BANK_B_AND_D_AND_F_AND_H = 64

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

    # ============================================================================
    # JD-Xi SysEx Message Lengths
    # ============================================================================
    SYSEX_LENGTH_ONE_BYTE_DATA = 15
    SYSEX_LENGTH_FOUR_BYTE_DATA = 18

    # ============================================================================
    # JD-Xi UI Constants
    # ============================================================================
    TIMER_INTERVAL = 10
    FILTER_PLOT_DEPTH = 1.0
    CHECKED = 2
    CENTER_OCTAVE_VALUE = 0x40  # for octave up/down buttons
