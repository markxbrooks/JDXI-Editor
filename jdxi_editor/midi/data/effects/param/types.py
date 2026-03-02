from __future__ import annotations

from jdxi_editor.midi.data.parameter.effects.effects import (
    DelayParam,
    Effect1Param,
    Effect2Param,
    ReverbParam,
)

# EffectParamRegistry expects classes (iterables with __members__), not instances
EFFECT_PARAM_TYPES = (Effect1Param, Effect2Param, DelayParam, ReverbParam)
