"""
Backward compatibility shim for picomidi.note

This module is deprecated. Use picomidi.messages.note instead.
"""

import warnings

warnings.warn(
    "picomidi.note is deprecated; use picomidi.messages.note instead.",
    DeprecationWarning,
    stacklevel=2,
)

from picomidi.messages.note import MidiNote

__all__ = ["MidiNote"]

