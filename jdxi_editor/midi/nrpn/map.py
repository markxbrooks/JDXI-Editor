"""
NRPN Map class
"""


class ParameterMap:
    def __init__(self, mapping: dict = None):
        self._map = mapping or {}

    def add_mapping(self, key: int, msb_lsb_pair: tuple):
        self._map[key] = msb_lsb_pair

    def get(self, key: int, default: Any = None):
        result = self._map.get(key, default)
        if isinstance(result, tuple):
            return result[1]  # return LSB
        return result

    def get_lsb(self, key: int):
        return self._map.get(key, (None, None))[1]

    def get_msb(self, key: int):
        return self._map.get(key, (None, None))[0]

    def __getitem__(self, key: int):
        return self._map[key]

    def __setitem__(self, key: int, value: tuple):
        self.add_mapping(key, value)

    def __contains__(self, key: int):
        return key in self._map

    def items(self):
        return self._map.items()

    def __repr__(self):
        return f"{self.__class__.__name__}({self._map})"


class NRPNMap(ParameterMap):
    pass


class RPNMap(ParameterMap):
    pass
