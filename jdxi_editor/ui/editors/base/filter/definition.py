"""
FilterDefinition
"""

from dataclasses import dataclass
from enum import IntEnum
from typing import Any

from jdxi_editor.ui.adsr.spec import ADSRStage, ADSRSpec
from jdxi_editor.ui.editors.base.layout.spec import LayoutSpec
from jdxi_editor.ui.widgets.spec import FilterWidgetSpec, FilterSpec


@dataclass(frozen=True)
class FilterDefinition:
    """Complete description of a synth filter implementation."""

    # identity
    modes: type[IntEnum]                 # canonical filter id enum

    # midi mapping
    param_mode: Any                      # parameter that stores filter mode
    midi_to_mode: dict[int, IntEnum]
    mode_to_midi: dict[IntEnum, int]

    # UI
    specs: dict[IntEnum, FilterSpec]
    widget_spec: FilterWidgetSpec
    sliders: LayoutSpec
    adsr: dict[ADSRStage, ADSRSpec]

    # behavior
    bypass_mode: IntEnum
    has_slope: bool = False
