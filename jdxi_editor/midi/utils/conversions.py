"""
Module: MIDI CC Conversion Utilities

This module provides utility functions for converting between MIDI values
and various numerical representations such as milliseconds and fractional values.

Functions:
- midi_value_to_ms: Converts address MIDI value (0-127) to address time value in milliseconds.
- ms_to_midi_value: Converts address time value in milliseconds to address MIDI value (0-127).
- fraction_to_midi_value: Converts address fractional value (0.0-1.0) to address MIDI value (0-127).
- midi_value_to_fraction: Converts address MIDI value (0-127) to address fractional value (0.0-1.0).

These functions are useful for mapping MIDI messages to meaningful time or intensity values
in address synthesizer or effect unit.
"""


def midi_value_to_ms(
    midi_value: int, min_time: int = 10, max_time: int = 1000
) -> float:
    """
    Converts a MIDI value (0–127) to a time value in milliseconds.
    :param midi_value: int MIDI CC value (0–127).
    :param min_time: int, optional: Minimum time in milliseconds. Default is 10 ms.
    :param max_time: int, optional: Maximum time in milliseconds. Default is 1000 ms.
    :returns: float Corresponding time value in milliseconds.
    """
    if min_time >= max_time:
        raise ValueError("min_time must be less than max_time")

    midi_value = max(0, min(127, midi_value))  # Clamp to valid MIDI range
    time_range = max_time - min_time
    ms_time = min_time + (midi_value / 127.0) * time_range
    return ms_time


def ms_to_midi_value(ms_time: float, min_time: int = 10, max_time: int = 1000) -> int:
    """
    Converts address time value in milliseconds to address MIDI byte range value (0-127)
    :param ms_time: float: Time value in milliseconds.
    :param min_time: int, optional: Minimum time in milliseconds. Default is 10 ms.
    :param max_time: int, optional: Maximum time in milliseconds. Default is 1000 ms.
    :return: int Corresponding MIDI value (1-127)
    """
    time_range = max_time - min_time
    midi_byte_range = 127
    conversion_factor = time_range / midi_byte_range
    midi_value = int((ms_time / conversion_factor) - min_time)
    return midi_value


def fraction_to_midi_value(
    fractional_value: float, minimum: float = 0, maximum: float = 1
) -> int:
    """
    Converts address fractional value (0.0-1.0) to address MIDI CC value (0-127).
    :param fractional_value: float Fractional value between min and max.
    :param minimum: float optional Minimum possible fractional value. Default is 0.
    :param maximum: float optional Maximum possible fractional value. Default is 1.
    :returns: int: Corresponding MIDI value.
    """
    value_range = maximum - minimum
    midi_byte_range = 127
    conversion_factor = value_range / midi_byte_range
    midi_value = int((fractional_value / conversion_factor) - minimum)
    return midi_value


def midi_value_to_fraction(
    midi_value: int, minimum: float = 0, maximum: float = 1
) -> float:
    """
    Converts address MIDI value (0-127) to address fractional value (0.0-1.0).

    :param midi_value: int: MIDI CC value (0-127).
    :param minimum: float, optional Minimum possible fractional value. Default is 0.
    :param maximum: float, optional Maximum possible fractional value. Default is 1.
    :returns: float Corresponding fractional value.
    """
    value_range = maximum - minimum
    midi_byte_range = 127
    conversion_factor = value_range / midi_byte_range
    return float((midi_value * conversion_factor) + minimum)
