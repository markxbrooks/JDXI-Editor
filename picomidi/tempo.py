"""
Backward compatibility shim for picomidi.tempo

This module is deprecated. Use picomidi.core.tempo instead.
"""

import warnings

from picomidi.core.tempo import MidiTempo

warnings.warn(
    "picomidi.tempo is deprecated; use picomidi.core.tempo instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["MidiTempo"]
