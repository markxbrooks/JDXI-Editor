"""
picoui.skin
Reusable skins for Qt applications: the look of a panel as an object.

- :class:`Skin` -- the base: margins, faceplate, ears, rail, screws
- :class:`LcdPalette`, :class:`Foreground`, :class:`Chassis` -- its colours
- :mod:`picoui.skin.textures` -- brushed metal, wood and moulded materials
- :class:`GradientStop`, :class:`GradientColorStops` -- gradients as data,
  applied with :func:`apply_gradient_stops`
- :class:`SkinRegistry` -- the skins offered, the active one, the saved
  choice, and listeners told when it changes
- :class:`RackPanel`, :class:`RackEars` -- widgets that wear a skin

An application subclasses :class:`Skin` for its looks, builds a registry
(with a :class:`QSettingsStore` to remember the choice), makes it the default
with :func:`set_default_registry`, and restyles itself in a listener.
"""

from picoui.skin.base import Skin
from picoui.skin.gradient import GradientColorStops, GradientStop, apply_gradient_stops
from picoui.skin.palette import (
    DARK_CHASSIS,
    DARK_LETTERING,
    DEFAULT_LCD,
    LIGHT_LETTERING,
    Chassis,
    Foreground,
    LcdPalette,
)
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
    "LcdPalette",
    "Foreground",
    "Chassis",
    "DARK_CHASSIS",
    "DARK_LETTERING",
    "DEFAULT_LCD",
    "LIGHT_LETTERING",
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
