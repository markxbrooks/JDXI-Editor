"""Roland-specific MIDI constants"""

# SysEx Headers
START_OF_SYSEX = 0xF0
END_OF_SYSEX = 0xF7
ROLAND_ID = 0x41
DEVICE_ID = 0x10

# Model ID bytes
MODEL_ID_1 = 0x00  # Manufacturer ID extension
MODEL_ID_2 = 0x00  # Device family code MSB
MODEL_ID_3 = 0x00  # Device family code LSB
MODEL_ID_4 = 0x0E  # Product code

# Full Model ID array
MODEL_ID = [MODEL_ID_1, MODEL_ID_2, MODEL_ID_3, MODEL_ID_4]

# Device Identification
JD_XI_ID = [ROLAND_ID, MODEL_ID_1, MODEL_ID_2, MODEL_ID_3, MODEL_ID_4]

# SysEx Commands
DT1_COMMAND_12 = 0x12  # Data Set 1
RQ1_COMMAND_11 = 0x11  # Data Request 1
