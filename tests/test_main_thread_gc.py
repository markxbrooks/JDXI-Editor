"""Garbage collection runs on the main thread only (a cycle with Qt objects
collected in the request queue's thread crashed the macOS runner)."""

import gc
import threading

from PySide6.QtWidgets import QApplication, QWidget

from jdxi_editor.ui import main_thread_gc

APP = QApplication.instance() or QApplication([])


class _Cycle:
    def __init__(self):
        self.me = self
        self.widget = QWidget()


def test_a_cycle_made_in_a_thread_is_collected_on_the_main_thread():
    was_enabled = gc.isenabled()
    holder = main_thread_gc.install(APP)
    try:
        assert not gc.isenabled()
        collected_in = []

        class Watched(_Cycle):
            def __del__(self):
                collected_in.append(threading.current_thread() is threading.main_thread())

        def worker():
            for _ in range(5):
                Watched()
            [object() for _ in range(50_000)]  # well past generation 0's threshold

        thread = threading.Thread(target=worker)
        thread.start()
        thread.join()
        assert collected_in == []  # nothing collected in the thread
        gc.collect()  # what the timer does when a generation is due
        assert collected_in and all(collected_in)
    finally:
        holder.timer.stop()
        holder.deleteLater()
        if was_enabled:
            gc.enable()


def test_collect_if_due_follows_the_thresholds():
    was_enabled = gc.isenabled()
    gc.disable()
    try:
        gc.collect()
        assert main_thread_gc.collect_if_due() == 0  # nothing due right after a collection
        cycles = [_Cycle() for _ in range(gc.get_threshold()[0] + 10)]
        del cycles
        assert main_thread_gc.collect_if_due() > 0
    finally:
        if was_enabled:
            gc.enable()
