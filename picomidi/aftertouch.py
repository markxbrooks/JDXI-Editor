"""
Backward compatibility shim for picomidi.aftertouch

This module is deprecated. Use picomidi.messages.aftertouch instead.
"""

import warnings

warnings.warn(
    "picomidi.aftertouch is deprecated; use picomidi.messages.aftertouch instead.",
    DeprecationWarning,
    stacklevel=2,
)

from picomidi.messages.aftertouch import Aftertouch

__all__ = ["Aftertouch"]
