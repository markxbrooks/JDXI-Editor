"""
Oscillator Layout Spec
"""

from dataclasses import dataclass, field
from typing import Callable, TypeAlias

from PySide6.QtWidgets import QWidget

from jdxi_editor.ui.editors.base.oscillator.layout_spec import OscillatorLayoutSpec
from jdxi_editor.ui.widgets.spec import (
    SliderSpec,
)

TabSpec: TypeAlias = tuple[object, QWidget]
TabBuilder: TypeAlias = Callable[[], None]


@dataclass
class DigitalOscillatorLayoutSpec(OscillatorLayoutSpec):
    """Oscillator Layout Spec"""

    pw_controls: list[SliderSpec] = field(default_factory=list)
    pe_controls: list[SliderSpec] = field(default_factory=list)