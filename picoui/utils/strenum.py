from enum import Enum


class StrEnum(str, Enum):
    """
    Python 3.10 compatible StrEnum.

    Behaves like Python 3.11 enum.StrEnum.
    """

    def __str__(self) -> str:
        return str(self.value)
