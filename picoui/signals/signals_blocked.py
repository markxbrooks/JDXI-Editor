"""
Block Signals Context Manager
"""

from contextlib import contextmanager

from PySide6.QtWidgets import QWidget


@contextmanager
def blocked_signals(widget: QWidget):
    """Temporarily block Qt signals for a widget within the context."""
    blockable = hasattr(widget, "blockSignals")
    if blockable:
        widget.blockSignals(True)
    try:
        yield
    finally:
        if blockable:
            widget.blockSignals(False)
