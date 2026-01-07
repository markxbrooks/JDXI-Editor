"""
Midi and JD-Xi Constant definitions
"""
from picomidi import BitMask


class MidiConstant:
    """Standard MIDI protocol constants."""

    # ============================================================================
    # Channel Voice Messages (Status Bytes)
    # ============================================================================
    NOTE_OFF = 0x80
    NOTE_ON = 0x90
    POLY_AFTERTOUCH = 0xA0
    CONTROL_CHANGE = 0xB0
    CONTROL_CHANGE_MAX = 0xBF
    PROGRAM_CHANGE = 0xC0
    PROGRAM_CHANGE_MAX = 0xCF
    CHANNEL_AFTERTOUCH = 0xD0
    PITCH_BEND = 0xE0

    # ============================================================================
    # System Common Messages
    # ============================================================================
    SYSTEM_EXCLUSIVE = 0xF0
    MIDI_TIME_CODE = 0xF1
    SONG_POSITION_POINTER = 0xF2
    SONG_SELECT = 0xF3
    TUNE_REQUEST = 0xF6
    END_OF_SYSEX = 0xF7

    # ============================================================================
    # System Realtime Messages
    # ============================================================================
    TIMING_CLOCK = 0xF8
    SONG_START = 0xFA
    SONG_CONTINUE = 0xFB
    SONG_STOP = 0xFC
    ACTIVE_SENSING = 0xFE
    SYSTEM_RESET = 0xFF

    # ============================================================================
    # Control Change Numbers (Standard MIDI)
    # ============================================================================
    class ControlChange:
        """Standard MIDI Control Change controller numbers."""
        BANK_SELECT_MSB = 0x00  # CC#0: Bank Select MSB (standard MIDI)
        BANK_SELECT_LSB = 0x20  # CC#32: Bank Select LSB (standard MIDI)
        NRPN_MSB = 99  # CC#99: Non-Registered Parameter Number MSB
        NRPN_LSB = 98  # CC#98: Non-Registered Parameter Number LSB

    # ============================================================================
    # SysEx Framing
    # ============================================================================
    START_OF_SYSEX = 0xF0
    END_OF_SYSEX = 0xF7

    # ============================================================================
    # Common MIDI Values
    # ============================================================================
    class CommonValues:
        """Common MIDI value constants."""
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

    # ============================================================================
    # Pitch Bend Constants
    # ============================================================================
    class PitchBend:
        """Pitch bend value constants."""
        RANGE = 16383  # 14-bit maximum (0x3FFF)
        CENTER = 8192  # Center position of the pitch wheel (0x2000)

    PITCH_BEND_RANGE = 16383  # 14-bit maximum (0x3FFF)
    PITCH_BEND_CENTER = 8192  # Center position of the pitch wheel

    # ============================================================================
    # Tempo Calculations
    # ============================================================================
    class Tempo:
        """Tempo and timing constants."""
        DEFAULT_120_BPM = 120
        CONVERT_SEC_TO_USEC = 1_000_000
        BPM_100_USEC = 600_000
        BPM_120_USEC = 500_000
        BPM_150_USEC = 400_000
        BPM_162_USEC = 370_370

    TEMPO_DEFAULT_120_BPM = 120
    TEMPO_CONVERT_SEC_TO_USEC = 1_000_000
    TEMPO_100_BPM_USEC = 600_000
    TEMPO_120_BPM_USEC = 500_000
    TEMPO_150_BPM_USEC = 400_000
    TEMPO_162_BPM_USEC = 370_370

    # ============================================================================
    # MIDI Protocol Limits
    # ============================================================================
    MIDI_CHANNELS_NUMBER = 16  # Standard MIDI has 16 channels (0-15 or 1-16)
    MIDI_NOTES_NUMBER = 128  # Standard MIDI has 128 notes (0-127)

    # ============================================================================
    # Bank Select (Standard MIDI)
    # ============================================================================
    BANK_SELECT_MSB = 0x00  # CC#0: Bank Select MSB (standard MIDI)
    BANK_SELECT_LSB = 0x20  # CC#32: Bank Select LSB (standard MIDI)

    # ============================================================================
    # Utility Constants
    # ============================================================================
    CHANNEL_BINARY_TO_DISPLAY = 1  # Convert 0-based to 1-based channel
    CHANNEL_DISPLAY_TO_BINARY = -1  # Convert 1-based to 0-based channel
    CHANNEL_MASK = BitMask.LOW_4_BITS  # Mask for extracting channel from status byte
    MIDI_CHANNEL_MASK = BitMask.LOW_4_BITS  # Alias for consistency

    # ============================================================================
    # Common Value Aliases (for backward compatibility)
    # ============================================================================
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

    # ============================================================================
    # Control Change Aliases (for backward compatibility)
    # ============================================================================
    CONTROL_CHANGE_NRPN_MSB = 99  # Controller number for NRPN MSB
    CONTROL_CHANGE_NRPN_LSB = 98  # Controller number for NRPN LSB

class MidiConstantOld:
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

