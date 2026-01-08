"""
Backward compatibility shim for picomidi.pc

This module is deprecated. Use picomidi.messages.program_change instead.
"""

import warnings

warnings.warn(
    "picomidi.pc.program_change is deprecated; use picomidi.messages.program_change instead.",
    DeprecationWarning,
    stacklevel=2,
)

from picomidi.messages.program_change import ProgramChange

__all__ = ["ProgramChange"]

