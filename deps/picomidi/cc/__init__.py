"""
Backward compatibility shim for picomidi.cc

This module is deprecated. Use picomidi.messages.control_change instead.
"""

import warnings


# Lazy import to avoid circular dependency
def __getattr__(name):
    if name == "ControlChange":
        warnings.warn(
            "picomidi.cc.control_change is deprecated; "
            "use picomidi.messages.control_change instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        from picomidi.messages.control_change import ControlChange

        return ControlChange
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# ControlChange is available via __getattr__, but pylint needs this for __all__
# pylint: disable=undefined-all-variable
__all__ = ["ControlChange"]
