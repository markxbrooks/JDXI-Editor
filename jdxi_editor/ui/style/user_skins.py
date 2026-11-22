"""
User skins
==========

Skins a user writes as TOML files, with no code, offered in the JDXiSkin menu
beside the built-in ones.

The files live in ``~/.jdxi_editor/skins/`` (:data:`USER_SKIN_DIR`), one skin
per ``*.toml`` file, and are read once when the editor starts. The format is
picoui's (see :mod:`picoui.skin.loader`), with what the editor adds:

- under ``[skin]``, ``meter = "bars"``, ``"needles"`` or ``"vintage_vu"``
  (the Audio Monitor's meters, :class:`~jdxi_editor.ui.style.rack_skin.MeterStyle`);
- a ``[lanes]`` table for the MIDI player: ``cards = true`` for punched
  cards, and ``backing`` the material they lie on;
- ``based_on`` may name any built-in skin, such as ``"tr909"``;
- the editor's woods may be named as gradients: ``"mini_wood"``,
  ``"juno_wood"``.

A file with a mistake is skipped, and the editor says why in its log, rather
than failing to start. A user skin cannot take a built-in skin's id.

See ``doc/skins/tr1000_user.toml`` for a complete example.
"""

from __future__ import annotations

import logging
from pathlib import Path
import re
from typing import Any, List, Mapping, Optional

from picoui.skin.loader import Resolver, SkinFileError, read_skin_file, skin_from_data
from picoui.skin.writer import dumps

from jdxi_editor.log.message import log_message
from jdxi_editor.project import __package_name__
from jdxi_editor.ui.style.rack_skin import (
    JUNO_WOOD,
    MINI_WOOD,
    PLAIN_LANES,
    REGISTRY,
    LaneStyle,
    MeterStyle,
    JDXiSkin,
)

#: Where a user's skin files are read from
USER_SKIN_DIR = Path.home() / f".{__package_name__}" / "skins"

#: Gradients a user's file can name, beyond picoui's own
EDITOR_GRADIENTS = {"mini_wood": MINI_WOOD, "juno_wood": JUNO_WOOD}

#: The skins the editor ships with, which a user skin cannot replace. Taken
#: when this module is first imported, before any user skin is offered.
BUILT_IN_IDS = frozenset(REGISTRY.skins)


def _meter(value: Any) -> MeterStyle:
    try:
        return MeterStyle(value)
    except ValueError:
        choices = ", ".join(f'"{style.value}"' for style in MeterStyle)
        raise ValueError(f"meter {value!r} is not one of {choices}") from None


def _lanes(table: Mapping[str, Any], resolver: Resolver) -> LaneStyle:
    unknown = sorted(set(table) - {"cards", "backing"})
    if unknown:
        raise SkinFileError(f"lanes: unknown {', '.join(unknown)}; [lanes] takes backing, cards")
    cards = table.get("cards", PLAIN_LANES.cards)
    if not isinstance(cards, bool):
        raise SkinFileError(f"lanes.cards: expected true or false, not {cards!r}")
    backing = (
        resolver.material(table["backing"], "lanes.backing")
        if "backing" in table
        else PLAIN_LANES.backing
    )
    return LaneStyle(cards=cards, backing=backing)


def skin_from_tables(data: Mapping[str, Any], registry=REGISTRY) -> JDXiSkin:
    """
    A user skin from a skin file's tables (as read, or as the Skin Editor
    holds them).

    :param data: the tables
    :param registry: SkinRegistry whose skins it may be based on
    :return: JDXiSkin
    :raises SkinFileError: saying where the fault is
    """
    return skin_from_data(
        data,
        JDXiSkin,
        bases=registry.skins,
        gradients=EDITOR_GRADIENTS,
        attributes={"meter": _meter},
        sections={"lanes": _lanes},
    )


def load_user_skin(path: Path, registry=REGISTRY) -> JDXiSkin:
    """
    One user skin from its file.

    :param path: Path the .toml file
    :param registry: SkinRegistry whose skins a file may be based on
    :return: JDXiSkin
    :raises SkinFileError: naming the file and where in it the fault is
    """
    path = Path(path)
    try:
        return skin_from_tables(read_skin_file(path), registry)
    except SkinFileError as error:
        message = str(error)
        raise SkinFileError(message if message.startswith(path.name) else f"{path.name}: {message}") from None


def skin_id_from_label(label: str) -> str:
    """
    An id for a skin named ``label``: lower case, words joined by "_".

    :param label: str such as "My TR-909"
    :return: str such as "my_tr_909"
    """
    words = re.findall(r"[A-Za-z0-9]+", label.lower())
    return "_".join(words) or "my_skin"


def user_skin_path(skin_id: str, folder: Optional[Path] = None) -> Path:
    """
    Where the skin ``skin_id`` is saved.

    :param skin_id: str
    :param folder: Path; :data:`USER_SKIN_DIR` if None
    :return: Path
    """
    return (USER_SKIN_DIR if folder is None else Path(folder)) / f"{skin_id}.toml"


def save_user_skin(data: Mapping[str, Any], folder: Optional[Path] = None) -> Path:
    """
    Write a skin's tables to its file, as TOML.

    :param data: the tables; ``data["skin"]["id"]`` names the file
    :param folder: Path; :data:`USER_SKIN_DIR` if None
    :return: Path the file written
    :raises ValueError: for a built-in skin's id
    """
    skin_id = str(data["skin"]["id"])
    if skin_id in BUILT_IN_IDS:
        raise ValueError(f"{skin_id!r} is a built-in skin's id; choose another")
    path = user_skin_path(skin_id, folder)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dumps(data), encoding="utf-8")
    return path


def load_user_skins(folder: Optional[Path] = None, registry=REGISTRY) -> List[JDXiSkin]:
    """
    Offer every skin in ``folder``'s ``*.toml`` files, in name order.

    Call once at start-up, before the window builds its JDXiSkin menu. A
    file with a mistake, or one taking a built-in skin's id, is skipped and
    logged.

    :param folder: Path; :data:`USER_SKIN_DIR` if None
    :param registry: SkinRegistry to offer them in
    :return: the skins offered
    """
    folder = USER_SKIN_DIR if folder is None else Path(folder)
    if not folder.is_dir():
        return []
    built_in = BUILT_IN_IDS if registry is REGISTRY else set(registry.skins)
    loaded: List[JDXiSkin] = []
    for path in sorted(folder.glob("*.toml")):
        try:
            skin = load_user_skin(path, registry)
        except SkinFileError as error:
            log_message(f"Skin file skipped: {error}", level=logging.WARNING)
            continue
        if skin.skin_id in built_in:
            log_message(
                f"Skin file skipped: {path.name}: id {skin.skin_id!r} is a built-in "
                f"skin's; give it an id of its own (based_on = {skin.skin_id!r} "
                "starts from that skin)",
                level=logging.WARNING,
            )
            continue
        registry.register(skin)
        loaded.append(skin)
        log_message(f"Skin loaded: {skin.label} ({path.name})")
    return loaded
