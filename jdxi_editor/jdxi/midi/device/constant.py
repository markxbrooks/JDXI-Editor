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
