from PySide6.QtCore import QObject, Signal
from typing import Dict, List


class ParameterHandler(QObject):
    parameters_updated = Signal(dict)  # Emits when parameters change

    def __init__(self):
        super().__init__()
        self._parameters = {}

    def update_parameter(self, address: List[int], value: int):
        """Update address parameter value"""
        addr_key = ".".join(str(x) for x in address)
        self._parameters[addr_key] = value
        self.parameters_updated.emit(self._parameters.copy())

    def get_parameter(self, address: List[int]) -> int:
        """Get address parameter value"""
        addr_key = ".".join(str(x) for x in address)
        return self._parameters.get(addr_key, 0)

    def clear_parameters(self):
        """Clear all parameters"""
        self._parameters.clear()
