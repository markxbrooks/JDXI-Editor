from typing import Protocol, runtime_checkable


@runtime_checkable
class LFOBehavior(Protocol):
    def build_widgets(self) -> None: ...
    def setup_ui(self) -> None: ...
