"""
jdxi_editor.midi.io.echo_guard
Stop editors echoing data received from the JD-Xi back to it.

When a DT1 reply arrives, editors set their controls from it. Several
composite widgets (envelopes, PWM, filter, WMT ranges) send a parameter
change for every value set this way, so each reply used to be written back to
the synth, sometimes with different values.

MidiInHandler delivers device SysEx inside ``device.applying_device_data()``
(see JDXiDevice); while that is active on the current thread, MidiOutHandler
drops outgoing DT1
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

class EchoGuard:
    """Per-thread scope in which outgoing DT1s are echoes of received data."""

    def __init__(self) -> None:
        self._state = threading.local()

    @contextmanager
    def applying(self) -> Iterator[None]:
        """Scope in which this thread is applying data received from the JD-Xi."""
        self._state.depth = getattr(self._state, "depth", 0) + 1
        try:
            yield
        finally:
            self._state.depth -= 1

    def is_active(self) -> bool:
        return getattr(self._state, "depth", 0) > 0

    def is_echo(self, message: Sequence[int]) -> bool:
        """True for a DT1 sent while this thread applies data from the JD-Xi."""
        return self.is_active() and roland_address(message, DT1_COMMAND) is not None


# The guard the MIDI helper's device uses (see JDXiDevice)
DEFAULT_ECHO_GUARD = EchoGuard()


def applying_device_data():
    """Scope in which this thread is applying data received from the JD-Xi."""
    return DEFAULT_ECHO_GUARD.applying()


def is_applying_device_data() -> bool:
    return DEFAULT_ECHO_GUARD.is_active()


def is_device_echo(message: Sequence[int]) -> bool:
    """True for a DT1 sent while this thread applies data from the JD-Xi."""
    return DEFAULT_ECHO_GUARD.is_echo(message)
