"""
Backward compatibility shim for picomidi.sysex

This module is deprecated. Use picomidi.messages.sysex instead.
"""

import warnings

warnings.warn(
    "picomidi.sysex.byte is deprecated; use picomidi.messages.sysex instead.",
    DeprecationWarning,
    stacklevel=2,
)

from picomidi.messages.sysex import SysExByte

__all__ = ["SysExByte"]

