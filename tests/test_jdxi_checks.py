"""
Checks against a JD-Xi that need no ears.

The same tests run twice:

    pytest tests/test_jdxi_checks.py               on the simulated JD-Xi (every run, no hardware)
    pytest -m hardware tests/test_jdxi_checks.py   on the real JD-Xi, on its MIDI ports

With the real JD-Xi: close the editor first (the ports are not shared on
Windows). Every test leaves the JD-Xi's temporary program as it found it.

They cover: identity, a whole reading, a write pending until read back,
and a reconnection with nothing changed and with a part changed and put back.

From JD-Xi Studio's tests/test_jdxi_checks.py (the checks that need its
v2 editors are not here).
"""

from __future__ import annotations

import os
import sys
import time
from typing import Optional

import pytest
from PySide6.QtWidgets import QApplication

sys.path.insert(0, os.path.dirname(__file__))

from jdxi_editor.midi.io.synth_memory import build_dt1  # noqa: E402
from jdxi_editor.midi.io.synth_state import parts_that_differ  # noqa: E402

ANALOG = bytes.fromhex("19420000")
ANALOG_AMP_LEVEL = 0x2A  # a safe parameter to change and put back
PARTS = ("program", "digital_1", "digital_2", "analog", "drums")


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def wait_for(condition, seconds: float = 10.0) -> bool:
    from PySide6.QtTest import QTest

    end = time.monotonic() + seconds
    while time.monotonic() < end:
        if condition():
            return True
        QTest.qWait(20)
    return bool(condition())


def _named_analog_tone() -> list:
    """An Analog tone the simulated JD-Xi starts with: a name and an amp level."""
    values = [0x40] * 0x40
    values[:12] = list(b"Check Tone  ")
    values[ANALOG_AMP_LEVEL] = 100
    return [bytes(build_dt1(ANALOG, values))]


class JDXi:
    """The instrument the checks talk to: simulated, or the real one."""

    def __init__(self, kind: str):
        from jdxi_editor.midi.io.device import device_for
        from jdxi_editor.midi.io.helper import MidiIOHelper
        from jdxi_editor.midi.sysex.request.read_session import patch_section_requests

        self.kind = kind
        self.helper = MidiIOHelper()
        self.fake = None
        self.reads: list = []  # each read: complete, seconds, sections not read
        if kind == "simulated":
            from fake_jdxi import FakeJDXi

            self.fake = FakeJDXi(self.helper)
            self.fake.load(_named_analog_tone())
        else:
            found_in, found_out = self.helper.find_jdxi_ports()
            if (
                not found_in
                or not found_out
                or not self.helper.connect_port_names(found_in, found_out)
            ):
                pytest.skip("no JD-Xi on the MIDI ports (close the editor, connect the JD-Xi)")
        self.device = device_for(self.helper)
        self.device.requests.clear()  # nothing left queued by the tests before
        if self.fake is not None:  # as the editor's own path: what goes out is noted as sent
            to_jdxi = self.helper.send_raw_message

            def send(message):
                self.device.sent([int(b) for b in message])
                return to_jdxi(message)

            self.helper.send_raw_message = send
        self.requests = [rq for _label, rq in patch_section_requests()]

    def read_all(self) -> bool:
        from jdxi_editor.midi.sysex.request.read_session import start_read_session

        results = []
        # the editor's 8 s are for a JD-Xi; a CI virtual machine can take longer
        # for the simulated one: these checks are about what is read, not how fast
        session = start_read_session(
            self.helper,
            self.requests,
            on_finished=lambda r: results.append(r),
            timeout_ms=30000,
        )
        started = time.monotonic()
        assert wait_for(
            lambda: results or getattr(session, "_done", False), 60
        ), "the reading never ended"
        complete = bool(results and results[0].complete)
        missing = (
            [f"{s.label}: {s.status.value}" for s in results[0].sections if s.status.value != "ok"]
            if results
            else ["no result"]
        )
        self.reads.append((complete, round(time.monotonic() - started, 2), missing))
        return complete

    def diagnosis(self, before: Optional[dict] = None) -> str:
        """For a failure message: the reads and the bytes that differ from *before*."""
        lines = [f"reads: {self.reads}"]
        if before is not None:
            now = self.snapshot()
            for key in sorted(set(before) | set(now)):
                a, b = before.get(key, b""), now.get(key, b"")
                if a != b:
                    offsets = [
                        i
                        for i in range(max(len(a), len(b)))
                        if (a[i] if i < len(a) else None) != (b[i] if i < len(b) else None)
                    ]
                    lines.append(f"{key}: {len(a)}/{len(b)} bytes, differ at {offsets[:12]}")
        return "\n".join(lines[:16])

    def snapshot(self) -> dict:
        return self.device.state.snapshot()

    def send_section(self, key: str, data: bytes) -> bool:
        return bool(
            self.helper.send_raw_message(list(build_dt1(bytes.fromhex(key), list(data))))
        )

    def put_back(self, snapshot: dict) -> None:
        for key, data in sorted(snapshot.items()):
            self.send_section(key, data)
        wait_for(lambda: False, 0.3)  # let the JD-Xi take them

    def analog_byte(self, offset: int) -> int:
        return self.snapshot()["19420000"][offset]

    def close(self) -> None:
        if self.fake is None:
            try:
                self.helper.close_ports()
            except Exception:
                pass
        else:
            self.fake.detach()
            self.device.state.program_changed()


@pytest.fixture(params=["simulated", pytest.param("hardware", marks=pytest.mark.hardware)])
def jdxi(request, app):
    """The JD-Xi, its temporary program saved before and put back after."""
    instrument = JDXi(request.param)
    assert instrument.read_all(), "the JD-Xi's program could not be read whole"
    saved = instrument.snapshot()
    yield instrument
    instrument.put_back(saved)
    instrument.close()


def test_identity_makes_it_connected(jdxi):
    """Connected only once it answers as a JD-Xi."""
    from jdxi_editor.midi.io import connection as conn

    # a connection of its own, as at start-up: the shared one is left as it is
    shared = conn.connection_for(jdxi.helper)
    replies = []
    shared._identity_seen.connect(replies.append)
    try:
        fresh = conn.Connection(jdxi.helper, poll_ms=0)
        assert jdxi.helper.send_identity_request()
        assert wait_for(lambda: replies, 5), "no Identity Reply"
        fresh.set_state_for_tests(conn.VERIFYING)
        fresh.identity_reply(replies[0])
        assert fresh.state == conn.ONLINE, replies[0]
    finally:
        shared._identity_seen.disconnect(replies.append)


def test_the_whole_program_reads_back(jdxi):
    """Every part of the program, confirmed."""
    from jdxi_editor.midi.io.synth_state import part_of_address

    snapshot = jdxi.snapshot()
    assert {part_of_address(key) for key in snapshot} >= set(PARTS)


def test_a_write_is_pending_until_read_back(jdxi):
    """What is sent is not confirmed until the JD-Xi gives it back."""
    old = jdxi.analog_byte(ANALOG_AMP_LEVEL)
    new = old - 10 if old >= 10 else old + 10
    address = ANALOG[:3] + bytes([ANALOG_AMP_LEVEL])
    assert jdxi.helper.send_raw_message(list(build_dt1(address, [new])))
    assert jdxi.device.state.pending_count() >= 1
    assert not jdxi.device.state.is_confirmed(address)
    assert jdxi.read_all()
    assert jdxi.analog_byte(ANALOG_AMP_LEVEL) == new
    assert jdxi.device.state.is_confirmed(address)


def test_reconnection_with_nothing_changed(jdxi):
    """Read again, compare: the same."""
    before = jdxi.snapshot()
    assert jdxi.read_all()
    assert parts_that_differ(before, jdxi.snapshot()) == []


def test_reconnection_with_a_part_changed_tells_that_part(jdxi):
    """The Analog part changed while away: only it differs; put back, it is the same again."""
    before = jdxi.snapshot()
    old = before["19420000"][ANALOG_AMP_LEVEL]
    address = ANALOG[:3] + bytes([ANALOG_AMP_LEVEL])
    jdxi.helper.send_raw_message(list(build_dt1(address, [old - 10 if old >= 10 else old + 10])))
    assert jdxi.read_all()
    assert parts_that_differ(before, jdxi.snapshot()) == ["analog"], jdxi.diagnosis(before)
    jdxi.send_section("19420000", before["19420000"])
    wait_for(lambda: False, 0.3)
    assert jdxi.read_all()
    assert parts_that_differ(before, jdxi.snapshot()) == [], jdxi.diagnosis(before)
    assert jdxi.analog_byte(ANALOG_AMP_LEVEL) == old
