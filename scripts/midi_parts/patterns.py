"""Repair a repeated section from its own repetitions."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import mido
import numpy as np

from midi_parts.models import DRUM_CHANNEL
from midi_parts.midi_io import (
    _seconds,
    _tempo_map,
    mmss,
)
from midi_parts.tempo import (
    BEATS_PER_BAR,
    steady_start_tick,
)



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
