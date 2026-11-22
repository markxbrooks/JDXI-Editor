"""
Peak and VU ballistics over a block of samples.

The peak meter attacks in about 10 ms and falls in about 150 ms. The VU
integrates over about 300 ms. Peak hold falls more slowly, so the highest
recent peak stays visible.
"""

import math

import numpy as np

from jdxi_editor.audio.audio_snapshot import DB_FLOOR, clip_db

#: Avoid log(0). A true digital zero lands on the meter floor.
_EPSILON = 1e-12

#: Time constants, seconds
PEAK_ATTACK = 0.010
PEAK_DECAY = 0.150
VU_INTEGRATION = 0.300
HOLD_DECAY = 1.5


def amplitude_db(amplitude: float) -> float:
    """
    ``20 log10`` of an amplitude.

    :param amplitude: float linear amplitude, 0..1
    :return: float decibels, not yet clipped to the meter
    """
    return float(20.0 * math.log10(amplitude + _EPSILON))


def _alpha(dt: float, tau: float) -> float:
    return 1.0 - math.exp(-dt / tau)


def _approach(current: float, target: float, alpha: float) -> float:
    return current + alpha * (target - current)


class VUAnalyser:
    """
    Stereo peak meter, peak hold, and VU, kept between blocks.
    """

    def __init__(self) -> None:
        self.peak = np.full(2, DB_FLOOR, dtype=np.float64)
        self.vu = np.full(2, DB_FLOOR, dtype=np.float64)
        self.hold = np.full(2, DB_FLOOR, dtype=np.float64)

    def block_levels(self, block: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """
        RMS and peak of one stereo block, in dB, unclipped.

        :param block: np.ndarray shape ``(n, 2)``
        :return: tuple of RMS and peak, each shape ``(2,)``
        """
        if block.size == 0:
            floor = np.full(2, DB_FLOOR, dtype=np.float64)
            return floor, floor.copy()
        squared = np.square(block.astype(np.float64, copy=False))
        rms = np.sqrt(np.mean(squared, axis=0))
        peak = np.max(np.abs(block), axis=0)
        return (
            np.array([amplitude_db(float(rms[0])), amplitude_db(float(rms[1]))]),
            np.array([amplitude_db(float(peak[0])), amplitude_db(float(peak[1]))]),
        )

    def update(self, block: np.ndarray, dt: float) -> dict[str, float]:
        """
        Fold one block into the meters.

        :param block: np.ndarray shape ``(n, 2)``
        :param dt: float seconds since the previous update
        :return: dict of clipped meter values, left then right
        """
        dt = max(float(dt), 1e-4)
        rms, peak = self.block_levels(block)
        attack = _alpha(dt, PEAK_ATTACK)
        decay = _alpha(dt, PEAK_DECAY)
        vu_alpha = _alpha(dt, VU_INTEGRATION)
        hold_alpha = _alpha(dt, HOLD_DECAY)
        for channel in (0, 1):
            alpha = attack if peak[channel] > self.peak[channel] else decay
            self.peak[channel] = _approach(self.peak[channel], peak[channel], alpha)
            self.vu[channel] = _approach(self.vu[channel], rms[channel], vu_alpha)
            if peak[channel] >= self.hold[channel]:
                self.hold[channel] = peak[channel]
            else:
                self.hold[channel] = _approach(
                    self.hold[channel], peak[channel], hold_alpha
                )
        return {
            "peak_left": clip_db(self.peak[0]),
            "peak_right": clip_db(self.peak[1]),
            "vu_left": clip_db(self.vu[0]),
            "vu_right": clip_db(self.vu[1]),
            "peak_hold_left": clip_db(self.hold[0]),
            "peak_hold_right": clip_db(self.hold[1]),
            "rms_left": clip_db(float(rms[0])),
            "rms_right": clip_db(float(rms[1])),
        }
