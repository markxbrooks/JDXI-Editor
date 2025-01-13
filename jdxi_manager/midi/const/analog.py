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

# Analog Oscillator Parameters
ANALOG_OSC_WAVE = 0x16        # Waveform (0-2: SAW,TRI,PW-SQR)
ANALOG_OSC_COARSE = 0x17      # Pitch Coarse (40-88: -24 to +24)
ANALOG_OSC_FINE = 0x18        # Pitch Fine (14-114: -50 to +50)

# Analog Filter Parameters
ANALOG_FILTER_SWITCH = 0x20    # Filter switch (0-1: BYPASS, LPF)
ANALOG_FILTER_CUTOFF = 0x21    # Filter cutoff frequency (0-127)
ANALOG_FILTER_KEYFOLLOW = 0x22 # Cutoff keyfollow (54-74: -100 to +100)
ANALOG_FILTER_RESONANCE = 0x23 # Filter resonance (0-127)
ANALOG_FILTER_ENV_VELO = 0x24  # Env velocity sens (1-127: -63 to +63)
ANALOG_FILTER_ENV_A = 0x25     # Filter env attack time (0-127)
ANALOG_FILTER_ENV_D = 0x26     # Filter env decay time (0-127)
ANALOG_FILTER_ENV_S = 0x27     # Filter env sustain level (0-127)
ANALOG_FILTER_ENV_R = 0x28     # Filter env release time (0-127)
ANALOG_FILTER_ENV_DEPTH = 0x29 # Filter env depth (1-127: -63 to +63)

# Filter Modes
FILTER_MODE_BYPASS = 0x00  # Bypass filter
FILTER_MODE_LPF = 0x01     # Low-pass filter

# Analog LFO Parameters
ANALOG_LFO_SHAPE = 0x30        # LFO Shape (0-5: TRI,SIN,SAW,SQR,S&H,RND)
ANALOG_LFO_RATE = 0x31         # LFO Rate (0-127)
ANALOG_LFO_FADE = 0x32         # LFO Fade Time (0-127)
ANALOG_LFO_SYNC = 0x33         # LFO Tempo Sync Switch (0-1)
ANALOG_LFO_SYNC_NOTE = 0x34    # LFO Tempo Sync Note (0-19)