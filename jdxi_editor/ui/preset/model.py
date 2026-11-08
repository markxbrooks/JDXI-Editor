"""
Preset domain model: named sounds with MIDI wire addresses.

Catalog dictionaries are converted to Preset at the load_presets boundary;
callers work with immutable Preset / ProgramChangeSelection objects only.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.bank import Bank
from jdxi_editor.ui.editors.helpers.preset import preset_to_jdxi_bank_pc
from jdxi_editor.ui.preset.source import PresetSource
from jdxi_editor.ui.preset.utils import convert_preset_dict_to_list

PRESET_SOURCES: Dict[PresetSource, Callable[[], object]] = {
    PresetSource.DIGITAL: lambda: JDXi.UI.Preset.Digital.PROGRAM_CHANGE,
    PresetSource.ANALOG: lambda: JDXi.UI.Preset.Analog.PROGRAM_CHANGE,
    PresetSource.DRUMS: lambda: JDXi.UI.Preset.Drum.PROGRAM_CHANGE,
}


@dataclass(frozen=True)
class Preset:
    """A synthesizer preset and its MIDI wire address."""

    name: str
    bank: Bank
    program: int  # wire PC 0–127
    category: str = ""
    source: Optional[PresetSource] = None
    id: str = ""  # catalog display id ("001", "131")
    preset_number: Optional[int] = None  # 1-based catalogue slot

    def __post_init__(self) -> None:
        if not 0 <= self.program <= 127:
            raise ValueError("Program must be between 0 and 127")

    @property
    def midi_address(self) -> tuple[int, int, int]:
        """Return (bank MSB, bank LSB, program) as wire values."""
        return self.bank.msb, self.bank.lsb, self.program


@dataclass(frozen=True)
class ProgramChangeSelection:
    """A preset selected for transmission on a MIDI channel."""

    channel: int
    preset: Preset

    def __post_init__(self) -> None:
        if not 0 <= self.channel <= 15:
            raise ValueError("Channel must be between 0 and 15")

    @property
    def bank(self) -> Bank:
        return self.preset.bank

    @property
    def program(self) -> int:
        return self.preset.program

    @property
    def name(self) -> str:
        return self.preset.name


def load_presets(source: PresetSource) -> List[Preset]:
    """
    Convert catalog PROGRAM_CHANGE data for ``source`` into wire-address Presets.

    Dictionaries do not leave this boundary.
    """
    raw = convert_preset_dict_to_list(PRESET_SOURCES[source]())
    presets: List[Preset] = []
    for row in raw:
        msb, lsb, midi_pc = preset_to_jdxi_bank_pc(
            int(row["msb"]), int(row["lsb"]), int(row["pc"])
        )
        catalog_id = str(row.get("id", ""))
        # Prefer numeric catalogue id (tone list index); fall back to catalog pc
        if catalog_id.isdigit():
            preset_number = int(catalog_id)
        else:
            preset_number = int(row["pc"])
        presets.append(
            Preset(
                name=str(row.get("name", "")),
                bank=Bank(msb=msb, lsb=lsb),
                program=midi_pc,
                category=str(row.get("category", "")),
                source=source,
                id=catalog_id,
                preset_number=preset_number,
            )
        )
    return presets
