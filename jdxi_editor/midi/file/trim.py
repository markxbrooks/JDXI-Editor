"""
Trim a MIDI file, or one of its tracks, to a range of ticks.

- trim_midi_file: keep [start, end) of every track and move it to the start
  of the file. The tempo, time signature, programs, controllers and SysEx in
  force at *start* are kept at tick 0, so the excerpt sounds as it did in place.
- trim_track: remove a track's notes outside [start, end) and leave its timing
  and other events as they were, so it stays in step with the other tracks.

Notes that begin before *start* are dropped; notes still sounding at *end* are
released there.
"""

from __future__ import annotations

from collections import defaultdict, deque
from typing import Iterable, Optional

import mido

from picomidi.message.type import MidoMessageType, MidoMetaMessageType

Event = tuple[int, mido.Message]  # (absolute tick, message)

# Meta events whose latest value before the cut still applies after it
_STATE_META = {
    MidoMetaMessageType.SET_TEMPO.value,
    MidoMetaMessageType.TIME_SIGNATURE.value,
    "key_signature",
    MidoMetaMessageType.TRACK_NAME.value,
    "instrument_name",
    "copyright",
    "midi_port",
    "channel_prefix",
}
_END_OF_TRACK = MidoMetaMessageType.END_OF_TRACK.value


def _is_note_on(msg: mido.Message) -> bool:
    return msg.type == MidoMessageType.NOTE_ON.value and msg.velocity > 0


def _is_note_off(msg: mido.Message) -> bool:
    return msg.type == MidoMessageType.NOTE_OFF.value or (
        msg.type == MidoMessageType.NOTE_ON.value and msg.velocity == 0
    )


def _is_note(msg: mido.Message) -> bool:
    return _is_note_on(msg) or _is_note_off(msg)


def _absolute(track: mido.MidiTrack) -> list[Event]:
    events, tick = [], 0
    for msg in track:
        tick += msg.time
        events.append((tick, msg))
    return events


def _to_track(events: Iterable[Event], end_tick: int) -> mido.MidiTrack:
    """A track of *events* (stable-sorted by tick), ending at *end_tick*."""
    track = mido.MidiTrack()
    previous = 0
    for tick, msg in sorted(events, key=lambda event: event[0]):
        track.append(msg.copy(time=tick - previous))
        previous = tick
    track.append(mido.MetaMessage(_END_OF_TRACK, time=max(0, end_tick - previous)))
    return track


def _notes_in_range(events: list[Event], start: int, end: int) -> list[Event]:
    """
    The note-ons of *events* in [start, end) with their note-offs, a note-off
    after *end* moved to *end*. Other events are left out.
    """
    sounding: dict[tuple[int, int], deque[bool]] = defaultdict(deque)
    kept: list[Event] = []
    for tick, msg in events:
        if _is_note_on(msg):
            keep = start <= tick < end
            sounding[(msg.channel, msg.note)].append(keep)
            if keep:
                kept.append((tick, msg))
        elif _is_note_off(msg):
            starts = sounding[(msg.channel, msg.note)]
            # A note-off with no note-on before it is dropped
            if starts and starts.popleft():
                kept.append((min(tick, end), msg))
    # Kept notes the track never releases end at *end*
    for (channel, note), starts in sounding.items():
        for keep in starts:
            if keep:
                off = mido.Message(
                    MidoMessageType.NOTE_OFF.value, channel=channel, note=note
                )
                kept.append((end, off))
    return kept


def _state_key(index: int, msg: mido.Message) -> Optional[tuple]:
    """
    What *msg* sets, if it is state to carry over a cut: a later message with
    the same key replaces it. None for events that only matter where they are.
    """
    if msg.is_meta:
        return ("meta", msg.type) if msg.type in _STATE_META else None
    if msg.type == MidoMessageType.PROGRAM_CHANGE.value:
        return ("program", msg.channel)
    if msg.type == MidoMessageType.CONTROL_CHANGE.value:
        return ("control", msg.channel, msg.control)
    if msg.type == MidoMessageType.PITCH_WHEEL.value:
        return ("pitch", msg.channel)
    if msg.type == MidoMessageType.SYSEX.value:
        return ("sysex", index)  # every SysEx (synth setup) is kept
    return None


def _check_range(start: int, end: int) -> None:
    if start < 0 or end <= start:
        raise ValueError(f"Invalid trim range {start}-{end} ticks")


def trim_track(track: mido.MidiTrack, start: int, end: int) -> mido.MidiTrack:
    """
    *track* with only the notes that begin in [start, end) (ticks), at the
    same times; its other events and its length are unchanged.
    """
    _check_range(start, end)
    events = _absolute(track)
    track_end = events[-1][0] if events else 0
    others = [
        (tick, msg)
        for tick, msg in events
        if not _is_note(msg) and msg.type != _END_OF_TRACK
    ]
    trimmed = _to_track(others + _notes_in_range(events, start, end), track_end)
    return trimmed


def trim_midi_file(midi_file: mido.MidiFile, start: int, end: int) -> mido.MidiFile:
    """
    A new file holding [start, end) (ticks) of *midi_file*, moved to tick 0.
    """
    _check_range(start, end)
    trimmed = mido.MidiFile(
        type=midi_file.type, ticks_per_beat=midi_file.ticks_per_beat
    )
    for track in midi_file.tracks:
        events = _absolute(track)
        state: dict[tuple, tuple[int, mido.Message]] = {}
        body: list[Event] = []
        for index, (tick, msg) in enumerate(events):
            if _is_note(msg) or msg.type == _END_OF_TRACK:
                continue
            if tick < start:
                key = _state_key(index, msg)
                if key is not None:
                    state[key] = (index, msg)
            elif tick < end:
                body.append((tick - start, msg))
        # The state in force at *start*, in its original order (bank select
        # stays ahead of its program change)
        carried = [(0, msg) for _, msg in sorted(state.values(), key=lambda s: s[0])]
        notes = [
            (tick - start, msg) for tick, msg in _notes_in_range(events, start, end)
        ]
        trimmed.tracks.append(_to_track(carried + body + notes, end - start))
    return trimmed
