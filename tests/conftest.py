"""Test-wide setup."""

import os

import pytest

# Tests check the built-in controller maps, not the user's edited copy in
# ~/.jdxi_editor/midi_controllers.json
os.environ["JDXI_EDITOR_MIDI_CONTROLLERS"] = ""


@pytest.fixture(scope="module", autouse=True)
def _destroy_leftover_windows():
    """
    Delete every top-level widget a test module leaves behind.

    Tests end with window.close(), which only hides a window: without
    WA_DeleteOnClose it stays in QApplication.allWidgets() for the rest of the
    session. Switching skins restyles every widget there (rack_skin's
    _restyle_application), so by test_rack_skin.py a single skin change was
    walking several leaked editors and took minutes, and touching a widget
    whose C++ half was half-gone crashed the run on the CI runners.

    Module scope, not function scope: many modules share one editor between
    their tests through a module-scoped fixture. An autouse fixture is set up
    before, and torn down after, the module's own fixtures.
    """
    yield
    try:
        from PySide6.QtCore import QCoreApplication, QEvent
        from PySide6.QtWidgets import QApplication
    except ImportError:
        return
    app = QApplication.instance()
    if app is None:
        return
    for widget in app.topLevelWidgets():
        try:
            widget.close()
            widget.deleteLater()
        except RuntimeError:
            # the C++ object is already gone
            continue
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    # Deliver what the module left queued (QTimer.singleShot and the like)
    # now, so a callback that outlives its widget fails in this module's
    # teardown rather than inside an unrelated test that happens to run next
    app.processEvents()
