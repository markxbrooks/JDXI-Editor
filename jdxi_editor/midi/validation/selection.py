"""
Cross-validation of bank-select + program-change sends against MidiWireInfo.

Pure functions with no Qt dependency (aside from MidiWireInfo dataclass).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from jdxi_editor.midi.bank import Bank
from jdxi_editor.midi.message.control.message import ControlChangeMessage
from jdxi_editor.midi.message.program.message import ProgramChangeMessage
from jdxi_editor.ui.midi.selection_info import MidiWireInfo

_COMPARE_FIELDS = ("channel", "bank", "program")


@dataclass(frozen=True)
class ValidationResult:
    """Outcome of comparing expected and actual MIDI wire values."""

    expected: MidiWireInfo
    actual: MidiWireInfo
    diff_fields: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.diff_fields

    @classmethod
    def compare(
        cls,
        expected: MidiWireInfo,
        actual: MidiWireInfo,
    ) -> "ValidationResult":
        differences = tuple(
            field
            for field in _COMPARE_FIELDS
            if getattr(expected, field) != getattr(actual, field)
        )
        return cls(
            expected=expected,
            actual=actual,
            diff_fields=differences,
        )


def wire_info_from_bank_pc(
    channel: int,
    bank_msb: int,
    bank_lsb: int,
    midi_pc: int,
) -> MidiWireInfo:
    """Build MidiWireInfo from send parameters."""
    return MidiWireInfo(
        channel=channel,
        bank=Bank(msb=bank_msb, lsb=bank_lsb),
        program=midi_pc,
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
    """Field-by-field diff on channel, bank, and program."""
    return ValidationResult.compare(expected, actual)


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
