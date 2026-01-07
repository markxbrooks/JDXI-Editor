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


class JDXiMidiConstant:
    """Miscellaneous MIDI constants for JD-Xi communication."""

    class ControlChange:
        BANK_SELECT_MSB = 85
        BANK_SELECT_LSB_BANK_E_AND_F = 0
        BANK_SELECT_LSB_BANK_G_AND_H = 1
        BANK_SELECT_LSB_BANK_A_AND_B = 64
        BANK_SELECT_LSB_BANK_C_AND_D = 65
        NRPN_MSB = 99
        NRPN_LSB = 98

    class ProgramChange:
        BANK_A_C_E_G = 0
        BANK_B_D_F_H = 64

    class Tempo:
        DEFAULT_120_BPM = 120
        CONVERT_SEC_TO_USEC = 1_000_000
        BPM_100_USEC = 600_000
        BPM_120_USEC = 500_000
        BPM_150_USEC = 400_000
        BPM_162_USEC = 370_370

    class SysEx:
        START_OF_SYSEX = 0xF0
        END_OF_SYSEX = 0xF7
        SONG_STOP = 0xFC
        SONG_START = 0xFA

    class CommonValues:
        ZERO_BYTE = 0x00
        VALUE_ON = 0x01
        VALUE_OFF = 0x00
        VALUE_MAX_FOUR_BIT = 0x0F
        VALUE_MAX_SEVEN_BIT = 0x7F
        VALUE_MAX_EIGHT_BIT = 0xFF
        VALUE_MAX_FOURTEEN_BIT = 0x3FFF
        VALUE_MAX_SIGNED_SIXTEEN_BIT = 0x7FFF
        VALUE_MIN_SIGNED_SIXTEEN_BIT = 0x8000
        VALUE_MAX_UNSIGNED_SIXTEEN_BIT = 0xFFFF
        VALUE_MAX_THIRTY_TWO_BIT = 0xFFFFFFFF

    class ChannelMessages:
        NOTE_OFF = 0x80
        NOTE_ON = 0x90
        POLY_AFTERTOUCH = 0xA0
        CONTROL_CHANGE = 0xB0
        CONTROL_CHANGE_MAX = 0xBF
        PROGRAM_CHANGE = 0xC0
        PROGRAM_CHANGE_MAX = 0xCF
        CHANNEL_AFTERTOUCH = 0xD0
        PITCH_BEND = 0xE0
        BANK_SELECT_MSB = 0x00
        BANK_SELECT_LSB = 0x20

    class PitchBend:
        RANGE = 16383  # 14-bit maximum
        CENTER = 8192  # Center position of the pitch wheel

    # Utility
    CHANNEL_BINARY_TO_DISPLAY = 1
    CHANNEL_DISPLAY_TO_BINARY = -1
    CHANNEL_MASK = BitMask.LOW_4_BITS

    # User Banks
    MIDI_CHANNELS_NUMBER = 16
    MIDI_NOTES_NUMBER = 128
    CONTROL_CHANGE_BANK_SELECT_MSB = 85
    CONTROL_CHANGE_BANK_SELECT_LSB_BANK_E_AND_F = 0
    CONTROL_CHANGE_BANK_SELECT_LSB_BANK_G_AND_H = 1
    # ROM banks
    CONTROL_CHANGE_BANK_SELECT_LSB_BANK_A_AND_B = 64
    CONTROL_CHANGE_BANK_SELECT_LSB_BANK_C_AND_D = 65
    # Program Change
    PROGRAM_CHANGE_BANK_A_AND_C_AND_E_AND_G = 0
    PROGRAM_CHANGE_BANK_B_AND_D_AND_F_AND_H = 64
    # Tempo calculations
    TEMPO_DEFAULT_120_BPM = 120
    TEMPO_CONVERT_SEC_TO_USEC = 1_000_000
    TEMPO_100_BPM_USEC = 600_000
    TEMPO_120_BPM_USEC = 500_000
    TEMPO_150_BPM_USEC = 400_000
    TEMPO_162_BPM_USEC = 370_370

    # SysEx framing
    CONTROL_CHANGE_NRPN_MSB = 99  # Controller number for NRPN MSB
    CONTROL_CHANGE_NRPN_LSB = 98  # Controller number for NRPN LSB
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
    VALUE_MAX_UNSIGNED_SIXTEEN_BIT = 0xFFFF  # 65535, full unsigned 16-bit range
    VALUE_MAX_THIRTY_TWO_BIT = 0xFFFFFFFF  # 4294967295, max unsigned 32-bit

    # Channel voice messages (base values)
    NOTE_OFF = 0x80
    NOTE_ON = 0x90
    POLY_AFTERTOUCH = 0xA0
    CONTROL_CHANGE = 0xB0  # Control Change (0xB0)
    CONTROL_CHANGE_MAX = 0xBF  # Maximum Control Change value (0xBF)
    PROGRAM_CHANGE = 0xC0  # Program Change (0xC0)
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
