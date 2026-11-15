"""
External MIDI controller maps
=============================

Routes control-change messages from a hardware controller (not the JD-Xi) to
filter controls of the synth editor that is open.

**Arturia MiniLab 3** (factory/User program, MIDI channel 1):

========  =====  ==============================
Control   CC     JD-Xi filter control
========  =====  ==============================
Knob 1    74     Cutoff
Knob 2    71     Resonance
Knob 3    76     Cutoff key follow
Knob 4    77     Envelope depth
Knob 5    93     Envelope velocity sensitivity
Fader 1   82     Filter envelope attack
Fader 2   83     Filter envelope decay
Fader 3   85     Filter envelope sustain
Fader 4   17     Filter envelope release
========  =====  ==============================

If your MiniLab program sends other CC numbers, watch them in the MIDI
Monitor and change :data:`MINILAB3_FILTER_MAP`. Every port the controller
exposes is listened to, so the knobs are picked up whichever mode it is in.

Example
-------
>>> MINILAB3_FILTER_MAP[74]
<FilterControl.CUTOFF: 'FILTER_CUTOFF'>
>>> find_controller_port(["JD-Xi", "Minilab3 DIN THRU", "Minilab3 MIDI"])
'Minilab3 MIDI'
"""

from __future__ import annotations

from enum import Enum
from typing import Iterable, Optional


class FilterControl(Enum):
    """Filter controls a hardware controller can drive; values are parameter names."""

    CUTOFF = "FILTER_CUTOFF"
    RESONANCE = "FILTER_RESONANCE"
    KEYFOLLOW = "FILTER_CUTOFF_KEYFOLLOW"
    ENV_DEPTH = "FILTER_ENV_DEPTH"
    ENV_VELOCITY = "FILTER_ENV_VELOCITY_SENSITIVITY"
    ENV_ATTACK = "FILTER_ENV_ATTACK_TIME"
    ENV_DECAY = "FILTER_ENV_DECAY_TIME"
    ENV_SUSTAIN = "FILTER_ENV_SUSTAIN_LEVEL"
    ENV_RELEASE = "FILTER_ENV_RELEASE_TIME"


#: MiniLab 3 CC number -> filter control (knobs 1-5, faders 1-4)
MINILAB3_FILTER_MAP: dict[int, FilterControl] = {
    74: FilterControl.CUTOFF,
    71: FilterControl.RESONANCE,
    76: FilterControl.KEYFOLLOW,
    77: FilterControl.ENV_DEPTH,
    93: FilterControl.ENV_VELOCITY,
    82: FilterControl.ENV_ATTACK,
    83: FilterControl.ENV_DECAY,
    85: FilterControl.ENV_SUSTAIN,
    17: FilterControl.ENV_RELEASE,
}

#: Substrings that identify a supported controller's input port
CONTROLLER_PORT_NAMES = ("minilab",)

#: Ports a MiniLab 3 also exposes. Which one carries the knobs and faders
#: depends on the mode the device is in (its Arturia/DAW/Analog Lab layers), so
#: these are listened to as well rather than guessed at; they are only ranked
#: below the main port when one has to be named.
_SECONDARY_PORT_NAMES = ("din thru", "mcu", "hui", "alv")


def find_controller_ports(port_names: Iterable[str]) -> list[str]:
    """
    Every input port belonging to a supported hardware controller.

    All of them are worth listening to: a MiniLab 3 sends its knobs on the port
    that matches its current mode, and listening to each one means the knobs
    are picked up without the user having to know which mode that is.

    :param port_names: Iterable[str] available MIDI input port names
    :return: list[str] the controller's ports, main port first
    """
    candidates = [
        name
        for name in port_names
        if any(key in name.lower() for key in CONTROLLER_PORT_NAMES)
    ]
    main = [
        name
        for name in candidates
        if not any(key in name.lower() for key in _SECONDARY_PORT_NAMES)
    ]
    secondary = [name for name in candidates if name not in main]
    return main + secondary


def find_controller_port(port_names: Iterable[str]) -> Optional[str]:
    """
    Pick the main input port of a supported hardware controller.

    :param port_names: Iterable[str] available MIDI input port names
    :return: Optional[str] the controller's main port, or None if none is connected
    """
    return next(iter(find_controller_ports(port_names)), None)
