class DrumDisplayOptions:
    """Drum UI Display Options"""

    # Partial Parameters
    PARTIAL_ENV_MODE = ["NO-SUS", "SUSTAIN"]
    ASSIGN_TYPE = ["MULTI", "SINGLE"]
    MUTE_GROUP = ["OFF"] + [str(i) for i in range(1, 31)]
    PARTIAL_RECEIVE_EXPRESSION = ["OFF", "ON"]
    PARTIAL_RECEIVE_HOLD_1 = ["OFF", "ON"]
    ONE_SHOT_MODE = ["OFF", "ON"]

    # Output Parameters
    PARTIAL_OUTPUT_ASSIGN = ["EFX1", "EFX2", "DLY", "REV", "DIR"]

    # TVF Parameters
    TVF_FILTER_TYPE = ["OFF", "LPF", "BPF", "HPF", "PKG", "LPF2", "LPF3"]
    TVF_CUTOFF_VELOCITY_CURVE = ["FIXED", "1", "2", "3", "4", "5", "6", "7"]
    TVF_ENV_VELOCITY_CURVE_TYPE = ["FIXED", "1", "2", "3", "4", "5", "6", "7"]

    # TVA Parameters
    TVA_LEVEL_VELOCITY_CURVE = ["FIXED", "1", "2", "3", "4", "5", "6", "7"]

    # WMT Parameters
    WMT_VELOCITY_CONTROL = ["OFF", "ON", "RANDOM"]
    WMT_WAVE_SWITCH = ["OFF", "ON"]
    WMT_WAVE_GAIN = ["-6", "0", "6", "12"]


class DrumDisplayValues:
    """Drum UI Display Options"""

    # Partial Parameters
    """
    PARTIAL_ENV_MODE = ["NO-SUS", "SUSTAIN"]
    ASSIGN_TYPE = ["MULTI", "SINGLE"]
    MUTE_GROUP = ["OFF"] + [str(i) for i in range(1, 31)]
    PARTIAL_RECEIVE_EXPRESSION = ["OFF", "ON"]
    PARTIAL_RECEIVE_HOLD_1 = ["OFF", "ON"]
    ONE_SHOT_MODE = ["OFF", "ON"]
    """

    # Output Parameters
    # PARTIAL_OUTPUT_ASSIGN = ["EFX1", "EFX2", "DLY", "REV", "DIR"]

    # TVF Parameters
    """TVF_FILTER_TYPE = ["OFF", "LPF", "BPF", "HPF", "PKG", "LPF2", "LPF3"]
    TVF_CUTOFF_VELOCITY_CURVE = ["FIXED", "1", "2", "3", "4", "5", "6", "7"]
    TVF_ENV_VELOCITY_CURVE_TYPE = ["FIXED", "1", "2", "3", "4", "5", "6", "7"]"""

    # TVA Parameters
    TVA_LEVEL_VELOCITY_CURVE = [0, 1, 2, 3, 4, 5, 6, 7]
