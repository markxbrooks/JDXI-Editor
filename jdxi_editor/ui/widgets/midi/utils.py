"""
Midi Widget Utils
"""

import mido
from mido import MidiFile
from PySide6.QtGui import QColor

from picomidi.message.type import MidoMessageType


def ticks_to_seconds(ticks: int, tempo: int, ticks_per_beat: int) -> float:
    """
    Convert MIDI ticks to seconds.
    :param ticks: int
    :param tempo: int (μs per quarter note)
    :param ticks_per_beat: int
    :return: float
    """
    return (tempo / 1_000_000.0) * (ticks / ticks_per_beat)


def get_total_duration_in_seconds(midi_file: MidiFile) -> float:
    """
    get_total_duration_in_seconds

    :param midi_file: MidiFile
    :return: float
    """
    ticks_per_beat = midi_file.ticks_per_beat
    current_tempo = 500_000  # default: 120 BPM
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
        time_seconds += (current_tempo / 1_000_000) * (delta_ticks / ticks_per_beat)
        last_tick = abs_tick

        if msg.type == MidoMessageType.SET_TEMPO:
            current_tempo = msg.tempo

    return time_seconds


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
        if msg.type == MidoMessageType.NOTE_ON:
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
            MidoMessageType.NOTE_ON,
            MidoMessageType.NOTE_OFF,
            MidoMessageType.CONTROL_CHANGE,
            MidoMessageType.PROGRAM_CHANGE,
        } and hasattr(msg, "channel"):
            return msg.channel
    return 0  # default fallback
