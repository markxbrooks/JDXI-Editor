"""
The connection to the JD-Xi, in one place.

Every window asks this object whether the JD-Xi can be talked to, instead
of looking at the MIDI ports on its own:

    OFFLINE    no ports open, or the JD-Xi is not there
    DETECTED   both ports open: not yet known to be a JD-Xi
    VERIFYING  Identity Request sent, waiting for the reply
    ONLINE     a Roland JD-Xi answered: reading and writing allowed
    UNSTABLE   ONLINE, but requests went unanswered: writes still go out,
               nothing is shown as verified until a whole reading succeeds

A JD-Xi switched off leaves its USB MIDI ports open on some systems: while
ONLINE, a JD-Xi silent for SILENT_ASK_S is asked who it is; silent for
LOST_AFTER_S it is OFFLINE (and asked again, quietly, until it answers).

A port merely named "JD-Xi" is not enough: the device has to answer the
Identity Request as a Roland JD-Xi (manufacturer 41h, family 0Eh).
"""

from __future__ import annotations

import os
import weakref
from typing import Optional, Sequence

from PySide6.QtCore import QObject, QTimer, Signal

OFFLINE = "offline"
DETECTED = "detected"
VERIFYING = "verifying"
ONLINE = "online"
UNSTABLE = "unstable"
STATES = (OFFLINE, DETECTED, VERIFYING, ONLINE, UNSTABLE)

ROLAND = 0x41
JDXI_FAMILY = 0x0E
POLL_MS = 1000
VERIFY_RETRY_MS = 3000  # a device that does not answer is asked again this often
UNSTABLE_AFTER = 2  # unanswered requests in a row
SILENT_ASK_S = 3.0  # an ONLINE JD-Xi heard nothing from for this long is asked who it is
LOST_AFTER_S = 8.0  # ... and after this long without an answer it is OFFLINE
# off in the tests (env JDXI_SILENCE_CHECK=0): their simulated JD-Xis come and go between tests
# on the one shared helper, and a «JD-Xi back» re-reading everything would cut into the next test
SILENCE_CHECK = os.environ.get("JDXI_SILENCE_CHECK", "1") != "0"


def ports_open(helper) -> bool:
    """Both MIDI ports of *helper* open (a reading needs to send and to receive)."""
    if helper is None:
        return False
    for name in ("midi_out", "midi_in"):
        port = getattr(helper, name, None)
        if port is None:
            return False
        is_open = getattr(port, "is_port_open", None)
        try:
            if callable(is_open) and not is_open():
                return False
        except Exception:
            return False
    return True


def is_jdxi_identity(data: Sequence[int]) -> bool:
    """An Identity Reply from a Roland JD-Xi (*data* with or without F0/F7)."""
    data = [int(b) for b in data]
    if data[:1] == [0xF0]:
        data = data[1:]
    # 7E dev 06 02 41 0E 03 ...
    return (len(data) >= 6 and data[0] == 0x7E and data[2] == 0x06 and data[3] == 0x02
            and data[4] == ROLAND and data[5] == JDXI_FAMILY)


class Connection(QObject):
    """The state of the connection to one JD-Xi (one MIDI helper)."""

    changed = Signal(str)  # the new state
    _identity_seen = Signal(object)  # from the MIDI input thread to this object's thread

    def __init__(self, helper, poll_ms: int = POLL_MS, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._helper = weakref.ref(helper) if helper is not None else (lambda: None)
        self.state = OFFLINE
        self.ever_online = False  # this session: the start-up warning is shown once
        self._unanswered = 0
        self._last_ask = None
        self._last_heard: Optional[float] = None  # time.monotonic() of the last MIDI from the JD-Xi
        self._lost = False  # went silent: OFFLINE while its ports are still open
        self._timer = QTimer(self)
        self._timer.setInterval(poll_ms)
        self._timer.timeout.connect(self.poll)
        self._identity_seen.connect(self.identity_reply)
        if poll_ms > 0:
            self._timer.start()

    # ------------------------------------------------------------- queries
    @property
    def helper(self):
        return self._helper()

    def can_talk(self) -> bool:
        """The JD-Xi answered and is still there: reading and writing allowed."""
        return self.state in (ONLINE, UNSTABLE)

    def verified(self) -> bool:
        """Results can be shown as verified (not while answers go missing)."""
        return self.state == ONLINE

    # ------------------------------------------------------------- changes
    def _set(self, state: str) -> None:
        if state == self.state:
            return
        self.state = state
        if state == ONLINE:
            self.ever_online = True
            self.heard()  # it just answered: silence counts from now
        self.changed.emit(state)

    def poll(self) -> None:
        """Follow the ports; ask a newly found device who it is; notice a JD-Xi gone silent."""
        import time

        if not ports_open(self.helper):
            self._unanswered = 0
            self._lost = False
            self._set(OFFLINE)
            return
        if self._lost:  # switched off: asked now and then, OFFLINE until it answers
            self._ask_identity()
            return
        if self.state in (ONLINE, UNSTABLE):
            if not SILENCE_CHECK:
                return
            now = time.monotonic()
            if self._last_heard is None:
                self._last_heard = now
            silent = now - self._last_heard
            if silent >= LOST_AFTER_S:
                self._lost = True
                self._set(OFFLINE)
            elif silent >= SILENT_ASK_S:
                self._ask_identity()
            return
        if self.state == OFFLINE:
            self._set(DETECTED)
        if self.state in (DETECTED, VERIFYING):
            self._ask_identity()

    def heard(self) -> None:
        """Any MIDI from the device (from the MIDI input thread): it is still there."""
        import time

        self._last_heard = time.monotonic()

    def _ask_identity(self) -> None:
        import time

        now = time.monotonic()
        quiet = self.state != DETECTED  # asked recently: not again before the retry time
        if quiet and self._last_ask is not None \
                and (now - self._last_ask) * 1000 < VERIFY_RETRY_MS:
            return
        self._last_ask = now
        helper = self.helper
        send = getattr(helper, "send_identity_request", None)
        if callable(send) and send() and self.state == DETECTED:
            self._set(VERIFYING)  # (an answer may already have come: then it is ONLINE)

    def identity_seen(self, data: Sequence[int]) -> None:
        """From any thread (the MIDI input): handled in this object's thread."""
        self._identity_seen.emit(list(data))

    def identity_reply(self, data: Sequence[int]) -> None:
        """An Identity Reply came in: a JD-Xi makes the connection ONLINE."""
        if not is_jdxi_identity(data):
            return
        self.heard()
        if self.state in (DETECTED, VERIFYING, OFFLINE) and ports_open(self.helper):
            self._unanswered = 0
            self._lost = False
            self._set(ONLINE)

    def request_unanswered(self) -> None:
        """A request to the JD-Xi got no answer in time."""
        if self.state not in (ONLINE, UNSTABLE):
            return
        self._unanswered += 1
        if self._unanswered >= UNSTABLE_AFTER:
            self._set(UNSTABLE)

    def request_answered(self) -> None:
        self._unanswered = 0

    def reading_complete(self) -> None:
        """A whole reading succeeded: answers arrive again."""
        self._unanswered = 0
        if self.state == UNSTABLE:
            self._set(ONLINE)

    def set_state_for_tests(self, state: str) -> None:
        assert state in STATES
        self._set(state)


def connection_for(helper) -> Optional[Connection]:
    """The Connection of *helper* (made the first time; None without a helper)."""
    if helper is None:
        return None
    existing = getattr(helper, "_jdxi_connection", None)
    if isinstance(existing, Connection):
        return existing
    try:
        connection = Connection(helper)
        helper._jdxi_connection = connection
    except Exception:  # a test double that takes no attributes
        return None
    return connection


def can_talk(helper) -> bool:
    """For the windows: the JD-Xi can be read and written through *helper*
    (looked at now: a closed port counts at once, a new one is asked who it is)."""
    connection = connection_for(helper)
    if connection is None:
        return False
    connection.poll()
    return connection.can_talk()
