from enum import Enum


class AddressParameterSetup(Enum):
    """Setup parameters"""

    # Reserved space (0x00-0x03)
    RESERVED_1 = 0x00  # Reserved
    RESERVED_2 = 0x01  # Reserved
    RESERVED_3 = 0x02  # Reserved
    RESERVED_4 = 0x03  # Reserved

    # Program selection (0x04-0x06)
    BANK_MSB = 0x04  # Program Bank Select MSB (CC#0) (0-127)
    BANK_LSB = 0x05  # Program Bank Select LSB (CC#32) (0-127)
    PROGRAM = 0x06  # Program Change Number (0-127)

    # More reserved space (0x07-0x3A)
    # Total size: 0x3B bytes
