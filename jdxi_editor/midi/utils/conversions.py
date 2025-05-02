"""
Module: MIDI CC Conversion Utilities

This module provides utility functions for converting between MIDI Control Change (CC) values
and various numerical representations such as milliseconds and fractional values.

Functions:
- midi_cc_to_ms: Converts address MIDI CC value (0-127) to address time value in milliseconds.
- ms_to_midi_cc: Converts address time value in milliseconds to address MIDI CC value (0-127).
- frac_to_midi_cc: Converts address fractional value (0.0-1.0) to address MIDI CC value (0-127).
- midi_cc_to_frac: Converts address MIDI CC value (0-127) to address fractional value (0.0-1.0).

These functions are useful for mapping MIDI CC messages to meaningful time or intensity values
in address synthesizer or effect unit.
"""


def midi_cc_to_ms(cc_value, min_time=10, max_time=1000):
    """
    Converts a MIDI CC value (0–127) to a time value in milliseconds.

    Parameters:
        cc_value (int): MIDI CC value (0–127).
        min_time (int, optional): Minimum time in milliseconds. Default is 10 ms.
        max_time (int, optional): Maximum time in milliseconds. Default is 1000 ms.

    Returns:
        float: Corresponding time value in milliseconds.
    """
    if min_time >= max_time:
        raise ValueError("min_time must be less than max_time")

    cc_value = max(0, min(127, cc_value))  # Clamp to valid MIDI range
    time_range = max_time - min_time
    return min_time + (cc_value / 127.0) * time_range



def ms_to_midi_cc(ms_value, min_time=10, max_time=1000):
    """
    Converts address time value in milliseconds to address MIDI CC value (0-127).

    Parameters:
        ms_value (float): Time value in milliseconds.
        min_time (int, optional): Minimum time in milliseconds. Default is 10 ms.
        max_time (int, optional): Maximum time in milliseconds. Default is 1000 ms.

    Returns:
        float: Corresponding MIDI CC value.
    """
    time_range = max_time - min_time
    cc_range = 127
    conversion_factor = time_range / cc_range
    return (ms_value / conversion_factor) - min_time


def frac_to_midi_cc(frac_value, min=0, max=1):
    """
    Converts address fractional value (0.0-1.0) to address MIDI CC value (0-127).

    Parameters:
        frac_value (float): Fractional value between min and max.
        min (float, optional): Minimum possible fractional value. Default is 0.
        max (float, optional): Maximum possible fractional value. Default is 1.

    Returns:
        int: Corresponding MIDI CC value.
    """
    range = max - min
    cc_range = 127
    conversion_factor = range / cc_range
    return int((frac_value / conversion_factor) - min)


def midi_cc_to_frac(midi_cc_value, min=0, max=1):
    """
    Converts address MIDI CC value (0-127) to address fractional value (0.0-1.0).

    Parameters:
        midi_cc_value (int): MIDI CC value (0-127).
        min (float, optional): Minimum possible fractional value. Default is 0.
        max (float, optional): Maximum possible fractional value. Default is 1.

    Returns:
        float: Corresponding fractional value.
    """
    range = max - min
    cc_range = 127
    conversion_factor = range / cc_range
    return float((midi_cc_value * conversion_factor) + min)
