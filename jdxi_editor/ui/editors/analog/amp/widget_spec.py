"""
Widget Spec
"""

from dataclasses import dataclass

from jdxi_editor.ui.editors.base.layout.spec import LayoutSpec
from jdxi_editor.ui.widgets.spec import SliderSpec, SwitchSpec


@dataclass(frozen=True)
class AnalogAmpLayoutSpec(LayoutSpec):
    """Analog Oscillator Widgets"""
    switches: list[SwitchSpec]
    tuning: list[SliderSpec]
    env: list[SliderSpec]
