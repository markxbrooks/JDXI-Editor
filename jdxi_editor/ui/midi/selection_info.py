"""
MIDI wire-format resolution for program and tone combo readouts.

Channel values are 0-based internally (MidiChannel enum). Display uses 1-based
channel numbers (Ch 1–16). CC0 and CC32 are bank-select values (MSB/LSB).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, List, Optional, Union

from jdxi_editor.midi.bank import Bank
from jdxi_editor.midi.channel.channel import MidiChannel

if TYPE_CHECKING:
    from jdxi_editor.ui.preset.model import ProgramChangeSelection


@dataclass(frozen=True)
class MidiWireInfo:
    """Resolved MIDI address for a program or tone selection."""

    channel: int  # 0-based MIDI channel
    bank: Bank
    program: int  # 0-based Program Change sent on wire

    def __post_init__(self) -> None:
        if not 0 <= self.channel <= 15:
            raise ValueError("Channel must be between 0 and 15")
        if not 0 <= self.program <= 127:
            raise ValueError("Program must be between 0 and 127")

    @property
    def cc0(self) -> int:
        return self.bank.msb

    @property
    def cc32(self) -> int:
        return self.bank.lsb

    @property
    def midi_pc(self) -> int:
        return self.program

    @property
    def channel_display(self) -> str:
        return channel_display_name(self.channel)

    @classmethod
    def from_selection(cls, selection: "ProgramChangeSelection") -> "MidiWireInfo":
        """Build wire info from a channel + preset selection."""
        return cls(
            channel=selection.channel,
            bank=selection.preset.bank,
            program=selection.preset.program,
        )


def channel_display_name(channel: int, label: Optional[str] = None) -> str:
    """Format a 0-based channel as ``Ch N`` with optional part label."""
    ch_num = channel + 1
    if label:
        return f"Ch {ch_num} ({label})"
    midi_ch = MidiChannel.from_midi_channel(channel)
    if midi_ch is not None:
        return str(midi_ch)
    return f"Ch {ch_num}"


def format_midi_wire_info(info: Optional[MidiWireInfo]) -> str:
    """Format wire info for UI readout or logs."""
    if info is None:
        return "MIDI  —"
    channel = channel_display_name(info.channel)
    return (
        f"MIDI  {channel} · "
        f"CC#0 {info.bank.msb} · "
        f"CC#32 {info.bank.lsb} · "
        f"PC {info.program}"
    )


def resolve_program_midi(
    bank: str,
    program_number: int,
    *,
    channel: int = MidiChannel.PROGRAM,
    channel_label: Optional[str] = "Program",
) -> Optional[MidiWireInfo]:
    """
    Resolve JD-Xi program bank/number to wire-format MIDI.

    :param bank: Bank letter A–H
    :param program_number: 1-based slot within bank (1–64)
    """
    from jdxi_editor.ui.editors.helpers.program import calculate_midi_values

    try:
        msb, lsb, midi_pc = calculate_midi_values(bank, program_number)
    except ValueError:
        return None
    if msb is None or lsb is None or midi_pc is None:
        return None

    return MidiWireInfo(
        channel=channel,
        bank=Bank(msb=msb, lsb=lsb),
        program=midi_pc,
    )


def resolve_program_midi_from_id(
    program_id: str,
    *,
    channel: int = MidiChannel.PROGRAM,
    channel_label: Optional[str] = "Program",
) -> Optional[MidiWireInfo]:
    """Resolve a program id such as ``A13`` or ``E05``."""
    if not program_id or len(program_id) < 3:
        return None
    bank = program_id[0].upper()
    try:
        number = int(program_id[1:3])
    except ValueError:
        return None
    return resolve_program_midi(
        bank, number, channel=channel, channel_label=channel_label
    )


def resolve_tone_midi(
    preset_id: Union[int, str],
    preset_list: List[Any],
    *,
    channel: int,
    channel_label: Optional[str] = None,
) -> Optional[MidiWireInfo]:
    """
    Resolve a tone preset id to wire-format MIDI using preset list lookup.

    :param preset_id: Preset number 1–256 (or id string)
    :param preset_list: Digital/Analog/Drum LIST or PROGRAM_CHANGE data
    :param channel: 0-based MIDI channel for the synth part
    """
    from jdxi_editor.ui.editors.helpers.preset import (
        get_preset_parameter_value,
        preset_to_jdxi_bank_pc,
    )

    try:
        preset_id_int = int(str(preset_id).strip())
    except (TypeError, ValueError):
        return None
    if preset_id_int < 1:
        return None

    program_number = str(preset_id_int).zfill(3)
    msb = get_preset_parameter_value("msb", program_number, preset_list)
    lsb = get_preset_parameter_value("lsb", program_number, preset_list)
    pc = get_preset_parameter_value("pc", program_number, preset_list)
    if msb is None or lsb is None or pc is None:
        return None

    bank_msb, bank_lsb, midi_pc = preset_to_jdxi_bank_pc(msb, lsb, pc)
    try:
        bank = Bank(msb=bank_msb, lsb=bank_lsb)
    except ValueError:
        # A preset list with an out-of-range bank shows no MIDI info for that
        # preset rather than stopping the editor from opening.
        return None
    return MidiWireInfo(
        channel=channel,
        bank=bank,
        program=midi_pc,
    )


def resolve_tone_midi_for_channel(
    preset_id: Union[int, str],
    preset_list: List[Any],
    channel: int,
    channel_label: str,
) -> Optional[MidiWireInfo]:
    """Resolve tone MIDI with an explicit channel override (cheat / automation)."""
    return resolve_tone_midi(
        preset_id,
        preset_list,
        channel=channel,
        channel_label=channel_label,
    )


def send_tone_with_expectation(
    midi_helper,
    preset_id: Union[int, str],
    preset_list: List[Any],
    channel: int,
    *,
    source: str,
    channel_label: Optional[str] = None,
) -> bool:
    """
    Resolve tone wire info, register validation expectation, and send bank+PC.

    Ensures readout resolver, send parameters, and validation expected match.
    """
    from jdxi_editor.log.midi_info import log_midi_wire_info
    from jdxi_editor.midi.validation.settings import is_midi_selection_validation_enabled

    expected = resolve_tone_midi(
        preset_id,
        preset_list,
        channel=channel,
        channel_label=channel_label,
    )
    if expected is None:
        return False

    if hasattr(midi_helper, "set_selection_expectation"):
        midi_helper.set_selection_expectation(expected, source, preset_id)
    if is_midi_selection_validation_enabled():
        log_midi_wire_info(expected)

    return midi_helper.send_bank_select_and_program_change(
        expected.channel,
        expected.cc0,
        expected.cc32,
        expected.midi_pc,
    )


def send_program_with_expectation(
    midi_helper,
    program_id: str,
    *,
    source: str,
    channel: int = MidiChannel.PROGRAM,
    channel_label: Optional[str] = "Program",
) -> bool:
    """Resolve program wire info, register validation expectation, and send bank+PC."""
    from jdxi_editor.log.midi_info import log_midi_wire_info
    from jdxi_editor.midi.validation.settings import is_midi_selection_validation_enabled

    expected = resolve_program_midi_from_id(
        program_id,
        channel=channel,
        channel_label=channel_label,
    )
    if expected is None:
        return False

    if hasattr(midi_helper, "set_selection_expectation"):
        midi_helper.set_selection_expectation(expected, source, program_id)
    if is_midi_selection_validation_enabled():
        log_midi_wire_info(expected)

    return midi_helper.send_bank_select_and_program_change(
        expected.channel,
        expected.cc0,
        expected.cc32,
        expected.midi_pc,
    )
