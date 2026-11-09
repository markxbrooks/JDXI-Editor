"""Note-by-note accuracy of a transcription against a ground-truth MIDI.

For when the right notes are known: a MIDI file rendered to audio and
transcribed (a round-trip test), or a hand-made sequence already in the
recording's time. Unlike `roundtrip`, which compares pitch content with the
audio and can't see octave errors, octave doublings or small timing errors,
this counts notes.

A transcribed note matches a reference note when it has the same pitch and
starts within `tolerance` (50 ms, as in MIREX). Matching is one to one. Both
files are first lined up by the global offset (searched within
`max_offset`) that matches most notes: Basic Pitch starts notes about 30 ms
late.

Reported: precision (share of transcribed notes that are right), recall
(share of reference notes found) and F; F when note ends must also match
(within 20% of the length or the tolerance); F forgiving octave errors;
frame F (sounding pitches every 10 ms); recall per reference part; and what
the wrong notes are (an octave or fifth above a reference note sounding at
the time, which is an overtone; a semitone off; or other).

The reference's time 0 must be the transcription's time 0 (within
max_offset). For a sequence in its own tempo, such as one used with
`classify --reference`, use classify's reference recall instead.
"""

from __future__ import annotations

import bisect
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

import numpy as np

from midi_parts.midi_io import _paired_notes
from midi_parts.models import DRUM_CHANNEL, GHOST

TOLERANCE = 0.05  # seconds either way for an onset to match
FRAME = 0.01  # seconds per frame for frame F
UNISON = 0.01  # reference notes of one pitch closer than this are one note


@dataclass(frozen=True)
class TNote:
    start: float
    end: float
    pitch: int
    part: str = ""


@dataclass
class Accuracy:
    notes: int  # transcribed notes scored
    reference: int  # reference notes scored
    offset: float  # seconds added to the transcription to line it up
    precision: float
    recall: float
    f: float
    f_end: float  # ends must match too
    f_octave: float  # any octave of the right pitch class
    frame_f: float
    recall_by_part: dict[str, tuple[int, int]] = field(default_factory=dict)  # part: (found, total)
    wrong: Counter = field(default_factory=Counter)  # kind of unmatched transcribed note: count


def load_notes(path: Path, exclude: tuple[str, ...] = (GHOST,), drums: bool = False) -> list[TNote]:
    """Pitched notes of a MIDI file, labelled by track name (else channel)."""
    out = []
    for start, end, pitch, _velocity, channel, name in _paired_notes(path):
        if channel == DRUM_CHANNEL and not drums:
            continue
        if name in exclude:
            continue
        out.append(TNote(start, end, pitch, name or f"channel {channel + 1}"))
    return out


def dedupe(notes: list[TNote], gap: float = UNISON) -> list[TNote]:
    """Drop a note when the previous note of the same pitch starts less than
    `gap` earlier (two parts doubling a note sound as one)."""
    out, last = [], {}
    for n in sorted(notes, key=lambda n: (n.start, n.pitch)):
        if n.pitch in last and n.start - last[n.pitch] < gap:
            continue
        last[n.pitch] = n.start
        out.append(n)
    return out


def match_notes(
    reference: list[TNote],
    transcription: list[TNote],
    offset: float = 0.0,
    tolerance: float = TOLERANCE,
    key: Callable[[int], int] = lambda p: p,
    with_end: bool = False,
) -> list[tuple[int, int]]:
    """One-to-one (reference index, transcription index) pairs: same key(pitch),
    onsets within tolerance after adding offset to the transcription, the
    nearest unused one for each reference note in time order."""
    by_key: dict[int, list[tuple[float, float, int]]] = defaultdict(list)
    for j, n in enumerate(transcription):
        by_key[key(n.pitch)].append((n.start + offset, n.end + offset, j))
    for candidates in by_key.values():
        candidates.sort()
    used: set[int] = set()
    pairs = []
    for i in sorted(range(len(reference)), key=lambda i: reference[i].start):
        r = reference[i]
        candidates = by_key.get(key(r.pitch), [])
        k = bisect.bisect_left(candidates, (r.start - tolerance, -1.0, -1))
        best = None
        while k < len(candidates) and candidates[k][0] <= r.start + tolerance:
            start, end, j = candidates[k]
            if j not in used and (not with_end or abs(end - r.end) <= max(tolerance, 0.2 * (r.end - r.start))):
                if best is None or abs(start - r.start) < abs(best[0] - r.start):
                    best = (start, j)
            k += 1
        if best is not None:
            used.add(best[1])
            pairs.append((i, best[1]))
    return pairs


def best_offset(
    reference: list[TNote], transcription: list[TNote], max_offset: float = 0.1, step: float = 0.005, tolerance: float = TOLERANCE
) -> float:
    """The offset (multiple of step within +-max_offset) matching most notes
    (the one nearest 0 on a tie), then moved by the median onset difference
    of the notes it matches, if that matches within 0.5% as many. A delay well inside the
    tolerance matches as many notes at 0, but still needs removing for note
    ends and frames; and on a plateau of equal counts, the median finds the
    middle rather than an edge."""
    if max_offset <= 0:
        return 0.0
    count = int(round(max_offset / step))
    offsets = sorted((k * step for k in range(-count, count + 1)), key=abs)
    hits = {o: len(match_notes(reference, transcription, o, tolerance)) for o in offsets}
    coarse = max(offsets, key=lambda o: hits[o])  # first maximum: nearest 0
    pairs = match_notes(reference, transcription, coarse, tolerance)
    if not pairs:
        return coarse
    fine = float(np.median([reference[i].start - transcription[j].start for i, j in pairs]))
    return fine if len(match_notes(reference, transcription, fine, tolerance)) >= 0.995 * len(pairs) else coarse


def _f(hits: int, reference: int, transcription: int) -> tuple[float, float, float]:
    p = hits / transcription if transcription else 0.0
    r = hits / reference if reference else 0.0
    return p, r, (2 * p * r / (p + r) if p + r else 0.0)


def frame_f(reference: list[TNote], transcription: list[TNote], offset: float = 0.0, frame: float = FRAME) -> float:
    """F of the (frame, pitch) cells where each file sounds a note."""
    if not reference or not transcription:
        return 0.0
    end = max(max(n.end for n in reference), max(n.end + offset for n in transcription))
    length = int(end / frame) + 2

    def roll(notes, shift):
        m = np.zeros((length, 128), dtype=bool)
        for n in notes:
            a = max(0, int((n.start + shift) / frame))
            m[a : max(a + 1, int((n.end + shift) / frame)), n.pitch] = True
        return m

    a, b = roll(reference, 0.0), roll(transcription, offset)
    total = int(a.sum() + b.sum())
    return 2 * int((a & b).sum()) / total if total else 0.0


def wrong_kind(n: TNote, reference: list[TNote], starts: list[float], offset: float, tolerance: float = TOLERANCE) -> str:
    """Why a transcribed note matched nothing: 'overtone' (an octave, twelfth
    or two octaves above a reference note sounding at its start), 'octave
    below', 'semitone' (one off a reference note starting with it), or 'other'."""
    t = n.start + offset
    k = bisect.bisect_right(starts, t + tolerance)
    sounding, starting = set(), set()
    for r in reference[max(0, k - 400) : k]:
        if r.start - tolerance <= t < r.end:
            sounding.add(r.pitch)
            if abs(r.start - t) <= tolerance:
                starting.add(r.pitch)
    if any(n.pitch - d in sounding for d in (12, 19, 24)):
        return "overtone"
    if any(n.pitch + d in sounding for d in (12, 24)):
        return "octave below"
    if n.pitch - 1 in starting or n.pitch + 1 in starting:
        return "semitone"
    return "other"


def accuracy(
    reference: list[TNote],
    transcription: list[TNote],
    offset: Optional[float] = None,
    max_offset: float = 0.1,
    tolerance: float = TOLERANCE,
    start: float = 0.0,
    end: Optional[float] = None,
) -> Accuracy:
    """Score the transcription against the reference (see the module doc).
    start/end (reference seconds) limit both files."""
    if offset is None:
        offset = best_offset(reference, transcription, max_offset, tolerance=tolerance)

    def inside(t: float, slack: float = 0.0) -> bool:
        return t >= start - slack and (end is None or t < end + slack)

    ref = [n for n in reference if inside(n.start)]
    # a transcribed note may start up to the tolerance outside the window
    est = [n for n in transcription if inside(n.start + offset, tolerance)]
    pairs = match_notes(ref, est, offset, tolerance)
    p, r, f = _f(len(pairs), len(ref), len(est))
    f_end = _f(len(match_notes(ref, est, offset, tolerance, with_end=True)), len(ref), len(est))[2]
    f_octave = _f(len(match_notes(ref, est, offset, tolerance, key=lambda q: q % 12)), len(ref), len(est))[2]
    found = {i for i, _ in pairs}
    by_part: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for i, n in enumerate(ref):
        by_part[n.part][1] += 1
        by_part[n.part][0] += i in found
    matched = {j for _, j in pairs}
    ordered = sorted(ref, key=lambda n: n.start)
    starts = [n.start for n in ordered]
    wrong = Counter(wrong_kind(n, ordered, starts, offset, tolerance) for j, n in enumerate(est) if j not in matched)
    return Accuracy(
        notes=len(est),
        reference=len(ref),
        offset=offset,
        precision=p,
        recall=r,
        f=f,
        f_end=f_end,
        f_octave=f_octave,
        frame_f=frame_f(ref, est, offset),
        recall_by_part={k: (v[0], v[1]) for k, v in by_part.items()},
        wrong=wrong,
    )


def run_accuracy(args) -> int:
    exclude = tuple(x.strip() for x in args.exclude.split(",") if x.strip())
    reference = load_notes(args.reference.expanduser(), exclude, drums=args.drums)
    if not args.keep_unisons:
        reference = dedupe(reference)
    if not reference:
        print(f"{args.reference}: no pitched notes")
        return 1
    parts = Counter(n.part for n in reference)
    print(f"reference: {args.reference.name}, {len(reference)} notes ({', '.join(f'{k} {v}' for k, v in parts.most_common())})")
    print(f"a note is right with the same pitch starting within {args.tolerance * 1000:.0f} ms, after the offset")
    names = [k for k, _ in parts.most_common()]
    width = max(24, *(len(p.stem[:40]) for p in args.midi))
    print(f"\n{'transcription':{width}}  notes  offset |   P     R     F  | F end | F octave | frame F")
    results = []
    for path in args.midi:
        est = load_notes(path.expanduser(), exclude, drums=args.drums)
        if not args.keep_unisons:
            est = dedupe(est)
        res = accuracy(reference, est, args.offset, args.max_offset, args.tolerance, args.start, args.end)
        results.append((path, res))
        print(
            f"{path.stem[:40]:{width}} {res.notes:6} {res.offset * 1000:+5.0f}ms"
            f" | {res.precision:.2f}  {res.recall:.2f}  {res.f:.2f} |  {res.f_end:.2f} |   {res.f_octave:.2f}   |  {res.frame_f:.2f}"
        )
    print(f"\nrecall by reference part:\n{'':{width}} " + " ".join(f"{n[:10]:>10}" for n in names))
    for path, res in results:
        cells = []
        for n in names:
            found, total = res.recall_by_part.get(n, (0, 0))
            cells.append(f"{found / total:10.0%}" if total else f"{'-':>10}")
        print(f"{path.stem[:40]:{width}} " + " ".join(cells))
    kinds = ("overtone", "octave below", "semitone", "other")
    print(f"\nwrong notes (share of transcribed notes):\n{'':{width}} " + " ".join(f"{k:>12}" for k in kinds))
    for path, res in results:
        print(f"{path.stem[:40]:{width}} " + " ".join(f"{res.wrong[k] / max(res.notes, 1):12.0%}" for k in kinds))
    print("\nP: share of transcribed notes that are right; R: share of reference notes found; F: their balance.")
    print("F end: ends must match too; F octave: any octave of the right note; frame F: sounding pitches every 10 ms.")
    print("overtone: an octave, twelfth or two octaves above a reference note sounding then.")
    return 0
