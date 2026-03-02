from typing import Optional

from picomidi.sysex.parameter.address import AddressParameter

from jdxi_editor.midi.parameter.spec import ParameterSpec


class SystemCommonParam(AddressParameter):
    """System Common parameters (address 02 00 00 xx)"""

    def __init__(
        self,
        address: int,
        min_val: int,
        max_val: int,
        display_min: Optional[int] = None,
        display_max: Optional[int] = None,
        description: Optional[str] = None,
        display_name: Optional[str] = None,
        options: Optional[list] = None,
        values: Optional[list] = None,
    ):
        super().__init__(address, min_val, max_val)
        self._display_name = display_name

    # Raw (min_val, max_val) per Roland spec; display range in min_display, max_display
    MASTER_TUNE = ParameterSpec(
        0x00, 24, 2024, -100, 100, "Master Tune"
    )  # 24-2024 -> -100..+100 cents
    MASTER_KEY_SHIFT = ParameterSpec(
        0x04, 40, 88, -24, 24, "Master Key Shift"
    )  # 40-88 -> -24..+24 semitones
    MASTER_LEVEL = ParameterSpec(0x05, 0, 127, description="Master Level")
    PROGRAM_CTRL_CH = ParameterSpec(0x11, 0, 16, description="Program Control Channel")
    RX_PROGRAM_CHANGE = ParameterSpec(0x29, 0, 1, description="Receive Program Change")
    RX_BANK_SELECT = ParameterSpec(0x2A, 0, 1, description="Receive Bank Select")

    @classmethod
    def __iter__(cls):
        for name in (
            "MASTER_TUNE",
            "MASTER_KEY_SHIFT",
            "MASTER_LEVEL",
            "PROGRAM_CTRL_CH",
            "RX_PROGRAM_CHANGE",
            "RX_BANK_SELECT",
        ):
            p = getattr(cls, name)
            p.name = name
            yield p

    def get_display_value(self) -> tuple:
        """Return (min_display, max_display) for slider/UI range."""
        val = getattr(self, "value", self)
        return (getattr(val, "min_display", getattr(self, "min_val", 0)), getattr(val, "max_display", getattr(self, "max_val", 127)))

    @staticmethod
    def format_value_for_display(param, value: int) -> str:
        """Convert raw value to display string for tooltips/logging."""
        if param == SystemCommonParam.MASTER_TUNE:  # Master Tune
            cents = (value - 1024) / 10  # Convert 24-2024 to -100.0/+100.0
            return f"{cents:+.1f} cents"
        elif param == SystemCommonParam.MASTER_KEY_SHIFT:  # Master Key Shift
            semitones = value - 64  # Convert 40-88 to -24/+24
            return f"{semitones:+d} st"
        elif param == SystemCommonParam.PROGRAM_CTRL_CH:  # Program Control Channel
            return "OFF" if value == 0 else str(value)
        elif param in (
            SystemCommonParam.RX_PROGRAM_CHANGE,
            SystemCommonParam.RX_BANK_SELECT,
        ):  # Switches
            return "ON" if value else "OFF"
        return str(value)

    @staticmethod
    def get_by_name(param_name: str) -> Optional["SystemCommonParam"]:
        """Get the Parameter by name."""
        name_to_param = {
            "MASTER_TUNE": SystemCommonParam.MASTER_TUNE,
            "MASTER_KEY_SHIFT": SystemCommonParam.MASTER_KEY_SHIFT,
            "MASTER_LEVEL": SystemCommonParam.MASTER_LEVEL,
            "PROGRAM_CTRL_CH": SystemCommonParam.PROGRAM_CTRL_CH,
            "RX_PROGRAM_CHANGE": SystemCommonParam.RX_PROGRAM_CHANGE,
            "RX_BANK_SELECT": SystemCommonParam.RX_BANK_SELECT,
        }
        return name_to_param.get(param_name)

    def get_nibbled_byte_size(self) -> int:
        """Get the nibbled byte size of the parameter"""
        if self.max_value - self.min_value <= 255:
            return 1
        else:
            return 4  # I don't know of any 2 byte parameters


# Attach conversion helpers after class is defined (avoids Enum __init__ issues)
SystemCommonParam.MASTER_TUNE.convert_to_midi = lambda v: max(24, min(2024, 1024 + int(v * 10)))
SystemCommonParam.MASTER_TUNE.convert_from_midi = lambda v: (v - 1024) / 10
SystemCommonParam.MASTER_TUNE.get_nibbled_size = lambda: 4
SystemCommonParam.MASTER_KEY_SHIFT.convert_to_midi = lambda v: max(40, min(88, 64 + int(v)))
SystemCommonParam.MASTER_KEY_SHIFT.convert_from_midi = lambda v: v - 64
