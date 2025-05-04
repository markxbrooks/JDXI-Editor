"""
Module: parameter_handler

This module defines the `ParameterHandler` class, which manages MIDI parameter values
and emits signals when parameters are updated.

Classes:
    - ParameterHandler: Handles storing, updating, retrieving, and clearing MIDI parameters.

Signals:
    - parameters_updated: Emitted when parameter values change.

Methods:
    - update_parameter(address, value): Updates the value of a parameter at the given address.
    - get_parameter(address): Retrieves the value of a parameter at the given address.
    - clear_parameters(): Clears all stored parameters.

"""

from PySide6.QtCore import QObject, Signal
from typing import List


class ParameterHandler(QObject):
    parameters_updated = Signal(dict)  # Emits when parameters change

    def __init__(self):
        super().__init__()
        self._parameters = {}

    def update_parameter(self, address: List[int], value: int):
        """Update address parameter value
        :param address: List[int]
        :param value: int
        :return: None
        """
        addr_key = ".".join(str(x) for x in address)
        self._parameters[addr_key] = value
        self.parameters_updated.emit(self._parameters.copy())

    def get_parameter(self, address: List[int]) -> int:
        """Get address parameter value
        :param address: List[int]
        :return: int
        """
        addr_key = ".".join(str(x) for x in address)
        return self._parameters.get(addr_key, 0)

    def clear_parameters(self):
        """Clear all parameters
        :return: None
        """
        self._parameters.clear()
