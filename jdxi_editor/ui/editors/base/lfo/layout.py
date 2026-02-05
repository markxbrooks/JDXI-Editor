from dataclasses import dataclass

from jdxi_editor.ui.widgets.spec import SliderSpec, SwitchSpec


@dataclass(frozen=True)
class LFOLayoutSpec:
    switches: list[SwitchSpec]
    depth_sliders: list[SliderSpec]
    rate_sliders: list[SliderSpec]
