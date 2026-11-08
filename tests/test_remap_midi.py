#!/usr/bin/env python3
"""scripts/remap_midi.py: tracks and channels move onto JD-Xi parts, GM
program/bank selects and SysEx are stripped, timing is preserved."""

import importlib.util
import sys
from pathlib import Path

import mido
import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "remap_midi.py"
spec = importlib.util.spec_from_file_location("remap_midi", SCRIPT)
remap_midi = importlib.util.module_from_spec(spec)
sys.modules["remap_midi"] = remap_midi  # dataclasses look the module up
spec.loader.exec_module(remap_midi)


def _song(path: Path) -> Path:
    midi = mido.MidiFile(ticks_per_beat=480)
    midi.tracks.append(mido.MidiTrack([mido.MetaMessage("set_tempo", tempo=500000)]))
    for name, ch, note in (("Strings", 2, 60), ("Bass", 0, 36), ("Echo", 1, 72)):
        midi.tracks.append(
            mido.MidiTrack(
                [
                    mido.MetaMessage("track_name", name=name),
                    mido.Message("control_change", channel=ch, control=0, value=0),
                    mido.Message("control_change", channel=ch, control=32, value=0),
                    mido.Message("program_change", channel=ch, program=30),
                    mido.Message("control_change", channel=ch, control=7, value=90),
                    mido.Message("sysex", data=[0x41, 0x10, 0x42], time=10),
                    mido.Message("note_on", channel=ch, note=note, velocity=100, time=110),
                    mido.Message("note_off", channel=ch, note=note, time=480),
                ]
            )
        )
    midi.save(path)
    return path


def _notes(midi):
    out, now = [], 0
    for track in midi.tracks:
        now = 0
        for msg in track:
            now += msg.time
            if msg.type == "note_on":
                out.append((now, msg.channel + 1, msg.note, msg.velocity))
    return sorted(out)


def test_remap_moves_strips_and_keeps_timing(tmp_path):
    plan = remap_midi.RemapPlan(
        source="in.mid",
        output="out.mid",
        channel_map={3: 1, 1: 3},
        tracks={3: None},
        expect_names={1: "Strings"},
        velocity_scale={3: 0.5},
    )
    midi, lines = remap_midi.remap_file(plan, _song(tmp_path / "in.mid"))
    msgs = [m for t in midi.tracks for m in t]
    assert not [m for m in msgs if m.type in ("program_change", "sysex")]
    assert not [m for m in msgs if m.type == "control_change" and m.control in (0, 32)]
    assert [m.value for m in msgs if m.type == "control_change"] == [90, 90]  # CC7 kept
    # Strings ch3 -> 1, bass ch1 -> 3 (velocity halved), echo track dropped
    assert _notes(midi) == [(120, 1, 60, 100), (120, 3, 36, 50)]
    assert any("removed:" in line and "sysex 3" in line for line in lines)


def test_wrong_track_name_is_refused(tmp_path):
    plan = remap_midi.RemapPlan("in.mid", "out.mid", expect_names={1: "Organ"})
    with pytest.raises(ValueError, match="expected 'Organ'"):
        remap_midi.remap_file(plan, _song(tmp_path / "in.mid"))


def test_cli_never_overwrites_the_source(tmp_path):
    src = _song(tmp_path / "song.mid")
    before = src.read_bytes()
    code = remap_midi.main(
        ["file", str(src), "--output", "song.mid", "--out-dir", str(tmp_path)]
    )
    assert code == 1 and src.read_bytes() == before
    assert remap_midi.main(["file", str(src), "--out-dir", str(tmp_path / "o")]) == 0
    assert (tmp_path / "o" / "song - JDXi.mid").exists()
