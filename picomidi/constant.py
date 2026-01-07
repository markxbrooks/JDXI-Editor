"""
Standard MIDI Protocol Constants
"""
from picomidi.core.bitmask import BitMask
from dataclasses import dataclass

@dataclass
class BitValue:
    size: int  # The number of bits
    
    @property
    def max(self):
        return self.max_for_size(self.size)

    @staticmethod
    def max_for_size(size: int) -> int:
        """
        Calculates or retrieves the maximum value based on a given bit size using a lookup.
        """
        size_map = {
            4: 0x0F,  # 15, 4-bit max
            7: 0x7F,  # 127, 7-bit max
            8: 0xFF,  # 255, 8-bit max
            14: 0x3FFF,  # 16383, 14-bit max
            16: 0xFFFF,  # 65535, 16-bit max
            32: 0xFFFFFFFF,  # 4294967295, 32-bit max
        }
        return size_map.get(size, (1 << size) - 1)  # Default to dynamic calc if not in map


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
        
        class BankSelect:
            MSB = 0x00  # CC#0: Bank Select MSB (standard MIDI)
            LSB = 0x20  # CC#32: Bank Select LSB (standard MIDI)

        class RegisteredParameterNumber:
            MSB = 101  # CC#101: Registered Parameter Number MSB
            LSB = 100  # CC#100: Registered Parameter Number LSB
    
        class NonRegisteredParameterNumber:
            MSB = 99  # CC#99: Non-Registered Parameter Number MSB
            LSB = 98  # CC#98: Non-Registered Parameter Number LSB
    
        class DataEntry:
            MSB = 6  # CC#6: Data Entry MSB
            LSB = 38  # CC#38: Data Entry LSB
            
        BANK_SELECT_MSB = 0x00  # CC#0: Bank Select MSB (standard MIDI)
        BANK_SELECT_LSB = 0x20  # CC#32: Bank Select LSB (standard MIDI)
        RPN_MSB = 101  # CC#101: Registered Parameter Number MSB
        RPN_LSB = 100  # CC#100: Registered Parameter Number LSB
        NRPN_MSB = 99  # CC#99: Non-Registered Parameter Number MSB
        NRPN_LSB = 98  # CC#98: Non-Registered Parameter Number LSB
        DATA_ENTRY_MSB = 6  # CC#6: Data Entry MSB
        DATA_ENTRY_LSB = 38  # CC#38: Data Entry LSB

    # ============================================================================
    # SysEx Framing
    # ============================================================================
    class SysExByte:
        START = 0xF0
        END = 0xF7
    
    START_OF_SYSEX = 0xF0
    END_OF_SYSEX = 0xF7

    # ============================================================================
    # Common MIDI Values
    # ============================================================================
    class CommonValues:
        """Common MIDI value constants."""
        
        # ------------------------------------------------------------------------
        # Single-Byte Values
        # ------------------------------------------------------------------------
        class SingleByte:
            """Single-byte MIDI constants."""
            ZERO = 0x00  # Zero byte
            ON = 0x01  # Value representing ON
            OFF = 0x00  # Value representing OFF
    
        # ------------------------------------------------------------------------
        # Maximum Values for Unsigned Integer Ranges
        # ------------------------------------------------------------------------
        class MaxValues:
            """Maximum unsigned constants for various bit-widths."""
            FOUR_BIT = 0x0F  # 15, 4-bit max (unsigned)
            SEVEN_BIT = 0x7F  # 127, 7-bit max (standard MIDI data byte)
            EIGHT_BIT = 0xFF  # 255, 8-bit max (unsigned)
            FOURTEEN_BIT = 0x3FFF  # 16383, 14-bit max (used in MIDI pitch bend)
            SIXTEEN_BIT = 0xFFFF  # 65535, unsigned 16-bit full range
            THIRTY_TWO_BIT = 0xFFFFFFFF  # 4294967295, max unsigned 32-bit
    
        # ------------------------------------------------------------------------
        # Signed Values
        # ------------------------------------------------------------------------
        class SignedSixteenBit:
            """Signed 16-bit integer constants."""
            MAX = 0x7FFF  # 32767, max positive signed 16-bit
            MIN = -0x8000  # -32768, two's complement min signed
    
        # ------------------------------------------------------------------------
        # Utility Methods
        # ------------------------------------------------------------------------
        @staticmethod
        def is_within_seven_bit_range(value):
            """
            Check if the given value falls within the range of a 7-bit unsigned integer.
            :param value: The value to validate.
            :return: True if the value is within range, False otherwise.
            """
            return 0 <= value <= CommonValues.MaxValues.SEVEN_BIT
        
        @staticmethod
        def is_within_sixteen_bit_range(value, signed=False):
            """
            Check if the given value falls within the range of a 16-bit integer.
            :param value: The value to validate.
            :param signed: If True, treat as signed range, otherwise unsigned.
            :return: True if the value is within range, False otherwise.
            """
            if signed:
                return CommonValues.SignedSixteenBit.MIN <= value <= CommonValues.SignedSixteenBit.MAX
            return 0 <= value <= CommonValues.MaxValues.SIXTEEN_BIT
            
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

