"""
PortAudio's picture of the audio hardware, and how to make it current.

PortAudio builds its device list once, in ``Pa_Initialize``, and never looks
again. A process that outlives a change to the hardware -- AirPods
connecting, headphones unplugged, a dock pulled out -- keeps asking for
devices by positions that have since moved or gone, and CoreAudio answers
that with ``paInternalError`` (-9986). Opening the *default* output fails the
same way, because PortAudio resolved which device that was at startup too.

That is what wedges SoundFont playback after a route change: the editor runs
for hours, the headphones come off, and every attempt to open an output from
then on fails until the application is restarted.

The only remedy PortAudio offers is to terminate it and initialise it again.
That is process-wide: it tears down *every* open stream, not only the one
being reopened. So anything else that is listening registers itself here
with :func:`holding`, and a refresh is refused while a holder is active
rather than silencing a recording in progress.
"""

import re
import threading
from contextlib import contextmanager
from itertools import count
from typing import Callable, Iterator, Optional

from decologr import Decologr as log

_SCOPE = "portaudio"

_lock = threading.RLock()
_holders: dict[int, str] = {}
_tokens = count(1)


def _sounddevice():
    """
    The installed sounddevice module, or None.

    Imported on use: the library is optional, and importing it loads
    PortAudio.

    :return: module or None
    """
    try:
        import sounddevice
    except Exception:
        return None
    return sounddevice


def hold(label: str) -> int:
    """
    Record that a stream is open, so a refresh will not close it.

    :param label: str what is listening, for the log
    :return: int token to pass to :func:`release`
    """
    token = next(_tokens)
    with _lock:
        _holders[token] = label
    return token


def release(token: Optional[int]) -> None:
    """
    Drop a hold taken by :func:`hold`. An unknown token is ignored.

    :param token: Optional[int]
    :return: None
    """
    if token is None:
        return
    with _lock:
        _holders.pop(token, None)


@contextmanager
def holding(label: str) -> Iterator[int]:
    """
    Hold for the duration of a block.

    :param label: str what is listening
    :return: Iterator[int] the token
    """
    token = hold(label)
    try:
        yield token
    finally:
        release(token)


def holders() -> list[str]:
    """
    Labels of the streams currently open.

    :return: list[str]
    """
    with _lock:
        return sorted(_holders.values())


def refresh_devices(module=None) -> bool:
    """
    Make PortAudio read the hardware again.

    Refused, and nothing is torn down, while another stream is open: see
    the module docstring. The caller's own stream must already be closed.

    :param module: sounddevice, for tests; the installed library otherwise
    :return: bool True when the device list was rebuilt
    """
    source = _sounddevice() if module is None else module
    if source is None:
        return False
    with _lock:
        busy = sorted(_holders.values())
        if busy:
            log.message(
                "Not refreshing the audio device list: still listening on "
                + ", ".join(busy),
                scope=_SCOPE,
            )
            return False
        try:
            source._terminate()
            source._initialize()
        except Exception as ex:
            log.error(f"Could not refresh the audio device list: {ex}", scope=_SCOPE)
            return False
    log.message("Audio device list refreshed", scope=_SCOPE)
    return True


# --- Naming a device so the name survives the hardware changing --------------
#
# An index is a position in the list PortAudio built at startup, so it is the
# one thing about a device that does not last. The name does, and on Windows
# the host API goes with it: one device is listed once per API, under exactly
# the same name each time, so the name alone is not enough to tell three
# entries apart in a menu either.

_INDEX_SUFFIX = re.compile(r" \(\d+\)$")

#: The device's own name for each label :func:`label_devices` has handed out.
#: A label may carry the host API, and a position after it, to tell devices of
#: the same name apart. That suffix is ours, and it is recorded here rather
#: than parsed back off, because a trailing parenthesis is not a reliable sign
#: of one: "Speakers (Realtek(R) Audio)" is a real Windows device name.
#:
#: Entries are kept, not cleared per listing: inputs and outputs are labelled
#: by the same code, and emptying the map on one listing would leave the
#: other's labels to be guessed at by :data:`_INDEX_SUFFIX`.
_plain_names: dict[str, str] = {}


def host_api_name(device, apis: list) -> str:
    """
    Name of the host API a device belongs to, or ``""``.

    :param device: a sounddevice device record
    :param apis: the result of ``query_hostapis()``
    :return: str
    """
    try:
        return str(apis[int(device["hostapi"])]["name"])
    except Exception:
        return ""


def label_devices(
    devices,
    apis: list,
    channels_key: str,
    suffix: Optional[Callable[[dict], str]] = None,
) -> list[tuple[str, int]]:
    """
    Devices with at least one channel, as ``(label, index)``.

    A name that occurs once is the label. A repeated one is told apart by its
    host API, and only when that is repeated too -- a pair of identical
    interfaces -- by its position, which is the last resort because it moves.

    :param devices: the result of ``query_devices()``
    :param apis: the result of ``query_hostapis()``; ``[]`` is tolerated
    :param channels_key: str "max_input_channels" or "max_output_channels"
    :param suffix: Optional[Callable] extra text for a label, from the record
    :return: list[tuple[str, int]]
    """
    found = []
    for index, device in enumerate(devices):
        try:
            channels = int(device[channels_key])
        except Exception:
            continue
        if channels <= 0:
            continue
        found.append(
            (str(device["name"]), host_api_name(device, apis), int(index), device)
        )

    names = [name for name, _api, _index, _device in found]
    with_api = [(name, api) for name, api, _index, _device in found]
    labelled = []
    for name, api, index, device in found:
        if names.count(name) == 1:
            label = name
        elif api and with_api.count((name, api)) == 1:
            label = f"{name} ({api})"
        elif api:
            label = f"{name} ({api}, {index})"
        else:
            label = f"{name} ({index})"
        if suffix is not None:
            label += suffix(device)
        labelled.append((label, index))
        _plain_names[label] = name
    return labelled


def plain_name(label: str) -> str:
    """
    A device's own name, without the suffix added for a repeated one.

    Looked up in :data:`_plain_names`, so no parenthesis in a genuine device
    name is ever mistaken for the suffix. A label this module did not hand
    out -- one built by hand, or stored by an older version -- falls back to
    dropping a trailing `` (index)``.

    :param label: str device label
    :return: str
    """
    if not label:
        return ""
    plain = _plain_names.get(label)
    if plain is not None:
        return plain
    return _INDEX_SUFFIX.sub("", label)
