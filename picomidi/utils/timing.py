"""
MIDI Timing Utilities

This module provides functions for MIDI timing calculations,
including tempo, BPM, ticks, and time conversions.
"""


def bpm_to_microseconds_per_quarter(bpm: float) -> int:
    """
    Convert BPM to microseconds per quarter note.

    This is the value stored in MIDI files for tempo.

    :param bpm: Beats per minute
    :return: Microseconds per quarter note
    """
    if bpm <= 0:
        raise ValueError(f"BPM must be positive, got {bpm}")
    return int(60_000_000 / bpm)


def microseconds_per_quarter_to_bpm(usec_per_quarter: int) -> float:
    """
    Convert microseconds per quarter note to BPM.

    :param usec_per_quarter: Microseconds per quarter note
    :return: Beats per minute
    """
    if usec_per_quarter <= 0:
        raise ValueError(
            f"Microseconds per quarter must be positive, got {usec_per_quarter}"
        )
    return 60_000_000 / usec_per_quarter


def ticks_to_milliseconds(ticks: int, ticks_per_beat: int, bpm: float) -> float:
    """
    Convert MIDI ticks to milliseconds.

    :param ticks: Number of MIDI ticks
    :param ticks_per_beat: Ticks per quarter note (TPQN)
    :param bpm: Beats per minute
    :return: Time in milliseconds
    """
    beats = ticks / ticks_per_beat
    seconds = beats * (60 / bpm)
    return seconds * 1000


def milliseconds_to_ticks(ms: float, ticks_per_beat: int, bpm: float) -> int:
    """
    Convert milliseconds to MIDI ticks.

    :param ms: Time in milliseconds
    :param ticks_per_beat: Ticks per quarter note (TPQN)
    :param bpm: Beats per minute
    :return: Number of MIDI ticks
    """
    seconds = ms / 1000
    beats = seconds * (bpm / 60)
    return int(beats * ticks_per_beat)


def ticks_to_seconds(ticks: int, ticks_per_beat: int, bpm: float) -> float:
    """
    Convert MIDI ticks to seconds.

    :param ticks: Number of MIDI ticks
    :param ticks_per_beat: Ticks per quarter note (TPQN)
    :param bpm: Beats per minute
    :return: Time in seconds
    """
    beats = ticks / ticks_per_beat
    return beats * (60 / bpm)


def seconds_to_ticks(seconds: float, ticks_per_beat: int, bpm: float) -> int:
    """
    Convert seconds to MIDI ticks.

    :param seconds: Time in seconds
    :param ticks_per_beat: Ticks per quarter note (TPQN)
    :param bpm: Beats per minute
    :return: Number of MIDI ticks
    """
    beats = seconds * (bpm / 60)
    return int(beats * ticks_per_beat)


def ticks_to_seconds_with_tempo(
    ticks: int, tempo: int, ticks_per_beat: int
) -> float:
    """
    Convert MIDI ticks to seconds using tempo in microseconds per quarter note.

    This is the standard MIDI timing calculation used in MIDI files.
    More precise than BPM-based calculations as it uses exact tempo values
    from MIDI file tempo meta events.

    :param ticks: Number of MIDI ticks
    :param tempo: Tempo in microseconds per quarter note (e.g., 500000 for 120 BPM)
    :param ticks_per_beat: Ticks per quarter note (TPQN, typically 480 or 960)
    :return: Duration in seconds
    """
    return (tempo / 1_000_000.0) * (ticks / ticks_per_beat)


def seconds_to_ticks_with_tempo(
    seconds: float, tempo: int, ticks_per_beat: int
) -> int:
    """
    Convert seconds to MIDI ticks using tempo in microseconds per quarter note.

    Inverse of `ticks_to_seconds_with_tempo()`.

    :param seconds: Duration in seconds
    :param tempo: Tempo in microseconds per quarter note
    :param ticks_per_beat: Ticks per quarter note (TPQN)
    :return: Number of MIDI ticks
    """
    return int((seconds * 1_000_000.0 / tempo) * ticks_per_beat)
