"""
Parameter Map for RPN/NRPN

Provides a generic mapping utility for RPN/NRPN parameters.
"""

from typing import Any, Dict, ItemsView, Optional, Tuple


class ParameterMap:
    """
    Generic parameter map for storing MSB/LSB pairs.

    Used for mapping parameter numbers to their MSB/LSB controller values.
    """

    def __init__(self, mapping: Optional[Dict[int, Tuple[int, int]]] = None) -> None:
        """
        Initialize the parameter map.

        :param mapping: Optional dictionary mapping parameter numbers to (MSB, LSB) tuples
        """
        self._map: Dict[int, Tuple[int, int]] = mapping or {}

    def add_mapping(self, key: int, msb_lsb_pair: Tuple[int, int]) -> None:
        """
        Add a mapping from parameter number to MSB/LSB pair.

        :param key: Parameter number
        :param msb_lsb_pair: Tuple of (MSB, LSB) values
        """
        self._map[key] = msb_lsb_pair

    def get(self, key: int, default: Any = None) -> Any:
        """
        Get the LSB value for a parameter (for backward compatibility).

        :param key: Parameter number
        :param default: Default value if not found
        :return: LSB value or default
        """
        result = self._map.get(key, default)
        if isinstance(result, tuple):
            return result[1]  # return LSB
        return result

    def get_lsb(self, key: int) -> Optional[int]:
        """
        Get the LSB value for a parameter.

        :param key: Parameter number
        :return: LSB value or None
        """
        return self._map.get(key, (None, None))[1]

    def get_msb(self, key: int) -> Optional[int]:
        """
        Get the MSB value for a parameter.

        :param key: Parameter number
        :return: MSB value or None
        """
        return self._map.get(key, (None, None))[0]

    def get_msb_lsb(self, key: int) -> Optional[Tuple[int, int]]:
        """
        Get both MSB and LSB values for a parameter.

        :param key: Parameter number
        :return: Tuple of (MSB, LSB) or None
        """
        return self._map.get(key)

    def __getitem__(self, key: int) -> Tuple[int, int]:
        """Get MSB/LSB pair for a parameter."""
        return self._map[key]

    def __setitem__(self, key: int, value: Tuple[int, int]) -> None:
        """Set MSB/LSB pair for a parameter."""
        self.add_mapping(key, value)

    def __contains__(self, key: int) -> bool:
        """Check if parameter exists in map."""
        return key in self._map

    def items(self) -> ItemsView[int, Tuple[int, int]]:
        """Get all parameter mappings."""
        return self._map.items()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._map})"


class RPNMap(ParameterMap):
    """
    Map for Registered Parameter Numbers (RPN).

    Maps RPN parameter numbers to their MSB/LSB controller values.
    """

    pass


class NRPNMap(ParameterMap):
    """
    Map for Non-Registered Parameter Numbers (NRPN).

    Maps NRPN parameter numbers to their MSB/LSB controller values.
    """

    pass
