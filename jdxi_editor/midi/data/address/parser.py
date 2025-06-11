"""
Parser
Example Usage

class ProgramAddress(Address):
    COMMON = 0x18
    DIGITAL_1 = 0x19

sysex_addr = b'\x18\x00\x20\x00'
parsed = parse_sysex_address(sysex_addr, ProgramAddress)

if parsed:
    base, offset = parsed
    print(f"Base: {base}, Offset: {offset}")
else:
    print("Unknown base address")


Output:

from
Base: <ProgramAddress.COMMON: 0x18>, Offset: (0, 32, 0)

"""

from typing import Tuple, Optional, Type, TypeVar

T = TypeVar("T")


def parse_sysex_address(
    address_bytes: bytes, enum_cls: Type[T]
) -> Optional[Tuple[T, Tuple[int, int, int]]]:
    """
    Parse a 4-byte SysEx address into a (base, offset) tuple.

    :param address_bytes: bytes The 4-byte SysEx address
    :param enum_cls: Type[T] The enum class
    :return: Optional[Tuple[T, Tuple[int, int, int]]] The (base, offset) tuple
    """
    if not isinstance(address_bytes, (bytes, bytearray)) or len(address_bytes) != 4:
        raise ValueError("Address must be a 4-byte bytes or bytearray")

    base = address_bytes[0]
    offset = (address_bytes[1], address_bytes[2], address_bytes[3])

    try:
        base_enum = enum_cls(base)
        return base_enum, offset
    except ValueError:
        # Not found in the given enum
        return None
