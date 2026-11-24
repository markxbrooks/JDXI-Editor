"""
SoundFont playback through an output the application chooses.

FluidSynth renders each block. sounddevice opens the device. The synth's
own audio driver is left closed, so a device name never has to match
CoreAudio's list.
"""

import sys
import threading
from ctypes import (
    CDLL,
    POINTER,
    Structure,
    byref,
    c_uint32,
    c_void_p,
    cast,
    create_string_buffer,
)
from typing import Callable, Optional

import numpy as np
from decologr import Decologr as log

from jdxi_editor.audio.audio_snapshot import SAMPLE_RATE
from jdxi_editor.audio.portaudio import (
    label_devices,
    plain_name,
    refresh_devices,
)

BLOCK_FRAMES = 512
#: Seconds of audio the output keeps queued. The callback runs Python, so it
#: waits for the interpreter lock whenever the interface is busy; sounddevice's
#: "high" latency is only 10-28 ms on typical Mac outputs, one or two blocks,
#: and a longer stall emptied it (an audible jump). 50 ms rides out ordinary
#: stalls and still feels immediate when playing a keyboard through it.
OUTPUT_LATENCY = 0.05
#: Python's thread switch interval while the SoundFont plays. The default 5 ms
#: let a busy interface keep the audio callback waiting up to ~8 ms of each
#: 10.7 ms block; 1 ms hands the lock over sooner.
AUDIO_SWITCH_INTERVAL = 0.001
_SCALE = np.float32(1.0 / 32768.0)

try:
    import sounddevice as _sounddevice_module
except Exception:
    _sounddevice_module = None

try:
    import fluidsynth as _fluidsynth_module
    from fluidsynth import fluid_synth_write_s16
except Exception:
    _fluidsynth_module = None
    fluid_synth_write_s16 = None


def sounddevice_available() -> bool:
    """
    Whether sounddevice imported.

    :return: bool
    """
    return _sounddevice_module is not None


#: Passed by callers that want the installed sounddevice module.
_INSTALLED = object()


def output_devices(module=_INSTALLED) -> list[tuple[str, int]]:
    """
    Output devices as ``(display name, sounddevice index)``.

    A repeated name is told apart by its host API; see
    :func:`~jdxi_editor.audio.portaudio.label_devices`. ``module=None``
    reports that sounddevice is absent. Omit ``module`` to query the
    installed library.

    :param module: sounddevice, or None when the library did not import
    :return: list
    """
    source = _sounddevice_module if module is _INSTALLED else module
    if source is None:
        return []
    try:
        devices = source.query_devices()
    except Exception:
        return []
    try:
        apis = list(source.query_hostapis())
    except Exception:
        apis = []

    return label_devices(devices, apis, "max_output_channels")


def chosen_output(current: str, saved: str, labels: list[str]) -> str:
    """
    Which output label to put back after the combo is rebuilt.

    The label on screen wins, then the saved name. ``""`` means the
    default output. An explicit ``(Default)`` stays the default, so a
    saved device does not replace it.

    :param current: str the label showing before the rebuild
    :param saved: str the stored preference
    :param labels: list device labels, without the default entry
    :return: str a label from ``labels``, or ``""`` for the default
    """
    if current in labels:
        return current
    if current == "(Default)":
        return ""
    if saved in labels:
        return saved
    if saved:
        # The label may have been stored when a repeated name was told apart
        # by its position, where it is now told apart by its host API. Match
        # on the device's own name so the choice survives that, rather than
        # quietly reverting to the default. Where several host APIs offer the
        # same device, the first listed is as good a guess as any.
        plain = _unindexed_name(saved)
        for label in labels:
            if _unindexed_name(label) == plain:
                return label
    return ""


def output_device_for(
    index: Optional[int],
    devices: list[tuple[str, int]],
    *,
    platform: Optional[str] = None,
    transport_type: Optional[Callable[[str], Optional[str]]] = None,
) -> Optional[int]:
    """
    The sounddevice index to open.

    On macOS the built-in output is opened as the system default (``None``),
    so CoreAudio follows the headphone jack. Every other selected device
    keeps its index. ``None`` stays the default on every platform.

    :param index: Optional[int] chosen sounddevice index
    :param devices: list of ``(label, index)``
    :param platform: str override for tests; the running OS otherwise
    :param transport_type: Callable name -> CoreAudio transport, or None to
        read it. ``"bltn"`` is the built-in output
    :return: Optional[int]
    """
    if index is None:
        return None
    system = sys.platform if platform is None else platform
    if system != "darwin":
        return index
    name = next((label for label, device_index in devices if device_index == index), "")
    lookup = _coreaudio_transport if transport_type is None else transport_type
    try:
        kind = lookup(name)
    except Exception:
        kind = None
    if kind == _TRANSPORT_BUILTIN or (kind is None and _builtin_output_name(name)):
        return None
    return index


def default_output_route() -> Optional[tuple]:
    """
    ``(device id, data source)`` of the macOS default output.

    The data source changes when the headphone jack is plugged or unplugged
    on the same device. ``None`` off macOS, or when CoreAudio cannot be read.

    :return: Optional[tuple]
    """
    if sys.platform != "darwin":
        return None
    try:
        device = _coreaudio_default_output()
        if device is None:
            return None
        return (device, _coreaudio_data_source(device))
    except Exception:
        return None


_BUILTIN_OUTPUT_NAMES = {"macbook pro speakers", "external headphones"}

# CoreAudio four-character selectors.
_SCOPE_GLOBAL = 0x676C6F62  # 'glob'
_SCOPE_OUTPUT = 0x6F757470  # 'outp'
_ELEMENT_MAIN = 0
_SYSTEM_OBJECT = 1
_PROP_DEVICES = 0x64657623  # 'dev#'
_PROP_DEFAULT_OUTPUT = 0x644F7574  # 'dOut'
_PROP_NAME = 0x6E616D65  # 'name'
_PROP_TRANSPORT = 0x7472616E  # 'tran'
_PROP_DATA_SOURCE = 0x73737263  # 'ssrc'
_PROP_STREAMS = 0x73746D23  # 'stm#'
_TRANSPORT_BUILTIN = "bltn"


class _AudioAddress(Structure):
    _fields_ = [
        ("selector", c_uint32),
        ("scope", c_uint32),
        ("element", c_uint32),
    ]


_coreaudio = None


def _coreaudio_library():
    """CoreAudio, loaded once. None when the framework cannot be opened."""
    global _coreaudio
    if _coreaudio is False:
        return None
    if _coreaudio is None:
        try:
            library = CDLL("/System/Library/Frameworks/CoreAudio.framework/CoreAudio")
            library.AudioObjectGetPropertyData.argtypes = [
                c_uint32,
                POINTER(_AudioAddress),
                c_uint32,
                c_void_p,
                POINTER(c_uint32),
                c_void_p,
            ]
            library.AudioObjectGetPropertyData.restype = c_uint32
            _coreaudio = library
        except Exception:
            _coreaudio = False
            return None
    return _coreaudio


def _audio_property(obj: int, selector: int, scope: int, size: int):
    """``(ok, buffer)`` for one CoreAudio property."""
    library = _coreaudio_library()
    if library is None:
        return False, None
    address = _AudioAddress(selector, scope, _ELEMENT_MAIN)
    stored = c_uint32(size)
    buffer = create_string_buffer(size)
    status = library.AudioObjectGetPropertyData(
        c_uint32(obj), byref(address), 0, None, byref(stored), buffer
    )
    if status != 0:
        return False, None
    return True, (buffer, stored.value)


def _unindexed_name(label: str) -> str:
    """
    A device's own name, without the suffix added for a repeated one.

    :param label: str device label
    :return: str
    """
    return plain_name(label)


def _builtin_output_name(label: str) -> bool:
    """True for the built-in speaker and headphone-jack names."""
    return _unindexed_name(label).casefold() in _BUILTIN_OUTPUT_NAMES


def _coreaudio_outputs() -> list[tuple[int, str]]:
    """Output devices as ``(CoreAudio id, name)``."""
    ok, payload = _audio_property(_SYSTEM_OBJECT, _PROP_DEVICES, _SCOPE_GLOBAL, 4096)
    if not ok:
        return []
    buffer, size = payload
    count = size // 4
    if count <= 0:
        return []
    ids = list(cast(buffer, POINTER(c_uint32 * count)).contents)
    found = []
    for device_id in ids:
        streams, _stream_size = _audio_property(device_id, _PROP_STREAMS, _SCOPE_OUTPUT, 64)
        if not streams:
            continue
        named, name_payload = _audio_property(device_id, _PROP_NAME, _SCOPE_GLOBAL, 256)
        if not named:
            continue
        name = name_payload[0].value.decode("utf-8", "replace")
        if name:
            found.append((int(device_id), name))
    return found


def _coreaudio_transport(label: str) -> Optional[str]:
    """
    CoreAudio transport of the output named *label* (``bltn``, ``usb ``, …).

    ``None`` when it cannot be read, or when several outputs share the name
    and disagree.

    :param label: str sounddevice label
    :return: Optional[str]
    """
    name = _unindexed_name(label)
    if not name:
        return None
    kinds = set()
    for device_id, device_name in _coreaudio_outputs():
        if device_name != name:
            continue
        ok, payload = _audio_property(device_id, _PROP_TRANSPORT, _SCOPE_GLOBAL, 4)
        if not ok:
            continue
        value = cast(payload[0], POINTER(c_uint32)).contents.value
        kinds.add(value.to_bytes(4, "big").decode("ascii", "replace"))
    if len(kinds) == 1:
        return kinds.pop()
    return None


def _coreaudio_default_output() -> Optional[int]:
    ok, payload = _audio_property(_SYSTEM_OBJECT, _PROP_DEFAULT_OUTPUT, _SCOPE_GLOBAL, 4)
    if not ok:
        return None
    return int(cast(payload[0], POINTER(c_uint32)).contents.value)


def _coreaudio_data_source(device: int) -> bytes:
    """The output data source (``ispk``, ``hdpn``), or empty when it has none."""
    ok, payload = _audio_property(device, _PROP_DATA_SOURCE, _SCOPE_OUTPUT, 4)
    if not ok:
        return b""
    value = cast(payload[0], POINTER(c_uint32)).contents.value
    if value == 0:
        return b""
    return value.to_bytes(4, "big")


def opened_output_name(device_index: Optional[int], devices: list[tuple[str, int]]) -> str:
    """
    The name of the output a stream actually opened.

    Looked up from the device index the stream reports, so a default
    combo entry cannot rename it.

    :param device_index: Optional[int]
    :param devices: list of ``(name, index)``
    :return: str the name, or ``""`` when the index is unknown
    """
    if isinstance(device_index, bool) or not isinstance(device_index, int):
        return ""
    for name, index in devices:
        if index == device_index:
            return name
    return ""


def copy_s16(pcm: np.ndarray, out: np.ndarray) -> None:
    """
    Convert interleaved int16 stereo into a float32 ``(frames, 2)`` buffer.

    Samples are scaled by ``1/32768``. Frames past the int16 block are silence.
    The float buffer is filled in place.

    :param pcm: np.ndarray int16, interleaved left, right
    :param out: np.ndarray float32, shape ``(frames, 2)``
    :return: None
    """
    frames = int(out.shape[0])
    count = min(frames, int(pcm.shape[0]) // 2)
    if count:
        stereo = pcm[: count * 2].reshape(count, 2)
        np.copyto(out[:count], stereo, casting="unsafe")
        out[:count] *= _SCALE
    if count < frames:
        out[count:].fill(0)


#: Name of the MIDI port other apps (and the MIDI Output list) see
MIDI_PORT_NAME = "SoundFont (JD-Xi Editor)"


class SoundfontMidiPort:
    """
    FluidSynth's own MIDI input: a virtual MIDI port (on macOS a CoreMIDI
    destination) that plays the synth.

    ``Synth.start`` used to open one along with FluidSynth's audio driver, and
    that port is what offered the SoundFont as a MIDI Output. Rendering now
    goes through our own stream, so the port is opened here on its own: a
    MIDI router into the synth, and a MIDI driver feeding the router.
    """

    def __init__(self, synth, port_name: str = MIDI_PORT_NAME) -> None:
        import fluidsynth as fs

        self._fs = fs
        try:
            synth.setting("midi.portname", port_name)
        except Exception:
            pass  # older FluidSynth: the driver's default name
        self.router = fs.new_fluid_midi_router(
            synth.settings, fs.fluid_synth_handle_midi_event, synth.synth
        )
        if not self.router:
            raise RuntimeError("FluidSynth could not create a MIDI router")
        # Only needed for router commands; missing from newer FluidSynth
        if getattr(fs, "fluid_synth_set_midi_router", None) is not None:
            fs.fluid_synth_set_midi_router(synth.synth, self.router)
        self.driver = fs.new_fluid_midi_driver(
            synth.settings, fs.fluid_midi_router_handle_midi_event, self.router
        )
        if not self.driver:
            self._delete_router()
            raise RuntimeError("FluidSynth could not open a MIDI port")

    def close(self) -> None:
        """Close the port, then the router. Before the synth is deleted."""
        driver, self.driver = self.driver, None
        delete = _delete_midi_driver(self._fs) if driver else None
        if delete is not None:
            delete(driver)
        self._delete_router()

    def _delete_router(self) -> None:
        router, self.router = self.router, None
        delete = _delete_midi_router(self._fs) if router else None
        if delete is not None:
            delete(router)


def _delete_midi_driver(fs):
    """pyfluidsynth binds new_fluid_midi_driver but not its delete."""
    from ctypes import c_void_p

    return fs.cfunc("delete_fluid_midi_driver", None, ("driver", c_void_p, 1))


def _delete_midi_router(fs):
    from ctypes import c_void_p

    return fs.cfunc("delete_fluid_midi_router", None, ("router", c_void_p, 1))


class SoundfontOutput:
    """
    A FluidSynth and the output stream that plays it.

    ``start`` does not call ``Synth.start``. Rendering happens in the
    stream callback, into a buffer allocated with the stream.
    """

    def __init__(self, lock: threading.RLock) -> None:
        """
        :param lock: threading.RLock shared with note forwarding
        """
        self._lock = lock
        self.synth = None
        self.sfid = None
        self._stream = None
        self._pcm_buf = None
        self._pcm: Optional[np.ndarray] = None
        self._logged_render = False
        self.midi_port = None
        #: Times the output ran dry (PortAudio's output underflow): each is an
        #: audible gap. Counted in the callback, reported on stop.
        self.underflows = 0
        self._switch_interval: Optional[float] = None
        #: The chosen output was the system default or the built-in jack, so a
        #: later change of that route reopens the stream.
        self.follows_default = False
        self._route: Optional[tuple] = None
        self._sf_path = ""
        self._requested_device: Optional[int] = None
        #: Name of the chosen output. The index is resolved from this at
        #: every open, never remembered across one.
        self._requested_name = ""
        self.on_reopened: Optional[Callable[[], None]] = None

    def start(
        self,
        sf_path: str,
        device: Optional[int] = None,
        stream_factory: Optional[Callable] = None,
        synth_factory: Optional[Callable] = None,
        midi_port_factory: Optional[Callable] = None,
    ) -> int:
        """
        Load a SoundFont and open the output.

        An output that is already open is stopped first. ``device`` None
        is the default output. On macOS the built-in output is opened the
        same way, so the headphone jack follows the system route.

        :param sf_path: str
        :param device: Optional[int] sounddevice index
        :param stream_factory: Optional[Callable] builds the output stream
        :param synth_factory: Optional[Callable] builds the synth
        :param midi_port_factory: Optional[Callable] opens the synth's MIDI
            port (SoundfontMidiPort); it is optional, so playback carries on
            without it
        :return: int SoundFont id
        """
        self.stop()
        self._sf_path = sf_path
        self._requested_device = device
        # The index is a position in PortAudio's list, good only until the
        # hardware changes; the name is what the choice really was.
        self._requested_name = _device_label(device, output_devices())
        synth = (synth_factory or _new_synth)()
        self.synth = synth
        try:
            with self._lock:
                sfid = synth.sfload(sf_path)
                synth.program_select(0, sfid, 0, 0)
            self.sfid = sfid
            self._allocate()
            opener = stream_factory or _output_stream
            self._stream, resolved = self._open_stream(opener)
            self.follows_default = resolved is None
            self._route = default_output_route() if self.follows_default else None
            self.underflows = 0
            self._hand_over_sooner()
            self._stream.start()
        except Exception:
            self.stop()
            raise
        try:
            self.midi_port = (midi_port_factory or SoundfontMidiPort)(synth)
        except Exception as ex:
            self.midi_port = None
            log.warning(f"SoundFont MIDI port not available: {ex}")
        return sfid

    def _resolve_device(self) -> Optional[int]:
        """
        The index to open now, for the device whose name was chosen.

        Looked up afresh every time. An index is a position in PortAudio's
        list, and that list is rebuilt whenever the hardware changes, so a
        remembered one can point at a different device or at nothing. A
        chosen device that has gone falls back to the system default
        rather than to whatever now sits at its old position.

        :return: Optional[int] sounddevice index, None for the default
        """
        devices = output_devices()
        name = self._requested_name
        if not name:
            # Either the default was asked for, or the index given is not in
            # the list at all. Honour what the caller passed; second-guessing
            # an explicit index is not this method's business.
            return output_device_for(self._requested_device, devices)
        index = next((i for label, i in devices if label == name), None)
        if index is None:
            log.warning(
                f"The chosen output ({name}) is not there; using the default"
            )
            return None
        return output_device_for(index, devices)

    def _open_stream(self, opener: Callable):
        """
        Open the output, rereading PortAudio's device list if it refuses.

        PortAudio reads the hardware once, at startup, so a stream opened
        after headphones have come and gone asks for a device that has
        moved or disappeared -- paInternalError, and the same for the
        default output, whose identity was resolved just as early. One
        retry on a freshly read list is the difference between playback
        following the route and nothing working until restart. The index is
        resolved again for that retry: the reread is what moves it.

        :param opener: Callable builds the stream
        :return: tuple (the open stream, the index it opened)
        """

        def build():
            device = self._resolve_device()
            stream = opener(
                samplerate=SAMPLE_RATE,
                channels=2,
                dtype="float32",
                blocksize=BLOCK_FRAMES,
                latency=OUTPUT_LATENCY,
                device=device,
                callback=self._callback,
            )
            return stream, device

        try:
            return build()
        except Exception as ex:
            log.message(f"Output would not open ({ex}); rereading the devices")
            if not refresh_devices():
                raise
            return build()

    def reopen(self) -> int:
        """
        Open the same SoundFont on the route chosen last time.

        Used when the macOS default output changes underneath a stream that
        is following it.

        :return: int SoundFont id
        """
        name = self._requested_name
        devices = output_devices() if name else []
        device = next((i for label, i in devices if label == name), None)
        sfid = self.start(self._sf_path, device)
        if name and device is None:
            # Away for the moment -- a dock unplugged, AirPods asleep. Keep
            # the choice so it is taken up again when the device comes back,
            # instead of settling on the default for good.
            self._requested_name = name
        return sfid

    def take_route_change(self) -> bool:
        """
        True once when the followed system route has changed.

        :return: bool
        """
        if not self.follows_default or self._stream is None:
            return False
        route = default_output_route()
        if route is None or route == self._route:
            return False
        self._route = route
        return True

    def opened_device(self) -> Optional[int]:
        """
        The output index the stream opened, or None when it is closed.

        :return: Optional[int]
        """
        stream = self._stream
        if stream is None:
            return None
        device = getattr(stream, "device", None)
        if isinstance(device, tuple):
            device = device[-1] if device else None
        if isinstance(device, bool) or not isinstance(device, int):
            return None
        return int(device)

    def stop(self) -> None:
        """
        Close the stream, then delete the synth.

        :return: None
        """
        self.follows_default = False
        self._route = None
        port, self.midi_port = self.midi_port, None
        if port is not None:
            try:
                port.close()
            except Exception:
                pass
        stream = self._stream
        self._stream = None
        if stream is not None:
            try:
                stream.stop()
            except Exception:
                pass
            try:
                stream.close()
            except Exception:
                pass
        self._restore_switch_interval()
        if self.underflows:
            log.warning(
                f"SoundFont output ran dry {self.underflows} time(s) "
                "(audible gaps): the application was too busy to keep up"
            )
        synth = self.synth
        self.synth = None
        self.sfid = None
        self._pcm_buf = None
        self._pcm = None
        if synth is not None:
            try:
                synth.delete()
            except Exception:
                pass

    def _allocate(self) -> None:
        from ctypes import create_string_buffer

        self._pcm_buf = create_string_buffer(BLOCK_FRAMES * 4)
        self._pcm = np.frombuffer(self._pcm_buf, dtype=np.int16)

    def _hand_over_sooner(self) -> None:
        import sys

        if self._switch_interval is None:
            self._switch_interval = sys.getswitchinterval()
            sys.setswitchinterval(min(self._switch_interval, AUDIO_SWITCH_INTERVAL))

    def _restore_switch_interval(self) -> None:
        import sys

        if self._switch_interval is not None:
            sys.setswitchinterval(self._switch_interval)
            self._switch_interval = None

    def _callback(self, outdata, frames, _time_info, status) -> None:
        if status and getattr(status, "output_underflow", False):
            self.underflows += 1
        try:
            self._render(outdata, int(frames))
        except Exception as ex:
            outdata.fill(0)
            if not self._logged_render:
                self._logged_render = True
                log.error(f"SoundFont render failed: {ex}")

    def _render(self, outdata, frames: int) -> None:
        synth = self.synth
        pcm = self._pcm
        if synth is None or pcm is None or fluid_synth_write_s16 is None:
            outdata.fill(0)
            return
        # The device may ask for more than one block at a time: render all of
        # it, a block at a time, rather than padding the rest with silence
        done = 0
        while done < frames:
            count = min(frames - done, BLOCK_FRAMES)
            with self._lock:
                fluid_synth_write_s16(
                    synth.synth,
                    count,
                    self._pcm_buf,
                    0,
                    2,
                    self._pcm_buf,
                    1,
                    2,
                )
            copy_s16(pcm[: count * 2], outdata[done : done + count])
            done += count


def _device_label(index: Optional[int], devices: list[tuple[str, int]]) -> str:
    """
    The label listed for an index, or ``""`` for the default.

    :param index: Optional[int] sounddevice index
    :param devices: list of ``(label, index)``
    :return: str
    """
    if index is None:
        return ""
    return next((label for label, device in devices if device == index), "")


def _new_synth():
    if _fluidsynth_module is None:
        raise RuntimeError("fluidsynth is not installed")
    return _fluidsynth_module.Synth(samplerate=SAMPLE_RATE)


def _output_stream(**kwargs):
    if _sounddevice_module is None:
        raise RuntimeError("sounddevice is not installed")
    return _sounddevice_module.OutputStream(**kwargs)
