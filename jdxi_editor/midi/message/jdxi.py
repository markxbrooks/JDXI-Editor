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
    [<ModelID.MODEL_ID_1: 0x00>, <ModelID.MODEL_ID_1: 0x00>, <ModelID.MODEL_ID_1: 0x00>, <ModelID.MODEL_ID_4: 0x0E>]
    >>> JDXiSysexHeader.to_list()
        [<RolandID.ROLAND_ID: 65>, <RolandID.DEVICE_ID: 16>, <ModelID.MODEL_ID_1: 0x00>, <ModelID.MODEL_ID_1: 0x00>, <ModelID.MODEL_ID_1: 0x00>, <ModelID.MODEL_ID_4: 0x0E>]


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


class JDXiSysexHeader:
    """
    JD-Xi System Exclusive Message Header
    """
    ID = RolandID
    MODEL = ModelID

    @classmethod
    def to_list(cls) -> list[int]:
        """
        Convert the header to a list of integers
        """
        return [cls.ID.ROLAND_ID, cls.ID.DEVICE_ID, cls.MODEL.MODEL_ID_1, cls.MODEL.MODEL_ID_2, cls.MODEL.MODEL_ID_3, cls.MODEL.MODEL_ID_4]
