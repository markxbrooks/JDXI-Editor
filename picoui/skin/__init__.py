"""
picoui.skin
Reusable skins for Qt applications: the look of a panel as an object.

- :class:`JDXiSkin` -- the base: margins, faceplate, ears, rail, screws
- :class:`LcdPalette`, :class:`Foreground`, :class:`Chassis` -- its colours
- :mod:`picoui.skin.textures` -- brushed metal, wood and moulded materials
- :class:`GradientStop`, :class:`GradientColorStops` -- gradients as plain
  data (RGBA tuples, no Qt), applied with :func:`apply_gradient_stops`
- :class:`FaceSpec`, :class:`EarSpec` and their materials and decorations
  (:mod:`picoui.skin.spec`) -- a faceplate and its cheeks as data, painted by
  :mod:`picoui.skin.render`
- :func:`load_skin_file` (:mod:`picoui.skin.loader`) -- a skin from a TOML
  file a user writes, with no code
- :class:`SkinRegistry` -- the skins offered, the active one, the saved
  choice, and listeners told when it changes
- :class:`RackPanel`, :class:`RackEars` -- widgets that wear a skin

An application subclasses :class:`JDXiSkin` for its looks, builds a registry
(with a :class:`QSettingsStore` to remember the choice), makes it the default
with :func:`set_default_registry`, and restyles itself in a listener.
"""

from picoui.skin.base import Skin
from picoui.skin.gradient import GradientColorStops, GradientStop, parse_color
from picoui.skin.qt import apply_gradient_stops
from picoui.skin.palette import (
    DARK_CHASSIS,
    DARK_LETTERING,
    DEFAULT_LCD,
    LIGHT_LETTERING,
    Chassis,
    Foreground,
    LcdPalette,
)
from picoui.skin.spec import (
    Band,
    BrushedFill,
    Frame,
    Grille,
    Keyboard,
    PatchCord,
    PebbleFill,
    RailSpec,
    SaggingCable,
    SolidFill,
    StepButtons,
    StepLights,
    Wash,
    EarSpec,
    FaceSpec,
    GradientBand,
    GradientFill,
    InsetRim,
    MaterialBand,
    Rule,
    WoodFill,
)
from picoui.skin.loader import SkinFileError, load_skin_file, skin_from_data
from picoui.skin.registry import (
    QSettingsStore,
    SkinRegistry,
    default_registry,
    set_default_registry,
)

__all__ = [
    "Skin",
    "GradientStop",
    "GradientColorStops",
    "apply_gradient_stops",
    "parse_color",
    "LcdPalette",
    "Foreground",
    "Chassis",
    "DARK_CHASSIS",
    "DARK_LETTERING",
    "DEFAULT_LCD",
    "LIGHT_LETTERING",
    "FaceSpec",
    "Frame",
    "Grille",
    "Keyboard",
    "PatchCord",
    "PebbleFill",
    "RailSpec",
    "SaggingCable",
    "SolidFill",
    "StepButtons",
    "StepLights",
    "Wash",
    "EarSpec",
    "GradientFill",
    "BrushedFill",
    "WoodFill",
    "Band",
    "GradientBand",
    "Rule",
    "InsetRim",
    "MaterialBand",
    "load_skin_file",
    "skin_from_data",
    "SkinFileError",
    "SkinRegistry",
    "QSettingsStore",
    "default_registry",
    "set_default_registry",
    "RackPanel",
    "RackEars",
]


def __getattr__(name):
    # The widgets need a QApplication's widget module; import them on use
    if name in ("RackPanel", "RackEars"):
        from picoui.skin import widgets

        return getattr(widgets, name)
    raise AttributeError(name)
