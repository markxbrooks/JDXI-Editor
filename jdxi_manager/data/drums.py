from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, List, Tuple

DRUM_PARTIAL_NAMES = [
    "COM",
    "BD1",
    "RIM",
    "BD2",
    "CLAP",
    "BD3",
    "SD1",
    "CHH",
    "SD2",
    "PHH",
    "SD3",
    "OHH",
    "SD4",
    "TOM1",
    "PRC1",
    "TOM2",
    "PRC2",
    "TOM3",
    "PRC3",
    "CYM1",
    "PRC4",
    "CYM2",
    "PRC5",
    "CYM3",
    "HIT",
    "OTH1",
    "OTH2",
    "D4",
    "Eb4",
    "E4",
    "F4",
    "F#4",
    "G4",
    "G#4",
    "A4",
    "Bb4",
    "B4",
    "C5",
    "C#5",
]

DRUM_ADDRESSES = (
    b"\x19\x70\x00\x00",
    b"\x19\x70\x2E\x00",
    b"\x19\x70\x30\x00",
    b"\x19\x70\x32\x00",
    b"\x19\x70\x34\x00",
    b"\x19\x70\x36\x00",
    b"\x19\x70\x38\x00",
    b"\x19\x70\x3A\x00",
    b"\x19\x70\x3C\x00",
    b"\x19\x70\x3E\x00",
    b"\x19\x70\x40\x00",
    b"\x19\x70\x42\x00",
    b"\x19\x70\x44\x00",
    b"\x19\x70\x46\x00",
    b"\x19\x70\x48\x00",
    b"\x19\x70\x4A\x00",
    b"\x19\x70\x4C\x00",
    b"\x19\x70\x4E\x00",
    b"\x19\x70\x50\x00",
    b"\x19\x70\x52\x00",
    b"\x19\x70\x54\x00",
    b"\x19\x70\x56\x00",
    b"\x19\x70\x58\x00",
    b"\x19\x70\x5A\x00",
    b"\x19\x70\x5C\x00",
    b"\x19\x70\x5E\x00",
    b"\x19\x70\x60\x00",
    b"\x19\x70\x62\x00",
    b"\x19\x70\x64\x00",
    b"\x19\x70\x66\x00",
    b"\x19\x70\x68\x00",
    b"\x19\x70\x6A\x00",
    b"\x19\x70\x6C\x00",
    b"\x19\x70\x6E\x00",
    b"\x19\x70\x70\x00",
    b"\x19\x70\x72\x00",
    b"\x19\x70\x74\x00",
    b"\x19\x70\x76\x00",
    b"\x19\x70\x78\x00",
)


def get_address_for_partial(partial_num: int) -> Tuple[int, int]:
    """Get parameter group and address adjusted for partial number"""
    LO = DRUM_ADDRESSES[partial_num + 1][
        2
    ]  # Skip the first row (common area), then extract the 3rd byte (zero-based index)
    HI = LO + 1
    return int(f"{LO:02X}", 16), int(f"{HI:02X}", 16)


class DrumParameter(Enum):
    """Drum kit parameters with their addresses and value ranges"""

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
    MUTE_GROUP = (0x0D, 0, 31)  # OFF, 1 - 31

    # Partial Level
    PARTIAL_LEVEL = (0x0E, 0, 127)

    # Partial Coarse Tune
    PARTIAL_COARSE_TUNE = (0x0F, 0, 127)  # C-1 - G9

    # Partial Fine Tune
    PARTIAL_FINE_TUNE = (0x10, 14, 114)  # -50 - +50

    # Partial Random Pitch Depth
    PARTIAL_RANDOM_PITCH_DEPTH = (0x11, 0, 30)

    # Partial Pan
    PARTIAL_PAN = (0x12, 0, 127)  # L64 - 63R

    # Partial Random Pan Depth
    PARTIAL_RANDOM_PAN_DEPTH = (0x13, 0, 63)

    # Partial Alternate Pan Depth
    PARTIAL_ALTERNATE_PAN_DEPTH = (0x14, 1, 127)  # L63 - 63R

    # Partial Env Mode
    PARTIAL_ENV_MODE = (0x15, 0, 1)  # NO-SUS, SUSTAIN

    # Partial Output Level
    PARTIAL_OUTPUT_LEVEL = (0x16, 0, 127)

    # Partial Chorus Send Level
    PARTIAL_CHORUS_SEND_LEVEL = (0x19, 0, 127)

    # Partial Reverb Send Level
    PARTIAL_REVERB_SEND_LEVEL = (0x1A, 0, 127)

    # Partial Output Assign
    PARTIAL_OUTPUT_ASSIGN = (0x1B, 0, 4)  # EFX1, EFX2, DLY, REV, DIR

    # Partial Pitch Bend Range
    PARTIAL_PITCH_BEND_RANGE = (0x1C, 0, 48)

    # Partial Receive Expression
    PARTIAL_RECEIVE_EXPRESSION = (0x1D, 0, 1)  # OFF, ON

    # Partial Receive Hold-1
    PARTIAL_RECEIVE_HOLD_1 = (0x1E, 0, 1)  # OFF, ON

    # WMT Velocity Control
    WMT_VELOCITY_CONTROL = (0x20, 0, 2)  # OFF, ON, RANDOM

    # WMT1 Wave Switch
    WMT1_WAVE_SWITCH = (0x21, 0, 1)  # OFF, ON

    # WMT1 Wave Group Type
    WMT1_WAVE_GROUP_TYPE = (0x22, 0, 0)  # Only one type

    # WMT1 Wave Group ID
    WMT1_WAVE_GROUP_ID = (0x23, 0, 16384)  # OFF, 1 - 16384

    # WMT1 Wave Number L (Mono)
    WMT1_WAVE_NUMBER_L = (0x27, 0, 16384)  # OFF, 1 - 16384

    # WMT1 Wave Number R
    WMT1_WAVE_NUMBER_R = (0x2B, 0, 16384)  # OFF, 1 - 16384

    # WMT1 Wave Gain
    WMT1_WAVE_GAIN = (0x2F, 0, 3)  # -6, 0, +6, +12 [dB]

    # WMT1 Wave FXM Switch
    WMT1_WAVE_FXM_SWITCH = (0x30, 0, 1)  # OFF, ON

    # WMT1 Wave FXM Color
    WMT1_WAVE_FXM_COLOR = (0x31, 0, 3)  # 1 - 4

    # WMT1 Wave FXM Depth
    WMT1_WAVE_FXM_DEPTH = (0x32, 0, 16)

    # WMT1 Wave Tempo Sync
    WMT1_WAVE_TEMPO_SYNC = (0x33, 0, 1)  # OFF, ON

    # WMT1 Wave Coarse Tune
    WMT1_WAVE_COARSE_TUNE = (0x34, 16, 112)  # -48 - +48

    # WMT1 Wave Fine Tune
    WMT1_WAVE_FINE_TUNE = (0x35, 14, 114)  # -50 - +50

    # WMT1 Wave Pan
    WMT1_WAVE_PAN = (0x36, 0, 127)  # L64 - 63R

    # WMT1 Wave Random Pan Switch
    WMT1_WAVE_RANDOM_PAN_SWITCH = (0x37, 0, 1)  # OFF, ON

    # WMT1 Wave Alternate Pan Switch
    WMT1_WAVE_ALTERNATE_PAN_SWITCH = (0x38, 0, 2)  # OFF, ON, REVERSE

    # WMT1 Wave Level
    WMT1_WAVE_LEVEL = (0x39, 0, 127)

    # WMT1 Velocity Range Lower
    WMT1_VELOCITY_RANGE_LOWER = (0x3A, 1, 127)  # 1 - UPPER

    # WMT1 Velocity Range Upper
    WMT1_VELOCITY_RANGE_UPPER = (0x3B, 1, 127)  # LOWER - 127

    # WMT1 Velocity Fade Width Lower
    WMT1_VELOCITY_FADE_WIDTH_LOWER = (0x3C, 0, 127)

    # WMT1 Velocity Fade Width Upper
    WMT1_VELOCITY_FADE_WIDTH_UPPER = (0x3D, 0, 127)

    # WMT2 Wave Switch
    WMT2_WAVE_SWITCH = (0x3E, 0, 1)  # OFF, ON

    # WMT2 Wave Group Type
    WMT2_WAVE_GROUP_TYPE = (0x3F, 0, 0)  # Only one type

    # WMT2 Wave Group ID
    WMT2_WAVE_GROUP_ID = (0x40, 0, 16384)  # OFF, 1 - 16384

    # WMT2 Wave Number L (Mono)
    WMT2_WAVE_NUMBER_L = (0x44, 0, 16384)  # OFF, 1 - 16384

    # WMT2 Wave Number R
    WMT2_WAVE_NUMBER_R = (0x48, 0, 16384)  # OFF, 1 - 16384

    # WMT2 Wave Gain
    WMT2_WAVE_GAIN = (0x4C, 0, 3)  # -6, 0, +6, +12 [dB]

    # WMT2 Wave FXM Switch
    WMT2_WAVE_FXM_SWITCH = (0x4D, 0, 1)  # OFF, ON

    # WMT2 Wave FXM Color
    WMT2_WAVE_FXM_COLOR = (0x4E, 0, 3)  # 1 - 4

    # WMT2 Wave FXM Depth
    WMT2_WAVE_FXM_DEPTH = (0x4F, 0, 16)

    # WMT2 Wave Tempo Sync
    WMT2_WAVE_TEMPO_SYNC = (0x50, 0, 1)  # OFF, ON

    # WMT2 Wave Coarse Tune
    WMT2_WAVE_COARSE_TUNE = (0x51, 16, 112)  # -48 - +48

    # WMT2 Wave Fine Tune
    WMT2_WAVE_FINE_TUNE = (0x52, 14, 114)  # -50 - +50

    # WMT2 Wave Pan
    WMT2_WAVE_PAN = (0x53, 0, 127)  # L64 - 63R

    # WMT2 Wave Random Pan Switch
    WMT2_WAVE_RANDOM_PAN_SWITCH = (0x54, 0, 1)  # OFF, ON

    # WMT2 Wave Alternate Pan Switch
    WMT2_WAVE_ALTERNATE_PAN_SWITCH = (0x55, 0, 2)  # OFF, ON, REVERSE

    # WMT2 Wave Level
    WMT2_WAVE_LEVEL = (0x56, 0, 127)

    # WMT2 Velocity Range Lower
    WMT2_VELOCITY_RANGE_LOWER = (0x57, 1, 127)  # 1 - UPPER

    # WMT2 Velocity Range Upper
    WMT2_VELOCITY_RANGE_UPPER = (0x58, 1, 127)  # LOWER - 127

    # WMT2 Velocity Fade Width Lower
    WMT2_VELOCITY_FADE_WIDTH_LOWER = (0x59, 0, 127)

    # WMT2 Velocity Fade Width Upper
    WMT2_VELOCITY_FADE_WIDTH_UPPER = (0x5A, 0, 127)

    # WMT3 Wave Switch
    WMT3_WAVE_SWITCH = (0x5B, 0, 1)  # OFF, ON

    # WMT3 Wave Group Type
    WMT3_WAVE_GROUP_TYPE = (0x5C, 0, 0)  # Only one type

    # WMT3 Wave Group ID
    WMT3_WAVE_GROUP_ID = (0x5D, 0, 16384)  # OFF, 1 - 16384

    # WMT3 Wave Number L (Mono)
    WMT3_WAVE_NUMBER_L = (0x61, 0, 16384)  # OFF, 1 - 16384

    # WMT3 Wave Number R
    WMT3_WAVE_NUMBER_R = (0x65, 0, 16384)  # OFF, 1 - 16384

    # WMT3 Wave Gain
    WMT3_WAVE_GAIN = (0x69, 0, 3)  # -6, 0, +6, +12 [dB]

    # WMT3 Wave FXM Switch
    WMT3_WAVE_FXM_SWITCH = (0x6A, 0, 1)  # OFF, ON

    # WMT3 Wave FXM Color
    WMT3_WAVE_FXM_COLOR = (0x6B, 0, 3)  # 1 - 4

    # WMT3 Wave FXM Depth
    WMT3_WAVE_FXM_DEPTH = (0x6C, 0, 16)

    # WMT3 Wave Tempo Sync
    WMT3_WAVE_TEMPO_SYNC = (0x6D, 0, 1)  # OFF, ON

    # WMT3 Wave Coarse Tune
    WMT3_WAVE_COARSE_TUNE = (0x6E, 16, 112)  # -48 - +48

    # WMT3 Wave Fine Tune
    WMT3_WAVE_FINE_TUNE = (0x6F, 14, 114)  # -50 - +50

    # WMT3 Wave Pan
    WMT3_WAVE_PAN = (0x70, 0, 127)  # L64 - 63R

    # WMT3 Wave Random Pan Switch
    WMT3_WAVE_RANDOM_PAN_SWITCH = (0x71, 0, 1)  # OFF, ON

    # WMT3 Wave Alternate Pan Switch
    WMT3_WAVE_ALTERNATE_PAN_SWITCH = (0x72, 0, 2)  # OFF, ON, REVERSE

    # WMT3 Wave Level
    WMT3_WAVE_LEVEL = (0x73, 0, 127)

    # WMT3 Velocity Range Lower
    WMT3_VELOCITY_RANGE_LOWER = (0x74, 1, 127)  # 1 - UPPER

    # WMT3 Velocity Range Upper
    WMT3_VELOCITY_RANGE_UPPER = (0x75, 1, 127)  # LOWER - 127

    # WMT3 Velocity Fade Width Lower
    WMT3_VELOCITY_FADE_WIDTH_LOWER = (0x76, 0, 127)

    # WMT3 Velocity Fade Width Upper
    WMT3_VELOCITY_FADE_WIDTH_UPPER = (0x77, 0, 127)

    # WMT4 Wave Switch
    WMT4_WAVE_SWITCH = (0x78, 0, 1)  # OFF, ON

    # WMT4 Wave Group Type
    WMT4_WAVE_GROUP_TYPE = (0x79, 0, 0)  # Only one type

    # WMT4 Wave Group ID
    WMT4_WAVE_GROUP_ID = (0x7A, 0, 16384)  # OFF, 1 - 16384

    # WMT4 Wave Number L (Mono)
    WMT4_WAVE_NUMBER_L = (0x7E, 0, 16384)  # OFF, 1 - 16384

    # WMT4 Wave Number R
    WMT4_WAVE_NUMBER_R = (0x102, 0, 16384)  # OFF, 1 - 16384

    # WMT4 Wave Gain
    WMT4_WAVE_GAIN = (0x106, 0, 3)  # -6, 0, +6, +12 [dB]

    # WMT4 Wave FXM Switch
    WMT4_WAVE_FXM_SWITCH = (0x107, 0, 1)  # OFF, ON

    # WMT4 Wave FXM Color
    WMT4_WAVE_FXM_COLOR = (0x108, 0, 3)  # 1 - 4

    # WMT4 Wave FXM Depth
    WMT4_WAVE_FXM_DEPTH = (0x109, 0, 16)

    # WMT4 Wave Tempo Sync
    WMT4_WAVE_TEMPO_SYNC = (0x10A, 0, 1)  # OFF, ON

    # WMT4 Wave Coarse Tune
    WMT4_WAVE_COARSE_TUNE = (0x10B, 16, 112)  # -48 - +48

    # WMT4 Wave Fine Tune
    WMT4_WAVE_FINE_TUNE = (0x10C, 14, 114)  # -50 - +50

    # WMT4 Wave Pan
    WMT4_WAVE_PAN = (0x10D, 0, 127)  # L64 - 63R

    # WMT4 Wave Random Pan Switch
    WMT4_WAVE_RANDOM_PAN_SWITCH = (0x10E, 0, 1)  # OFF, ON

    # WMT4 Wave Alternate Pan Switch
    WMT4_WAVE_ALTERNATE_PAN_SWITCH = (0x10F, 0, 2)  # OFF, ON, REVERSE

    # WMT4 Wave Level
    WMT4_WAVE_LEVEL = (0x110, 0, 127)

    # WMT4 Velocity Range Lower
    WMT4_VELOCITY_RANGE_LOWER = (0x111, 1, 127)  # 1 - UPPER

    # WMT4 Velocity Range Upper
    WMT4_VELOCITY_RANGE_UPPER = (0x112, 1, 127)  # LOWER - 127

    # WMT4 Velocity Fade Width Lower
    WMT4_VELOCITY_FADE_WIDTH_LOWER = (0x113, 0, 127)

    # WMT4 Velocity Fade Width Upper
    WMT4_VELOCITY_FADE_WIDTH_UPPER = (0x114, 0, 127)

    # Pitch Env Depth
    PITCH_ENV_DEPTH = (0x115, 52, 76)  # -12 - +12

    # Pitch Env Velocity Sens
    PITCH_ENV_VELOCITY_SENS = (0x116, 1, 127)  # -63 - +63

    # Pitch Env Time 1 Velocity Sens
    PITCH_ENV_TIME_1_VELOCITY_SENS = (0x117, 1, 127)  # -63 - +63

    # Pitch Env Time 4 Velocity Sens
    PITCH_ENV_TIME_4_VELOCITY_SENS = (0x118, 1, 127)  # -63 - +63

    # Pitch Env Time 1
    PITCH_ENV_TIME_1 = (0x119, 0, 127)

    # Pitch Env Time 2
    PITCH_ENV_TIME_2 = (0x11A, 0, 127)

    # Pitch Env Time 3
    PITCH_ENV_TIME_3 = (0x11B, 0, 127)

    # Pitch Env Time 4
    PITCH_ENV_TIME_4 = (0x11C, 0, 127)

    # Pitch Env Level 0
    PITCH_ENV_LEVEL_0 = (0x11D, 1, 127)  # -63 - +63

    # Pitch Env Level 1
    PITCH_ENV_LEVEL_1 = (0x11E, 1, 127)  # -63 - +63

    # Pitch Env Level 2
    PITCH_ENV_LEVEL_2 = (0x11F, 1, 127)  # -63 - +63

    # Pitch Env Level 3
    PITCH_ENV_LEVEL_3 = (0x120, 1, 127)  # -63 - +63

    # Pitch Env Level 4
    PITCH_ENV_LEVEL_4 = (0x121, 1, 127)  # -63 - +63

    # TVF Filter Type
    TVF_FILTER_TYPE = (0x122, 0, 6)  # OFF, LPF, BPF, HPF, PKG, LPF2, LPF3

    # TVF Cutoff Frequency
    TVF_CUTOFF_FREQUENCY = (0x123, 0, 127)

    # TVF Cutoff Velocity Curve
    TVF_CUTOFF_VELOCITY_CURVE = (0x124, 0, 7)  # FIXED, 1 - 7

    # TVF Cutoff Velocity Sens
    TVF_CUTOFF_VELOCITY_SENS = (0x125, 1, 127)  # -63 - +63

    # TVF Resonance
    TVF_RESONANCE = (0x126, 0, 127)

    # TVF Resonance Velocity Sens
    TVF_RESONANCE_VELOCITY_SENS = (0x127, 1, 127)  # -63 - +63

    # TVF Env Depth
    TVF_ENV_DEPTH = (0x128, 1, 127)  # -63 - +63

    # TVF Env Velocity Curve Type
    TVF_ENV_VELOCITY_CURVE_TYPE = (0x129, 0, 7)  # FIXED, 1 - 7

    # TVF Env Velocity Sens
    TVF_ENV_VELOCITY_SENS = (0x137, 1, 127)  # -63 - +63

    # TVF Env Time 1 Velocity Sens
    TVF_ENV_TIME_1_VELOCITY_SENS = (0x12B, 1, 127)  # -63 - +63

    # TVF Env Time 4 Velocity Sens
    TVF_ENV_TIME_4_VELOCITY_SENS = (0x12C, 1, 127)  # -63 - +63

    # TVF Env Time 1
    TVF_ENV_TIME_1 = (0x12D, 0, 127)

    # TVF Env Time 2
    TVF_ENV_TIME_2 = (0x12E, 0, 127)

    # TVF Env Time 3
    TVF_ENV_TIME_3 = (0x12F, 0, 127)

    # TVF Env Time 4
    TVF_ENV_TIME_4 = (0x130, 0, 127)

    # TVF Env Level 0
    TVF_ENV_LEVEL_0 = (0x131, 0, 127)

    # TVF Env Level 1
    TVF_ENV_LEVEL_1 = (0x132, 0, 127)

    # TVF Env Level 2
    TVF_ENV_LEVEL_2 = (0x133, 0, 127)

    # TVF Env Level 3
    TVF_ENV_LEVEL_3 = (0x134, 0, 127)

    # TVF Env Level 4
    TVF_ENV_LEVEL_4 = (0x135, 0, 127)

    # TVA Level Velocity Curve
    TVA_LEVEL_VELOCITY_CURVE = (0x136, 0, 7)  # FIXED, 1 - 7

    # TVA Level Velocity Sens
    TVA_LEVEL_VELOCITY_SENS = (0x137, 1, 127)  # -63 - +63

    # TVA Env Time 1 Velocity Sens
    TVA_ENV_TIME_1_VELOCITY_SENS = (0x138, 1, 127)  # -63 - +63

    # TVA Env Time 4 Velocity Sens
    TVA_ENV_TIME_4_VELOCITY_SENS = (0x139, 1, 127)  # -63 - +63

    # TVA Env Time 1
    TVA_ENV_TIME_1 = (0x13A, 0, 127)

    # TVA Env Time 2
    TVA_ENV_TIME_2 = (0x13B, 0, 127)

    # TVA Env Time 3
    TVA_ENV_TIME_3 = (0x13C, 0, 127)

    # TVA Env Time 4
    TVA_ENV_TIME_4 = (0x13D, 0, 127)

    # TVA Env Level 1
    TVA_ENV_LEVEL_1 = (0x13E, 0, 127)

    # TVA Env Level 2
    TVA_ENV_LEVEL_2 = (0x13F, 0, 127)

    # TVA Env Level 3
    TVA_ENV_LEVEL_3 = (0x140, 0, 127)

    # One Shot Mode
    ONE_SHOT_MODE = (0x141, 0, 1)  # OFF, ON

    # Relative Level
    RELATIVE_LEVEL = (0x142, 0, 127)  # -64 - +63

    DRUM_PART = (0x70, 1, 5)  # Hack alert @@

    DRUM_GROUP = (0x2F, 1, 5)  # Hack alert @@

    # Define only relevant parameters for DrumParameter
    # TVF_ENV_TIME_4 = (0x2F, 0x13E, 0, 127)
    # TVF_ENV_LEVEL_0 = (0x2F, 0x13F, 0, 127)
    # Add other relevant drum parameters here

    def __init__(self, address: int, min_val: int, max_val: int):
        self.address = address
        self.min_val = min_val
        self.max_val = max_val

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


# Drum parameter offsets and ranges
DR = {
    "common": {
        "level": (0x00, 0, 127),
        "pan": (0x01, 0, 127),
        "reverb_send": (0x02, 0, 127),
        "delay_send": (0x03, 0, 127),
        "fx_send": (0x04, 0, 127),
    },
    "pad": {
        "wave": (0x00, 0, 127),
        "level": (0x01, 0, 127),
        "pan": (0x02, 0, 127),
        "tune": (0x03, -50, 50),
        "decay": (0x04, 0, 127),
        "mute_group": (0x05, 0, 31),
        "reverb_send": (0x06, 0, 127),
        "delay_send": (0x07, 0, 127),
        "fx_send": (0x08, 0, 127),
    },
}

# Drum part categories
DRUM_PARTS = {
    "KICK": ["Kick 1", "Kick 2", "Kick 3", "TR-808 Kick", "TR-909 Kick"],
    "SNARE": ["Snare 1", "Snare 2", "Rim Shot", "TR-808 Snare", "TR-909 Snare"],
    "HI_HAT": ["Closed HH", "Open HH", "Pedal HH", "TR-808 CH", "TR-808 OH"],
    "CYMBAL": ["Crash 1", "Crash 2", "Ride", "China", "Splash"],
    "TOM": ["Tom Hi", "Tom Mid", "Tom Low", "TR-808 Tom Hi", "TR-808 Tom Low"],
    "PERCUSSION": ["Conga Hi", "Conga Low", "Bongo Hi", "Bongo Low", "Timbale"],
}


class MuteGroup(Enum):
    """Drum pad mute groups"""

    OFF = 0
    GROUPS = range(1, 32)  # Groups 1-31


class Note(Enum):
    """MIDI note numbers for drum pads"""

    PAD_1 = 36  # C1
    PAD_2 = 37  # C#1
    PAD_3 = 38  # D1
    PAD_4 = 39  # D#1
    PAD_5 = 40  # E1
    PAD_6 = 41  # F1
    PAD_7 = 42  # F#1
    PAD_8 = 43  # G1
    PAD_9 = 44  # G#1
    PAD_10 = 45  # A1
    PAD_11 = 46  # A#1
    PAD_12 = 47  # B1
    PAD_13 = 48  # C2
    PAD_14 = 49  # C#2
    PAD_15 = 50  # D2
    PAD_16 = 51  # D#2


class DrumPad:
    """Represents a single drum pad's settings"""

    # Parameter offsets within each pad
    PARAM_OFFSET = 0x10  # Each pad takes 16 bytes of parameter space

    # Parameter addresses within pad
    WAVE = 0x00
    LEVEL = 0x01
    PAN = 0x02
    MUTE_GROUP = 0x03
    TUNE = 0x04
    DECAY = 0x05
    REVERB_SEND = 0x06
    DELAY_SEND = 0x07
    FX_SEND = 0x08

    def __init__(self):
        self.wave = 0
        self.level = 100
        self.pan = 64  # Center
        self.mute_group = 0
        self.tune = 0
        self.decay = 64
        self.reverb_send = 0
        self.delay_send = 0
        self.fx_send = 0


@dataclass
class DrumPadSettings:
    """Settings for a single drum pad"""

    wave: int = 0
    level: int = 100
    pan: int = 64  # Center
    tune: int = 0
    decay: int = 64
    mute_group: int = 0  # OFF
    reverb_send: int = 0
    delay_send: int = 0
    fx_send: int = 0


@dataclass
class DrumKitPatch:
    """Complete drum kit patch data"""

    # Common parameters
    level: int = 100
    pan: int = 64  # Center
    reverb_send: int = 0
    delay_send: int = 0
    fx_send: int = 0

    # Individual pad settings
    pads: Dict[int, DrumPadSettings] = None

    def __post_init__(self):
        """Initialize pad settings"""
        if self.pads is None:
            self.pads = {i: DrumPadSettings() for i in range(16)}


# SuperNATURAL drum kit presets
SN_PRESETS = [
    "001: Studio Standard",
    "002: Studio Rock",
    "003: Studio Jazz",
    "004: Studio Dance",
    "005: Studio R&B",
    "006: Studio Latin",
    "007: Power Kit",
    "008: Rock Kit",
    "009: Jazz Kit",
    "010: Brush Kit",
    "011: Orchestra Kit",
    "012: Dance Kit",
    "013: House Kit",
    "014: Hip Hop Kit",
    "015: R&B Kit",
    "016: Latin Kit",
    "017: World Kit",
    "018: Electronic Kit",
    "019: TR-808 Kit",
    "020: TR-909 Kit",
    "021: CR-78 Kit",
    "022: TR-606 Kit",
    "023: TR-707 Kit",
    "024: TR-727 Kit",
    "025: Percussion Kit",
    "026: SFX Kit",
    "027: User Kit 1",
    "028: User Kit 2",
    "029: User Kit 3",
    "030: User Kit 4",
]

# Drum kit presets
DRUM_PRESETS: Tuple[str, ...] = (
    "001: TR-909 Kit 1",
    "002: TR-808 Kit 1",
    "003: 707&727 Kit1",
    "004: CR-78 Kit 1",
    "005: TR-606 Kit 1",
    "006: TR-626 Kit 1",
    "007: EDM Kit 1",
    "008: Drum&Bs Kit1",
    "009: Techno Kit 1",
    "010: House Kit 1",
    "011: Hiphop Kit 1",
    "012: R&B Kit 1",
    "013: TR-909 Kit 2",
    "014: TR-909 Kit 3",
    "015: TR-808 Kit 2",
    "016: TR-808 Kit 3",
    "017: TR-808 Kit 4",
    "018: 808&909 Kit1",
    "019: 808&909 Kit2",
    "020: 707&727 Kit2",
    "021: 909&7*7 Kit1",
    "022: 808&7*7 Kit1",
    "023: EDM Kit 2",
    "024: Techno Kit 2",
    "025: Hiphop Kit 2",
    "026: 80's Kit 1",
    "027: 90's Kit 1",
    "028: Noise Kit 1",
    "029: Pop Kit 1",
    "030: Pop Kit 2",
    "031: Rock Kit",
    "032: Jazz Kit",
    "033: Latin Kit",
)

# Drum kit categories
DRUM_CATEGORIES: Dict[str, list] = {
    "VINTAGE ROLAND": [
        "001: TR-909 Kit 1",
        "002: TR-808 Kit 1",
        "003: 707&727 Kit1",
        "004: CR-78 Kit 1",
        "005: TR-606 Kit 1",
        "006: TR-626 Kit 1",
        "013: TR-909 Kit 2",
        "014: TR-909 Kit 3",
        "015: TR-808 Kit 2",
        "016: TR-808 Kit 3",
        "017: TR-808 Kit 4",
    ],
    "HYBRID": [
        "018: 808&909 Kit1",
        "019: 808&909 Kit2",
        "020: 707&727 Kit2",
        "021: 909&7*7 Kit1",
        "022: 808&7*7 Kit1",
    ],
    "ELECTRONIC": [
        "007: EDM Kit 1",
        "008: Drum&Bs Kit1",
        "009: Techno Kit 1",
        "023: EDM Kit 2",
        "024: Techno Kit 2",
        "028: Noise Kit 1",
    ],
    "MODERN": [
        "010: House Kit 1",
        "011: Hiphop Kit 1",
        "012: R&B Kit 1",
        "025: Hiphop Kit 2",
        "026: 80's Kit 1",
        "027: 90's Kit 1",
    ],
    "ACOUSTIC": [
        "029: Pop Kit 1",
        "030: Pop Kit 2",
        "031: Rock Kit",
        "032: Jazz Kit",
        "033: Latin Kit",
    ],
}


def _on_tva_level_velocity_sens_slider_changed(self, value: int):
    """Handle TVA Level Velocity Sens change"""
    if self.midi_helper:
        # Convert -63 to +63 range to MIDI value (0 to 127)
        midi_value = value + 63  # Center at 63
        self.midi_helper.send_parameter(
            area=DRUM_KIT_AREA,
            part=DRUM_PART,
            group=DRUM_LEVEL,
            param=0x137,  # Address for TVA Level Velocity Sens
            value=midi_value,
        )
        print(f"TVA Level Velocity Sens changed to {midi_value}")
