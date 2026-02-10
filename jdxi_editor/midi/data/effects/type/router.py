from __future__ import annotations

from typing import Set, Tuple

from jdxi_editor.ui.widgets.writer import WidgetWriter


class EffectTypeRouter:
    """Handles EFX type changes separately from normal params"""

    def __init__(self, editor):
        self.editor = editor
        self.pending_label_updates: Set[Tuple[str, int]] = set()

    def try_handle(self, param_name: str, value: int) -> bool:
        if param_name == "EFX1_TYPE":
            self._handle_type("efx1", value)
            return True
        if param_name == "EFX2_TYPE":
            self._handle_type("efx2", value)
            return True
        return False

    def _handle_type(self, kind: str, value: int):
        if kind == "efx1":
            ctrl = self.editor.tuning.get(self.editor.Effect1Param.EFX1_TYPE)
            values = self.editor.EffectsData.efx1_type_values
        else:
            ctrl = self.editor.tuning.get(self.editor.Effect2Param.EFX2_TYPE)
            values = self.editor.EffectsData.efx2_type_values

        if not ctrl:
            return

        try:
            idx = values.index(value)
        except ValueError:
            return

        WidgetWriter.set_combo(ctrl, idx)
        self.pending_label_updates.add((kind, value))

    def flush(self):
        for kind, value in self.pending_label_updates:
            if kind == "efx1":
                self.editor._update_efx1_labels(value)
            else:
                self.editor._update_efx2_labels(value)
        self.pending_label_updates.clear()
