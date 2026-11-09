"""Read and write MIDI notes, tempo maps, and classification output files."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import mido
import numpy as np

from midi_parts.models import (
    DRUM_CHANNEL,
    GHOST,
    Note,
    RefNote,
    Result,
)



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
