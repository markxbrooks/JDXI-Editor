"""
FilterDefinition
"""

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from jdxi_editor.ui.adsr.spec import ADSRSpec, ADSRStage
from jdxi_editor.ui.editors.base.layout.spec import LayoutSpec
from jdxi_editor.ui.widgets.spec import FilterSpec, FilterWidgetSpec


@runtime_checkable
class FilterMode(Protocol):
    name: str
    value: int


@dataclass(frozen=True)
class FilterDefinition:
    """Complete description of a synth filter implementation."""

    # identity
    modes: type  # canonical filter id enum

    # midi mapping
    param_mode: Any  # parameter that stores filter mode
    midi_to_mode: dict[int, Any]
    mode_to_midi: dict[Any, int]

    # UI
    specs: dict[Any, FilterSpec]
    widget_spec: FilterWidgetSpec
    sliders: LayoutSpec
    adsr: dict[ADSRStage, ADSRSpec]

    # behavior
    bypass_mode: Any
    has_slope: bool = False
