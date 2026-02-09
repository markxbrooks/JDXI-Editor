from dataclasses import dataclass
from typing import Optional

from jdxi_editor.ui.widgets.spec import ComboBoxSpec, SliderSpec, SwitchSpec


@dataclass
class LayoutSpec:
    """Layout of Widgets"""

    controls: Optional[list[SwitchSpec | SliderSpec | ComboBoxSpec]] = None
    combos: Optional[list[ComboBoxSpec | None]] = None
    sliders: Optional[list[SliderSpec | None]] = None
    switches: Optional[list[SwitchSpec | None]] = None
    misc: Optional[list[SwitchSpec | SliderSpec | ComboBoxSpec]] = None

    def get(self, item, fallback=None):
        """Dict-like access: return the attribute named `item`, else `fallback`."""
        if hasattr(self, item):
            return getattr(self, item)
        return fallback
