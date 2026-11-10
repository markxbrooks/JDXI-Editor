"""Repeated multi-bar phrases on one quantized 4/4 track.

A phrase is a run of bars that comes back later. The copies may differ by a
few notes, sit in another key, or return in a new order (AABA). This reports
the pairs and where they agree. It does not add, move, or delete notes, and
it does not use the fixed-period figures from cycles.
"""

from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
import mido

from midi_parts.patterns import _grid_notes
from midi_parts.tempo import BEATS_PER_BAR, steady_start_tick

STEPS = 16
MAX_SCAN = 512
INTERVAL_LIMIT = 24
# Onset and interval carry the phrase. Density only breaks ties. Absolute
# pitch is dropped when the search is allowed to transpose, and the rest of
# the weights are scaled to keep the score in 0..1.
_WEIGHTS = {
    "onset": 0.30,
    "interval": 0.25,
    "pitch_class": 0.20,
    "rest": 0.10,
    "density": 0.05,
    "absolute": 0.10,
}


@dataclass
class BarPrint:
    """One bar. Pitch classes are stored unweighted; rarity is applied when
    two bars are compared, so a pedal can be down-weighted from the whole track."""

    onsets: frozenset
    rests: frozenset
    intervals: dict
    classes: frozenset
    pitches: frozenset
    density: float


@dataclass
class BarAlignment:
    offset: int
    similarity: float
    status: str  # matched | shifted | different
    only_left: tuple
    only_right: tuple


@dataclass
class PhraseMatch:
    track: int
    bar_a: int  # 1-based, from the start of the file
    tick_a: int
    bar_b: int
    tick_b: int
    bars: int
    ticks: int
    similarity: float
    confidence: float  # share of the bars at or above the similarity line
    transposition: int  # semitones the second copy sits above the first
    alignment: list = field(default_factory=list)


def _jaccard(a: frozenset, b: frozenset) -> float:
    if not a and not b:
        return 1.0
    union = len(a | b)
    return len(a & b) / union if union else 0.0


def _weighted_jaccard(a: dict, b: dict) -> float:
    keys = set(a) | set(b)
    if not keys:
        return 1.0
    num = sum(min(a.get(k, 0.0), b.get(k, 0.0)) for k in keys)
    den = sum(max(a.get(k, 0.0), b.get(k, 0.0)) for k in keys)
    return num / den if den else 1.0


def _cosine(a: dict, b: dict) -> float:
    keys = set(a) | set(b)
    if not keys:
        return 1.0
    dot = sum(a.get(k, 0.0) * b.get(k, 0.0) for k in keys)
    na = sum(v * v for v in a.values()) ** 0.5
    nb = sum(v * v for v in b.values()) ** 0.5
    if na == 0 or nb == 0:
        return 1.0 if na == 0 and nb == 0 else 0.0
    return dot / (na * nb)


def bar_fingerprint(notes: list, origin: int, bar_ticks: int, step: int) -> BarPrint:
    """The bar that starts at `origin`. An onset is the sixteenth it falls in."""
    cells = []
    for note in notes:
        if origin <= note.start < origin + bar_ticks:
            slot = min(STEPS - 1, max(0, (note.start - origin) // step))
            cells.append((slot, note.pitch))
    cells.sort()
    onsets = frozenset(slot for slot, _p in cells)
    intervals: Counter = Counter()
    for (_s0, p0), (_s1, p1) in zip(cells, cells[1:]):
        intervals[max(-INTERVAL_LIMIT, min(INTERVAL_LIMIT, p1 - p0))] += 1
    return BarPrint(
        onsets,
        frozenset(s for s in range(STEPS) if s not in onsets),
        dict(intervals),
        frozenset(p % 12 for _s, p in cells),
        frozenset(p for _s, p in cells),
        len(cells) / STEPS,
    )


def pitch_class_rarity(prints: list) -> dict:
    """1, falling to 0.25 as a pitch class spreads from half the sounding bars
    to all of them. A rare class stays at 1: one wrong note must not outweigh
    the phrase. A pedal on most bars loses weight."""
    counts: Counter = Counter()
    total = 0
    for fp in prints:
        if not fp.classes:
            continue
        total += 1
        counts.update(fp.classes)
    if not total:
        return {}
    out = {}
    for pc, n in counts.items():
        share = n / total
        if share <= 0.5:
            out[pc] = 1.0
        else:
            out[pc] = max(0.25, 1.0 - 0.75 * (share - 0.5) / 0.5)
    return out


def _pc_vector(classes: frozenset, rarity: dict, shift: int) -> dict:
    return {(pc + shift) % 12: rarity.get(pc, 1.0) for pc in classes}


def bar_similarity(a: BarPrint, b: BarPrint, shift: int, rarity: dict, absolute: bool) -> float:
    """Weighted mean of the channels. `shift` is how many semitones `b` sits
    above `a`, so `b`'s pitch classes are rotated down by that amount.
    Absolute pitch is left out when `absolute` is false, and the other
    weights are scaled so the score still runs from 0 to 1."""
    parts = [
        (_WEIGHTS["onset"], _jaccard(a.onsets, b.onsets)),
        (_WEIGHTS["interval"], _cosine(a.intervals, b.intervals)),
        (
            _WEIGHTS["pitch_class"],
            _weighted_jaccard(_pc_vector(a.classes, rarity, 0), _pc_vector(b.classes, rarity, -shift)),
        ),
        (_WEIGHTS["rest"], _jaccard(a.rests, b.rests)),
        (_WEIGHTS["density"], 1.0 - abs(a.density - b.density)),
    ]
    if absolute:
        parts.append((_WEIGHTS["absolute"], _jaccard(a.pitches, b.pitches)))
    weight = sum(w for w, _v in parts)
    return sum(w * v for w, v in parts) / weight if weight else 0.0


def _diff_budget(length: int) -> int:
    """One differing bar per four bars, and at least one so a short phrase
    can still carry a single bad bar."""
    return max(1, length // 4)


def _grow(prints, rarity, i: int, j: int, shift: int, max_bars: int, minimum: float, absolute: bool):
    """Bars i.. and j.. at one transposition, extended while the difference
    budget holds and the ranges do not overlap. Returns (rows, diffs) or
    None when the passage never reaches a bar."""
    rows = []
    diffs = 0
    n = len(prints)
    for length in range(1, max_bars + 1):
        if i + length > j or j + length > n:
            break
        sim = bar_similarity(prints[i + length - 1], prints[j + length - 1], shift, rarity, absolute)
        differs = sim < minimum
        if differs and diffs + 1 > _diff_budget(length):
            break
        left, right = prints[i + length - 1], prints[j + length - 1]
        only_left = tuple(sorted(p for p in left.pitches if p + shift not in right.pitches))
        only_right = tuple(sorted(p for p in right.pitches if p - shift not in left.pitches))
        if differs:
            status = "different"
        elif shift:
            status = "shifted"
        else:
            status = "matched"
        rows.append(BarAlignment(length - 1, sim, status, only_left, only_right))
        diffs += int(differs)
    return rows


def _passage(prints, rarity, i, j, max_bars, minimum, absolute):
    """The longest passage from bars i and j whose mean stays at or above
    `minimum`. The transposition is the shift with the best mean."""
    shifts = range(-12, 13) if not absolute else (0,)
    best = None
    for shift in shifts:
        rows = _grow(prints, rarity, i, j, shift, max_bars, minimum, absolute)
        # The seed bar is at or above the line. A later bar may fall short,
        # within the difference budget, and still stay if the mean holds.
        if not rows or rows[0].similarity < minimum:
            continue
        while len(rows) >= 2 and sum(r.similarity for r in rows) / len(rows) < minimum:
            rows.pop()
        mean = sum(r.similarity for r in rows) / len(rows)
        if mean < minimum:
            continue
        # Longer first, then the higher mean. An equal score keeps the
        # smaller transposition, so an untransposed copy reports 0.
        rank = (len(rows), mean, -abs(shift))
        if best is None or rank > best[0]:
            best = (rank, rows, mean, shift)
    if best is None:
        return None
    return best[1], best[2], best[3]


def _overlaps(a: PhraseMatch, b: PhraseMatch) -> bool:
    return a.bar_a < b.bar_a + b.bars and b.bar_a < a.bar_a + a.bars


def _suppress(matches: list) -> list:
    """Same-lag matches that cover the same bars collapse to the longer,
    higher-scoring one, so a window slid one bar into the next section does
    not survive beside the phrase it overlaps. A third copy is a different
    lag and is kept, which is how AABA holds both returns of A."""
    matches.sort(key=lambda m: (m.bars, m.similarity), reverse=True)
    kept = []
    for match in matches:
        lag = match.bar_b - match.bar_a
        if any(prior.bar_b - prior.bar_a == lag and _overlaps(prior, match) for prior in kept):
            continue
        kept.append(match)
    kept.sort(key=lambda m: (m.bar_a, m.bar_b, -m.bars))
    return kept


def find_phrases(
    notes: list,
    track: int,
    tpb: int,
    start: int,
    min_bars: int = 2,
    max_bars: int = 8,
    min_similarity: float = 0.75,
    allow_transposition: bool = False,
) -> list:
    """Phrase pairs on `track` from `start`. At most 512 bars are read.
    Ranges that contain no notes are not reported."""
    bar_ticks = BEATS_PER_BAR * tpb
    step = tpb * 4 // STEPS
    if bar_ticks <= 0 or step <= 0:
        return []
    mine = [n for n in notes if n.track == track and n.start >= start]
    if not mine:
        return []
    n_bars = min(MAX_SCAN, (max(n.start for n in mine) - start) // bar_ticks + 1)
    prints = [bar_fingerprint(mine, start + i * bar_ticks, bar_ticks, step) for i in range(n_bars)]
    rarity = pitch_class_rarity(prints)
    absolute = not allow_transposition
    first_bar = start // bar_ticks + 1
    found = []
    for i in range(n_bars):
        for j in range(i + min_bars, n_bars):
            grown = _passage(prints, rarity, i, j, max_bars, min_similarity, absolute)
            if grown is None:
                continue
            rows, mean, shift = grown
            if len(rows) < min_bars:
                continue
            if not any(prints[i + k].pitches or prints[j + k].pitches for k in range(len(rows))):
                continue
            confident = sum(1 for row in rows if row.similarity >= min_similarity) / len(rows)
            found.append(PhraseMatch(
                track,
                first_bar + i,
                start + i * bar_ticks,
                first_bar + j,
                start + j * bar_ticks,
                len(rows),
                len(rows) * bar_ticks,
                mean,
                confident,
                shift,
                rows,
            ))
    return _suppress(found)


def write_phrases(matches: list, phrases_csv: Path, alignments_csv: Path, track_name: str) -> None:
    """One row per pair, and one row per bar of each pair. The MIDI file is
    not involved."""
    with phrases_csv.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["track", "bar_a", "tick_a", "bar_b", "tick_b", "bars", "ticks", "similarity", "confidence", "transposition"])
        for m in matches:
            w.writerow([track_name, m.bar_a, m.tick_a, m.bar_b, m.tick_b, m.bars, m.ticks, f"{m.similarity:.3f}", f"{m.confidence:.3f}", m.transposition])
    with alignments_csv.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["track", "bar_a", "bar_b", "offset", "similarity", "status", "transposition", "only_left", "only_right"])
        for m in matches:
            for row in m.alignment:
                w.writerow([
                    track_name, m.bar_a, m.bar_b, row.offset, f"{row.similarity:.3f}", row.status, m.transposition,
                    " ".join(str(p) for p in row.only_left), " ".join(str(p) for p in row.only_right),
                ])


def run_phrases(args) -> int:
    """Read `midi`, write phrases.csv and alignments.csv, print the pairs.
    The MIDI file is not modified."""
    source = args.midi.expanduser()
    midi = mido.MidiFile(source)
    exclude = {t.strip() for t in args.exclude.split(",") if t.strip()}
    names = {i: next((m.name.strip() for m in t if m.type == "track_name"), "") for i, t in enumerate(midi.tracks)}
    wanted = [i for i, name in names.items() if name == args.track]
    if not wanted:
        raise SystemExit(f"no track named {args.track}")
    if len(wanted) > 1:
        raise SystemExit(f"more than one track named {args.track}")
    tpb = midi.ticks_per_beat
    bar = BEATS_PER_BAR * tpb
    start = (args.from_bar - 1) * bar if args.from_bar else steady_start_tick(midi)
    matches = find_phrases(
        _grid_notes(midi, exclude), wanted[0], tpb, start,
        args.min_bars, args.max_bars, args.min_similarity, args.allow_transposition,
    )
    out = (args.out_dir or source.parent).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    write_phrases(matches, out / "phrases.csv", out / "alignments.csv", args.track)
    print(f"phrases: {len(matches)}")
    for m in matches:
        print(
            f"bar {m.bar_a}-{m.bar_a + m.bars - 1} ~ bar {m.bar_b}-{m.bar_b + m.bars - 1} "
            f"({m.bars} bars, similarity {m.similarity:.3f}, confidence {m.confidence:.3f}, shift {m.transposition:+d})"
        )
    print(f"written: {out / 'phrases.csv'}")
    return 0
