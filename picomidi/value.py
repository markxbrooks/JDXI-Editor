"""
Backward compatibility shim for picomidi.value

This module is deprecated. Use picomidi.core.value instead.
"""

import warnings

warnings.warn(
    "picomidi.value is deprecated; use picomidi.core.value instead.",
    DeprecationWarning,
    stacklevel=2,
)

from picomidi.core.value import MidiValue

__all__ = ["MidiValue"]
