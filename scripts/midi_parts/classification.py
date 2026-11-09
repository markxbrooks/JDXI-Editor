"""Clean up a transcription, find sections and lines, and label parts."""

from __future__ import annotations

import bisect
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Optional

import numpy as np

from midi_parts.models import (
    GHOST,
    Grid,
    Note,
    Result,
)
from midi_parts.midi_io import (
    load_reference,
    load_transcription,
    mmss,
    write_csv,
    write_midi,
    write_piano_roll,
)
from midi_parts.alignment import (
    align_reference,
    match_reference,
)

RULE_PARTS = ("Bass", "Chords", "Lead", "Sequence", "High")
GROUP_S = 0.04  # onsets this close count as simultaneous


# --- Stage 1: clean up -------------------------------------------------------


def merge_fragments(notes: list[Note], overlap: float = 0.0005) -> tuple[list[Note], int]:
    """Join a note to the next one of the same pitch when they overlap
    (Basic Pitch restarted a pitch it was still holding). Back-to-back notes
    are kept: in a sequencer part they are repeated notes."""
    # Mutates the kept note's end and velocity in place.
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
    # Mutates note.flag in place.
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
    # Mutates note.line in place.
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
    # Mutates note.poly, lowest, highest, and on_grid in place.
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
    # Mutates note.part and confidence in place.
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
    # Mutates note.confidence and sometimes note.part in place.
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
    # Mutates note.part, confidence, and source in place.
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
    # Mutates note.part, confidence, and source in place.
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
    # Mutates note.section in place.
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
