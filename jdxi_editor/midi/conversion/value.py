from enum import Enum, auto

from picomidi.utils.conversion import midi_value_to_fraction, midi_value_to_ms


class ValueTransform(Enum):
    MS = auto()
    FRACTION = auto()
    PITCH_ENV_TIME = auto()


def convert_value(transform: ValueTransform, midi_value: int) -> float:
    if transform is ValueTransform.FRACTION:
        return midi_value_to_fraction(midi_value)

    if transform is ValueTransform.PITCH_ENV_TIME:
        return midi_value_to_ms(midi_value, 10, 5000)

    return midi_value_to_ms(midi_value)
