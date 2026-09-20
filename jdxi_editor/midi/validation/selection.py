"""
Cross-validation of bank-select + program-change sends against MidiWireInfo.

Pure functions with no Qt dependency (aside from MidiWireInfo dataclass).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from jdxi_editor.midi.message.control.message import ControlChangeMessage
from jdxi_editor.midi.message.program.message import ProgramChangeMessage
from jdxi_editor.ui.midi.selection_info import MidiWireInfo

_COMPARE_FIELDS = ("channel", "cc0", "cc32", "midi_pc")


@dataclass(frozen=True)
class ValidationResult:
    """Outcome of comparing expected vs actual wire-format MIDI."""

    ok: bool
    expected: MidiWireInfo
    actual: MidiWireInfo
    diff_fields: List[str]


def wire_info_from_bank_pc(
    channel: int,
    bank_msb: int,
    bank_lsb: int,
    midi_pc: int,
    *,
    channel_display: Optional[str] = None,
    preset_pc: Optional[int] = None,
    program_id: Optional[str] = None,
) -> MidiWireInfo:
    """Build MidiWireInfo from send parameters."""
    display = channel_display or f"Ch {channel + 1}"
    return MidiWireInfo(
        channel=channel,
        channel_display=display,
        cc0=bank_msb,
        cc32=bank_lsb,
        midi_pc=midi_pc,
        preset_pc=preset_pc,
        program_id=program_id,
    )


def build_bank_select_pc_bytes(
    channel: int, cc0: int, cc32: int, midi_pc: int
) -> List[List[int]]:
    """Return CC0, CC32, and Program Change byte lists for the given wire values."""
    cc0_msg = ControlChangeMessage(channel=channel, controller=0, value=cc0)
    cc32_msg = ControlChangeMessage(channel=channel, controller=32, value=cc32)
    pc_msg = ProgramChangeMessage(channel=channel, program=midi_pc)
    return [
        cc0_msg.to_message_list(),
        cc32_msg.to_message_list(),
        pc_msg.to_message_list(),
    ]


def parse_bank_select_pc_sequence(
    messages: List[List[int]],
) -> Optional[MidiWireInfo]:
    """Reverse-parse CC0 + CC32 + PC from three consecutive MIDI messages."""
    if len(messages) < 3:
        return None

    cc0_msg, cc32_msg, pc_msg = messages[0], messages[1], messages[2]
    if len(cc0_msg) < 3 or (cc0_msg[0] & 0xF0) != 0xB0:
        return None
    channel = cc0_msg[0] & 0x0F
    if cc0_msg[1] != 0:
        return None
    cc0 = cc0_msg[2]

    if len(cc32_msg) < 3 or (cc32_msg[0] & 0xF0) != 0xB0:
        return None
    if (cc32_msg[0] & 0x0F) != channel or cc32_msg[1] != 32:
        return None
    cc32 = cc32_msg[2]

    if len(pc_msg) < 2 or (pc_msg[0] & 0xF0) != 0xC0:
        return None
    if (pc_msg[0] & 0x0F) != channel:
        return None
    midi_pc = pc_msg[1]

    return wire_info_from_bank_pc(channel, cc0, cc32, midi_pc)


def compare_wire_info(
    expected: MidiWireInfo, actual: MidiWireInfo
) -> ValidationResult:
    """Field-by-field diff on channel, cc0, cc32, and midi_pc."""
    diff_fields = [
        field
        for field in _COMPARE_FIELDS
        if getattr(expected, field) != getattr(actual, field)
    ]
    return ValidationResult(
        ok=not diff_fields,
        expected=expected,
        actual=actual,
        diff_fields=diff_fields,
    )


def validate_bank_select_pc_send(
    channel: int,
    msb: int,
    lsb: int,
    program: int,
    expected: Optional[MidiWireInfo],
) -> Optional[ValidationResult]:
    """
    Build outgoing bytes, parse them, and compare to expected wire info.

    Returns None when expected is None (validation skipped).
    """
    if expected is None:
        return None

    messages = build_bank_select_pc_bytes(channel, msb, lsb, program)
    actual = parse_bank_select_pc_sequence(messages)
    if actual is None:
        actual = wire_info_from_bank_pc(channel, msb, lsb, program)
    return compare_wire_info(expected, actual)
