"""
jdxi_editor.midi.io.echo_guard
Stop editors echoing data received from the JD-Xi back to it.

When a DT1 reply arrives, editors set their controls from it. Several
composite widgets (envelopes, PWM, filter, WMT ranges) send a parameter
change for every value set this way, so each reply used to be written back to
the synth, sometimes with different values.

MidiInHandler delivers device SysEx inside ``applying_device_data()``; while
that is active on the current thread, MidiOutHandler drops outgoing DT1
(data set) messages. Requests (RQ1) and other messages still go out, and the
scope is per thread, so the request queue's worker is not affected.

Example:
    >>> is_applying_device_data()
    False
    >>> with applying_device_data():
    ...     is_applying_device_data()
    True
"""

import threading
from contextlib import contextmanager
from typing import Iterator, Sequence

from jdxi_editor.midi.io.request_queue import DT1_COMMAND, roland_address

_state = threading.local()


@contextmanager
def applying_device_data() -> Iterator[None]:
    """Scope in which this thread is applying data received from the JD-Xi."""
    _state.depth = getattr(_state, "depth", 0) + 1
    try:
        yield
    finally:
        _state.depth -= 1


def is_applying_device_data() -> bool:
    return getattr(_state, "depth", 0) > 0


def is_device_echo(message: Sequence[int]) -> bool:
    """True for a DT1 sent while this thread applies data from the JD-Xi."""
    return is_applying_device_data() and roland_address(message, DT1_COMMAND) is not None
