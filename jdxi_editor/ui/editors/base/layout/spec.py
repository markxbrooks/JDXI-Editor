from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional

from jdxi_editor.ui.widgets.spec import ComboBoxSpec, SliderSpec, SwitchSpec


class OscillatorFeature(Enum):
    """Oscillator capability flags; defined here to avoid circular import (layout.spec must not import from digital)."""

    PW_SHIFT = auto()
    WAVEFORM = auto()
    TUNING = auto()
    PWM = auto()
    PITCH_ENV = auto()
    PCM = auto()
    SUB_OSC = auto()
    SUPER_SAW = auto()
    ADSR = auto()


class FilterFeature(Enum):
    """Oscillator capability flags; defined here to avoid circular import (layout.spec must not import from digital)."""

    MODE_BUTTONS = auto()
    FILTER_CUTOFF = auto()
    FILTER_RESONANCE = auto()
    FILTER_DEPTH = auto()
    FILTER_CUTOFF_KEYFOLLOW = auto()
    FILTER_DEPTH_VELOCITY_SENS = auto()
    ADSR = auto()
    ADSR_DEPTH = auto()


@dataclass
class LayoutSpec:
    """Layout of Widgets"""

    controls: Optional[list[SwitchSpec | SliderSpec | ComboBoxSpec]] = None
    combos: Optional[list[ComboBoxSpec | None]] = None
    adsr: Optional[dict] = None
    sliders: Optional[list[SliderSpec | None]] = None
    switches: Optional[list[SwitchSpec | None]] = None
    misc: Optional[list[SwitchSpec | SliderSpec | ComboBoxSpec]] = None
    features: set[OscillatorFeature] = field(default_factory=set)
    feature_tabs: set[OscillatorFeature] = field(default_factory=set)

    def get(self, item, fallback=None):
        """Dict-like access: return the attribute named `item`, else `fallback`."""
        if hasattr(self, item):
            return getattr(self, item)
        return fallback
