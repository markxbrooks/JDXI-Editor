"""
MIDI wire-format resolution for program and tone combo readouts.

Channel values are 0-based internally (MidiChannel enum). Display uses 1-based
channel numbers (Ch 1–16). CC0 and CC32 are bank-select values (MSB/LSB).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Optional, Union

from jdxi_editor.midi.channel.channel import MidiChannel
from jdxi_editor.ui.editors.helpers.preset import (
    get_preset_parameter_value,
    preset_to_jdxi_bank_pc,
)
from jdxi_editor.ui.editors.helpers.program import calculate_midi_values


@dataclass(frozen=True)
class MidiWireInfo:
    """Wire-format MIDI values that will be sent for a program or tone selection."""

    channel: int  # 0-based MIDI channel
    channel_display: str  # e.g. "Ch 3 (Analog)"
    cc0: int  # Bank MSB (CC#0)
    cc32: int  # Bank LSB (CC#32)
    midi_pc: int  # 0-based Program Change sent on wire
    preset_pc: Optional[int] = None  # 1-based slot from preset list or internal PC
    program_id: Optional[str] = None  # e.g. "A01" for JD-Xi programs


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
    parts = [
        f"MIDI  {info.channel_display}",
        f"CC0: {info.cc0}",
        f"CC32: {info.cc32}",
        f"PC: {info.midi_pc}",
    ]
    if info.program_id:
        parts.append(info.program_id)
    line = "  ·  ".join(parts)
    if info.preset_pc is not None and info.program_id is None:
        line += f"\n      (preset slot {info.preset_pc})"
    return line


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
    msb, lsb, midi_pc = calculate_midi_values(bank, program_number)
    if msb is None or lsb is None or midi_pc is None:
        return None

    internal_pc = midi_pc + 1
    program_id = f"{bank.upper()}{program_number:02d}"
    return MidiWireInfo(
        channel=channel,
        channel_display=channel_display_name(channel, channel_label),
        cc0=msb,
        cc32=lsb,
        midi_pc=midi_pc,
        preset_pc=internal_pc,
        program_id=program_id,
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
    info = resolve_program_midi(
        bank, number, channel=channel, channel_label=channel_label
    )
    if info is None:
        return None
    return MidiWireInfo(
        channel=info.channel,
        channel_display=info.channel_display,
        cc0=info.cc0,
        cc32=info.cc32,
        midi_pc=info.midi_pc,
        preset_pc=info.preset_pc,
        program_id=program_id.upper(),
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
    label = channel_label
    if label is None:
        midi_ch = MidiChannel.from_midi_channel(channel)
        if midi_ch == MidiChannel.PROGRAM:
            label = "Program"
    return MidiWireInfo(
        channel=channel,
        channel_display=channel_display_name(channel, label),
        cc0=bank_msb,
        cc32=bank_lsb,
        midi_pc=midi_pc,
        preset_pc=pc,
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
