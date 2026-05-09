"""
MIDI tempo and timing constants and conversion.
"""

from typing import Any

from mido import MidiTrack


class MidiTempo:
    """Tempo and timing constants."""

    BPM_120 = 120
    BPM_100_USEC = 600_000
    BPM_120_USEC = 500_000
    BPM_150_USEC = 400_000
    BPM_162_USEC = 370_370
    MICROSECONDS_PER_SECOND = 1_000_000
    MICROSECONDS_PER_MINUTE = 60_000_000
    MILLISECONDS_PER_SECOND = 1_000
    MILLISECONDS_PER_MINUTE = 60_000
    SECONDS_PER_MINUTE = 60


def milliseconds_per_note(bpm: int | float, division: int = 4) -> float:
    """calculate step duration
    1 = quarter note
    2 = eighth note
    4 = 16th note
    """
    if bpm <= 0:
        raise ValueError("BPM must be positive")
    if division <= 0:
        raise ValueError("division must be positive")
    ms_per_step = (MidiTempo.MILLISECONDS_PER_MINUTE / bpm) / division  # 4 = ms per 16th note
    return ms_per_step


def milliseconds_per_note_fraction(bpm: float, note_fraction: float) -> float:
    """
    Calculate milliseconds for a note duration.

    note_fraction:
        1.0   = quarter note
        0.5   = eighth
        0.25  = sixteenth
        1/3   = eighth triplet
    """
    if bpm <= 0:
        raise ValueError("BPM must be positive")
    if note_fraction <= 0:
        raise ValueError("note_fraction must be positive")
    return (MidiTempo.MILLISECONDS_PER_MINUTE / bpm) * note_fraction


def convert_absolute_time_to_delta_time(events: list[Any], track: MidiTrack):
    """Convert absolute time → delta time"""
    last_time = 0
    for abs_time, msg in events:
        delta = abs_time - last_time
        msg.time = delta
        track.append(msg)
        last_time = abs_time


class MeasureBeats:
    """Measure Beats with support for multiple time signatures."""

    # Beats per measure for common time signatures
    PER_MEASURE_4_4 = 16
    PER_MEASURE_3_4 = 12
    PER_MEASURE_2_4 = 8
    PER_MEASURE_6_8 = 24
    PER_MEASURE_5_4 = 20
    PER_MEASURE_7_8 = 28

    # Optional mapping for dynamic resolution if you want to look up by signature
    _SIG_TO_BEATS = {
        (4, 4): PER_MEASURE_4_4,
        (3, 4): PER_MEASURE_3_4,
        (2, 4): PER_MEASURE_2_4,
        (6, 8): PER_MEASURE_6_8,
        (5, 4): PER_MEASURE_5_4,
        (7, 8): PER_MEASURE_7_8,
    }

    @classmethod
    def beats_per_measure(cls, numerator: int, denominator: int) -> int:
        return cls._SIG_TO_BEATS.get((numerator, denominator), None)



def bpm_to_tempo_us(bpm: float) -> int:
    """bpm to tempo in us"""
    return int(MidiTempo.MICROSECONDS_PER_MINUTE / bpm)


def bpm_to_tempo_ms(bpm: float) -> int:
    """bpm to tempo in us"""
    return int(MidiTempo.MILLISECONDS_PER_MINUTE / bpm)


def ms_to_ticks(duration_ms: int, bpm: float, ppq: int) -> int:
    """ms to ticks"""
    ms_per_beat = bpm_to_tempo_ms(bpm)
    return int((duration_ms / ms_per_beat) * ppq)


def us_to_ticks(duration_us: int, bpm: float, ppq: int) -> int:
    """ms to ticks"""
    ms_per_beat = bpm_to_tempo_ms(bpm)
    return int((duration_us * 1_000 / ms_per_beat) * ppq)


def ticks_to_ms(ticks: int, bpm: float, ppq: int = 480):
    """ticks to duration in ms"""
    ms_per_beat = bpm_to_tempo_ms(bpm)
    return ticks / ppq * ms_per_beat


def ticks_to_duration_ms(ticks, tempo: int, ppq: int) -> float | Any:
    """tempo is in us"""
    return (ticks / ppq) * (tempo / 1000.0)


def bpm_to_ticks(bpm: int, duration_ms: float, ticks_per_beat: int) -> int:
    """Convert a duration in milliseconds to MIDI ticks."""
    ticks = (
        (duration_ms / 1000.0)  # ms → seconds
        * (bpm / 60.0)  # beats per second
        * ticks_per_beat  # ticks per beat
    )
    return int(round(ticks))
