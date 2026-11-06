"""
Pattern importer

Reads a MIDI file into step-sequencer notes. Used both for "Load Pattern" and
for loading the MIDI File Player's file, so both behave the same:

- every track is read; notes are mapped to rows by MIDI channel
- note starts are rounded to the nearest 16th-note step
- note lengths and velocities are kept (lengths in steps, from the note-offs)
- notes that start on the same step of a row (chords, simultaneous drum
  hits) are all kept, in file order; the first is the step's main note
- what cannot be represented is counted, not silently lost: notes on other
  channels, the same note starting twice on one step, and tempo changes
  after the first

The inverse of jdxi_editor.midi.pattern.compiler.compile_pattern for files it
produced.
"""

import math
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Optional

from mido import MidiFile, tempo2bpm

STEPS_PER_BEAT = 4
DEFAULT_STEPS_PER_BAR = 16


def _count(n: int, noun: str) -> str:
    return f"{n} {noun}" if n == 1 else f"{n} {noun}s"


@dataclass(frozen=True)
class ImportedNote:
    """A note placed on the step grid."""

    bar: int
    step: int
    row: int
    note: int
    velocity: int
    duration_steps: float


@dataclass
class PatternImport:
    """Result of reading a MIDI file into the step grid."""

    bars: int
    bpm: Optional[float]
    ticks_per_beat: int
    notes: list[ImportedNote] = field(default_factory=list)
    dropped_overlapping: int = 0  # same note starting again on the same step
    dropped_channels: dict[int, int] = field(default_factory=dict)  # channel -> notes
    tempo_changes_ignored: int = 0

    @property
    def dropped_total(self) -> int:
        return self.dropped_overlapping + sum(self.dropped_channels.values())

    def summary(self) -> str:
        """One line describing what was imported and what was not."""
        parts = [
            f"Imported {_count(len(self.notes), 'note')} in {_count(self.bars, 'bar')}"
        ]
        if self.dropped_overlapping:
            parts.append(
                f"{_count(self.dropped_overlapping, 'repeated note')} on the same step "
                "not imported"
            )
        if self.dropped_channels:
            channels = ", ".join(
                f"Ch {ch + 1} ({count})" for ch, count in sorted(self.dropped_channels.items())
            )
            parts.append(f"notes on channels without a row not imported: {channels}")
        if self.tempo_changes_ignored:
            parts.append(
                f"{_count(self.tempo_changes_ignored, 'tempo change')} ignored "
                "(pattern uses one tempo)"
            )
        return "; ".join(parts)


def import_pattern(
    midi_file: MidiFile,
    channel_to_row: dict[int, int],
    steps_per_bar: int = DEFAULT_STEPS_PER_BAR,
) -> PatternImport:
    """
    Place the notes of *midi_file* on the step grid.

    :param midi_file: File to read
    :param channel_to_row: 0-based MIDI channel -> sequencer row
    :param steps_per_bar: Steps per bar (16 for 4/4, 12 for 3/4)
    :return: PatternImport with notes and a count of what was left out
    """
    ticks_per_step = midi_file.ticks_per_beat / STEPS_PER_BEAT
    events = []  # (tick, order, msg) merged across tracks, file order within a tick
    order = 0
    for track in midi_file.tracks:
        tick = 0
        for msg in track:
            tick += msg.time
            events.append((tick, order, msg))
            order += 1
    events.sort(key=lambda item: (item[0], item[1]))

    tempos = [msg.tempo for _, _, msg in events if msg.type == "set_tempo"]
    distinct_tempos = list(dict.fromkeys(tempos))
    last_tick = max((t for t, _, m in events if not m.is_meta), default=0)

    # Pair note-ons with note-offs per (channel, note), first in first out
    open_notes: dict[tuple[int, int], deque] = defaultdict(deque)
    lengths: dict[int, int] = {}  # order of note_on -> length in ticks
    starts = []  # (tick, order, msg)
    for tick, idx, msg in events:
        if msg.type == "note_on" and msg.velocity > 0:
            open_notes[(msg.channel, msg.note)].append((tick, idx))
            starts.append((tick, idx, msg))
        elif msg.type in ("note_off", "note_on"):
            pending = open_notes.get((msg.channel, msg.note))
            if pending:
                on_tick, on_idx = pending.popleft()
                lengths[on_idx] = tick - on_tick

    result = PatternImport(
        bars=1,
        bpm=tempo2bpm(distinct_tempos[0]) if distinct_tempos else None,
        ticks_per_beat=midi_file.ticks_per_beat,
        tempo_changes_ignored=max(0, len(distinct_tempos) - 1),
    )
    dropped_channels: dict[int, int] = defaultdict(int)
    used: set[tuple[int, int, int, int]] = set()  # (row, bar, step, note)
    last_bar = 0
    for tick, idx, msg in starts:
        row = channel_to_row.get(msg.channel)
        if row is None:
            dropped_channels[msg.channel] += 1
            continue
        global_step = round(tick / ticks_per_step)
        bar, step = divmod(global_step, steps_per_bar)
        if (row, bar, step, msg.note) in used:
            result.dropped_overlapping += 1
            continue
        used.add((row, bar, step, msg.note))
        length_ticks = lengths.get(idx)
        duration_steps = (
            round(length_ticks / ticks_per_step, 3) if length_ticks else 1.0
        )
        result.notes.append(
            ImportedNote(
                bar=bar,
                step=step,
                row=row,
                note=msg.note,
                velocity=msg.velocity,
                duration_steps=max(duration_steps, 0.001),
            )
        )
        last_bar = max(last_bar, bar)

    ticks_per_bar = ticks_per_step * steps_per_bar
    result.bars = max(1, math.ceil(last_tick / ticks_per_bar), last_bar + 1)
    result.dropped_channels = dict(dropped_channels)
    return result
