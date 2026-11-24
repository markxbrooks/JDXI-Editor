"""Opening an input: the rate fallback and the busy-device message."""

import numpy as np
import pytest

from jdxi_editor.audio import audio_source
from jdxi_editor.audio.audio_buffer import SampleRing
from jdxi_editor.audio.audio_source import InputDeviceSource, describe_open_error


class _FakeSoundDevice:
    """
    A sounddevice stand-in whose one device opens only at ``rates``, like a
    raw ALSA hw: device, which does no rate conversion.
    """

    def __init__(self, rates, default_rate, error="Invalid sample rate [PaErrorCode -9997]"):
        self.rates = set(rates)
        self.default_rate = default_rate
        self.error = error
        self.attempts = []

    def query_devices(self, device=None, kind=None):
        return {"name": "JD-Xi", "max_input_channels": 2, "default_samplerate": float(self.default_rate)}

    def InputStream(self, device, channels, samplerate, blocksize, dtype, callback):
        self.attempts.append((samplerate, channels))
        if samplerate not in self.rates:
            raise RuntimeError(f"Error opening InputStream: {self.error}")
        return _FakeStream()


class _FakeStream:
    def start(self):
        pass

    def stop(self):
        pass

    def close(self):
        pass


def _source():
    return InputDeviceSource(SampleRing(4096))


def test_a_device_that_refuses_48k_opens_at_its_own_rate(monkeypatch):
    fake = _FakeSoundDevice(rates={44_100}, default_rate=44_100)
    monkeypatch.setattr(audio_source, "_sounddevice", lambda: fake)
    source = _source()
    assert source.start(3) == 44_100
    assert source.sample_rate == 44_100
    # 48 kHz is tried first, in stereo and mono, then the device's own rate
    assert fake.attempts == [(48_000, 2), (48_000, 1), (44_100, 2)]


def test_48k_is_kept_when_the_device_takes_it(monkeypatch):
    fake = _FakeSoundDevice(rates={44_100, 48_000}, default_rate=44_100)
    monkeypatch.setattr(audio_source, "_sounddevice", lambda: fake)
    source = _source()
    assert source.start(3) == 48_000
    assert fake.attempts == [(48_000, 2)]


def test_a_failed_open_does_not_change_the_preferred_rate(monkeypatch):
    """After falling back to 44.1 kHz once, the next device still tries 48 kHz first."""
    monkeypatch.setattr(audio_source, "_sounddevice", lambda: _FakeSoundDevice({44_100}, 44_100))
    source = _source()
    source.start(3)
    fake = _FakeSoundDevice(rates={48_000}, default_rate=48_000)
    monkeypatch.setattr(audio_source, "_sounddevice", lambda: fake)
    assert source.start(4) == 48_000
    assert fake.attempts[0] == (48_000, 2)


def test_a_busy_device_says_which_input_to_choose(monkeypatch):
    fake = _FakeSoundDevice(rates=set(), default_rate=44_100, error="Device unavailable [PaErrorCode -9985]")
    monkeypatch.setattr(audio_source, "_sounddevice", lambda: fake)
    with pytest.raises(RuntimeError) as raised:
        _source().start(3)
    message = str(raised.value)
    assert "-9985" in message and "pipewire" in message


def test_other_errors_are_reported_as_they_are():
    assert describe_open_error(RuntimeError("Invalid number of channels")) == "Invalid number of channels"
    assert describe_open_error(None) == "no input device"
