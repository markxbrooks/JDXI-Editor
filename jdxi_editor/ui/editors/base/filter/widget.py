"""
FilterWidgets class

Single container for all filter UI widgets used by both Analog and Digital
filter sections. Optional fields default to None so either section can
populate only what it uses.
"""

from dataclasses import dataclass
from typing import Any

from PySide6.QtWidgets import QGroupBox, QTabWidget, QWidget


@dataclass
class FilterWidgets:
    """All filter widgets in one place (Analog and Digital)."""

    filter_widget: QWidget | None = None
    controls_group: QGroupBox | None = None
    adsr_widget: QWidget | None = None
    filter_mode_buttons: dict[Any, QWidget] | None = None
    tab_widget: QTabWidget | None = None
