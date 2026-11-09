"""Straight, triplet, swung, and free bar classification."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Optional

import mido
import numpy as np

from midi_parts.models import DRUM_CHANNEL
from midi_parts.midi_io import (
    _paired_notes,
    _seconds,
    _tempo_map,
    mmss,
)
from midi_parts.tempo import (
    BEATS_PER_BAR,
    plan_tempo,
)



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
