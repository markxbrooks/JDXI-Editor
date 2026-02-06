"""
Wave Shape Spec
"""

from dataclasses import dataclass


@dataclass
class WaveShapeSpec:
    """Wave Shape"""
    shape: int = None
    icon: str = ""
