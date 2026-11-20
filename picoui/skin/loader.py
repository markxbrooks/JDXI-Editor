"""
picoui.skin.loader
A skin from a TOML file.

A skin's look is plain data (:mod:`picoui.skin.spec`), so a user can write
one without code. The file mirrors the specs: a table per part, with a
``type`` naming each material, decoration or detail. Colours are "#RRGGBB"
or ``[r, g, b]`` / ``[r, g, b, a]``; "$name" uses a colour from
``[colors]``, and a gradient is named from ``[gradients]`` (or picoui's own:
"aluminium", "gunmetal", "walnut", "teak") or written inline as
``[[position, colour], ...]``.

Example file::

    [skin]
    id = "my_tr1000"
    label = "My TR-1000"
    ear_width = 14

    [colors]
    accent = "#E64A32"
    cheek_light = "#35383B"

    [gradients]
    panel = [[0.0, "#777A7D"], [0.5, "#66696C"], [1.0, "#55585B"]]
    cheek = [[0.0, "$cheek_light"], [1.0, "#25282B"]]

    [lcd]
    bg_edge = "#0F1011"
    bg_mid = "#1B1D1F"
    bg_glow = "#2A2D30"
    text = "#F0EEE8"
    text_dim = "#9A9893"

    [foreground]
    text = "#F0EEE8"
    text_secondary = "#CFCDC7"
    rule = "#484B4E"

    [chassis]
    body = "#626568"
    surface = "#25282B"
    surface_alt = "#303336"
    border = "#484B4E"
    accent = "$accent"

    [face]
    material = { type = "gradient", stops = "panel" }
    rim = "#383B3E"

    [[face.decorations]]
    type = "rule"
    edge = "top"
    offset = 2.5
    color = "$accent"

    [[face.decorations]]
    type = "step_buttons"
    thickness = 6
    count = 16
    colors = ["#E6E3DB"]
    background = "$cheek_light"
    group = 4
    gap = 0.8
    group_gap = 1.6
    button_top = 2
    lights = { height = 2, on = "#F04430", off = "#351914" }

    [ear]
    material = { type = "gradient", stops = "cheek", direction = "horizontal" }
    rim = "#1D2022"
    screw = "#8B8E90"

A palette table may give only some of its colours; the rest are the base
skin class's. A file can instead start from a skin already offered: with
``based_on = "tr909"`` under ``[skin]`` only what the file gives changes,
field by field (``[chassis] accent = ...`` alone recolours the accent, and a
``[face]`` with only ``rim`` keeps the rest of that face).

This module needs no Qt until the skin object itself is made.
"""

from __future__ import annotations

import dataclasses
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Union

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover - Python 3.10
    import tomli as tomllib  # type: ignore[no-redef]

from picoui.skin import spec as specs
from picoui.skin.gradient import GradientColorStops, GradientStop, parse_color
from picoui.skin.palette import Chassis, Foreground, LcdPalette
from picoui.skin.textures import ALUMINIUM, GUNMETAL, TEAK, WALNUT

#: The gradients a file can name without defining
BUILTIN_GRADIENTS: Dict[str, GradientColorStops] = {
    "aluminium": ALUMINIUM,
    "gunmetal": GUNMETAL,
    "walnut": WALNUT,
    "teak": TEAK,
}

#: ``type`` names, and the spec each makes
MATERIALS = {
    "gradient": specs.GradientFill,
    "brushed": specs.BrushedFill,
    "wood": specs.WoodFill,
    "solid": specs.SolidFill,
    "pebble": specs.PebbleFill,
}
DECORATIONS = {
    "band": specs.Band,
    "gradient_band": specs.GradientBand,
    "material_band": specs.MaterialBand,
    "rule": specs.Rule,
    "inset_rim": specs.InsetRim,
    "frame": specs.Frame,
    "wash": specs.Wash,
    "keyboard": specs.Keyboard,
    "step_buttons": specs.StepButtons,
}
DETAILS = {
    "patch_cord": specs.PatchCord,
    "grille": specs.Grille,
    "sagging_cable": specs.SaggingCable,
}

#: Spec fields that hold one colour
COLOR_FIELDS = {
    "color", "rim", "wash", "seam", "screw", "line", "ivory", "black",
    "divider", "background", "on", "off", "plate", "holes",
}

#: The tables that make the skin's palettes
PALETTES = {"lcd": LcdPalette, "foreground": Foreground, "chassis": Chassis}

#: The tables that make its look, and the spec each makes
PARTS = {"face": specs.FaceSpec, "ear": specs.EarSpec, "rail": specs.RailSpec}

#: Turns a ``[skin]`` value into the attribute it sets
Converter = Callable[[Any], Any]
#: Turns a whole extra table into the attribute it sets
SectionConverter = Callable[[Mapping[str, Any], "Resolver"], Any]


class SkinFileError(ValueError):
    """A skin file that cannot be read, saying where in it the fault is."""


class Resolver:
    """
    Turns a file's values into spec values: colours (and "$name"
    references), gradients by name or inline, materials, decorations and
    details.

    :param colors: the file's ``[colors]``
    :param gradients: gradients a file may name, its own included
    """

    def __init__(self, colors: Mapping[str, Any], gradients: Mapping[str, GradientColorStops]):
        self.colors: Dict[str, Any] = {}
        for name, value in colors.items():
            self.colors[name] = self.color(value, f"colors.{name}")
        self.gradients = dict(gradients)

    # --- Values -------------------------------------------------------------

    def color(self, value: Any, where: str):
        """A colour: "#RRGGBB", [r, g, b(, a)] or "$name"."""
        if isinstance(value, str) and value.startswith("$"):
            name = value[1:]
            if name not in self.colors:
                raise SkinFileError(f"{where}: no colour {value!r} in [colors]")
            return self.colors[name]
        if isinstance(value, list):
            value = tuple(value)
        try:
            return parse_color(value)
        except ValueError as error:
            raise SkinFileError(f"{where}: {error}") from None

    def gradient(self, value: Any, where: str) -> GradientColorStops:
        """A gradient: a name, or [[position, colour], ...]."""
        if isinstance(value, str):
            if value not in self.gradients:
                known = ", ".join(sorted(self.gradients)) or "none"
                raise SkinFileError(f"{where}: no gradient {value!r}; known: {known}")
            return self.gradients[value]
        if not isinstance(value, list):
            raise SkinFileError(f"{where}: a gradient is a name or [[position, colour], ...]")
        stops = []
        for index, stop in enumerate(value):
            if not (isinstance(stop, list) and len(stop) == 2):
                raise SkinFileError(f"{where}[{index}]: a stop is [position, colour]")
            position, colour = stop
            try:
                stops.append(GradientStop(position, self.color(colour, f"{where}[{index}]")))
            except ValueError as error:
                raise SkinFileError(f"{where}[{index}]: {error}") from None
        try:
            return GradientColorStops(tuple(stops))
        except ValueError as error:
            raise SkinFileError(f"{where}: {error}") from None

    def typed(self, table: Any, kinds: Mapping[str, type], where: str):
        """A spec chosen by the table's ``type``, from its other keys."""
        if not isinstance(table, dict):
            raise SkinFileError(f"{where}: expected a table with a 'type'")
        kind = table.get("type")
        if kind not in kinds:
            raise SkinFileError(
                f"{where}: type {kind!r} is not one of {', '.join(sorted(kinds))}"
            )
        fields = {key: value for key, value in table.items() if key != "type"}
        return self.build(kinds[kind], fields, where)

    def material(self, table: Any, where: str):
        return self.typed(table, MATERIALS, where)

    # --- Specs --------------------------------------------------------------

    def field(self, name: str, value: Any, where: str) -> Any:
        """One field's value, converted by what the field holds."""
        here = f"{where}.{name}"
        if name in ("material", "backing"):
            return self.material(value, here)
        if name == "stops":
            return self.gradient(value, here)
        if name == "lights":
            return self.build(specs.StepLights, value, here)
        if name in ("decorations", "overlays"):
            return tuple(self.typed(item, DECORATIONS, f"{here}[{i}]") for i, item in enumerate(_list(value, here)))
        if name == "details":
            return tuple(self.typed(item, DETAILS, f"{here}[{i}]") for i, item in enumerate(_list(value, here)))
        if name in COLOR_FIELDS:
            return self.color(value, here)
        if name == "colors":
            return tuple(self.color(item, f"{here}[{i}]") for i, item in enumerate(_list(value, here)))
        if isinstance(value, list):
            return tuple(value)
        return value

    def fields(self, cls: type, table: Any, where: str) -> Dict[str, Any]:
        """A table's keys as ``cls``'s fields, each converted."""
        if not isinstance(table, dict):
            raise SkinFileError(f"{where}: expected a table")
        names = {f.name for f in dataclasses.fields(cls)}
        unknown = sorted(set(table) - names)
        if unknown:
            raise SkinFileError(
                f"{where}: unknown {', '.join(unknown)}; {cls.__name__} takes "
                f"{', '.join(sorted(names))}"
            )
        return {key: self.field(key, value, where) for key, value in table.items()}

    def build(self, cls: type, table: Any, where: str, base: Any = None):
        """
        A ``cls`` from a table; given ``base``, that one with the table's
        fields replaced.
        """
        values = self.fields(cls, table, where)
        try:
            if base is not None:
                return dataclasses.replace(base, **values)
            return cls(**values)
        except (TypeError, ValueError) as error:
            raise SkinFileError(f"{where}: {error}") from None


def _list(value: Any, where: str) -> list:
    if not isinstance(value, list):
        raise SkinFileError(f"{where}: expected a list")
    return value


def read_skin_file(path: Union[str, Path]) -> Dict[str, Any]:
    """
    The tables of a skin file.

    :param path: the .toml file
    :return: dict
    :raises SkinFileError: if it is not TOML
    """
    path = Path(path)
    try:
        with path.open("rb") as handle:
            return tomllib.load(handle)
    except tomllib.TOMLDecodeError as error:
        raise SkinFileError(f"{path.name}: not valid TOML: {error}") from None
    except OSError as error:
        raise SkinFileError(f"{path.name}: {error.strerror or error}") from None


def skin_from_data(
    data: Mapping[str, Any],
    base: Optional[type] = None,
    *,
    bases: Optional[Mapping[str, Any]] = None,
    gradients: Optional[Mapping[str, GradientColorStops]] = None,
    attributes: Optional[Mapping[str, Converter]] = None,
    sections: Optional[Mapping[str, SectionConverter]] = None,
):
    """
    A skin from a skin file's tables.

    :param data: the tables, as :func:`read_skin_file` returns them
    :param base: the Skin class a new skin extends; picoui's Skin if None
    :param bases: skins a file may start from with ``based_on``, by id
    :param gradients: gradients a file may name, beyond picoui's own
    :param attributes: ``[skin]`` keys the application adds, each with the
        function that turns the file's value into the attribute
    :param sections: extra tables the application adds, each with the
        function that turns the table into the attribute of that name
    :return: an instance of a new subclass of ``base`` (or of the class of
        the skin it is based on)
    :raises SkinFileError: saying where the fault is
    """
    attributes = dict(attributes or {})
    sections = dict(sections or {})
    known = {"skin", "colors", "gradients", *PALETTES, *PARTS, *sections}
    unknown = sorted(set(data) - known)
    if unknown:
        raise SkinFileError(f"unknown table {', '.join(unknown)}; a skin file has {', '.join(sorted(known))}")

    head = dict(data.get("skin") or {})
    skin_id = head.pop("id", None)
    if not isinstance(skin_id, str) or not skin_id.strip():
        raise SkinFileError("skin.id: every skin needs an id, such as id = \"my_skin\"")
    label = head.pop("label", skin_id)

    template = None
    based_on = head.pop("based_on", None)
    if based_on is not None:
        if not bases or based_on not in bases:
            offered = ", ".join(sorted(bases or {})) or "none"
            raise SkinFileError(f"skin.based_on: no skin {based_on!r}; offered: {offered}")
        template = bases[based_on]
        cls = type(template)
    else:
        if base is None:
            from picoui.skin.base import Skin  # Qt is needed only from here

            base = Skin
        cls = base

    # The file's own gradients may use its colours, and each other's names
    resolver = Resolver(data.get("colors") or {}, {**BUILTIN_GRADIENTS, **(gradients or {})})
    for name, value in (data.get("gradients") or {}).items():
        resolver.gradients[name] = resolver.gradient(value, f"gradients.{name}")

    # Simple settings go on the new class, where the skin's own __init__
    # sees them (the SH-101 builds its look from body_color there); specs and
    # palettes go on the instance afterwards
    settings: Dict[str, Any] = {}
    values: Dict[str, Any] = {}
    for key, value in head.items():
        where = f"skin.{key}"
        if key in attributes:
            try:
                values[key] = attributes[key](value)
            except (TypeError, ValueError) as error:
                raise SkinFileError(f"{where}: {error}") from None
            continue
        current = getattr(template if template is not None else cls, key, None)
        if key.startswith("_") or current is None or not isinstance(current, (bool, int, float, str)):
            raise SkinFileError(f"{where}: not a setting a skin file can change")
        expected = type(current)
        if expected is float and isinstance(value, int) and not isinstance(value, bool):
            value = float(value)
        if type(value) is not expected:
            raise SkinFileError(f"{where}: expected {expected.__name__}, not {value!r}")
        settings[key] = value

    for name, palette in PALETTES.items():
        if name in data:
            current = getattr(template if template is not None else cls, name, None)
            table = {key: _hex(resolver.color(value, f"{name}.{key}")) for key, value in _table(data[name], name).items()}
            # Fields left out keep the skin's own (the base class's, or the
            # skin it is based on), so one colour can be changed alone
            values[name] = resolver.build(palette, table, name, base=current)

    for name, part in PARTS.items():
        if name in data:
            current = getattr(template, name, None) if template is not None else None
            values[name] = resolver.build(part, data[name], name, base=current)

    for name, convert in sections.items():
        if name in data:
            try:
                values[name] = convert(_table(data[name], name), resolver)
            except SkinFileError:
                raise
            except (TypeError, ValueError) as error:
                raise SkinFileError(f"{name}: {error}") from None

    # A subclass names the skin; the file's values are set on the instance,
    # after the class's own __init__ (some skins build their look there)
    skin_class = type(
        f"FileSkin_{_identifier(skin_id)}",
        (cls,),
        {"skin_id": skin_id, "label": label, **settings},
    )
    try:
        skin = skin_class()
    except (TypeError, ValueError) as error:
        raise SkinFileError(f"skin: {error}") from None
    for key, value in values.items():
        setattr(skin, key, value)
    return skin


def load_skin_file(path: Union[str, Path], base: Optional[type] = None, **options):
    """
    A skin from a TOML file; see :func:`skin_from_data` for the options.

    :param path: the .toml file
    :param base: the Skin class a new skin extends
    :raises SkinFileError: naming the file and where in it the fault is
    """
    path = Path(path)
    data = read_skin_file(path)
    try:
        return skin_from_data(data, base, **options)
    except SkinFileError as error:
        raise SkinFileError(f"{path.name}: {error}") from None


def _table(value: Any, where: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise SkinFileError(f"{where}: expected a table")
    return value


def _hex(rgba) -> str:
    """Palettes hold "#RRGGBB" text, as stylesheets take it."""
    return "#{:02X}{:02X}{:02X}".format(*rgba[:3])


def _identifier(text: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in text)
