from __future__ import annotations

from typing import Any, Dict

from jdxi_editor.midi.data.effects.param.registry import EffectParamRegistry
from jdxi_editor.midi.data.effects.type.handler import EffectTypeHandler
from jdxi_editor.ui.editors.effects.dispatch_stats import DispatchStats
from jdxi_editor.ui.widgets.controls.registry import ControlResolver
from jdxi_editor.ui.widgets.writer import WidgetWriter


class EffectsSysExDispatcher:
    """Clean, deterministic, editor-agnostic SysEx UI updater"""

    METADATA_KEYS = {"SYNTH_TONE", "TEMPORARY_AREA"}

    def __init__(
        self,
        controls: ControlResolver,
        param_registry: EffectParamRegistry,
        type_handler: EffectTypeHandler,
    ):
        self.controls = controls
        self.registry = param_registry
        self.type_handler = type_handler

    def dispatch(self, sysex_data: Dict[str, Any]) -> DispatchStats:
        """dispatch"""
        stats = DispatchStats(applied=[], skipped=[], failed=[], successes=[])

        for name, raw_value in sysex_data.items():
            if name in self.METADATA_KEYS:
                continue

            param = self.registry.resolve(name)
            if not param:
                stats.record_skipped(name)
                continue

            value = int(raw_value) if not isinstance(raw_value, int) else raw_value

            # --- type-specific handling ---
            if self.type_handler.try_handle(name, value):
                stats.record_applied(name)
                continue

            widget = self.controls.get(param)
            if not widget:
                stats.record_failed(name)
                continue

            try:
                display = (
                    param.convert_from_midi(value)
                    if hasattr(param, "convert_from_midi")
                    else value
                )

                if hasattr(widget, "setValue"):
                    WidgetWriter.set_slider(widget, display)
                elif hasattr(widget, "combo_box"):
                    WidgetWriter.set_combo(widget, value)
                else:
                    stats.record_failed(name)
                    continue

                stats.record_applied(name)

            except Exception:
                stats.record_failed(name)

        self.type_handler.flush()
        return stats
