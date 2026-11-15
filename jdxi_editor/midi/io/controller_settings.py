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

from jdxi_editor.midi.io.controller_map import MINILAB3_FILTER_MAP, FilterControl
from jdxi_editor.project import __organization_name__, __program__

#: QSettings group holding one key per mapped control
MAPPING_GROUP = "midi_controller/mapping"


def _settings() -> QSettings:
    """
    The application's settings store.

    :return: QSettings
    """
    return QSettings(__organization_name__, __program__)


def default_filter_map() -> Dict[int, FilterControl]:
    """
    The built-in MiniLab 3 map.

    :return: dict CC number -> FilterControl
    """
    return dict(MINILAB3_FILTER_MAP)


def load_filter_map(settings: Optional[QSettings] = None) -> Dict[int, FilterControl]:
    """
    The stored mapping, falling back to the built-in one per control.

    A control with nothing stored keeps its default CC, so a part-finished
    learn still leaves a usable map.

    :param settings: Optional[QSettings] store to read; defaults to the
        application's own
    :return: dict CC number -> FilterControl
    """
    store = _settings() if settings is None else settings
    mapping: Dict[int, FilterControl] = {}
    for control in FilterControl:
        value = store.value(f"{MAPPING_GROUP}/{control.name}")
        cc = _as_cc(value)
        if cc is None:
            cc = _default_cc(control)
        if cc is not None:
            mapping[cc] = control
    return mapping


def save_filter_map(
    mapping: Dict[int, FilterControl], settings: Optional[QSettings] = None
) -> None:
    """
    Store ``mapping``, replacing whatever was there.

    :param mapping: dict CC number -> FilterControl
    :param settings: Optional[QSettings] store to write; defaults to the
        application's own
    :return: None
    """
    store = _settings() if settings is None else settings
    store.remove(MAPPING_GROUP)
    for cc, control in mapping.items():
        store.setValue(f"{MAPPING_GROUP}/{control.name}", int(cc))
    store.sync()
    log.message(
        f"Saved {len(mapping)} controller mappings", scope="controller_settings"
    )


def clear_filter_map(settings: Optional[QSettings] = None) -> None:
    """
    Forget the stored mapping, so the built-in one is used again.

    :param settings: Optional[QSettings] store to clear; defaults to the
        application's own
    :return: None
    """
    store = _settings() if settings is None else settings
    store.remove(MAPPING_GROUP)
    store.sync()


def _default_cc(control: FilterControl) -> Optional[int]:
    """
    The built-in CC number for ``control``.

    :param control: FilterControl
    :return: Optional[int]
    """
    return next((cc for cc, c in MINILAB3_FILTER_MAP.items() if c is control), None)


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
