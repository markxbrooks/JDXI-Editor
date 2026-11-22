"""
Rack skins
==========

The look of a panel, as an object: the faceplate painted behind the content,
any rack ears beside it, and the palette its display picks up.

A skin owns chrome only, never layout. The room it is allowed to take is the
three numbers it declares -- :attr:`JDXiSkin.ear_width`, :attr:`JDXiSkin.bezel`
and :attr:`JDXiSkin.rail_height` -- which
:meth:`JDXiSkin.content_margins` turns into the margins
:class:`~jdxi_editor.ui.widgets.rack.panel.RackPanel` sets on its layout.
Everything left over belongs to the content, so a skin cannot quietly grow.

The default skin is the JD-Xi's shiny black panel exactly as it was before
skins existed, so wrapping something in a RackPanel changes nothing until
another skin is chosen.

A skin drives three things:

- the chrome a :class:`RackPanel` paints,
- the panel image behind an editor's outermost groups (``mark_sheen``, which
  reaches them as a stylesheet ``border-image``: see
  :func:`jdxi_editor.ui.style.editor_style.gloss_panel_file`),
- the colours of the LCD widgets, so a brushed aluminium faceplate is not left
  with a Roland-orange display.

The reusable part -- the :class:`~picoui.skin.JDXiSkin` base, its palettes and
textures, the :class:`~picoui.skin.SkinRegistry` and the RackPanel / RackEars
widgets -- lives in :mod:`picoui.skin`. This module holds the editor's own
skins, its :data:`REGISTRY` of them, and the restyling the editor needs when
the skin changes (the registry's listener).

Adding one means subclassing :class:`JDXiSkin`, declaring those three numbers
and its look -- a :class:`~picoui.skin.spec.FaceSpec` as ``face`` and an
:class:`~picoui.skin.spec.EarSpec` as ``ear`` -- then adding it to
:data:`REGISTRY`. The machine details are specs too (the TB-303's keyboard,
the TR-909's steps, the MS-20's patch cords), so any skin can borrow one. A
paint hook is overridden only for what no spec describes yet: the Minimoog's
rail is the one left.

The choice is remembered in QSettings under ``ui/skin``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Optional

from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor, QPainter, QPen

from picoui.skin import (  # noqa: F401  re-exported: the editor imports them from here
    DARK_CHASSIS,
    DARK_LETTERING,
    LIGHT_LETTERING,
    Chassis,
    Foreground,
    LcdPalette,
    QSettingsStore,
    Skin,
    SkinRegistry,
    set_default_registry,
)
from picoui.skin.spec import (  # noqa: F401
    Material,
    Band,
    BrushedFill,
    EarSpec,
    FaceSpec,
    Frame,
    GradientBand,
    GradientFill,
    Grille,
    InsetRim,
    Keyboard,
    MaterialBand,
    PatchCord,
    PebbleFill,
    RailSpec,
    Rule,
    SaggingCable,
    SolidFill,
    StepButtons,
    StepLights,
    Wash,
    WoodFill,
)
from picoui.skin.gradient import GradientColorStops, GradientStop
from picoui.skin.qt import rgba
from picoui.skin.textures import (  # noqa: F401
    ALUMINIUM,
    GRAIN_SATIN,
    GUNMETAL,
    TEAK,
    WALNUT,
    brushed_tile as _brushed_tile,
    pebble_tile as _pebble_tile,
    wood_tile as _wood_tile,
)


#: QSettings key holding the chosen skin's id
SKIN_SETTING = "ui/skin"

#: The editor's illuminated red (AppEditorStyle.ACCENT): the accent of the
#: skins whose machines have no colour of their own to lend
EDITOR_ACCENT = "#E04435"


#: The JD-Xi's orange-on-dark-red display
ROLAND_LCD = LcdPalette(
    bg_edge="#1A0A0A",
    bg_mid="#331111",
    bg_glow="#551100",
    text="#FF6A00",
    text_dim="#CC5500",
)

#: The blue backlit screen of the rackmount unit
JDXV_BLUE_LCD = LcdPalette(
    bg_edge="#07234F",
    bg_mid="#0E3C86",
    bg_glow="#1557BF",
    text="#CFEEFF",
    text_dim="#7FB4E6",
)

#: Warm amber on near-black, as on painted studio gear
AMBER_LCD = LcdPalette(
    bg_edge="#120E08",
    bg_mid="#241A0C",
    bg_glow="#3A2810",
    text="#FFB545",
    text_dim="#B87A28",
)

#: The red LEDs of a TR-808's step buttons
LED_RED_LCD = LcdPalette(
    bg_edge="#120807",
    bg_mid="#2A100C",
    bg_glow="#431711",
    text="#FF4A33",
    text_dim="#B3301F",
)

#: The TB-303's red LED numerals, harder and purer than the 808's
LED_303_LCD = LcdPalette(
    bg_edge="#140604",
    bg_mid="#2A0A06",
    bg_glow="#49100A",
    text="#FF1F10",
    text_dim="#A81608",
)

#: The TR-909's red LED display, in its dark neutral bezel
LED_909_LCD = LcdPalette(
    bg_edge="#0E0D0D",
    bg_mid="#241513",
    bg_glow="#3E1A15",
    text="#FF3A20",
    text_dim="#AD2412",
)

#: The Jupiter-8's patch number display
LED_JP8_LCD = LcdPalette(
    bg_edge="#100706",
    bg_mid="#270C08",
    bg_glow="#43130D",
    text="#FF2A14",
    text_dim="#A81B0C",
)

#: A green fluorescent display, as 1970s rack gear had
VINTAGE_GREEN_LCD = LcdPalette(
    bg_edge="#07140C",
    bg_mid="#0C2415",
    bg_glow="#12361F",
    text="#5BFF9B",
    text_dim="#2E9960",
)

#: The Juno-106 has no screen of its own; the editor's display takes the
#: cool grey-blue of the panel rather than another machine's orange or red
JUNO_LCD = LcdPalette(
    bg_edge="#101418",
    bg_mid="#1A222C",
    bg_glow="#243448",
    text="#C5D8EA",
    text_dim="#7A94AE",
)


class MeterStyle(str, Enum):
    """
    How the Audio Monitor draws its level meters. Any skin can take any of
    them: the meter belongs to the skin's era, not to its material.
    """

    #: Two horizontal bars on one dB scale
    BARS = "bars"
    #: Circular dials with needles
    NEEDLES = "needles"
    #: A pair of backlit analogue VU meters: cream faces, a needle and a red
    #: zone, as studio gear of the 1970s had (see analog_vu)
    VINTAGE_VU = "vintage_vu"


@dataclass(frozen=True)
class LaneStyle:
    """
    How the MIDI player draws its track lanes.

    :param cards: bool each lane drawn as a punched card
    :param backing: Material the cards lie on, filling the lane list behind
        them: the cabinet's wood, or the faceplate's metal
    """

    cards: bool = False
    backing: Material = WoodFill(WALNUT)


#: Plain lanes, as the editor draws them without a skin
PLAIN_LANES = LaneStyle()


class JDXiSkin(Skin):
    """
    The JD-Xi's shiny black panel, and the base every editor skin extends.

    The painting, margins and palette machinery are picoui's
    :class:`~picoui.skin.JDXiSkin`; what is added here is the JD-Xi's own display
    and the editor's features a skin chooses: its :attr:`meter` style on the
    Audio Monitor and its :attr:`lanes` in the MIDI player.
    """

    skin_id = "glossy_black"
    label = "JD-Xi Black"
    lcd = ROLAND_LCD
    #: The Audio Monitor's meters
    meter = MeterStyle.BARS
    #: The MIDI player's lanes
    lanes = PLAIN_LANES

#: The JDXV's lit chamfer, from the top edge down
JDXV_CHAMFER = GradientColorStops(
    (
        GradientStop(0.0, (126, 132, 140)),
        GradientStop(1.0, (74, 78, 85)),
    )
)


class JdxiRackSkin(JDXiSkin):
    """
    The JD-Xi as a 1U rack unit, after the JDXV: brushed gunmetal rather than
    the shiny black plastic, a lit chamfer along the top, a red stripe along
    the bottom, and a blue backlit screen.

    The chamfer and the stripe are painted as part of the face rather than as
    chrome around it. That costs no room -- both sit in the bezel the content
    already leaves free -- and, more importantly, it is what makes the skin
    recognisable: the faceplate reaches an editor's groups as a nine-slice
    image whose top and bottom edges are drawn unstretched, so anything in
    them appears on every panel in the application. The ears are not part of
    that image -- a nine-slice would stretch them -- so a RackPanel or a
    RackEars strip draws them itself.
    """

    skin_id = "jdxi_rack"
    label = "JD-Xi Rackmount"
    ear_width = 16
    bezel = 6
    rail_height = 0
    lcd = JDXV_BLUE_LCD
    #: the illuminated red of the stripe (AppEditorStyle.ACCENT)
    rail_color = EDITOR_ACCENT
    chassis = Chassis(
        body="#2A2C30", surface="#202225", surface_alt="#292C30",
        border="#3A3D42", accent=rail_color,
    )
    #: thickness of that stripe, within the nine-slice bottom edge
    #: (editor_style.SHEEN_SLICE_BOTTOM), leaving room for the rim below it
    rail_thickness = 4
    face = FaceSpec(
        # Brushed gunmetal, not the glossy black of the default skin
        material=BrushedFill(GUNMETAL, grain=10),
        decorations=(
            # The chamfer along the top, catching the light, and its shadow
            GradientBand("top", 2, JDXV_CHAMFER, span=3),
            Rule("top", 2.5, (0, 0, 0, 90), inset=0),
            # The red stripe, just inside the bottom edge
            Band("bottom", rail_thickness, (rail_color,)),
        ),
        rim=(12, 13, 15),
        radius=3,
    )
    #: A rack ear: the same metal, darker than the face and parted from it
    #: by a seam, with its mounting screws
    ear = EarSpec(
        BrushedFill(GUNMETAL, grain=7),
        wash=(0, 0, 0, 60),
        seam=(0, 0, 0, 170),
        screw=(118, 124, 132),
        screw_inset=11,
    )


#: The satin aluminium's shades, by role: the faceplate's highlight, base
#: and shadow (the stops of picoui's ALUMINIUM), and the darker metal of the
#: chassis and the cheeks' outer edge
SATIN_HIGHLIGHT = "#C5C5C1"
SATIN_BASE = "#A6A6A3"
SATIN_SHADOW = "#777875"
SATIN_DARK = "#8A8A87"

#: The brushed-aluminium cheeks, shading across from their outer edge
BRUSHED_70S_COLOR_STOPS = GradientColorStops(
    stops=(
        GradientStop(0.0, SATIN_DARK),
        GradientStop(1.0, SATIN_BASE),
    )
)


class Brushed70sSkin(JDXiSkin):
    """
    Satin-finished aluminium with a green display, as 1970s rack gear had.

    The panel is a bevel: lit along its top edge, shadowed along its bottom,
    with the grain kept faint enough that the metal reads by its gradient
    rather than by its texture. Legends are ink, and red is reserved for lamps.
    """

    skin_id = "brushed_70s"
    label = "Brushed Metal (70s)"
    ear_width = 18
    bezel = 6
    rail_height = 0
    lcd = VINTAGE_GREEN_LCD
    # Near-white lettering on satin aluminium is 1.96:1, well under the 4.5:1
    # that body text needs: this faceplate has to be written on in ink
    foreground = DARK_LETTERING
    ink_legends = True
    mounted_controls = True
    #: Backlit analogue VU meters, as 1970s studio gear had
    meter = MeterStyle.VINTAGE_VU
    #: The cards lie on the same satin aluminium as the faceplate, not wood
    lanes = LaneStyle(cards=True, backing=BrushedFill(ALUMINIUM, grain=4, coverage=0.35))
    chassis = Chassis(
        body=SATIN_DARK, surface="#101010", surface_alt="#191919",
        border="#4A4A47", accent=EDITOR_ACCENT,
    )
    #: the chassis, for anything wanting to match it
    base_color = SATIN_BASE
    highlight_color = SATIN_HIGHLIGHT
    shadow_color = SATIN_SHADOW
    face = FaceSpec(
        # Grain about 70% quieter than GRAIN_SATIN, and only on some rows,
        # so the brushing shows up close and the gradient carries the metal.
        material=BrushedFill(ALUMINIUM, grain=4, coverage=0.35),
        # A lip with some thickness: the light catches the top edge and
        # leaves the bottom in shadow. Two pixels, so it survives inside
        # the unstretched rim of the panel image.
        decorations=(
            Rule("top", 1, (230, 230, 226), width=2),
            Rule("top", 3.5, (242, 242, 238, 150), width=2),
            Rule("bottom", 2, shadow_color, width=2),
            Rule("bottom", 4.5, (90, 91, 88, 170), width=2),
        ),
        rim=shadow_color,
    )
    ear = EarSpec(
        GradientFill(BRUSHED_70S_COLOR_STOPS, direction="horizontal"),
        rim=shadow_color,
        screw=highlight_color,
        screw_radius=4.5,
    )


#: The Juno-106's end cheeks: a redder, sunlit mahogany than the walnut above
JUNO_WOOD = GradientColorStops(
    (
        GradientStop(0.0, (176, 102, 52)),
        GradientStop(0.45, (146, 78, 38)),
        GradientStop(1.0, (102, 50, 24)),
    )
)


#: Ivory painted steel, top to bottom
IVORY_PAINT = GradientColorStops(
    (
        GradientStop(0.0, (243, 238, 227)),
        GradientStop(0.45, (232, 225, 210)),
        GradientStop(1.0, (208, 199, 181)),
    )
)


class IvoryWalnutSkin(JDXiSkin):
    """
    Ivory painted steel with walnut end cheeks, as on 1970s studio gear.

    The one pale faceplate in the set, which is why :class:`Foreground`
    exists: its lettering is ink rather than near-white, while the controls
    standing on it keep their dark surfaces.
    """

    skin_id = "ivory_walnut"
    label = "Ivory & Walnut"
    ear_width = 18
    bezel = 6
    rail_height = 0
    lcd = AMBER_LCD
    foreground = Foreground(
        text="#22201C", text_secondary="#5F584C", rule="#B9AE99"
    )
    #: the walnut pinstripe along the bottom, this skin's signature
    stripe_color = "#684022"
    chassis = Chassis(
        body="#CFC7B6", surface="#241F18", surface_alt="#2F2920",
        border="#5A5043", accent=stripe_color,
    )
    stripe_thickness = 2
    #: where the panel's top edge catches the light
    highlight_color = (255, 253, 248)
    face = FaceSpec(
        material=GradientFill(IVORY_PAINT),
        decorations=(
            Rule("top", 0.5, highlight_color),
            Rule("bottom", 3.5, (168, 158, 140)),
            Band("bottom", stripe_thickness, (stripe_color,)),
        ),
        rim=(150, 140, 122),
    )
    #: A walnut end cheek rather than a rack ear
    ear = EarSpec(WoodFill(WALNUT), rim=(48, 28, 14), screw=(196, 186, 168))

#: The TR-808's matte charcoal, top to bottom
TR808_CHARCOAL = GradientColorStops(
    (
        GradientStop(0.0, (52, 53, 56)),
        GradientStop(0.5, (42, 43, 45)),
        GradientStop(1.0, (33, 34, 36)),
    )
)


class Tr808Skin(JDXiSkin):
    """
    The TR-808: matte charcoal, orange silkscreen, teak cheeks, and the
    step-button run of red, orange, yellow and white along the bottom.

    That run of colour is the machine, so it goes in the face rather than in
    chrome around it: the bottom edge of the nine-slice is drawn on every
    panel in the application, where ears and rails never appear.
    """

    skin_id = "tr808"
    label = "TR-808"
    ear_width = 14
    bezel = 6
    rail_height = 0
    lcd = LED_RED_LCD
    foreground = Foreground(
        text="#E8E4DA", text_secondary="#A09A8E", rule="#4A4B4D"
    )
    #: the Roland orange of the lettering and the rule under it
    accent_color = "#E8622A"
    chassis = Chassis(
        body="#232426", surface="#1C1D1F", surface_alt="#27282B",
        border="#3A3B3E", accent=accent_color,
    )
    #: the four step-button colours, left to right
    step_colors = ("#E33B2E", "#EE7B2C", "#EFC93F", "#EDE9DC")
    step_band = 4
    face = FaceSpec(
        # Matte charcoal, cooler and flatter than the glossy panel
        material=GradientFill(TR808_CHARCOAL),
        decorations=(
            # The orange rule printed under the machine's name
            Rule("top", 0.5, (70, 71, 74)),
            Rule("top", 2.5, accent_color),
            # The step buttons, in their four colours across the bottom
            Band("bottom", step_band, step_colors),
        ),
        rim=(16, 17, 18),
    )
    #: A teak side panel, as the 808 has
    ear = EarSpec(WoodFill(TEAK), rim=(30, 18, 9))

#: The TB-303's painted cheeks, across from their outer edge
TB303_CHEEK = GradientColorStops(
    (
        GradientStop(0.0, (126, 132, 130)),
        GradientStop(1.0, (152, 158, 156)),
    )
)


class Tb303Skin(JDXiSkin):
    """
    The TB-303 Bass Line: the silver box, orange knob line, red LED numerals
    and the little keyboard of step buttons along the bottom.

    Its faceplate is flat painted metal rather than brushed, which is what
    separates it from the satin aluminium skin at a glance; the keyboard
    band separates it from everything else. Both live in the face, so they
    reach every panel rather than only a RackPanel.
    """

    skin_id = "tb303"
    label = "TB-303"
    ear_width = 14
    bezel = 6
    rail_height = 0
    lcd = LED_303_LCD
    foreground = Foreground(
        text="#1E1E1C", text_secondary="#35342F", rule="#6E7472"
    )
    #: the orange of the Bass Line knobs
    accent_color = "#E87328"
    chassis = Chassis(
        body="#8A8F8D", surface="#232524", surface_alt="#2E312F",
        border="#4A4E4C", accent=accent_color,
    )
    #: the step buttons' keyboard: ivory keys, black keys, and their shadow
    key_ivory = "#E6E3D8"
    key_black = "#1A1A1A"
    #: height of that keyboard, within the nine-slice bottom edge
    key_band = 5
    #: keyboards drawn across the source image, before it is stretched
    key_octaves = 4
    #: flat painted metal: a cool grey, no grain, top to bottom
    panel_stops = GradientColorStops(
        (
            GradientStop(0.0, (168, 173, 171)),
            GradientStop(0.45, (142, 148, 146)),
            GradientStop(1.0, (110, 116, 114)),
        )
    )
    #: where the panel's top edge catches the light
    highlight_color = (206, 210, 208)
    face = FaceSpec(
        material=GradientFill(panel_stops),
        decorations=(
            Rule("top", 0.5, highlight_color),
            # The orange line the knobs stand on
            Rule("top", 2.5, accent_color),
            # The step buttons, laid out as the keyboard they are
            Keyboard(key_band, key_octaves, key_ivory, key_black),
        ),
        rim=(74, 78, 77),
    )
    #: A painted metal cheek, matching the box
    ear = EarSpec(
        GradientFill(TB303_CHEEK, direction="horizontal"),
        rim=(72, 76, 75),
        screw=(182, 188, 186),
        screw_inset=11,
    )

#: The TR-909's light grey painted steel, top to bottom
TR909_STEEL = GradientColorStops(
    (
        GradientStop(0.0, (214, 214, 209)),
        GradientStop(0.45, (198, 198, 193)),
        GradientStop(1.0, (168, 168, 163)),
    )
)

#: Its dark moulded cheeks, across from their outer edge
TR909_CHEEK = GradientColorStops(
    (
        GradientStop(0.0, (62, 62, 60)),
        GradientStop(1.0, (44, 44, 42)),
    )
)


class Tr909Skin(JDXiSkin):
    """
    The TR-909: a light grey box with blue silkscreen, dark end cheeks, and
    the sixteen cream step buttons with a red LED over each one.

    That row of buttons and lights is the machine's face, so it goes in the
    faceplate's bottom edge and appears on every panel. The steps are drawn
    in fours, as they are grouped on the hardware.
    """

    skin_id = "tr909"
    label = "TR-909"
    ear_width = 14
    bezel = 6
    rail_height = 0
    lcd = LED_909_LCD
    foreground = Foreground(
        text="#1E1E1C", text_secondary="#35342F", rule="#9A9A95"
    )
    #: the blue of the 909's silkscreen groupings
    accent_color = "#2C6AB0"
    chassis = Chassis(
        body="#9A9A95", surface="#232423", surface_alt="#2E2F2E",
        border="#4C4D4B", accent=accent_color,
    )
    #: the step buttons, their lights, and the strip they sit in
    button_color = "#E8E6DC"
    led_color = "#FF3A20"
    led_off_color = "#3A1410"
    strip_color = "#4A4A47"
    #: height of the button row and of the lights above it
    button_band = 4
    led_band = 2
    #: sixteen steps, in four groups of four
    steps = 16
    steps_per_group = 4
    #: where the panel's top edge catches the light
    highlight_color = (238, 238, 234)
    face = FaceSpec(
        # Light grey painted steel, flat
        material=GradientFill(TR909_STEEL),
        decorations=(
            Rule("top", 0.5, highlight_color),
            # The blue rule the groups are printed against
            Rule("top", 2.5, accent_color),
            # The step buttons, each under its own light, with a wider gap
            # every four steps, as the hardware groups them; the light is
            # lit on the downbeat of each group
            StepButtons(
                button_band + led_band,
                steps,
                (button_color,),
                strip_color,
                group=steps_per_group,
                gap=0.8,
                group_gap=1.6,
                button_top=led_band,
                lights=StepLights(
                    led_band, led_color, led_off_color, every=steps_per_group
                ),
            ),
        ),
        rim=(104, 104, 100),
    )
    #: A dark moulded cheek, as the 909 has at each end
    ear = EarSpec(
        GradientFill(TR909_CHEEK, direction="horizontal"),
        rim=(22, 22, 21),
        screw=(128, 128, 124),
        screw_inset=11,
    )

#: The TR-1000's colours that more than one part shares. They are an
#: interpretation of the machine, not sampled from the hardware.
#: The warm white of its lettering, which its display takes too
TR1000_LETTERING = "#F0EEE8"
#: The red of its top rule and of the chassis accent
TR1000_ACCENT = "#E64A32"
#: The rule between sections, and the chassis border
TR1000_RULE = "#484B4E"
#: The dark cheeks, lit edge and shadowed edge; the lit one is also the
#: strip behind the step buttons, the deep one the chassis surface
TR1000_CHEEK_LIGHT = "#35383B"
TR1000_CHEEK_DEEP = "#25282B"

#: The TR-1000's display: its lettering on charcoal
TR1000_LCD = LcdPalette(
    bg_edge="#0F1011",
    bg_mid="#1B1D1F",
    bg_glow="#2A2D30",
    text=TR1000_LETTERING,
    text_dim="#9A9893",
)

#: The TR-1000's grey panel, top to bottom
TR1000_PANEL = GradientColorStops(
    (
        GradientStop(0.0, "#777A7D"),
        GradientStop(0.5, "#66696C"),
        GradientStop(1.0, "#55585B"),
    )
)

#: Its dark cheeks, across from their outer edge
TR1000_CHEEK = GradientColorStops(
    (
        GradientStop(0.0, TR1000_CHEEK_LIGHT),
        GradientStop(1.0, TR1000_CHEEK_DEEP),
    )
)


class Tr1000Skin(JDXiSkin):
    """
    The TR-1000: a modern rhythm machine in mid grey, with dark cheeks, a
    red rule and the sixteen step buttons with a light over each one.

    Declared entirely from specs, with no paint method: the test that a new
    skin needs configuration rather than drawing code.
    """

    skin_id = "tr1000"
    label = "TR-1000"
    ear_width = 14
    bezel = 6
    rail_height = 0
    lcd = TR1000_LCD
    foreground = Foreground(
        text=TR1000_LETTERING, text_secondary="#CFCDC7", rule=TR1000_RULE
    )
    chassis = Chassis(
        body="#626568", surface=TR1000_CHEEK_DEEP, surface_alt="#303336",
        border=TR1000_RULE, accent=TR1000_ACCENT,
    )
    #: where the panel's top edge catches the light
    highlight_color = "#96999B"
    #: the step buttons and the lights over them, as on the TR-909
    button_color = "#E6E3DB"
    led_color = "#F04430"
    led_off_color = "#351914"
    #: the step row: lights above the buttons, inside the nine-slice bottom
    #: edge (editor_style.SHEEN_SLICE_BOTTOM)
    led_band = 2
    button_band = 4
    steps = 16
    steps_per_group = 4
    face = FaceSpec(
        material=GradientFill(TR1000_PANEL),
        decorations=(
            Rule("top", 0.5, highlight_color),
            Rule("top", 2.5, TR1000_ACCENT),
            StepButtons(
                led_band + button_band,
                steps,
                (button_color,),
                TR1000_CHEEK_LIGHT,
                group=steps_per_group,
                gap=0.8,
                group_gap=1.6,
                # below the lights, not over them
                button_top=led_band,
                lights=StepLights(
                    led_band, led_color, led_off_color, every=steps_per_group
                ),
            ),
        ),
        rim="#383B3E",
    )
    ear = EarSpec(
        GradientFill(TR1000_CHEEK, direction="horizontal"),
        rim="#1D2022",
        screw="#8B8E90",
        screw_inset=11,
    )


#: The light falling down the Jupiter-8's textured panel
JP8_SHADE = GradientColorStops(
    (
        GradientStop(0.0, (255, 255, 255, 10)),
        GradientStop(1.0, (0, 0, 0, 40)),
    )
)

#: Its silver end cheeks, top to bottom
JP8_CHEEK = GradientColorStops(
    (
        GradientStop(0.0, (208, 208, 204)),
        GradientStop(0.5, (188, 188, 184)),
        GradientStop(1.0, (168, 168, 164)),
    )
)


class Jupiter8Skin(JDXiSkin):
    """
    The Jupiter-8: a textured near-black panel under bold red section bars,
    with the run of coloured patch buttons along the bottom.

    The red header bar is what the eye remembers of a JP-8, so it takes the
    whole of the faceplate's top edge rather than the hairline the other
    skins draw there, and the patch buttons are discrete keys with gaps
    rather than a continuous stripe.
    """

    skin_id = "jupiter8"
    label = "Jupiter-8"
    ear_width = 14
    bezel = 6
    rail_height = 0
    lcd = LED_JP8_LCD
    foreground = LIGHT_LETTERING
    #: the red of the section headers
    header_color = "#E03A20"
    chassis = Chassis(
        body="#1F1F1F", surface="#1A1A1A", surface_alt="#252525",
        border="#3A3A3A", accent=header_color,
    )
    #: how much of the top edge that bar takes (editor_style.SHEEN_SLICE_TOP)
    header_band = 3
    #: the patch buttons, in the order they run across the panel
    button_colors = (
        "#D8392A",  # red
        "#E8762A",  # orange
        "#E8C02A",  # yellow
        "#E4E0D6",  # white
        "#3FA85A",  # green
        "#2F7FD0",  # blue
    )
    button_band = 4
    buttons = 18
    face = FaceSpec(
        # Textured matte paint, not the gloss of the default skin
        material=PebbleFill("#282828"),
        decorations=(
            Wash(JP8_SHADE),
            # The section header bar across the top
            Band("top", header_band, (header_color,)),
            Rule("top", header_band + 0.5, (12, 12, 12), inset=0),
            # The patch buttons: separate keys with the panel between them
            StepButtons(
                button_band,
                buttons,
                button_colors,
                (26, 26, 26),
                gap_fraction=0.16,
                button_top=1,
            ),
        ),
        rim=(10, 10, 10),
    )
    #: A silver end cheek, the same metal on both sides
    ear = EarSpec(
        GradientFill(JP8_CHEEK),
        rim=(96, 96, 92),
        screw=(120, 120, 116),
        screw_inset=11,
    )

#: The red JD-Xi's body, across a cheek from its outer edge
JDXI_RED_BODY = GradientColorStops(
    (
        GradientStop(0.0, (196, 28, 25)),
        GradientStop(1.0, (168, 24, 21)),
    )
)


class RedJdxiSkin(JDXiSkin):
    """
    The red JD-Xi: the same glossy black control panel, set into a scarlet
    body instead of the matte black one.

    What changes is almost all chassis rather than faceplate -- the body
    around the panels, the keyboard strip, the lettering on them -- so the
    panel keeps the thin red edge the hardware shows where the inset meets
    the body, which is also what tells this skin's faceplate apart from the
    plain glossy one.
    """

    skin_id = "jdxi_red"
    label = "JD-Xi Red"
    ear_width = 14
    bezel = 6
    rail_height = 0
    lcd = ROLAND_LCD
    #: the scarlet body, and the darker red of the rules and borders on it
    body_color = "#D81F1C"
    rule_color = "#8A2A26"
    foreground = Foreground(
        text="#FFFFFF", text_secondary="#F3D3D1", rule=rule_color
    )
    chassis = Chassis(
        body=body_color, surface="#1A1A1A", surface_alt="#262626",
        border=rule_color, accent="#FF5247",
    )
    #: the body showing around the inset panel
    rim_color = body_color
    rim_width = 2
    #: the glossy panel, with the red body showing round it
    face = FaceSpec(overlays=(InsetRim(rim_color, rim_width, radius=2),))
    #: A cheek of the red body
    ear = EarSpec(
        GradientFill(JDXI_RED_BODY, direction="horizontal"),
        rim=(96, 14, 12),
        screw=(214, 214, 210),
        screw_inset=11,
    )


#: The white JD-Xi's body, across a cheek from its outer edge
JDXI_WHITE_BODY = GradientColorStops(
    (
        GradientStop(0.0, (228, 228, 224)),
        GradientStop(1.0, (246, 246, 243)),
    )
)


class WhiteJdxiSkin(JDXiSkin):
    """
    The white JD-Xi: a silver control panel set into a white body.

    The panel is the same glossy construction as the default skin -- the
    gradient, the diagonal reflection, the rim and the top highlight -- in
    light metal instead of black plastic, so it is declared as colours
    rather than painted again. The sheen is stronger than the black panel's,
    because a bright surface returns more of the light that falls on it.
    """

    skin_id = "jdxi_white"
    label = "JD-Xi White"
    ear_width = 14
    bezel = 6
    rail_height = 0
    lcd = ROLAND_LCD
    foreground = DARK_LETTERING
    chassis = Chassis(
        body="#EFEFEC", surface="#1E1E1E", surface_alt="#2A2A2A",
        border="#B8B8B2", accent=EDITOR_ACCENT,
    )
    face_stops = GradientColorStops(
        (
            GradientStop(0.0, (226, 231, 235)),
            GradientStop(0.5, (208, 213, 217)),
            GradientStop(1.0, (184, 190, 195)),
        )
    )
    face_rim = "#8E979B"
    face_highlight = (255, 255, 255, 200)
    sheen_strength = (60, 12)
    #: A cheek of the white body
    ear = EarSpec(
        GradientFill(JDXI_WHITE_BODY, direction="horizontal"),
        rim=(174, 174, 168),
        screw=(150, 152, 150),
        screw_inset=11,
    )

#: The Juno-106's matte slate panel, top to bottom
JUNO_SLATE = GradientColorStops(
    (
        GradientStop(0.0, (62, 66, 70)),
        GradientStop(0.55, (54, 58, 62)),
        GradientStop(1.0, (44, 48, 52)),
    )
)


class Juno106Skin(JDXiSkin):
    """
    The Juno-106: a matte slate panel, a red bar and a blue bar along the
    top, and wooden end cheeks.

    The bars are the coloured section rules across the machine, so they take
    the faceplate's top edge, which the nine-slice keeps at its own size.
    The cheeks are the wood at each end, drawn as the ears.
    """

    skin_id = "juno106"
    label = "Juno-106"
    ear_width = 18
    bezel = 6
    rail_height = 0
    lcd = JUNO_LCD
    foreground = LIGHT_LETTERING
    #: the red and blue section rules, top to bottom
    red_bar = "#D4202A"
    blue_bar = "#2F6FBE"
    chassis = Chassis(
        body="#2E3236", surface="#141618", surface_alt="#1E2226",
        border="#4A4E52", accent=red_bar,
    )
    #: each bar's thickness, together inside editor_style.SHEEN_SLICE_TOP
    bar = 2
    face = FaceSpec(
        material=GradientFill(JUNO_SLATE),
        decorations=(
            Band("top", bar, (red_bar,)),
            Band("top", bar, (blue_bar,), offset=bar),
        ),
        rim=(18, 20, 22),
    )
    #: A mahogany end cheek, with the dark screws the Juno uses
    ear = EarSpec(WoodFill(JUNO_WOOD), rim=(62, 32, 16), screw=(36, 32, 28))


#: The Minimoog's cabinet, taken from the lit rail: a honey walnut
MINI_WOOD = GradientColorStops(
    (
        GradientStop(0.0, (206, 156, 112)),
        GradientStop(0.45, (186, 128, 86)),
        GradientStop(1.0, (140, 88, 52)),
    )
)

#: The Minimoog has no screen. The editor's display takes the cream of the
#: legends printed on its black panel.
MINI_LCD = LcdPalette(
    bg_edge="#12100E",
    bg_mid="#1E1A16",
    bg_glow="#2C261E",
    text="#F4E6C8",
    text_dim="#A89878",
)


#: The Minimoog's black panel, top to bottom
MINI_PANEL = GradientColorStops(
    (
        GradientStop(0.0, (36, 34, 32)),
        GradientStop(0.55, (22, 20, 18)),
        GradientStop(1.0, (12, 10, 9)),
    )
)


class MiniMoogSkin(JDXiSkin):
    """
    The Minimoog: a matte black panel set in a walnut cabinet.

    The cabinet is the wood at each end and the lip above and below the
    panel. Its lanes are punched cards, on this cabinet's own wood.
    """

    skin_id = "minimoog"
    label = "Mini Moog"
    ear_width = 18
    bezel = 6
    #: The wooden rail under the panel
    rail_height = 8
    lcd = MINI_LCD
    foreground = LIGHT_LETTERING
    meter = MeterStyle.VINTAGE_VU
    #: Punched cards on the cabinet's honey walnut
    lanes = LaneStyle(cards=True, backing=WoodFill(MINI_WOOD))
    chassis = Chassis(
        body="#241C16", surface="#141210", surface_alt="#1C1916",
        border="#3A322C", accent="#E06A32",
    )
    #: How much of the top slice is the cabinet lip, inside SHEEN_SLICE_TOP
    lip = 4
    #: the dark seam where the wood meets the panel, above and below it
    seam_color = "#301C10"
    face = FaceSpec(
        material=GradientFill(MINI_PANEL),
        decorations=(
            MaterialBand("top", lip, WoodFill(MINI_WOOD)),
            Rule("top", lip, seam_color, inset=0),
        ),
        rim=(8, 7, 6),
    )
    #: A cabinet cheek. The sides are plain wood, with no rack screws.
    ear = EarSpec(WoodFill(MINI_WOOD), rim=(110, 64, 32))

    def paint_rail(self, painter: QPainter, rect: QRectF) -> None:
        """The wooden rail under the panel, the same plank as the cheeks."""
        span = max(1, int(round(rect.bottom())))
        painter.drawTiledPixmap(rect, _wood_tile(span, MINI_WOOD))
        painter.setPen(QPen(QColor(self.seam_color), 1))
        painter.drawLine(rect.topLeft(), rect.topRight())


#: The MC-101's small monochrome OLED: white pixels on true black
OLED_LCD = LcdPalette(
    bg_edge="#000000",
    bg_mid="#040506",
    bg_glow="#0B0D10",
    text="#F2F5F7",
    text_dim="#8C949B",
)


#: The MC-101's matte black moulding, top to bottom
MC101_BODY = GradientColorStops(
    (
        GradientStop(0.0, (40, 41, 44)),
        GradientStop(0.5, (30, 31, 34)),
        GradientStop(1.0, (22, 23, 25)),
    )
)

#: The MC-101's sides: darkest at each edge, where they turn away from the light
MC101_SIDE_EDGE = "#141517"
#: Its rounded sides, across the curve
MC101_SIDE = GradientColorStops(
    (
        GradientStop(0.0, MC101_SIDE_EDGE),
        GradientStop(0.5, "#222326"),
        GradientStop(1.0, MC101_SIDE_EDGE),
    )
)


def group_colors(colors, per_group: int, count: int, dim: int = 190) -> tuple:
    """
    A colour for each of ``count`` steps lit in groups: each group takes the
    next of ``colors``, its first step at full strength and the rest dimmed.

    :param colors: sequence of "#RRGGBB", one per group, reused in turn
    :param per_group: int steps in a group
    :param count: int steps
    :param dim: int how much darker the off-beat steps are (QColor.darker)
    :return: tuple of "#rrggbb"
    """
    result = []
    for index in range(count):
        colour = QColor(colors[(index // per_group) % len(colors)])
        if index % per_group:
            colour = colour.darker(dim)
        result.append(colour.name())
    return tuple(result)


class Mc101Skin(JDXiSkin):
    """
    The MC-101 groovebox: a compact matte black body, a white OLED, and the
    sixteen backlit step pads along its front edge.

    The pads are what the machine is recognised by, so, like the TR-909's
    buttons, they go in the faceplate's bottom edge and appear on every
    panel. Each group of four is lit in its own colour, as the pads take the
    colour of the track being edited, with the first step of each group
    brightest. The sides are the moulded body itself: no wood, no screws.
    """

    skin_id = "mc101"
    label = "MC-101"
    ear_width = 8
    bezel = 6
    rail_height = 0
    lcd = OLED_LCD
    foreground = LIGHT_LETTERING
    #: the pads' lit colours, one per group of four steps
    pad_colors = ("#18C8E8", "#F23C8C", "#FFB000", "#5ADC3C")
    chassis = Chassis(
        body="#18191B", surface="#0E0F10", surface_alt="#1B1C1F",
        border="#36383C", accent=pad_colors[0],
    )
    #: an unlit pad, and the slot the pads sit in, whose black also
    #: outlines the body
    pad_off_color = "#2A2C30"
    slot_color = "#060607"
    #: the pad row's height, inside editor_style.SHEEN_SLICE_BOTTOM
    pad_band = 5
    steps = 16
    steps_per_group = 4
    #: each step's colour: its group's, dimmer off the beat
    step_colors = group_colors(pad_colors, steps_per_group, steps)
    face = FaceSpec(
        # Matte black moulding: a soft fall-off, no reflection
        material=GradientFill(MC101_BODY),
        decorations=(
            # The bevel where the top surface turns down
            Rule("top", 0.5, (78, 80, 85), inset=2),
            # The sixteen step pads in their slot
            StepButtons(
                pad_band + 1,
                steps,
                step_colors,
                slot_color,
                group=steps_per_group,
                gap=0.8,
                group_gap=1.6,
                button_top=1,
            ),
        ),
        rim=slot_color,
        radius=3,
    )
    #: The rounded side of the body, in the same matte black
    ear = EarSpec(GradientFill(MC101_SIDE, direction="horizontal"), rim=slot_color)

    def pad_color(self, index: int) -> str:
        """The colour step `index` is lit in: its group's, dimmer off the beat."""
        return self.step_colors[index % len(self.step_colors)]

#: The MS-20 has no screen. The editor's display takes the white of the
#: lettering printed on its black panel, on a cold dark ground.
ICE_LCD = LcdPalette(
    bg_edge="#0B0C0D",
    bg_mid="#15181A",
    bg_glow="#1F2427",
    text="#E6EEF0",
    text_dim="#8E9A9F",
)


#: The MS-20's matte black panel, top to bottom
MS20_PANEL = GradientColorStops(
    (
        GradientStop(0.0, (34, 34, 34)),
        GradientStop(0.5, (24, 24, 24)),
        GradientStop(1.0, (16, 16, 16)),
    )
)


class Ms20Skin(JDXiSkin):
    """
    The Korg MS-20: a matte black panel with its sections boxed in white
    lines, and patch cables.

    Editor panels are drawn from a stretched image that keeps only a few
    pixels of each edge sharp, so cables across their middle would be
    distorted and sit behind the controls. They get the white section box,
    drawn in that sharp edge. The cables are on the rack-mounted panels
    instead, where nothing lies behind them: each cheek is a small patch bay
    with a cable looped between two jacks, and a third cable sags along a
    slim rail under the panel, plugged into the foot of each cheek.
    """

    skin_id = "ms20"
    label = "MS-20"
    ear_width = 20
    bezel = 6
    #: The rail the long cable hangs in
    rail_height = 12
    lcd = ICE_LCD
    foreground = Foreground(
        text="#F2F2F0", text_secondary="#B4B4B0", rule="#5A5A58"
    )
    #: cables: left cheek, right cheek, and the one along the rail
    cable_colors = ("#D23A2E", "#E8B828", "#2F6FD0")
    chassis = Chassis(
        body="#1C1C1C", surface="#101010", surface_alt="#1A1A1A",
        border="#444444", accent=cable_colors[0],
    )
    #: the white section outline
    section_line = "#E4E4E0"
    #: the cheeks and rail: dark grey plate
    plate_color = "#262626"
    #: the dark edge of the cheeks and the rail
    edge_color = "#080808"
    #: cable thickness, px, and the height below which a cheek holds one
    #: jack rather than a looped pair
    cable_width = 3.6
    loop_height = 28
    face = FaceSpec(
        material=GradientFill(MS20_PANEL),
        # The section box, inside the sharp edge of the panel image
        decorations=(Frame(section_line, inset=(2.0, 2.0, 2.0, 3.0)),),
        rim=(6, 6, 6),
    )
    #: A patch bay: jacks on a dark plate, with a cable looped outward
    ear = EarSpec(
        SolidFill(plate_color),
        details=(PatchCord(cable_colors[:2], cable_width, loop_height),),
        rim=edge_color,
    )
    #: A slim rail under the panel, with a cable sagging along it, plugged
    #: in at the foot of each cheek
    rail = RailSpec(
        SolidFill(plate_color),
        line=edge_color,
        details=(
            SaggingCable(
                cable_colors[2],
                width=cable_width * 0.85,
                inset=ear_width / 2.0,
                jack_size=ear_width * 0.75,
            ),
        ),
    )

#: The SH-101 has no screen, only red LEDs over its sequencer and arpeggio
#: keys; the editor's display takes those
SH101_LED_LCD = LcdPalette(
    bg_edge="#110706",
    bg_mid="#240C0A",
    bg_glow="#3B120E",
    text="#FF4E3A",
    text_dim="#A9321F",
)


#: The SH-101's dark slider panel, top to bottom; the same in every body
SH101_PANEL = GradientColorStops(
    (
        GradientStop(0.0, (44, 45, 47)),
        GradientStop(0.5, (32, 33, 35)),
        GradientStop(1.0, (22, 23, 24)),
    )
)


class Sh101Skin(JDXiSkin):
    """
    The SH-101: a dark matte control panel set in a coloured plastic body.

    The SH-101 came in grey, red and blue, so it is offered in all three,
    as the JD-Xi is in black, red and white. What changes is the body: the
    rim of plastic showing round the panel, the lip along its front edge,
    the sides, and the chassis behind everything. The panel itself stays the
    same dark charcoal. A portable synth, so the sides are plain moulded
    plastic: no rack screws.

    The body colours are mid tones, dark enough that white lettering stays
    legible on the body as well as the panel.
    """

    skin_id = "sh101_grey"
    label = "SH-101 Grey"
    ear_width = 14
    bezel = 6
    rail_height = 0
    lcd = SH101_LED_LCD
    foreground = Foreground(
        text="#FFFFFF", text_secondary="#E4E4E0", rule="#55565A"
    )
    #: the plastic body
    body_color = "#707270"
    #: the plastic showing round the inset panel, and its front lip
    rim_width = 2
    lip = 3


    def __init__(self) -> None:
        body = QColor(self.body_color)
        self.chassis = Chassis(
            body=self.body_color,
            surface="#141516",
            surface_alt="#1F2022",
            border=body.darker(150).name(),
            accent=body.lighter(140).name(),
        )
        self.face = FaceSpec(
            # The dark slider panel: matte, a soft fall-off
            material=GradientFill(SH101_PANEL),
            # The body's front lip, inside the image's sharp bottom edge
            decorations=(Band("bottom", self.lip, (rgba(body.darker(115)),)),),
            rim=None,
            radius=3,
            overlays=(
                # The plastic round the panel, and where it catches the light
                InsetRim(rgba(body), self.rim_width, radius=2),
                Rule("top", 0.5, rgba(body.lighter(135)), inset=3),
            ),
        )
        # A side of the moulded body, rounded off toward its outer edge
        self.ear = EarSpec(
            GradientFill(
                GradientColorStops(
                    (
                        GradientStop(0.0, rgba(body.darker(118))),
                        GradientStop(0.5, rgba(body)),
                        GradientStop(1.0, rgba(body.darker(118))),
                    )
                ),
                direction="horizontal",
            ),
            rim=rgba(body.darker(170)),
        )

class Sh101RedSkin(Sh101Skin):
    """The SH-101 in red."""

    skin_id = "sh101_red"
    label = "SH-101 Red"
    body_color = "#C42C24"


class Sh101BlueSkin(Sh101Skin):
    """The SH-101 in blue."""

    skin_id = "sh101_blue"
    label = "SH-101 Blue"
    body_color = "#2A5DB4"


#: Every skin, by id, in the order they are offered
def _editor_settings_store() -> Optional[QSettingsStore]:
    try:
        from jdxi_editor.project import __organization_name__, __program__
    except Exception:
        return None
    return QSettingsStore(__organization_name__, __program__, SKIN_SETTING)


#: The ARP 2600 has no screen. The editor's display takes the white of the
#: legends printed on its dark panel, on black.
ARP_LCD = LcdPalette(
    bg_edge="#0A0B0C",
    bg_mid="#141618",
    bg_glow="#1E2124",
    text="#E8EAEC",
    text_dim="#9A9FA4",
)


class Arp2600Skin(JDXiSkin):
    """
    The ARP 2600: a dark charcoal panel printed in white, in a black case,
    with its speakers behind perforated grilles, and patch cords looped over
    them as on the MS-20's cheeks (white on the left, orange on the right).

    The panel's look is its printing: white legends, white boxes round the
    module titles and white signal-flow lines between them. Editor panels
    get a white box and the printed flow line along the top, inside the
    sharp edges of the panel image (so section titles print in that white,
    ink_legends). On the hardware the speaker grilles are in the panel's
    lower corners; here they are the cheeks either side, the one place on a
    rack panel nothing else sits. The case's black base runs under the panel
    as a rail, and its red power lamp is the accent.
    """

    skin_id = "arp2600"
    label = "ARP 2600"
    ear_width = 26
    bezel = 6
    rail_height = 6
    lcd = ARP_LCD
    foreground = Foreground(
        text="#F0F0EE", text_secondary="#B9BCBF", rule="#6A6E72"
    )
    ink_legends = True
    chassis = Chassis(
        body="#1B1C1E", surface="#111213", surface_alt="#1C1E20",
        border="#45494D", accent="#E0302A",
    )
    #: the painted panel, top to bottom
    panel_stops = GradientColorStops(
        (
            GradientStop(0.0, (50, 53, 57)),
            GradientStop(0.5, (42, 45, 48)),
            GradientStop(1.0, (33, 35, 38)),
        )
    )
    #: the white printing
    print_color = "#E6E8EA"
    #: the outline of the panel and of the grilles
    rim_color = "#080809"
    #: the case's deepest black: its edges, and what shows through the
    #: grilles' holes
    case_shadow = "#040405"
    #: the black case
    case_stops = GradientColorStops(
        (
            GradientStop(0.0, (30, 31, 33)),
            GradientStop(1.0, (14, 15, 16)),
        )
    )
    #: patch cords over the grilles: white like the printing on the left,
    #: ARP orange on the right
    cable_colors = ("#D9DBDD", "#E07A26")
    meter = MeterStyle.VINTAGE_VU
    #: cable thickness, px, and the height below which a cheek holds one jack
    cable_width = 3.6
    loop_height = 28
    face = FaceSpec(
        material=GradientFill(panel_stops),
        decorations=(
            # The white box round the section, as round each module's title
            Frame(print_color, inset=(1.5, 1.5, 1.5, 2.5)),
            # The printed signal-flow line, inside the sharp top edge: the
            # printing's white, fainter
            Rule("top", 4.0, (230, 232, 234, 150), inset=4),
        ),
        rim=rim_color,
    )
    #: A speaker grille in the black case: holes punched in the charcoal
    #: panel (its middle shade), with a patch cord looped over it
    ear = EarSpec(
        GradientFill(case_stops, direction="horizontal"),
        details=(
            Grille(panel_stops.stops[1].color, case_shadow, rim_color),
            PatchCord(cable_colors, cable_width, loop_height),
        ),
        rim=case_shadow,
    )
    #: The case's black base, under the panel
    rail = RailSpec(GradientFill(case_stops), line=case_shadow)

#: The editor's skins, in the order they are offered; the default registry,
#: which RackPanel and RackEars follow. Changing skin restyles the editor
#: (see _restyle_application, the registry's listener).
REGISTRY = SkinRegistry(
    (JDXiSkin(),
     RedJdxiSkin(),
     WhiteJdxiSkin(),
     JdxiRackSkin(),
     Tr808Skin(),
     Tb303Skin(),
     Tr909Skin(),
     Tr1000Skin(),
     Jupiter8Skin(),
     Juno106Skin(),
     MiniMoogSkin(),
     Mc101Skin(),
     Ms20Skin(),
     Sh101Skin(),
     Sh101RedSkin(),
     Sh101BlueSkin(),
     Arp2600Skin(),
     Brushed70sSkin(),
     IvoryWalnutSkin(),

     ),
    default_id="glossy_black",
    store=_editor_settings_store(),
)
set_default_registry(REGISTRY)

#: Every skin, by id, in the order they are offered (the registry's own dict)
SKINS: Dict[str, JDXiSkin] = REGISTRY.skins


def skin_by_id(skin_id: Optional[str]) -> JDXiSkin:
    """
    The skin ``skin_id`` names, falling back to the default.

    :param skin_id: Optional[str] a key of :data:`SKINS`
    :return: JDXiSkin
    """
    return REGISTRY.get(skin_id)


def active_skin() -> JDXiSkin:
    """
    The skin everything is drawn with.

    :return: JDXiSkin
    """
    return REGISTRY.active()


def set_active_skin(skin: "str | JDXiSkin", *, remember: bool = True) -> JDXiSkin:
    """
    Change the skin, and restyle the running application.

    :param skin: str | JDXiSkin the skin, or its id
    :param remember: bool store the choice for next time
    :return: JDXiSkin the skin now in use
    """
    return REGISTRY.set_active(skin, remember=remember)


#: the panel image's filename in a stylesheet, whichever skin rendered it
_PANEL_IMAGE = re.compile(r"gloss_panel_[A-Za-z0-9_]+_(?P<size>\d+x\d+)\.png")


def _restyle_application(_skin: Optional[JDXiSkin] = None) -> None:
    """
    Repoint the chrome at the new skin's panel image.

    The panel behind an editor's outermost groups reaches them as a stylesheet
    ``border-image``, whose path names the skin that rendered it. Every editor
    carries its own stylesheet, with its own accent, and is a child of the main
    window rather than a window itself, so the path is swapped in place
    wherever it appears: rebuilding the stylesheets instead would reach none of
    them, and would throw away each editor's accent.

    :return: None
    """
    from shiboken6 import isValid
    from PySide6.QtWidgets import QApplication, QWidget

    application = QApplication.instance()
    if application is None:
        return

    from jdxi_editor.ui.style.editor_style import AppEditorStyle, gloss_panel_file

    gloss_panel_file.cache_clear()
    # The stylesheet is not cached today, but may be
    clear = getattr(AppEditorStyle.editor_stylesheet, "cache_clear", None)
    if callable(clear):
        clear()

    from jdxi_editor.ui.style.editor_style import CHASSIS_MARKER, chassis_rules
    from jdxi_editor.ui.style.jdxi import JDXiUIStyle

    chassis = chassis_rules()
    mounted = active_skin().mounted_controls
    cap = JDXiUIStyle.BUTTON_ROUND_CAP
    flat = JDXiUIStyle.BUTTON_ROUND
    desired_cap = cap if mounted else flat
    previous_cap = flat if mounted else cap

    def repoint(sheet: str) -> str:
        """The same stylesheet, with this skin's panel image and lettering."""
        sheet = _PANEL_IMAGE.sub(
            lambda match: Path(gloss_panel_file(*_size(match.group("size")))).name,
            sheet,
        )
        # The chassis block is last, so it can be replaced wholesale; rewriting
        # colours in place would catch the controls' text as well
        marker = sheet.find(CHASSIS_MARKER)
        return sheet if marker < 0 else sheet[:marker] + chassis

    if "gloss_panel_" in (application.styleSheet() or ""):
        application.setStyleSheet(repoint(application.styleSheet()))
    from jdxi_editor.ui.widgets.midi.track_viewer import MidiTrackViewer
    from jdxi_editor.ui.widgets.rack.ears import RackEars
    from jdxi_editor.ui.widgets.rack.panel import RackPanel

    for widget in application.allWidgets():
        # allWidgets() can hand back a widget whose C++ half has already gone:
        # a window closed moments ago is destroyed on Qt's side while the
        # Python wrapper waits for the garbage collector. Touching one then
        # raises RuntimeError at best and takes the process down at worst, and
        # one dead widget must not stop the rest being restyled. isValid asks
        # shiboken whether the C++ object is still there, which is cheaper and
        # safer than provoking the error and catching it; the try below stays
        # for the window where a widget dies between the check and the call.
        if not isValid(widget):
            continue
        if not isValid(widget):
            continue
        try:
            if isinstance(widget, (RackEars, MidiTrackViewer)):
                widget.apply_skin()
            elif isinstance(widget, RackPanel) and widget._pinned_skin is None:
                widget.refresh_skin()
            sheet = widget.styleSheet()
            if sheet == previous_cap:
                widget.setStyleSheet(desired_cap)
            elif sheet and ("gloss_panel_" in sheet or CHASSIS_MARKER in sheet):
                widget.setStyleSheet(repoint(sheet))
        except RuntimeError:
            continue

    # Repaint by window rather than by widget. Setting a stylesheet already
    # schedules the widget's own repaint, and a window repaints its children,
    # so touching every widget in the application only multiplies the chances
    # of reaching one that is being torn down. QWidget.update explicitly: an
    # item view overrides update() with one that demands a model index, and
    # would raise on a bare call.
    for window in application.topLevelWidgets():
        if not isValid(window):
            continue
        try:
            QWidget.update(window)
        except RuntimeError:
            continue


def _size(size: str) -> tuple:
    """
    The width and height a panel image's name ends with.

    :param size: str e.g. ``"1000x420"``
    :return: tuple[int, int]
    """
    width, _, height = size.partition("x")
    return int(width), int(height)


REGISTRY.add_listener(_restyle_application)
