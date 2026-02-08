from __future__ import annotations

from typing import Iterable, Dict, Any


class EffectParamRegistry:
    """Precomputed O(1) lookup from param_name -> enum value"""

    def __init__(self, param_types: Iterable[type]):
        self.map: Dict[str, Any] = {}
        for cls in param_types:
            members = getattr(cls, "__members__", None)
            if not members:
                continue
            for p in cls:
                self.map[p.name] = p

    def resolve(self, name: str):
        return self.map.get(name)
