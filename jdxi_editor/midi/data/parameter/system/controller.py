"""
System Controller Parameters
===========================

Defines SystemControllerParam for System Controller block (0x02 00 03 00).
Per Roland Parameter Address Map (midi_parameters.txt).
Total size 0x11 bytes.
"""

from typing import Optional, Tuple

from picomidi.sysex.parameter.address import AddressParameter

from jdxi_editor.midi.parameter.spec import ParameterSpec


class SystemControllerParam(AddressParameter):
    """System Controller parameters (transmit, keyboard velocity)"""

    def __init__(
        self,
        address: int,
        min_val: Optional[int] = None,
        max_val: Optional[int] = None,
        display_min: Optional[int] = None,
        display_max: Optional[int] = None,
        tooltip: Optional[str] = None,
        display_name: Optional[str] = None,
    ):
        super().__init__(address, min_val, max_val)
        self.display_min = display_min if display_min is not None else min_val
        self.display_max = display_max if display_max is not None else max_val
        self.tooltip = tooltip if tooltip is not None else ""
        self._display_name = display_name

    TRANSMIT_PROGRAM_CHANGE = ParameterSpec(0x00, 0, 1)  # OFF, ON
    TRANSMIT_BANK_SELECT = ParameterSpec(0x01, 0, 1)  # OFF, ON
    KEYBOARD_VELOCITY = ParameterSpec(0x02, 0, 127)  # REAL, 1-127
    KEYBOARD_VELOCITY_CURVE = ParameterSpec(0x03, 1, 3)  # LIGHT, MEDIUM, HEAVY
    KEYBOARD_VELOCITY_CURVE_OFFSET = ParameterSpec(0x04, 54, 73, -10, 9)

    @classmethod
    def __iter__(cls):
        for name in (
            "TRANSMIT_PROGRAM_CHANGE",
            "TRANSMIT_BANK_SELECT",
            "KEYBOARD_VELOCITY",
            "KEYBOARD_VELOCITY_CURVE",
            "KEYBOARD_VELOCITY_CURVE_OFFSET",
        ):
            p = getattr(cls, name)
            p.name = name
            yield p

    def get_display_value(self) -> Tuple[int, int]:
        """Get the digital value range (min, max) for the parameter"""
        if hasattr(self, "display_min") and hasattr(self, "display_max"):
            return self.display_min, self.display_max
        return self.min_val, self.max_val

    @property
    def display_name(self) -> str:
        """Get display name for the parameter."""
        if getattr(self, "_display_name", None) is not None:
            return self._display_name
        return self.name.replace("_", " ").title()

    @staticmethod
    def get_by_name(param_name: str) -> Optional["SystemControllerParam"]:
        """Get the Parameter by name."""
        members = getattr(SystemControllerParam, "__members__", None)
        if members is not None:
            return members.get(param_name, None)
        return getattr(SystemControllerParam, param_name, None)
