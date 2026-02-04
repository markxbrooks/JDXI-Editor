from typing import runtime_checkable, Protocol


@runtime_checkable
class LFOBehavior(Protocol):
    def build_widgets(self) -> None: ...
    def setup_ui(self) -> None: ...
