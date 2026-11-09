"""Combine independent transcriptions of one recording."""

from __future__ import annotations

import bisect
from collections import defaultdict
from pathlib import Path

import mido

from midi_parts.models import Note
from midi_parts.midi_io import (
    _seconds,
    _tempo_map,
    load_transcription,
)
from midi_parts.classification import merge_fragments



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
