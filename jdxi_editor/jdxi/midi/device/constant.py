"""
Device information
"""


class JDXiSysExIdentity:
    """Roland JDXiDevice SysEx Info"""

    ROLAND = [
        0x41,
        0x10,
        0x00,
    ]  # Manufacturer ID, Device ID, Model ID (JD-Xi = 0x0E)
    JD_XI = 0x0E

    # SysEx Identity Request/Reply
    NUMBER = 0x7E  # Non-realtime ID (0x7E) or realtime (0x7F), depending on context
    DEVICE = 0x7F  # 'All Call' for all devices
    SUB1_GENERAL_INFORMATION = 0x06
    SUB2_IDENTITY_REQUEST = 0x01
    SUB2_IDENTITY_REPLY = 0x02
    
    """
    JD_XI_MODEL_ID = [
        ModelID.MODEL_ID_1,
        ModelID.MODEL_ID_2,
        ModelID.MODEL_ID_3,
        ModelID.MODEL_ID_4,
    ]
    JD_XI_HEADER_LIST = [RolandID.ROLAND_ID, RolandID.DEVICE_ID, *JD_XI_MODEL_ID]
    """
