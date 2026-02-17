"""
Envelope Parameters
"""


class EnvelopeParameter:
    """Parameters for Envelope Widgets"""

    # Generic
    INITIAL_LEVEL: str = "initial_level"
    RANGE_LOWER = "range_lower"
    RANGE_UPPER = "range_upper"
    DURATION = "duration"
    # Filter
    FILTER_CUTOFF = "filter_cutoff"
    FILTER_SLOPE: str = "slope_param"
    FILTER_RESONANCE = "filter_resonance"
    PEAK_LEVEL: str = "peak_level"
    MOD_DEPTH: str = "mod_depth"
    # ADSR
    DEPTH: str = "depth"
    SUSTAIN_LEVEL: str = "sustain_level"
    ATTACK_TIME: str = "attack_time"
    DECAY_TIME: str = "decay_time"
    RELEASE_TIME: str = "release_time"
    # PWM
    PULSE_WIDTH: str = "pulse_width"
    # WMT
    FADE_LOWER: str = "fade_lower"
    FADE_UPPER: str = "fade_upper"
    V_SENS: str = "v_sens"
    T1_V_SENS: str = "t1_v_sens"
    T4_V_SENS: str = "t4_v_sens"
    TIME_0: str = "time_0"
    TIME_1: str = "time_1"
    TIME_2: str = "time_2"
    TIME_3: str = "time_3"
    TIME_4: str = "time_4"
    LEVEL_0: str = "level_0"
    LEVEL_1: str = "level_1"
    LEVEL_2: str = "level_2"
    LEVEL_3: str = "level_3"
    LEVEL_4: str = "level_4"
