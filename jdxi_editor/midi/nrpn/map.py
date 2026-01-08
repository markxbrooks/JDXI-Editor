"""
Parameter Map

This module re-exports ParameterMap classes from PicMidi for backward compatibility.
New code should import directly from picomidi.rpn.
"""

# Import from PicMidi
from picomidi.rpn import NRPNMap, ParameterMap, RPNMap

# Re-export for backward compatibility
__all__ = ["ParameterMap", "NRPNMap", "RPNMap"]
