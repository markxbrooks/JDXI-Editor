"""
Backward compatibility shim for picomidi.channel

This module is deprecated. Use picomidi.core.channel_legacy instead.
"""

import warnings

warnings.warn(
    "picomidi.channel is deprecated; use picomidi.core.channel_legacy instead.",
    DeprecationWarning,
    stacklevel=2,
)

from picomidi.core.channel_legacy import MidiChannel

__all__ = ["MidiChannel"]
