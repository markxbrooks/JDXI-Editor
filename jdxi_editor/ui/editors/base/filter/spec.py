"""
FilterFeature and Filter Spec classes
"""

from dataclasses import dataclass, field
from typing import Any, Optional

from jdxi_editor.ui.editors.base.layout.spec import FilterFeature
from jdxi_editor.ui.widgets.spec import ComboBoxSpec, SliderSpec, SwitchSpec


@dataclass
class FilterLayoutSpec:
    """Layout of Widgets"""

    controls: Optional[list[SwitchSpec | SliderSpec | ComboBoxSpec]] = None
    adsr: Optional[dict] = None
    features: set[FilterFeature] = field(default_factory=set)
    feature_tabs: dict[Any, Any] = field(default_factory=dict)

    def get(self, item, fallback=None):
        """Dict-like access: return the attribute named `item`, else `fallback`."""
        if hasattr(self, item):
            return getattr(self, item)
        return fallback

    def supports(self, feature: FilterFeature) -> bool:
        return feature in self.features
