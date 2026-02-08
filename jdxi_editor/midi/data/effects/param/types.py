from __future__ import annotations

from jdxi_editor.midi.data.parameter.effects.effects import (
    DelayParam,
    Effect1Param,
    Effect2Param,
    ReverbParam,
)

EFFECT_PARAM_TYPES = (
    *list(Effect1Param),
    *list(Effect2Param),
    *list(DelayParam),
    *list(ReverbParam),
)
