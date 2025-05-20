"""
Midi and JD-Xi Constant definitions
"""

from jdxi_editor.jdxi.sysex.bitmask import BitMask


class MidiConstant:
    """Miscellaneous MIDI constants for JD-Xi communication."""

    # SysEx framing
    START_OF_SYSEX = 0xF0
    END_OF_SYSEX = 0xF7

    # Common values
    ZERO_BYTE = 0x00
    VALUE_ON = 0x01
    VALUE_OFF = 0x00
    MAX_VALUE = 0x7F  # 7-bit maximum value (standard MIDI data byte)
    MAX_EIGHT_BIT_VALUE = 0xFF  # 8-bit max for comparison

    # Channel voice messages (base values)
    NOTE_OFF = 0x80
    NOTE_ON = 0x90
    POLY_AFTERTOUCH = 0xA0
    CONTROL_CHANGE = 0xB0
    PROGRAM_CHANGE = 0xC0
    CHANNEL_AFTERTOUCH = 0xD0
    PITCH_BEND = 0xE0

    # Utility
    MIDI_CHANNEL_MASK = BitMask.LOW_4_BITS  # Useful when masking/combining channel and status

    PITCH_BEND_RANGE = 16383  # 14-bit maximum (0x3FFF)
    PITCH_BEND_CENTER = 8192  # Center position of the pitch wheel


class JDXiConstant:
    """JD-Xi-specific MIDI and SysEx constants."""

    # Roland SysEx header (Identity Request/Reply)
    ID_NUMBER = 0x7E  # Non-realtime ID (0x7E) or realtime (0x7F), depending on context
    DEVICE_ID = 0x7F  # 'All Call' for all devices
    SUB_ID_1_GENERAL_INFORMATION = 0x06
    SUB_ID_2_IDENTITY_REQUEST = 0x01
    SUB_ID_2_IDENTITY_REPLY = 0x02

    # JD-Xi SysEx expected message lengths (including full header/footer)
    SYSEX_LENGTH_ONE_BYTE_DATA = 15
    SYSEX_LENGTH_FOUR_BYTE_DATA = 18
    ROLAND_ID = [0x41, 0x10, 0x00]  # Manufacturer ID, Device ID, Model ID (JD-Xi = 0x0E)
    JD_XI_MODEL_ID = 0x0E
