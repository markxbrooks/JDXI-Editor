"""
Block Signals Context Manager
"""

from contextlib import contextmanager

from PySide6.QtWidgets import QWidget


@contextmanager
def blocked_signals(widget: QWidget):
    """Temporarily block Qt signals for a widget within the context."""
    if hasattr(widget, "blockSignals"):
        try:
            widget.blockSignals(True)
            yield
        finally:
            widget.blockSignals(False)
