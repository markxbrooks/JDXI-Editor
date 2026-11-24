"""
Recovering from PortAudio's stale device list.

PortAudio reads the audio hardware once, in ``Pa_Initialize``. A session that
outlives a change to it -- AirPods connecting, headphones unplugged -- asks
for devices by positions that have moved or gone, and gets paInternalError
(-9986), the default output included. That is what stopped SoundFont playback
after a route change, and left every later attempt failing until restart.

Terminating PortAudio and initialising it again is the only cure, and it
closes every stream in the process, so it must not happen while something
else is listening.
"""

import os
import sys
import threading

sys.path.insert(0, os.path.abspath("."))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

from jdxi_editor.audio import portaudio
from jdxi_editor.audio.soundfont_output import SoundfontOutput

#: What CoreAudio answers with once the device it was told about has gone.
INTERNAL_ERROR = "Error opening OutputStream: Internal PortAudio error [PaErrorCode -9986]"


class FakeSounddevice:
    """Counts the terminate/initialise pair."""

    def __init__(self) -> None:
        self.refreshes = 0

    def _terminate(self) -> None:
        self.refreshes += 1

    def _initialize(self) -> None:
        pass


@pytest.fixture(autouse=True)
def no_holders():
    """Each test starts with nothing listening."""
    portaudio._holders.clear()
    yield
    portaudio._holders.clear()


def test_refresh_rereads_the_devices_when_nothing_is_listening():
    module = FakeSounddevice()
    assert portaudio.refresh_devices(module) is True
    assert module.refreshes == 1


def test_a_refresh_is_refused_while_a_stream_is_open():
    module = FakeSounddevice()
    token = portaudio.hold("USB recording")
    assert portaudio.refresh_devices(module) is False
    assert module.refreshes == 0, "a recording in progress was torn down"
    assert portaudio.holders() == ["USB recording"]
    portaudio.release(token)
    assert portaudio.refresh_devices(module) is True


def test_holding_releases_on_the_way_out():
    with portaudio.holding("Audio Monitor"):
        assert portaudio.holders() == ["Audio Monitor"]
    assert portaudio.holders() == []
    portaudio.release(None)  # tolerated


class FakeStream:
    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs
        self.started = False

    def start(self) -> None:
        self.started = True

    def stop(self) -> None:
        self.started = False

    def close(self) -> None:
        pass

    @property
    def device(self):
        return self.kwargs.get("device")


class FakeSynth:
    """Enough of a FluidSynth for start() to get as far as the stream."""

    def __init__(self) -> None:
        self.settings = object()
        self.synth = object()

    def sfload(self, path):
        return 1

    def program_select(self, *args):
        pass

    def delete(self) -> None:
        pass


def _player():
    return SoundfontOutput(threading.RLock())


def test_a_stale_device_list_is_reread_and_the_output_opens(monkeypatch):
    """The failure from the log: one refusal, then the stream opens."""
    refreshed = []
    monkeypatch.setattr(
        "jdxi_editor.audio.soundfont_output.refresh_devices",
        lambda: refreshed.append(True) or True,
    )
    attempts = []

    def opener(**kwargs):
        attempts.append(kwargs)
        if len(attempts) == 1:
            raise RuntimeError(INTERNAL_ERROR)
        return FakeStream(**kwargs)

    player = _player()
    sfid = player.start(
        "ignored.sf2",
        None,
        stream_factory=opener,
        synth_factory=FakeSynth,
        midi_port_factory=lambda synth: None,
    )
    assert sfid == 1
    assert len(attempts) == 2, "the open was not retried"
    assert refreshed == [True]
    assert player._stream.started
    player.stop()


def test_the_error_is_raised_when_the_devices_cannot_be_reread(monkeypatch):
    """A refusal (something else is listening) must not be swallowed."""
    monkeypatch.setattr(
        "jdxi_editor.audio.soundfont_output.refresh_devices", lambda: False
    )
    attempts = []

    def opener(**kwargs):
        attempts.append(kwargs)
        raise RuntimeError(INTERNAL_ERROR)

    player = _player()
    with pytest.raises(RuntimeError, match="-9986"):
        player.start(
            "ignored.sf2",
            None,
            stream_factory=opener,
            synth_factory=FakeSynth,
            midi_port_factory=lambda synth: None,
        )
    assert len(attempts) == 1, "retried without a fresh device list"


def test_a_refreshed_list_that_still_fails_reports_the_second_error(monkeypatch):
    monkeypatch.setattr(
        "jdxi_editor.audio.soundfont_output.refresh_devices", lambda: True
    )
    attempts = []

    def opener(**kwargs):
        attempts.append(kwargs)
        raise RuntimeError(INTERNAL_ERROR)

    player = _player()
    with pytest.raises(RuntimeError, match="-9986"):
        player.start(
            "ignored.sf2",
            None,
            stream_factory=opener,
            synth_factory=FakeSynth,
            midi_port_factory=lambda synth: None,
        )
    assert len(attempts) == 2
