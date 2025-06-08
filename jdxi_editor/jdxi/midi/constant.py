"""
Midi and JD-Xi Constant definitions
"""

from jdxi_editor.jdxi.sysex.bitmask import BitMask


class MidiConstant:
    """Miscellaneous MIDI constants for JD-Xi communication."""

    # SysEx framing
    SONG_STOP = 0xFC
    SONG_START = 0xFA
    START_OF_SYSEX = 0xF0
    END_OF_SYSEX = 0xF7

    # Common values
    ZERO_BYTE = 0x00
    VALUE_ON = 0x01
    VALUE_OFF = 0x00
    VALUE_MAX_FOUR_BIT = 0x0F  # 15, 4-bit max (unsigned)
    VALUE_MAX_SEVEN_BIT = 0x7F  # 127, 7-bit max (standard MIDI data byte)
    VALUE_MAX_EIGHT_BIT = 0xFF  # 255, 8-bit max (unsigned)
    VALUE_MAX_FOURTEEN_BIT = 0x3FFF  # 16383, 14-bit max (used in MIDI pitch bend)
    VALUE_MAX_SIGNED_SIXTEEN_BIT = 0x7FFF  # 32767, max positive signed 16-bit
    VALUE_MIN_SIGNED_SIXTEEN_BIT = 0x8000  # -32768, two's complement min signed
    VALUE_MAX_UNSIGNED_SIXTEEN_BIT = 0xFFFF   # 65535, full unsigned 16-bit range
    VALUE_MAX_THIRTY_TWO_BIT = 0xFFFFFFFF  # 4294967295, max unsigned 32-bit
    
    # Channel voice messages (base values)
    NOTE_OFF = 0x80
    NOTE_ON = 0x90
    POLY_AFTERTOUCH = 0xA0
    CONTROL_CHANGE = 0xB0 # Control Change (0xB0)
    CONTROL_CHANGE_MAX = 0xBF  # Maximum Control Change value (0xBF)
    PROGRAM_CHANGE = 0xC0 # Program Change (0xC0)
    PROGRAM_CHANGE_MAX = 0xCF  # Maximum Program Change value (0xCF)
    CHANNEL_AFTERTOUCH = 0xD0
    PITCH_BEND = 0xE0
    BANK_SELECT_MSB = 0x00
    BANK_SELECT_LSB = 0x20

    # Utility
    MIDI_CHANNEL_MASK = BitMask.LOW_4_BITS  # Useful when masking/combining channel and status

    PITCH_BEND_RANGE = 16383  # 14-bit maximum (0x3FFF)
    PITCH_BEND_CENTER = 8192  # Center position of the pitch wheel
    CHANNEL_BINARY_TO_DISPLAY = 1  # Convert binary to display value
    CHANNEL_DISPLAY_TO_BINARY = -1  # Convert display to binary value


class JDXiConstant:
    """JD-Xi-specific MIDI and SysEx constants."""

    # Roland SysEx header (Identity Request/Reply)
    CENTER_OCTAVE_VALUE = 0x40  # for octave up/down buttons
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
