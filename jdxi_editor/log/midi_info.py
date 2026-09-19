"""
Log Midi Info
"""

from typing import TYPE_CHECKING, Optional

from decologr import Decologr as log

if TYPE_CHECKING:
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
