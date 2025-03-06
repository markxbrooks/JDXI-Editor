from typing import Tuple, Optional

from jdxi_manager.data.parameter.synth import SynthParameter

"""
For Reference:

+------------------------------------------------------------------------------+
| Offset      |                                                                |
| Address     | Description                                                    |
|-------------+----------------------------------------------------------------|
| 00 00 | 0aaa aaaa | Program Name 1 (32 - 127)                                |
| 32 - 127 [ASCII]                                                             |
| 00 01 | 0aaa aaaa | Program Name 2 (32 - 127)                                |
| 32 - 127 [ASCII]  |                                                          |
| 00 02 | 0aaa aaaa | Program Name 3 (32 - 127) |                              |
|  32 - 127 [ASCII] |                                                          |
| 00 04 | 0aaa aaaa | Program Name 4 (32 - 127) |                              |
| 32 - 127 [ASCII]  |                                                          |
| 00 06 | 0aaa aaaa | Program Name 5 (32 - 127) |                              |
| 32 - 127 [ASCII]  |                                                          |
| 00 08 | 0aaa aaaa | Program Name 6 (32 - 127) |                              |
| 32 - 127 [ASCII]  |                                                          |
| 00 0A | 0aaa aaaa | Program Name 7 (32 - 127) |                              |
| 32 - 127 [ASCII]  |                                                          |
| 00 0C | 0aaa aaaa | Program Name 8 (32 - 127) |                              |
| 32 - 127 [ASCII]  |                                                          |
| 00 0E | 0aaa aaaa | Program Name 9 (32 - 127) |                              |
| 32 - 127 [ASCII]  |                                                          |
| 00 10 | 0aaa aaaa | Program Name 10 (32 - 127)                               |
| 32 - 127 [ASCII]  |                                                          |
| 00 12 | 0aaa aaaa | Program Name 11 (32 - 127)                               |
| 32 - 127 [ASCII]  |                                                          |
| 00 14 | 0aaa aaaa | Program Name 12 (32 - 127)                               |
| 32 - 127 [ASCII]  |                                                          |
|-------------+-----------+----------------------------------------------------|
| 00 16 | 0000 aaaa | Program Level (0 - 127) |                                |
|# 00 17 | 0000 aaaa |                                                         |
| 0000 bbbb |                                                                  |
| 0000 cccc |                                                                  |
| 0000 dddd | Program Tempo (500 - 30000) |                                    |
| 5.00 - 300.00 |                                                              |
| 00 1B | 0000 000a | (reserve) <*> |                                          |
|-------------+-----------+----------------------------------------------------|
| 00 1C | 0aaa aaaa | Vocal Effect (0 - 2)                                     |
| OFF, VOCODER, AUTO-PITCH |                                                   |
|-------------+-----------+----------------------------------------------------|
| 00 1D | 0000 aaaa | Vocal Effect Part (0 - 1) |                              |
| 1 - 2 |                                                                      |
|-------------+-----------+----------------------------------------------------|
| 00 1E | 0000 000a | Auto Note Switch (0 - 1) |                               |
| OFF, ON |                                                                    |
|-------------+----------------------------------------------------------------|
| 00 00 00 1F | Total Size |                                                   |
+------------------------------------------------------------------------------+
"""


class ProgramCommonParameter(SynthParameter):
    """Program Common parameters"""

    def __init__(self, address: int, min_val: Optional[int] = None, max_val: Optional[int] = None,
                 display_min: Optional[int] = None, display_max: Optional[int] = None):
        super().__init__(address, min_val, max_val)
        self.display_min = display_min if display_min is not None else min_val
        self.display_max = display_max if display_max is not None else max_val

    NAME_1 = 0x00      # Character 1 of name (ASCII)
    NAME_2 = 0x01      # Character 2 of name
    NAME_3 = 0x02      # Character 3 of name
    NAME_4 = 0x03      # Character 4 of name
    NAME_5 = 0x04      # Character 5 of name
    NAME_6 = 0x05      # Character 6 of name
    NAME_7 = 0x06      # Character 7 of name
    NAME_8 = 0x07      # Character 8 of name
    NAME_9 = 0x08      # Character 9 of name
    NAME_10 = 0x09     # Character 10 of name
    NAME_11 = 0x0A     # Character 11 of name
    NAME_12 = 0x0B     # Character 12 of name

    PROGRAM_LEVEL = (0x10, 0, 127, 0, 127)  # Program Level (0-127)
    PROGRAM_TEMPO = (0x11, 500, 30000, 500, 30000)  # Program Tempo (500-30000: 5.00-300.00 BPM)
    VOCAL_EFFECT = (0x16, 0, 2, 0, 2)  # Vocal Effect (0: OFF, 1: VOCODER, 2: AUTO-PITCH)
    VOCAL_EFFECT_NUMBER = (0x1C, 0, 20, 0, 20)  # Vocal Effect Number (0-20: 1-21)
    VOCAL_EFFECT_PART = (0x1D, 0, 1, 0, 1)  # Vocal Effect Part (0: Part 1, 1: Part 2)
    AUTO_NOTE_SWITCH = (0x1E, 0, 1, 0, 1)  # Auto Note Switch (0: OFF, 1: ON)

    def get_display_value(self) -> Tuple[int, int]:
        """Get the display value range (min, max) for the parameter"""
        if hasattr(self, 'display_min') and hasattr(self, 'display_max'):
            return self.display_min, self.display_max
        return self.min_val, self.max_val

    @property
    def display_name(self) -> str:
        """Get display name for the parameter"""
        return {
            self.AUTO_NOTE_SWITCH: "Auto Note",
        }.get(self, self.name.replace("_", " ").title())

    def get_address_for_partial(self, partial_num: int = 0) -> Tuple[int, int]:
        """Get parameter area and address adjusted for partial number."""
        group_map = {0: 0x00}
        group = group_map.get(partial_num, 0x00)  # Default to 0x20 if partial_name is not 1, 2, or 3
        return group, self.address

    @property
    def is_switch(self) -> bool:
        """Returns True if parameter is address binary/enum switch"""
        return self in []

    def get_switch_text(self, value: int) -> str:
        """Get display text for switch values"""
        if self == self.AUTO_NOTE_SWITCH:
            return ["OFF", "---", "ON"][value]
        elif self.is_switch:
            return "ON" if value else "OFF"
        return str(value)

    def validate_value(self, value: int) -> int:
        """Validate and convert parameter value"""
        if not isinstance(value, int):
            raise ValueError(f"Value must be integer, got {type(value)}")

        # Special handling for ring switch
        if self == self.AUTO_NOTE_SWITCH and value == 1:
            # Skip over the "---" value
            value = 2

        # Regular range check
        if value < self.min_val or value > self.max_val:
            raise ValueError(
                f"Value {value} out of range for {self.name} "
                f"(valid range: {self.min_val}-{self.max_val})"
            )

        return value

    def get_partial_number(self) -> Optional[int]:
        """Returns the partial number (1-3) if this is address partial parameter, None otherwise"""
        partial_params = {}
        """
        {
            self.PARTIAL1_SWITCH: 1,
            self.PARTIAL1_SELECT: 1,
            self.PARTIAL2_SWITCH: 2,
            self.PARTIAL2_SELECT: 2,
            self.PARTIAL3_SWITCH: 3,
            self.PARTIAL3_SELECT: 3,
        }
        """
        return partial_params.get(self)

    @staticmethod
    def get_by_name(param_name):
        """Get the Parameter by name."""
        # Return the parameter member by name, or None if not found
        return DigitalCommonParameter.__members__.get(param_name, None)
