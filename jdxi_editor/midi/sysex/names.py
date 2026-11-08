"""
Names of SysEx bytes from the JD-Xi address and parameter enums.

Example:
    >>> from jdxi_editor.midi.data.address.address import CommandID
    >>> parse_sysex_byte(0x12, CommandID)
    'DT1'
"""

from typing import Optional, Protocol, Type, TypeVar, runtime_checkable

T = TypeVar("T", bound="EnumWithAddress")


@runtime_checkable
class SysExEnumProtocol(Protocol):
    @classmethod
    def message_position(cls) -> int: ...

    def __call__(self, value: int): ...


class EnumWithAddress(Protocol):
    @classmethod
    def message_position(cls) -> int:
        """Get the position of the message in the SysEx message.
        :return: int - the position of the message
        """
        ...

    @classmethod
    def get_parameter_by_address(cls, address: int) -> Optional[T]:
        """Get the enum member by address.
        :param address: int
        :return: Optional[T] - the enum member or None if not found
        """
        ...


def parse_sysex_byte(byte_value: int, enum_cls: Type[SysExEnumProtocol]) -> str:
    """
    Get the name of a SysEx byte value using a given enum class.

    Supports both:
    - address-aware enums (get_parameter_by_address)
    - value-based enums (IntEnum / Enum)

    :param byte_value: SysEx byte value
    :param enum_cls: Enum class
    :return: name or "COMMON (0x??)" if not found
    """
    enum_member = None

    if hasattr(enum_cls, "get_parameter_by_address"):
        enum_member = enum_cls.get_parameter_by_address(byte_value)
    else:
        try:
            enum_member = enum_cls(byte_value)
        except (ValueError, TypeError):
            enum_member = None

    return enum_member.name if enum_member else f"COMMON (0x{byte_value:02X})"
