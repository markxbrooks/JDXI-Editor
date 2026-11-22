"""
SoundFont playback renders into a buffer and opens a chosen output.

No audio device is opened. The stream and the synth are fakes.
"""

import threading

import numpy as np

from jdxi_editor.audio.audio_snapshot import SAMPLE_RATE
from jdxi_editor.audio import soundfont_output
from jdxi_editor.audio.soundfont_output import (
    BLOCK_FRAMES,
    SoundfontOutput,
    chosen_output,
    copy_s16,
    opened_output_name,
    output_device_for,
    output_devices,
)


def test_int16_samples_scale_into_the_float_buffer():
    pcm = np.array([32767, -32768, 0, 16384], dtype=np.int16)
    out = np.ones((3, 2), dtype=np.float32)
    copy_s16(pcm, out)
    assert abs(float(out[0, 0]) - 32767 / 32768) < 1e-6
    assert float(out[0, 1]) == -1.0
    assert float(out[1, 0]) == 0.0
    assert abs(float(out[1, 1]) - 16384 / 32768) < 1e-6
    assert float(out[2, 0]) == 0.0 and float(out[2, 1]) == 0.0


def test_the_device_list_keeps_outputs_and_their_indexes():
    class Library:
        def query_devices(self):
            return [
                {"name": "Mic", "max_output_channels": 0},
                {"name": "Speakers", "max_output_channels": 2},
                {"name": "Headphones", "max_output_channels": 2},
                {"name": "Speakers", "max_output_channels": 2},
            ]

    listed = output_devices(module=Library())
    assert listed == [("Speakers (1)", 1), ("Headphones", 2), ("Speakers (3)", 3)]
    assert output_devices(module=None) == []
    live = output_devices()
    assert all(isinstance(name, str) and isinstance(index, int) for name, index in live)


def test_a_current_output_wins_and_an_unknown_one_falls_back():
    labels = ["External Headphones", "MacBook Pro Speakers"]
    assert chosen_output("External Headphones", "", labels) == "External Headphones"
    assert (
        chosen_output("External Headphones", "MacBook Pro Speakers", labels)
        == "External Headphones"
    )
    assert chosen_output("", "MacBook Pro Speakers", labels) == "MacBook Pro Speakers"
    assert chosen_output("Gone", "Also gone", labels) == ""
    assert chosen_output("(Default)", "MacBook Pro Speakers", labels) == ""


def test_a_builtin_output_follows_the_system_route():
    devices = [
        ("MacBook Pro Speakers", 3),
        ("External Headphones", 2),
        ("Mark's AirPods", 1),
        ("Multi-Output Device", 9),
    ]

    def transport(name):
        if "MacBook" in name or name == "External Headphones":
            return "bltn"
        if "AirPods" in name:
            return "blue"
        return "grup"

    assert output_device_for(None, devices, platform="darwin", transport_type=transport) is None
    assert output_device_for(3, devices, platform="darwin", transport_type=transport) is None
    assert output_device_for(2, devices, platform="darwin", transport_type=transport) is None
    assert output_device_for(1, devices, platform="darwin", transport_type=transport) == 1
    assert output_device_for(9, devices, platform="darwin", transport_type=transport) == 9
    assert output_device_for(3, devices, platform="linux", transport_type=transport) == 3
    assert output_device_for(1, devices, platform="win32", transport_type=transport) == 1


def test_a_builtin_name_is_the_fallback_when_transport_cannot_be_read():
    devices = [("MacBook Pro Speakers (10)", 10), ("USB Audio", 4)]
    unknown = lambda _name: None
    assert output_device_for(10, devices, platform="darwin", transport_type=unknown) is None
    assert output_device_for(4, devices, platform="darwin", transport_type=unknown) == 4
    assert output_device_for(10, devices, platform="linux", transport_type=unknown) == 10


def test_start_opens_the_builtin_output_as_the_default(monkeypatch):
    monkeypatch.setattr(
        "jdxi_editor.audio.soundfont_output.output_device_for",
        lambda index, devices: None if index == 3 else index,
    )
    opened = {}

    def factory(**kwargs):
        opened.update(kwargs)
        return _Stream()

    player = SoundfontOutput(threading.RLock())
    player.start(
        "piano.sf2",
        3,
        stream_factory=factory,
        synth_factory=lambda: _Synth([]),
        midi_port_factory=lambda synth: None,
    )
    try:
        assert opened["device"] is None
        assert player.follows_default
    finally:
        player.stop()
    assert not player.follows_default


def test_a_followed_route_change_is_reported_once(monkeypatch):
    routes = iter([(1, b"hdpn"), (1, b"hdpn")])
    monkeypatch.setattr(
        "jdxi_editor.audio.soundfont_output.default_output_route",
        lambda: next(routes),
    )
    player = SoundfontOutput(threading.RLock())
    player.follows_default = True
    player._stream = object()
    player._route = (1, b"ispk")
    assert player.take_route_change()
    assert not player.take_route_change()
    player.follows_default = False
    assert not player.take_route_change()


def test_the_status_name_comes_from_the_stream_device():
    devices = [("External Headphones", 1), ("MacBook Pro Speakers", 3)]
    player = SoundfontOutput(threading.RLock())
    player._stream = type("Stream", (), {"device": 1})()
    assert player.opened_device() == 1
    assert opened_output_name(player.opened_device(), devices) == "External Headphones"
    assert opened_output_name(None, devices) == ""


def test_start_opens_the_chosen_index_without_starting_the_synth_driver(monkeypatch):
    # On macOS an output that looks built-in is opened as the system default
    # instead of by index. Index 7 is not a real device here, so the name
    # comes back empty and the index was remapped to None, failing on a Mac
    # and passing on Linux. Say what the device is; the remapping itself is
    # covered by the output_device_for tests above.
    monkeypatch.setattr(
        soundfont_output, "_coreaudio_transport", lambda label: "usb"
    )
    events = []

    class Synth:
        def __init__(self):
            self.synth = object()
            self.started = False

        def start(self, *args, **kwargs):
            self.started = True

        def sfload(self, path):
            self.loaded = path
            return 4

        def program_select(self, channel, sfid, bank, preset):
            self.program = (channel, sfid, bank, preset)

        def delete(self):
            events.append("synth-delete")

    class Stream:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
            events.append("stream-init")

        def start(self):
            events.append("stream-start")

        def stop(self):
            events.append("stream-stop")

        def close(self):
            events.append("stream-close")

    opened = {}

    def factory(**kwargs):
        opened.update(kwargs)
        return Stream(**kwargs)

    synth = Synth()
    player = SoundfontOutput(threading.RLock())
    sfid = player.start(
        "piano.sf2",
        7,
        stream_factory=factory,
        synth_factory=lambda: synth,
    )
    try:
        assert sfid == 4
        assert synth.loaded == "piano.sf2"
        assert synth.program == (0, 4, 0, 0)
        assert not synth.started
        assert opened["device"] == 7
        assert opened["samplerate"] == SAMPLE_RATE
        assert opened["channels"] == 2
        assert opened["dtype"] == "float32"
        assert opened["blocksize"] == BLOCK_FRAMES
        assert opened["callback"] == player._callback
    finally:
        player.stop()
    assert events[-3:] == ["stream-stop", "stream-close", "synth-delete"]


class _Stream:
    def __init__(self, **kwargs):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def close(self):
        pass


class _Synth:
    def __init__(self, events):
        self.events = events
        self.synth = object()

    def sfload(self, path):
        return 1

    def program_select(self, *args):
        pass

    def delete(self):
        self.events.append("synth-delete")


def test_the_soundfont_opens_a_midi_port_and_closes_it_before_the_synth():
    """
    The port is what lists the SoundFont as a MIDI Output; Synth.start used
    to open it, and rendering through our own stream had lost it.
    """
    events = []

    class Port:
        def __init__(self, synth):
            events.append("port-open")
            self.synth = synth

        def close(self):
            events.append("port-close")

    synth = _Synth(events)
    player = SoundfontOutput(threading.RLock())
    player.start("piano.sf2", stream_factory=_Stream, synth_factory=lambda: synth,
                 midi_port_factory=Port)
    assert isinstance(player.midi_port, Port) and player.midi_port.synth is synth
    player.stop()
    assert player.midi_port is None
    assert events == ["port-open", "port-close", "synth-delete"]


def test_playback_carries_on_without_a_midi_port():
    def no_port(_synth):
        raise RuntimeError("no MIDI driver here")

    player = SoundfontOutput(threading.RLock())
    sfid = player.start("piano.sf2", stream_factory=_Stream,
                        synth_factory=lambda: _Synth([]), midi_port_factory=no_port)
    assert sfid == 1 and player.midi_port is None and player.synth is not None
    player.stop()


def test_the_real_port_is_listed_as_a_midi_output(tmp_path):
    """With FluidSynth installed and a MIDI system, the port appears by name."""
    import glob
    import os

    import pytest

    mido = pytest.importorskip("mido")
    from jdxi_editor.audio import soundfont_output as module

    if module._fluidsynth_module is None:
        pytest.skip("fluidsynth is not installed")
    fonts = glob.glob(os.path.expanduser("~/SoundFonts/**/*.sf2"), recursive=True)
    if not fonts:
        pytest.skip("no SoundFont to load")
    # Count rather than look for the name: a running copy of the editor may
    # have its own SoundFont port open
    def ours() -> int:
        return mido.get_output_names().count(module.MIDI_PORT_NAME)

    import time

    before = ours()
    if before:
        pytest.skip("another program (e.g. a running editor) has the SoundFont port open")
    player = SoundfontOutput(threading.RLock())
    player.start(fonts[0], stream_factory=_Stream)
    try:
        if player.midi_port is None:
            pytest.skip("no MIDI driver on this system")
        assert ours() == before + 1
    finally:
        player.stop()
    # CoreMIDI drops a closed port from its list shortly afterwards
    deadline = time.monotonic() + 3.0
    while ours() > before and time.monotonic() < deadline:
        time.sleep(0.05)
    assert ours() == before


def test_a_large_device_request_is_rendered_in_full_not_padded_with_silence():
    """A device asking for more than one block gets every frame rendered."""
    from jdxi_editor.audio import soundfont_output as module

    calls = []

    def fake_write(_synth, count, buf, *_args):
        calls.append(count)
        samples = np.frombuffer(buf, dtype=np.int16)
        samples[: count * 2] = 16384  # half scale, every frame

    player = SoundfontOutput(threading.RLock())
    player.synth = _Synth([])
    player._allocate()
    out = np.zeros((BLOCK_FRAMES * 2 + 100, 2), dtype=np.float32)
    original = module.fluid_synth_write_s16
    module.fluid_synth_write_s16 = fake_write
    try:
        player._render(out, out.shape[0])
    finally:
        module.fluid_synth_write_s16 = original
    assert calls == [BLOCK_FRAMES, BLOCK_FRAMES, 100]
    assert np.allclose(out, 0.5)


def test_the_stream_keeps_a_deeper_buffer_and_dropouts_are_counted():
    import sys
    from types import SimpleNamespace

    from jdxi_editor.audio.soundfont_output import AUDIO_SWITCH_INTERVAL, OUTPUT_LATENCY

    opened = {}

    def factory(**kwargs):
        opened.update(kwargs)
        return _Stream(**kwargs)

    before = sys.getswitchinterval()
    player = SoundfontOutput(threading.RLock())
    player.start("piano.sf2", stream_factory=factory, synth_factory=lambda: _Synth([]),
                 midi_port_factory=lambda _s: None)
    try:
        assert opened["latency"] == OUTPUT_LATENCY >= 0.04
        assert sys.getswitchinterval() <= AUDIO_SWITCH_INTERVAL
        out = np.zeros((BLOCK_FRAMES, 2), dtype=np.float32)
        player._callback(out, BLOCK_FRAMES, None, SimpleNamespace(output_underflow=True))
        player._callback(out, BLOCK_FRAMES, None, SimpleNamespace(output_underflow=False))
        assert player.underflows == 1
    finally:
        player.stop()
    assert sys.getswitchinterval() == before
