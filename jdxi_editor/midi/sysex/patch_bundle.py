"""
jdxi_editor.midi.sysex.patch_bundle
Write and read the JSON sections of a patch bundle (.jsz / .msz).

Saving takes each section from the synth's memory (see SynthMemory) when it
is complete there: the JSON is the parsed DT1, exactly as a reply from the
JD-Xi, plus ``SYSEX`` (that DT1) and ``VALUE_FORMAT: "midi"``. Sections the
memory does not hold are written from the editor controls and converted to
raw MIDI values.

Loading sends a section's ``SYSEX`` unchanged when it has one; older
sections, saved in display units, are converted first.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from decologr import Decologr as log

from picomidi.utils.conversion import split_16bit_value_to_nibbles

from jdxi_editor.midi.io.synth_memory import (
    SynthMemory,
    address_to_linear,
    build_dt1,
    linear_to_address,
)
from jdxi_editor.midi.sysex.parser.sysex import JDXiSysExParser
from jdxi_editor.midi.sysex.patch_values import (
    SYSEX,
    VALUE_FORMAT,
    VALUE_FORMAT_MIDI,
    METADATA_KEYS,
    is_midi_section,
    param_class_for_address,
    section_values_to_midi,
    upgrade_legacy_section,
)
from jdxi_editor.midi.sysex.sections import SysExSection

JDXI_HEADER_HEX = "f041100000000e"
# Temporary Program (18) and Temporary Tone (19): what a patch consists of
PATCH_AREAS = (0x18, 0x19)
_PARSER_NOISE = ("parameter_block", "block_name")


def section_file_name(address_hex: str) -> str:
    return f"jdxi_tone_data_{address_hex.lower()}.json"


def section_from_dt1(dt1: bytes) -> dict:
    """Bundle JSON for one DT1 section: parsed values, 4-byte ADDRESS, SYSEX."""
    try:
        parsed = JDXiSysExParser().parse_bytes(dt1)
        section = {k: v for k, v in parsed.items() if k not in _PARSER_NOISE}
    except Exception as ex:  # keep the bytes even if the parser cannot name them
        log.warning(f"Could not parse section {dt1[8:12].hex()}: {ex}", scope="patch_bundle")
        section = {SysExSection.JD_XI_HEADER: JDXI_HEADER_HEX}
    section[SysExSection.ADDRESS] = dt1[8:12].hex()  # parser reports cmd + 3 bytes
    section[VALUE_FORMAT] = VALUE_FORMAT_MIDI
    section[SYSEX] = dt1.hex(" ").upper()
    return section


def write_memory_sections(memory: SynthMemory, folder: Path) -> set[str]:
    """Write every complete patch section in *memory*; returns their addresses."""
    written: set[str] = set()
    for address, size in memory.sections():
        if address[0] not in PATCH_AREAS:
            continue
        dt1 = memory.section_dt1(address, size)
        if dt1 is None:
            continue
        section = section_from_dt1(dt1)
        path = folder / section_file_name(section[SysExSection.ADDRESS])
        path.write_text(json.dumps(section, indent=2), encoding="utf-8")
        written.add(section[SysExSection.ADDRESS])
    return written


def convert_editor_sections(folder: Path, skip: set[str]) -> int:
    """
    Convert the editor-written sections in *folder* to raw MIDI values.

    :param skip: addresses written from the synth's memory (already raw)
    :return: number of files converted
    """
    converted = 0
    for path in folder.glob("jdxi_tone_data_*.json"):
        try:
            section = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        address = str(section.get(SysExSection.ADDRESS, "")).lower()
        if address in skip or is_midi_section(section):
            continue
        path.write_text(
            json.dumps(section_values_to_midi(section), indent=2), encoding="utf-8"
        )
        converted += 1
    return converted


def section_sysex(section: dict) -> Optional[bytes]:
    """The section's DT1 message, if it carries one."""
    sysex = section.get(SYSEX)
    if not sysex:
        return None
    try:
        return bytes.fromhex(str(sysex))
    except ValueError:
        return None


def load_section(section: dict) -> dict:
    """A loaded section in raw MIDI values (old sections are converted)."""
    return upgrade_legacy_section(section)


def section_param_dt1s(section: dict) -> list[bytes]:
    """
    One DT1 per parameter of a section in raw MIDI values.

    The values are written as they are (no display conversion), at the
    section address plus the parameter's offset; 4-nibble parameters are
    split as the JD-Xi expects.
    """
    address_hex = str(section.get(SysExSection.ADDRESS, "")).lower()
    param_class = param_class_for_address(address_hex)
    if param_class is None or len(address_hex) != 8:
        return []
    base = address_to_linear(bytes.fromhex(address_hex))
    messages = []
    for name, value in section.items():
        if name in METADATA_KEYS or isinstance(value, bool) or not isinstance(value, int):
            continue
        param = param_class.get_by_name(name)
        if param is None:
            continue
        size = param.get_nibbled_size() if hasattr(param, "get_nibbled_size") else 1
        if size == 1:
            if not 0 <= value <= 127:
                continue
            data = [value]
        else:
            if not 0 <= value <= 0xFFFF:
                continue
            data = split_16bit_value_to_nibbles(value)
        messages.append(build_dt1(linear_to_address(base + int(param.address)), data))
    return messages
