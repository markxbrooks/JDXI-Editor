"""
jdxi_editor.midi.io.request_queue
One paced queue for all SysEx sent with send_with_delay.

The JD-Xi answers one RQ1 (data request) at a time and drops requests that
arrive while it is still sending a reply. Editors used to start a thread each
on program change, so dozens of requests (many identical) went out within a
few milliseconds and about half were never answered.

The queue sends one message at a time from a single worker thread:

- an RQ1 is followed by a wait for the DT1 reply at the same address (or a
  timeout), then a short gap
- any other message is followed by MIDI_SLEEP_TIME, as before
- a request that is already queued or waiting for its reply is not queued
  again; the reply reaches every listener anyway

Replies are reported through notify_reply(); the MIDI helper's JDXiDevice
owns the queue and passes on every incoming message.

Example:
    >>> sent = []
    >>> queue = SysExRequestQueue(sent.append, reply_timeout=0.01)
    >>> rq1 = bytes.fromhex("F0 41 10 00 00 00 0E 11 19 42 00 00 00 00 00 40 65 F7")
    >>> queue.submit([rq1, rq1])
    1
    >>> queue.wait_idle(1.0)
    True
    >>> len(sent)
    1
"""

from __future__ import annotations

import threading
import time
from collections import deque
from dataclasses import dataclass
from typing import Any, Callable, Iterable, Optional, Sequence, Union

from decologr import Decologr as log

from jdxi_editor.midi.sleep import MIDI_SLEEP_TIME

ROLAND_ID = 0x41
RQ1_COMMAND = 0x11
DT1_COMMAND = 0x12
SYSEX_START = 0xF0

REPLY_TIMEOUT = 0.3  # seconds to wait for a DT1 reply before moving on
REPLY_GAP = 0.005  # pause after a reply before the next request



def roland_address(data: Sequence[int], command: int) -> Optional[str]:
    """
    4-byte address (hex) of a Roland SysEx message with *command*, else None.

    Accepts the message with or without F0 (mido's ``sysex.data`` omits it).
    Layout without F0: 41, device, model×4, command, address×4, ...
    """
    data = list(data)
    if data and data[0] == SYSEX_START:
        data = data[1:]
    if len(data) < 11 or data[0] != ROLAND_ID or data[6] != command:
        return None
    return "".join(f"{b:02x}" for b in data[7:11])


@dataclass
class _Item:
    data: bytes
    reply_address: Optional[str]  # set for RQ1s


class SysExRequestQueue:
    """Send messages one at a time, waiting for each RQ1's reply."""

    def __init__(
        self,
        send: Callable[[bytes], Any],
        *,
        reply_timeout: float = REPLY_TIMEOUT,
        reply_gap: float = REPLY_GAP,
        message_gap: float = MIDI_SLEEP_TIME,
    ):
        self._send = send
        self._reply_timeout = reply_timeout
        self._reply_gap = reply_gap
        self._message_gap = message_gap
        self._items: deque[_Item] = deque()
        self._pending: set[bytes] = set()  # queued or awaiting reply
        self._cond = threading.Condition()
        self._reply = threading.Event()
        self._awaiting: Optional[str] = None
        self._busy = False
        self._worker: Optional[threading.Thread] = None

    def submit(self, messages: Iterable[Union[str, bytes, Sequence[int]]]) -> int:
        """Queue *messages* (hex strings or bytes); returns how many were queued."""
        queued = 0
        with self._cond:
            for message in messages:
                if not message:
                    continue
                data = (
                    bytes.fromhex(message) if isinstance(message, str) else bytes(message)
                )
                address = roland_address(data, RQ1_COMMAND)
                if address is not None:
                    if data in self._pending:
                        continue
                    self._pending.add(data)
                self._items.append(_Item(data, address))
                queued += 1
            if queued:
                self._ensure_worker()
                self._cond.notify()
        return queued

    def notify_reply(self, data: Sequence[int]) -> None:
        """Report incoming SysEx; a DT1 at the awaited address ends the wait."""
        address = roland_address(data, DT1_COMMAND)
        if address is not None and address == self._awaiting:
            self._reply.set()

    def clear(self) -> int:
        """
        Drop everything not yet sent (e.g. on disconnect); a request awaiting
        its reply stops waiting. Returns how many messages were dropped.
        """
        with self._cond:
            dropped = len(self._items)
            self._items.clear()
            self._pending.clear()
            self._cond.notify_all()
        self._reply.set()
        return dropped

    def wait_idle(self, timeout: float) -> bool:
        """Block until everything queued has been sent (for tests and shutdown)."""
        deadline = time.monotonic() + timeout
        with self._cond:
            while self._items or self._busy:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return False
                self._cond.wait(remaining)
        return True

    def _ensure_worker(self) -> None:
        if self._worker is None or not self._worker.is_alive():
            self._worker = threading.Thread(
                target=self._run, name="SysExRequestQueue", daemon=True
            )
            self._worker.start()

    def _run(self) -> None:
        while True:
            with self._cond:
                while not self._items:
                    self._busy = False
                    self._cond.notify_all()
                    self._cond.wait()
                item = self._items.popleft()
                self._busy = True
            self._process(item)

    def _process(self, item: _Item) -> None:
        self._reply.clear()
        self._awaiting = item.reply_address
        try:
            self._send(item.data)
        except Exception as ex:
            log.error(f"Error {ex} sending {item.data.hex(' ')}", scope="SysExRequestQueue")
        if item.reply_address is not None:
            if self._reply.wait(self._reply_timeout):
                time.sleep(self._reply_gap)
            else:
                log.debug(
                    f"No reply to RQ1 at {item.reply_address}", scope="SysExRequestQueue"
                )
            self._awaiting = None
            with self._cond:
                self._pending.discard(item.data)
        else:
            time.sleep(self._message_gap)
