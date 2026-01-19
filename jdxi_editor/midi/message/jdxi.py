"""
JD-Xi Model ID and Header List Constants
=======================================

This module contains constants for JD-Xi model IDs and header lists.

Constants Used:
    - ModelID: Model ID constants
    - RolandID: Roland ID constants

Usage Example:
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


class JDXiSysexHeader:
    """
    JD-Xi System Exclusive Message Header

    This class provides a structured way to work with JD-Xi SysEx headers,
    replacing the old JD_XI_HEADER_LIST constant.

    Usage:
        >>> header = JDXiSysexHeader.to_list()
        >>> header_bytes = JDXiSysexHeader.to_bytes()
        >>> header_len = len(JDXiSysexHeader.to_list())
    """

    ID = RolandID
    MODEL = ModelID

    @classmethod
    def to_list(cls) -> list[int]:
        """
        Convert the header to a list of integers.

        :return: list[int] Header bytes as a list [RolandID, DeviceID, ModelID1-4]
        """

        # Helper to safely convert enum to int
        def safe_int(val):
            if isinstance(val, int):
                return val
            if hasattr(val, "value"):  # Handle enums
                enum_val = val.value
                return int(enum_val) if not isinstance(enum_val, int) else enum_val
            try:
                return int(float(val))  # Handle floats and strings
            except (ValueError, TypeError):
                return 0

        return [
            safe_int(cls.ID.ROLAND_ID),
            safe_int(cls.ID.DEVICE_ID),
            safe_int(cls.MODEL.MODEL_ID_1),
            safe_int(cls.MODEL.MODEL_ID_2),
            safe_int(cls.MODEL.MODEL_ID_3),
            safe_int(cls.MODEL.MODEL_ID_4),
        ]

    @classmethod
    def to_bytes(cls) -> bytes:
        """
        Convert the header to bytes.

        :return: bytes Header bytes
        """
        return bytes(cls.to_list())

    @classmethod
    def length(cls) -> int:
        """
        Get the length of the header in bytes.

        :return: int Number of bytes in the header
        """
        return len(cls.to_list())


# Deprecated: Use JDXiSysexHeader.to_list() instead
JD_XI_HEADER_LIST = JDXiSysexHeader.to_list()
