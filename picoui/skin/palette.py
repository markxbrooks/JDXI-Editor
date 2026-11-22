"""
picoui.skin.palette
The colours a skin hands to the rest of an application: its display, the
lettering printed on its faceplate, and the chassis the panels sit on.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LcdPalette:
    """
    Colours of a display, so it matches the faceplate around it.

    :param bg_edge: str darkest part of the screen, at its edges
    :param bg_mid: str screen between edge and glow
    :param bg_glow: str backlight in the middle of the screen
    :param text: str the characters
    :param text_dim: str secondary lines
    """

    bg_edge: str
    bg_mid: str
    bg_glow: str
    text: str
    text_dim: str


@dataclass(frozen=True)
class Foreground:
    """
    Lettering printed on the faceplate, and the rules drawn between it.

    The chassis and the controls are different surfaces: the silkscreen on a
    pale faceplate has to be dark, while the buttons and fields sitting in it
    keep their own dark surfaces and light text. Only the chassis is covered
    here, which is why a light skin does not simply invert the whole UI.

    :param text: str labels and group text on the faceplate
    :param text_secondary: str quieter labels on the faceplate
    :param rule: str hairlines drawn on the faceplate
    """

    text: str
    text_secondary: str
    rule: str


@dataclass(frozen=True)
class Chassis:
    """
    The body the panels are mounted on, and the control surfaces on it.

    The faceplate is only part of a skin: behind it is the instrument's body,
    and standing on it are the tabs, lists and fields. Those stay dark even
    on a pale skin -- they are the electronics, not the chassis -- so they
    are given here rather than derived from the faceplate.

    :param body: str the matte body behind the panels
    :param surface: str control surfaces (selected tab, lists, menus)
    :param surface_alt: str quieter control surfaces (unselected tabs)
    :param border: str outlines between them
    :param accent: str the skin's own accent, for the selected tab's underline
    """

    body: str
    surface: str
    surface_alt: str
    border: str
    accent: str


#: The JD-Xi's matte black body and the application's dark controls
DARK_CHASSIS = Chassis(
    body="#2C2C2C",
    surface="#202020",
    surface_alt="#292929",
    border="#383838",
    accent="#E04435",
)


#: What the dark skins use: the application's own colours
LIGHT_LETTERING = Foreground(
    text="#E6E6E6", text_secondary="#999999", rule="#3A3A3C"
)

#: Silkscreen on a pale faceplate. The secondary ink is dark enough to hold
#: up on the body as well as the panel, which is a shade deeper.
DARK_LETTERING = Foreground(
    text="#1E1E1C", text_secondary="#3A3935", rule="#7A7A77"
)

#: A neutral amber-on-black display, for skins that do not name their own
DEFAULT_LCD = LcdPalette(
    bg_edge="#120E08",
    bg_mid="#241A0C",
    bg_glow="#3A2810",
    text="#FFB545",
    text_dim="#B87A28",
)
