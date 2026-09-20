"""
Log Midi Info
"""

from typing import TYPE_CHECKING, Any, Optional

from decologr import Decologr as log

if TYPE_CHECKING:
    from jdxi_editor.midi.validation.selection import ValidationResult
    from jdxi_editor.ui.midi.selection_info import MidiWireInfo


def log_midi_info(msb: int, lsb: int, pc: int) -> None:
    """
    Log MIDI information in a consistent format.

    :param msb: int most significant byte
    :param lsb: int least significant byte
    :param pc: int program (preset-list slot, typically 1-based)
    :return: None
    """
    log.message(f"msb: {msb}, lsb: {lsb}, pc: {pc}")


def log_midi_wire_info(info: Optional["MidiWireInfo"]) -> None:
    """Log resolved wire-format MIDI (channel, CC0/CC32, wire PC)."""
    from jdxi_editor.ui.midi.selection_info import format_midi_wire_info

    if info is None:
        log.message("MIDI wire info: —")
        return
    log.message(format_midi_wire_info(info))


def _format_wire_summary(info: "MidiWireInfo") -> str:
    return (
        f"Ch{info.channel + 1} CC0={info.cc0} CC32={info.cc32} PC={info.midi_pc}"
    )


def log_midi_validation_result(
    result: "ValidationResult",
    *,
    source: str = "",
    selection_value: Any = None,
) -> None:
    """Log MIDI selection cross-validation outcome (warning on mismatch)."""
    if result.ok:
        log.debug(
            f"[MIDI selection validation OK] {_format_wire_summary(result.actual)}"
        )
        return

    ctx_parts = []
    if source:
        ctx_parts.append(f"source={source}")
    if selection_value is not None:
        ctx_parts.append(f"selection={selection_value}")
    ctx = f" {' '.join(ctx_parts)}" if ctx_parts else ""

    fields = ", ".join(result.diff_fields)
    log.warning(
        f"[MIDI selection validation FAILED]{ctx} "
        f"expected {_format_wire_summary(result.expected)}; "
        f"sent {_format_wire_summary(result.actual)} ({fields})"
    )
