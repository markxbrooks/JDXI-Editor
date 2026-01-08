"""
Backward compatibility shim for picomidi.tempo

This module is deprecated. Use picomidi.core.tempo instead.
"""

import warnings

warnings.warn(
    "picomidi.tempo is deprecated; use picomidi.core.tempo instead.",
    DeprecationWarning,
    stacklevel=2,
)

from picomidi.core.tempo import MidiTempo

__all__ = ["MidiTempo"]
