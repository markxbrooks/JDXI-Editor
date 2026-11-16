"""
Stored controller mappings
==========================

The CC numbers a controller sends differ between devices, and between the
programs of one device: the MiniLab 3 map in
:mod:`jdxi_editor.midi.io.controller_map` is only a sensible default. What the
user learns in the MIDI Controller dialog is kept here, in QSettings, so it
survives a restart.

Each entry is stored as ``midi_controller/mapping/<control name>`` -> CC
number, for example ``midi_controller/mapping/CUTOFF`` -> ``74``.
"""

from __future__ import annotations

from typing import Dict, Optional

from decologr import Decologr as log
from PySide6.QtCore import QSettings

from jdxi_editor.midi.io.controller_map import (
    MINILAB3,
    ControllerProfile,
    FilterControl,
)
from jdxi_editor.project import __organization_name__, __program__

#: QSettings group holding one key per mapped control (MiniLab 3; other
#: controllers use :func:`mapping_group`)
MAPPING_GROUP = "midi_controller/mapping"


def mapping_group(profile: ControllerProfile = MINILAB3) -> str:
    """
    QSettings group for ``profile``'s learnt mappings.

    The MiniLab 3 keeps the original group, so mappings learnt before other
    controllers were supported still load.

    :param profile: ControllerProfile
    :return: str settings group
    """
    if profile.profile_id == MINILAB3.profile_id:
        return MAPPING_GROUP
    return f"midi_controller/{profile.profile_id}/mapping"


def _settings() -> QSettings:
    """
    The application's settings store.

    :return: QSettings
    """
    return QSettings(__organization_name__, __program__)


def default_filter_map(
    profile: ControllerProfile = MINILAB3,
) -> Dict[int, FilterControl]:
    """
    The built-in map of ``profile``.

    :param profile: ControllerProfile defaults to the MiniLab 3
    :return: dict CC number -> FilterControl
    """
    return dict(profile.cc_map)


def load_filter_map(
    settings: Optional[QSettings] = None, profile: ControllerProfile = MINILAB3
) -> Dict[int, FilterControl]:
    """
    The stored mapping, falling back to the built-in one per control.

    A control with nothing stored keeps its default CC, so a part-finished
    learn still leaves a usable map.

    :param settings: Optional[QSettings] store to read; defaults to the
        application's own
    :param profile: ControllerProfile whose mappings and defaults to use
    :return: dict CC number -> FilterControl
    """
    store = _settings() if settings is None else settings
    group = mapping_group(profile)
    mapping: Dict[int, FilterControl] = {}
    for control in FilterControl:
        value = store.value(f"{group}/{control.name}")
        cc = _as_cc(value)
        if cc is None:
            cc = _default_cc(control, profile)
        if cc is not None:
            mapping[cc] = control
    return mapping


def save_filter_map(
    mapping: Dict[int, FilterControl],
    settings: Optional[QSettings] = None,
    profile: ControllerProfile = MINILAB3,
) -> None:
    """
    Store ``mapping`` for ``profile``, replacing whatever was there.

    :param mapping: dict CC number -> FilterControl
    :param settings: Optional[QSettings] store to write; defaults to the
        application's own
    :param profile: ControllerProfile the mapping belongs to
    :return: None
    """
    store = _settings() if settings is None else settings
    group = mapping_group(profile)
    store.remove(group)
    for cc, control in mapping.items():
        store.setValue(f"{group}/{control.name}", int(cc))
    store.sync()
    log.message(
        f"Saved {len(mapping)} controller mappings", scope="controller_settings"
    )


def clear_filter_map(
    settings: Optional[QSettings] = None, profile: ControllerProfile = MINILAB3
) -> None:
    """
    Forget ``profile``'s stored mapping, so its built-in one is used again.

    :param settings: Optional[QSettings] store to clear; defaults to the
        application's own
    :param profile: ControllerProfile whose mapping to forget
    :return: None
    """
    store = _settings() if settings is None else settings
    store.remove(mapping_group(profile))
    store.sync()


def _default_cc(
    control: FilterControl, profile: ControllerProfile = MINILAB3
) -> Optional[int]:
    """
    ``profile``'s built-in CC number for ``control``.

    :param control: FilterControl
    :param profile: ControllerProfile
    :return: Optional[int]
    """
    return next((cc for cc, c in profile.cc_map.items() if c is control), None)


def _as_cc(value: object) -> Optional[int]:
    """
    Read a stored value as a CC number.

    QSettings hands back strings on some platforms, and the file can be edited
    by hand, so anything unusable is discarded rather than trusted.

    :param value: object stored value
    :return: Optional[int] a CC number 0-127, or None
    """
    if value is None:
        return None
    try:
        cc = int(value)
    except (TypeError, ValueError):
        return None
    return cc if 0 <= cc <= 127 else None
