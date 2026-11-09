"""Key detection and the optional out-of-key filter."""

from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import mido
import numpy as np

from midi_parts.models import (
    DRUM_CHANNEL,
    Note,
)
from midi_parts.midi_io import (
    _paired_notes,
    _seconds,
    _tempo_map,
    mmss,
)
from midi_parts.classification import find_sections
from midi_parts.chords import (
    CHORD_QUALITIES,
    PITCH_NAMES,
    chord_name,
    parse_chord,
)



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
