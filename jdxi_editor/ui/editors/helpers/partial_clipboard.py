"""
In-process clipboard for Digital / Drum partial control dictionaries.

Paste only succeeds when the destination kind matches the source kind
(Manager pastePart length/type check analogue).
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from decologr import Decologr as log

# (kind, controls_dict) — kind is "digital_partial" or "drum_partial"
_CLIPBOARD: Optional[Tuple[str, Dict[str, Any]]] = None


def copy_partial(kind: str, controls: Dict[str, Any]) -> None:
    """Store a partial's control values."""
    global _CLIPBOARD
    _CLIPBOARD = (kind, dict(controls))
    log.message(
        f"Copied {kind} ({len(controls)} params)",
        scope="partial_clipboard",
    )


def paste_partial(kind: str) -> Optional[Dict[str, Any]]:
    """
    Return copied controls if kind matches; otherwise None.
    """
    if _CLIPBOARD is None:
        return None
    src_kind, controls = _CLIPBOARD
    if src_kind != kind:
        log.warning(
            f"Paste rejected: clipboard is {src_kind}, destination is {kind}",
            scope="partial_clipboard",
        )
        return None
    return dict(controls)


def apply_controls_to_editor(editor: Any, controls: Dict[str, Any]) -> int:
    """
    Apply control name→value mapping to an editor's widgets and send MIDI.

    :return: Number of parameters applied
    """
    applied = 0
    param_by_name = {}
    for param in getattr(editor, "controls", {}) or {}:
        param_by_name[param.name] = param

    for name, value in controls.items():
        param = param_by_name.get(name)
        if param is None:
            continue
        widget = editor.controls.get(param)
        if widget is None:
            continue
        try:
            display = int(value) if not isinstance(value, int) else value
            if hasattr(widget, "setValue"):
                widget.blockSignals(True)
                widget.setValue(display)
                widget.blockSignals(False)
            elif hasattr(widget, "combo_box"):
                widget.combo_box.blockSignals(True)
                # Prefer setValue if ComboBox wrapper has it
                if hasattr(widget, "setValue"):
                    widget.setValue(display)
                widget.combo_box.blockSignals(False)
            address = getattr(editor, "address", None)
            if hasattr(editor, "send_midi_parameter"):
                editor.send_midi_parameter(param, display, address=address)
            applied += 1
        except Exception as ex:
            log.warning(f"Could not apply {name}: {ex}", scope="partial_clipboard")
    return applied
