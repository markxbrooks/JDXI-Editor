"""SysEx Byte"""
from enum import IntEnum
from typing import Type, Optional, T


class SysExByte(IntEnum):
    """Base class for SysEx message byte positions."""

    @classmethod
    def message_position(cls):
        """Return the fixed message position for command bytes."""
        raise NotImplementedError("To be subclassed")

    @classmethod
    def get_parameter_by_address(cls: Type[T], address: int) -> Optional[T]:
        """
        Get parameter by address

        :param address: int The address
        :return: Optional[T] The parameter
        """
        return next(
            (parameter for parameter in cls if parameter.value == address), None
        )
