"""
Test-wide setup.

The tests run on in-memory MIDI ports instead of rtmidi's (from JD-Xi Studio).
Many tests build the MidiIOHelper, which opens rtmidi.MidiIn and
rtmidi.MidiOut: on machines without a MIDI API (Linux CI runners have no ALSA
sequencer) that fails, and elsewhere the result depends on what is plugged in.
So rtmidi's port classes are replaced, before any test module is imported,
with fakes that list one port named "JD-Xi" and record what is sent.

To use the real ports and a connected JD-Xi: ``pytest -m hardware``, or set
JDXI_TEST_REAL_MIDI=1.
"""

from __future__ import annotations

import gc
import os
from typing import Callable, Optional

import pytest

# Tests check the built-in controller maps, not the user's edited copy in
# ~/.jdxi_editor/midi_controllers.json
os.environ["JDXI_EDITOR_MIDI_CONTROLLERS"] = ""

import rtmidi

FAKE_JDXI_PORT = "JD-Xi (test)"


class FakeMidiPort:
    """In-memory stand-in for rtmidi.MidiIn / rtmidi.MidiOut."""

    ports = [FAKE_JDXI_PORT]

    def __init__(self, *_args, **_kwargs) -> None:
        self._open_port: Optional[int] = None
        self._callback: Optional[Callable] = None
        self._callback_data = None
        self.sent: list[list[int]] = []

    # --- ports
    def get_ports(self) -> list[str]:
        return list(self.ports)

    def get_port_count(self) -> int:
        return len(self.ports)

    def get_port_name(self, index: int, *_args) -> Optional[str]:
        return self.ports[index] if 0 <= index < len(self.ports) else None

    def open_port(self, port: int = 0, *_args, **_kwargs) -> "FakeMidiPort":
        if not 0 <= port < len(self.ports):
            raise rtmidi.InvalidPortError(f"Invalid port number: {port}")
        self._open_port = port
        return self

    def open_virtual_port(self, *_args, **_kwargs) -> "FakeMidiPort":
        self._open_port = 0
        return self

    def close_port(self) -> None:
        self._open_port = None

    def is_port_open(self) -> bool:
        return self._open_port is not None

    def delete(self) -> None:
        self.close_port()

    def get_current_api(self) -> int:
        return rtmidi.API_RTMIDI_DUMMY

    def set_client_name(self, *_args) -> None:
        pass

    def set_port_name(self, *_args) -> None:
        pass

    # --- input
    def set_callback(self, callback: Callable, data=None) -> None:
        self._callback, self._callback_data = callback, data

    def cancel_callback(self) -> None:
        self._callback = None

    def ignore_types(self, *_args, **_kwargs) -> None:
        pass

    def get_message(self) -> None:
        return None

    def receive(self, message: list[int], delta_time: float = 0.0) -> None:
        """Deliver a message to the input callback, as the JD-Xi would."""
        if self._callback is not None:
            self._callback((list(message), delta_time), self._callback_data)

    # --- output
    def send_message(self, message) -> None:
        self.sent.append(list(message))

    # --- context manager, as rtmidi's ports
    def __enter__(self) -> "FakeMidiPort":
        return self

    def __exit__(self, *_exc) -> None:
        self.close_port()

    # --- camelCase spellings used in parts of the code base
    getPortCount = get_port_count
    getPortName = get_port_name
    openPort = open_port
    closePort = close_port
    isPortOpen = is_port_open
    setCallback = set_callback
    ignoreTypes = ignore_types


class FakeMidiIn(FakeMidiPort):
    pass


class FakeMidiOut(FakeMidiPort):
    pass


def _wants_real_midi(config) -> bool:
    if os.environ.get("JDXI_TEST_REAL_MIDI") == "1":
        return True
    return "hardware" in (config.getoption("markexpr", default="") or "").replace(
        "not hardware", ""
    )


def pytest_configure(config) -> None:
    # Runs before the test modules are imported, so every MidiIOHelper the
    # tests create gets the fake ports
    if not _wants_real_midi(config):
        rtmidi.MidiIn = FakeMidiIn
        rtmidi.MidiOut = FakeMidiOut
    # As in the app, no garbage collection in other threads (the request
    # queue's): a cycle holding Qt objects collected there crashes Qt
    gc.disable()


def pytest_runtest_teardown(item, nextitem) -> None:
    from jdxi_editor.ui.main_thread_gc import collect_if_due

    collect_if_due()


_HELPER_METHODS = (
    "send_midi_message",
    "send_raw_message",
    "send_control_change",
    "send_program_change",
    "send_bank_select_and_program_change",
)


@pytest.fixture(autouse=True)
def _restore_the_shared_midi_helper():
    """
    Put back the sending methods a test replaced on the shared MidiIOHelper.

    It is a singleton: a test that patched send_raw_message and left it made
    the next tests send nothing through the real path. Replacements made by
    module fixtures, before the test, are kept.
    """
    try:
        from jdxi_editor.midi.io.helper import MidiIOHelper
    except Exception:  # pragma: no cover
        yield
        return
    helper = MidiIOHelper._instance
    before = {
        name: helper.__dict__[name]
        for name in _HELPER_METHODS
        if helper is not None and name in helper.__dict__
    }
    yield
    helper = MidiIOHelper._instance
    if helper is None:
        return
    for name in _HELPER_METHODS:
        if name in before:
            helper.__dict__[name] = before[name]
        else:
            helper.__dict__.pop(name, None)


@pytest.fixture(autouse=True)
def _flush_deferred_deletes():
    """
    Carry out the deleteLater() calls a test made, once it has finished.

    deleteLater() only posts a DeferredDelete event; nothing deletes the
    widget until an event loop dispatches it, and no test runs one.
    processEvents() does not count: Qt leaves DeferredDelete events to the
    loop that posted them. So every editor a test closed and "deleted" stayed
    alive for the rest of the session. A skin switch restyles every live
    widget (rack_skin._restyle_application), and after test_drum_editor_ui
    had left its DrumCommonEditors behind, one switch in test_rack_skin took
    minutes: the Windows runner spent 55 of its 61 minutes there.
    """
    yield
    try:
        from PySide6.QtCore import QCoreApplication, QEvent
    except ImportError:  # pragma: no cover - PySide6 is a hard dependency
        return
    if QCoreApplication.instance() is not None:
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
