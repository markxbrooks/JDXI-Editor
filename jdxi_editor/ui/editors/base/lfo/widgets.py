"""
LFOWidgets class

Single container for all LFO UI widgets used by Analog, Digital LFO, and Mod LFO
sections. Optional fields default to empty lists so any section can populate
only what it uses.
"""

from dataclasses import dataclass, field

from PySide6.QtWidgets import QWidget


@dataclass
class LFOWidgets:
    """All LFO widgets in one place (Analog, Digital LFO, Mod LFO)."""

    switches: list[QWidget] = field(default_factory=list)
    depth: list[QWidget] = field(default_factory=list)
    rate: list[QWidget] = field(default_factory=list)
