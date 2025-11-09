"""
Drum parameter module for JD-Xi editor.

This module exports drum parameter classes for common and partial parameters.
"""

from jdxi_editor.midi.data.parameter.drum.common import AddressParameterDrumCommon
from jdxi_editor.midi.data.parameter.drum.partial import AddressParameterDrumPartial

__all__ = [
    "AddressParameterDrumCommon",
    "AddressParameterDrumPartial",
]
