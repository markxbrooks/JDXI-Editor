from enum import Enum


class BaseParameter(Enum):
    """Base class for synth parameters with area, address, and value range."""

    def __new__(cls, address: int, min_val: int, max_val: int):
        obj = object.__new__(cls)
        obj._value_ = address
        obj.address = address
        obj.min_val = min_val
        obj.max_val = max_val
        return obj

    def validate_value(self, value: int) -> int:
        """Validate and convert parameter value to MIDI range (0-127)"""
        if not isinstance(value, int):
            raise ValueError(f"Value must be integer, got {type(value)}")
        if not self.min_val <= value <= self.max_val:
            raise ValueError(
                f"Value {value} out of range for {self.name} "
                f"(valid range: {self.min_val}-{self.max_val})"
            )
        return value

    @staticmethod
    def get_by_name(param_name):
        """Get the parameter by name."""
        return BaseParameter.__members__.get(param_name, None)

    @staticmethod
    def get_name_by_address(address: int):
        """Return the parameter name for address given address."""
        for param in BaseParameter:
            if param.address == address:
                return param.name
        return None

    @property
    def display_name(self) -> str:
        """Get display name for the parameter"""
        return self.name.replace("_", " ").title()
