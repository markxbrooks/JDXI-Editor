"""tie-notes: joining same-pitch fragments a tremolo split, judged on a
hand-made semitone spectrogram (0.01 s frames)."""

import sys
from pathlib import Path

import mido
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from midi_parts import ties  # noqa: E402
from midi_parts.evidence import SemitoneSpectrogram  # noqa: E402

HOP = 0.01
C2 = 36


def _spec(seconds: float, held: list[tuple[int, float, float, float]]) -> SemitoneSpectrogram:
    """Level 0.2 everywhere; each (pitch, start, end, level) raises one pitch."""
    level = np.full((int(seconds / HOP), 128), 0.2, dtype=np.float32)
    for p, a, b, v in held:
        level[int(round(a / HOP)) : int(round(b / HOP)), p] = v
    return SemitoneSpectrogram(level, 0.0, HOP, 0.0)


def _note(start: float, end: float, pitch: int = C2, velocity: int = 60) -> ties.TieNote:
    # 1 s = 1000 ticks keeps the arithmetic readable
    return ties.TieNote(start, end, pitch, velocity, int(start * 1000), int(end * 1000), 0)


def test_abutting_fragments_of_a_held_note_become_one_note():
    spec = _spec(3.0, [(C2, 0.0, 2.0, 2.0)])
    frags = [_note(0.1, 0.4, velocity=50), _note(0.4, 0.7, velocity=70), _note(0.7, 1.0, velocity=40)]
    out, joints = ties.plan_ties(frags, spec)
    assert [(n.start, n.end, n.velocity) for n in out] == [(0.1, 1.0, 70)]
    assert [j.decision for j in joints] == ["abutting", "abutting"]


def test_a_gap_is_bridged_only_when_the_pitch_is_held_through_it():
    held = _spec(3.0, [(C2, 0.0, 2.0, 2.0)])
    out, joints = ties.plan_ties([_note(0.1, 0.5), _note(0.8, 1.2)], held)
    assert len(out) == 1 and joints[0].decision == "bridged"

    # The pitch stops in the gap and comes back without a sharp attack (a fade)
    stopped = _spec(3.0, [(C2, 0.0, 0.5, 2.0), (C2, 0.75, 1.5, 2.0)])
    stopped.level[75:135, C2] = np.linspace(0.2, 2.0, 60)  # rises over 0.6 s: no re-attack
    out, joints = ties.plan_ties([_note(0.1, 0.5), _note(0.8, 1.2)], stopped)
    assert len(out) == 2 and joints[0].decision == "kept: audio"


def test_a_new_attack_keeps_abutting_notes_apart():
    spec = _spec(3.0, [(C2, 0.0, 0.45, 0.4), (C2, 0.5, 1.5, 2.5)])
    out, joints = ties.plan_ties([_note(0.1, 0.5), _note(0.5, 1.0)], spec)
    assert len(out) == 2 and joints[0].decision == "kept: re-attack"


def test_notes_further_apart_than_max_gap_are_not_joints():
    spec = _spec(3.0, [(C2, 0.0, 3.0, 2.0)])
    out, joints = ties.plan_ties([_note(0.1, 0.5), _note(1.5, 2.0)], spec)
    assert len(out) == 2 and joints == []


def test_other_pitches_in_between_do_not_block_a_tie():
    spec = _spec(3.0, [(C2, 0.0, 2.0, 2.0)])
    notes = [_note(0.1, 0.4), _note(0.4, 0.42, pitch=29, velocity=30), _note(0.4, 0.8)]
    out, _ = ties.plan_ties(notes, spec)
    assert sorted((n.pitch, n.start, n.end) for n in out) == [(29, 0.4, 0.42), (C2, 0.1, 0.8)]


def test_tie_midi_rewrites_only_the_named_track(tmp_path):
    tpb = 500  # with 120 BPM, 1000 ticks = 1 s
    bass = mido.MidiTrack([mido.MetaMessage("track_name", name="Bass"), mido.Message("program_change", program=38, time=0)])
    for i in range(4):  # four abutting 0.125 s fragments from 0.25 s
        bass += [mido.Message("note_on", note=C2, velocity=50 + i, time=250 if i == 0 else 0), mido.Message("note_off", note=C2, time=125)]
    bass.append(mido.Message("control_change", control=7, value=90, time=100))
    lead = mido.MidiTrack([mido.MetaMessage("track_name", name="Lead"), mido.Message("note_on", note=72, velocity=80, time=0), mido.Message("note_off", note=72, time=250)])
    midi = mido.MidiFile(ticks_per_beat=tpb)
    midi.tracks += [mido.MidiTrack([mido.MetaMessage("set_tempo", tempo=500000)]), bass, lead]
    path = tmp_path / "in.mid"
    midi.save(path)

    midi = mido.MidiFile(path)
    lead_before = str(midi.tracks[2])
    results = ties.tie_midi(midi, ["Bass"], _spec(3.0, [(C2, 0.0, 2.0, 2.0)]))
    assert results[0].before == 4 and len(results[0].notes) == 1
    midi.save(tmp_path / "out.mid")

    midi = mido.MidiFile(tmp_path / "out.mid")
    notes = ties.track_notes(midi, 1)
    assert [(n.start_tick, n.end_tick, n.velocity) for n in notes] == [(250, 750, 53)]
    assert str(midi.tracks[2]) == lead_before
    ticks, events = 0, {}
    for msg in midi.tracks[1]:
        ticks += msg.time
        if msg.type in ("program_change", "control_change"):
            events[msg.type] = ticks
    assert events == {"program_change": 0, "control_change": 850}
