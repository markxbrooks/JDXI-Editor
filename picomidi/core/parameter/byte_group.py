from abc import abstractmethod, ABC
from dataclasses import dataclass


@dataclass(frozen=True)
class ByteGroup(ABC):
    name: str = None

    @abstractmethod
    def length(self):
        raise NotImplementedError("To be implemented by subclass")

    @abstractmethod
    def bytes_string(self):
        raise NotImplementedError("To be implemented by subclass")

    @property
    @abstractmethod
    def bytes(self) -> tuple[int, ...]:
        ...

    def __repr__(self):
        return f"{self.__class__.__name__}(address='{self.bytes_string()}')"

    def __post_init__(self):
        if self.length not in [3, 4]:
            raise ValueError("ByteGroup length must be 3 or 4.")
