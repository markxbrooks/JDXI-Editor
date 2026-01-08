"""
JD-Xi Model ID and Header List Constants
=======================================

This module contains constants for JD-Xi model IDs and header lists.

Constants Used:
    - ModelID: Model ID constants
    - RolandID: Roland ID constants

Usage Example:
    >>> from jdxi_editor.midi_state.data.address.address import ModelID
    >>> from jdxi_editor.midi_state.data.address.SYSEX import RolandID
    >>> JD_XI_MODEL_ID
    [ModelID.MODEL_ID_1, ModelID.MODEL_ID_2, ModelID.MODEL_ID_3, ModelID.MODEL_ID_4]
    >>> JD_XI_HEADER_LIST
    [RolandID.ROLAND_ID, RolandID.DEVICE_ID, *JD_XI_MODEL_ID]

"""

from jdxi_editor.midi.data.address.address import ModelID
from jdxi_editor.midi.data.address.sysex import RolandID

JD_XI_MODEL_ID = [
    ModelID.MODEL_ID_1,
    ModelID.MODEL_ID_2,
    ModelID.MODEL_ID_3,
    ModelID.MODEL_ID_4,
]
JD_XI_HEADER_LIST = [RolandID.ROLAND_ID, RolandID.DEVICE_ID, *JD_XI_MODEL_ID]
