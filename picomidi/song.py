"""
Backward compatibility shim for picomidi.song

This module is deprecated. Use picomidi.messages.song instead.
"""

import warnings

warnings.warn(
    "picomidi.song is deprecated; use picomidi.messages.song instead.",
    DeprecationWarning,
    stacklevel=2,
)

from picomidi.messages.song import Song

__all__ = ["Song"]
