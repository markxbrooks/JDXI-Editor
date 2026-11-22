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

import dataclasses
import json
import math
import re
from typing import Any, Dict, List, Mapping

from picoui.skin.gradient import GradientColorStops, parse_color
from picoui.skin.loader import COLOR_FIELDS, DECORATIONS, DETAILS, MATERIALS

#: Each spec class's ``type`` name in a file
_TYPE_NAMES = {cls: name for kinds in (MATERIALS, DECORATIONS, DETAILS) for name, cls in kinds.items()}

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


def color_value(rgba: Any) -> Any:
    """
    A colour as a file writes it: "#RRGGBB", or [r, g, b, a] when it is
    not opaque (a file refuses 8-digit hex).
    """
    rgba = parse_color(rgba)
    if rgba[3] == 255:
        return "#{:02X}{:02X}{:02X}".format(*rgba[:3])
    return list(rgba)


def _gradient_value(stops: GradientColorStops) -> list:
    return [[float(stop.position), color_value(stop.color)] for stop in stops.stops]


def _field_value(name: str, value: Any) -> Any:
    if isinstance(value, GradientColorStops):
        return _gradient_value(value)
    if name in ("material", "backing"):
        return spec_table(value)
    if name == "lights":
        return spec_table(value, typed=False)
    if name in ("decorations", "overlays", "details"):
        return [spec_table(item) for item in value]
    if name in COLOR_FIELDS:
        return color_value(value)
    if name == "colors":
        return [color_value(item) for item in value]
    if isinstance(value, tuple):
        return list(value)
    return value


def spec_table(spec: Any, typed: bool = True) -> Dict[str, Any]:
    """
    A spec as the table a skin file gives for it, the inverse of
    :class:`picoui.skin.loader.Resolver`: its ``type`` (for a material,
    decoration or detail) and every field that differs from its default.

    >>> from picoui.skin.spec import Rule
    >>> spec_table(Rule("top", 2.5, "#E64A32"))
    {'type': 'rule', 'edge': 'top', 'offset': 2.5, 'color': '#E64A32'}

    :param spec: a spec from :mod:`picoui.skin.spec`
    :param typed: False for a nested table without a ``type`` (step lights)
    :return: dict
    """
    table: Dict[str, Any] = {}
    if typed:
        name = _TYPE_NAMES.get(type(spec))
        if name is None:
            raise TypeError(f"A skin file has no type for {type(spec).__name__}")
        table["type"] = name
    for field in dataclasses.fields(spec):
        value = getattr(spec, field.name)
        has_default = field.default is not dataclasses.MISSING
        if (has_default and value == field.default) or value is None:
            continue  # TOML has no None, and a default needs no writing
        table[field.name] = _field_value(field.name, value)
    return table


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
