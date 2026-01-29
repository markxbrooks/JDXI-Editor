from dataclasses import dataclass
from enum import Enum


class ADSRStage(Enum):
    ATTACK = "attack"
    DECAY = "decay"
    SUSTAIN = "sustain"
    RELEASE = "release"
    PEAK = "peak"


@dataclass(frozen=True, slots=True)
class ADSRSpec:
    stage: ADSRStage
    param: object  # or Digital.Param if you want strict typing
