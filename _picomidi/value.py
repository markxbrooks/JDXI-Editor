"""
Backward compatibility shim for picomidi.value

This module is deprecated. Use picomidi.core.value instead.
"""

import warnings

from picomidi.core.value import MidiValue

warnings.warn(
    "picomidi.value is deprecated; use picomidi.core.value instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["MidiValue"]
