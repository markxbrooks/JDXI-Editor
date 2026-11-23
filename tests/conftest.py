"""Test-wide setup."""

import os

import pytest

# Tests check the built-in controller maps, not the user's edited copy in
# ~/.jdxi_editor/midi_controllers.json
os.environ["JDXI_EDITOR_MIDI_CONTROLLERS"] = ""


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
