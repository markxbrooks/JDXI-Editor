"""
Backward compatibility shim for picomidi.pc

This module is deprecated. Use picomidi.messages.program_change instead.
"""

import warnings

from picomidi.messages.program_change import ProgramChange

warnings.warn(
    "picomidi.pc.program_change is deprecated; "
    "use picomidi.messages.program_change instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["ProgramChange"]
