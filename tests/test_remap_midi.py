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


def test_track_by_name_onto_mono_analog(tmp_path):
    midi = mido.MidiFile(type=1, ticks_per_beat=480)
    midi.tracks.append(mido.MidiTrack([mido.MetaMessage("set_tempo", tempo=500000)]))

    def track(name, channel, notes, program=None):
        t = mido.MidiTrack([mido.MetaMessage("track_name", name=name)])
        if program is not None:
            t += [
                mido.Message("control_change", channel=channel, control=0, value=95),
                mido.Message("program_change", channel=channel, program=program),
            ]
        events = []
        for start, end, pitch in notes:
            events += [(start, 1, pitch), (end, 0, pitch)]
        last = 0
        for at, on, pitch in sorted(events, key=lambda e: (e[0], e[1])):
            kind = "note_on" if on else "note_off"
            t.append(mido.Message(kind, channel=channel, note=pitch, velocity=90 if on else 0, time=at - last))
            last = at
        return t

    # Bass: a chord (36 + 48 together), then an overlap (40 runs into 43)
    midi.tracks.append(track("Bass", 0, [(0, 480, 36), (0, 480, 48), (480, 1200, 40), (960, 1440, 43)], program=30))
    midi.tracks.append(track("Pad", 0, [(0, 1920, 60)], program=30))
    source = tmp_path / "song.mid"
    midi.save(source)
    code = remap_midi.main(
        ["file", str(source), "--out-dir", str(tmp_path), "--track-name", "Bass:3", "--mono", "3", "--keep-programs", "--strip-moved-programs"]
    )
    assert code == 0
    out = mido.MidiFile(tmp_path / "song - JDXi.mid")
    bass, pad = out.tracks[1], out.tracks[2]
    assert {m.channel for m in bass if m.type in ("note_on", "note_off")} == {2}
    assert not [m for m in bass if m.type == "program_change" or (m.type == "control_change" and m.control == 0)]
    assert [m.program for m in pad if m.type == "program_change"] == [30]  # untouched track keeps its program
    now, spans, held = 0, [], {}
    for m in bass:
        now += m.time
        if m.type == "note_on" and m.velocity:
            held[m.note] = now
        elif m.type in ("note_on", "note_off") and m.note in held:
            spans.append((held.pop(m.note), now, m.note))
    assert sorted(spans) == [(0, 480, 36), (480, 960, 40), (960, 1440, 43)]


def test_layout_and_transpose_by_track_name(tmp_path):
    def file(path, tracks):
        midi = mido.MidiFile(type=1, ticks_per_beat=480)
        midi.tracks.append(mido.MidiTrack([mido.MetaMessage("set_tempo", tempo=500000)]))
        for name, channel, program, notes in tracks:
            t = mido.MidiTrack([mido.MetaMessage("track_name", name=name)])
            if program is not None:
                t += [mido.Message("control_change", channel=channel, control=0, value=95), mido.Message("program_change", channel=channel, program=program)]
            for k, p in enumerate(notes):
                t += [mido.Message("note_on", channel=channel, note=p, velocity=90, time=0 if k == 0 else 0),
                      mido.Message("note_off", channel=channel, note=p, velocity=0, time=240)]
            midi.tracks.append(t)
        midi.save(path)
        return path

    template = file(tmp_path / "layout.mid", [("Pad", 1, 33, [60]), ("Lead", 0, 30, [72])])
    source = file(tmp_path / "new.mid", [("Lead", 5, None, [70, 71]), ("Pad", 6, 2, [50]), ("Other", 7, None, [40])])
    code = remap_midi.main(["file", str(source), "--out-dir", str(tmp_path), "--layout", str(template), "--transpose", "Lead:12", "--keep-programs"])
    assert code == 0
    out = mido.MidiFile(tmp_path / "new - JDXi.mid")
    tracks = {remap_midi.track_name(t): t for t in out.tracks}
    lead, pad, other = tracks["Lead"], tracks["Pad"], tracks["Other"]
    assert {m.channel for m in lead if not m.is_meta} == {0}
    assert [m.note for m in lead if m.type == "note_on"] == [82, 83]
    assert [m.program for m in lead if m.type == "program_change"] == [30]
    assert [m.program for m in pad if m.type == "program_change"] == [33]  # template's, not its own 2
    assert {m.channel for m in pad if not m.is_meta} == {1}
    assert {m.channel for m in other if not m.is_meta} == {7}  # not in the layout: unchanged


def test_merge_transcriptions_keeps_repeats_and_drops_doubles():
    import importlib.util as iu
    spec = iu.spec_from_file_location("classify_midi_parts", SCRIPT.parent / "classify_midi_parts.py")
    cmp = iu.module_from_spec(spec)
    sys.modules["classify_midi_parts"] = cmp
    spec.loader.exec_module(cmp)
    base = [(0.0, 0.5, 60, 90), (1.0, 1.2, 62, 90)]
    other = [
        (0.03, 0.4, 60, 80),  # the same note, 30 ms later
        (0.12, 0.6, 60, 80),  # the same note, 120 ms later, overlapping
        (0.5, 0.7, 60, 80),  # a repeat after the first ends
        (1.0, 1.2, 64, 80),  # a new pitch
    ]
    merged, counts = cmp.merge_transcriptions([base, other])
    assert counts == [2, 2]
    assert (0.5, 0.7, 60, 80) in merged and (1.0, 1.2, 64, 80) in merged


def test_merge_within_base_span():
    import importlib.util as iu
    spec = iu.spec_from_file_location("classify_midi_parts", SCRIPT.parent / "classify_midi_parts.py")
    cmp = iu.module_from_spec(spec)
    sys.modules["classify_midi_parts"] = cmp
    spec.loader.exec_module(cmp)
    base = [(20.0, 21.0, 60, 90), (100.0, 101.0, 62, 90)]
    other = [(3.0, 4.0, 50, 80), (50.0, 51.0, 64, 80), (120.0, 121.0, 65, 80)]
    merged, counts = cmp.merge_transcriptions([base, other], within_base=True)
    assert counts == [2, 1] and (50.0, 51.0, 64, 80) in merged
