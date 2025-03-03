import logging
import re
from typing import Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from jdxi_manager.data.parameter.synth import SynthParameter

"""
Drum Kit Parameters Reference
============================

+-------------------------------------------------------------------------------+
| Offset    |           |                                                       |
| Address   |           | Description                                           |
|-----------+-----------+-------------------------------------------------------|
| 00 00     | 0aaa aaaa | Partial Name 1 (32 - 127)                             |
|           |           |                                      32 - 127 [ASCII] |
| 00 01     | 0aaa aaaa | Partial Name 2 (32 - 127)                             |
|           |           |                                      32 - 127 [ASCII] |
| 00 02     | 0aaa aaaa | Partial Name 3 (32 - 127)                             |
|           |           |                                      32 - 127 [ASCII] |
| 00 03     | 0aaa aaaa | Partial Name 4 (32 - 127)                             |
|           |           |                                      32 - 127 [ASCII] |
| 00 04     | 0aaa aaaa | Partial Name 5 (32 - 127)                             |
|           |           |                                      32 - 127 [ASCII] |
| 00 05     | 0aaa aaaa | Partial Name 6 (32 - 127)                             |
|           |           |                                      32 - 127 [ASCII] |
| 00 06     | 0aaa aaaa | Partial Name 7 (32 - 127)                             |
|           |           |                                      32 - 127 [ASCII] |
| 00 07     | 0aaa aaaa | Partial Name 8 (32 - 127)                             |
|           |           |                                      32 - 127 [ASCII] |
| 00 08     | 0aaa aaaa | Partial Name 9 (32 - 127)                             |
|           |           |                                      32 - 127 [ASCII] |
| 00 09     | 0aaa aaaa | Partial Name 10 (32 - 127)                            |
|           |           |                                      32 - 127 [ASCII] |
| 00 0A     | 0aaa aaaa | Partial Name 11 (32 - 127)                            |
|           |           |                                      32 - 127 [ASCII] |
| 00 0B     | 0aaa aaaa | Partial Name 12 (32 - 127)                            |
|           |           |                                      32 - 127 [ASCII] |
|-----------+-----------+-------------------------------------------------------|
| 00 0C     | 0000 000a | Assign Type                                 (0 - 1)   |
|           |           |                                     MULTI, SINGLE     |
| 00 0D     | 000a aaaa | Mute Group                                 (0 - 31)   |
|           |           |                                     OFF, 1 - 31       |
|-----------+-----------+-------------------------------------------------------|
| 00 0E     | 0aaa aaaa | Partial Level                             (0 - 127)   |
| 00 0F     | 0aaa aaaa | Partial Coarse Tune                       (0 - 127)   |
|           |           |                                      C-1 - G9         |
| 00 10     | 0aaa aaaa | Partial Fine Tune                        (14 - 114)   |
|           |           |                                      -50 - +50        |
| 00 11     | 000a aaaa | Partial Random Pitch Depth                (0 - 30)    |
|           |           |                                      0, 1, 2, 3, 4,   |
|           |           |                                      5, 6, 7, 8, 9,   |
|           |           |                                      10, 20, 30, 40,  |
|           |           |                                      50, 60, 70, 80,  |
|           |           |                                      90, 100, 200,    |
|           |           |                                      300, 400, 500,   |
|           |           |                                      600, 700, 800,   |
|           |           |                                      900, 1000, 1100, |
|           |           |                                      1200             |
| 00 12     | 0aaa aaaa | Partial Pan                               (0 - 127)   |
|           |           |                                      L64 - 63R        |
| 00 13     | 00aa aaaa | Partial Random Pan Depth                  (0 - 63)    |
| 00 14     | 0aaa aaaa | Partial Alternate Pan Depth               (1 - 127)   |
|           |           |                                        L63 - 63R      |
| 00 15     | 0000 000a | Partial Env Mode                          (0 - 1)     |
|           |           |                                       NO-SUS, SUSTAIN |
|-----------+-----------+-------------------------------------------------------|
| 00 16     | 0aaa aaaa | Partial Output Level                      (0 - 127)   |
| 00 17     | 0aaa aaaa | (reserve)                                             |
| 00 18     | 0aaa aaaa | (reserve)                                             |
| 00 19     | 0aaa aaaa | Partial Chorus Send Level                 (0 - 127)   |
| 00 1A     | 0aaa aaaa | Partial Reverb Send Level                 (0 - 127)   |
| 00 1B     | 0000 aaaa | Partial Output Assign                     (0 - 4)     |
|           |           |                                        EFX1, EFX2,    |
|           |           |                                        DLY, REV, DIR  |
|-----------+-----------+-------------------------------------------------------|
| 00 1C     | 00aa aaaa | Partial Pitch Bend Range                  (0 - 48)    |
| 00 1D     | 0000 000a | Partial Receive Expression                (0 - 1)     |
|           |           |                                         OFF, ON       |
| 00 1E     | 0000 000a | Partial Receive Hold-1                    (0 - 1)     |
|           |           |                                        OFF, ON        |
| 00 1F     | 0000 000a | (reserve)                                             |
|-----------+-----------+-------------------------------------------------------|
| 01 1E     | 0aaa aaaa | Pitch Env Level 1                         (1 - 127)   |
|           |           |                                           -63 - +63   |
| 01 1F     | 0aaa aaaa | Pitch Env Level 2                         (1 - 127)   |
|           |           |                                           -63 - +63   |
| 01 20     | 0aaa aaaa | Pitch Env Level 3                        (1 - 127)    |
|           |           |                                           -63 - +63   |
| 01 21     | 0aaa aaaa | Pitch Env Level 4                        (1 - 127)    |
|           |           |                                           -63 - +63   |
|-----------+-----------+-------------------------------------------------------|
| 01 22     | 0000 0aaa | TVF Filter Type                           (0 - 6)     |
|           |           |                                           OFF, LPF,   |
|           |           |                                            BPF, HPF,  |
|           |           |                                            PKG, LPF2, |
|           |           |                                           LPF3        |
|-----------+-----------+-------------------------------------------------------|
| 01 23    | 0aaa aaaa | TVF Cutoff Frequency                       (0 - 127)   |
| 01 24    | 0000 0aaa | TVF Cutoff Velocity Curve                  (0 - 7)     |
|          |           |                                          FIXED, 1 - 7  |
| 01 25    | 0aaa aaaa | TVF Cutoff Velocity Sens                   (1 - 127)   |
|          |           |                                          -63 - +63     |
| 01 26    | 0aaa aaaa | TVF Resonance                             (0 - 127)    |
| 01 27    | 0aaa aaaa | TVF Resonance Velocity Sens               (1 - 127)    |
|          |           |                                          -63 - +63     |
| 01 28    | 0aaa aaaa | TVF Env Depth                             (1 - 127)    |
|          |           |                                          -63 - +63     |
| 01 29    | 0000 0aaa | TVF Env Velocity Curve Type               (0 - 7)      |
|          |           |                                          FIXED, 1 - 7  |
| 01 2A    | 0aaa aaaa | TVF Env Velocity Sens                     (1 - 127)    |
|          |           |                                          -63 - +63     |
| 01 2B    | 0aaa aaaa | TVF Env Time 1 Velocity Sens              (1 - 127)    |
|          |           |                                          -63 - +63     |
| 01 2C    | 0aaa aaaa | TVF Env Time 4 Velocity Sens              (1 - 127)    |
|          |           |                                          -63 - +63     |
| 01 2D    | 0aaa aaaa | TVF Env Time 1                            (0 - 127)    |
| 01 2E    | 0aaa aaaa | TVF Env Time 2                            (0 - 127)    |
| 01 2F    | 0aaa aaaa | TVF Env Time 3                            (0 - 127)    |
| 01 30    | 0aaa aaaa | TVF Env Time 4                            (0 - 127)    |
| 01 31    | 0aaa aaaa | TVF Env Level 0                           (0 - 127)    |
| 01 32    | 0aaa aaaa | TVF Env Level 1                           (0 - 127)    |
| 01 33    | 0aaa aaaa | TVF Env Level 2                           (0 - 127)    |
| 01 34    | 0aaa aaaa | TVF Env Level 3                           (0 - 127)    |
| 01 35    | 0aaa aaaa | TVF Env Level 4                           (0 - 127)    |
|----------+-----------+--------------------------------------------------------|
| 01 36    | 0000 0aaa | TVA Level Velocity Curve                  (0 - 7)      |
|          |           |                                          FIXED, 1 - 7  |
| 01 37    | 0aaa aaaa | TVA Level Velocity Sens                   (1 - 127)    |
|          |           |                                          -63 - +63     |
| 01 38    | 0aaa aaaa | TVA Env Time 1 Velocity Sens              (1 - 127)    |
|          |           |                                          -63 - +63     |
| 01 39    | 0aaa aaaa | TVA Env Time 4 Velocity Sens              (1 - 127)    |
|          |           |                                          -63 - +63     |
| 01 3A    | 0aaa aaaa | TVA Env Time 1                            (0 - 127)    |
| 01 3B    | 0aaa aaaa | TVA Env Time 2                            (0 - 127)    |
| 01 3C    | 0aaa aaaa | TVA Env Time 3                            (0 - 127)    |
| 01 3D    | 0aaa aaaa | TVA Env Time 4                            (0 - 127)    |
| 01 3E    | 0aaa aaaa | TVA Env Level 1                           (0 - 127)    |
| 01 3F    | 0aaa aaaa | TVA Env Level 2                           (0 - 127)    |
| 01 40    | 0aaa aaaa | TVA Env Level 3                           (0 - 127)    |
|----------+-----------+--------------------------------------------------------|
| 01 41    | 0000 000a | One Shot Mode                             (0 - 1)      |
|          |           |                                          OFF, ON       |
| 01 42    | 0aaa aaaa | Relative Level                            (0 - 127)    |
|          |           |                                          -64 - +63     |
|-----------+-----------+-------------------------------------------------------|
| 00 00 01 43           |                                        Total Size     |
+-------------------------------------------------------------------------------+
           "COM": 0x00,  # Common parameters
            "BD1": 0x2E,  # Drum Kit Partial (Key # 36)
            "RIM": 0x30,  # Drum Kit Partial (Key # 37)
            "BD2": 0x32,  # Drum Kit Partial (Key # 38)
            "CLAP": 0x34,  # Drum Kit Partial (Key # 39)
            "BD3": 0x36,  # Drum Kit Partial (Key # 40)
            "SD1": 0x38,  # Drum Kit Partial (Key # 41)
            "CHH": 0x3A,  # Drum Kit Partial (Key # 42)
            "SD2": 0x3C,  # Drum Kit Partial (Key # 43)
            "PHH": 0x3E,  # Drum Kit Partial (Key # 44)
            "SD3": 0x40,  # Drum Kit Partial (Key # 45)
            "OHH": 0x42,  # Drum Kit Partial (Key # 46)
            "SD4": 0x44,  # Drum Kit Partial (Key # 47)
            "TOM1": 0x46,  # Drum Kit Partial (Key # 48)
            "PRC1": 0x48,  # Drum Kit Partial (Key # 49)
            "TOM2": 0x4A,  # Drum Kit Partial (Key # 50)
            "PRC2": 0x4C,  # Drum Kit Partial (Key # 51)
            "TOM3": 0x4E,  # Drum Kit Partial (Key # 52)
            "PRC3": 0x50,  # Drum Kit Partial (Key # 53)
            "CYM1": 0x52,  # Drum Kit Partial (Key # 54)
            "PRC4": 0x54,  # Drum Kit Partial (Key # 55)
            "CYM2": 0x56,  # Drum Kit Partial (Key # 56)
            "PRC5": 0x58,  # Drum Kit Partial (Key # 57)
            "CYM3": 0x5A,  # Drum Kit Partial (Key # 58)
            "HIT": 0x5C,  # Drum Kit Partial (Key # 59)
            "OTH1": 0x5E,  # Drum Kit Partial (Key # 60)
            "OTH2": 0x60,  # Drum Kit Partial (Key # 61)
            "D4": 0x62,  # Drum Kit Partial (Key # 62)
            "Eb4": 0x64,  # Drum Kit Partial (Key # 63)
            "E4": 0x66,  # Drum Kit Partial (Key # 64)
            "F4": 0x68,  # Drum Kit Partial (Key # 65)
            "F#4": 0x6A,  # Drum Kit Partial (Key # 66)
            "G4": 0x6C,  # Drum Kit Partial (Key # 67)
            "G#4": 0x6E,  # Drum Kit Partial (Key # 68)
            "A4": 0x70,  # Drum Kit Partial (Key # 69)
            "Bb4": 0x72,  # Drum Kit Partial (Key # 70)
            "B4": 0x74,  # Drum Kit Partial (Key # 71)
            "C5": 0x76,  # Drum Kit Partial (Key # 72)

"""
DRUM_ADDRESSES = {
    "COM": 0x00,
    "BD1": 0x2E,
    "RIM": 0x30,
    "BD2": 0x32,
    "CLAP": 0x34,
    "BD3": 0x36,
    "SD1": 0x38,
    "CHH": 0x3A,
    "SD2": 0x3C,
    "PHH": 0x3E,
    "SD3": 0x40,
    "OHH": 0x42,
    "SD4": 0x44,
    "TOM1": 0x46,
    "PRC1": 0x48,
    "TOM2": 0x4A,
    "PRC2": 0x4C,
    "TOM3": 0x4E,
    "PRC3": 0x50,
    "CYM1": 0x52,
    "PRC4": 0x54,
    "CYM2": 0x56,
    "PRC5": 0x58,
    "CYM3": 0x5A,
    "HIT": 0x5C,
    "OTH1": 0x5E,
    "OTH2": 0x60,
    "D4": 0x62,
    "Eb4": 0x64,
    "E4": 0x66,
    "F4": 0x68,
    "F#4": 0x6A,
    "G4": 0x6C,
    "G#4": 0x6E,
    "A4": 0x70,
    "Bb4": 0x72,
    "B4": 0x74,
    "C5": 0x76,
}


def get_address_for_partial_name(partial_name: str) -> int:
    """Get parameter group and address adjusted for partial number."""

    address_map = {
        "COM": 0x00,  # Common parameters
        "BD1": 0x2E,  # Drum Kit Partial (Key # 36)
        "RIM": 0x30,  # Drum Kit Partial (Key # 37)
        "BD2": 0x32,  # Drum Kit Partial (Key # 38)
        "CLAP": 0x34,  # Drum Kit Partial (Key # 39)
        "BD3": 0x36,  # Drum Kit Partial (Key # 40)
        "SD1": 0x38,  # Drum Kit Partial (Key # 41)
        "CHH": 0x3A,  # Drum Kit Partial (Key # 42)
        "SD2": 0x3C,  # Drum Kit Partial (Key # 43)
        "PHH": 0x3E,  # Drum Kit Partial (Key # 44)
        "SD3": 0x40,  # Drum Kit Partial (Key # 45)
        "OHH": 0x42,  # Drum Kit Partial (Key # 46)
        "SD4": 0x44,  # Drum Kit Partial (Key # 47)
        "TOM1": 0x46,  # Drum Kit Partial (Key # 48)
        "PRC1": 0x48,  # Drum Kit Partial (Key # 49)
        "TOM2": 0x4A,  # Drum Kit Partial (Key # 50)
        "PRC2": 0x4C,  # Drum Kit Partial (Key # 51)
        "TOM3": 0x4E,  # Drum Kit Partial (Key # 52)
        "PRC3": 0x50,  # Drum Kit Partial (Key # 53)
        "CYM1": 0x52,  # Drum Kit Partial (Key # 54)
        "PRC4": 0x54,  # Drum Kit Partial (Key # 55)
        "CYM2": 0x56,  # Drum Kit Partial (Key # 56)
        "PRC5": 0x58,  # Drum Kit Partial (Key # 57)
        "CYM3": 0x5A,  # Drum Kit Partial (Key # 58)
        "HIT": 0x5C,  # Drum Kit Partial (Key # 59)
        "OTH1": 0x5E,  # Drum Kit Partial (Key # 60)
        "OTH2": 0x60,  # Drum Kit Partial (Key # 61)
        "D4": 0x62,  # Drum Kit Partial (Key # 62)
        "Eb4": 0x64,  # Drum Kit Partial (Key # 63)
        "E4": 0x66,  # Drum Kit Partial (Key # 64)
        "F4": 0x68,  # Drum Kit Partial (Key # 65)
        "F#4": 0x6A,  # Drum Kit Partial (Key # 66)
        "G4": 0x6C,  # Drum Kit Partial (Key # 67)
        "G#4": 0x6E,  # Drum Kit Partial (Key # 68)
        "A4": 0x70,  # Drum Kit Partial (Key # 69)
        "Bb4": 0x72,  # Drum Kit Partial (Key # 70)
        "B4": 0x74,  # Drum Kit Partial (Key # 71)
        "C5": 0x76,  # Drum Kit Partial (Key # 72)
    }
    address = address_map.get(partial_name, 0x00)  # Default to 0x00 for common area
    return address


class DrumParameter(SynthParameter):
    """Drum kit parameters with their addresses and value ranges"""

    def __init__(self, address: int, min_val: int, max_val: int,
                 display_min: Optional[int] = None, display_max: Optional[int] = None):
        super().__init__(address, min_val, max_val)
        self.display_min = display_min if display_min is not None else min_val
        self.display_max = display_max if display_max is not None else max_val

    # Partial Name parameters
    PARTIAL_NAME_1 = (0x00, 32, 127)
    PARTIAL_NAME_2 = (0x01, 32, 127)
    PARTIAL_NAME_3 = (0x02, 32, 127)
    PARTIAL_NAME_4 = (0x03, 32, 127)
    PARTIAL_NAME_5 = (0x04, 32, 127)
    PARTIAL_NAME_6 = (0x05, 32, 127)
    PARTIAL_NAME_7 = (0x06, 32, 127)
    PARTIAL_NAME_8 = (0x07, 32, 127)
    PARTIAL_NAME_9 = (0x08, 32, 127)
    PARTIAL_NAME_10 = (0x09, 32, 127)
    PARTIAL_NAME_11 = (0x0A, 32, 127)
    PARTIAL_NAME_12 = (0x0B, 32, 127)

    # Assign Type
    ASSIGN_TYPE = (0x0C, 0, 1)  # MULTI, SINGLE

    # Mute Group
    MUTE_GROUP = (0x0D, 0, 31, 0, 31)  # OFF, 1 - 31

    # Partial Level
    PARTIAL_LEVEL = (0x0E, 0, 127, 0, 127)

    # Partial Coarse Tune
    PARTIAL_COARSE_TUNE = (0x0F, 0, 127)  # C-1 - G9

    # Partial Fine Tune
    PARTIAL_FINE_TUNE = (0x10, 14, 114, -50, 50)  # -50 - +50

    # Partial Random Pitch Depth
    PARTIAL_RANDOM_PITCH_DEPTH = (0x11, 0, 30, 0, 30)

    # Partial Pan
    PARTIAL_PAN = (0x12, 0, 127)  # L64 - 63R

    # Partial Random Pan Depth
    PARTIAL_RANDOM_PAN_DEPTH = (0x13, 0, 63, 0, 63)

    # Partial Alternate Pan Depth
    PARTIAL_ALTERNATE_PAN_DEPTH = (0x14, 1, 127, 1, 127)  # L63 - 63R

    # Partial Env Mode
    PARTIAL_ENV_MODE = (0x15, 0, 1)  # NO-SUS, SUSTAIN

    # Partial Output Level
    PARTIAL_OUTPUT_LEVEL = (0x16, 0, 127, 0, 127)

    # Partial Chorus Send Level
    PARTIAL_CHORUS_SEND_LEVEL = (0x19, 0, 127, 0, 127)

    # Partial Reverb Send Level
    PARTIAL_REVERB_SEND_LEVEL = (0x1A, 0, 127, 0, 127)

    # Partial Output Assign
    PARTIAL_OUTPUT_ASSIGN = (0x1B, 0, 4, 0, 4)  # EFX1, EFX2, DLY, REV, DIR

    # Partial Pitch Bend Range
    PARTIAL_PITCH_BEND_RANGE = (0x1C, 0, 48, 0, 48)

    # Partial Receive Expression
    PARTIAL_RECEIVE_EXPRESSION = (0x1D, 0, 1, 0, 1)  # OFF, ON

    # Partial Receive Hold-1
    PARTIAL_RECEIVE_HOLD_1 = (0x1E, 0, 1, 0, 1)  # OFF, ON

    # WMT Velocity Control
    WMT_VELOCITY_CONTROL = (0x20, 0, 2, 0, 2)  # OFF, ON, RANDOM

    # WMT1 Wave Switch
    WMT1_WAVE_SWITCH = (0x21, 0, 1, 0, 1)  # OFF, ON

    # WMT1 Wave Group Type
    WMT1_WAVE_GROUP_TYPE = (0x22, 0, 0, 0, 0)  # Only one preset_type

    # WMT1 Wave Group ID
    WMT1_WAVE_GROUP_ID = (0x23, 0, 16384, 0, 16384)  # OFF, 1 - 16384

    # WMT1 Wave Number L (Mono)
    WMT1_WAVE_NUMBER_L = (0x27, 0, 16384, 0, 16384)  # OFF, 1 - 16384

    # WMT1 Wave Number R
    WMT1_WAVE_NUMBER_R = (0x2B, 0, 16384, 0, 16384)  # OFF, 1 - 16384

    # WMT1 Wave Gain
    WMT1_WAVE_GAIN = (0x2F, 0, 3, 0, 3)  # -6, 0, +6, +12 [dB]

    # WMT1 Wave FXM Switch
    WMT1_WAVE_FXM_SWITCH = (0x30, 0, 1, 0, 1)  # OFF, ON

    # WMT1 Wave FXM Color
    WMT1_WAVE_FXM_COLOR = (0x31, 0, 3, 1, 4)  # 1 - 4

    # WMT1 Wave FXM Depth
    WMT1_WAVE_FXM_DEPTH = (0x32, 0, 16, 0, 16)

    # WMT1 Wave Tempo Sync
    WMT1_WAVE_TEMPO_SYNC = (0x33, 0, 1, 0, 1)  # OFF, ON

    # WMT1 Wave Coarse Tune
    WMT1_WAVE_COARSE_TUNE = (0x34, 16, 112, 16, 112)  # -48 - +48

    # WMT1 Wave Fine Tune
    WMT1_WAVE_FINE_TUNE = (0x35, 14, 114, 14, 114)  # -50 - +50

    # WMT1 Wave Pan
    WMT1_WAVE_PAN = (0x36, 0, 127, 0, 127)  # L64 - 63R

    # WMT1 Wave Random Pan Switch
    WMT1_WAVE_RANDOM_PAN_SWITCH = (0x37, 0, 1, 0, 1)  # OFF, ON

    # WMT1 Wave Alternate Pan Switch
    WMT1_WAVE_ALTERNATE_PAN_SWITCH = (0x38, 0, 2, 0, 2)  # OFF, ON, REVERSE

    # WMT1 Wave Level
    WMT1_WAVE_LEVEL = (0x39, 0, 127, 0, 127)

    # WMT1 Velocity Range Lower
    WMT1_VELOCITY_RANGE_LOWER = (0x3A, 1, 127, 1, 127)  # 1 - UPPER

    # WMT1 Velocity Range Upper
    WMT1_VELOCITY_RANGE_UPPER = (0x3B, 1, 127, 1, 127)  # LOWER - 127

    # WMT1 Velocity Fade Width Lower
    WMT1_VELOCITY_FADE_WIDTH_LOWER = (0x3C, 0, 127, 0, 127)

    # WMT1 Velocity Fade Width Upper
    WMT1_VELOCITY_FADE_WIDTH_UPPER = (0x3D, 0, 127, 0, 127)

    # WMT2 Wave Switch
    WMT2_WAVE_SWITCH = (0x3E, 0, 1, 0, 1)  # OFF, ON

    # WMT2 Wave Group Type
    WMT2_WAVE_GROUP_TYPE = (0x3F, 0, 0, 0, 0)  # Only one preset_type

    # WMT2 Wave Group ID
    WMT2_WAVE_GROUP_ID = (0x40, 0, 16384, 0, 16384)  # OFF, 1 - 16384

    # WMT2 Wave Number L (Mono)
    WMT2_WAVE_NUMBER_L = (0x44, 0, 16384, 0, 16384)  # OFF, 1 - 16384

    # WMT2 Wave Number R
    WMT2_WAVE_NUMBER_R = (0x48, 0, 16384, 0, 16384)  # OFF, 1 - 16384

    # WMT2 Wave Gain
    WMT2_WAVE_GAIN = (0x4C, 0, 3, 0, 3)  # -6, 0, +6, +12 [dB]

    # WMT2 Wave FXM Switch
    WMT2_WAVE_FXM_SWITCH = (0x4D, 0, 1, 0, 1)  # OFF, ON

    # WMT2 Wave FXM Color
    WMT2_WAVE_FXM_COLOR = (0x4E, 0, 3, 1, 4)  # 1 - 4

    # WMT2 Wave FXM Depth
    WMT2_WAVE_FXM_DEPTH = (0x4F, 0, 16, 0, 16)

    # WMT2 Wave Tempo Sync
    WMT2_WAVE_TEMPO_SYNC = (0x50, 0, 1, 0, 1)  # OFF, ON

    # WMT2 Wave Coarse Tune
    WMT2_WAVE_COARSE_TUNE = (0x51, 16, 112, 16, 112)  # -48 - +48

    # WMT2 Wave Fine Tune
    WMT2_WAVE_FINE_TUNE = (0x52, 14, 114, 14, 114)  # -50 - +50

    # WMT2 Wave Pan
    WMT2_WAVE_PAN = (0x53, 0, 127, 0, 127)  # L64 - 63R

    # WMT2 Wave Random Pan Switch
    WMT2_WAVE_RANDOM_PAN_SWITCH = (0x54, 0, 1, 0, 1)  # OFF, ON

    # WMT2 Wave Alternate Pan Switch
    WMT2_WAVE_ALTERNATE_PAN_SWITCH = (0x55, 0, 2, 0, 2)  # OFF, ON, REVERSE

    # WMT2 Wave Level
    WMT2_WAVE_LEVEL = (0x56, 0, 127, 0, 127)

    # WMT2 Velocity Range Lower
    WMT2_VELOCITY_RANGE_LOWER = (0x57, 1, 127, 1, 127)  # 1 - UPPER

    # WMT2 Velocity Range Upper
    WMT2_VELOCITY_RANGE_UPPER = (0x58, 1, 127, 1, 127)  # LOWER - 127

    # WMT2 Velocity Fade Width Lower
    WMT2_VELOCITY_FADE_WIDTH_LOWER = (0x59, 0, 127, 0, 127)

    # WMT2 Velocity Fade Width Upper
    WMT2_VELOCITY_FADE_WIDTH_UPPER = (0x5A, 0, 127, 0, 127)

    # WMT3 Wave Switch
    WMT3_WAVE_SWITCH = (0x5B, 0, 1, 0, 1)  # OFF, ON

    # WMT3 Wave Group Type
    WMT3_WAVE_GROUP_TYPE = (0x5C, 0, 0, 0, 0)  # Only one preset_type

    # WMT3 Wave Group ID
    WMT3_WAVE_GROUP_ID = (0x5D, 0, 16384, 0, 16384)  # OFF, 1 - 16384

    # WMT3 Wave Number L (Mono)
    WMT3_WAVE_NUMBER_L = (0x61, 0, 16384, 0, 16384)  # OFF, 1 - 16384

    # WMT3 Wave Number R
    WMT3_WAVE_NUMBER_R = (0x65, 0, 16384, 0, 16384)  # OFF, 1 - 16384

    # WMT3 Wave Gain
    WMT3_WAVE_GAIN = (0x69, 0, 3, 0, 3)  # -6, 0, +6, +12 [dB]

    # WMT3 Wave FXM Switch
    WMT3_WAVE_FXM_SWITCH = (0x6A, 0, 1, 0, 1)  # OFF, ON

    # WMT3 Wave FXM Color
    WMT3_WAVE_FXM_COLOR = (0x6B, 0, 3, 0, 3)  # 1 - 4

    # WMT3 Wave FXM Depth
    WMT3_WAVE_FXM_DEPTH = (0x6C, 0, 16, 0, 16)

    # WMT3 Wave Tempo Sync
    WMT3_WAVE_TEMPO_SYNC = (0x6D, 0, 1, 0, 1)  # OFF, ON

    # WMT3 Wave Coarse Tune
    WMT3_WAVE_COARSE_TUNE = (0x6E, 16, 112, 16, 112)  # -48 - +48

    # WMT3 Wave Fine Tune
    WMT3_WAVE_FINE_TUNE = (0x6F, 14, 114, 14, 114)  # -50 - +50

    # WMT3 Wave Pan
    WMT3_WAVE_PAN = (0x70, 0, 127, 0, 127)  # L64 - 63R

    # WMT3 Wave Random Pan Switch
    WMT3_WAVE_RANDOM_PAN_SWITCH = (0x71, 0, 1, 0, 1)  # OFF, ON

    # WMT3 Wave Alternate Pan Switch
    WMT3_WAVE_ALTERNATE_PAN_SWITCH = (0x72, 0, 2, 0, 2)  # OFF, ON, REVERSE

    # WMT3 Wave Level
    WMT3_WAVE_LEVEL = (0x73, 0, 127, 0, 127)

    # WMT3 Velocity Range Lower
    WMT3_VELOCITY_RANGE_LOWER = (0x74, 1, 127, 1, 127)  # 1 - UPPER

    # WMT3 Velocity Range Upper
    WMT3_VELOCITY_RANGE_UPPER = (0x75, 1, 127, 1, 127)  # LOWER - 127

    # WMT3 Velocity Fade Width Lower
    WMT3_VELOCITY_FADE_WIDTH_LOWER = (0x76, 0, 127, 0, 127)

    # WMT3 Velocity Fade Width Upper
    WMT3_VELOCITY_FADE_WIDTH_UPPER = (0x77, 0, 127, 0, 127)

    # WMT4 Wave Switch
    WMT4_WAVE_SWITCH = (0x78, 0, 1, 0, 1)  # OFF, ON

    # WMT4 Wave Group Type
    WMT4_WAVE_GROUP_TYPE = (0x79, 0, 0, 0, 0)  # Only one preset_type

    # WMT4 Wave Group ID
    WMT4_WAVE_GROUP_ID = (0x7A, 0, 16384, 0, 16384)  # OFF, 1 - 16384

    # WMT4 Wave Number L (Mono)
    WMT4_WAVE_NUMBER_L = (0x7E, 0, 16384, 0, 16384)  # OFF, 1 - 16384

    # WMT4 Wave Number R
    WMT4_WAVE_NUMBER_R = (0x102, 0, 16384, 0, 16384)  # OFF, 1 - 16384

    # WMT4 Wave Gain
    WMT4_WAVE_GAIN = (0x106, 0, 3, 0, 3)  # -6, 0, +6, +12 [dB]

    # WMT4 Wave FXM Switch
    WMT4_WAVE_FXM_SWITCH = (0x107, 0, 1, 0, 1)  # OFF, ON

    # WMT4 Wave FXM Color
    WMT4_WAVE_FXM_COLOR = (0x108, 0, 3, 0, 3)  # 1 - 4

    # WMT4 Wave FXM Depth
    WMT4_WAVE_FXM_DEPTH = (0x109, 0, 16, 0, 16)

    # WMT4 Wave Tempo Sync
    WMT4_WAVE_TEMPO_SYNC = (0x10A, 0, 1, 0, 1)  # OFF, ON

    # WMT4 Wave Coarse Tune
    WMT4_WAVE_COARSE_TUNE = (0x10B, 16, 112, 16, 112)  # -48 - +48

    # WMT4 Wave Fine Tune
    WMT4_WAVE_FINE_TUNE = (0x10C, 14, 114, 14, 114)  # -50 - +50

    # WMT4 Wave Pan
    WMT4_WAVE_PAN = (0x10D, 0, 127, 0, 127)  # L64 - 63R

    # WMT4 Wave Random Pan Switch
    WMT4_WAVE_RANDOM_PAN_SWITCH = (0x10E, 0, 1, 0, 1)  # OFF, ON

    # WMT4 Wave Alternate Pan Switch
    WMT4_WAVE_ALTERNATE_PAN_SWITCH = (0x10F, 0, 2, 0, 2)  # OFF, ON, REVERSE

    # WMT4 Wave Level
    WMT4_WAVE_LEVEL = (0x110, 0, 127, 0, 127)

    # WMT4 Velocity Range Lower
    WMT4_VELOCITY_RANGE_LOWER = (0x111, 1, 127, 1, 127)  # 1 - UPPER

    # WMT4 Velocity Range Upper
    WMT4_VELOCITY_RANGE_UPPER = (0x112, 1, 127, 1, 127)  # LOWER - 127

    # WMT4 Velocity Fade Width Lower
    WMT4_VELOCITY_FADE_WIDTH_LOWER = (0x113, 0, 127, 0, 127)

    # WMT4 Velocity Fade Width Upper
    WMT4_VELOCITY_FADE_WIDTH_UPPER = (0x114, 0, 127, 0, 127)

    # Pitch Env Depth
    PITCH_ENV_DEPTH = (0x115, 52, 76, 52, 76)  # -12 - +12

    # Pitch Env Velocity Sens
    PITCH_ENV_VELOCITY_SENS = (0x116, 1, 127, 1, 127)  # -63 - +63

    # Pitch Env Time 1 Velocity Sens
    PITCH_ENV_TIME_1_VELOCITY_SENS = (0x117, 1, 127, 1, 127)  # -63 - +63

    # Pitch Env Time 4 Velocity Sens
    PITCH_ENV_TIME_4_VELOCITY_SENS = (0x118, 1, 127, 1, 127)  # -63 - +63

    # Pitch Env Time 1
    PITCH_ENV_TIME_1 = (0x119, 0, 127, 0, 127)

    # Pitch Env Time 2
    PITCH_ENV_TIME_2 = (0x11A, 0, 127, 0, 127)

    # Pitch Env Time 3
    PITCH_ENV_TIME_3 = (0x11B, 0, 127, 0, 127)

    # Pitch Env Time 4
    PITCH_ENV_TIME_4 = (0x11C, 0, 127, 0, 127)

    # Pitch Env Level 0
    PITCH_ENV_LEVEL_0 = (0x11D, 1, 127, 1, 127)  # -63 - +63

    # Pitch Env Level 1
    PITCH_ENV_LEVEL_1 = (0x11E, 1, 127, 1, 127)  # -63 - +63

    # Pitch Env Level 2
    PITCH_ENV_LEVEL_2 = (0x11F, 1, 127, 1, 127)  # -63 - +63

    # Pitch Env Level 3
    PITCH_ENV_LEVEL_3 = (0x120, 1, 127, 1, 127)  # -63 - +63

    # Pitch Env Level 4
    PITCH_ENV_LEVEL_4 = (0x121, 1, 127, 1, 127)  # -63 - +63

    # TVF Filter Type
    TVF_FILTER_TYPE = (0x122, 0, 6, 0, 6)  # OFF, LPF, BPF, HPF, PKG, LPF2, LPF3

    # TVF Cutoff Frequency
    TVF_CUTOFF_FREQUENCY = (0x123, 0, 127, 0, 127)

    # TVF Cutoff Velocity Curve
    TVF_CUTOFF_VELOCITY_CURVE = (0x124, 0, 7, 0, 7)  # FIXED, 1 - 7

    # TVF Cutoff Velocity Sens
    TVF_CUTOFF_VELOCITY_SENS = (0x125, 1, 127, 1, 127)  # -63 - +63

    # TVF Resonance
    TVF_RESONANCE = (0x126, 0, 127, 0, 127)

    # TVF Resonance Velocity Sens
    TVF_RESONANCE_VELOCITY_SENS = (0x127, 1, 127, 1, 127)  # -63 - +63

    # TVF Env Depth
    TVF_ENV_DEPTH = (0x128, 1, 127, 1, 127)  # -63 - +63

    # TVF Env Velocity Curve Type
    TVF_ENV_VELOCITY_CURVE_TYPE = (0x129, 0, 7, 0, 7)  # FIXED, 1 - 7

    # TVF Env Velocity Sens
    TVF_ENV_VELOCITY_SENS = (0x137, 1, 127, 1, 127)  # -63 - +63

    # TVF Env Time 1 Velocity Sens
    TVF_ENV_TIME_1_VELOCITY_SENS = (0x12B, 1, 127, 1, 127)  # -63 - +63

    # TVF Env Time 4 Velocity Sens
    TVF_ENV_TIME_4_VELOCITY_SENS = (0x12C, 1, 127, 1, 127)  # -63 - +63

    # TVF Env Time 1
    TVF_ENV_TIME_1 = (0x12D, 0, 127, 0, 127)

    # TVF Env Time 2
    TVF_ENV_TIME_2 = (0x12E, 0, 127, 0, 127)

    # TVF Env Time 3
    TVF_ENV_TIME_3 = (0x12F, 0, 127, 0, 127)

    # TVF Env Time 4
    TVF_ENV_TIME_4 = (0x130, 0, 127, 0, 127)

    # TVF Env Level 0
    TVF_ENV_LEVEL_0 = (0x131, 0, 127, 0, 127)

    # TVF Env Level 1
    TVF_ENV_LEVEL_1 = (0x132, 0, 127, 0, 127)

    # TVF Env Level 2
    TVF_ENV_LEVEL_2 = (0x133, 0, 127, 0, 127)

    # TVF Env Level 3
    TVF_ENV_LEVEL_3 = (0x134, 0, 127, 0, 127)

    # TVF Env Level 4
    TVF_ENV_LEVEL_4 = (0x135, 0, 127, 0, 127)

    # TVA Level Velocity Curve
    TVA_LEVEL_VELOCITY_CURVE = (0x136, 0, 7, 0, 7)  # FIXED, 1 - 7

    # TVA Level Velocity Sens
    TVA_LEVEL_VELOCITY_SENS = (0x137, 1, 127, 1, 127)  # -63 - +63

    # TVA Env Time 1 Velocity Sens
    TVA_ENV_TIME_1_VELOCITY_SENS = (0x138, 1, 127, 1, 127)  # -63 - +63

    # TVA Env Time 4 Velocity Sens
    TVA_ENV_TIME_4_VELOCITY_SENS = (0x139, 1, 127, 1, 127)  # -63 - +63

    # TVA Env Time 1
    TVA_ENV_TIME_1 = (0x13A, 0, 127, 0, 127)

    # TVA Env Time 2
    TVA_ENV_TIME_2 = (0x13B, 0, 127, 0, 127)

    # TVA Env Time 3
    TVA_ENV_TIME_3 = (0x13C, 0, 127, 0, 127)

    # TVA Env Time 4
    TVA_ENV_TIME_4 = (0x13D, 0, 127, 0, 127)

    # TVA Env Level 1
    TVA_ENV_LEVEL_1 = (0x13E, 0, 127, 0, 127)

    # TVA Env Level 2
    TVA_ENV_LEVEL_2 = (0x13F, 0, 127, 0, 127)

    # TVA Env Level 3
    TVA_ENV_LEVEL_3 = (0x140, 0, 127, 0, 127)

    # One Shot Mode
    ONE_SHOT_MODE = (0x141, 0, 1, 0, 1)  # OFF, ON

    # Relative Level
    RELATIVE_LEVEL = (0x142, 0, 127, 0, 127)  # -64 - +63

    DRUM_PART = (0x70, 1, 5, 1, 5)  # Hack alert @@

    DRUM_GROUP = (0x2F, 1, 5, 1, 5)  # Hack alert @@

    # Define only relevant parameters for DrumParameter
    # TVF_ENV_TIME_4 = (0x2F, 0x13E, 0, 127)
    # TVF_ENV_LEVEL_0 = (0x2F, 0x13F, 0, 127)
    # Add other relevant drum parameters here

    # def __init__(self, address: int, min_val: int, max_val: int):
    #    self.address = address
    #    self.min_val = min_val
    #    self.max_val = max_val

    def validate_value(self, value: int) -> int:
        """Validate and convert parameter value to MIDI range (0-127)"""
        if not isinstance(value, int):
            raise ValueError(f"Value must be integer, got {type(value)}")

        # Ensure value is in valid MIDI range
        if value < 0 or value > 127:
            raise ValueError(
                f"MIDI value {value} out of range for {self.name} (must be 0-127)"
            )

        return value

    def convert_from_display(self, display_value: int) -> int:
        """Convert from display value to MIDI value (0-127)"""
        return display_value

    def get_display_value(self) -> Tuple[int, int]:
        """Get the display range for the parameter"""
        return self.display_min, self.display_max

    @staticmethod
    def get_address_for_partial(partial_index: int) -> tuple:
        """Get the address for address drum partial by index"""
        if not isinstance(partial_index, int):
            raise ValueError(f"Partial index must be an integer, got {type(partial_index)}")

        if partial_index < 0 or partial_index >= 72:
            raise ValueError(f"Invalid partial index: {partial_index}")

        group_map = {
            0: 0x00, # Common parameters
            36: 0x2E, # Drum Kit Partial (Key # 36)
            37: 0x30, # Drum Kit Partial (Key # 37)
            38: 0x32, # Drum Kit Partial (Key # 38)
            39: 0x34, # Drum Kit Partial (Key # 39)
            40: 0x36, # Drum Kit Partial (Key # 40)
            41: 0x38, # Drum Kit Partial (Key # 41)
            42: 0x3A, # Drum Kit Partial (Key # 42)
            43: 0x3C, # Drum Kit Partial (Key # 43)
            44: 0x3E, # Drum Kit Partial (Key # 44)
            45: 0x40, # Drum Kit Partial (Key # 45)
            46: 0x42, # Drum Kit Partial (Key # 46)
            47: 0x44, # Drum Kit Partial (Key # 47)
            48: 0x46, # Drum Kit Partial (Key # 48)
            49: 0x48, # Drum Kit Partial (Key # 49)
            50: 0x4A, # Drum Kit Partial (Key # 50)
            51: 0x4C, # Drum Kit Partial (Key # 51)
            52: 0x4E, # Drum Kit Partial (Key # 52)
            53: 0x50, # Drum Kit Partial (Key # 53)
            54: 0x52, # Drum Kit Partial (Key # 54)
            55: 0x54, # Drum Kit Partial (Key # 55)
            56: 0x56, # Drum Kit Partial (Key # 56)
            57: 0x58, # Drum Kit Partial (Key # 57)
            58: 0x5A, # Drum Kit Partial (Key # 58)
            59: 0x5C, # Drum Kit Partial (Key # 59)
            60: 0x5E, # Drum Kit Partial (Key # 60)
            61: 0x60, # Drum Kit Partial (Key # 61)
            62: 0x62, # Drum Kit Partial (Key # 62)
            63: 0x64, # Drum Kit Partial (Key # 63)
            64: 0x66, # Drum Kit Partial (Key # 64)
            65: 0x68, # Drum Kit Partial (Key # 65)
            66: 0x6A, # Drum Kit Partial (Key # 66)
            67: 0x6C, # Drum Kit Partial (Key # 67)
            68: 0x6E, # Drum Kit Partial (Key # 68)
            69: 0x70, # Drum Kit Partial (Key # 69)
            70: 0x72, # Drum Kit Partial (Key # 70)
            71: 0x74, # Drum Kit Partial (Key # 71)
            72: 0x76, # Drum Kit Partial (Key # 72)

        }
        group = group_map.get(partial_index, 0x2E)  # Default to 0x2E if partial_name is not 1, 2, or 3
        return group

    @staticmethod
    def get_address_for_partial_name(partial_name: str) -> int:
        """Get parameter group and address adjusted for partial number."""

        address_map = {
            "COM": 0x00,  # Common parameters
            "BD1": 0x2E,  # Drum Kit Partial (Key # 36)
            "RIM": 0x30,  # Drum Kit Partial (Key # 37)
            "BD2": 0x32,  # Drum Kit Partial (Key # 38)
            "CLAP": 0x34,  # Drum Kit Partial (Key # 39)
            "BD3": 0x36,  # Drum Kit Partial (Key # 40)
            "SD1": 0x38,  # Drum Kit Partial (Key # 41)
            "CHH": 0x3A,  # Drum Kit Partial (Key # 42)
            "SD2": 0x3C,  # Drum Kit Partial (Key # 43)
            "PHH": 0x3E,  # Drum Kit Partial (Key # 44)
            "SD3": 0x40,  # Drum Kit Partial (Key # 45)
            "OHH": 0x42,  # Drum Kit Partial (Key # 46)
            "SD4": 0x44,  # Drum Kit Partial (Key # 47)
            "TOM1": 0x46,  # Drum Kit Partial (Key # 48)
            "PRC1": 0x48,  # Drum Kit Partial (Key # 49)
            "TOM2": 0x4A,  # Drum Kit Partial (Key # 50)
            "PRC2": 0x4C,  # Drum Kit Partial (Key # 51)
            "TOM3": 0x4E,  # Drum Kit Partial (Key # 52)
            "PRC3": 0x50,  # Drum Kit Partial (Key # 53)
            "CYM1": 0x52,  # Drum Kit Partial (Key # 54)
            "PRC4": 0x54,  # Drum Kit Partial (Key # 55)
            "CYM2": 0x56,  # Drum Kit Partial (Key # 56)
            "PRC5": 0x58,  # Drum Kit Partial (Key # 57)
            "CYM3": 0x5A,  # Drum Kit Partial (Key # 58)
            "HIT": 0x5C,  # Drum Kit Partial (Key # 59)
            "OTH1": 0x5E,  # Drum Kit Partial (Key # 60)
            "OTH2": 0x60,  # Drum Kit Partial (Key # 61)
            "D4": 0x62,  # Drum Kit Partial (Key # 62)
            "Eb4": 0x64,  # Drum Kit Partial (Key # 63)
            "E4": 0x66,  # Drum Kit Partial (Key # 64)
            "F4": 0x68,  # Drum Kit Partial (Key # 65)
            "F#4": 0x6A,  # Drum Kit Partial (Key # 66)
            "G4": 0x6C,  # Drum Kit Partial (Key # 67)
            "G#4": 0x6E,  # Drum Kit Partial (Key # 68)
            "A4": 0x70,  # Drum Kit Partial (Key # 69)
            "Bb4": 0x72,  # Drum Kit Partial (Key # 70)
            "B4": 0x74,  # Drum Kit Partial (Key # 71)
            "C5": 0x76,  # Drum Kit Partial (Key # 72)
        }
        address = address_map.get(partial_name, 0x00)  # Default to 0x00 for common area
        return address

    @staticmethod
    def get_by_name(param_name):
        """Get the AnalogParameter by name."""
        # Return the parameter member by name, or None if not found
        return DrumParameter.__members__.get(param_name, None)

    def convert_from_midi(self, midi_value: int) -> int:
        """Convert from MIDI value to display value"""
        return midi_value


class DrumCommonParameter(SynthParameter):
    """Common parameters for Digital/SuperNATURAL synth tones.
    These parameters are shared across all partials.
    """

    def __init__(self, address: int, min_val: int, max_val: int):
        super().__init__(address, min_val, max_val)
        self.address = address
        self.min_val = min_val
        self.max_val = max_val

    # Tone name parameters (12 ASCII characters)
    TONE_NAME_1 = (0x00, 32, 127)  # ASCII character 1
    TONE_NAME_2 = (0x01, 32, 127)  # ASCII character 2
    TONE_NAME_3 = (0x02, 32, 127)  # ASCII character 3
    TONE_NAME_4 = (0x03, 32, 127)  # ASCII character 4
    TONE_NAME_5 = (0x04, 32, 127)  # ASCII character 5
    TONE_NAME_6 = (0x05, 32, 127)  # ASCII character 6
    TONE_NAME_7 = (0x06, 32, 127)  # ASCII character 7
    TONE_NAME_8 = (0x07, 32, 127)  # ASCII character 8
    TONE_NAME_9 = (0x08, 32, 127)  # ASCII character 9
    TONE_NAME_10 = (0x09, 32, 127)  # ASCII character 10
    TONE_NAME_11 = (0x0A, 32, 127)  # ASCII character 11
    TONE_NAME_12 = (0x0B, 32, 127)  # ASCII character 12

    # Tone level
    KIT_LEVEL = (0x0C, 0, 127)  # Overall tone level

    @property
    def display_name(self) -> str:
        """Get display name for the parameter"""
        return {
            self.RING_SWITCH: "Ring Mod",
            self.UNISON_SWITCH: "Unison",
            self.PORTAMENTO_MODE: "Porto Mode",
            self.LEGATO_SWITCH: "Legato",
            self.ANALOG_FEEL: "Analog Feel",
            self.WAVE_SHAPE: "Wave Shape",
            self.TONE_CATEGORY: "Category",
            self.UNISON_SIZE: "Uni Size",
        }.get(self, self.name.replace("_", " ").title())

    def get_address_for_partial(self, partial_num: int = 0) -> int:
        """Get parameter group and address adjusted for partial number."""
        group_map = {0: 0x00}
        group = group_map.get(partial_num, 0x00)  # Default to 0x20 if partial_name is not 1, 2, or 3
        return group

    @property
    def is_switch(self) -> bool:
        """Returns True if parameter is address binary/enum switch"""
        return self in [
            self.PORTAMENTO_SWITCH,
            self.MONO_SWITCH,
            self.PARTIAL1_SWITCH,
            self.PARTIAL1_SELECT,
            self.PARTIAL2_SWITCH,
            self.PARTIAL2_SELECT,
            self.PARTIAL3_SWITCH,
            self.PARTIAL3_SELECT,
            self.RING_SWITCH,
            self.UNISON_SWITCH,
            self.PORTAMENTO_MODE,
            self.LEGATO_SWITCH,
        ]

    def get_switch_text(self, value: int) -> str:
        """Get display text for switch values"""
        if self == self.RING_SWITCH:
            return ["OFF", "---", "ON"][value]
        elif self == self.PORTAMENTO_MODE:
            return ["NORMAL", "LEGATO"][value]
        elif self == self.UNISON_SIZE:
            return f"{value + 2} VOICE"  # 0=2 voices, 1=3 voices, etc.
        elif self.is_switch:
            return "ON" if value else "OFF"
        return str(value)

    def validate_value(self, value: int) -> int:
        """Validate and convert parameter value"""
        if not isinstance(value, int):
            raise ValueError(f"Value must be integer, got {type(value)}")

        # Special handling for ring switch
        if self == self.RING_SWITCH and value == 1:
            # Skip over the "---" value
            value = 2

        # Regular range check
        if value < self.min_val or value > self.max_val:
            raise ValueError(
                f"Value {value} out of range for {self.name} "
                f"(valid range: {self.min_val}-{self.max_val})"
            )

        return value

    def get_partial_number(self) -> Optional[int]:
        """Returns the partial number (1-3) if this is address partial parameter, None otherwise"""
        partial_params = {
            self.PARTIAL1_SWITCH: 1,
            self.PARTIAL1_SELECT: 1,
            self.PARTIAL2_SWITCH: 2,
            self.PARTIAL2_SELECT: 2,
            self.PARTIAL3_SWITCH: 3,
            self.PARTIAL3_SELECT: 3,
        }
        return partial_params.get(self)

    @staticmethod
    def get_by_name(param_name):
        """Get the Parameter by name."""
        # Return the parameter member by name, or None if not found
        return DigitalCommonParameter.__members__.get(param_name, None)

