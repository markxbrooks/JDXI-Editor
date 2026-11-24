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

import threading
from contextlib import contextmanager
from itertools import count
from typing import Iterator, Optional

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
