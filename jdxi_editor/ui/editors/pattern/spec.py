"""
Sequencer Row Spec
"""

from dataclasses import dataclass


@dataclass
class SequencerRowSpec:
    label: str
    icon: str
    accent_color: str
