from __future__ import annotations

from jdxi_editor.midi.data.parameter.effects.effects import Effect1Param, Effect2Param


class EffectTypeHandler:
    def __init__(self, on_efx1_change, on_efx2_change):
        self.pending_efx1 = None
        self.pending_efx2 = None
        self.on_efx1_change = on_efx1_change
        self.on_efx2_change = on_efx2_change

    def handle(self, param, value) -> bool:

        if param is Effect1Param.EFX1_TYPE:
            self.pending_efx1 = value
            return False  # still update widget

        if param is Effect2Param.EFX2_TYPE:
            self.pending_efx2 = value
            return False

        return False

    def flush(self):
        if self.pending_efx1 is not None:
            self.on_efx1_change(self.pending_efx1)
        if self.pending_efx2 is not None:
            self.on_efx2_change(self.pending_efx2)
