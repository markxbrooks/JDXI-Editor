"""
Spec Definitions
"""


class MidiSynthSpec:
    """Synth Spec Class"""
    Param = None
    Display = None
    Wave = None
    Filter = None
    Amp = None
    Tab = None
    GroupBox = None
    ControlChange = None
    RPN = None


class DisplaySpec:
    """Display Spec class"""
    Name = None
    Values = None
    Options = None


class WaveSpec:
    """Wave Spec"""
    LFO = None
    Osc = None
    SubOsc = None
    WaveType = None
    Tab = None


class FilterSpec:
    """Filter Spec"""
    Mode = None
    ModeType = None
    FilterType = None
    ADSR = None
    Tab = None


class AmpSpec:
    """Amp Spec"""
    ADSR = None
    Tab = None
