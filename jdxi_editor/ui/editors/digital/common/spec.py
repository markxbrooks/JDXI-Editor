"""
Common Editor Widget Spec
"""

from dataclasses import dataclass

from jdxi_editor.ui.widgets.spec import ComboBoxSpec, SwitchSpec, SliderSpec


@dataclass
class CommonWidgetSpec:
    """Common Editor Widgets"""
    pitch: list[SliderSpec] = None
    portamento_switches: list[SwitchSpec] = None
    octave_shift: list[ComboBoxSpec] = None
    other_switches: list[SwitchSpec] = None
