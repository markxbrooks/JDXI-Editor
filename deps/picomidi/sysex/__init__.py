"""
Backward compatibility shim for picomidi.sysex

This module is deprecated. Use picomidi.messages.sysex instead.
"""

import warnings

from picomidi.messages.sysex import SysExByte

warnings.warn(
    "picomidi.sysex.byte is deprecated; use picomidi.messages.sysex instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["SysExByte"]
