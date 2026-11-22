"""
Analysis of synthetic audio. No device is opened and Qt is not loaded.
"""

import math
import time

import numpy as np

from jdxi_editor.audio.analysers.spectrum_analyser import (
    ATTACK,
    BAND_CENTERS,
    band_for_frequency,
)
from jdxi_editor.audio.analysers.vu_analyser import VUAnalyser, amplitude_db
from jdxi_editor.audio.analysers.waveform_analyser import (
    TIMEBASE_MS,
    decimate_minmax,
    window_samples,
)
from jdxi_editor.audio.audio_analyser import AudioAnalyser
from jdxi_editor.audio.audio_buffer import SampleRing
from jdxi_editor.audio.audio_snapshot import DB_FLOOR, FFT_SIZE, SAMPLE_RATE
from jdxi_editor.audio.audio_source import copy_input


def _sine(frequency: float, count: int, amplitude: float = 1.0) -> np.ndarray:
    times = np.arange(count) / SAMPLE_RATE
    return (amplitude * np.sin(2 * math.pi * frequency * times)).astype(np.float32)


def test_a_full_scale_sine_is_about_minus_three_rms_and_zero_peak():
    tone = _sine(1000, 4800)
    block = np.column_stack((tone, tone * 0.5))
    rms, peak = VUAnalyser().block_levels(block)
    assert abs(rms[0] - amplitude_db(1 / math.sqrt(2))) < 0.05
    assert abs(peak[0] - 0.0) < 0.05
    assert abs(peak[1] - amplitude_db(0.5)) < 0.05


def test_silence_sits_on_the_floor_and_the_vu_integrates():
    analyser = VUAnalyser()
    silence = np.zeros((1024, 2), dtype=np.float32)
    levels = analyser.update(silence, 0.1)
    assert levels["rms_left"] == DB_FLOOR
    assert levels["vu_left"] == DB_FLOOR

    tone = np.column_stack((_sine(440, 2048), _sine(440, 2048)))
    # A long step reaches the block RMS. 300 ms cannot.
    jumped = analyser.update(tone, 10.0)
    target = amplitude_db(1 / math.sqrt(2))
    assert abs(jumped["vu_left"] - target) < 0.2
    assert jumped["peak_hold_left"] == 0.0

    held = analyser.update(silence, 0.03)
    assert held["peak_hold_left"] > held["peak_left"]


def test_a_single_sample_click_survives_decimation():
    samples = np.zeros(2400, dtype=np.float32)
    samples[1234] = 1.0
    columns = decimate_minmax(samples, 100)
    assert columns[:, 1].max() == 1.0
    assert columns[:, 0].min() == 0.0


def test_timebases_match_the_sample_rate():
    assert [window_samples(ms, 48_000) for ms in TIMEBASE_MS] == [
        240, 480, 960, 2400, 4800,
    ]


def test_a_one_kilohertz_sine_lands_in_its_band():
    assert BAND_CENTERS.shape == (31,)
    assert band_for_frequency(1000) == int(np.where(BAND_CENTERS == 1000)[0][0])
    from jdxi_editor.audio.analysers.spectrum_analyser import SpectrumAnalyser

    analyser = SpectrumAnalyser(SAMPLE_RATE)
    measured = analyser.magnitude_bands(_sine(1000, FFT_SIZE))
    assert int(np.argmax(measured)) == band_for_frequency(1000)
    assert measured[band_for_frequency(1000)] > measured[band_for_frequency(100)] + 20

    first = analyser.update(_sine(1000, FFT_SIZE))
    # From the floor, one attack step moves a fraction of the way
    hot = measured[band_for_frequency(1000)]
    expected = DB_FLOOR + ATTACK * (min(0.0, hot) - DB_FLOOR)
    # update() clips. Compare the stored smoother via a second, known step.
    assert first[band_for_frequency(1000)] > DB_FLOOR + 10
    quiet = analyser.update(np.zeros(FFT_SIZE, dtype=np.float32))
    assert quiet[band_for_frequency(1000)] < first[band_for_frequency(1000)]


def test_the_ring_keeps_the_newest_frames_and_a_mono_copy_is_stereo():
    ring = SampleRing(8)
    ring.write(np.arange(5, dtype=np.float32))
    latest = ring.latest(5)
    assert latest.shape == (5, 2)
    assert np.allclose(latest[:, 0], [0, 1, 2, 3, 4])
    assert np.allclose(latest[:, 1], latest[:, 0])

    ring.write(np.column_stack((
        np.arange(10, 16, dtype=np.float32),
        np.arange(20, 26, dtype=np.float32),
    )))
    latest = ring.latest(8)
    # 5 mono frames then 6 stereo, capacity 8: the last 8
    assert np.allclose(latest[:, 0], [3, 4, 10, 11, 12, 13, 14, 15])
    assert np.allclose(latest[:, 1], [3, 4, 20, 21, 22, 23, 24, 25])


def test_the_callback_only_copies_into_the_ring():
    ring = SampleRing(16)
    scratch = np.zeros((8, 2), dtype=np.float32)
    mono = np.array([[0.25], [0.5], [-0.25]], dtype=np.float32)
    copy_input(mono, scratch, ring)
    stereo = np.array([[0.1, -0.1], [0.2, -0.2]], dtype=np.float32)
    copy_input(stereo, scratch, ring)
    latest = ring.latest(5)
    assert np.allclose(latest[:, 0], [0.25, 0.5, -0.25, 0.1, 0.2])
    assert np.allclose(latest[:, 1], [0.25, 0.5, -0.25, -0.1, -0.2])


def test_the_worker_publishes_a_snapshot_without_a_device():
    ring = SampleRing(FFT_SIZE * 2)
    tone = _sine(1000, FFT_SIZE)
    ring.write(np.column_stack((tone, tone)))
    analyser = AudioAnalyser(ring, sample_rate=SAMPLE_RATE)
    analyser.start()
    try:
        snapshot = None
        deadline = time.monotonic() + 1.0
        while time.monotonic() < deadline:
            snapshot = analyser.latest_snapshot()
            if snapshot is not None:
                break
            time.sleep(0.02)
        assert snapshot is not None
        assert int(np.argmax(snapshot.spectrum)) == band_for_frequency(1000)
        assert snapshot.waveform_left.shape[1] == 2
        assert snapshot.rms_left > -6.0
    finally:
        analyser.stop()
