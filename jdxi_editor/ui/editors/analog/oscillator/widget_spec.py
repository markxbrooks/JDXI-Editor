from dataclasses import dataclass

from jdxi_editor.ui.widgets.spec import ComboBoxSpec, SliderSpec, SwitchSpec


@dataclass(frozen=True)
class AnalogOscillatorLayoutSpec:
    """Analog Oscillator Widgets"""
    switches: list[SwitchSpec]
    tuning: list[SliderSpec]
    env: list[SliderSpec]

    def get(self, item, fallback=None):
        """Dict-like access: return the attribute named `item`, else `fallback`."""
        if hasattr(self, item):
            return getattr(self, item)
        return fallback
