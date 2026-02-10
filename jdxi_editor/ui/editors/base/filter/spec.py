"""
FilterFeature and Filter Spec classes
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional

from jdxi_editor.ui.widgets.spec import ComboBoxSpec, SliderSpec, SwitchSpec


class FilterFeature(Enum):
    """Oscillator capability flags; defined here to avoid circular import (layout.spec must not import from digital)."""

    PWM = auto()
    PITCH_ENV = auto()
    PCM = auto()
    SUB_OSC = auto()
    SUPER_SAW = auto()
    ADSR = auto()


@dataclass
class FilterLayoutSpec:
    """Layout of Widgets"""

    controls: Optional[list[SwitchSpec | SliderSpec | ComboBoxSpec]] = None
    adsr: Optional[dict] = None
    features: set[FilterFeature] = field(default_factory=set)

    def get(self, item, fallback=None):
        """Dict-like access: return the attribute named `item`, else `fallback`."""
        if hasattr(self, item):
            return getattr(self, item)
        return fallback
