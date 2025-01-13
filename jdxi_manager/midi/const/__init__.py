"""MIDI constants for Roland JD-Xi"""

# Memory Areas
ANALOG_SYNTH_AREA = 0x01
DIGITAL_SYNTH_AREA = 0x02
DRUM_KIT_AREA = 0x03
EFFECTS_AREA = 0x04

# Part Numbers
ANALOG_PART = 0x00
DIGITAL_1_PART = 0x01
DIGITAL_2_PART = 0x02
DRUM_PART = 0x03

# Bank Select Values
ANALOG_BANK_MSB = 0x5E    # 94 - Analog synth
DIGITAL_BANK_MSB = 0x5F   # 95 - Digital synth
DRUM_BANK_MSB = 0x56      # 86 - Drum kit

PRESET_BANK_LSB = 0x00    # 0 - Preset bank 1
PRESET_BANK_2_LSB = 0x01  # 1 - Preset bank 2 (Digital only)
USER_BANK_LSB = 0x10      # 16 - User bank

# MIDI Control Change messages
BANK_SELECT_MSB = 0x00    # CC 0
BANK_SELECT_LSB = 0x20    # CC 32
PROGRAM_CHANGE = 0xC0     # Program Change

# SysEx Headers
START_OF_SYSEX = 0xF0
END_OF_SYSEX = 0xF7
ROLAND_ID = 0x41
DEVICE_ID = 0x10
MODEL_ID = [0x00, 0x00, 0x00, 0x0E]

# Filter Modes
FILTER_MODE_BYPASS = 0x00  # Bypass filter
FILTER_MODE_LPF = 0x01     # Low-pass filter
