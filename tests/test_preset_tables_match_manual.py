"""
The preset tables must match Roland's own lists.

tests/fixtures/jdxi_manual_presets.json holds the Preset Tone Lists and the
Preset Drum Kit List from the JD-Xi Parameter Guide (pp. 44-47). Every copy of
the presets in the editor (ENUMERATED, LIST, PROGRAM_CHANGE) has to agree with
it: a wrong PC loads a different sound on the instrument, and a missing entry
cannot be selected at all.
"""

import json
from pathlib import Path

import pytest

from jdxi_editor.ui.preset.tone.analog.list import JDXiPresetToneListAnalog
from jdxi_editor.ui.preset.tone.digital.list import JDXiPresetToneListDigital
from jdxi_editor.ui.preset.tone.drum.list import JDXiPresetToneListDrum

MANUAL = json.loads(
    (Path(__file__).parent / "fixtures" / "jdxi_manual_presets.json").read_text(
        encoding="utf-8"
    )
)


def _rows(table):
    """Normalize a list-of-dicts or {number: {...}} table to {number: (name, msb, lsb, pc)}."""
    if isinstance(table, dict):
        return {
            int(number): (entry["Name"], entry["MSB"], entry["LSB"], entry["PC"])
            for number, entry in table.items()
        }
    return {
        int(entry["id"]): (
            entry["name"],
            int(float(entry["msb"])),
            int(float(entry["lsb"])),
            int(float(entry["pc"])),
        )
        for entry in table
    }


def _expected(kind):
    return {
        int(row["id"]): (row["name"], row["msb"], row["lsb"], row["pc"])
        for row in MANUAL[kind]
    }


TABLES = [
    ("digital", "PROGRAM_CHANGE", JDXiPresetToneListDigital.PROGRAM_CHANGE),
    ("digital", "LIST", JDXiPresetToneListDigital.LIST),
    ("analog", "PROGRAM_CHANGE", JDXiPresetToneListAnalog.PROGRAM_CHANGE),
    ("analog", "LIST", JDXiPresetToneListAnalog.LIST),
    ("drum", "PROGRAM_CHANGE", JDXiPresetToneListDrum.PROGRAM_CHANGE),
]


@pytest.mark.parametrize("kind,name,table", TABLES, ids=[f"{k}.{n}" for k, n, _ in TABLES])
def test_table_matches_the_parameter_guide(kind, name, table):
    assert _rows(table) == _expected(kind)


@pytest.mark.parametrize(
    "kind,enumerated",
    [
        ("digital", JDXiPresetToneListDigital.ENUMERATED),
        ("analog", JDXiPresetToneListAnalog.ENUMERATED),
        ("drum", JDXiPresetToneListDrum.ENUMERATED),
    ],
)
def test_enumerated_names_match_the_parameter_guide(kind, enumerated):
    expected = [f"{row['id']}: {row['name']}" for row in MANUAL[kind]]
    assert enumerated == expected


def test_bank_select_follows_the_midi_implementation():
    """Digital 1-128 on LSB 64 and 129-256 on LSB 65, PC 1-128 within each bank."""
    for number, (_, msb, lsb, pc) in _rows(JDXiPresetToneListDigital.PROGRAM_CHANGE).items():
        assert msb == 95
        assert (lsb, pc) == ((64, number) if number <= 128 else (65, number - 128))
