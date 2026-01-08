"""
Backward compatibility shim for picomidi.pitch

This module is deprecated. Use picomidi.messages.pitch_bend instead.
"""

import warnings

from picomidi.messages.pitch_bend import PitchBend

warnings.warn(
    "picomidi.pitch.bend is deprecated; use picomidi.messages.pitch_bend instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["PitchBend"]
