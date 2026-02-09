class LFOSwitchGroup:
    """LFO Switch Group"""

    SWITCH_ROW: str = "switch_row_widgets"


class LFOSliderGroup:
    """Slider Group"""

    DEPTH: str = "depth"
    RATE_FADE: str = "rate_fade"


class LFOGroup:
    """LFO Groups"""

    label: str = "LFO"
    slider: LFOSliderGroup = LFOSliderGroup
    switch: LFOSwitchGroup = LFOSwitchGroup
    combo: None
