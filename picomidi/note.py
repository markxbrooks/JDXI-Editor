"""
Backward compatibility shim for picomidi.note

This module is deprecated. Use picomidi.messages.note instead.
"""

import warnings

from picomidi.messages.note import MidiNote

warnings.warn(
    "picomidi.note is deprecated; use picomidi.messages.note instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["MidiNote"]
