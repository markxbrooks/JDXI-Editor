from dataclasses import dataclass
from typing import Optional

from jdxi_editor.ui.widgets.spec import SwitchSpec, ComboBoxSpec, SliderSpec


@dataclass
class AmpWidgetSpec:
    """Layout of Widgets"""

    controls: Optional[list[SwitchSpec | SliderSpec | ComboBoxSpec]] = None
    pan: Optional[list[SliderSpec | None]] = None
    adsr: Optional[dict] = None

    def get(self, item, fallback=None):
        """Dict-like access: return the attribute named `item`, else `fallback`."""
        if hasattr(self, item):
            return getattr(self, item)
        return fallback