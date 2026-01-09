class JDXiDevice:
    """Roland SysEx Header"""

    ROLAND_ID = [
        0x41,
        0x10,
        0x00,
    ]  # Manufacturer ID, Device ID, Model ID (JD-Xi = 0x0E)
    JD_XI_MODEL_ID = 0x0E

    # SysEx Identity Request/Reply
    ID_NUMBER = 0x7E  # Non-realtime ID (0x7E) or realtime (0x7F), depending on context
    DEVICE_ID = 0x7F  # 'All Call' for all devices
    SUB_ID_1_GENERAL_INFORMATION = 0x06
    SUB_ID_2_IDENTITY_REQUEST = 0x01
    SUB_ID_2_IDENTITY_REPLY = 0x02
