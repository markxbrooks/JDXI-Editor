"""
jdxi_editor.midi.io.program_channel
The channel the JD-Xi takes program changes on.

The editor sends programs on channel 16 (index 15), the JD-Xi's factory
setting. The JD-Xi takes them on its SYSTEM › Program Ctrl Ch, which can be
another channel or OFF; set to another one, the app's program changes did
nothing (the window then read the program back and showed the old one again).
The window reads the setting at start (follow.py) and records it here; program
changes meant for channel 16 then go to the channel the JD-Xi listens on.

Example:
    >>> set_from_system(0x00, rx_program_change=1, rx_bank_select=1)  # Ch 1
    >>> route(15), route(2)
    (0, 2)
    >>> reset(); route(15)
    15
"""

from __future__ import annotations

from typing import Optional

DEFAULT = 15  # channel 16
OFF = 16  # the SYSTEM value for OFF

_channel: Optional[int] = None  # None: not read yet (channel 16 assumed)
_rx_program_change = True
_rx_bank_select = True


def reset() -> None:
    global _channel, _rx_program_change, _rx_bank_select
    _channel, _rx_program_change, _rx_bank_select = None, True, True


def set_from_system(channel: int, rx_program_change: int, rx_bank_select: int) -> None:
    """The SYSTEM values: Program Ctrl Ch (0-15, 16 OFF), Rx Program Change, Rx Bank Select."""
    global _channel, _rx_program_change, _rx_bank_select
    _channel = int(channel)
    _rx_program_change = bool(rx_program_change)
    _rx_bank_select = bool(rx_bank_select)


def channel() -> int:
    """The program channel (0-15); channel 16 when not read or OFF."""
    return _channel if _channel is not None and _channel < OFF else DEFAULT


def route(requested: int) -> int:
    """Program changes for channel 16 go to the JD-Xi's program channel."""
    try:
        requested = int(requested)
    except (TypeError, ValueError):
        return requested
    return channel() if requested == DEFAULT else requested


def problem() -> Optional[str]:
    """Why the JD-Xi will not take program changes (None if it will, or not read yet)."""
    if _channel is None:
        return None
    reasons = []
    if _channel >= OFF:
        reasons.append("Program Ctrl Ch: OFF")
    if not _rx_program_change:
        reasons.append("Rx Program Change: OFF")
    if not _rx_bank_select:
        reasons.append("Rx Bank Select: OFF")
    return ", ".join(reasons) or None
