"""
Control Change Parameters
"""

from enum import IntEnum


class ControlChange(IntEnum):
    """Base class for Synth Control Change parameters"""

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to digital value"""
        if param == 3:  # LFO Shape
            shapes = ["TRI", "SIN", "SAW", "SQR", "S&H", "RND"]
            return shapes[value]
        return str(value)
