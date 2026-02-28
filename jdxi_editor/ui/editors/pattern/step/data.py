from dataclasses import dataclass
from typing import Optional


@dataclass
class StepData:
    """Step data"""

    active: bool = False
    note: int = 60
    velocity: int = 100
    duration_steps: Optional[int] = 1
    probability: float = 1.0
    micro_shift: int = 0
