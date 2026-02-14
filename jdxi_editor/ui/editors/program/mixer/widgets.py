"""
Synth Label Widget Registry
"""

from dataclasses import dataclass, field
from typing import Optional

from PySide6.QtWidgets import QLabel


@dataclass
class LabelWidgetRegistry:
    """Runtime label registry for mixer tracks"""

    _labels: dict[str, QLabel] = field(default_factory=dict)

    def register(self, synth: str, label: QLabel) -> None:
        self._labels[synth] = label

    def get(self, synth: str) -> Optional[QLabel]:
        return self._labels.get(synth)

    def set_text(self, synth: str, text: str) -> None:
        label = self.get(synth)
        if label:
            label.setText(text)
