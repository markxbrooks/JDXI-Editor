"""
Random analog tone generation (Manager rndVoice analogue).

Uses AnalogParam min/max ranges; tone-name slots get printable ASCII (48–57)
matching Manager's AN_rnd name-byte ranges.
"""

from __future__ import annotations

import random
from typing import Any

from decologr import Decologr as log

from jdxi_editor.midi.data.parameter.analog.address import AnalogParam


def randomize_analog_editor(editor: Any) -> int:
    """
    Randomize Analog editor controls within parameter ranges and send to device.

    :return: Number of parameters randomized
    """
    applied = 0
    for param, widget in list(getattr(editor, "controls", {}).items()):
        if not isinstance(param, AnalogParam) and not hasattr(param, "min_val"):
            continue
        name = getattr(param, "name", "")
        try:
            if name.startswith("TONE_NAME_"):
                # Manager: first five name bytes 48–57 ("0"–"9"); rest often fixed
                lo, hi = 48, 57
            else:
                lo = int(getattr(param, "min_val", 0))
                hi = int(getattr(param, "max_val", 127))
            if hi < lo:
                lo, hi = hi, lo
            value = random.randint(lo, hi)
            if hasattr(widget, "setValue"):
                widget.blockSignals(True)
                widget.setValue(value)
                widget.blockSignals(False)
            address = getattr(editor, "address", None) or getattr(
                getattr(editor, "synth_data", None), "address", None
            )
            if hasattr(editor, "send_midi_parameter"):
                editor.send_midi_parameter(param, value, address=address)
            applied += 1
        except Exception as ex:
            log.warning(
                f"Skip randomize {name}: {ex}",
                scope="analog_random",
            )
    log.message(f"Randomized {applied} analog parameters", scope="analog_random")
    return applied
