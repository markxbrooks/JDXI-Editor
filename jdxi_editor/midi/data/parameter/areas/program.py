from enum import Enum


class ProgramArea(Enum):
    """Program memory areas"""

    COMMON = 0x00  # 00 00 00: Program Common
    VOCAL_FX = 0x01  # 00 01 00: Program Vocal Effect
    EFFECT_1 = 0x02  # 00 02 00: Program Effect 1
    EFFECT_2 = 0x04  # 00 04 00: Program Effect 2
    DELAY = 0x06  # 00 06 00: Program Delay
    REVERB = 0x08  # 00 08 00: Program Reverb

    # Program Parts
    DIGITAL_1_PART = 0x20  # 00 20 00: Digital Synth Part 1
    DIGITAL_2_PART = 0x21  # 00 21 00: Digital Synth Part 2
    ANALOG_PART = 0x22  # 00 22 00: Analog Synth Part
    DRUMS_PART = 0x23  # 00 23 00: Drums Part

    # Program Zones
    DIGITAL_1_ZONE = 0x30  # 00 30 00: Digital Synth Zone 1
    DIGITAL_2_ZONE = 0x31  # 00 31 00: Digital Synth Zone 2
    ANALOG_ZONE = 0x32  # 00 32 00: Analog Synth Zone
    DRUMS_ZONE = 0x33  # 00 33 00: Drums Zone

    CONTROLLER = 0x40  # 00 40 00: Program Controller
