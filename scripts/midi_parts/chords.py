"""Chord names, detection, and rebuilding a chord track."""

from __future__ import annotations

import csv
import math
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional

import mido
import numpy as np

from midi_parts.models import (
    DRUM_CHANNEL,
    GHOST,
)
from midi_parts.midi_io import (
    _paired_notes,
    _tempo_map,
    _ticks,
    mmss,
)
from midi_parts.audio import (
    CHORD_HOP,
    audio_chroma,
    audio_offset,
    blend_chroma,
    chroma_frames,
)



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
    from midi_parts.key import _note_rows, detect_key

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
