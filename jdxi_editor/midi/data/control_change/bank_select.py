from enum import Enum


class BankSelectCC(Enum):

    # Bank Select MSB/LSB values
    BANK_MSB = 0x55  # 85 (0x55) for all JD-Xi banks
    BANK_LSB = {
        "USER_E": 0x00,  # User Bank E (001-064)
        "USER_F": 0x00,  # User Bank F (065-128)
        "USER_G": 0x01,  # User Bank G (001-064)
        "USER_H": 0x01,  # User Bank H (065-128)
        "PRESET_A": 0x40,  # Preset Bank A (001-064) [64 decimal]
        "PRESET_B": 0x40,  # Preset Bank B (065-128)
        "PRESET_C": 0x41,  # Preset Bank C (001-064) [65 decimal]
        "PRESET_D": 0x41,  # Preset Bank D (065-128)
        "EXTRA_S": 0x60,  # Extra Bank S (001-064) [96 decimal]
        "EXTRA_T": 0x61,  # Extra Bank T (065-128) [97 decimal]
        "EXTRA_U": 0x62,  # Extra Bank U (001-064) [98 decimal]
        "EXTRA_V": 0x63,  # Extra Bank V (065-128) [99 decimal]
        "EXTRA_W": 0x64,  # Extra Bank W (001-064) [100 decimal]
        "EXTRA_X": 0x65,  # Extra Bank X (065-128) [101 decimal]
        "EXTRA_Y": 0x66,  # Extra Bank Y (001-064) [102 decimal]
        "EXTRA_Z": 0x67,  # Extra Bank Z (001-064) [103 decimal]
    }

    # Bank Select MSB values for different synth types
    ANALOG_BANK_MSB = 0x5E  # 94 (0x5E) for Analog synth
    DIGITAL_BANK_MSB = 0x5F  # 95 (0x5F) for Digital synth (SuperNATURAL)
    DRUM_BANK_MSB = 0x56  # 86 (0x56) for Drum kits

    # Bank Select LSB values
    PRESET_BANK_LSB = 0x40  # 64 (0x40) for preset bank
    PRESET_BANK_2_LSB = 0x41  # 65 (0x41) for second preset bank (Digital only)