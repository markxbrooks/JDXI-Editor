"""
Backward compatibility shim for picomidi.aftertouch

This module is deprecated. Use picomidi.messages.aftertouch instead.
"""

import warnings

from picomidi.messages.aftertouch import Aftertouch

warnings.warn(
    "picomidi.aftertouch is deprecated; use picomidi.messages.aftertouch instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["Aftertouch"]
