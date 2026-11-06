"""
Midi Widget Utils
"""

import bisect
from typing import Callable

import mido
from mido import MidiFile
from PySide6.QtGui import QColor

from picomidi import Midi, MidiTempo
from picomidi.message.type import MidoMessageType


def ticks_to_seconds(ticks: int, tempo: int, ticks_per_beat: int) -> float:
    """
    Convert MIDI ticks to seconds.
    :param ticks: int
    :param tempo: int (μs per quarter note)
    :param ticks_per_beat: int
    :return: float
    """
    return (tempo / float(MidiTempo.MICROSECONDS_PER_SECOND)) * (ticks / ticks_per_beat)


def get_total_duration_in_seconds(midi_file: MidiFile) -> float:
    """
    get_total_duration_in_seconds

    :param midi_file: MidiFile
    :return: float
    """
    ticks_per_beat = midi_file.ticks_per_beat
    current_tempo = Midi.tempo.BPM_120_USEC  # default: 120 BPM
    time_seconds = 0
    last_tick = 0

    # Collect all events with absolute ticks
    events = []
    for track in midi_file.tracks:
        abs_tick = 0
        for msg in track:
            abs_tick += msg.time
            events.append((abs_tick, msg))

    # Sort all events by tick
    events.sort(key=lambda x: x[0])

    for abs_tick, msg in events:
        delta_ticks = abs_tick - last_tick
        time_seconds += (current_tempo / MidiTempo.MICROSECONDS_PER_SECOND) * (
            delta_ticks / ticks_per_beat
        )
        last_tick = abs_tick

        if msg.type == MidoMessageType.SET_TEMPO.value:
            current_tempo = msg.tempo

    return time_seconds


def build_tick_to_seconds(midi_file: MidiFile) -> Callable[[int], float]:
    """
    Build a tick → seconds converter using the file-wide tempo map.

    In Type 1 files tempo changes usually live in track 0 only, so every
    track must be timed with the merged map to line up with playback.

    :param midi_file: MidiFile
    :return: Callable taking an absolute tick and returning seconds
    """
    ticks_per_beat = midi_file.ticks_per_beat
    tempo_changes = {0: Midi.tempo.BPM_120_USEC}
    for track in midi_file.tracks:
        abs_tick = 0
        for msg in track:
            abs_tick += msg.time
            if msg.type == MidoMessageType.SET_TEMPO.value:
                tempo_changes[abs_tick] = msg.tempo

    seg_ticks: list[int] = []
    seg_seconds: list[float] = []
    seg_tempos: list[int] = []
    seconds = 0.0
    for tick in sorted(tempo_changes):
        if seg_ticks:
            seconds += ticks_to_seconds(tick - seg_ticks[-1], seg_tempos[-1], ticks_per_beat)
        seg_ticks.append(tick)
        seg_seconds.append(seconds)
        seg_tempos.append(tempo_changes[tick])

    def tick_to_seconds(tick: int) -> float:
        idx = max(0, bisect.bisect_right(seg_ticks, tick) - 1)
        return seg_seconds[idx] + ticks_to_seconds(
            tick - seg_ticks[idx], seg_tempos[idx], ticks_per_beat
        )

    return tick_to_seconds


def extract_notes_with_absolute_time(
    track: mido.MidiTrack, tempo: int, ticks_per_beat: int
) -> list:
    """
    Extract notes with absolute time from a MIDI track

    :param track: mido.MidiTrack
    :param tempo: int
    :param ticks_per_beat: int
    :return: list
    """
    notes = []
    current_time = 0
    for msg in track:
        current_time += msg.time
        if msg.type == MidoMessageType.NOTE_ON.value:
            abs_time = mido.tick2second(current_time, ticks_per_beat, tempo)
            notes.append((abs_time, msg))
    return notes


def generate_track_colors(n: int) -> list[str]:
    """
    Generate visually distinct colors for up to n tracks.

    :param n: int Number of tracks
    :return:
    """
    return [
        QColor.fromHsvF(i / max(1, n), 0.7, 0.9)  # HSV for distinct hues
        for i in range(n)
    ]


def get_first_channel(track: mido.MidiTrack) -> int | None:
    """
    Get the first channel from a MIDI track.

    :param track: mido.MidiTrack
    :return: int | None
    """
    for msg in track:
        if msg.type in {
            MidoMessageType.NOTE_ON.value,
            MidoMessageType.NOTE_OFF.value,
            MidoMessageType.CONTROL_CHANGE.value,
            MidoMessageType.PROGRAM_CHANGE.value,
        } and hasattr(msg, "channel"):
            return msg.channel
    return 0  # default fallback
