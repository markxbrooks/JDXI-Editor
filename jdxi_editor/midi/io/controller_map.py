"""
External MIDI controller maps
=============================

Routes control-change messages from a hardware controller (not the JD-Xi) to
filter controls of the synth editor that is open, and to the effect levels that
the JD-Xi's own right-hand knobs set.

Each supported controller is a :class:`ControllerProfile`, read from JSON
rather than written here:

* ``midi_controllers.json`` next to this module holds the built-in controllers
  (the Arturia MiniLab 3 and the SINCO VMX8);
* ``~/.jdxi_editor/midi_controllers.json`` (:func:`user_config_path`) is the
  user's copy, written on first start by :func:`install_user_config`. A
  controller in it overrides the keys it gives of the built-in one with the
  same ``id``; a new ``id`` adds a controller.

Set the environment variable ``JDXI_EDITOR_MIDI_CONTROLLERS`` to read another
user file, or to an empty string to use the built-in controllers only.
Changes to the file take effect when the editor is restarted. Mappings learnt
in the MIDI Controller dialog are stored separately and take precedence
(:mod:`jdxi_editor.midi.io.controller_settings`).

A controller entry looks like::

    {
      "id": "minilab3",
      "label": "Arturia MiniLab 3",
      "port_names": ["minilab"],
      "secondary_port_names": ["din thru", "mcu", "hui", "alv"],
      "single_port": false,
      "mappings": [{"cc": 74, "control": "CUTOFF", "source": "Knob 1"}, ...],
      "transport": [{"action": "PLAY", "cc": 107}, {"action": "PAUSE", "note": 93}]
    }

``control`` is a :class:`FilterControl` name and ``source`` the physical knob
or fader, shown in the MIDI Controller dialog. ``transport`` lists the
controller's transport buttons (:class:`TransportAction` names), each sending a
``cc`` or a ``note``, with an optional ``channel`` (0 = MIDI channel 1).

Example
-------
>>> MINILAB3_FILTER_MAP[74]
<FilterControl.CUTOFF: 'FILTER_CUTOFF'>
>>> MINILAB3.sources[FilterControl.CUTOFF]
'Knob 1'
>>> find_controller_port(["JD-Xi", "Minilab3 DIN THRU", "Minilab3 MIDI"])
'Minilab3 MIDI'
>>> find_controller_ports(["JD-Xi", "SINCO VMX8-Private", "SINCO VMX8-Master"])
['SINCO VMX8-Private']
>>> VMX8_FILTER_MAP[32]
<FilterControl.CUTOFF: 'FILTER_CUTOFF'>
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Iterable, Optional

from decologr import Decologr as log

from jdxi_editor.project import __package_name__


class FilterControl(Enum):
    """
    Controls a hardware controller can drive; values are parameter names.

    Despite the name, this also covers the program effect levels
    (:data:`EFFECT_CONTROLS`), which the Effects editor holds.
    """

    CUTOFF = "FILTER_CUTOFF"
    RESONANCE = "FILTER_RESONANCE"
    KEYFOLLOW = "FILTER_CUTOFF_KEYFOLLOW"
    ENV_DEPTH = "FILTER_ENV_DEPTH"
    ENV_VELOCITY = "FILTER_ENV_VELOCITY_SENSITIVITY"
    ENV_ATTACK = "FILTER_ENV_ATTACK_TIME"
    ENV_DECAY = "FILTER_ENV_DECAY_TIME"
    ENV_SUSTAIN = "FILTER_ENV_SUSTAIN_LEVEL"
    ENV_RELEASE = "FILTER_ENV_RELEASE_TIME"
    EFFECT1_LEVEL = "EFX1_LEVEL"
    EFFECT2_LEVEL = "EFX2_LEVEL"
    DELAY_LEVEL = "DELAY_LEVEL"
    REVERB_LEVEL = "REVERB_LEVEL"


#: Controls held by the Effects editor rather than a synth editor
EFFECT_CONTROLS = frozenset(
    {
        FilterControl.EFFECT1_LEVEL,
        FilterControl.EFFECT2_LEVEL,
        FilterControl.DELAY_LEVEL,
        FilterControl.REVERB_LEVEL,
    }
)


class TransportAction(Enum):
    """Transport commands a hardware controller's buttons can request."""

    PLAY = auto()
    PAUSE = auto()
    STOP = auto()
    RECORD = auto()
    REWIND = auto()
    FAST_FORWARD = auto()


@dataclass(frozen=True)
class TransportSpec:
    """
    One transport button of a controller, as ``midi_controllers.json`` lists it.

    :param action: TransportAction what the button does
    :param kind: str ``"cc"`` (press 127 / release 0) or ``"note"`` (note on / off)
    :param channel: int MIDI channel as mido numbers it (0 = MIDI channel 1)
    :param number: int CC or note number 0-127
    """

    action: TransportAction
    kind: str
    channel: int
    number: int

    @classmethod
    def from_dict(cls, entry: dict) -> "TransportSpec":
        """
        Build a button from one ``transport`` entry, e.g. ``{"action": "PLAY", "cc": 52}``.

        :param entry: dict with ``action``, one of ``cc`` / ``note``, and
            optionally ``channel`` (default 0)
        :return: TransportSpec
        :raises KeyError: if the action is unknown or neither ``cc`` nor ``note`` is given
        :raises ValueError: if a number is outside its MIDI range
        """
        kind = next((k for k in ("cc", "note") if k in entry), None)
        if kind is None:
            raise KeyError("transport entry needs 'cc' or 'note'")
        number, channel = int(entry[kind]), int(entry.get("channel", 0))
        if not (0 <= number <= 127 and 0 <= channel <= 15):
            raise ValueError(f"{kind} {number} / channel {channel} out of range")
        return cls(TransportAction[entry["action"]], kind, channel, number)

    def to_dict(self) -> dict:
        """
        This button as a ``transport`` entry, the inverse of :meth:`from_dict`.

        :return: dict e.g. ``{"action": "PLAY", "cc": 52, "channel": 0}``
        """
        return {"action": self.action.name, self.kind: self.number, "channel": self.channel}

    @property
    def label(self) -> str:
        """
        What the button sends, for display.

        :return: str e.g. ``"CC 52"``, ``"Note 94"`` or ``"CC 52 (ch 2)"``
        """
        text = f"{'CC' if self.kind == 'cc' else 'Note'} {self.number}"
        return text if self.channel == 0 else f"{text} (ch {self.channel + 1})"

    def matches(self, message: object) -> bool:
        """
        Whether ``message`` is a press of this button.

        :param message: mido.Message
        :return: bool True for a note-on with velocity, or a CC of 64 or more
        """
        if getattr(message, "channel", None) != self.channel:
            return False
        if self.kind == "cc":
            return (
                getattr(message, "type", None) == "control_change"
                and message.control == self.number
                and message.value >= 64
            )
        return (
            getattr(message, "type", None) == "note_on"
            and message.note == self.number
            and message.velocity > 0
        )


@dataclass(frozen=True)
class ControllerProfile:
    """
    A supported hardware controller: how to find its ports, and its default map.

    :param profile_id: str stable id, used as the settings key
    :param label: str name shown in the MIDI Controller dialog
    :param port_names: tuple[str, ...] lower-case substrings of its port names
    :param secondary_port_names: tuple[str, ...] substrings of ports ranked
        after the main one
    :param single_port: bool listen to the main port only; for devices that
        send every message on each of their ports
    :param cc_map: dict CC number -> FilterControl defaults
    :param sources: dict FilterControl -> physical control that sends it, e.g.
        "Knob 1"; controls whose source is unknown are left out
    :param transport: tuple[TransportSpec, ...] its transport buttons
    """

    profile_id: str
    label: str
    port_names: tuple[str, ...]
    secondary_port_names: tuple[str, ...] = ()
    single_port: bool = False
    cc_map: dict[int, FilterControl] = field(default_factory=dict)
    sources: dict[FilterControl, str] = field(default_factory=dict)
    transport: tuple[TransportSpec, ...] = ()

    @classmethod
    def from_dict(cls, entry: dict) -> "ControllerProfile":
        """
        Build a profile from one ``controllers`` entry of the JSON config.

        :param entry: dict with ``id``, ``label``, ``port_names`` and ``mappings``,
            and optionally ``secondary_port_names``, ``single_port`` and ``transport``
        :return: ControllerProfile
        :raises KeyError: if a required key or a control name is unknown
        :raises ValueError: if a CC number is not 0-127
        :raises TypeError: if a value has the wrong type
        """
        cc_map: dict[int, FilterControl] = {}
        sources: dict[FilterControl, str] = {}
        for mapping in entry["mappings"]:
            cc = int(mapping["cc"])
            if not 0 <= cc <= 127:
                raise ValueError(f"CC {cc} is outside 0-127")
            control = FilterControl[mapping["control"]]
            cc_map[cc] = control
            if mapping.get("source"):
                sources[control] = str(mapping["source"])
        return cls(
            profile_id=str(entry["id"]),
            label=str(entry.get("label", entry["id"])),
            port_names=tuple(n.lower() for n in entry["port_names"]),
            secondary_port_names=tuple(
                n.lower() for n in entry.get("secondary_port_names", ())
            ),
            single_port=bool(entry.get("single_port", False)),
            cc_map=cc_map,
            sources=sources,
            transport=tuple(
                TransportSpec.from_dict(t) for t in entry.get("transport", ())
            ),
        )

    def matches(self, port_name: str) -> bool:
        """
        Whether ``port_name`` belongs to this controller.

        :param port_name: str MIDI port name
        :return: bool
        """
        return any(key in port_name.lower() for key in self.port_names)

    def ports(self, port_names: Iterable[str]) -> list[str]:
        """
        This controller's ports among ``port_names`` that should be opened.

        :param port_names: Iterable[str] available MIDI input port names
        :return: list[str] main port(s) first; only one for ``single_port``
        """
        candidates = [name for name in port_names if self.matches(name)]
        main = [
            name
            for name in candidates
            if not any(key in name.lower() for key in self.secondary_port_names)
        ]
        ordered = main + [name for name in candidates if name not in main]
        return ordered[:1] if self.single_port else ordered


#: Built-in controllers, shipped with the package
BUILTIN_CONFIG_PATH = Path(__file__).with_name("midi_controllers.json")
#: File name of the user's controller config in ``~/.jdxi_editor``
USER_CONFIG_NAME = "midi_controllers.json"
#: Environment variable naming another user config ("" for built-ins only)
CONFIG_ENV_VAR = "JDXI_EDITOR_MIDI_CONTROLLERS"


def user_config_path() -> Optional[Path]:
    """
    Where the user's controller config is read from.

    :return: Optional[Path] ``~/.jdxi_editor/midi_controllers.json``, the path in
        ``JDXI_EDITOR_MIDI_CONTROLLERS``, or None if that variable is empty
    """
    try:
        override = os.environ[CONFIG_ENV_VAR]
    except KeyError:
        return Path.home() / f".{__package_name__}" / USER_CONFIG_NAME
    return Path(override).expanduser() if override else None


def read_entries(path: Path) -> list[dict]:
    """
    The raw ``controllers`` entries of one JSON config file.

    :param path: Path JSON file with a ``controllers`` list
    :return: list[dict] in file order
    :raises OSError: if the file cannot be read
    :raises ValueError: if it is not valid JSON
    """
    return list(json.loads(path.read_text(encoding="utf-8")).get("controllers", []))


def _parse(entries: Iterable[dict], origin: object) -> list[ControllerProfile]:
    """
    Profiles from raw entries; an entry that cannot be read is logged and skipped.

    :param entries: Iterable[dict] raw controller entries
    :param origin: object where they came from, for the log
    :return: list[ControllerProfile]
    """
    profiles = []
    for entry in entries:
        try:
            profiles.append(ControllerProfile.from_dict(entry))
        except (KeyError, ValueError, TypeError, AttributeError) as ex:
            log.warning(
                f"{origin}: skipping controller {entry.get('id', '?')!r}: {ex!r}",
                scope="controller_map",
            )
    return profiles


def read_profiles(path: Path) -> list[ControllerProfile]:
    """
    The controllers in one JSON config file.

    An entry that cannot be read is logged and skipped, so one typo does not
    lose the other controllers.

    :param path: Path JSON file with a ``controllers`` list
    :return: list[ControllerProfile] in file order
    :raises OSError: if the file cannot be read
    :raises ValueError: if it is not valid JSON
    """
    return _parse(read_entries(path), path)


def load_controller_profiles(
    user_path: Optional[Path] = None,
) -> tuple[ControllerProfile, ...]:
    """
    The built-in controllers, overridden or extended by the user's config.

    A user entry with a built-in ``id`` overrides only the keys it has: an
    older copy without ``transport`` still gets the built-in transport buttons.

    :param user_path: Optional[Path] user config; defaults to :func:`user_config_path`
    :return: tuple[ControllerProfile, ...] built-in order first, then new user ones
    """
    entries = {e["id"]: e for e in read_entries(BUILTIN_CONFIG_PATH)}
    path = user_config_path() if user_path is None else user_path
    if path is not None:
        try:
            user_entries = read_entries(path)
        except FileNotFoundError:
            user_entries = []
        except (OSError, ValueError) as ex:
            log.warning(
                f"Ignoring controller config {path}: {ex!r}", scope="controller_map"
            )
            user_entries = []
        for entry in user_entries:
            try:
                entries[entry["id"]] = {**entries.get(entry["id"], {}), **entry}
            except (KeyError, TypeError) as ex:
                log.warning(f"{path}: skipping entry: {ex!r}", scope="controller_map")
    return tuple(_parse(entries.values(), path or BUILTIN_CONFIG_PATH))


def install_user_config(path: Optional[Path] = None) -> Optional[Path]:
    """
    Copy the built-in controller config to the user's, if there is none yet.

    An existing file is never overwritten.

    :param path: Optional[Path] destination; defaults to :func:`user_config_path`
    :return: Optional[Path] the user config, or None if it is disabled or
        could not be written
    """
    target = user_config_path() if path is None else path
    if target is None:
        return None
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("x", encoding="utf-8") as handle:
            handle.write(BUILTIN_CONFIG_PATH.read_text(encoding="utf-8"))
    except FileExistsError:
        return target
    except OSError as ex:
        log.warning(f"Cannot write {target}: {ex!r}", scope="controller_map")
        return None
    log.message(f"Wrote controller config {target}", scope="controller_map")
    return target


#: Supported controllers, in the order they are looked for
CONTROLLER_PROFILES: tuple[ControllerProfile, ...] = load_controller_profiles()


def _profile(profile_id: str) -> ControllerProfile:
    return next(p for p in CONTROLLER_PROFILES if p.profile_id == profile_id)


#: Arturia MiniLab 3, the default controller
MINILAB3 = _profile("minilab3")
#: SINCO VMX8 (its map is translated from the MiniLab 3's through ElMo)
VMX8 = _profile("vmx8")
#: MiniLab 3 CC number -> control (knobs 1-8, faders 1-4)
MINILAB3_FILTER_MAP: dict[int, FilterControl] = MINILAB3.cc_map
#: SINCO VMX8 CC number -> control
VMX8_FILTER_MAP: dict[int, FilterControl] = VMX8.cc_map

#: Substrings that identify a supported controller's input port
CONTROLLER_PORT_NAMES = tuple(
    key for profile in CONTROLLER_PROFILES for key in profile.port_names
)


def profile_by_id(profile_id: Optional[str]) -> ControllerProfile:
    """
    The profile with ``profile_id``, or the MiniLab 3 one if there is none.

    :param profile_id: Optional[str]
    :return: ControllerProfile
    """
    return next(
        (p for p in CONTROLLER_PROFILES if p.profile_id == profile_id), MINILAB3
    )


def detect_profile(port_names: Iterable[str]) -> Optional[ControllerProfile]:
    """
    The first supported controller that has a port among ``port_names``.

    :param port_names: Iterable[str] MIDI port names
    :return: Optional[ControllerProfile] None if no supported controller is connected
    """
    names = list(port_names)
    return next(
        (p for p in CONTROLLER_PROFILES if any(p.matches(n) for n in names)), None
    )


def find_controller_ports(port_names: Iterable[str]) -> list[str]:
    """
    The input ports to open for the connected hardware controller.

    For a MiniLab 3 that is every port, since it sends its knobs on the port
    matching its current mode; for a VMX8, which repeats each message on both
    its ports, it is the main port alone (see :class:`ControllerProfile`).

    :param port_names: Iterable[str] available MIDI input port names
    :return: list[str] the controller's ports, main port first
    """
    names = list(port_names)
    profile = detect_profile(names)
    return profile.ports(names) if profile is not None else []


def find_controller_port(port_names: Iterable[str]) -> Optional[str]:
    """
    Pick the main input port of a supported hardware controller.

    :param port_names: Iterable[str] available MIDI input port names
    :return: Optional[str] the controller's main port, or None if none is connected
    """
    return next(iter(find_controller_ports(port_names)), None)
