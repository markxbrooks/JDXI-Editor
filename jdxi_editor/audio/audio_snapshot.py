"""
The latest analysis, handed to the window as one immutable value.
"""

from dataclasses import dataclass

import numpy as np

#: Meter floor and ceiling, in dB
DB_FLOOR = -60.0
DB_CEIL = 0.0

#: Display rate, and the FFT the spectrum analyser consumes
REFRESH_HZ = 30
FFT_SIZE = 4096
BAND_COUNT = 31

#: Columns stored for the oscilloscope. The widget scales them to its width.
WAVEFORM_COLUMNS = 480

SAMPLE_RATE = 48_000
BLOCK_SIZE = 1024


def clip_db(value: float) -> float:
    """
    Clamp a level onto the meter scale.

    :param value: float decibels
    :return: float in DB_FLOOR..DB_CEIL
    """
    return float(min(DB_CEIL, max(DB_FLOOR, value)))


@dataclass(frozen=True)
class AudioSnapshot:
    """
    One published frame of analysis.

    Levels are decibels on the meter scale. ``spectrum`` has
    :data:`BAND_COUNT` bands. Each waveform is ``(columns, 2)`` of
    min and max per column, so a transient is not averaged away.

    :param rms_left: float block RMS, left, dB
    :param rms_right: float block RMS, right, dB
    :param peak_left: float peak meter, left, dB
    :param peak_right: float peak meter, right, dB
    :param peak_hold_left: float held peak, left, dB
    :param peak_hold_right: float held peak, right, dB
    :param vu_left: float VU, left, dB
    :param vu_right: float VU, right, dB
    :param spectrum: np.ndarray band levels, dB
    :param waveform_left: np.ndarray decimated min/max
    :param waveform_right: np.ndarray decimated min/max
    :param sample_rate: int Hz
    :param timebase_ms: int oscilloscope window
    """

    rms_left: float
    rms_right: float
    peak_left: float
    peak_right: float
    peak_hold_left: float
    peak_hold_right: float
    vu_left: float
    vu_right: float
    spectrum: np.ndarray
    waveform_left: np.ndarray
    waveform_right: np.ndarray
    sample_rate: int
    timebase_ms: int
