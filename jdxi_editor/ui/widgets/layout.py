from dataclasses import dataclass

from jdxi_editor.ui.widgets.spec import ComboBoxSpec, SliderSpec, SwitchSpec


@dataclass(frozen=True)
class WidgetLayoutSpec:
    """Generic Widget Layout"""
    switches: list[SwitchSpec]
    sliders: list[SliderSpec]
    combos: list[ComboBoxSpec]
