"""
Parameter Map
"""

from typing import Any, Dict, Tuple, Optional, ItemsView


class ParameterMap:
    def __init__(self, mapping: Optional[Dict[int, Tuple[int, int]]] = None) -> None:
        self._map: Dict[int, Tuple[int, int]] = mapping or {}

    def add_mapping(self, key: int, msb_lsb_pair: Tuple[int, int]) -> None:
        self._map[key] = msb_lsb_pair

    def get(self, key: int, default: Any = None) -> Any:
        result = self._map.get(key, default)
        if isinstance(result, tuple):
            return result[1]  # return LSB
        return result

    def get_lsb(self, key: int) -> Optional[int]:
        return self._map.get(key, (None, None))[1]

    def get_msb(self, key: int) -> Optional[int]:
        return self._map.get(key, (None, None))[0]

    def __getitem__(self, key: int) -> Tuple[int, int]:
        return self._map[key]

    def __setitem__(self, key: int, value: Tuple[int, int]) -> None:
        self.add_mapping(key, value)

    def __contains__(self, key: int) -> bool:
        return key in self._map

    def items(self) -> ItemsView[int, Tuple[int, int]]:
        return self._map.items()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._map})"


class NRPNMap(ParameterMap):
    pass


class RPNMap(ParameterMap):
    pass
