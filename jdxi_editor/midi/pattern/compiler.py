"""
Pattern compiler

Turns a step pattern into a mido.MidiFile. The same file is played by the
shared TransportController and written by Save, so what you hear is what is
saved, and a saved pattern sounds the same in the MIDI File Player.

The file is Type 1:
- track 0: tempo, time signature
- one track per pattern row (named, notes on the row's channel)
Every track ends exactly at the end of the last bar, so looping the file
repeats whole bars with no gap.

Example:
    >>> spec = PatternSpec(bars=1, steps_per_bar=16, bpm=120,
    ...                    rows=[PatternRow("Digital Synth 1", channel=0)],
    ...                    notes=[PatternNote(bar=0, step=0, row=0, note=60,
    ...                                       velocity=100, duration_ticks=120)])
    >>> compile_pattern(spec).length
    2.0
"""

from dataclasses import dataclass, field
from typing import Optional

from mido import Message, MetaMessage, MidiFile, MidiTrack, bpm2tempo

DEFAULT_TICKS_PER_BEAT = 480
STEPS_PER_BEAT = 4  # 16th-note steps
TIME_SIGNATURE_DENOMINATOR = 4
MIN_VELOCITY = 1  # velocity 0 would be read as a note-off
MAX_VELOCITY = 127


@dataclass(frozen=True)
class PatternRow:
    """A sequencer row: its track name and MIDI channel (0-15)."""

    name: str
    channel: int


@dataclass(frozen=True)
class PatternNote:
    """One active step."""

    bar: int
    step: int  # step within the bar (16th notes)
    row: int
    note: int
    velocity: int
    duration_ticks: int


@dataclass
class PatternSpec:
    """Everything needed to compile a pattern."""

    bars: int
    steps_per_bar: int
    bpm: float
    rows: list[PatternRow]
    notes: list[PatternNote] = field(default_factory=list)
    ticks_per_beat: int = DEFAULT_TICKS_PER_BEAT

    @property
    def ticks_per_step(self) -> int:
        return self.ticks_per_beat // STEPS_PER_BEAT

    @property
    def ticks_per_bar(self) -> int:
        return self.ticks_per_step * self.steps_per_bar

    @property
    def length_ticks(self) -> int:
        return self.ticks_per_bar * max(1, self.bars)

    def step_tick(self, bar: int, step: int) -> int:
        """Absolute tick of *step* in *bar*."""
        return bar * self.ticks_per_bar + step * self.ticks_per_step


def compile_pattern(spec: PatternSpec) -> MidiFile:
    """
    Compile *spec* to a Type 1 MIDI file.

    - Velocities are clamped to 1–127.
    - Notes are clipped at the pattern end, and where the same note on the
      same row starts again, so a long note never cuts off its successor.
    - A note-off sorts before a note-on at the same tick.
    """
    midi_file = MidiFile(type=1, ticks_per_beat=spec.ticks_per_beat)
    midi_file.tracks.append(_conductor_track(spec))

    notes_by_row: dict[int, list[PatternNote]] = {}
    for note in spec.notes:
        if 0 <= note.row < len(spec.rows) and 0 <= note.step < spec.steps_per_bar:
            notes_by_row.setdefault(note.row, []).append(note)

    for row_index, row in enumerate(spec.rows):
        midi_file.tracks.append(
            _row_track(spec, row, notes_by_row.get(row_index, []))
        )
    return midi_file


def _conductor_track(spec: PatternSpec) -> MidiTrack:
    track = MidiTrack()
    track.append(MetaMessage("track_name", name="Pattern", time=0))
    track.append(MetaMessage("set_tempo", tempo=bpm2tempo(spec.bpm), time=0))
    numerator = max(1, spec.steps_per_bar // STEPS_PER_BEAT)
    track.append(
        MetaMessage(
            "time_signature",
            numerator=numerator,
            denominator=TIME_SIGNATURE_DENOMINATOR,
            time=0,
        )
    )
    track.append(MetaMessage("end_of_track", time=spec.length_ticks))
    return track


def _row_track(spec: PatternSpec, row: PatternRow, notes: list[PatternNote]) -> MidiTrack:
    end = spec.length_ticks
    starts = sorted(
        ((spec.step_tick(n.bar, n.step), n) for n in notes if n.bar < spec.bars),
        key=lambda item: item[0],
    )
    # Next start of the same note number, to clip overlapping notes
    next_start: dict[int, Optional[int]] = {}
    timed: list[tuple[int, int, int, Message]] = []  # (tick, off/on, index, message)
    for index, (tick, note) in reversed(list(enumerate(starts))):
        off_tick = min(tick + max(1, note.duration_ticks), end)
        following = next_start.get(note.note)
        if following is not None:
            off_tick = min(off_tick, following)
        next_start[note.note] = tick
        if off_tick <= tick:
            continue  # Another start at the same tick on the same note
        velocity = max(MIN_VELOCITY, min(MAX_VELOCITY, int(note.velocity)))
        timed.append(
            (tick, 1, index, Message("note_on", note=note.note, velocity=velocity, channel=row.channel))
        )
        timed.append(
            (off_tick, 0, index, Message("note_off", note=note.note, velocity=0, channel=row.channel))
        )
    # Note-offs before note-ons at a tick; otherwise the pattern's note order
    timed.sort(key=lambda item: (item[0], item[1], item[2]))

    track = MidiTrack()
    track.append(MetaMessage("track_name", name=row.name, time=0))
    previous = 0
    for tick, _, _, msg in timed:
        track.append(msg.copy(time=tick - previous))
        previous = tick
    track.append(MetaMessage("end_of_track", time=end - previous))
    return track
