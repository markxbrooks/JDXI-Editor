"""from typing import Protocol


class AmpAPI(Protocol):
    def set_level(self, value: int) -> None: ...
    def set_pan(self, value: int) -> None: ...
    def set_velocity_sensitivity(self, value: int) -> None: ...

    def set_adsr(self,
                 attack: int | None = None,
                 decay: int | None = None,
                 sustain: int | None = None,
                 release: int | None = None) -> None

    def get_state(self) -> dict: ..."""
