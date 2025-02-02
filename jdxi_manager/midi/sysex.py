"""Basic MIDI System Exclusive constants"""

# MIDI Constants
START_OF_SYSEX = 0xF0
END_OF_SYSEX = 0xF7
ROLAND_ID = 0x41
JD_XI_ID = 0x00
XI_HEADER = bytes([0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E])

# Roland Commands
DT1_COMMAND_12 = 0x12  # Data Set 1
RQ1_COMMAND_11 = 0x11  # Data Request 1

PROGRAM_COMMON = 0x00