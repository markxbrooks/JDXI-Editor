"""Align a reference sequence to a transcription and match notes."""

from __future__ import annotations

import bisect
import math
from collections import Counter
from typing import Iterable

import numpy as np

from midi_parts.models import (
    Note,
    RefNote,
)

FRAME_S = 0.25  # alignment frame


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
    # Mutates RefNote.mapped in place.
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
    # Mutates note.part, source, confidence, and flag in place.
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
