"""
jdxi_editor.midi.io.device
The connected JD-Xi as the editor sees it.

One JDXiDevice holds the state that belongs to the synth rather than to any
editor:

- ``requests``: the SysExRequestQueue that paces RQ1 requests, one reply at a
  time
- ``memory``: the SynthMemory mirror of the synth's parameter bytes, which
  patches are saved from
- ``echo_guard``: the EchoGuard that stops data received from the synth being
  written straight back to it

The MIDI helper owns one (``helper.device``) and reports every message to it:
``received()`` for incoming messages, ``before_send()`` and ``sent()`` for
outgoing ones.

Example:
    >>> sent = []
    >>> device = JDXiDevice(sent.append)
    >>> reply = bytes.fromhex("F0 41 10 00 00 00 0E 12 19 42 00 00 01 02 22 F7")
    >>> device.received(reply)
    >>> device.memory.read(bytes.fromhex("19 42 00 00"), 2)
    b'\\x01\\x02'
    >>> with device.applying_device_data():
    ...     device.before_send(reply)   # an editor echoing the reply
    False
    >>> device.received([0xC0, 0x05])  # program change: the program is replaced
    >>> device.memory.sections()
    []
"""

from __future__ import annotations

from contextlib import AbstractContextManager
from typing import Any, Callable, Iterable, Sequence, Union

from jdxi_editor.midi.io.echo_guard import DEFAULT_ECHO_GUARD, EchoGuard
from jdxi_editor.midi.io.request_queue import SYSEX_START, SysExRequestQueue
from jdxi_editor.midi.io.synth_memory import SynthMemory

PROGRAM_CHANGE_STATUS = 0xC0


def _is_program_change(message: Sequence[int]) -> bool:
    return bool(message) and int(message[0]) & 0xF0 == PROGRAM_CHANGE_STATUS


class JDXiDevice:
    """Request queue, memory mirror and echo guard of one JD-Xi."""

    def __init__(
        self,
        send: Callable[[Sequence[int]], Any],
        requests: SysExRequestQueue | None = None,
        memory: SynthMemory | None = None,
        echo_guard: EchoGuard | None = None,
    ) -> None:
        """
        :param send: sends one raw MIDI message (used by the request queue)
        """
        self.requests = requests or SysExRequestQueue(send)
        self.memory = memory or SynthMemory()
        # Shared by default: the scope is per thread, and the input handler
        # and output handler must agree on it
        self.echo_guard = echo_guard or DEFAULT_ECHO_GUARD

    # --- Requests ---------------------------------------------------------

    def request(self, messages: Iterable[Union[str, bytes, Sequence[int]]]) -> int:
        """Queue RQ1 (and other) messages; returns how many were queued."""
        return self.requests.submit(messages)

    def applying_device_data(self) -> AbstractContextManager[None]:
        """Scope in which this thread applies data received from the JD-Xi."""
        return self.echo_guard.applying()

    # --- Traffic ----------------------------------------------------------

    def received(self, message: Sequence[int]) -> None:
        """
        A message from the JD-Xi (SysEx with or without F0/F7, or channel data).

        A DT1 reply lets the queue send its next request and is recorded in
        memory; a program change replaces the temporary program, so memory is
        cleared.
        """
        data = [int(b) for b in message]
        if _is_program_change(data):
            self.memory.clear()
            return
        if data and data[0] != SYSEX_START and data[0] >= 0x80:
            return  # other channel messages
        self.requests.notify_reply(data)
        self.memory.record_dt1(data)

    def before_send(self, message: Sequence[int]) -> bool:
        """False if *message* must not be sent (a DT1 echoing received data)."""
        return not self.echo_guard.is_echo(message)

    def sent(self, message: Sequence[int]) -> None:
        """A message the editor sent: what the synth now holds."""
        data = [int(b) for b in message]
        if _is_program_change(data):
            self.memory.clear()
        else:
            self.memory.record_dt1(data)


def device_for(owner: Any) -> JDXiDevice:
    """
    The JDXiDevice of a MIDI helper (``owner.device``).

    For objects that are not MidiIOControllers (tests, tools), a device is
    created on first use and kept on the object.
    """
    device = getattr(owner, "device", None)
    if isinstance(device, JDXiDevice):
        return device
    device = getattr(owner, "_jdxi_device", None)
    if device is None:
        device = JDXiDevice(owner.send_raw_message)
        owner._jdxi_device = device
    return device
