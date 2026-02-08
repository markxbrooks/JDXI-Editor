from __future__ import annotations

from jdxi_editor.midi.data.parameter.effects.effects import Effect1Param, Effect2Param, DelayParam, ReverbParam

EFFECT_PARAM_TYPES = (
    *list(Effect1Param),
    *list(Effect2Param),
    *list(DelayParam),
    *list(ReverbParam),
)
