class MidiConstant :
    """Miscellaneous MIDI constants for JD-Xi communication."""
    START_OF_SYSEX = 0xF0
    END_OF_SYSEX = 0xF7
    ZERO_BYTE = 0x00
    VALUE_ON = 0x01
    VALUE_OFF = 0x00
    NOTE_ON = 0x90
    NOTE_OFF = 0x80
    MAX_VALUE = 0x7F  # maximum MIDI value of 7 bits without the status bit
    MAX_EIGHT_BIT_VALUE = 255  # maximum value held by eight bits
    ONE_BYTE_SYSEX_DATA_LENGTH = 15
    FOUR_BYTE_SYSEX_DATA_LENGTH = 18


class JDXiMidiConstant :
    """Miscellaneous MIDI constants for JD-Xi communication."""
    START_OF_SYSEX = 0xF0
    END_OF_SYSEX = 0xF7
    ID_NUMBER = 0x7E
    DEVICE_ID = 0x7F
    SUB_ID_1_GENERAL_INFORMATION = 0x06
    SUB_ID_2_IDENTITY_REQUEST = 0x01
    SUB_ID_2_IDENTITY_REPLY = 0x02
    ZERO_BYTE = 0x00
    VALUE_ON = 0x01
    VALUE_OFF = 0x00
    NOTE_ON = 0x90
    NOTE_OFF = 0x80
    MAX_EIGHT_BIT_VALUE = 255  # maximum values held by eight bits
    ONE_BYTE_SYSEX_DATA_LENGTH = 15
    FOUR_BYTE_SYSEX_DATA_LENGTH = 18
