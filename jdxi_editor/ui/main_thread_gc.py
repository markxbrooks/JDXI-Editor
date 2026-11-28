"""
Python's garbage collector runs on the main (Qt) thread only.

Left automatic, the collector runs in whichever thread happens to allocate
when a generation is full: the MIDI request queue's or a recording thread.
Collecting a reference cycle that holds Qt objects there destroys them
outside the main thread, and Qt crashes (a segmentation fault seen on macOS:
"Garbage-collecting" in the request queue's thread).

So automatic collection is turned off and the same thresholds are checked
from the main thread: by a timer in the app (install), after each test in
the tests (collect_if_due).
"""

from __future__ import annotations

import gc
from typing import Optional

from PySide6.QtCore import QObject, QTimer

INTERVAL_MS = 500


def collect_if_due() -> int:
    """Collect the generations whose counts passed their thresholds, as the
    automatic collector would; returns the objects collected."""
    threshold = gc.get_threshold()
    counts = gc.get_count()
    collected = 0
    for generation in (2, 1, 0):  # the oldest due includes the younger ones
        if threshold[generation] and counts[generation] > threshold[generation]:
            collected += gc.collect(generation)
            break
    return collected


class MainThreadGC(QObject):
    def __init__(self, parent: Optional[QObject] = None, interval_ms: int = INTERVAL_MS):
        super().__init__(parent)
        gc.disable()
        self.timer = QTimer(self)
        self.timer.timeout.connect(collect_if_due)
        self.timer.start(interval_ms)


def install(app: QObject) -> MainThreadGC:
    """Turn automatic collection off and collect from *app*'s thread (call once,
    after creating the QApplication); the object lives as long as *app*."""
    return MainThreadGC(app)
