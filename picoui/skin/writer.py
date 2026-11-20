"""
picoui.skin.writer
A skin file's tables written back as TOML, for a skin editor to save.

This writes the subset a skin file uses: tables of strings, numbers, booleans,
arrays and inline tables, with a list of tables (a face's decorations) written
as ``[[face.decorations]]`` blocks so it reads as the hand-written examples
do. The tables come out in a skin file's usual order: ``[skin]`` first, then
colours, gradients, palettes and the look.

Example:
    >>> print(dumps({"skin": {"id": "mine", "ear_width": 14},
    ...              "face": {"rim": "#383B3E",
    ...                       "material": {"type": "gradient", "stops": "panel"}}}))
    [skin]
    id = "mine"
    ear_width = 14
    <BLANKLINE>
    [face]
    rim = "#383B3E"
    material = { type = "gradient", stops = "panel" }
    <BLANKLINE>
"""

from __future__ import annotations

import json
import math
import re
from typing import Any, List, Mapping

#: The order a skin file's tables are written in; any others follow
TABLE_ORDER = (
    "skin", "colors", "gradients", "lcd", "foreground", "chassis",
    "face", "ear", "rail", "lanes",
)

_BARE_KEY = re.compile(r"[A-Za-z0-9_-]+")


def _key(key: str) -> str:
    return key if _BARE_KEY.fullmatch(key) else json.dumps(key)


def _value(value: Any) -> str:
    """One value, inline."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            raise ValueError(f"TOML has no number for {value!r} in a skin file")
        return repr(value)
    if isinstance(value, str):
        # A TOML basic string takes JSON's escapes
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(_value(item) for item in value) + "]"
    if isinstance(value, Mapping):
        if not value:
            return "{}"
        return "{ " + ", ".join(f"{_key(k)} = {_value(v)}" for k, v in value.items()) + " }"
    raise TypeError(f"Cannot write {type(value).__name__} to a skin file: {value!r}")


def _is_table_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(v, Mapping) for v in value)


def _table(name: str, table: Mapping[str, Any], lines: List[str]) -> None:
    lines.append(f"[{name}]")
    later = []
    for key, value in table.items():
        if _is_table_list(value):
            later.append((key, value))  # after the plain keys, as blocks
        else:
            lines.append(f"{_key(key)} = {_value(value)}")
    lines.append("")
    for key, items in later:
        for item in items:
            lines.append(f"[[{name}.{_key(key)}]]")
            for k, v in item.items():
                lines.append(f"{_key(k)} = {_value(v)}")
            lines.append("")


def dumps(data: Mapping[str, Mapping[str, Any]]) -> str:
    """
    A skin file's tables as TOML text.

    :param data: the tables, as :func:`picoui.skin.loader.read_skin_file`
        returns them (each top-level value a table)
    :return: str
    """
    lines: List[str] = []
    names = [n for n in TABLE_ORDER if n in data] + [n for n in data if n not in TABLE_ORDER]
    for name in names:
        table = data[name]
        if not isinstance(table, Mapping):
            raise TypeError(f"[{name}] must be a table, not {type(table).__name__}")
        if table:
            _table(_key(name), table, lines)
    return "\n".join(lines)
