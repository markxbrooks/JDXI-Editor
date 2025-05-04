"""
Module for defining drum kit parameters in the Roland JD-Xi editor.

This module provides the `DrumPartialParameter` class, which extends `SynthParameter`
to define the addresses, value ranges, and characteristics of drum partial parameters.
It includes various attributes representing different drum-related parameters, such as
tuning, level, panning, and effects settings.

Classes:
    DrumPartialParameter -- Represents a drum partial parameter with its address,
                            value range, and optional display range.

Attributes:
    DRUM_GROUP_MAP -- Mapping of drum groups.
    DRUM_ADDRESS_MAP -- Mapping of parameter names to MIDI addresses.

Example usage:
    drum_param = DrumPartialParameter(0x0F, 0, 127)
    print(drum_param.address)  # Output: 0x0F
    print(drum_param.min_val)  # Output: 0
    print(drum_param.max_val)  # Output: 127
"""


from typing import Optional, Tuple

from jdxi_editor.midi.data.parameter.drum.addresses import (
    DRUM_GROUP_MAP,
    DRUM_ADDRESS_MAP,
)
from jdxi_editor.midi.data.parameter.synth import AddressParameter


class AddressParameterDrumPartial(AddressParameter):
    """Drum kit parameters with their addresses and value ranges"""

    def __init__(
        self,
        address: int,
        min_val: int,
        max_val: int,
        display_min: Optional[int] = None,
        display_max: Optional[int] = None,
    ) :
        super().__init__(address, min_val, max_val)
        self.display_min = display_min if display_min is not None else min_val
        self.display_max = display_max if display_max is not None else max_val
        self.bipolar_parameters = [
            "PARTIAL_FINE_TUNE",
            "PARTIAL_FINE_TUNE",
            "PARTIAL_PAN",
            "PARTIAL_ALTERNATE_PAN_DEPTH",
            "TVA_ENV_TIME_1_VELOCITY_SENS",
            "TVA_ENV_TIME_4_VELOCITY_SENS",
            "TVF_CUTOFF_VELOCITY_SENS",
            "TVF_ENV_DEPTH",
            "TVF_ENV_VELOCITY_SENS",
            "TVF_ENV_TIME_1_VELOCITY_SENS",
            "TVF_ENV_TIME_4_VELOCITY_SENS",
            "WMT1_WAVE_COARSE_TUNE",
            "WMT1_WAVE_FINE_TUNE",
            "WMT1_WAVE_PAN",
            "WMT2_WAVE_COARSE_TUNE",
            "WMT2_WAVE_FINE_TUNE",
            "WMT2_WAVE_PAN",
            "WMT3_WAVE_COARSE_TUNE",
            "WMT3_WAVE_FINE_TUNE",
            "WMT3_WAVE_PAN",
            "WMT4_WAVE_COARSE_TUNE",
            "WMT4_WAVE_FINE_TUNE",
            "WMT4_WAVE_PAN",
        ]

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
    PARTIAL_PAN = (0x12, 0, 127, -64, 63)  # L64 - 63R

    # Partial Random Pan Depth
    PARTIAL_RANDOM_PAN_DEPTH = (0x13, 0, 63, 0, 63)

    # Partial Alternate Pan Depth
    PARTIAL_ALTERNATE_PAN_DEPTH = (0x14, 1, 127, -63, 63)  # L63 - 63R

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
    WMT1_WAVE_COARSE_TUNE = (0x34, 16, 112, -48, 48)  # -48 - +48

    # WMT1 Wave Fine Tune
    WMT1_WAVE_FINE_TUNE = (0x35, 14, 114, -50, 50)  # -50 - +50

    # WMT1 Wave Pan
    WMT1_WAVE_PAN = (0x36, 0, 127, -64, 63)  # L64 - 63R

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
    WMT2_WAVE_COARSE_TUNE = (0x51, 16, 112, -48, 48)  # -48 - +48

    # WMT2 Wave Fine Tune
    WMT2_WAVE_FINE_TUNE = (0x52, 14, 114, -50, 50)  # -50 - +50

    # WMT2 Wave Pan
    WMT2_WAVE_PAN = (0x53, 0, 127, -64, 63)  # L64 - 63R

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
    WMT3_WAVE_COARSE_TUNE = (0x6E, 16, 112, -48, 48)  # -48 - +48

    # WMT3 Wave Fine Tune
    WMT3_WAVE_FINE_TUNE = (0x6F, 14, 114, -50, 50)  # -50 - +50

    # WMT3 Wave Pan
    WMT3_WAVE_PAN = (0x70, 0, 127, -64, 64)  # L64 - 63R

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
    WMT4_WAVE_COARSE_TUNE = (0x10B, 16, 112, -48, 48)  # -48 - +48

    # WMT4 Wave Fine Tune
    WMT4_WAVE_FINE_TUNE = (0x10C, 14, 114, -50, 50)  # -50 - +50

    # WMT4 Wave Pan
    WMT4_WAVE_PAN = (0x10D, 0, 127, -64, 64)  # L64 - 63R

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
    PITCH_ENV_DEPTH = (0x115, 52, 76, -12, 12)  # -12 - +12

    # Pitch Env Velocity Sens
    PITCH_ENV_VELOCITY_SENS = (0x116, 1, 127, -63, 63)  # -63 - +63

    # Pitch Env Time 1 Velocity Sens
    PITCH_ENV_TIME_1_VELOCITY_SENS = (0x117, 1, 127, -63, 63)  # -63 - +63

    # Pitch Env Time 4 Velocity Sens
    PITCH_ENV_TIME_4_VELOCITY_SENS = (0x118, 1, 127, -63, 63)  # -63 - +63

    # Pitch Env Time 1
    PITCH_ENV_TIME_1 = (0x119, 0, 127, 0, 127)

    # Pitch Env Time 2
    PITCH_ENV_TIME_2 = (0x11A, 0, 127, 0, 127)

    # Pitch Env Time 3
    PITCH_ENV_TIME_3 = (0x11B, 0, 127, 0, 127)

    # Pitch Env Time 4
    PITCH_ENV_TIME_4 = (0x11C, 0, 127, 0, 127)

    # Pitch Env Level 0
    PITCH_ENV_LEVEL_0 = (0x11D, 1, 127, -63, 63)  # -63 - +63

    # Pitch Env Level 1
    PITCH_ENV_LEVEL_1 = (0x11E, 1, 127, -63, 63)  # -63 - +63

    # Pitch Env Level 2
    PITCH_ENV_LEVEL_2 = (0x11F, 1, 127, -63, 63)  # -63 - +63

    # Pitch Env Level 3
    PITCH_ENV_LEVEL_3 = (0x120, 1, 127, -63, 63)  # -63 - +63

    # Pitch Env Level 4
    PITCH_ENV_LEVEL_4 = (0x121, 1, 127, -63, 63)  # -63 - +63

    # TVF Filter Type
    TVF_FILTER_TYPE = (0x122, 0, 6, 0, 6)  # OFF, LPF, BPF, HPF, PKG, LPF2, LPF3

    # TVF Cutoff Frequency
    TVF_CUTOFF_FREQUENCY = (0x123, 0, 127, 0, 127)

    # TVF Cutoff Velocity Curve
    TVF_CUTOFF_VELOCITY_CURVE = (0x124, 0, 7, 0, 7)  # FIXED, 1 - 7

    # TVF Cutoff Velocity Sens
    TVF_CUTOFF_VELOCITY_SENS = (0x125, 1, 127, -63, 63)  # -63 - +63

    # TVF Resonance
    TVF_RESONANCE = (0x126, 0, 127, 0, 127)

    # TVF Resonance Velocity Sens
    TVF_RESONANCE_VELOCITY_SENS = (0x127, 1, 127, -63, 63)  # -63 - +63

    # TVF Env Depth
    TVF_ENV_DEPTH = (0x128, 1, 127, -63, 63)  # -63 - +63

    # TVF Env Velocity Curve Type
    TVF_ENV_VELOCITY_CURVE_TYPE = (0x129, 0, 7, 0, 7)  # FIXED, 1 - 7

    # TVF Env Velocity Sens
    TVF_ENV_VELOCITY_SENS = (0x137, 1, 127, -63, 63)  # -63 - +63

    # TVF Env Time 1 Velocity Sens
    TVF_ENV_TIME_1_VELOCITY_SENS = (0x12B, 1, 127, -63, 63)  # -63 - +63

    # TVF Env Time 4 Velocity Sens
    TVF_ENV_TIME_4_VELOCITY_SENS = (0x12C, 1, 127, -63, 63)  # -63 - +63

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
    TVA_LEVEL_VELOCITY_SENS = (0x137, 1, 127, -63, 63)  # -63 - +63

    # TVA Env Time 1 Velocity Sens
    TVA_ENV_TIME_1_VELOCITY_SENS = (0x138, 1, 127, -63, 63)  # -63 - +63

    # TVA Env Time 4 Velocity Sens
    TVA_ENV_TIME_4_VELOCITY_SENS = (0x139, 1, 127, -63, 63)  # -63 - +63

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
    RELATIVE_LEVEL = (0x142, 0, 127, -64, 64)  # -64 - +63

    DRUM_PART = (0x70, 1, 5, 1, 5)  # Hack alert @@

    DRUM_GROUP = (0x2F, 1, 5, 1, 5)  # Hack alert @@

    def validate_value(self, value: int) -> int:
        """Validate and convert parameter value to MIDI range (0-127)
        :param value: int The value
        :return: int The validated value
        """
        if not isinstance(value, int):
            raise ValueError(f"Value must be integer, got {type(value)}")

        # Ensure value is in valid MIDI range
        if value < 0 or value > 127:
            raise ValueError(
                f"MIDI value {value} out of range for {self.name} (must be 0-127)"
            )

        return value

    def convert_from_display(self, display_value: int) -> int:
        """Convert from display value to MIDI value (0-127)
        :param display_value: int The display value
        :return: int The MIDI value
        """
        return display_value

    def get_display_value(self) -> Tuple[int, int]:
        """Get the display range for the parameter
        :return: Tuple[int, int] The display range
        """
        return self.display_min, self.display_max

    def get_address_for_partial(self, partial_index: int) -> tuple:
        """Get the address for address drum partial by index
        :param partial_index: int The partial index
        :return: tuple The address
        """
        if not isinstance(partial_index, int):
            raise ValueError(
                f"Partial index must be an integer, got {type(partial_index)}"
            )

        if partial_index < 0 or partial_index >= 72:
            raise ValueError(f"Invalid partial index: {partial_index}")

        address_lmb = DRUM_GROUP_MAP.get(
            partial_index + 1, 0x2E
        )  # Default to 0x2E if partial_name is not 1, 2, or 3
        return address_lmb, 0x00

    @staticmethod
    def get_address_for_partial_name(partial_name: str) -> int:
        """Get parameter area and address adjusted for partial number.
        :param partial_name: str The partial name
        :return: int The address
        """
        address = DRUM_ADDRESS_MAP.get(
            partial_name, 0x00
        )  # Default to 0x00 for common area
        return address

    @staticmethod
    def get_by_name(param_name: str) -> Optional[object]:
        """Get the AnalogParameter by name.
        :param param_name: str The parameter name
        :return: Optional[AddressParameterDrumPartial] The parameter
        Return the parameter member by name, or None if not found
        """
        return AddressParameterDrumPartial.__members__.get(param_name, None)

    def convert_from_midi(self, midi_value: int) -> int:
        """Convert from MIDI value to display value
        :param midi_value: int The MIDI value
        :return: int The display value
        """
        return midi_value
