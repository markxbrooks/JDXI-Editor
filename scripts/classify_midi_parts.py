#!/usr/bin/env python3
"""
Classify the notes of an audio-to-MIDI transcription (e.g. Spotify Basic
Pitch: one track, every instrument mixed) into instrumental parts.

MIDI keeps pitch, timing, length and velocity but not the instrument, so parts
are inferred from behaviour, in stages:

1. Clean up: merge split notes; mark overtone "ghosts" (an octave, twelfth or
   two octaves above a louder note starting with it, a Basic Pitch artefact).
2. Beat grid: the eighth-note period and phase, from the onsets.
3. Sections: split where note density, length and register change.
4. Lines: trace monophonic lines through the notes (pitch closeness, gaps).
5. Labels:
   a. With --reference (a sequence of the same piece with one named track per
      part): align it to the transcription (one tempo ratio and offset, on
      pitch-class onset profiles, then local timing) and give each
      transcribed note the matching reference note's part.
   b. Other notes: a profile learned from (a) in the same section, else rules
      (Bass, Chords, Lead, Sequence, High), smoothed along each line.
   c. --corrections: your fixes, applied last.
6. Output: a MIDI file with one named track per part (plus Ghost), a colour-
   coded piano roll, a CSV of every note, and a report.

Usage:
    python scripts/classify_midi_parts.py classify "OxygeneV - basic_pitch.mid" \
        --reference "oxygene5 2.mid" --out-dir parts

    # Accuracy check on audio whose parts are known:
    python scripts/classify_midi_parts.py render-test "oxygene5 2.mid" test.wav
    #   ... transcribe test.wav with Basic Pitch, then:
    python scripts/classify_midi_parts.py evaluate test_basic_pitch.mid \
        --truth "oxygene5 2.mid"

    # Rebuild the Chords track as held chords (chroma + Viterbi), optionally
    # limited to the chords in the score:
    python scripts/classify_midi_parts.py chords "OxygeneV - basic_pitch - parts.mid" \
        --chords "C,Am,A7,Dm,G7,E7,D7,G" --audio OxygeneV.wav

    # Give the file the song's real tempo map (steady section fitted, bars
    # before it from the chord chart) and quantize the steady section:
    python scripts/classify_midi_parts.py quantize "... - chords.mid" \
        --bars "... - chord chart.csv"

    # Repair loops that repeat (including transposed copies). The original
    # file is left as it is; odd notes go to a "<track> once" review track:
    python scripts/classify_midi_parts.py repeats "... - quantized.mid"

    # One note gate per track (25/50/75/100% of that track's own step).
    # Onsets are not moved:
    python scripts/classify_midi_parts.py gates "... - parts.mid"

    # How much of the recording's pitch content MIDI files carry:
    python scripts/classify_midi_parts.py roundtrip OxygeneV.wav a.mid b.mid [--render]

    # The key (whole piece and sections); an optional filter, off unless asked:
    python scripts/classify_midi_parts.py key parts.mid
    python scripts/classify_midi_parts.py filter-key parts.mid --chords chart.csv --keep-separate

    # Repair the sequenced section from its repetitions (after quantize):
    python scripts/classify_midi_parts.py patterns "... - quantized.mid"

    # Combine transcriptions (Basic Pitch on the mix and on stems, Logic's
    # with its tempo map) before classifying:
    python scripts/classify_midi_parts.py merge mix.mid other.mid bass.mid vocals.mid \
        "OxygeneV.mid+OxygeneV.tempo.mid"

    # Straight, triplet, swung or free, bar by bar (before quantizing):
    python scripts/classify_midi_parts.py rhythm "<parts>.mid" --bars chart.csv --per-track

    # Arpeggiator/sequencer figures: start, stop, notes, rests, velocity, errors
    python scripts/classify_midi_parts.py cycles "... - patterns.mid" --track SeqSynth1 [--repair]

    # Musical fidelity: harmony, rhythm, dynamics, texture and form against the recording
    python scripts/classify_midi_parts.py musicality OxygeneV.wav a.mid b.mid [--plot dir] [--sections sections.json]

    # Diagnosis: weak sections, likely causes, what to try (changes nothing)
    python scripts/classify_midi_parts.py diagnose OxygeneV.wav final.mid --sections sections.json

Corrections file (JSON), each rule applied in order:
    [{"start": 330, "end": 580, "low": 24, "high": 47, "part": "BassSynth"}]
(seconds and MIDI note numbers, inclusive; omitted fields mean "any").
"""

from __future__ import annotations

import argparse
import bisect
import csv
import json
import math
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional

import mido
import numpy as np

DRUM_CHANNEL = 9  # MIDI channel 10
GHOST = "Ghost"
RULE_PARTS = ("Bass", "Chords", "Lead", "Sequence", "High")
GROUP_S = 0.04  # onsets this close count as simultaneous
FRAME_S = 0.25  # alignment frame
SOUNDFONT = Path("~/SoundFonts/FluidR3_GM.sf2").expanduser()


@dataclass
class Note:
    start: float
    end: float
    pitch: int
    velocity: int
    flag: str = ""  # "ghost"
    section: int = 0
    line: int = -1
    part: str = ""
    confidence: float = 0.0
    source: str = ""  # reference | profile | rule | manual
    poly: int = 1  # notes sounding at this onset (not ghosts)
    lowest: bool = False
    highest: bool = False
    on_grid: bool = False

    @property
    def dur(self) -> float:
        return self.end - self.start


@dataclass
class RefNote:
    start: float
    end: float
    pitch: int
    part: str
    mapped: float = 0.0


@dataclass
class Grid:
    period: float  # seconds per grid step (eighth note)
    phase: float

    @property
    def bpm(self) -> float:
        return 60.0 / (2 * self.period)

    def offset(self, t: float) -> float:
        """Distance from the nearest grid step, in steps (0-0.5)."""
        x = ((t - self.phase) / self.period) % 1.0
        return min(x, 1.0 - x)


@dataclass
class Result:
    notes: list[Note]
    sections: list[tuple[float, float]]
    grids: list[Optional[Grid]]
    merged: int = 0
    alignment: Optional[dict] = None
    recall: dict[str, tuple[int, int]] = field(default_factory=dict)


# --- Loading -----------------------------------------------------------------


def _paired_notes(path: Path) -> list[tuple[float, float, int, int, int, str]]:
    """(start, end, pitch, velocity, channel, track name) in seconds."""
    midi = mido.MidiFile(path)
    tempo_map = _tempo_map(midi)
    out = []
    for track in midi.tracks:
        name = next((m.name.strip() for m in track if m.type == "track_name"), "")
        held: dict[tuple[int, int], list[tuple[float, int]]] = defaultdict(list)
        ticks = 0
        for msg in track:
            ticks += msg.time
            if msg.type not in ("note_on", "note_off"):
                continue
            key = (msg.channel, msg.note)
            now = _seconds(ticks, tempo_map, midi.ticks_per_beat)
            if msg.type == "note_on" and msg.velocity > 0:
                held[key].append((now, msg.velocity))
            elif held[key]:
                start, velocity = held[key].pop(0)
                if now > start:
                    out.append((start, now, msg.note, velocity, msg.channel, name))
    return sorted(out)


def _tempo_map(midi: mido.MidiFile) -> list[tuple[int, int]]:
    changes = []
    for track in midi.tracks:
        ticks = 0
        for msg in track:
            ticks += msg.time
            if msg.type == "set_tempo":
                changes.append((ticks, msg.tempo))
    changes.sort()
    if not changes or changes[0][0] != 0:
        changes.insert(0, (0, 500000))
    return changes


def _seconds(ticks: int, tempo_map: list[tuple[int, int]], tpb: int) -> float:
    seconds, last_tick, tempo = 0.0, 0, tempo_map[0][1]
    for change_tick, change_tempo in tempo_map[1:]:
        if change_tick >= ticks:
            break
        seconds += (change_tick - last_tick) * tempo / (tpb * 1e6)
        last_tick, tempo = change_tick, change_tempo
    return seconds + (ticks - last_tick) * tempo / (tpb * 1e6)


def load_transcription(path: Path) -> list[Note]:
    return [Note(s, e, p, v) for s, e, p, v, _ch, _name in _paired_notes(path)]


def load_reference(path: Path) -> list[RefNote]:
    """Pitched notes of a sequence with one named track per part (no drums)."""
    rows = [r for r in _paired_notes(path) if r[4] != DRUM_CHANNEL]
    # Tracks sharing a name (e.g. two "BassSynth") become "BassSynth", "BassSynth 2"
    channels_by_name: dict[str, list[int]] = defaultdict(list)
    for _s, _e, _p, _v, ch, name in rows:
        if ch not in channels_by_name[name]:
            channels_by_name[name].append(ch)
    notes = []
    for s, e, p, _v, ch, name in rows:
        label = name or f"Channel {ch + 1}"
        rank = channels_by_name[name].index(ch)
        notes.append(RefNote(s, e, p, label if rank == 0 else f"{label} {rank + 1}"))
    return notes


# --- Stage 1: clean up -------------------------------------------------------


def merge_fragments(notes: list[Note], overlap: float = 0.0005) -> tuple[list[Note], int]:
    """Join a note to the next one of the same pitch when they overlap
    (Basic Pitch restarted a pitch it was still holding). Back-to-back notes
    are kept: in a sequencer part they are repeated notes."""
    by_pitch: dict[int, list[Note]] = defaultdict(list)
    for note in notes:
        by_pitch[note.pitch].append(note)
    out, merged = [], 0
    for pitch_notes in by_pitch.values():
        pitch_notes.sort(key=lambda n: n.start)
        current = pitch_notes[0]
        for note in pitch_notes[1:]:
            if note.start < current.end - overlap:
                current.end = max(current.end, note.end)
                current.velocity = max(current.velocity, note.velocity)
                merged += 1
            else:
                out.append(current)
                current = note
        out.append(current)
    out.sort(key=lambda n: (n.start, n.pitch))
    return out, merged


def mark_ghosts(notes: list[Note]) -> int:
    """Flag likely overtones: 12/19/24 semitones above a clearly louder note
    that starts with it and lasts at least as long."""
    starts = [n.start for n in notes]
    count = 0
    for note in notes:
        lo = bisect.bisect_left(starts, note.start - GROUP_S)
        hi = bisect.bisect_right(starts, note.start + GROUP_S)
        for other in notes[lo:hi]:
            if (
                other is not note
                and note.pitch - other.pitch in (12, 19, 24)
                and note.velocity <= 0.85 * other.velocity
                and note.end <= other.end + 0.05
            ):
                note.flag = "ghost"
                count += 1
                break
    return count


# --- Stage 2: beat grid ------------------------------------------------------


def estimate_grid(notes: list[Note], lo: float = 0.10, hi: float = 0.30) -> Optional[Grid]:
    """Eighth-note period (lo-hi s) from the onset autocorrelation."""
    onsets = np.array([n.start for n in notes if not n.flag])
    if len(onsets) < 32:
        return None
    step = 0.005
    train = np.zeros(int((onsets.max() - onsets.min()) / step) + 2)
    np.add.at(train, ((onsets - onsets.min()) / step).astype(int), 1.0)
    spectrum = np.fft.rfft(train - train.mean(), n=2 * len(train))
    corr = np.fft.irfft(spectrum * np.conj(spectrum))[: len(train)]
    a, b = int(lo / step), int(hi / step)
    if b >= len(corr):
        return None
    lag = a + int(np.argmax(corr[a:b]))
    # Refine past the 5 ms step: the period at which onsets line up best
    # (a small period error accumulates over hundreds of notes)
    best_strength, period = -1.0, lag * step
    for candidate in np.linspace(lag * step * 0.97, lag * step * 1.03, 241):
        strength = abs(np.exp(2j * np.pi * onsets / candidate).mean())
        if strength > best_strength:
            best_strength, period = strength, float(candidate)
    angles = 2 * np.pi * (onsets / period)
    phase = (math.atan2(np.sin(angles).mean(), np.cos(angles).mean()) / (2 * np.pi)) * period
    return Grid(period, phase % period)


# --- Stage 3: sections -------------------------------------------------------


def find_sections(
    notes: list[Note], window: float = 10.0, max_sections: int = 3, min_windows: int = 6
) -> list[tuple[float, float]]:
    """Binary segmentation on per-window density, note length and register."""
    real = [n for n in notes if not n.flag]
    if not real:
        return [(0.0, 0.0)]
    end = max(n.end for n in real)
    count = max(1, math.ceil(end / window))
    feats = np.zeros((count, 3))
    last = np.array([0.0, math.log(0.2), 60.0])
    for w in range(count):
        seg = [n for n in real if w * window <= n.start < (w + 1) * window]
        if seg:
            last = np.array(
                [
                    math.log1p(len(seg)),
                    float(np.median([math.log(max(n.dur, 0.01)) for n in seg])),
                    float(np.median([n.pitch for n in seg])),
                ]
            )
            feats[w] = last
        else:
            feats[w] = [0.0, last[1], last[2]]
    std = feats.std(axis=0)
    feats = (feats - feats.mean(axis=0)) / np.where(std > 0, std, 1)

    def sse(a: int, b: int) -> float:
        block = feats[a:b]
        return float(((block - block.mean(axis=0)) ** 2).sum()) if b > a else 0.0

    bounds = [0, count]
    while len(bounds) - 1 < max_sections:
        best = None
        for k in range(len(bounds) - 1):
            a, b = bounds[k], bounds[k + 1]
            total = sse(a, b)
            for split in range(a + min_windows, b - min_windows + 1):
                gain = total - sse(a, split) - sse(split, b)
                if best is None or gain > best[0]:
                    best = (gain, split, total)
        if best is None or best[0] < 0.3 * max(best[2], 1e-9):
            break
        bounds = sorted(bounds + [best[1]])
    return [(bounds[k] * window, bounds[k + 1] * window) for k in range(len(bounds) - 1)]


# --- Stage 4: lines and context ----------------------------------------------


def _groups(notes: list[Note]) -> Iterable[list[Note]]:
    group: list[Note] = []
    for note in sorted(notes, key=lambda n: (n.start, n.pitch)):
        if group and note.start - group[0].start > GROUP_S:
            yield group
            group = []
        group.append(note)
    if group:
        yield group


def trace_lines(notes: list[Note], max_jump: int = 12, max_gap: float = 2.0) -> int:
    """Assign each (non-ghost) note to a monophonic line."""
    lines: list[dict] = []  # {"pitch", "end"}
    for group in _groups([n for n in notes if not n.flag]):
        start = group[0].start
        open_lines = [
            i for i, line in enumerate(lines)
            if line["end"] - start <= 0.05 and start - line["end"] <= max_gap
        ]
        pairs = []
        for note in group:
            for i in open_lines:
                jump = abs(note.pitch - lines[i]["pitch"])
                if jump <= max_jump:
                    gap = max(0.0, start - lines[i]["end"])
                    pairs.append((jump + 2.0 * max(0.0, gap - 0.5), id(note), i, note))
        pairs.sort(key=lambda p: (p[0], p[1]))
        used_notes, used_lines = set(), set()
        for _cost, key, i, note in pairs:
            if key in used_notes or i in used_lines:
                continue
            note.line = i
            lines[i].update(pitch=note.pitch, end=note.end)
            used_notes.add(key)
            used_lines.add(i)
        for note in group:
            if id(note) not in used_notes:
                note.line = len(lines)
                lines.append({"pitch": note.pitch, "end": note.end})
    return len(lines)


def add_context(notes: list[Note], grids: list[Optional[Grid]]) -> None:
    real = sorted((n for n in notes if not n.flag), key=lambda n: n.start)
    starts = [n.start for n in real]
    for note in notes:
        lo = bisect.bisect_left(starts, note.start - 8.0)
        hi = bisect.bisect_right(starts, note.start + GROUP_S)
        sounding = [o for o in real[lo:hi] if o.end > note.start + 0.01]
        pitches = [o.pitch for o in sounding] or [note.pitch]
        note.poly = max(1, len(sounding))
        note.lowest = note.pitch <= min(pitches)
        note.highest = note.pitch >= max(pitches)
        grid = grids[note.section] if note.section < len(grids) else None
        note.on_grid = bool(grid and grid.offset(note.start) < 0.15)


# --- Stage 5a: reference alignment -------------------------------------------


def _onset_chroma(events: Iterable[tuple[float, int, float]], frames: int) -> np.ndarray:
    """Pitch-class onset strength per FRAME_S frame."""
    m = np.zeros((frames, 12))
    for start, pitch, weight in events:
        k = int(start / FRAME_S)
        if 0 <= k < frames:
            m[k, pitch % 12] += weight
    return m


def align_reference(
    notes: list[Note], ref: list[RefNote], ratios: Iterable[float] = np.arange(0.70, 1.40, 0.005)
) -> dict:
    """Find the tempo ratio and offset that best overlay the reference's
    pitch-class onsets on the transcription's; sets RefNote.mapped. The local
    timing drift left over is corrected while matching."""
    t_frames = int(max(n.end for n in notes) / FRAME_S) + 1
    target = _onset_chroma(((n.start, n.pitch, n.velocity / 127) for n in notes if not n.flag), t_frames)
    energy = np.concatenate(([0.0], np.cumsum((target ** 2).sum(axis=1))))
    best = (-1.0, 1.0, 0)
    for ratio in ratios:
        length = int(max(r.start for r in ref) * ratio / FRAME_S) + 1
        if length >= t_frames:
            continue
        scaled = _onset_chroma(((r.start * ratio, r.pitch, 1.0) for r in ref), length)
        size = 1 << int(math.ceil(math.log2(t_frames + length)))
        corr = np.zeros(size)
        for pc in range(12):
            corr += np.fft.irfft(
                np.fft.rfft(target[:, pc], size) * np.conj(np.fft.rfft(scaled[:, pc], size)), size
            )
        offsets = np.arange(0, t_frames - length)
        # Raw overlap: dividing by the transcription's energy per window
        # would favour quiet stretches (the fade-out)
        score = corr[offsets] / (np.linalg.norm(scaled) * math.sqrt(energy[-1]) + 1e-9)
        k = int(np.argmax(score))
        if score[k] > best[0]:
            best = (float(score[k]), float(ratio), int(offsets[k]))
    score, ratio, offset = best
    for r in ref:
        r.mapped = offset * FRAME_S + r.start * ratio
    span = max(r.start for r in ref) * ratio
    return {"start": offset * FRAME_S, "end": offset * FRAME_S + span, "ratio": ratio, "score": score}


def match_reference(notes: list[Note], ref: list[RefNote]) -> dict[str, tuple[int, int]]:
    """Label transcribed notes with the part of the reference note they match.
    Two passes: coarse (exact pitch) to measure the local timing error, then
    fine, allowing octave errors."""
    candidates = sorted(notes, key=lambda n: n.start)
    starts = [n.start for n in candidates]

    def nearest(r: RefNote, at: float, tol: float, octave: bool):
        lo = bisect.bisect_left(starts, at - tol)
        hi = bisect.bisect_right(starts, at + tol)
        best = None
        for note in candidates[lo:hi]:
            exact = note.pitch == r.pitch
            if not exact and not (octave and (note.pitch - r.pitch) % 12 == 0 and abs(note.pitch - r.pitch) <= 24):
                continue
            score = abs(note.start - at) / tol + (0.0 if exact else 0.5)
            if best is None or score < best[0]:
                best = (score, note, exact)
        return best

    # Pass 1: local timing correction from confident exact matches
    offsets = []
    for r in ref:
        hit = nearest(r, r.mapped, 0.5, octave=False)
        if hit:
            offsets.append((r.mapped, hit[1].start - r.mapped))
    if offsets:
        offsets.sort()
        times = np.array([t for t, _ in offsets])
        values = np.array([o for _, o in offsets])
        k = 15
        smooth = np.array([np.median(values[max(0, i - k): i + k + 1]) for i in range(len(values))])
        for r in ref:
            r.mapped += float(np.interp(r.mapped, times, smooth))

    # Pass 2: one-to-one matching, best scores first
    proposals = []
    for r in ref:
        hit = nearest(r, r.mapped, 0.12, octave=True)
        if hit:
            proposals.append((hit[0], id(hit[1]), r, hit[1], hit[2]))
    proposals.sort(key=lambda p: (p[0], p[1]))
    taken_notes, taken_refs = set(), set()
    found: Counter = Counter()
    for score, key, r, note, exact in proposals:
        if key in taken_notes or id(r) in taken_refs:
            continue
        taken_notes.add(key)
        taken_refs.add(id(r))
        note.part = r.part
        note.source = "reference"
        note.confidence = round(max(0.3, 1.0 - 0.5 * score), 2)
        note.flag = ""  # a matched "ghost" was a real note
        found[r.part] += 1
    totals = Counter(r.part for r in ref)
    return {part: (found[part], totals[part]) for part in totals}


# --- Stage 5b: profiles, rules and smoothing ---------------------------------


def _features(n: Note) -> list[float]:
    """Profile features other than pitch (pitch has its own histogram)."""
    return [math.log(max(n.dur, 0.01)), n.velocity, n.poly, float(n.on_grid), float(n.lowest), float(n.highest)]


PITCH_SMOOTHING = 1.5  # semitones (Gaussian), for each part's pitch histogram


def _train_profiles(labelled: list[Note]) -> Optional[dict]:
    """Per part: a smoothed histogram of the pitches it plays (its range and
    favourite notes, which a single Gaussian can't describe: parts often
    play two registers) and Gaussians for duration, velocity and context."""
    by_part: dict[str, list[Note]] = defaultdict(list)
    for n in labelled:
        by_part[n.part].append(n)
    by_part = {p: v for p, v in by_part.items() if len(v) >= 20}
    if len(by_part) < 2:
        return None
    total = sum(len(v) for v in by_part.values())
    pitches = np.arange(128)
    model = {}
    for part, members in by_part.items():
        x = np.array([_features(n) for n in members])
        hist = np.zeros(128)
        # From the transcribed notes labelled from the reference, not the
        # reference's own notes: the profile has to describe how the part
        # appears in the transcription, octave errors included (the
        # reference's own pitches measured worse: 62% held-out against 71%)
        for n in members:
            hist += np.exp(-0.5 * ((pitches - n.pitch) / PITCH_SMOOTHING) ** 2)
        hist = (hist + 1e-3) / (hist.sum() + 0.128)  # a small floor: no pitch is impossible
        model[part] = {
            "mean": x.mean(axis=0),
            "var": x.var(axis=0) + 0.05,
            "prior": len(members) / total,
            "pitch": np.log(hist),
            "polyphony": _max_polyphony(members),
        }
    return model


def _max_polyphony(notes: list[Note], legato: float = 0.02) -> int:
    """Notes sounding at once (95th percentile over note starts), ignoring
    overlaps shorter than `legato` s."""
    ordered = sorted(notes, key=lambda n: n.start)
    counts = []
    for i, n in enumerate(ordered):
        counts.append(1 + sum(1 for m in ordered[max(0, i - 16) : i] if m.end - legato > n.start))
    return int(np.percentile(counts, 95)) if counts else 1


def _profile_scores(model: dict, n: Note) -> dict[str, float]:
    x = np.array(_features(n))
    scores = {}
    for part, m in model.items():
        gauss = -0.5 * float(np.sum(np.log(2 * np.pi * m["var"]) + (x - m["mean"]) ** 2 / m["var"]))
        scores[part] = math.log(m["prior"]) + m["pitch"][n.pitch] + gauss
    return scores


def _classify_profile(model: dict, n: Note) -> tuple[str, float]:
    logp = _profile_scores(model, n)
    best = max(logp, key=logp.get)
    top = logp[best]
    total = sum(math.exp(v - top) for v in logp.values())
    return best, 1.0 / total


def enforce_polyphony(notes: list[Note], model: dict, legato: float = 0.02) -> int:
    """Give each profile-labelled note a part that has room for it: a part
    the reference plays with at most k notes at once gets at most k. A note
    that would exceed that moves to its most likely part with room (by the
    profile), or stays if none has room. Reference labels are fixed."""
    moved = 0
    sounding: dict[str, list[Note]] = defaultdict(list)
    for n in sorted(notes, key=lambda n: (n.start, n.pitch)):
        for part in sounding:
            sounding[part] = [m for m in sounding[part] if m.end - legato > n.start]
        if n.source == "profile" and n.part in model:
            limit = lambda part: model[part]["polyphony"]
            if len(sounding[n.part]) >= limit(n.part):
                ranked = sorted(_profile_scores(model, n).items(), key=lambda kv: -kv[1])
                for part, _score in ranked:
                    if len(sounding[part]) < limit(part):
                        if part != n.part:
                            n.part = part
                            n.confidence = round(n.confidence * 0.8, 2)
                            moved += 1
                        break
        sounding[n.part].append(n)
    return moved


def rule_label(n: Note) -> tuple[str, float]:
    if n.pitch < 48 and n.lowest:
        return "Bass", 0.6
    if n.poly >= 3 and n.dur >= 0.3:
        return "Chords", 0.5
    if n.pitch >= 84 and n.dur < 0.25:
        return "High", 0.4
    if n.dur < 0.25 and n.on_grid:
        return "Sequence", 0.5
    if n.highest and n.dur >= 0.25:
        return "Lead", 0.45
    return "Chords", 0.3


def constraint_fit(note: Note, part: str) -> float:
    """How typical `note` is for `part`, from 0 to 1. A poor fit lowers
    confidence; it does not forbid the part. Electronic parts break the
    usual rules often enough that none of these are hard limits."""
    if part == "Bass":
        register = 1.0 if note.pitch < 52 else max(0.0, 1.0 - (note.pitch - 52) / 24)
        single = 1.0 if note.lowest else 0.35
        return 0.5 * register + 0.5 * single
    if part == "Sequence":
        short = 1.0 if note.dur < 0.3 else 0.35
        grid = 1.0 if note.on_grid else 0.55
        return 0.5 * short + 0.5 * grid
    if part == "Chords":
        held = 1.0 if note.dur >= 0.3 else 0.45
        thick = 1.0 if note.poly >= 3 else 0.55
        return 0.5 * held + 0.5 * thick
    if part == "Lead":
        top = 1.0 if note.highest else 0.45
        shaped = 1.0 if note.dur >= 0.2 else 0.5
        return 0.5 * top + 0.5 * shaped
    if part == "High":
        return 1.0 if note.pitch >= 84 and note.dur < 0.3 else 0.35
    return 1.0


def apply_part_constraints(notes: list[Note]) -> int:
    """Scale confidence by how well the note fits its part. A second low
    note within 20 ms of a bass note is a doubtful extra attack, not a
    second bass voice: it keeps its pitch, at a low confidence."""
    changed = 0
    ordered = sorted((n for n in notes if n.source in ("rule", "profile")), key=lambda n: (n.start, n.pitch))
    for note in ordered:
        fit = constraint_fit(note, note.part)
        if fit < 0.999:
            note.confidence = round(note.confidence * fit, 2)
            changed += 1
    for note in ordered:
        if note.pitch >= 60:
            continue
        partner = next(
            (
                other
                for other in ordered
                if other is not note
                and other.part == "Bass"
                and other.pitch < note.pitch
                and abs(other.start - note.start) <= 0.02
            ),
            None,
        )
        if partner is None:
            continue
        if note.part == "Bass":
            note.part = "Sequence" if note.dur < 0.25 else "Chords"
        note.confidence = round(min(note.confidence, 0.25), 2)
        changed += 1
    return changed


def label_remaining(
    notes: list[Note],
    sections: list[tuple[float, float]],
    use_profiles: bool = True,
    polyphony: bool = False,
) -> None:
    for s in range(len(sections)):
        in_section = [n for n in notes if n.section == s]
        labelled = [n for n in in_section if n.source == "reference"]
        model = _train_profiles(labelled) if use_profiles and len(labelled) >= 200 else None
        for n in in_section:
            if n.source:
                continue
            if n.flag == "ghost":
                n.part, n.confidence, n.source = GHOST, 0.5, "rule"
                continue
            if model:
                # In a section with learned profiles, a doubtful note still
                # gets the most likely of the real parts (a low confidence
                # says how sure): the generic rule parts never match the
                # reference's
                part, p = _classify_profile(model, n)
                n.part, n.confidence, n.source = part, round(p, 2), "profile"
                continue
            part, conf = rule_label(n)
            n.part, n.confidence, n.source = part, conf, "rule"
        if model and polyphony:
            enforce_polyphony(in_section, model)
    # Smooth inferred labels along each line
    by_line: dict[int, list[Note]] = defaultdict(list)
    for n in notes:
        if n.line >= 0 and n.source in ("profile", "rule"):
            by_line[n.line].append(n)
    for members in by_line.values():
        if len(members) < 4:
            continue
        part, count = Counter(n.part for n in members).most_common(1)[0]
        if count / len(members) >= 0.6:
            for n in members:
                n.part = part
    apply_part_constraints(notes)


def apply_corrections(notes: list[Note], path: Path) -> int:
    rules = json.loads(path.read_text())
    changed = 0
    for rule in rules:
        for n in notes:
            if (
                n.start >= rule.get("start", -math.inf)
                and n.start <= rule.get("end", math.inf)
                and rule.get("low", 0) <= n.pitch <= rule.get("high", 127)
                and (rule.get("from") in (None, n.part))
            ):
                n.part, n.confidence, n.source = rule["part"], 1.0, "manual"
                changed += 1
    return changed


# --- Pipeline ----------------------------------------------------------------


def classify(
    transcription: Path,
    reference: Optional[Path] = None,
    corrections: Optional[Path] = None,
    use_profiles: bool = True,
    alignment: Optional[tuple[float, float]] = None,
    polyphony: bool = False,
) -> Result:
    notes, merged = merge_fragments(load_transcription(transcription))
    mark_ghosts(notes)
    sections = find_sections(notes)
    for n in notes:
        n.section = next((k for k, (a, b) in enumerate(sections) if a <= n.start < b), len(sections) - 1)
    grids = [estimate_grid([n for n in notes if n.section == k]) for k in range(len(sections))]
    trace_lines(notes)
    add_context(notes, grids)
    result = Result(notes, sections, grids, merged)
    if reference:
        ref = load_reference(reference)
        if alignment:  # (offset s, tempo ratio): album time = offset + ratio x reference time
            offset, ratio = alignment
            for r in ref:
                r.mapped = offset + r.start * ratio
            span = (min(r.start for r in ref) * ratio + offset, max(r.start for r in ref) * ratio + offset)
            result.alignment = {"start": span[0], "end": span[1], "ratio": ratio, "score": float("nan")}
        else:
            result.alignment = align_reference(notes, ref)
        result.recall = match_reference(notes, ref)
    label_remaining(notes, sections, use_profiles, polyphony)
    if corrections:
        apply_corrections(notes, corrections)
    return result


# --- Stage 6: output ---------------------------------------------------------


def part_order(notes: list[Note]) -> list[str]:
    """Parts by median pitch, low to high; Ghost last."""
    pitches: dict[str, list[int]] = defaultdict(list)
    for n in notes:
        pitches[n.part].append(n.pitch)
    parts = sorted((p for p in pitches if p != GHOST), key=lambda p: float(np.median(pitches[p])))
    return parts + ([GHOST] if GHOST in pitches else [])


def write_midi(notes: list[Note], path: Path) -> list[tuple[str, int, int]]:
    """One named track per part, each on its own channel (10 skipped)."""
    tpb, tempo = 480, 500000  # 120 BPM: 960 ticks per second
    midi = mido.MidiFile(type=1, ticks_per_beat=tpb)
    midi.tracks.append(mido.MidiTrack([mido.MetaMessage("set_tempo", tempo=tempo)]))
    channels = [c for c in range(16) if c != DRUM_CHANNEL]
    layout = []
    for index, part in enumerate(part_order(notes)):
        channel = channels[index % len(channels)]
        events = []
        for n in notes:
            if n.part == part:
                events.append((round(n.start * 960), 1, n.pitch, n.velocity))
                events.append((round(n.end * 960), 0, n.pitch, 0))
        events.sort(key=lambda e: (e[0], e[1]))
        track = mido.MidiTrack([mido.MetaMessage("track_name", name=part)])
        last = 0
        for tick, on, pitch, velocity in events:
            kind = "note_on" if on else "note_off"
            track.append(mido.Message(kind, channel=channel, note=pitch, velocity=velocity, time=tick - last))
            last = tick
        midi.tracks.append(track)
        layout.append((part, len(midi.tracks) - 1, channel + 1))
    midi.save(path)
    return layout


def write_csv(notes: list[Note], path: Path) -> None:
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["start", "end", "pitch", "velocity", "part", "confidence", "source", "section", "line", "poly", "on_grid", "flag"])
        for n in sorted(notes, key=lambda n: (n.start, n.pitch)):
            w.writerow([f"{n.start:.3f}", f"{n.end:.3f}", n.pitch, n.velocity, n.part, n.confidence, n.source, n.section, n.line, n.poly, int(n.on_grid), n.flag])


def write_piano_roll(notes: list[Note], result: Result, path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    parts = part_order(notes)
    # tab20's strong colours, then its light ones; its greys are kept for Ghost
    colours = plt.get_cmap("tab20").colors
    palette = [colours[i] for i in list(range(0, 20, 2)) + list(range(1, 20, 2)) if i not in (14, 15)]
    end = max(n.end for n in notes)
    fig, ax = plt.subplots(figsize=(max(16, end / 12), 8), dpi=110)
    fig.patch.set_facecolor("#111111")
    ax.set_facecolor("#1b1b1b")
    for k, part in enumerate(parts):
        colour = "#555555" if part == GHOST else palette[k % len(palette)]
        bars = [(n.start, max(n.dur, 0.03)) for n in notes if n.part == part]
        pitches = [n.pitch for n in notes if n.part == part]
        for (x, w), p in zip(bars, pitches):
            ax.add_patch(plt.Rectangle((x, p - 0.4), w, 0.8, color=colour, linewidth=0))
        ax.plot([], [], color=colour, linewidth=6, label=f"{part} ({len(pitches)})")
    for a, _b in result.sections[1:]:
        ax.axvline(a, color="#ff4040", linewidth=1, linestyle="--")
    if result.alignment:
        ax.axvspan(result.alignment["start"], result.alignment["end"], color="#ffffff", alpha=0.04)
    pitches = [n.pitch for n in notes]
    ax.set_xlim(0, end)
    ax.set_ylim(min(pitches) - 2, max(pitches) + 2)
    ax.set_xlabel("time (s)", color="#cccccc")
    ax.set_ylabel("MIDI note", color="#cccccc")
    ax.tick_params(colors="#aaaaaa")
    ax.legend(loc="upper left", ncol=min(len(parts), 6), facecolor="#222222", labelcolor="#dddddd", fontsize=9)
    ax.set_title(f"{path.stem}: dashed = section boundaries, shaded = aligned reference", color="#dddddd")
    fig.tight_layout()
    fig.savefig(path, facecolor=fig.get_facecolor())
    plt.close(fig)


def mmss(seconds: float) -> str:
    seconds = round(seconds, 1)  # so 359.97 shows as 6:00.0, not 5:60.0
    return f"{int(seconds // 60)}:{seconds % 60:04.1f}"


def report(result: Result, layout: list[tuple[str, int, int]]) -> str:
    notes = result.notes
    lines = [f"notes: {len(notes)} (merged {result.merged} split notes)"]
    ghosts = sum(1 for n in notes if n.part == GHOST)
    lines.append(f"ghost (overtone) notes: {ghosts}")
    for k, (a, b) in enumerate(result.sections):
        grid = result.grids[k]
        g = f"grid {grid.period * 1000:.0f} ms = {grid.bpm:.0f} BPM (eighths)" if grid else "no grid"
        count = sum(1 for n in notes if n.section == k)
        lines.append(f"section {k}: {mmss(a)} - {mmss(b)}, {count} notes, {g}")
    if result.alignment:
        al = result.alignment
        lines.append(
            f"reference aligned to {mmss(al['start'])} - {mmss(al['end'])} (tempo ratio {al['ratio']:.3f}, fit {al['score']:.2f})"
        )
        lines.append("reference notes found in the transcription (recall):")
        for part, (found, total) in sorted(result.recall.items()):
            lines.append(f"  {part:<12} {found:5}/{total:<5} {100 * found / max(total, 1):5.1f}%")
    lines.append("parts written:")
    sources = Counter((n.part, n.source) for n in notes)
    for part, track, channel in layout:
        members = [n for n in notes if n.part == part]
        pitches = sorted(n.pitch for n in members)
        how = ", ".join(f"{s} {c}" for (p, s), c in sorted(sources.items()) if p == part)
        conf = np.mean([n.confidence for n in members])
        lines.append(
            f"  track {track:2} ch {channel:2} {part:<12} {len(members):5} notes, "
            f"MIDI {pitches[0]}-{pitches[-1]}, confidence {conf:.2f} ({how})"
        )
    return "\n".join(lines)


def run_classify(args) -> int:
    source = args.transcription.expanduser()
    result = classify(
        source,
        args.reference.expanduser() if args.reference else None,
        args.corrections.expanduser() if args.corrections else None,
        use_profiles=not args.rules_only,
        alignment=(args.ref_offset, args.ref_ratio) if args.ref_offset is not None else None,
        polyphony=args.polyphony,
    )
    out = (args.out_dir or source.parent).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    stem = source.stem
    layout = write_midi(result.notes, out / f"{stem} - parts.mid")
    write_csv(result.notes, out / f"{stem} - notes.csv")
    write_piano_roll(result.notes, result, out / f"{stem} - piano roll.png")
    text = report(result, layout)
    (out / f"{stem} - report.txt").write_text(text + "\n")
    print(text)
    print(f"\nwritten to {out}: '{stem} - parts.mid', '- notes.csv', '- piano roll.png', '- report.txt'")
    return 0


# --- Chords: rebuild a chord track from its harmony -------------------------

PITCH_NAMES = ("C", "C#", "D", "Eb", "E", "F", "F#", "G", "G#", "A", "Bb", "B")
_ROOTS = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
# Longer names are matched before shorter ones ("m7" before "m", "maj7" before "7").
CHORD_QUALITIES = {
    "": (0, 4, 7),
    "m": (0, 3, 7),
    "7": (0, 4, 7, 10),
    "maj7": (0, 4, 7, 11),
    "m7": (0, 3, 7, 10),
    "sus2": (0, 2, 7),
    "sus4": (0, 5, 7),
    "dim": (0, 3, 6),
    "aug": (0, 4, 8),
}
NO_CHORD = "N"
CHORD_HOP = 0.25  # seconds per chroma frame


@dataclass
class ChordSpan:
    start: float
    end: float
    name: str
    score: float  # mean template match, 0-1
    voicing: list[int] = field(default_factory=list)


def parse_chord(name: str) -> tuple[int, tuple[int, ...]]:
    """'C', 'Am', 'F#7', 'Bbmaj7', 'Dsus4' -> (root pitch class, intervals)."""
    name = name.strip()
    if not name or name[0].upper() not in _ROOTS:
        raise ValueError(f"not a chord: {name!r}")
    root, rest = _ROOTS[name[0].upper()], name[1:]
    if rest[:1] in ("#", "b"):
        root += 1 if rest[0] == "#" else -1
        rest = rest[1:]
    for quality in sorted(CHORD_QUALITIES, key=len, reverse=True):
        if rest == quality:
            return root % 12, CHORD_QUALITIES[quality]
    known = ", ".join(quality or "triad" for quality in sorted(CHORD_QUALITIES, key=len, reverse=True))
    raise ValueError(f"unknown chord quality in {name!r} (use {known})")


def chord_name(root: int, quality: str) -> str:
    return PITCH_NAMES[root % 12] + quality


def chord_vocabulary(names: Optional[Iterable[str]] = None) -> dict[str, tuple[int, set[int]]]:
    """name -> (root, pitch classes). By default every major, minor, 7th,
    maj7, m7, sus2, sus4, diminished and augmented chord."""
    if names is None:
        names = [chord_name(r, q) for q in CHORD_QUALITIES for r in range(12)]
    vocab = {}
    for name in names:
        root, intervals = parse_chord(name)
        vocab[name.strip()] = (root, {(root + i) % 12 for i in intervals})
    return vocab


def chroma_frames(rows, end: float, hop: float = CHORD_HOP) -> tuple[np.ndarray, np.ndarray]:
    """Pitch-class energy (sounding time x velocity) per frame, and the
    lowest pitch sounding in each frame (-1 if none)."""
    frames = int(math.ceil(end / hop)) + 1
    chroma = np.zeros((frames, 12))
    lowest = np.full(frames, 999)
    for s, e, p, v in rows:
        a, b = int(s / hop), min(int(math.ceil(e / hop)), frames)
        for k in range(a, b):
            overlap = min(e, (k + 1) * hop) - max(s, k * hop)
            if overlap > 0:
                chroma[k, p % 12] += overlap * v
                lowest[k] = min(lowest[k], p)
    lowest[lowest == 999] = -1
    return chroma, lowest


def load_wav_mono(path: Path) -> tuple[np.ndarray, int]:
    """A PCM WAV file as mono float samples in -1..1, and its sample rate."""
    import wave

    with wave.open(str(path), "rb") as w:
        channels, width, rate = w.getnchannels(), w.getsampwidth(), w.getframerate()
        raw = w.readframes(w.getnframes())
    if width == 1:
        data = (np.frombuffer(raw, np.uint8).astype(np.float32) - 128) / 128
    elif width == 2:
        data = np.frombuffer(raw, "<i2").astype(np.float32) / 32768
    elif width == 3:
        b = np.frombuffer(raw, np.uint8).reshape(-1, 3).astype(np.int32)
        ints = b[:, 0] | (b[:, 1] << 8) | (b[:, 2] << 16)
        data = (np.where(ints >= 1 << 23, ints - (1 << 24), ints)).astype(np.float32) / (1 << 23)
    elif width == 4:
        data = np.frombuffer(raw, "<i4").astype(np.float32) / (1 << 31)
    else:
        raise SystemExit(f"unsupported WAV sample width: {width * 8} bits")
    return data.reshape(-1, channels).mean(axis=1), rate


def have_librosa() -> bool:
    try:
        import librosa  # noqa: F401
    except Exception:
        return False
    return True


def audio_chroma(path: Path, hop: float = CHORD_HOP, method: str = "fft") -> tuple[np.ndarray, str]:
    """Chromagram of a recording (frames x 12, frame k covering
    [k * hop, (k + 1) * hop), as chroma_frames), and a description of how it
    was made. method: "fft" (NumPy only, about 1 s for ten minutes) or "cqt"
    (librosa: tuning correction and drum removal, about 40 s; on Oxygene V
    it matched the score no better than "fft")."""
    if method == "cqt":
        if not have_librosa():
            raise SystemExit("--audio-method cqt needs librosa: pip install librosa")
        return _cqt_chroma(path, hop)
    return _fft_chroma(path, hop), "FFT (NumPy)"


def _cqt_chroma(path: Path, hop: float, rate: int = 22050) -> tuple[np.ndarray, str]:
    """librosa: harmonic part only (median-filter HPSS, so drums and the
    rhythm box don't smear the chroma), tuning estimated from the recording
    (old analogue synths drift off A440), then a constant-Q chromagram (three
    bins per semitone, C1 to C8), averaged into hop-sized frames."""
    import librosa

    # Not librosa.load: its fallback backend can hang waiting for ffmpeg
    samples, native = load_wav_mono(path)
    y = librosa.resample(samples, orig_sr=native, target_sr=rate, res_type="soxr_hq") if native != rate else samples
    sr = rate
    harmonic = librosa.effects.harmonic(y, margin=2.0)
    tuning = float(librosa.estimate_tuning(y=harmonic, sr=sr))
    step = 512
    chroma = librosa.feature.chroma_cqt(
        y=harmonic, sr=sr, hop_length=step, tuning=tuning, bins_per_octave=36, n_octaves=7, fmin=librosa.note_to_hz("C1")
    ).T  # cqt frames x 12, frame j centred on j * step / sr
    times = np.arange(len(chroma)) * step / sr
    frames = int(len(y) / sr / hop)
    index = np.minimum((times / hop).astype(int), frames - 1)
    out = np.zeros((frames, 12))
    np.add.at(out, index, chroma)
    counts = np.bincount(index, minlength=frames)[:, None]
    out = out / np.maximum(counts, 1)
    # chroma_cqt scales each frame to max 1, so silence looks like a chord:
    # weight frames by their loudness and zero the near-silent ones
    rms = librosa.feature.rms(y=harmonic, frame_length=2048, hop_length=step)[0]
    loud = np.zeros(frames)
    np.add.at(loud, index[: len(rms)], rms[: len(index)])
    loud /= np.maximum(counts[:, 0], 1)
    out *= (loud > 0.01 * loud.max())[:, None]
    return out, f"constant-Q (librosa {librosa.__version__}, harmonic part, tuning {tuning * 100:+.0f} cents)"


def _fft_chroma(path: Path, hop: float = CHORD_HOP, low: int = 36, high: int = 96) -> np.ndarray:
    """Pitch classes of _fft_semitones."""
    return fold_chroma(_fft_semitones(path, hop, low=low, high=high), low)


def fold_chroma(semitones: np.ndarray, low: int) -> np.ndarray:
    """frames x semitones (from MIDI note `low`) -> frames x 12."""
    chroma = np.zeros((len(semitones), 12))
    for i in range(semitones.shape[1]):
        chroma[:, (low + i) % 12] += semitones[:, i]
    return chroma


def _fft_semitones(
    path: Path,
    hop: float = CHORD_HOP,
    window: float = 0.37,
    low: int = 36,
    high: int = 96,
) -> np.ndarray:
    """Hann-windowed FFT, magnitudes mapped onto semitones low..high,
    log-compressed, with the broadband floor (a moving average across an
    octave) removed: frames x (high - low + 1)."""
    samples, rate = load_wav_mono(path)
    n_fft = 1 << int(round(math.log2(window * rate)))
    freqs = np.fft.rfftfreq(n_fft, 1 / rate)
    with np.errstate(divide="ignore"):
        bin_pitch = 69 + 12 * np.log2(np.where(freqs > 0, freqs, 1e-9) / 440.0)
    pitches = np.arange(low, high + 1)
    weights = np.clip(1 - np.abs(bin_pitch[:, None] - pitches[None, :]), 0, None)  # bins x pitches
    used = weights.sum(axis=1) > 0
    weights = weights[used]
    frames = int(len(samples) / rate / hop)
    padded = np.concatenate([np.zeros(n_fft // 2, np.float32), samples, np.zeros(n_fft, np.float32)])
    taper = np.hanning(n_fft).astype(np.float32)
    salience = np.zeros((frames, len(pitches)))
    for a in range(0, frames, 128):
        idx = range(a, min(a + 128, frames))
        centres = [int(((k + 0.5) * hop) * rate) for k in idx]
        block = np.stack([padded[c : c + n_fft] * taper for c in centres])
        mags = np.abs(np.fft.rfft(block, axis=1))[:, used]
        salience[a : a + len(centres)] = mags @ weights
    peak = salience.max() or 1.0
    salience = np.log1p(1000 * salience / peak)
    kernel = np.ones(13) / 13
    floor = np.stack([np.convolve(row, kernel, mode="same") for row in salience])
    return np.clip(salience - floor, 0, None)


def _unit_rows(chroma: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(chroma, axis=1)
    return chroma / np.where(norms > 0, norms, 1)[:, None]


def audio_offset(notes_chroma: np.ndarray, audio: np.ndarray, max_lag: float = 10.0, hop: float = CHORD_HOP) -> int:
    """Frames to shift the audio chroma so it lines up with the notes (the
    lag with the best mean cosine; positive: the audio starts later)."""
    a, b = _unit_rows(notes_chroma), _unit_rows(audio)
    best, best_lag = -1.0, 0
    for lag in range(-int(max_lag / hop), int(max_lag / hop) + 1):
        x = a[max(0, -lag) :]
        y = b[max(0, lag) :]
        n = min(len(x), len(y))
        if n <= 0:
            continue
        value = float(np.mean(np.sum(x[:n] * y[:n], axis=1)))
        if value > best:
            best, best_lag = value, lag
    return best_lag


def blend_chroma(notes_chroma: np.ndarray, audio: np.ndarray, weight: float, lag: int = 0) -> np.ndarray:
    """Per-frame unit chroma: (1 - weight) x notes + weight x audio, the
    audio shifted by lag frames; frames with only one source use that one."""
    shifted = np.zeros_like(notes_chroma)
    src = audio[max(0, lag) :]
    dst = max(0, -lag)
    n = max(0, min(len(src), len(shifted) - dst))
    shifted[dst : dst + n] = src[:n]
    a, b = _unit_rows(notes_chroma), _unit_rows(shifted)
    has_a, has_b = a.any(axis=1), b.any(axis=1)
    out = (1 - weight) * a + weight * b
    out[has_a & ~has_b] = a[has_a & ~has_b]
    out[~has_a & has_b] = b[~has_a & has_b]
    return out


def detect_chords(
    chroma: np.ndarray,
    lowest: np.ndarray,
    vocab: dict[str, tuple[int, set[int]]],
    hop: float = CHORD_HOP,
    smooth: float = 1.0,
    change_cost: float = 4.0,
    min_chord: float = 1.0,
) -> list[ChordSpan]:
    """Chord per frame: template match of smoothed chroma, then Viterbi with
    a cost for every change, so chords hold until the harmony moves."""
    width = max(1, int(round(smooth / hop))) | 1  # odd: centred, no lag
    kernel = np.ones(width) / width
    smoothed = np.stack([np.convolve(chroma[:, c], kernel, mode="same") for c in range(12)], axis=1)
    norms = np.linalg.norm(smoothed, axis=1)
    names = list(vocab) + [NO_CHORD]
    templates = np.zeros((len(vocab), 12))
    for i, (root, pcs) in enumerate(vocab.values()):
        templates[i, list(pcs)] = 1.0
        templates[i] /= np.linalg.norm(templates[i])
    unit = smoothed / np.where(norms > 0, norms, 1)[:, None]
    match = unit @ templates.T  # cosine, frames x chords
    roots = np.array([root for root, _ in vocab.values()])
    bass_on_root = (lowest[:, None] >= 0) & ((lowest[:, None] % 12) == roots[None, :])
    sevenths = np.array([len(pcs) > 3 for _, pcs in vocab.values()])
    emit = match + 0.08 * bass_on_root - 0.03 * sevenths[None, :]
    silent = norms <= 1e-9
    no_chord = np.where(silent, 1.0, 0.25)[:, None]
    emit = np.where(silent[:, None], 0.0, emit)
    emit = np.hstack([emit, no_chord]) * 10.0  # log-likelihood scale

    frames, states = emit.shape
    score = emit[0].copy()
    back = np.zeros((frames, states), dtype=np.int32)
    for t in range(1, frames):
        best = int(np.argmax(score))
        switch = score[best] - change_cost
        stay = score
        back[t] = np.where(stay >= switch, np.arange(states), best)
        score = np.maximum(stay, switch) + emit[t]
    path = np.zeros(frames, dtype=np.int32)
    path[-1] = int(np.argmax(score))
    for t in range(frames - 1, 0, -1):
        path[t - 1] = back[t, path[t]]

    spans: list[ChordSpan] = []
    for t, state in enumerate(path):
        name = names[state]
        value = float(match[t, state]) if state < len(vocab) else 0.0
        if spans and spans[-1].name == name:
            spans[-1].end = (t + 1) * hop
            spans[-1].voicing.append(value)  # scores, averaged below
        else:
            spans.append(ChordSpan(t * hop, (t + 1) * hop, name, 0.0, [value]))
    for span in spans:
        span.score, span.voicing = float(np.mean(span.voicing)), []
    # Fold chords shorter than min_chord into the previous one
    merged: list[ChordSpan] = []
    for span in spans:
        if merged and (span.end - span.start < min_chord or span.name == merged[-1].name):
            merged[-1].end = span.end
        else:
            merged.append(span)
    if len(merged) > 1 and merged[0].end - merged[0].start < min_chord:
        merged[1].start = merged[0].start
        merged.pop(0)
    # Snap each change to the frame where the raw harmony changes most
    for left, right in zip(merged, merged[1:]):
        b = int(round(right.start / hop))
        best, best_k = -1.0, b
        for k in range(max(1, b - 2), min(len(chroma) - 1, b + 2) + 1):
            before = chroma[max(0, k - 4) : k].sum(axis=0)
            after = chroma[k : k + 4].sum(axis=0)
            nb, na = np.linalg.norm(before), np.linalg.norm(after)
            change = 1 - (before @ after) / (nb * na) if nb > 0 and na > 0 else 0.0
            if change > best + 1e-9:
                best, best_k = change, k
        left.end = right.start = best_k * hop
    return [s for s in merged if s.name != NO_CHORD]


def voice_chord(
    span: ChordSpan,
    pcs: set[int],
    root: int,
    target_rows,
    previous: list[int],
    voices: int = 4,
    low: int = 48,
    high: int = 84,
    fill: bool = True,
) -> list[int]:
    """Up to `voices` chord tones the track actually holds in the span
    (longest first). fill: complete the chord near the previous voicing and
    put the root at the bottom (root position); else only the held notes."""
    length = span.end - span.start
    held: dict[int, float] = defaultdict(float)
    for s, e, p, _v in target_rows:
        overlap = min(e, span.end) - max(s, span.start)
        if overlap > 0 and p % 12 in pcs and low <= p <= high:
            held[p] += overlap
    upper = [p for p, t in sorted(held.items(), key=lambda kv: -kv[1]) if t >= 0.2 * length][:voices]
    if not fill:
        return sorted(upper)
    centre = float(np.mean(previous[1:] or previous)) if previous else low + 14
    for pc in sorted(pcs, key=lambda c: (c - root) % 12):
        if len(upper) >= voices:
            break
        if not any(p % 12 == pc for p in upper):
            options = [p for p in range(low, high + 1) if p % 12 == pc and p not in upper]
            # Stay close to the previous voicing, so a chord change does not
            # leap every voice. The root is still placed at the bottom below.
            if previous:
                upper.append(min(options, key=lambda p: min(abs(p - prev) for prev in previous)))
            else:
                upper.append(min(options, key=lambda p: abs(p - centre)))
    # the root at the bottom: the lowest upper note if it is the root, else
    # the nearest root below it (down to low - 12)
    bass = max(p for p in range(low - 12, min(upper) + 1) if p % 12 == root)
    return sorted({bass, *upper})


def _ticks(seconds: float, tempo_map: list[tuple[int, int]], tpb: int) -> int:
    """Inverse of _seconds."""
    elapsed, last_tick, tempo = 0.0, 0, tempo_map[0][1]
    for change_tick, change_tempo in tempo_map[1:]:
        span = (change_tick - last_tick) * tempo / (tpb * 1e6)
        if elapsed + span > seconds:
            break
        elapsed += span
        last_tick, tempo = change_tick, change_tempo
    return last_tick + round((seconds - elapsed) * tpb * 1e6 / tempo)


@dataclass
class ChordResult:
    spans: list[ChordSpan]
    kept: list[tuple[float, float, int, int]]  # rebuilt chord notes
    extra: list[tuple[float, float, int, int]]  # target notes the held chords don't cover
    replaced: int  # target notes replaced by the held chords
    audio_offset: Optional[float] = None  # seconds the audio was shifted by
    audio_method: Optional[str] = None  # how the audio chroma was made
    held: int = 0  # notes of the rebuilt chords
    untouched: int = 0  # target notes left as they were (no chord there, or outside start..end)


def rebuild_chords(
    path: Path,
    target: str = "Chords",
    evidence: Optional[list[str]] = None,
    vocab_names: Optional[list[str]] = None,
    start: float = 0.0,
    end: Optional[float] = None,
    change_cost: float = 4.0,
    min_chord: float = 1.0,
    voices: int = 4,
    coverage: float = 0.3,
    fill: bool = True,
    keep_moving: bool = True,
    audio: Optional[Path] = None,
    audio_weight: float = 0.5,
    audio_method: str = "fft",
) -> ChordResult:
    rows = [r for r in _paired_notes(path) if r[4] != DRUM_CHANNEL]
    names = {r[5] for r in rows}
    if target not in names:
        raise SystemExit(f"no track named {target!r}; tracks: {', '.join(sorted(names))}")
    use = set(evidence) if evidence else names - {GHOST}
    finish = end if end is not None else max(r[1] for r in rows)
    clip = lambda rs: [(s, e, p, v) for s, e, p, v, _c, _n in rs if e > start and s < finish]
    harmony = clip([r for r in rows if r[5] in use])
    target_rows = clip([r for r in rows if r[5] == target])
    vocab = chord_vocabulary(vocab_names)
    chroma, lowest = chroma_frames(harmony, finish)
    lag, how = None, None
    if audio is not None:
        recorded, how = audio_chroma(audio, method=audio_method)
        lag = audio_offset(chroma, recorded)
        chroma = blend_chroma(chroma, recorded, audio_weight, lag)
    chroma[: int(start / CHORD_HOP)] = 0
    chroma[int(math.ceil(finish / CHORD_HOP)) :] = 0
    spans = detect_chords(chroma, lowest, vocab, change_cost=change_cost, min_chord=min_chord)
    for span in spans:  # smoothing can reach past the range: clip to it
        span.start, span.end = max(span.start, start), min(span.end, finish)
    spans = [x for x in spans if x.end - x.start >= min(min_chord, 0.5)]
    activity, _ = chroma_frames(target_rows, finish)
    active = activity.sum(axis=1) > 0

    kept, previous = [], []
    for span in spans:
        a, b = int(span.start / CHORD_HOP), max(int(span.start / CHORD_HOP) + 1, int(span.end / CHORD_HOP))
        if active[a:b].mean() < coverage:
            continue  # the track is silent here: leave it silent
        root, pcs = vocab[span.name]
        span.voicing = voice_chord(span, pcs, root, target_rows, previous, voices, fill=fill)
        if not span.voicing:
            continue  # nothing held long enough: leave the original notes
        velocities = [v for s, e, p, v in target_rows if s < span.end and e > span.start and p % 12 in pcs]
        velocity = int(np.median(velocities)) if velocities else 80
        for p in span.voicing:
            # an unchanged note is held over, as on the organ
            tied = next((i for i, n in enumerate(kept) if n[2] == p and abs(n[1] - span.start) < 1e-6), None)
            if tied is not None:
                kept[tied] = (kept[tied][0], span.end, p, kept[tied][3])
            else:
                kept.append((span.start, span.end, p, velocity))
        previous = span.voicing

    def chords_over(s: float, e: float):
        """What the rebuilt chords the note overlaps cover (None: none): their
        pitch classes, or with keep_moving only the pitches they hold."""
        over = [x for x in spans if x.voicing and x.start < e and x.end > s]
        if not over:
            return None
        if keep_moving:
            return {p for x in over for p in x.voicing}
        return set().union(*(vocab[x.name][1] for x in over))

    extra, replaced = [], 0
    for s, e, p, v in target_rows:
        covered = chords_over(s, e)
        if covered is not None and (p in covered if keep_moving else p % 12 in covered):
            replaced += 1
        elif covered is not None:
            extra.append((s, e, p, v))
        else:
            kept.append((s, e, p, v))  # outside any rebuilt chord: unchanged
    # The target's notes outside start..end are not touched
    outside = [(s, e, p, v) for s, e, p, v, _c, name in rows if name == target and (e <= start or s >= finish)]
    held = len(kept) - sum(1 for n in kept if n in set(target_rows))
    result = ChordResult(spans, sorted(kept + outside), sorted(extra), replaced, None if lag is None else lag * CHORD_HOP, how)
    result.held, result.untouched = held, len(kept) - held + len(outside)
    return result


def write_chord_midi(source: Path, out: Path, target: str, result: ChordResult) -> None:
    """The source file with the target track's notes replaced, and the notes
    outside the chords on a new track '<target> extra' (same channel)."""
    midi = mido.MidiFile(source)
    tempo_map, tpb = _tempo_map(midi), midi.ticks_per_beat
    index = next(
        i for i, t in enumerate(midi.tracks) if any(m.type == "track_name" and m.name.strip() == target for m in t)
    )
    track = midi.tracks[index]
    channel = next((m.channel for m in track if m.type in ("note_on", "note_off")), 0)

    def rebuild(meta_and_ctrl, notes, name=None):
        events, ticks = [], 0
        for msg in meta_and_ctrl:
            ticks += msg.time
            if msg.type in ("note_on", "note_off", "end_of_track"):
                continue
            if name and msg.type == "track_name":
                msg = msg.copy(name=name)
            events.append((ticks, 0, msg.copy(time=0)))
        for s, e, p, v in notes:
            events.append((_ticks(s, tempo_map, tpb), 2, mido.Message("note_on", channel=channel, note=p, velocity=v)))
            events.append((_ticks(e, tempo_map, tpb), 1, mido.Message("note_off", channel=channel, note=p, velocity=0)))
        events.sort(key=lambda x: (x[0], x[1]))
        new, last = mido.MidiTrack(), 0
        for tick, _order, msg in events:
            new.append(msg.copy(time=tick - last))
            last = tick
        return new

    midi.tracks[index] = rebuild(track, result.kept)
    if result.extra:
        extra_name = f"{target} extra"
        existing = next(
            (i for i, t in enumerate(midi.tracks) if any(m.type == "track_name" and m.name.strip() == extra_name for m in t)),
            None,
        )
        if existing is not None:  # a second pass over another range: add to it
            earlier = [(s, e, p, v) for s, e, p, v, _c, name in _paired_notes(source) if name == extra_name]
            midi.tracks[existing] = rebuild(midi.tracks[existing], sorted(earlier + result.extra))
        else:
            header = [m for m in track if m.is_meta and m.type == "track_name"] or [mido.MetaMessage("track_name", name=target)]
            midi.tracks.append(rebuild(header, result.extra, name=extra_name))
    midi.save(out)


def run_chords(args) -> int:
    source = args.midi.expanduser()
    vocab = [c for c in args.chords.split(",") if c.strip()] if args.chords else None
    evidence = [t.strip() for t in args.evidence.split(",")] if args.evidence else None
    result = rebuild_chords(
        source,
        args.track,
        evidence,
        vocab,
        args.start,
        args.end,
        args.change_cost,
        args.min_chord,
        args.voices,
        keep_moving=not args.drop_moving,
        audio=args.audio.expanduser() if args.audio else None,
        audio_weight=args.audio_weight,
        audio_method=args.audio_method,
    )
    if result.audio_offset is not None:
        print(f"audio chroma: {result.audio_method}")
        print(f"  blended at weight {args.audio_weight:.2f}, shifted {result.audio_offset:+.2f} s to match the notes")
    out = (args.out_dir or source.parent).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    midi_path = out / f"{source.stem} - chords.mid"
    write_chord_midi(source, midi_path, args.track, result)
    chart = out / f"{source.stem} - chord chart.csv"
    with chart.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["start", "end", "time", "chord", "match", "voicing"])
        for s in result.spans:
            voicing = " ".join(f"{PITCH_NAMES[p % 12]}{p // 12 - 1}" for p in s.voicing)
            w.writerow([f"{s.start:.2f}", f"{s.end:.2f}", mmss(s.start), s.name, f"{s.score:.2f}", voicing or "(track silent)"])
    line, lines = [], []
    for s in result.spans:
        line.append(s.name if s.voicing else f"({s.name})")
        if len(line) == 8:
            lines.append(line)
            line = []
    lines.append(line)
    key = detect_key(_note_rows(source, {GHOST}))
    print(f"key: {key.name} (fit {key.fit:.2f}; next {key.runner_up} {key.runner_up_fit:.2f})")
    print(f"{len(result.spans)} chords; first {mmss(result.spans[0].start) if result.spans else '-'}")
    t = iter(result.spans)
    for row in lines:
        if row:
            print(f"  {mmss(next(t).start):>7}  " + " ".join(f"{c:<5}" for c in row))
            for _ in range(len(row) - 1):
                next(t)
    print(
        f"{args.track}: {result.replaced} notes replaced by {result.held} held notes; "
        f"{len(result.extra)} other notes (melody, moving lines, stray notes) moved to '{args.track} extra'; "
        f"{result.untouched} left as they were"
    )
    print(f"written: {midi_path}\n         {chart}")
    return 0


# --- Quantize: a tempo map for the song, and notes on its grid ---------------

BEATS_PER_BAR = 4


@dataclass
class TempoPlan:
    beats: np.ndarray  # time (s) of every beat; beats[0] == 0; a bar every 4
    steady_start: float  # seconds: the steady (sequenced) section starts here
    step: float  # seconds per grid step in the steady section
    steps_per_beat: int
    coherence: float  # 0-1: how tightly the steady section's onsets sit on the grid
    opening: str  # how the bars before steady_start were placed

    @property
    def bpm(self) -> float:
        return 60.0 / (self.step * self.steps_per_beat)

    def position(self, seconds) -> np.ndarray:
        """Beat position (fractional) of times in seconds."""
        index = np.arange(len(self.beats), dtype=float)
        return np.interp(seconds, self.beats, index)


def grid_coherence(onsets: np.ndarray, weights: np.ndarray, period: float) -> tuple[float, float]:
    """(coherence 0-1, phase s): how tightly onsets cluster on a grid of
    `period`, as the length of the mean of unit phasors."""
    z = np.sum(weights * np.exp(2j * np.pi * onsets / period))
    return float(abs(z) / weights.sum()), float((np.angle(z) / (2 * np.pi)) % 1 * period)


def fit_steady_grid(onsets: np.ndarray, weights: np.ndarray, approx: float, spread: float = 0.08) -> tuple[float, float, float]:
    """(period, phase, coherence) of the constant grid that fits the onsets
    best, searched finely within approx x (1 +- spread)."""
    best = (0.0, approx)
    for resolution, width in ((2e-4, spread), (1e-5, 4e-4)):
        centre = best[1]
        for factor in np.arange(-width, width + resolution / 2, resolution):
            period = centre * (1 + factor)
            coherence, _ = grid_coherence(onsets, weights, period)
            if coherence > best[0]:
                best = (coherence, period)
    coherence, phase = grid_coherence(onsets, weights, best[1])
    return best[1], phase, coherence


def steady_region(onsets, weights, period, phase, window=16.0, hop=4.0, threshold=0.3) -> float:
    """Start of the longest run of windows whose onsets sit on the grid."""
    starts = np.arange(onsets.min(), onsets.max() - window / 2, hop)
    good = []
    for a in starts:
        sel = (onsets >= a) & (onsets < a + window)
        if sel.sum() < 8:
            good.append(False)
            continue
        z = np.sum(weights[sel] * np.exp(2j * np.pi * (onsets[sel] - phase) / period))
        good.append(abs(z) / weights[sel].sum() >= threshold)
    best_len, best_start, run = 0, None, 0
    for k, ok in enumerate(good):
        run = run + 1 if ok else 0
        if run > best_len:
            best_len, best_start = run, starts[k - run + 1]
    if best_start is None:
        raise SystemExit("no steady section found: give --steady-start and --bpm")
    # The first window can reach back into the free part: move the start to
    # the first onset from which a short window (4 s) is already on the grid
    for t in onsets[(onsets >= best_start) & (onsets < best_start + window)]:
        sel = (onsets >= t) & (onsets < t + 4.0)
        if sel.sum() >= 8:
            z = np.sum(weights[sel] * np.exp(2j * np.pi * (onsets[sel] - phase) / period))
            if abs(z) / weights[sel].sum() >= threshold:
                return float(t)
    return float(best_start)


def _bars_from_chart(chart: Path, until: float) -> tuple[list[float], float]:
    """Downbeats before `until` from a chord chart (each chord starts a bar;
    chords lasting n bars are split evenly), and the typical bar length."""
    rows = []
    with chart.open() as f:
        for row in csv.DictReader(f):
            rows.append((float(row["start"]), float(row["end"])))
    rows = [(a, min(b, until)) for a, b in sorted(rows) if a < until - 0.5]
    if not rows:
        return [], 0.0
    lengths = np.array([b - a for a, b in rows])
    short = lengths[lengths <= 1.5 * np.percentile(lengths, 25)]
    bar = float(np.median(short))
    downbeats = []
    for a, b in rows:
        n = max(1, int(round((b - a) / bar)))
        downbeats += list(a + (b - a) * np.arange(n) / n)
    return downbeats, bar


def _fill_bars(a: float, b: float, bar: float) -> list[float]:
    """Downbeats from a (inclusive) to b (exclusive): whole bars, evenly spaced."""
    n = max(1, int(round((b - a) / bar)))
    return list(a + (b - a) * np.arange(n) / n)


def plan_tempo(
    rows,
    end: float,
    chart: Optional[Path] = None,
    bpm: Optional[float] = None,
    steps_per_beat: int = 4,
    steady_start: Optional[float] = None,
    downbeat: Optional[float] = None,
) -> TempoPlan:
    """A beat for every moment of the song:
    - the steady section: a constant tempo fitted to the note onsets
      (sequencers keep perfect time), downbeats where the low notes fall;
    - before it (played freely): bars from the chord chart, if given, so the
      tempo follows the playing bar by bar; else the steady tempo, extended."""
    on = np.array([r[0] for r in rows])
    weights = np.array([r[3] * (1.5 if r[2] < 52 else 1.0) for r in rows], dtype=float)
    if bpm:
        approx, spread = 60.0 / bpm / steps_per_beat, 0.005
    else:
        guess = estimate_grid([Note(r[0], r[1], r[2], r[3]) for r in rows if r[0] >= (steady_start or 0)])
        if guess is None:
            raise SystemExit("could not estimate a tempo: give --bpm")
        approx, spread = guess.period, 0.08
    late = on >= (steady_start or 0)
    period, phase, _ = fit_steady_grid(on[late], weights[late], approx, spread)
    if steady_start is None:
        steady_start = steady_region(on, weights, period, phase)
        late = on >= steady_start
        period, phase, _ = fit_steady_grid(on[late], weights[late], period, 0.003)
    coherence, phase = grid_coherence(on[late], weights[late], period)
    # Beat phase: of the steps_per_beat grid offsets, the one with most weight;
    # bar phase: of the 4 beats, the one with most low-note weight
    beat = period * steps_per_beat
    rel = on[late] - phase
    step_index = np.round(rel / period).astype(int)
    near = np.abs(rel - step_index * period) < period / 4
    beat_offset = int(np.argmax([weights[late][near & (step_index % steps_per_beat == k)].sum() for k in range(steps_per_beat)]))
    beat_phase = phase + beat_offset * period
    if downbeat is not None:
        bar_phase = beat_phase + round((downbeat - beat_phase) / beat) * beat
    else:
        low = np.array([r[2] < 52 for r in rows])[late]
        beat_index = np.round((on[late] - beat_phase) / beat).astype(int)
        close = np.abs(on[late] - beat_phase - beat_index * beat) < beat / 8
        scores = [(weights[late] * low)[close & (beat_index % BEATS_PER_BAR == k)].sum() for k in range(BEATS_PER_BAR)]
        bar_phase = beat_phase + int(np.argmax(scores)) * beat
    bar = beat * BEATS_PER_BAR
    first_steady = bar_phase + math.ceil((steady_start - bar / 2 - bar_phase) / bar) * bar
    steady = list(np.arange(first_steady, end + 2 * bar, bar))

    opening_bars, opening_bar = ([], 0.0)
    if chart is not None:
        opening_bars, opening_bar = _bars_from_chart(chart, first_steady)
    if opening_bars:
        how = f"bars from {chart.name} (typical bar {opening_bar:.2f} s = {60 * BEATS_PER_BAR / opening_bar:.1f} BPM)"
        # the lead-in before the first chord gets bars of its own (a short
        # one at a faster tempo if need be), so every chord keeps its downbeat
        head = _fill_bars(0.0, opening_bars[0], opening_bar) if opening_bars[0] > 0.05 else []
        if not head:
            opening_bars[0] = 0.0
        tail = _fill_bars(opening_bars[-1], first_steady, opening_bar)[1:]
        downbeats = head + opening_bars + tail + steady
    else:
        how = "steady tempo extended back to the start"
        back = list(np.arange(first_steady - bar, 0, -bar))[::-1]
        if back and back[0] > bar / 2:
            back = _fill_bars(0.0, back[0], bar) + back
        elif back:
            back[0] = 0.0
        else:
            back = [0.0] if first_steady > 0 else []
        downbeats = back + steady
    beats = []
    for a, b in zip(downbeats, downbeats[1:]):
        beats += list(a + (b - a) * np.arange(BEATS_PER_BAR) / BEATS_PER_BAR)
    beats.append(downbeats[-1])
    return TempoPlan(np.array(beats), float(first_steady), period, steps_per_beat, coherence, how)


@dataclass
class QuantizeStats:
    moved: int
    total: int
    mean_shift_ms: float
    merged: int  # notes that landed on a same-pitch note and were joined


def quantize_midi(
    source: Path,
    out: Path,
    plan: TempoPlan,
    strength: float = 1.0,
    quantize_opening: bool = False,
    opening_steps: int = 2,
    triplet_bars: Optional[dict[int, int]] = None,
) -> QuantizeStats:
    """Rewrite `source` with plan's tempo map (4/4) so its bars match the
    music; snap notes in the steady section (and, with quantize_opening,
    before it) towards the grid by `strength`; everything else keeps its
    real time."""
    midi = mido.MidiFile(source)
    old_map, old_tpb = _tempo_map(midi), midi.ticks_per_beat
    tpb = 480
    result = mido.MidiFile(type=1, ticks_per_beat=tpb)
    seconds = lambda ticks: _seconds(ticks, old_map, old_tpb)
    tick_of = lambda pos: int(round(float(pos) * tpb))

    shifts, merged = [], 0
    for index, track in enumerate(midi.tracks):
        events, ticks = [], 0
        held: dict[tuple[int, int], list[tuple[float, int]]] = defaultdict(list)
        notes = []
        for msg in track:
            ticks += msg.time
            if msg.type in ("set_tempo", "time_signature", "end_of_track"):
                continue
            t = seconds(ticks)
            if msg.type == "note_on" and msg.velocity > 0:
                held[(msg.channel, msg.note)].append((t, msg.velocity))
            elif msg.type in ("note_on", "note_off"):
                if held[(msg.channel, msg.note)]:
                    start, velocity = held[(msg.channel, msg.note)].pop(0)
                    notes.append((start, t, msg.channel, msg.note, velocity))
            else:
                events.append((tick_of(plan.position(t)), 0, msg.copy(time=0)))
        if index == 0:
            events.append((0, 0, mido.MetaMessage("time_signature", numerator=BEATS_PER_BAR, denominator=4)))
            last = None
            for k in range(len(plan.beats) - 1):
                tempo = int(round((plan.beats[k + 1] - plan.beats[k]) * 1e6))
                if last is None or abs(tempo - last) > 1:
                    events.append((k * tpb, 0, mido.MetaMessage("set_tempo", tempo=tempo)))
                    last = tempo
        by_key: dict[tuple[int, int], list[list[int]]] = defaultdict(list)
        for start, end, channel, note, velocity in sorted(notes):
            a, b = plan.position(start), plan.position(end)
            if start >= plan.steady_start - plan.step / 2:
                grid = 1.0 / plan.steps_per_beat
                if triplet_bars and int(a // BEATS_PER_BAR) in triplet_bars:
                    grid = 1.0 / triplet_bars[int(a // BEATS_PER_BAR)]
            elif quantize_opening:
                grid = 1.0 / opening_steps
            else:
                grid = None
            if grid:
                qa = a + strength * (round(a / grid) * grid - a)
                qb = b + strength * (round(b / grid) * grid - b)
                if qb - qa < grid * strength:
                    qb = qa + max(grid * strength, b - a)
                shifts.append(abs(np.interp(qa, np.arange(len(plan.beats)), plan.beats) - start))
                a, b = qa, qb
            ta, tb = tick_of(a), max(tick_of(b), tick_of(a) + 1)
            same = by_key[(channel, note)]
            if same and same[-1][0] == ta:  # snapped onto the same onset: join
                same[-1][1] = max(same[-1][1], tb)
                merged += 1
                continue
            if same and same[-1][1] > ta:  # overlaps the next onset: shorten
                same[-1][1] = ta
            same.append([ta, tb, velocity])
        for (channel, note), items in by_key.items():
            for ta, tb, velocity in items:
                events.append((ta, 2, mido.Message("note_on", channel=channel, note=note, velocity=velocity)))
                events.append((tb, 1, mido.Message("note_off", channel=channel, note=note, velocity=0)))
        events.sort(key=lambda e: (e[0], e[1]))
        new, last_tick = mido.MidiTrack(), 0
        for tick, _order, msg in events:
            new.append(msg.copy(time=tick - last_tick))
            last_tick = tick
        result.tracks.append(new)
    result.save(out)
    shifts = np.array(shifts) if shifts else np.zeros(1)
    return QuantizeStats(int((shifts > 0.005).sum()), len(shifts), float(shifts.mean() * 1000), merged)


def run_quantize(args) -> int:
    source = args.midi.expanduser()
    rows = [r for r in _paired_notes(source) if r[4] != DRUM_CHANNEL and r[5] != GHOST]
    end = max(r[1] for r in rows)
    plan = plan_tempo(
        rows,
        end,
        args.bars.expanduser() if args.bars else None,
        args.bpm,
        args.steps_per_beat,
        args.steady_start,
        args.downbeat,
    )
    out = (args.out_dir or source.parent).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{source.stem} - quantized.mid"
    # Bars of the steady section in triplets (strictly: p < 0.001)
    index = np.arange(len(plan.beats), dtype=float)
    positions = np.interp([r[0] for r in rows], plan.beats, index)
    weights = np.array([r[3] for r in rows], dtype=float)
    first_bar = int(plan.position(plan.steady_start) // BEATS_PER_BAR)
    steady = positions >= first_bar * BEATS_PER_BAR
    found = {
        b.bar: b.division
        for b in bar_rhythms(positions[steady], weights[steady], plan.beats, alpha=0.001)
        if b.kind == "triplet" and b.bar >= first_bar
    }
    stats = quantize_midi(source, path, plan, args.strength, args.quantize_opening, found if args.triplets else None)
    bar_seconds = plan.step * plan.steps_per_beat * BEATS_PER_BAR
    print(
        f"steady section from {mmss(plan.steady_start)} (bar {int(plan.position(plan.steady_start)) // BEATS_PER_BAR + 1}): "
        f"{plan.bpm:.2f} BPM, grid 1/{plan.steps_per_beat * 4} = {plan.step * 1000:.1f} ms, "
        f"onsets on the grid: coherence {plan.coherence:.2f}"
    )
    print(f"before it: {plan.opening}")
    print(f"bars: {(len(plan.beats) - 1) // BEATS_PER_BAR}, 4/4; bar {bar_seconds:.2f} s in the steady section")
    scope = "steady section" + (" and opening" if args.quantize_opening else "")
    print(
        f"quantized ({scope}, strength {args.strength:.0%}): {stats.moved}/{stats.total} notes moved, "
        f"mean shift {stats.mean_shift_ms:.0f} ms; {stats.merged} doubled notes joined"
    )
    if found:
        bars_text = ", ".join(str(b + 1) for b in sorted(found))
        if args.triplets:
            print(f"triplet grid used in bars {bars_text}")
        else:
            print(f"bars {bars_text} look like triplets: --triplets snaps them to a triplet grid instead of 1/{plan.steps_per_beat * 4}")
    else:
        print("no triplet bars in the steady section")
    print(f"written: {path}")
    return 0


# --- Round trip: how much of the recording a MIDI file carries ----------------

ROUNDTRIP_LOW, ROUNDTRIP_HIGH = 36, 96  # C2..C7


def notes_semitones(rows, frames: int, hop: float = CHORD_HOP, low: int = ROUNDTRIP_LOW, high: int = ROUNDTRIP_HIGH) -> np.ndarray:
    """A piano roll of MIDI notes in the same frames as _fft_semitones
    (sounding time x velocity per frame and semitone), log-compressed."""
    roll = np.zeros((frames, high - low + 1))
    for s, e, p, v in rows:
        if not low <= p <= high:
            continue
        a, b = int(s / hop), min(int(math.ceil(e / hop)), frames)
        for k in range(a, b):
            overlap = min(e, (k + 1) * hop) - max(s, k * hop)
            if overlap > 0:
                roll[k, p - low] += overlap * v
    peak = roll.max() or 1.0
    return np.log1p(1000 * roll / peak)


def _shift(rows: np.ndarray, lag: int, length: int) -> np.ndarray:
    """rows[lag:] placed at 0 (lag < 0: delayed), padded/cut to length."""
    out = np.zeros((length, rows.shape[1]))
    src = rows[max(0, lag) :]
    dst = max(0, -lag)
    n = max(0, min(len(src), length - dst))
    out[dst : dst + n] = src[:n]
    return out


@dataclass
class RoundTrip:
    lag: float  # seconds the recording was shifted by to line up
    chroma: float  # mean cosine of pitch-class frames, 0-1 (octave-blind)
    chroma_r: float  # Pearson r of the aligned pitch-class matrices
    pitch: float  # mean cosine of semitone frames, 0-1 (counts octave errors)
    coverage: float  # share of the recording's sounding frames the MIDI covers
    windows: list  # (start s, chroma cosine, Pearson r) per window


def roundtrip_scores(
    recording: np.ndarray,
    midi: np.ndarray,
    hop: float = CHORD_HOP,
    window: float = 30.0,
    start: float = 0.0,
    end: Optional[float] = None,
    max_lag: float = 10.0,
) -> RoundTrip:
    """Compare two semitone matrices (frames x semitones from
    ROUNDTRIP_LOW): the recording's and the MIDI's (its notes or a render)."""
    rec_chroma = fold_chroma(recording, ROUNDTRIP_LOW)
    midi_chroma = fold_chroma(midi, ROUNDTRIP_LOW)
    lag = audio_offset(midi_chroma, rec_chroma, max_lag=max_lag, hop=hop)
    length = len(midi)
    rec = _shift(recording, lag, length)
    rec_c = _shift(rec_chroma, lag, length)
    a, b = int(start / hop), int((end if end is not None else length * hop) / hop)
    rec, rec_c, mid, mid_c = rec[a:b], rec_c[a:b], midi[a:b], midi_chroma[a:b]
    sounding = np.linalg.norm(rec_c, axis=1) > 0
    both = sounding & (np.linalg.norm(mid_c, axis=1) > 0)
    cos = lambda x, y: np.sum(_unit_rows(x) * _unit_rows(y), axis=1)
    chroma_cos = cos(rec_c, mid_c)
    pitch_cos = cos(rec, mid)
    r = float(np.corrcoef(rec_c[both].ravel(), mid_c[both].ravel())[0, 1]) if both.sum() > 1 else 0.0
    per = max(1, int(window / hop))
    windows = []
    for k in range(0, len(both), per):
        block = slice(k, k + per)
        sel = both[block]
        if sel.sum() < per // 4:
            continue
        x = rec_c[block][sel].ravel()
        y = mid_c[block][sel].ravel()
        pearson = float(np.corrcoef(x, y)[0, 1]) if x.size > 1 and np.std(x) > 0 and np.std(y) > 0 else 0.0
        windows.append(((a + k) * hop, float(chroma_cos[block][sel].mean()), pearson))
    return RoundTrip(
        lag * hop,
        float(chroma_cos[both].mean()) if both.any() else 0.0,
        r,
        float(pitch_cos[both].mean()) if both.any() else 0.0,
        float(both.sum() / max(sounding.sum(), 1)),
        windows,
    )


def _render_copy(source: Path, out: Path, exclude: set[str], program: int) -> None:
    """source without the excluded tracks or drums, every channel set to
    one sustained General MIDI program (JD-Xi program numbers mean other
    instruments in General MIDI), for rendering."""
    midi = mido.MidiFile(source)
    keep = []
    channels = set()
    for track in midi.tracks:
        name = next((m.name.strip() for m in track if m.type == "track_name"), "")
        if name in exclude:
            continue
        new = mido.MidiTrack()
        carry = 0
        for msg in track:
            drop = msg.type == "program_change" or (msg.type == "control_change" and msg.control in (0, 32))
            drop = drop or (not msg.is_meta and getattr(msg, "channel", None) == DRUM_CHANNEL)
            if drop:
                carry += msg.time
                continue
            if not msg.is_meta and hasattr(msg, "channel"):
                channels.add(msg.channel)
            new.append(msg.copy(time=msg.time + carry))
            carry = 0
        keep.append(new)
    setup = mido.MidiTrack([mido.Message("program_change", channel=c, program=program) for c in sorted(channels)])
    midi.tracks = [setup] + keep
    midi.save(out)


def write_correlation_histogram(windows: list, path: Path, title: str, overall_r: float) -> None:
    """Bars of the Pearson chroma correlation in each time window."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    starts = np.array([w[0] for w in windows])
    values = np.array([w[2] for w in windows])
    width = (starts[1] - starts[0]) if len(starts) > 1 else 30.0
    fig, ax = plt.subplots(figsize=(max(12, starts[-1] / 40), 4.8), dpi=120)
    fig.patch.set_facecolor("#111111")
    ax.set_facecolor("#1b1b1b")
    colours = plt.get_cmap("RdYlGn")(np.clip((values + 1) / 2, 0, 1))
    ax.bar(starts / 60, values, width=width / 60 * 0.92, align="edge", color=colours, linewidth=0)
    ax.axhline(overall_r, color="#8ecae6", linewidth=1, linestyle="--", label=f"whole song r = {overall_r:.3f}")
    ax.set_ylim(-0.05, 1.05)
    ax.set_xlim(0, (starts[-1] + width) / 60)
    ax.set_xlabel("song position (minutes)", color="#cccccc")
    ax.set_ylabel("correlation coefficient", color="#cccccc")
    ax.set_title(title, color="#dddddd")
    ax.tick_params(colors="#aaaaaa")
    for spine in ax.spines.values():
        spine.set_color("#444444")
    ax.legend(loc="lower right", facecolor="#222222", labelcolor="#dddddd", fontsize=9)
    fig.tight_layout()
    fig.savefig(path, facecolor=fig.get_facecolor())
    plt.close(fig)


def run_roundtrip(args) -> int:
    import tempfile

    wav = args.wav.expanduser()
    recording = _fft_semitones(wav, low=ROUNDTRIP_LOW, high=ROUNDTRIP_HIGH)
    exclude = {t.strip() for t in args.exclude.split(",") if t.strip()}
    how = f"rendered with FluidSynth (GM program {args.program})" if args.render else "its notes directly"
    print(f"recording: {wav.name}; each MIDI file compared through {how}; excluded tracks: {', '.join(sorted(exclude)) or 'none'}")
    print(f"{'MIDI file':<52} {'lag s':>6} {'chroma':>7} {'r':>6} {'pitch':>6} {'cover':>6}  weakest {args.window:.0f} s windows")
    for path in args.midi:
        path = path.expanduser()
        if args.render:
            with tempfile.TemporaryDirectory() as tmp:
                copy, rendered = Path(tmp) / "copy.mid", Path(tmp) / "render.wav"
                _render_copy(path, copy, exclude, args.program)
                cmd = ["fluidsynth", "-ni", "-g", "0.6", "-r", "44100", "-F", str(rendered), str(args.soundfont.expanduser()), str(copy)]
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                midi_semi = _fft_semitones(rendered, low=ROUNDTRIP_LOW, high=ROUNDTRIP_HIGH)
        else:
            rows = [(s, e, p, v) for s, e, p, v, ch, name in _paired_notes(path) if ch != DRUM_CHANNEL and name not in exclude]
            midi_semi = notes_semitones(rows, len(recording))
        n = min(len(recording), len(midi_semi)) if args.render else len(recording)
        result = roundtrip_scores(recording[:n] if args.render else recording, midi_semi[:n], window=args.window, start=args.start, end=args.end, max_lag=args.max_lag)
        weakest = sorted(result.windows, key=lambda w: w[1])[:3]
        weak = ", ".join(f"{mmss(t)[:-2]} {v:.2f}" for t, v, _r in sorted(weakest))
        name = path.name if len(path.name) <= 52 else path.name[:49] + "..."
        print(f"{name:<52} {result.lag:+6.2f} {result.chroma:7.3f} {result.chroma_r:6.3f} {result.pitch:6.3f} {result.coverage:6.2f}  {weak}")
        if args.plot and result.windows:
            plot = args.plot.expanduser()
            if len(args.midi) > 1:
                plot.mkdir(parents=True, exist_ok=True)
                plot = plot / f"{path.stem} - correlation.png"
            else:
                plot.parent.mkdir(parents=True, exist_ok=True)
            write_correlation_histogram(
                result.windows,
                plot,
                f"{path.stem}: Pearson correlation by song position",
                result.chroma_r,
            )
            print(f"  histogram: {plot}")
    print("chroma: mean cosine of pitch-class frames (harmony and timing; deaf to octave errors); r: Pearson of the same;")
    print("pitch: mean cosine per semitone C2-C7 (counts octave errors); cover: share of the recording's sounding frames the MIDI covers")
    print("lag: seconds the recording was shifted to line up (negative: the recording is earlier than the MIDI)")
    return 0


# --- Key: detection, and an optional filter -------------------------------------

# Krumhansl-Kessler key profiles (probe-tone ratings), from the tonic
KEY_PROFILES = {
    "": np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]),
    "m": np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]),
}
SCALES = {"": (0, 2, 4, 5, 7, 9, 11), "m": (0, 2, 3, 5, 7, 8, 10)}  # major, natural minor


@dataclass
class Key:
    name: str  # e.g. "C", "Am"
    root: int
    mode: str  # "" major, "m" minor
    fit: float  # correlation with the key profile, -1..1
    runner_up: str
    runner_up_fit: float

    def scale(self, harmonic: bool = False) -> set[int]:
        pcs = {(self.root + i) % 12 for i in SCALES[self.mode]}
        if harmonic and self.mode == "m":
            pcs |= {(self.root + 9) % 12, (self.root + 11) % 12}  # raised 6th and 7th
        return pcs


def pitch_class_profile(rows) -> np.ndarray:
    """Sounding time x velocity per pitch class."""
    profile = np.zeros(12)
    for s, e, p, v in rows:
        profile[p % 12] += (e - s) * v
    return profile


def detect_key(rows) -> Key:
    """The major or minor key whose Krumhansl-Kessler profile correlates best
    with the notes' pitch-class profile (duration x velocity)."""
    profile = pitch_class_profile(rows)
    if not profile.any():
        raise ValueError("no notes")
    fits = sorted(
        ((float(np.corrcoef(profile, np.roll(KEY_PROFILES[mode], root))[0, 1]), root, mode) for root in range(12) for mode in KEY_PROFILES),
        reverse=True,
    )
    (fit, root, mode), (fit2, root2, mode2) = fits[0], fits[1]
    return Key(chord_name(root, mode), root, mode, fit, chord_name(root2, mode2), fit2)


def parse_key(name: str) -> Key:
    root, intervals = parse_chord(name)
    mode = "m" if intervals == CHORD_QUALITIES["m"] else ""
    if intervals not in (CHORD_QUALITIES[""], CHORD_QUALITIES["m"]):
        raise ValueError(f"a key is major or minor, e.g. 'C' or 'Am': {name!r}")
    return Key(chord_name(root, mode), root, mode, float("nan"), "", float("nan"))


def _parse_pitch_classes(text: str) -> set[int]:
    return {parse_chord(name.strip())[0] for name in text.split(",") if name.strip()}


def _note_rows(path: Path, exclude: set[str]):
    return [(s, e, p, v) for s, e, p, v, ch, name in _paired_notes(path) if ch != DRUM_CHANNEL and name not in exclude]


def run_key(args) -> int:
    path = args.midi.expanduser()
    exclude = {t.strip() for t in args.exclude.split(",") if t.strip()}
    rows = _note_rows(path, exclude)
    key = detect_key(rows)
    print(f"{path.name}: {key.name} (fit {key.fit:.2f}; next {key.runner_up} {key.runner_up_fit:.2f})")
    sections = find_sections([Note(s, e, p, v) for s, e, p, v in rows])
    if len(sections) > 1:
        for a, b in sections:
            part = [r for r in rows if a <= r[0] < b]
            if part:
                k = detect_key(part)
                print(f"  {mmss(a)} - {mmss(b)}: {k.name} (fit {k.fit:.2f}; next {k.runner_up} {k.runner_up_fit:.2f})")
    profile = pitch_class_profile(rows)
    share = profile / profile.sum()
    scale = key.scale()
    outside = sum(share[pc] for pc in range(12) if pc not in scale)
    print("pitch classes: " + " ".join(f"{PITCH_NAMES[pc]} {100 * share[pc]:.0f}%" for pc in range(12)))
    print(f"outside {key.name} {'minor' if key.mode else 'major'}: {100 * outside:.0f}% of the sounding time")
    return 0


def _chord_at(chart_rows, t: float) -> Optional[set[int]]:
    for a, b, pcs in chart_rows:
        if a <= t < b:
            return pcs
    return None


def _read_chart(chart: Path) -> list[tuple[float, float, set[int]]]:
    rows = []
    with chart.open() as f:
        for row in csv.DictReader(f):
            root, intervals = parse_chord(row["chord"])
            rows.append((float(row["start"]), float(row["end"]), {(root + i) % 12 for i in intervals}))
    return rows


def run_filter_key(args) -> int:
    """Remove (or set aside) notes outside the key. Off by default in every
    other command: check with 'roundtrip' that it helps before using it."""
    source = args.midi.expanduser()
    exclude = {t.strip() for t in args.exclude.split(",") if t.strip()}
    if args.key in (None, "auto"):
        key = detect_key(_note_rows(source, exclude))
        how = f"detected (fit {key.fit:.2f}; next {key.runner_up} {key.runner_up_fit:.2f})"
    else:
        key, how = parse_key(args.key), "given"
    allow = _parse_pitch_classes(args.allow) if args.allow else set()
    chart = _read_chart(args.chords.expanduser()) if args.chords else None

    midi = mido.MidiFile(source)
    tempo_map, tpb = _tempo_map(midi), midi.ticks_per_beat
    allowed = key.scale(args.harmonic) | allow
    removed_total, total, set_aside = 0, 0, []
    for index, track in enumerate(midi.tracks):
        name = next((m.name.strip() for m in track if m.type == "track_name"), "")
        if name in exclude:
            continue
        ticks, held, drop = 0, defaultdict(list), set()
        absolute = []
        for position, msg in enumerate(track):
            ticks += msg.time
            absolute.append(ticks)
            if msg.type not in ("note_on", "note_off") or msg.channel == DRUM_CHANNEL:
                continue
            key_ = (msg.channel, msg.note)
            if msg.type == "note_on" and msg.velocity > 0:
                held[key_].append((position, ticks))
            elif held[key_]:
                on_position, on_ticks = held[key_].pop(0)
                total += 1
                pc = msg.note % 12
                if pc in allowed:
                    continue
                if chart:
                    middle = _seconds((on_ticks + ticks) // 2, tempo_map, tpb)
                    pcs = _chord_at(chart, middle)
                    if pcs is not None and pc in pcs:
                        continue
                drop |= {on_position, position}
                set_aside.append((on_ticks, ticks, msg.channel, msg.note, track[on_position].velocity))
        if not drop:
            continue
        removed_total += len(drop) // 2
        kept, last = mido.MidiTrack(), 0
        for position, msg in enumerate(track):
            if position in drop:
                continue
            kept.append(msg.copy(time=absolute[position] - last))
            last = absolute[position]
        midi.tracks[index] = kept
    if args.keep_separate and set_aside:
        events = []
        for a, b, ch, note, vel in set_aside:
            events.append((a, 1, mido.Message("note_on", channel=ch, note=note, velocity=vel)))
            events.append((b, 0, mido.Message("note_off", channel=ch, note=note, velocity=0)))
        events.sort(key=lambda e: (e[0], e[1]))
        track, last = mido.MidiTrack([mido.MetaMessage("track_name", name="Out of key")]), 0
        for tick, _o, msg in events:
            track.append(msg.copy(time=tick - last))
            last = tick
        midi.tracks.append(track)
    out = (args.out_dir or source.parent).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{source.stem} - in {key.name}.mid"
    midi.save(path)
    scale = " ".join(PITCH_NAMES[pc] for pc in sorted(allowed, key=lambda pc: (pc - key.root) % 12))
    print(f"key {key.name}, {how}; allowed: {scale}" + (" + the notes of the chord playing (chart)" if chart else ""))
    where = "moved to an 'Out of key' track" if args.keep_separate else "removed"
    print(f"{removed_total} of {total} notes outside it {where}")
    print(f"written: {path}")
    print("check the result with 'roundtrip' against the recording before using it")
    return 0


# --- Patterns: repair a repeated (sequenced) section from its repetitions ------

REVIEW_CHANNEL = 15  # MIDI channel 16: not a JD-Xi part, so review notes stay silent


@dataclass
class GridNote:
    track: int
    start: int  # ticks
    end: int
    pitch: int
    velocity: int
    channel: int


def _grid_notes(midi: mido.MidiFile, exclude: set[str]) -> list[GridNote]:
    notes = []
    for index, track in enumerate(midi.tracks):
        name = next((m.name.strip() for m in track if m.type == "track_name"), "")
        if name in exclude:
            continue
        now, held = 0, defaultdict(list)
        for msg in track:
            now += msg.time
            if msg.type not in ("note_on", "note_off") or msg.channel == DRUM_CHANNEL:
                continue
            if msg.type == "note_on" and msg.velocity > 0:
                held[(msg.channel, msg.note)].append((now, msg.velocity))
            elif held[(msg.channel, msg.note)]:
                start, velocity = held[(msg.channel, msg.note)].pop(0)
                notes.append(GridNote(index, start, now, msg.note, velocity, msg.channel))
    return notes


def steady_start_tick(midi: mido.MidiFile) -> int:
    """Tick of the last tempo change (from 'quantize': where the steady
    section starts), rounded down to a bar."""
    last, now = 0, 0
    for track in midi.tracks:
        now = 0
        for msg in track:
            now += msg.time
            if msg.type == "set_tempo":
                last = max(last, now)
    bar = BEATS_PER_BAR * midi.ticks_per_beat
    return last // bar * bar


def _bar_similarity(a: set, b: set, tolerance: int = 1, steps: int = 16) -> tuple[float, int]:
    """(similarity 0-1, transposition) of two bars' (step, pitch) cells:
    shared cells over all cells, with steps matching within +-tolerance, at
    the transposition (-12..12, smallest on ties) that shares most."""
    best = (0.0, 0)
    for shift in range(-12, 13):
        moved = {(st, p + shift) for st, p in b}
        hit = sum(1 for st, p in a if any(((st + d) % steps, p) in moved for d in range(-tolerance, tolerance + 1)))
        union = len(a) + len(moved) - hit
        value = hit / union if union else 0.0
        if value > best[0] + 1e-9 or (abs(value - best[0]) < 1e-9 and abs(shift) < abs(best[1])):
            best = (value, shift)
    return best


@dataclass
class PatternChange:
    action: str  # add, move, octave, review
    track: int
    tick: int
    pitch: int
    support: float  # share of the similar repetitions that agree
    new_pitch: Optional[int] = None


def repair_patterns(
    notes: list[GridNote],
    start: int,
    bar: int,
    step: int,
    window: int = 8,
    similarity: float = 0.3,
    neighbours: int = 8,
    min_neighbours: int = 3,
    add: Optional[float] = 0.5,
    move: Optional[float] = None,
    octave: Optional[float] = None,
    review: Optional[float] = None,
    keep: float = 0.25,
) -> tuple[list[GridNote], list[GridNote], list[PatternChange]]:
    """Repair each bar from start on with the bars that repeat it.

    For every bar, the most similar bars within +-window (similarity >=
    `similarity`, transposition allowed, up to `neighbours`) vote on each
    (step, pitch) cell. With at least min_neighbours of them:
    - add: a cell at least this share of them have, missing here, is added
      (length, velocity and track from the notes that voted for it);
    - move: a note almost none of them have (< keep) moves one step to a
      cell this share have;
    - octave: likewise an octave up or down;
    - review: a note this share or fewer have goes to the review list.
    Returns (notes, review notes, changes)."""
    steps = bar // step
    cells: dict[int, dict[tuple[int, int], int]] = defaultdict(dict)
    for i, n in enumerate(notes):
        if n.start >= start:
            offset = n.start - start
            cells[offset // bar][(round((offset % bar) / step) % steps, n.pitch)] = i
    out = [GridNote(**n.__dict__) for n in notes]
    reviewed: set[int] = set()
    added: list[GridNote] = []
    changes: list[PatternChange] = []
    bars = sorted(cells)
    for u in bars:
        here = set(cells[u])
        if len(here) < 2:
            continue
        candidates = []
        for v in bars:
            if v != u and abs(v - u) <= window:
                value, shift = _bar_similarity(here, set(cells[v]), steps=steps)
                if value >= similarity:
                    candidates.append((value, v, shift))
        candidates = sorted(candidates, reverse=True)[:neighbours]
        if len(candidates) < min_neighbours:
            continue
        count = len(candidates)
        votes: Counter = Counter()
        voters: dict[tuple[int, int], list[int]] = defaultdict(list)
        for _value, v, shift in candidates:
            for (st, p), i in cells[v].items():
                votes[(st, p + shift)] += 1
                voters[(st, p + shift)].append(i)
        share = lambda cell: votes[cell] / count
        taken = set()
        for (st, p), i in cells[u].items():
            if share((st, p)) >= keep:
                taken.add((st, p))
                continue
            target = None
            options = []
            if move is not None:
                options += [(((st + d) % steps, p), "move") for d in (-1, 1)]
            if octave is not None:
                options += [((st, p + d), "octave") for d in (-12, 12)]
            for cell, kind in options:
                limit = move if kind == "move" else octave
                if share(cell) >= limit and cell not in cells[u] and (target is None or share(cell) > share(target[0])):
                    target = (cell, kind)
            if target:
                (st2, p2), kind = target
                d = st2 - st
                d = d - steps if d > steps // 2 else d + steps if d < -steps // 2 else d
                n = out[i]
                changes.append(PatternChange(kind, n.track, n.start, n.pitch, share((st2, p2)), p2))
                n.start, n.end, n.pitch = n.start + d * step, n.end + d * step, p2
                taken.add((st2, p2))
                continue
            if review is not None and share((st, p)) <= review:
                reviewed.add(i)
                changes.append(PatternChange("review", notes[i].track, notes[i].start, notes[i].pitch, share((st, p))))
        if add is not None:
            for cell, n_votes in votes.items():
                if n_votes / count >= add and cell not in cells[u] and cell not in taken:
                    st, p = cell
                    sources = [notes[i] for i in voters[cell]]
                    length = int(np.median([x.end - x.start for x in sources]))
                    velocity = int(np.median([x.velocity for x in sources]))
                    track, channel = Counter((x.track, x.channel) for x in sources).most_common(1)[0][0]
                    tick = start + u * bar + st * step
                    added.append(GridNote(track, tick, tick + max(length, 1), p, velocity, channel))
                    changes.append(PatternChange("add", track, tick, p, n_votes / count))
    kept = [n for i, n in enumerate(out) if i not in reviewed]
    return kept + added, [notes[i] for i in sorted(reviewed)], changes


def write_pattern_midi(source: Path, out: Path, notes: list[GridNote], review: list[GridNote], exclude: set[str]) -> None:
    """source with the notes of every repaired track replaced, and the
    review notes on a 'Pattern review' track on channel 16 (silent on the JD-Xi)."""
    midi = mido.MidiFile(source)
    by_track = defaultdict(list)
    for n in notes:
        by_track[n.track].append(n)

    def build(messages, items, channel=None):
        events, now = [], 0
        for msg in messages:
            now += msg.time
            if msg.type in ("note_on", "note_off", "end_of_track"):
                continue
            events.append((now, 0, msg.copy(time=0)))
        for n in items:
            ch = n.channel if channel is None else channel
            events.append((n.start, 2, mido.Message("note_on", channel=ch, note=n.pitch, velocity=n.velocity)))
            events.append((n.end, 1, mido.Message("note_off", channel=ch, note=n.pitch, velocity=0)))
        events.sort(key=lambda e: (e[0], e[1]))
        track, last = mido.MidiTrack(), 0
        for at, _order, msg in events:
            track.append(msg.copy(time=at - last))
            last = at
        return track

    for index, track in enumerate(midi.tracks):
        name = next((m.name.strip() for m in track if m.type == "track_name"), "")
        drums = [m for m in track if m.type in ("note_on", "note_off") and m.channel == DRUM_CHANNEL]
        if name in exclude or drums:
            continue
        midi.tracks[index] = build(track, by_track.get(index, []))
    if review:
        midi.tracks.append(build([mido.MetaMessage("track_name", name="Pattern review")], review, REVIEW_CHANNEL))
    midi.save(out)


def run_patterns(args) -> int:
    source = args.midi.expanduser()
    midi = mido.MidiFile(source)
    exclude = {t.strip() for t in args.exclude.split(",") if t.strip()}
    tpb = midi.ticks_per_beat
    bar, step = BEATS_PER_BAR * tpb, tpb * 4 // args.grid
    if args.from_bar:
        start = (args.from_bar - 1) * bar
    else:
        start = steady_start_tick(midi)
    notes = _grid_notes(midi, exclude)
    repaired, review, changes = repair_patterns(
        notes,
        start,
        bar,
        step,
        window=args.window,
        similarity=args.similarity,
        neighbours=args.neighbours,
        min_neighbours=args.min_neighbours,
        add=None if args.add <= 0 else args.add,
        move=args.move,
        octave=args.octave,
        review=args.review,
    )
    out = (args.out_dir or source.parent).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{source.stem} - patterns.mid"
    write_pattern_midi(source, path, repaired, review, exclude)
    names = {i: next((m.name.strip() for m in t if m.type == "track_name"), "") for i, t in enumerate(midi.tracks)}
    tempo_map = _tempo_map(midi)
    chart = out / f"{source.stem} - pattern changes.csv"
    with chart.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["action", "bar", "step", "time", "track", "pitch", "new_pitch", "support"])
        for ch in sorted(changes, key=lambda x: x.tick):
            bar_no, rest = divmod(ch.tick, bar)
            w.writerow([ch.action, bar_no + 1, rest // step + 1, mmss(_seconds(ch.tick, tempo_map, tpb)), names.get(ch.track, ""), ch.pitch, ch.new_pitch or "", f"{ch.support:.2f}"])
    counts = Counter(ch.action for ch in changes)
    by_track = Counter(names.get(ch.track, "") for ch in changes if ch.action == "add")
    print(f"repeated section from bar {start // bar + 1}; grid 1/{args.grid}; {sum(1 for n in notes if n.start >= start)} notes in it")
    print("changes: " + (", ".join(f"{k} {v}" for k, v in sorted(counts.items())) or "none"))
    if by_track:
        print("added by track: " + ", ".join(f"{k} {v}" for k, v in by_track.most_common()))
    print(f"written: {path}\n         {chart}")
    return 0


# --- Merge: combine independent transcriptions of one recording ----------------


def load_source(spec: str) -> list[tuple[float, float, int, int]]:
    """Notes (start, end, pitch, velocity) in seconds from 'notes.mid', or
    'notes.mid+tempo.mid' when the tempo map is in a separate file (Logic's
    Smart Tempo export). Overlapping duplicates are merged."""
    notes_path, _, tempo_path = spec.partition("+")
    notes_path = Path(notes_path).expanduser()
    if not tempo_path:
        return [(n.start, n.end, n.pitch, n.velocity) for n in merge_fragments(load_transcription(notes_path))[0]]
    midi = mido.MidiFile(notes_path)
    tempo_map = _tempo_map(mido.MidiFile(Path(tempo_path).expanduser()))
    rows = []
    for track in midi.tracks:
        now, held = 0, defaultdict(list)
        for msg in track:
            now += msg.time
            if msg.type == "note_on" and msg.velocity > 0:
                held[msg.note].append((now, msg.velocity))
            elif msg.type in ("note_on", "note_off") and held[msg.note]:
                start, velocity = held[msg.note].pop(0)
                rows.append(
                    Note(_seconds(start, tempo_map, midi.ticks_per_beat), _seconds(now, tempo_map, midi.ticks_per_beat), msg.note, velocity)
                )
    return [(n.start, n.end, n.pitch, n.velocity) for n in merge_fragments(sorted(rows, key=lambda n: (n.start, n.pitch)))[0]]


def merge_transcriptions(sources: list[list], window: float = 0.2, within_base: bool = False) -> tuple[list, list[int]]:
    """Union of transcriptions, earlier sources first: a note is added
    unless a kept note of the same pitch starts within 50 ms of it, or is
    sounding when it starts and began less than `window` s away (the same
    note heard by two transcribers). A repeat that starts after the previous
    note ends is kept. within_base: notes of the other sources outside the
    first source's span are left out. Returns (notes, how many each source
    contributed)."""
    kept: list = []
    index: dict[int, list[tuple[float, float]]] = defaultdict(list)
    counts = []
    first = min(n[0] for n in sources[0]) if within_base and sources[0] else float("-inf")
    last = max(n[1] for n in sources[0]) if within_base and sources[0] else float("inf")
    for number, source in enumerate(sources):
        added = 0
        for s, e, p, v in sorted(source):
            if number and not first <= s <= last:
                continue  # outside the base transcription: e.g. noise before the music
            spans = index[p]
            k = bisect.bisect_left(spans, (s, -1.0))
            duplicate = any(
                abs(a - s) < 0.05 or (abs(a - s) < window and a < e and s < b)
                for a, b in spans[max(0, k - 4) : k + 4]
            )
            if duplicate:
                continue
            kept.append((s, e, p, v))
            spans.insert(k, (s, e))
            added += 1
        counts.append(added)
    return sorted(kept), counts


def run_merge(args) -> int:
    sources = [load_source(spec) for spec in args.sources]
    merged, counts = merge_transcriptions(sources, args.window, args.within_base)
    first = Path(args.sources[0].partition("+")[0]).expanduser()
    out = (args.out_dir or first.parent).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    path = out / (args.output or f"{first.stem} - merged.mid")
    midi = mido.MidiFile(type=1, ticks_per_beat=480)
    midi.tracks.append(mido.MidiTrack([mido.MetaMessage("set_tempo", tempo=500000)]))
    events = []
    for s, e, p, v in merged:
        events += [(round(s * 960), 1, p, v), (max(round(e * 960), round(s * 960) + 1), 0, p, 0)]
    events.sort(key=lambda x: (x[0], x[1]))
    track, last = mido.MidiTrack([mido.MetaMessage("track_name", name="merged")]), 0
    for tick, on, p, v in events:
        track.append(mido.Message("note_on" if on else "note_off", note=p, velocity=v, time=tick - last))
        last = tick
    midi.tracks.append(track)
    midi.save(path)
    for spec, source, count in zip(args.sources, sources, counts):
        print(f"{Path(spec.partition('+')[0]).name:40} {len(source):6} notes, {count:6} added")
    print(f"merged: {len(merged)} notes -> {path}")
    return 0


# --- Rhythm: straight, triplet, swung or free, bar by bar ---------------------

STRAIGHT_DIVISIONS = (2, 4)  # per beat: eighths, sixteenths
TRIPLET_DIVISIONS = (3, 6)  # per beat: triplet eighths, triplet sixteenths


def subdivision_fits(positions: np.ndarray, weights: np.ndarray) -> dict[int, float]:
    """How tightly onsets (in beats) cluster on each subdivision of the beat,
    0-1: the length of the mean phasor at 2, 3, 4, 6 and 8 per beat."""
    total = weights.sum() or 1.0
    return {d: float(abs(np.sum(weights * np.exp(2j * np.pi * positions * d))) / total) for d in (2, 3, 4, 6, 8)}


def _grid_scores(fits: dict[int, float]) -> tuple[float, float, int, int]:
    """(straight, triplet, best straight division, best triplet division).
    Finer grids fit anything coarser, so they count at 0.9."""
    weight = lambda d: 1.0 if d <= 4 else 0.9
    straight = max(((fits[d] * weight(d), d) for d in (2, 4, 8)))
    triplet = max(((fits[d] * weight(d), d) for d in TRIPLET_DIVISIONS))
    return straight[0], triplet[0], straight[1], triplet[1]


def swing_ratio(positions: np.ndarray, division: int) -> Optional[float]:
    """Where the off-beat notes of a straight grid fall, as a share of their
    pair, measured from the on-beat notes (so a bar that is late or early as
    a whole, e.g. a slowing fade against a constant tempo map, reads as
    straight): 0.50 straight, 0.58 light swing, 0.67 triplet swing. None when
    there are too few on- or off-beats to tell."""
    pair = division / 2  # pairs per beat: 1 for eighths, 2 for sixteenths
    phase = (positions * pair) % 1.0
    on = phase[(phase < 0.2) | (phase > 0.9)]
    off = phase[(phase > 0.3) & (phase < 0.85)]
    if len(on) < 3 or len(off) < 4:
        return None
    on_offset = float(np.angle(np.mean(np.exp(2j * np.pi * on))) / (2 * np.pi))  # -0.5..0.5
    return float(np.mean(off) - on_offset)


@dataclass
class BarRhythm:
    bar: int  # 0-based
    start: float  # seconds
    notes: int
    kind: str  # straight, triplet, swing, free, (empty: too few notes)
    division: int  # per beat (0: none)
    fit: float  # 0-1, of the chosen grid
    p: float  # chance of a fit this good from random onsets
    swing: Optional[float] = None


def bar_rhythms(
    positions: np.ndarray,
    weights: np.ndarray,
    beats: np.ndarray,
    window: int = 1,
    min_notes: int = 6,
    alpha: float = 0.01,
    simulations: int = 300,
    seed: int = 0,
) -> list[BarRhythm]:
    """For each `window` bars: the grid the onsets (positions in beats) fit,
    tested against `simulations` sets of as many random onsets. A grid
    counts only if it fits better than 1 - alpha of them; triplet over
    straight needs the triplet grid to fit better too."""
    rng = np.random.default_rng(seed)
    span = BEATS_PER_BAR * window
    out = []
    bars = int(positions.max() // span) + 1 if len(positions) else 0
    for k in range(bars):
        a = k * span
        sel = (positions >= a) & (positions < a + span)
        n = int(sel.sum())
        start = float(np.interp(a, np.arange(len(beats)), beats))
        if n < min_notes:
            out.append(BarRhythm(k * window, start, n, "", 0, 0.0, 1.0))
            continue
        pos, w = positions[sel], weights[sel]
        straight, triplet, sd, td = _grid_scores(subdivision_fits(pos, w))
        null = np.array([_grid_scores(subdivision_fits(a + rng.uniform(0, span, n), w))[:2] for _ in range(simulations)])
        p_straight = float((null[:, 0] >= straight).mean())
        p_triplet = float(((null[:, 1] - null[:, 0]) >= (triplet - straight)).mean())
        if triplet > straight and p_triplet < alpha:
            out.append(BarRhythm(k * window, start, n, "triplet", td, triplet, p_triplet))
        elif p_straight < alpha:
            swing = swing_ratio(pos, sd)
            kind = "swing" if swing is not None and swing >= 0.55 else "straight"
            out.append(BarRhythm(k * window, start, n, kind, sd, straight, p_straight, swing))
        else:
            out.append(BarRhythm(k * window, start, n, "free", 0, max(straight, triplet), min(p_straight, p_triplet)))
    return out


def rhythm_runs(bars: list[BarRhythm]) -> list[tuple[int, int, str]]:
    """Consecutive bars of one kind (bars with too few notes join the run
    around them): (first bar, last bar, kind). A run of straight or triplet
    bars is sequenced (or very steady) playing."""
    runs: list[list] = []
    for b in bars:
        kind = b.kind or (runs[-1][2] if runs else "")
        if runs and runs[-1][2] == kind:
            runs[-1][1] = b.bar
        else:
            runs.append([b.bar, b.bar, kind])
    return [tuple(r) for r in runs if r[2]]


def run_rhythm(args) -> int:
    source = args.midi.expanduser()
    exclude = {t.strip() for t in args.exclude.split(",") if t.strip()}
    rows = [r for r in _paired_notes(source) if r[4] != DRUM_CHANNEL and r[5] not in exclude]
    if args.own_tempo_map:
        midi = mido.MidiFile(source)
        tempo_map, tpb = _tempo_map(midi), midi.ticks_per_beat
        end = max(r[1] for r in rows)
        beats = [0.0]
        while beats[-1] <= end + 4:
            beats.append(_seconds(len(beats) * tpb, tempo_map, tpb))
        beats = np.array(beats)
    else:
        plan = plan_tempo(rows, max(r[1] for r in rows), args.bars.expanduser() if args.bars else None, args.bpm, 4, args.steady_start, args.downbeat)
        beats = plan.beats
    index = np.arange(len(beats), dtype=float)
    groups = {"all tracks": rows}
    if args.per_track:
        groups = defaultdict(list)
        for r in rows:
            groups[r[5]].append(r)
    out = (args.out_dir or source.parent).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    chart = out / f"{source.stem} - rhythm.csv"
    with chart.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["track", "bar", "time", "notes", "kind", "per_beat", "fit", "p", "swing"])
        for name, members in groups.items():
            positions = np.interp([r[0] for r in members], beats, index)
            weights = np.array([r[3] for r in members], dtype=float)
            bars = bar_rhythms(positions, weights, beats, args.window, alpha=args.alpha)
            for b in bars:
                w.writerow([name, b.bar + 1, mmss(b.start), b.notes, b.kind, b.division or "", f"{b.fit:.2f}", f"{b.p:.3f}", "" if b.swing is None else f"{b.swing:.2f}"])
            counts = Counter(b.kind for b in bars if b.kind)
            print(f"{name}: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())) + " bars")
            for first, last, kind in rhythm_runs(bars):
                if last - first + 1 >= args.min_run or kind == "triplet":
                    members_ = [b for b in bars if first <= b.bar <= last and b.kind == kind]
                    grid = Counter(b.division for b in members_).most_common(1)[0][0] if members_ and kind != "free" else 0
                    label = {"straight": f"straight, {grid} per beat", "triplet": f"TRIPLETS, {grid} per beat", "swing": f"swung, {grid} per beat", "free": "free (no steady grid)"}[kind]
                    t = np.interp(first * BEATS_PER_BAR, index, beats)
                    print(f"  bars {first + 1:3}-{last + 1:<3} from {mmss(t)}: {label}")
    print(f"written: {chart}")
    return 0


# --- Cycles: arpeggiator / sequencer figures, found by aligning a track with itself


@dataclass
class Cycle:
    track: int
    first: int  # step (from the section start) of the first instance
    last: int  # step after the last instance
    period: int  # steps
    pitches: list  # per phase: tuple of pitches (empty: a rest)
    velocity: list  # per phase: median velocity (0 for rests)
    length: list  # per phase: median length in steps
    agreement: float  # mean share of the cycle's notes each instance plays
    errors: list = field(default_factory=list)  # (step, kind, pitch, other track)


def _step_notes(notes: list[GridNote], start: int, step: int) -> dict[int, dict[int, list[GridNote]]]:
    """track -> step -> notes starting on it (from `start`, on the grid)."""
    out: dict[int, dict[int, list[GridNote]]] = defaultdict(lambda: defaultdict(list))
    for n in notes:
        if n.start >= start:
            out[n.track][round((n.start - start) / step)].append(n)
    return out


def self_alignment(steps: dict[int, list[GridNote]], a: int, b: int, lag: int) -> float:
    """Share of the notes in steps a..b whose pitch recurs exactly `lag`
    steps later."""
    hit = total = 0
    for t in range(a, b - lag):
        here = {n.pitch for n in steps.get(t, ())}
        if here:
            total += len(here)
            hit += len(here & {n.pitch for n in steps.get(t + lag, ())})
    return hit / total if total else 0.0


def find_cycle_period(
    steps, a: int, b: int, lags=range(2, 17), min_notes: int = 8, min_contrast: float = 0.2
) -> tuple[int, float]:
    """(period, score) for steps a..b: the shortest lag scoring at least 90%
    of the best (a figure repeating every 4 steps also repeats every 8). The
    period must also stand out: score at least min_contrast above the median
    lag, or a dense repeated note (which recurs at every lag) would pass as
    a figure of any length. (0, 0) when there is none."""
    if sum(len(steps.get(t, ())) for t in range(a, b)) < min_notes:
        return 0, 0.0
    scores = {lag: self_alignment(steps, a, b, lag) for lag in lags}
    best = max(scores.values())
    period = min(lag for lag, v in scores.items() if v >= 0.9 * best)
    if scores[period] - float(np.median(list(scores.values()))) < min_contrast:
        return 0, 0.0
    return period, scores[period]


def _consensus(steps, origin: int, period: int, instances: list[int], presence: float = 0.5):
    """Per phase: the pitches at least `presence` of the instances play, with
    their median velocity and length."""
    pitches, velocity, length = [], [], []
    for phase in range(period):
        counts: Counter = Counter()
        vel, dur = defaultdict(list), defaultdict(list)
        for k in instances:
            for n in steps.get(origin + k * period + phase, ()):
                counts[n.pitch] += 1
                vel[n.pitch].append(n.velocity)
                dur[n.pitch].append(n.end - n.start)
        keep = tuple(sorted(p for p, c in counts.items() if c >= presence * len(instances)))
        pitches.append(keep)
        velocity.append(int(np.median([v for p in keep for v in vel[p]])) if keep else 0)
        length.append(float(np.median([d for p in keep for d in dur[p]])) if keep else 0.0)
    return pitches, velocity, length


def _instance_agreement(steps, origin: int, period: int, k: int, pitches) -> float:
    expected = [(phase, p) for phase in range(period) for p in pitches[phase]]
    if not expected:
        return 0.0
    hit = sum(1 for phase, p in expected if any(n.pitch == p for n in steps.get(origin + k * period + phase, ())))
    return hit / len(expected)


def find_cycles(
    notes: list[GridNote],
    start: int,
    step: int,
    bar_steps: int = 16,
    window_bars: int = 2,
    min_score: float = 0.5,
    min_bars: int = 2,
    min_agreement: float = 0.5,
    tracks: Optional[set[int]] = None,
    min_repeats: int = 8,
) -> list[Cycle]:
    """Repeating figures in each track: 2-bar windows (moving a bar at a
    time) whose notes recur at one period make a run; the run's figure is
    the consensus of the instances that agree with it; its ends are moved
    to the first and last instances that still agree."""
    by_track = _step_notes(notes, start, step)
    cycles = []
    for track, steps in by_track.items():
        if tracks is not None and track not in tracks:
            continue
        last_step = max(steps) + 1
        windows = []
        for w in range(0, last_step, bar_steps):
            period, score = find_cycle_period(steps, w, w + window_bars * bar_steps)
            windows.append((w, period if score >= min_score else 0))
        runs: list[list[int]] = []  # [first window step, last window step, period]
        for w, period in windows:
            if period and runs and runs[-1][2] == period and runs[-1][1] == w - bar_steps:
                runs[-1][1] = w
            elif period:
                runs.append([w, w, period])
        for a, b, period in runs:
            if (b - a) // bar_steps + 1 < min_bars:
                continue
            origin = a
            span = b + window_bars * bar_steps
            instances = list(range((span - origin) // period))
            pitches, _v, _l = _consensus(steps, origin, period, instances)
            agreeing = [k for k in instances if _instance_agreement(steps, origin, period, k, pitches) >= min_agreement]
            if len(agreeing) < 4:
                continue
            pitches, velocity, length = _consensus(steps, origin, period, agreeing)
            if not any(pitches):
                continue
            # move the ends to the first/last instances that agree, looking
            # beyond the windows too
            k0, k1 = 0, len(instances) - 1
            while origin + (k0 - 1) * period >= 0 and _instance_agreement(steps, origin, period, k0 - 1, pitches) >= min_agreement:
                k0 -= 1
            while _instance_agreement(steps, origin, period, k1 + 1, pitches) >= min_agreement:
                k1 += 1
            while k0 < k1 and _instance_agreement(steps, origin, period, k0, pitches) < min_agreement:
                k0 += 1
            while k1 > k0 and _instance_agreement(steps, origin, period, k1, pitches) < min_agreement:
                k1 -= 1
            if k1 - k0 + 1 < min_repeats:
                continue
            scores = [_instance_agreement(steps, origin, period, k, pitches) for k in range(k0, k1 + 1)]
            cycles.append(
                Cycle(track, origin + k0 * period, origin + (k1 + 1) * period, period, pitches, velocity, length, float(np.mean(scores)))
            )
    # overlapping runs of one track (e.g. a window pair at the seam): keep the longer
    cycles.sort(key=lambda c: (c.track, c.first))
    kept: list[Cycle] = []
    for cyc in cycles:
        if kept and kept[-1].track == cyc.track and cyc.first < kept[-1].last:
            if cyc.last - cyc.first > kept[-1].last - kept[-1].first:
                kept[-1] = cyc
            continue
        kept.append(cyc)
    # the errors of each instance
    for cyc in kept:
        steps = by_track[cyc.track]
        for t in range(cyc.first, cyc.last):
            expected = set(cyc.pitches[(t - cyc.first) % cyc.period])
            present = {n.pitch for n in steps.get(t, ())}
            for p in expected - present:
                other = next((tr for tr, st in by_track.items() if tr != cyc.track and any(n.pitch == p for n in st.get(t, ()))), None)
                cyc.errors.append((t, "in another track" if other is not None else "missing", p, other))
            for p in present - expected:
                kind = "wrong pitch" if expected and not (expected & present) else "extra"
                cyc.errors.append((t, kind, p, None))
    return kept


def repair_cycles(
    notes: list[GridNote],
    cycles: list[Cycle],
    start: int,
    step: int,
    fill: bool = True,
    adopt: bool = True,
    fix_pitch: bool = False,
    review_extra: bool = False,
) -> tuple[list[GridNote], list[GridNote], Counter]:
    """Apply the cycle's corrections: fill = add missing notes (the phase's
    velocity and length); adopt = move the right note from another track into
    the figure's track; fix_pitch = give a wrong note the figure's pitch;
    review_extra = set extra notes aside."""
    out = [GridNote(**n.__dict__) for n in notes]
    review, counts = [], Counter()
    index = defaultdict(list)
    for i, n in enumerate(out):
        if n.start >= start:
            index[(n.track, round((n.start - start) / step))].append(i)
    drop = set()
    for cyc in cycles:
        channel = next((n.channel for n in notes if n.track == cyc.track), 0)
        for t, kind, pitch, other in cyc.errors:
            phase = (t - cyc.first) % cyc.period
            tick = start + t * step
            if kind == "missing" and fill:
                out.append(GridNote(cyc.track, tick, tick + max(1, int(cyc.length[phase])), pitch, max(1, cyc.velocity[phase]), channel))
                counts["filled"] += 1
            elif kind == "in another track" and adopt:
                for i in index[(other, t)]:
                    if out[i].pitch == pitch and i not in drop:
                        out[i].track, out[i].channel = cyc.track, channel
                        counts["moved into the figure's track"] += 1
                        break
            elif kind == "wrong pitch" and fix_pitch:
                for i in index[(cyc.track, t)]:
                    if out[i].pitch == pitch:
                        expected = cyc.pitches[phase]
                        out[i].pitch = expected[0]
                        counts["pitch corrected"] += 1
                        break
            elif kind == "extra" and review_extra:
                for i in index[(cyc.track, t)]:
                    if out[i].pitch == pitch and i not in drop:
                        drop.add(i)
                        review.append(out[i])
                        counts["extra set aside"] += 1
                        break
    return [n for i, n in enumerate(out) if i not in drop], review, counts


def describe_cycle(cyc: Cycle) -> str:
    cells = []
    for pitches, vel in zip(cyc.pitches, cyc.velocity):
        cells.append("+".join(f"{PITCH_NAMES[p % 12]}{p // 12 - 1}" for p in pitches) + f"/{vel}" if pitches else "rest")
    return " ".join(cells)


def run_cycles(args) -> int:
    source = args.midi.expanduser()
    midi = mido.MidiFile(source)
    exclude = {t.strip() for t in args.exclude.split(",") if t.strip()}
    tpb = midi.ticks_per_beat
    bar, step = BEATS_PER_BAR * tpb, tpb * 4 // args.grid
    start = (args.from_bar - 1) * bar if args.from_bar else steady_start_tick(midi)
    names = {i: next((m.name.strip() for m in t if m.type == "track_name"), "") for i, t in enumerate(midi.tracks)}
    wanted = None
    if args.track:
        wanted = {i for i, n in names.items() if n in set(args.track)}
        if not wanted:
            raise SystemExit(f"no track named {', '.join(args.track)}")
    notes = _grid_notes(midi, exclude)
    cycles = find_cycles(notes, start, step, bar // step, min_score=args.min_score, min_bars=args.min_bars, tracks=wanted)
    tempo_map = _tempo_map(midi)
    at = lambda t: (start + t * step)
    where = lambda t: f"bar {at(t) // bar + 1} step {(at(t) % bar) // step + 1} ({mmss(_seconds(at(t), tempo_map, tpb))})"
    out = (args.out_dir or source.parent).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    chart = out / f"{source.stem} - cycles.csv"
    with chart.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["track", "bar", "step", "time", "error", "pitch", "other_track"])
        for cyc in cycles:
            notes_n = sum(1 for p in cyc.pitches if p)
            kinds = Counter(k for _t, k, _p, _o in cyc.errors)
            print(f"{names[cyc.track]}: every {cyc.period} steps ({notes_n} notes, {cyc.period - notes_n} rests): {describe_cycle(cyc)}")
            print(f"  from {where(cyc.first)} to {where(cyc.last)}: {(cyc.last - cyc.first) // cyc.period} repeats, each plays {cyc.agreement:.0%} of the figure on average")
            print("  errors: " + (", ".join(f"{k} {v}" for k, v in kinds.most_common()) or "none"))
            for t, kind, pitch, other in cyc.errors:
                b, r = divmod(at(t), bar)
                w.writerow([names[cyc.track], b + 1, r // step + 1, mmss(_seconds(at(t), tempo_map, tpb)), kind, f"{PITCH_NAMES[pitch % 12]}{pitch // 12 - 1}", names.get(other, "") if other is not None else ""])
    if not cycles:
        print("no repeating figures found")
    if args.repair:
        repaired, review, counts = repair_cycles(notes, cycles, start, step, fill=not args.no_fill, adopt=not args.no_adopt, fix_pitch=args.fix_pitch, review_extra=args.review_extra)
        path = out / f"{source.stem} - cycles.mid"
        write_pattern_midi(source, path, repaired, review, exclude)
        print("repaired: " + (", ".join(f"{k} {v}" for k, v in counts.items()) or "nothing to do") + f"\nwritten: {path}")
    print(f"errors listed in {chart}")
    return 0


# --- Accuracy check ----------------------------------------------------------


def _script_module(name: str):
    scripts = str(Path(__file__).resolve().parent)
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    return __import__(name)


def _midi_patterns():
    return _script_module("midi_patterns")


def run_repeats(args) -> int:
    """Replace inconsistent repetitions with the consensus cell."""
    source = args.midi.expanduser()
    rows = [r for r in _paired_notes(source) if r[4] != DRUM_CHANNEL and r[5] != GHOST and not r[5].endswith(" once")]
    if not rows:
        raise SystemExit("no pitched notes")
    plan = plan_tempo(
        rows,
        max(r[1] for r in rows),
        args.bars.expanduser() if args.bars else None,
        args.bpm,
        args.steps_per_beat,
        args.steady_start,
        args.downbeat,
    )
    out = (args.out_dir or source.parent).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{source.stem} - repeats.mid"
    steady_from = plan.steady_start if args.steady_start is None else args.steady_start
    runs = _midi_patterns().rebuild_file(source, path, plan, args.match, args.agree, steady_from)
    print(
        f"steady section from {mmss(steady_from)}: {plan.bpm:.2f} BPM, "
        f"grid 1/{plan.steps_per_beat * 4} = {plan.step * 1000:.1f} ms"
    )
    print(_midi_patterns().format_report(runs))
    print(f"written: {path}")
    print("check the result with 'roundtrip' against the recording before using it")
    return 0


def run_gates(args) -> int:
    """Give each track one gate. Onsets stay put."""
    source = args.midi.expanduser()
    out = (args.out_dir or source.parent).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{source.stem} - gates.mid"
    reports = _script_module("midi_gates").apply_gates(source, path)
    print(_script_module("midi_gates").format_report(reports))
    print(f"written: {path}")
    return 0


def run_musicality(args) -> int:
    """Musical fidelity: harmony, rhythm, dynamics, texture and form of the
    recording against each MIDI file. A dimension's headline is the plain
    mean of its components, printed 0-100. There is no overall score."""
    mus = _script_module("midi_musicality")
    wav = args.wav.expanduser()
    samples, rate = load_wav_mono(wav)
    audio = mus.audio_features(samples, rate)
    frames, onset_frames = len(audio.semitones), len(audio.onsets)
    exclude = {t.strip() for t in args.exclude.split(",") if t.strip()}
    chords = [c for c in args.chords.split(",") if c.strip()] if args.chords else None
    sections = mus.read_sections(args.sections.expanduser()) if args.sections else None
    print(f"Musical fidelity: {wav.name}; excluded tracks: {', '.join(sorted(exclude)) or 'none'}")
    print(mus.header())
    for path in args.midi:
        path = path.expanduser()
        grouped: dict[str, list] = defaultdict(list)
        for s, e, p, v, ch, name in _paired_notes(path):
            if ch == DRUM_CHANNEL or name in exclude:
                continue
            grouped[name or "MIDI"].append((s, e, p, v))
        rows = [note for notes in grouped.values() for note in notes]
        result = mus.musicality(
            audio,
            mus.midi_features(rows, frames, onset_frames, grouped),
            args.window,
            args.max_lag,
            chords,
            keep_curves=bool(args.plot),
            onset_tolerance=args.onset_tolerance,
            sections=sections,
        )
        name = path.name if len(path.name) <= 44 else path.name[:41] + "..."
        print(mus.format_row(name, result))
        print(mus.format_details(result))
        printed = mus.format_sections(result)
        if printed:
            print(printed)
        if args.controls:
            midi_obj = mido.MidiFile(path)
            tempo = _tempo_map(midi_obj)[-1][1]
            bar = args.bar_seconds or BEATS_PER_BAR * tempo / 1e6
            print(f"  controls (each changes one thing; one bar = {bar:.2f} s; shifted controls are not re-aligned):")
            print(f"    {'control':<26}" + "".join(f"{k:>8}" for k in mus.DIMENSIONS) + f" {'cover':>8} {'offset':>8}   should drop")
            for label, notes, lag_limit, expect in mus.control_variants(rows, bar):
                r = mus.musicality(
                    audio,
                    mus.midi_features(notes, frames, onset_frames),
                    args.window,
                    lag_limit,
                    chords,
                    onset_tolerance=args.onset_tolerance,
                )
                offset = r.extras["texture"]["register offset"]
                print(
                    f"    {label:<26}"
                    + "".join(mus.hundred(r.scores[k]) for k in mus.DIMENSIONS)
                    + f" {mus.hundred(r.coverage['recording']):>8} {offset:+7.1f}st   {expect}"
                )
        if args.per_window:
            for start, scores in result.windows:
                print(f"    {mmss(start)[:-2]:>6} " + " ".join(f"{k} {mus.hundred(v).strip()}" for k, v in scores.items()))
        if args.plot:
            out = args.plot.expanduser()
            if len(args.midi) > 1:
                out.mkdir(parents=True, exist_ok=True)
                out = out / f"{path.stem} - musicality.png"
            else:
                out.parent.mkdir(parents=True, exist_ok=True)
            mus.plot(result, out, f"{path.stem}: musical fidelity, recording (blue) against MIDI (orange)")
            print(f"    plot: {out}")
    print("Headlines are the mean of the components under them, on 0-100 (a negative correlation prints as 0).")
    print("harmony: chord, root, quality, chroma. rhythm: onsets, onset F, inter-onset intervals, bar pattern.")
    print("dynamics: attacks, sounding velocity, note count, dynamic range, fades. texture: density and register.")
    print("form: self-similarity of harmony and of rhythm. coverage: active frames and shared silence.")
    return 0


def run_diagnose(args) -> int:
    """Where a MIDI file departs from its recording, the likely cause, and
    what to try. Changes nothing."""
    mus = _script_module("midi_musicality")
    diag = _script_module("midi_diagnose")
    samples, rate = load_wav_mono(args.wav.expanduser())
    audio = mus.audio_features(samples, rate)
    exclude = {t.strip() for t in args.exclude.split(",") if t.strip()}
    chords = [c for c in args.chords.split(",") if c.strip()] if args.chords else None
    sections = mus.read_sections(args.sections.expanduser())
    for path in args.midi:
        path = path.expanduser()
        midi = mido.MidiFile(path)
        tempos = _tempo_map(midi)
        steady = args.steady_start
        if steady is None and len(tempos) > 2:
            steady = _seconds(steady_start_tick(midi), tempos, midi.ticks_per_beat)
        paired = [r for r in _paired_notes(path) if r[4] != DRUM_CHANNEL and r[5] not in exclude]
        baseline = None
        if args.baseline:
            baseline = [r for r in _paired_notes(args.baseline.expanduser()) if r[4] != DRUM_CHANNEL and r[5] not in exclude]
        result = diag.diagnose(audio, paired, sections, steady, chords, args.max_lag, baseline, midi_path=path if steady is not None else None, exclude=exclude)
        text = diag.format_report(result, path.name)
        print(text)
        if args.json:
            import json as _json

            out = args.json.expanduser()
            if len(args.midi) > 1:
                out.mkdir(parents=True, exist_ok=True)
                out = out / f"{path.stem} - diagnosis.json"
            out.write_text(_json.dumps(diag.to_json(result, path.name), indent=2))
            print(f"\nJSON: {out}")
        if args.report:
            out = args.report.expanduser()
            if len(args.midi) > 1:
                out.mkdir(parents=True, exist_ok=True)
                out = out / f"{path.stem} - diagnosis.md"
            out.write_text(text + "\n")
            print(f"\nwritten: {out}")
    return 0


def run_render_test(args) -> int:
    """Render the reference to audio (FluidSynth) for transcription."""
    soundfont = args.soundfont.expanduser()
    cmd = ["fluidsynth", "-ni", "-g", "0.8", "-r", "44100", "-F", str(args.wav.expanduser()), str(soundfont), str(args.reference.expanduser())]
    print(" ".join(cmd))
    return subprocess.call(cmd)


def run_evaluate(args) -> int:
    """How well the transcription and the rules recover known parts."""
    truth = args.truth.expanduser()
    referenced = classify(args.transcription.expanduser(), truth)
    print("Reference matching (truth notes found in the transcription):")
    for part, (found, total) in sorted(referenced.recall.items()):
        print(f"  {part:<12} {found:5}/{total:<5} {100 * found / max(total, 1):5.1f}%")
    true_part = {id(n): n.part for n in referenced.notes if n.source == "reference"}
    rules = classify(args.transcription.expanduser(), use_profiles=False)
    # same notes in both runs: pair them by (start, pitch)
    truth_by_key = {(round(n.start, 3), n.pitch): true_part[id(n)] for n in referenced.notes if id(n) in true_part}
    confusion: dict[str, Counter] = defaultdict(Counter)
    for n in rules.notes:
        key = (round(n.start, 3), n.pitch)
        if key in truth_by_key:
            confusion[truth_by_key[key]][n.part] += 1
    print("\nRules only (no reference): truth part -> labels given")
    for part in sorted(confusion):
        row = confusion[part]
        total = sum(row.values())
        print(f"  {part:<12} " + ", ".join(f"{label} {100 * c / total:.0f}%" for label, c in row.most_common(4)))
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="mode", required=True)

    c = sub.add_parser("classify", help="split a transcription into parts")
    c.add_argument("transcription", type=Path)
    c.add_argument("--reference", type=Path, help="labelled sequence of the same piece")
    c.add_argument("--corrections", type=Path, help="JSON list of manual fixes")
    c.add_argument("--out-dir", type=Path)
    c.add_argument("--rules-only", action="store_true", help="don't learn profiles from the reference")
    c.add_argument("--polyphony", action="store_true", help="limit each part to as many notes at once as the reference plays (moves the extras)")
    c.add_argument("--ref-offset", type=float, help="album time (s) of the reference's time 0, instead of searching")
    c.add_argument("--ref-ratio", type=float, default=1.0, help="with --ref-offset: album seconds per reference second")
    c.set_defaults(func=run_classify)

    r = sub.add_parser("render-test", help="render a labelled sequence to WAV")
    r.add_argument("reference", type=Path)
    r.add_argument("wav", type=Path)
    r.add_argument("--soundfont", type=Path, default=SOUNDFONT)
    r.set_defaults(func=run_render_test)

    e = sub.add_parser("evaluate", help="score a transcription of a rendered sequence")
    e.add_argument("transcription", type=Path)
    e.add_argument("--truth", type=Path, required=True)
    e.set_defaults(func=run_evaluate)

    h = sub.add_parser("chords", help="rebuild a chord track as held chords from its harmony")
    h.add_argument("midi", type=Path, help="a parts file, e.g. '... - parts.mid'")
    h.add_argument("--track", default="Chords", help="track to rebuild (default Chords)")
    h.add_argument("--evidence", help="comma-separated tracks to read the harmony from (default all but Ghost)")
    h.add_argument(
        "--chords",
        help="allowed chords, e.g. 'C,Am,A7,Dm7,Gsus4' (default every major, minor, 7, maj7, m7, sus2, sus4, dim and aug)",
    )
    h.add_argument("--start", type=float, default=0.0, help="seconds")
    h.add_argument("--end", type=float, help="seconds")
    h.add_argument("--change-cost", type=float, default=4.0, help="higher: fewer chord changes")
    h.add_argument("--min-chord", type=float, default=1.0, help="shortest chord, seconds")
    h.add_argument("--voices", type=int, default=4, help="notes per chord above the bass root")
    h.add_argument(
        "--drop-moving",
        action="store_true",
        help="delete every chord-tone note the held chords replace (default: keep those at pitches the chord doesn't hold, on '<track> extra')",
    )
    h.add_argument("--audio", type=Path, help="the recording the transcription came from (PCM WAV): adds its FFT chromagram")
    h.add_argument("--audio-weight", type=float, default=0.5, help="share of the audio chromagram, 0-1 (default 0.5)")
    h.add_argument(
        "--audio-method",
        choices=("fft", "cqt"),
        default="fft",
        help="fft: NumPy FFT (default, fast); cqt: librosa constant-Q with tuning correction and drums removed (slower)",
    )
    h.add_argument("--out-dir", type=Path)
    h.set_defaults(func=run_chords)

    q = sub.add_parser("quantize", help="give a parts file the song's real tempo map and snap notes to it")
    q.add_argument("midi", type=Path)
    q.add_argument("--bars", type=Path, help="a chord chart CSV (from 'chords'): its chord changes set the bars before the steady section")
    q.add_argument("--bpm", type=float, help="approximate tempo of the steady section (refined to +-0.5%%)")
    q.add_argument("--steps-per-beat", type=int, default=4, help="grid steps per beat in the steady section (4: sixteenths)")
    q.add_argument("--steady-start", type=float, help="seconds where the steady section starts (default: found)")
    q.add_argument("--downbeat", type=float, help="a time (s) in the steady section that is the first beat of a bar")
    q.add_argument("--strength", type=float, default=1.0, help="0-1: how far notes move towards the grid")
    q.add_argument("--quantize-opening", action="store_true", help="also quantize the freely played part (to eighths)")
    q.add_argument("--triplets", action="store_true", help="snap steady-section bars found to be in triplets to a triplet grid")
    q.add_argument("--out-dir", type=Path)
    q.set_defaults(func=run_quantize)

    rp = sub.add_parser("repeats", help="repair repeated cells from the notes that survive most repetitions")
    rp.add_argument("midi", type=Path)
    rp.add_argument("--bars", type=Path, help="a chord chart CSV: bars before the steady section, as for quantize")
    rp.add_argument("--bpm", type=float, help="approximate tempo of the steady section")
    rp.add_argument("--steps-per-beat", type=int, default=4, help="grid steps per beat (4: sixteenths)")
    rp.add_argument("--steady-start", type=float, help="seconds where the steady section starts (default: found)")
    rp.add_argument("--downbeat", type=float, help="a time (s) in the steady section that is beat 1 of a bar")
    rp.add_argument("--match", type=float, default=0.75, help="how alike two cells must be to count as the same loop")
    rp.add_argument("--agree", type=float, default=0.75, help="share of repetitions a note must survive to stay in the loop")
    rp.add_argument("--out-dir", type=Path)
    rp.set_defaults(func=run_repeats)

    g = sub.add_parser("gates", help="set each track's note lengths to 25, 50, 75 or 100 percent of its own step")
    g.add_argument("midi", type=Path)
    g.add_argument("--out-dir", type=Path)
    g.set_defaults(func=run_gates)

    t = sub.add_parser("roundtrip", help="how much of a recording's pitch content MIDI files carry (chroma correlation)")
    t.add_argument("wav", type=Path, help="the recording (PCM WAV)")
    t.add_argument("midi", type=Path, nargs="+", help="MIDI files to compare")
    t.add_argument("--render", action="store_true", help="render each MIDI with FluidSynth and compare audio with audio")
    t.add_argument("--soundfont", type=Path, default=SOUNDFONT)
    t.add_argument("--program", type=int, default=81, help="GM program for --render (default 81, sawtooth lead)")
    t.add_argument("--exclude", default=GHOST, help="comma-separated track names to leave out (default Ghost)")
    t.add_argument("--start", type=float, default=0.0)
    t.add_argument("--end", type=float)
    t.add_argument("--window", type=float, default=30.0, help="seconds per window in the breakdown")
    t.add_argument("--max-lag", type=float, default=10.0, help="search this many seconds either way to line the files up (0: none)")
    t.add_argument("--plot", type=Path, help="write a histogram of the correlation coefficient by song position (a directory when comparing several MIDI files)")
    t.set_defaults(func=run_roundtrip)

    k = sub.add_parser("key", help="detect the key of a MIDI file (whole piece and each section)")
    k.add_argument("midi", type=Path)
    k.add_argument("--exclude", default=GHOST, help="comma-separated track names to leave out (default Ghost)")
    k.set_defaults(func=run_key)

    fk = sub.add_parser("filter-key", help="optional: remove notes outside the key (check with roundtrip first)")
    fk.add_argument("midi", type=Path)
    fk.add_argument("--key", default="auto", help="e.g. 'C' or 'Am' (default: detected)")
    fk.add_argument("--allow", help="extra pitch classes to keep, e.g. 'Bb,F#'")
    fk.add_argument("--harmonic", action="store_true", help="minor keys: also keep the raised 6th and 7th")
    fk.add_argument("--chords", type=Path, help="a chord chart: also keep notes of the chord playing (A7's C# in C major, ...)")
    fk.add_argument("--keep-separate", action="store_true", help="move the notes to an 'Out of key' track instead of removing them")
    fk.add_argument("--exclude", default=GHOST, help="tracks to leave untouched and out of the key detection (default Ghost)")
    fk.add_argument("--out-dir", type=Path)
    fk.set_defaults(func=run_filter_key)

    pt = sub.add_parser("patterns", help="repair a sequenced section from its repetitions (run after quantize)")
    pt.add_argument("midi", type=Path, help="a quantized file (from 'quantize')")
    pt.add_argument("--from-bar", type=int, help="first bar of the repeated section (default: the last tempo change)")
    pt.add_argument("--grid", type=int, default=16, help="note grid (16: sixteenths)")
    pt.add_argument("--window", type=int, default=8, help="bars either side to look for repetitions")
    pt.add_argument("--similarity", type=float, default=0.3, help="how alike a bar must be to vote (0-1)")
    pt.add_argument("--neighbours", type=int, default=8, help="most similar bars that vote")
    pt.add_argument("--min-neighbours", type=int, default=3, help="voters needed before changing a bar")
    pt.add_argument("--add", type=float, default=0.5, help="add a missing note this share of voters have (0: off)")
    pt.add_argument("--move", type=float, help="move a lone note one step to a cell this share have (off by default)")
    pt.add_argument("--octave", type=float, help="move a lone note an octave to a cell this share have (off by default)")
    pt.add_argument("--review", type=float, help="set aside notes this share or fewer of voters have (off by default)")
    pt.add_argument("--exclude", default=GHOST, help="tracks left out and untouched (default Ghost)")
    pt.add_argument("--out-dir", type=Path)
    pt.set_defaults(func=run_patterns)

    mg = sub.add_parser("merge", help="combine independent transcriptions of one recording (first = base)")
    mg.add_argument("sources", nargs="+", help="transcriptions, base first; 'notes.mid+tempo.mid' for a separate tempo map")
    mg.add_argument("--window", type=float, default=0.2, help="seconds within which a sounding same-pitch note counts as the same note")
    mg.add_argument("--within-base", action="store_true", help="add no notes before the base's first note or after its last")
    mg.add_argument("--output", help="output file name (default '<base> - merged.mid')")
    mg.add_argument("--out-dir", type=Path)
    mg.set_defaults(func=run_merge)

    rh = sub.add_parser("rhythm", help="straight, triplet, swung or free, bar by bar (use timing before quantizing)")
    rh.add_argument("midi", type=Path)
    rh.add_argument("--own-tempo-map", action="store_true", help="use the file's own tempo map for the beats (a DAW or 'quantize' file)")
    rh.add_argument("--bars", type=Path, help="else: a chord chart for the bars before the steady section (as quantize)")
    rh.add_argument("--bpm", type=float)
    rh.add_argument("--steady-start", type=float)
    rh.add_argument("--downbeat", type=float)
    rh.add_argument("--window", type=int, default=1, help="bars per verdict")
    rh.add_argument("--per-track", action="store_true", help="a verdict for each track, not just all tracks together")
    rh.add_argument("--alpha", type=float, default=0.01, help="significance against random onsets")
    rh.add_argument("--min-run", type=int, default=4, help="shortest run of bars to list")
    rh.add_argument("--exclude", default=GHOST)
    rh.add_argument("--out-dir", type=Path)
    rh.set_defaults(func=run_rhythm)

    cy = sub.add_parser("cycles", help="find arpeggiator/sequencer figures (start, stop, notes, rests, velocity) and their errors")
    cy.add_argument("midi", type=Path, help="a quantized file")
    cy.add_argument("--track", nargs="*", help="only these tracks (default: all)")
    cy.add_argument("--from-bar", type=int, help="start of the gridded section (default: the last tempo change)")
    cy.add_argument("--grid", type=int, default=16)
    cy.add_argument("--min-score", type=float, default=0.5, help="share of notes that must recur at the period, per 2-bar window")
    cy.add_argument("--min-bars", type=int, default=2, help="shortest figure run, in windows")
    cy.add_argument("--repair", action="store_true", help="write '<name> - cycles.mid' with the corrections")
    cy.add_argument("--no-fill", action="store_true", help="with --repair: don't add missing notes")
    cy.add_argument("--no-adopt", action="store_true", help="with --repair: don't move the figure's notes from other tracks")
    cy.add_argument("--fix-pitch", action="store_true", help="with --repair: give wrong notes the figure's pitch")
    cy.add_argument("--review-extra", action="store_true", help="with --repair: set extra notes aside (channel 16)")
    cy.add_argument("--exclude", default=GHOST)
    cy.add_argument("--out-dir", type=Path)
    cy.set_defaults(func=run_cycles)

    mu = sub.add_parser("musicality", help="score harmony, rhythm, dynamics, texture and form against the recording")
    mu.add_argument("wav", type=Path, help="the recording (PCM WAV)")
    mu.add_argument("midi", type=Path, nargs="+", help="MIDI files to compare")
    mu.add_argument("--window", type=float, default=60.0, help="seconds per window in the breakdown")
    mu.add_argument("--max-lag", type=float, default=10.0, help="search this many seconds either way to line the files up")
    mu.add_argument("--onset-tolerance", type=float, default=0.05, help="seconds within which an onset counts as matching (default 50 ms)")
    mu.add_argument("--chords", help="chord vocabulary (default: every major, minor, 7, maj7, m7, sus2, sus4, dim and aug)")
    mu.add_argument("--exclude", default=GHOST)
    mu.add_argument("--per-window", action="store_true", help="print the scores of each window")
    mu.add_argument("--plot", type=Path, help="write a plot of the curves (a directory when comparing several files)")
    mu.add_argument("--sections", type=Path, help="named sections to score separately: JSON [{name, start, end}] or CSV name,start,end")
    mu.add_argument("--controls", action="store_true", help="also score the validation controls of each file (shifted, transposed, shuffled, ...)")
    mu.add_argument("--bar-seconds", type=float, help="bar length for the controls (default: from the file's last tempo)")
    mu.set_defaults(func=run_musicality)

    dg = sub.add_parser("diagnose", help="where a MIDI file departs from its recording, the likely cause and what to try (changes nothing)")
    dg.add_argument("wav", type=Path, help="the recording (PCM WAV)")
    dg.add_argument("midi", type=Path, nargs="+")
    dg.add_argument("--sections", type=Path, required=True, help="named sections: JSON [{name, start, end}] or CSV name,start,end")
    dg.add_argument("--steady-start", type=float, help="seconds where the steady section starts (default: the file's last tempo change)")
    dg.add_argument("--chords", help="chord vocabulary for harmony")
    dg.add_argument("--max-lag", type=float, default=10.0)
    dg.add_argument("--exclude", default=GHOST)
    dg.add_argument("--baseline", type=Path, help="another version of the MIDI: register and density are judged as changes from it")
    dg.add_argument("--json", type=Path, help="write the findings as JSON (a directory for several files)")
    dg.add_argument("--report", type=Path, help="write the report as Markdown (a directory for several files)")
    dg.set_defaults(func=run_diagnose)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
