"""
Control Registry

Dict-like registry of parameter -> widget, owned by SynthBase (or one per partial).
Supports get(param) with optional name fallback so param identity matches across
partials. Use register(param, widget) or registry[param] = widget; lookup via
registry.get(param) or registry[param].
"""

from typing import Any, Iterator, Protocol, runtime_checkable

from PySide6.QtWidgets import QWidget


@runtime_checkable
class ControlResolver(Protocol):
    def get(self, param, default: QWidget | None = None) -> QWidget | None: ...


class ControlRegistry:
    """Registry of parameter -> control widget. Dict-like; use per partial (Analog, Digital1, Digital2, Drums)."""

    def __init__(self) -> None:
        self._controls: dict[Any, QWidget] = {}

    def register(self, param: Any, widget: QWidget) -> None:
        self._controls[param] = widget

    def get(self, param: Any, default: QWidget | None = None) -> QWidget | None:
        if param in self._controls:
            return self._controls[param]
        name = getattr(param, "name", None)
        if name:
            for k, w in self._controls.items():
                if getattr(k, "name", None) == name:
                    return w
        return default

    def __setitem__(self, param: Any, widget: QWidget) -> None:
        self.register(param, widget)

    def __getitem__(self, param: Any) -> QWidget:
        w = self.get(param)
        if w is None:
            raise KeyError(param)
        return w

    def __contains__(self, param: Any) -> bool:
        if param in self._controls:
            return True
        name = getattr(param, "name", None)
        if name:
            for k in self._controls:
                if getattr(k, "name", None) == name:
                    return True
        return False

    def __len__(self) -> int:
        return len(self._controls)

    def __iter__(self) -> Iterator[Any]:
        return iter(self._controls)

    def items(self) -> Iterator[tuple[Any, QWidget]]:
        return iter(self._controls.items())

    def keys(self) -> Iterator[Any]:
        return iter(self._controls.keys())

    def values(self) -> Iterator[QWidget]:
        return iter(self._controls.values())

    def pop(self, param: Any, default: QWidget | None = None) -> QWidget | None:
        return self._controls.pop(param, default)

    def update(self, other: Any = (), /, **kwargs: Any) -> None:
        """Update registry from another mapping (e.g. dict or ControlRegistry) or iterable of (param, widget)."""
        if hasattr(other, "items"):
            for k, v in other.items():
                self._controls[k] = v
        else:
            for k, v in other:
                self._controls[k] = v
        for k, v in kwargs.items():
            self._controls[k] = v
