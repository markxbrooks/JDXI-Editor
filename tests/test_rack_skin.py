"""Rack skins and the panel that wears them."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QRectF, Qt  # noqa: E402
from PySide6.QtGui import QColor, QImage, QPainter  # noqa: E402
from PySide6.QtWidgets import QApplication, QLabel  # noqa: E402

from picoui.skin import render as skin_render  # noqa: E402
from jdxi_editor.ui.style import rack_skin  # noqa: E402
from jdxi_editor.ui.style.rack_skin import (  # noqa: E402
    SKINS,
    Brushed70sSkin,
    JdxiRackSkin,
    JDXiSkin,
    active_skin,
    set_active_skin,
    skin_by_id,
)
from jdxi_editor.ui.widgets.rack import RackPanel  # noqa: E402


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


@pytest.fixture(autouse=True)
def restore_active_skin():
    """
    Start every test on the default skin, and leave the setting alone.

    Without pinning it, the skin is whatever is saved in the user's own
    QSettings, so the same test passes or fails depending on which skin they
    last chose.
    """
    saved = rack_skin.active_skin()
    rack_skin.REGISTRY.set_active("glossy_black", remember=False, notify=False)
    yield
    rack_skin.REGISTRY.set_active(saved, remember=False, notify=False)


def render(widget, width=400, height=120) -> QImage:
    """The widget's pixels, for asserting on what was actually painted."""
    widget.resize(width, height)
    image = QImage(width, height, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    widget.render(image)
    return image


# ----------------------------------------------------------------------
# Skins
# ----------------------------------------------------------------------
def relative_luminance(colour: str) -> float:
    """WCAG relative luminance of a #rrggbb colour."""
    channels = []
    for index in (1, 3, 5):
        value = int(colour[index : index + 2], 16) / 255
        channels.append(
            value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
        )
    red, green, blue = channels
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast(first: str, second: str) -> float:
    """WCAG contrast ratio between two colours."""
    lighter, darker = sorted(
        (relative_luminance(first), relative_luminance(second)), reverse=True
    )
    return (lighter + 0.05) / (darker + 0.05)


def face_colour(skin) -> str:
    """The middle of the skin's faceplate, as #rrggbb."""
    image = QImage(80, 80, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    skin.paint_face(painter, QRectF(0.5, 0.5, 79, 79))
    painter.end()
    return image.pixelColor(40, 40).name()


def test_the_skins_are_offered():
    assert list(SKINS) == [
        "glossy_black",
        "jdxi_red",
        "jdxi_white",
        "jdxi_rack",
        "tr808",
        "tb303",
        "tr909",
        "tr1000",
        "jupiter8",
        "juno106",
        "minimoog",
        "mc101",
        "ms20",
        "sh101_grey",
        "sh101_red",
        "sh101_blue",
        "arp2600",
        "brushed_70s",
        "ivory_walnut",
    ]


def test_lettering_is_legible_on_every_faceplate(qapp):
    """
    Near-white lettering on satin aluminium was 1.96:1, which is why a skin
    carries its own foreground: a faceplate has to be legible whatever it is
    made of.

    The body is checked as well as the panel. Lettering appears on both --
    the keyboard area's labels sit on the body -- and checking only the
    panel let the TB-303 ship at 3.88:1 against its own chassis.
    """
    for skin in SKINS.values():
        surfaces = {"face": face_colour(skin), "body": skin.chassis.body}
        for where, colour in surfaces.items():
            with subtest_name(skin, where):
                assert contrast(skin.foreground.text, colour) >= 4.5
                assert contrast(skin.foreground.text_secondary, colour) >= 3.0


def test_brushed_metal_is_neutral_silver(qapp):
    """The satin face is grey-silver, so a later warm-up toward bronze fails."""
    colour = QColor(face_colour(SKINS["brushed_70s"]))
    channels = (colour.red(), colour.green(), colour.blue())
    assert max(channels) - min(channels) <= 8
    assert 140 <= colour.lightness() <= 210
    body = QColor(SKINS["brushed_70s"].chassis.body)
    body_channels = (body.red(), body.green(), body.blue())
    assert max(body_channels) - min(body_channels) <= 8


def subtest_name(skin, where: str = ""):
    """Name the skin in a failure, without needing pytest-subtests."""
    import contextlib

    @contextlib.contextmanager
    def named():
        try:
            yield
        except AssertionError as error:
            label = f"{skin.skin_id} ({where})" if where else skin.skin_id
            raise AssertionError(f"{label}: {error}") from None

    return named()


def face_signature(skin) -> tuple:
    """
    Several points across the faceplate, not just its middle.

    Two skins can share a centre and still look nothing alike: the red
    JD-Xi is the glossy panel with the body showing at its edge.
    """
    image = QImage(120, 80, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    skin.paint_face(painter, QRectF(0.5, 0.5, 119, 79))
    painter.end()
    points = ((60, 40), (60, 2), (60, 77), (2, 40), (117, 40), (20, 20))
    return tuple(image.pixelColor(x, y).name() for x, y in points)


def test_each_face_is_distinct(qapp):
    # The complaint that started this: two skins that render the same
    faces = {skin.skin_id: face_signature(skin) for skin in SKINS.values()}
    assert len(set(faces.values())) == len(faces), faces


def test_the_303_wears_its_step_keyboard(qapp):
    """The step buttons are a keyboard on the machine, so they are here too."""
    from jdxi_editor.ui.style.rack_skin import Tb303Skin

    skin = Tb303Skin()
    image = QImage(560, 60, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    skin.paint_face(painter, QRectF(0.5, 0.5, 559, 59))
    painter.end()

    # Along the top of the band the black keys alternate with ivory ones;
    # below them the keys are all ivory
    row = [image.pixelColor(x, 56).name() for x in range(10, 550, 5)]
    assert skin.key_black.lower() in row
    assert skin.key_ivory.lower() in row
    bottom = {image.pixelColor(x, 58).name() for x in range(10, 550, 5)}
    assert skin.key_black.lower() not in bottom


def test_the_juno_wears_its_bars_and_wooden_cheeks(qapp):
    """A red bar over a blue bar on the slate, and mahogany where the ears are."""
    from jdxi_editor.ui.style.rack_skin import Juno106Skin

    skin = Juno106Skin()
    image = QImage(360, 60, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    skin.paint_face(painter, QRectF(0.5, 0.5, 359, 59))
    painter.end()

    assert [image.pixelColor(x, 1).name() for x in (20, 180, 340)] == [
        skin.red_bar.lower()
    ] * 3
    assert [image.pixelColor(x, 3).name() for x in (20, 180, 340)] == [
        skin.blue_bar.lower()
    ] * 3

    panel = QImage(400, 160, QImage.Format.Format_ARGB32)
    panel.fill(Qt.GlobalColor.transparent)
    painter = QPainter(panel)
    skin.paint(painter, QRectF(0.5, 0.5, 399, 159))
    painter.end()
    left = panel.pixelColor(8, 40)
    right = panel.pixelColor(390, 40)
    assert left.red() > left.green() > left.blue()
    assert left.red() > left.blue() + 40
    # The two cheeks are the same plank. A leaked screw brush once painted
    # the right one nearly black.
    assert abs(left.red() - right.red()) <= 8
    assert abs(left.green() - right.green()) <= 8
    assert abs(left.blue() - right.blue()) <= 8


def test_the_minimoog_is_a_black_panel_in_a_walnut_cabinet(qapp):
    """Matte black between a wooden lip, wooden cheeks, and a wooden rail."""
    from jdxi_editor.ui.style.rack_skin import SKINS, MiniMoogSkin

    skin = MiniMoogSkin()
    assert {s.skin_id for s in SKINS.values() if s.lanes.cards} == {
        "brushed_70s",
        "minimoog",
    }

    face = QImage(360, 80, QImage.Format.Format_ARGB32)
    face.fill(Qt.GlobalColor.transparent)
    painter = QPainter(face)
    skin.paint_face(painter, QRectF(0.5, 0.5, 359, 79))
    painter.end()
    lip = face.pixelColor(180, 1)
    panel = face.pixelColor(180, 40)
    assert lip.red() > lip.green() > lip.blue()
    assert lip.red() > lip.blue() + 40
    assert panel.lightness() < 40

    image = QImage(400, 160, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    skin.paint(painter, QRectF(0.5, 0.5, 399, 159))
    painter.end()
    left = image.pixelColor(8, 40)
    right = image.pixelColor(390, 40)
    rail = image.pixelColor(200, 155)
    for wood in (left, right, rail):
        assert wood.red() > wood.green() > wood.blue(), wood.name()
        assert wood.red() > wood.blue() + 40, wood.name()
    assert abs(left.red() - right.red()) <= 8
    assert image.pixelColor(200, 40).lightness() < 40


def test_both_cheeks_are_the_same_material(qapp):
    """
    A screw used to leave its brush set, and the next cheek's outline filled
    with that colour. Every skin's two cheeks are the same material.
    """
    for skin in SKINS.values():
        if not skin.ear_width:
            continue
        image = QImage(400, 160, QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.transparent)
        painter = QPainter(image)
        skin.paint(painter, QRectF(0.5, 0.5, 399, 159))
        painter.end()
        # The middle of each cheek, clear of the screws at the top and bottom
        left = image.pixelColor(skin.ear_width // 2, 80)
        right = image.pixelColor(399 - skin.ear_width // 2, 80)
        for channel in ("red", "green", "blue"):
            gap = abs(getattr(left, channel)() - getattr(right, channel)())
            assert gap <= 12, f"{skin.skin_id} {channel} {left.name()} {right.name()}"


def test_the_jupiter_wears_its_header_bar_and_patch_buttons(qapp):
    """
    The red section bar is the JP-8's signature, so it takes the whole top
    edge; the patch buttons are separate keys, not a continuous stripe.
    """
    from jdxi_editor.ui.style.rack_skin import Jupiter8Skin

    skin = Jupiter8Skin()
    image = QImage(360, 60, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    skin.paint_face(painter, QRectF(0.5, 0.5, 359, 59))
    painter.end()

    header = [image.pixelColor(x, 1).name() for x in (20, 180, 340)]
    assert header == [skin.header_color.lower()] * 3

    # The panel shows between the buttons, which is what makes them buttons
    band = [image.pixelColor(x, 57).name() for x in range(4, 356, 2)]
    assert any(colour.lower() in band for colour in skin.button_colors)
    assert "#1a1a1a" in band

    panel = QImage(400, 80, QImage.Format.Format_ARGB32)
    panel.fill(Qt.GlobalColor.transparent)
    painter = QPainter(panel)
    skin.paint(painter, QRectF(0.5, 0.5, 399, 79))
    painter.end()
    left = panel.pixelColor(6, 40)
    right = panel.pixelColor(392, 40)
    for cheek in (left, right):
        channels = (cheek.red(), cheek.green(), cheek.blue())
        assert max(channels) - min(channels) <= 12
        assert min(channels) >= 150
    assert abs(left.red() - right.red()) <= 12


def test_the_909_wears_its_step_buttons_and_lights(qapp):
    """Cream buttons in fours, each with a light above it, lit on the downbeat."""
    from jdxi_editor.ui.style.rack_skin import Tr909Skin

    skin = Tr909Skin()
    image = QImage(640, 60, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    skin.paint_face(painter, QRectF(0.5, 0.5, 639, 59))
    painter.end()

    step = 640 / skin.steps
    buttons = [
        image.pixelColor(int((index + 0.5) * step), 57).name()
        for index in range(skin.steps)
    ]
    assert buttons == [skin.button_color.lower()] * skin.steps

    lights = [
        image.pixelColor(int((index + 0.5) * step), 54).name()
        for index in range(skin.steps)
    ]
    lit = [index for index, colour in enumerate(lights)
           if colour == skin.led_color.lower()]
    assert lit == [0, 4, 8, 12]


def test_the_mc101_wears_its_lit_step_pads(qapp):
    """Sixteen pads in four coloured groups on matte black, first of each brightest."""
    from jdxi_editor.ui.style.rack_skin import Mc101Skin

    skin = Mc101Skin()
    image = QImage(640, 60, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    skin.paint_face(painter, QRectF(0.5, 0.5, 639, 59))
    painter.end()

    step = 640 / skin.steps
    pads = [image.pixelColor(int((i + 0.5) * step), 56).name() for i in range(skin.steps)]
    assert pads == [skin.pad_color(i) for i in range(skin.steps)]
    assert [pads[i] for i in (0, 4, 8, 12)] == [c.lower() for c in skin.pad_colors]
    for i in range(skin.steps):
        if i % 4:
            assert QColor(pads[i]).value() < QColor(pads[i - i % 4]).value()
    # The body is matte black, and the screen is white on black
    assert image.pixelColor(320, 30).lightness() < 40
    assert QColor(skin.lcd.bg_edge).lightness() == 0
    assert skin.chassis.accent.lower() == skin.pad_colors[0].lower()


def test_the_ms20_is_boxed_in_white_with_patch_cables(qapp):
    """
    A black panel in a white section box; patch cables on the rack panels,
    looped on each cheek and sagging along the rail, clear of the content.
    """
    from jdxi_editor.ui.style.rack_skin import Ms20Skin

    skin = Ms20Skin()
    face = QImage(300, 120, QImage.Format.Format_ARGB32)
    face.fill(Qt.GlobalColor.transparent)
    painter = QPainter(face)
    skin.paint_face(painter, QRectF(0.5, 0.5, 299, 119))
    painter.end()
    assert face.pixelColor(150, 60).lightness() < 40  # matte black
    # The white box sits in the image's sharp top edge (SHEEN_SLICE_TOP)
    assert any(face.pixelColor(150, y).lightness() > 150 for y in range(1, 5))

    # Painted away from the image's edge, as a panel in a window is: the
    # cheeks must still get their own cables
    image = QImage(420, 220, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.translate(10, 10)
    skin.paint(painter, QRectF(10.5, 10.5, 399, 199))
    painter.end()
    image = image.copy(20, 20, 400, 200)

    def near(colour_hex, x0, x1, y0, y1):
        target = QColor(colour_hex)
        return any(
            abs(image.pixelColor(x, y).red() - target.red()) < 30
            and abs(image.pixelColor(x, y).green() - target.green()) < 30
            and abs(image.pixelColor(x, y).blue() - target.blue()) < 30
            for x in range(x0, x1) for y in range(y0, y1)
        )

    red, yellow, blue = skin.cable_colors
    ear, rail = skin.ear_width, skin.rail_height
    assert near(red, 0, ear, 20, 180)  # looped on the left cheek
    assert near(yellow, 400 - ear, 400, 20, 180)  # and on the right
    assert near(blue, ear, 400 - ear, 200 - rail, 200)  # sagging along the rail
    # Nothing of the cables reaches the content area
    margins = skin.content_margins()
    for colour in skin.cable_colors:
        assert not near(colour, margins.left() + 2, 400 - margins.right() - 2,
                        margins.top() + 2, 200 - margins.bottom() - 2)


def test_the_sh101_comes_in_three_colours_round_one_panel(qapp):
    """
    Grey, red and blue bodies round the same dark panel: the rim, the front
    lip, the sides and the chassis take the body colour; the panel does not.
    """
    from jdxi_editor.ui.style.rack_skin import SKINS

    skins = [SKINS[i] for i in ("sh101_grey", "sh101_red", "sh101_blue")]
    assert len({s.body_color for s in skins}) == 3

    def render(skin):
        image = QImage(400, 160, QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.transparent)
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        skin.paint(painter, QRectF(0.5, 0.5, 399, 159))
        painter.end()
        return image

    def close(colour, hex_colour, tolerance=40):
        target = QColor(hex_colour)
        return (abs(colour.red() - target.red()) + abs(colour.green() - target.green())
                + abs(colour.blue() - target.blue())) <= tolerance

    panels = set()
    for skin in skins:
        image = render(skin)
        middle = image.pixelColor(200, 80)
        assert middle.lightness() < 45  # the dark slider panel
        panels.add(middle.name())
        assert close(image.pixelColor(skin.ear_width // 2, 80), skin.body_color)  # the side
        face_left = skin.ear_width
        assert close(image.pixelColor(200, 1), skin.body_color, 90)  # the rim
        assert skin.chassis.body == skin.body_color
        assert not close(image.pixelColor(face_left + 40, 80), skin.body_color)
    assert len(panels) == 1  # one panel, three bodies


def test_the_arp2600_is_a_dark_panel_printed_in_white(qapp):
    """
    A dark charcoal panel boxed and lined in white, between speaker grilles
    in the black case with patch cords looped over them, and the case's base
    under it.
    """
    from jdxi_editor.ui.style.rack_skin import SKINS

    skin = SKINS["arp2600"]
    assert skin.ink_legends  # section titles printed in the panel's white
    assert not skin.mounted_controls  # a dark panel needs no caps and wells
    image = QImage(400, 160, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    skin.paint(painter, QRectF(0.5, 0.5, 399, 159))
    painter.end()
    assert image.pixelColor(200, 70).lightness() < 70  # dark charcoal
    # The grille, on the inner side of the cheek (the cord bows outward):
    # holes darker than the plate they are punched in
    ear = skin.ear_width
    grille = [image.pixelColor(x, y).lightness()
              for x in range(ear // 2 + 1, ear - 5) for y in range(60, 100)]
    assert max(grille) < 60 and max(grille) - min(grille) > 8

    # Patch cords over the grilles: white on the left, orange on the right
    def has(colour_hex, x0, x1):
        target = QColor(colour_hex)
        return any(
            abs(image.pixelColor(x, y).red() - target.red()) < 30
            and abs(image.pixelColor(x, y).green() - target.green()) < 30
            and abs(image.pixelColor(x, y).blue() - target.blue()) < 30
            for x in range(x0, x1) for y in range(10, 150)
        )

    white, orange = skin.cable_colors
    assert has(white, 0, ear) and not has(orange, 0, ear)
    assert has(orange, 400 - ear, 400) and not has(white, 400 - ear, 400)
    assert image.pixelColor(200, 160 - skin.rail_height // 2).lightness() < 40  # the base
    # The white box and printed line, in the face's sharp top edge
    face = QImage(300, 80, QImage.Format.Format_ARGB32)
    face.fill(Qt.GlobalColor.transparent)
    painter = QPainter(face)
    skin.paint_face(painter, QRectF(0.5, 0.5, 299, 79))
    painter.end()
    top = [face.pixelColor(150, y).lightness() for y in range(1, 5)]
    assert max(top) > 180
    assert face.pixelColor(150, 40).lightness() < 70


@pytest.mark.parametrize("height", [24, 34, 50, 80])
def test_the_ms20_cheeks_carry_cables_on_short_strips(qapp, height):
    """
    The MIDI player's bands and the status bar are short: each cheek still
    shows its cable (looped between two jacks, or hanging off one), red on
    the left and yellow on the right wherever the strip sits.
    """
    from jdxi_editor.ui.style.rack_skin import Ms20Skin

    skin = Ms20Skin()
    image = QImage(460, height + 20, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    skin.paint_ears(painter, QRectF(30.5, 10.5, 400, height))
    painter.end()

    def has(colour_hex, x0, x1):
        target = QColor(colour_hex)
        return any(
            abs(image.pixelColor(x, y).red() - target.red()) < 30
            and abs(image.pixelColor(x, y).green() - target.green()) < 30
            and abs(image.pixelColor(x, y).blue() - target.blue()) < 30
            for x in range(x0, x1) for y in range(10, 10 + height)
        )

    red, yellow, _blue = skin.cable_colors
    ear = skin.ear_width
    assert has(red, 30, 30 + ear) and not has(yellow, 30, 30 + ear)
    assert has(yellow, 430 - ear, 431) and not has(red, 430 - ear, 431)
    jacks = skin_render.jack_points(QRectF(0, 0, ear, height), skin.loop_height)
    assert len(jacks) == (2 if height >= skin.loop_height else 1)


def test_the_808_wears_its_step_buttons(qapp):
    """The run of step colours is in the face, so it reaches every panel."""
    from jdxi_editor.ui.style.rack_skin import Tr808Skin

    skin = Tr808Skin()
    image = QImage(200, 60, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    skin.paint_face(painter, QRectF(0.5, 0.5, 199, 59))
    painter.end()
    band = [image.pixelColor(x, 57).name() for x in (25, 75, 125, 175)]
    assert band == [colour.lower() for colour in skin.step_colors]


def test_the_default_skin_is_the_panel_it_replaced(qapp):
    """
    Pixel for pixel the Instrument window's panel.

    This is what makes the widget a drop-in: wrapping something in a
    RackPanel must not change how it looks until a skin is chosen.
    """
    from jdxi_editor.ui.image.instrument import draw_gloss_panel

    def render_face(paint) -> QImage:
        image = QImage(400, 160, QImage.Format.Format_ARGB32_Premultiplied)
        image.fill(Qt.GlobalColor.transparent)
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        paint(painter, QRectF(0.5, 0.5, 399, 159))
        painter.end()
        return image

    original = render_face(lambda p, r: draw_gloss_panel(p, r, sheen=True))
    skinned = render_face(JDXiSkin().paint_face)
    assert original == skinned


def test_an_unknown_skin_falls_back_to_the_default():
    assert skin_by_id("no-such-skin").skin_id == "glossy_black"
    assert skin_by_id(None).skin_id == "glossy_black"


def test_the_default_skin_claims_no_more_room_than_the_old_panel():
    # The glossy panel is a drop-in: 7px of bezel, no ears, no stripe
    margins = JDXiSkin().content_margins()
    assert (margins.left(), margins.top(), margins.right(), margins.bottom()) == (
        7,
        7,
        7,
        7,
    )


def test_chrome_is_exactly_what_the_skin_declares():
    # A skin cannot take room it has not declared: the margins are derived
    for skin in SKINS.values():
        margins = skin.content_margins()
        assert margins.left() == skin.ear_width + skin.bezel
        assert margins.right() == skin.ear_width + skin.bezel
        assert margins.top() == skin.bezel
        assert margins.bottom() == skin.bezel + skin.rail_height


def test_the_rack_skins_stay_thin():
    # The point of the design: chrome must not eat the content area
    for skin in (JdxiRackSkin(), Brushed70sSkin()):
        margins = skin.content_margins()
        assert margins.left() + margins.right() <= 48
        assert margins.top() + margins.bottom() <= 16


def test_each_skin_carries_its_own_display_palette():
    # Orange on dark red, the blue backlit screen of the rack unit, and a
    # green fluorescent one: no two skins share a display
    texts = {skin.skin_id: skin.lcd.text for skin in SKINS.values()}
    assert texts == {
        "glossy_black": "#FF6A00",   # the JD-Xi's orange on dark red
        "jdxi_red": "#FF6A00",       # the same machine, so the same display
        "jdxi_white": "#FF6A00",     # and so is this one
        "jdxi_rack": "#CFEEFF",      # the rack unit's blue backlit screen
        "tr808": "#FF4A33",          # the 808's red step LEDs
        "tb303": "#FF1F10",          # the 303's red LED numerals
        "tr909": "#FF3A20",          # the 909's red LED display
        "tr1000": "#F0EEE8",         # warm white on charcoal
        "jupiter8": "#FF2A14",       # the JP-8's patch number display
        "juno106": "#C5D8EA",        # a cool grey-blue, the Juno has no screen
        "minimoog": "#F4E6C8",       # cream legends, the Mini has no screen
        "mc101": "#F2F5F7",          # the MC-101's white OLED
        "ms20": "#E6EEF0",           # the MS-20's white lettering, no screen
        "sh101_grey": "#FF4E3A",     # the SH-101's red LEDs, no screen
        "sh101_red": "#FF4E3A",      # the same machine in another colour
        "sh101_blue": "#FF4E3A",
        "arp2600": "#E8EAEC",        # the 2600's white legends, no screen
        "brushed_70s": "#5BFF9B",    # a green fluorescent display
        "ivory_walnut": "#FFB545",   # warm amber on painted studio gear
    }
    # Displays are not unique across skins and should not be: the red JD-Xi
    # has the same screen as the black one. What keeps the skins apart is
    # their faceplates (see test_each_face_is_distinct).


def test_setting_the_active_skin(qapp):
    set_active_skin("brushed_70s", remember=False)
    assert active_skin().skin_id == "brushed_70s"
    set_active_skin(JDXiSkin(), remember=False)
    assert active_skin().skin_id == "glossy_black"


def test_each_skin_paints_without_error(qapp):
    for skin in SKINS.values():
        image = QImage(200, 80, QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.transparent)
        painter = QPainter(image)
        skin.paint(painter, QRectF(0.5, 0.5, 199, 79))
        painter.end()
        assert image.pixelColor(100, 40).alpha() == 255, skin.skin_id


def test_the_stylesheet_image_is_named_after_the_skin(qapp):
    from jdxi_editor.ui.style.editor_style import gloss_panel_file

    gloss_panel_file.cache_clear()
    set_active_skin("brushed_70s", remember=False)
    brushed = gloss_panel_file()
    gloss_panel_file.cache_clear()
    set_active_skin("glossy_black", remember=False)
    glossy = gloss_panel_file()
    # One skin must not serve another's cached image
    assert brushed != glossy
    assert "brushed_70s" in brushed and "glossy_black" in glossy


# ----------------------------------------------------------------------
# The panel
# ----------------------------------------------------------------------
def test_rack_ears_follow_the_skin(qapp):
    """A strip grows ears with a rack skin and loses them with the default."""
    from PySide6.QtWidgets import QLabel

    from jdxi_editor.ui.style.rack_skin import JdxiRackSkin
    from jdxi_editor.ui.widgets.rack.ears import RackEars

    set_active_skin("jdxi_rack", remember=False)
    strip = RackEars(QLabel("content"))
    ears = JdxiRackSkin().ear_width
    assert strip.layout().contentsMargins().left() == ears
    assert strip.layout().contentsMargins().right() == ears

    set_active_skin("glossy_black", remember=False)
    assert strip.layout().contentsMargins().left() == 0
    assert strip.layout().contentsMargins().right() == 0

    set_active_skin("jdxi_rack", remember=False)
    strip.resize(240, 80)
    image = QImage(strip.size(), QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    strip.render(image)
    # The ear is metal; the middle, past the ear, is not that same pixel.
    assert image.pixelColor(4, 40).alpha() > 0
    assert image.pixelColor(4, 40) != image.pixelColor(ears + 8, 40)


def test_the_panel_gives_its_margins_to_the_skin(qapp):
    panel = RackPanel(QLabel("content"), skin="jdxi_rack")
    margins = panel.layout().contentsMargins()
    assert margins.left() == JdxiRackSkin().content_margins().left()


def test_a_panel_without_a_skin_follows_the_application(qapp):
    panel = RackPanel(QLabel("content"))
    set_active_skin("brushed_70s", remember=False)
    assert panel.skin.skin_id == "brushed_70s"
    set_active_skin("glossy_black", remember=False)
    assert panel.skin.skin_id == "glossy_black"


def test_a_named_skin_pins_the_panel(qapp):
    panel = RackPanel(QLabel("content"), skin="jdxi_rack")
    set_active_skin("brushed_70s", remember=False)
    assert panel.skin.skin_id == "jdxi_rack"


def test_changing_a_panels_skin_moves_its_content(qapp):
    panel = RackPanel(QLabel("content"))
    before = panel.layout().contentsMargins().left()
    panel.set_skin("jdxi_rack")
    after = panel.layout().contentsMargins().left()
    assert after > before
    panel.set_skin(None)  # back to following the application
    assert panel.layout().contentsMargins().left() == before


def test_replacing_the_content(qapp):
    first, second = QLabel("first"), QLabel("second")
    panel = RackPanel(first)
    panel.set_content(second)
    assert panel.content() is second
    assert first.parent() is None
    assert panel.layout().count() == 1


def test_the_panel_paints_its_skin(qapp):
    # The ears are the visible difference, so the two skins cannot render alike
    content = QLabel("content")
    glossy = render(RackPanel(content, skin="glossy_black"))
    racked = render(RackPanel(QLabel("content"), skin="jdxi_rack"))
    assert glossy != racked
    # ... and the JD-Xi rack's stripe is its accent red along the bottom
    stripe = racked.pixelColor(200, 118)
    assert (stripe.red(), stripe.green(), stripe.blue()) == (224, 68, 53)


def test_switching_restyles_a_panel_that_is_not_a_window(qapp):
    """
    The editors carry their own stylesheet and are children of the main
    window, so restyling only top-level widgets reaches none of them.
    """
    from PySide6.QtWidgets import QGroupBox, QMainWindow, QTabWidget, QVBoxLayout

    from jdxi_editor.ui.style.editor_style import AppEditorStyle, mark_sheen

    set_active_skin("glossy_black", remember=False)
    editor = QGroupBox()
    QVBoxLayout(editor).addWidget(QLabel("content"))
    mark_sheen(editor)
    editor.setStyleSheet(AppEditorStyle.editor_stylesheet())
    tabs = QTabWidget()
    tabs.addTab(editor, "Pattern")
    window = QMainWindow()
    window.setCentralWidget(tabs)
    window.resize(420, 200)
    window.show()
    qapp.processEvents()
    assert not editor.isWindow()

    def panel_rgb() -> tuple:
        image = QImage(editor.width(), editor.height(), QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.transparent)
        editor.render(image)
        colour = image.pixelColor(editor.width() // 2, editor.height() // 2)
        return colour.red(), colour.green(), colour.blue()

    glossy = panel_rgb()
    set_active_skin("brushed_70s", remember=False)
    qapp.processEvents()
    brushed = panel_rgb()
    window.close()

    assert glossy[0] < 60, glossy  # the shiny black panel
    assert brushed[0] > 120, brushed  # brushed aluminium


def test_switching_survives_widgets_whose_update_takes_an_index(qapp):
    """
    An item view overrides update() with one that demands a model index, so
    a bare widget.update() over every widget raises TypeError.
    """
    from PySide6.QtWidgets import QListView

    view = QListView()
    view.show()
    qapp.processEvents()
    set_active_skin("brushed_70s", remember=False)  # must not raise
    view.close()


def test_the_jdxi_skin_is_recognisable_without_a_rack_panel(qapp):
    """
    Ears are drawn by a widget, never by the nine-slice, so the stripe has to
    be part of the face: otherwise the skin is identical to the plain glossy
    one everywhere the faceplate arrives as a stylesheet image.
    """
    from jdxi_editor.ui.style.rack_skin import JdxiRackSkin

    def bottom_rows(skin) -> list:
        image = QImage(120, 60, QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.transparent)
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        skin.paint_face(painter, QRectF(0.5, 0.5, 119, 59))
        painter.end()
        return [image.pixelColor(60, y) for y in range(54, 59)]

    rail = QColorRGB(JdxiRackSkin().rail_color)
    assert any(
        (c.red(), c.green(), c.blue()) == rail for c in bottom_rows(JdxiRackSkin())
    )
    assert not any(
        (c.red(), c.green(), c.blue()) == rail for c in bottom_rows(JDXiSkin())
    )


def QColorRGB(name: str) -> tuple:
    """The red, green and blue of a colour name, for comparing pixels."""
    from PySide6.QtGui import QColor

    colour = QColor(name)
    return colour.red(), colour.green(), colour.blue()


def test_brushed_metal_prints_ink_and_mounts_its_controls(qapp):
    """
    The brushed plate silkscreens its section titles and shades idle buttons
    as caps. Other skins keep the red section rule, and a lit button stays red.
    """
    from jdxi_editor.ui.style.editor_style import AppEditorStyle, CHASSIS_MARKER
    from jdxi_editor.ui.style.factory import active_round_button_style
    from jdxi_editor.ui.style.jdxi import JDXiUIStyle
    from jdxi_editor.ui.style.rack_skin import DARK_LETTERING

    set_active_skin("brushed_70s", remember=False)
    chassis = AppEditorStyle.editor_stylesheet()
    chassis = chassis[chassis.index(CHASSIS_MARKER) :]
    assert "QGroupBox::title" in chassis
    assert DARK_LETTERING.text in chassis
    assert DARK_LETTERING.rule in chassis
    assert "stop:0 #4A4A46" in chassis
    cap = active_round_button_style()
    assert cap == JDXiUIStyle.BUTTON_ROUND_CAP
    assert "#E04435" not in cap.split("QPushButton:checked")[0]
    assert "border_pressed" in cap or ":checked" in cap

    set_active_skin("glossy_black", remember=False)
    chassis = AppEditorStyle.editor_stylesheet()
    chassis = chassis[chassis.index(CHASSIS_MARKER) :]
    assert "QGroupBox::title" not in chassis
    assert active_round_button_style() == JDXiUIStyle.BUTTON_ROUND


def test_the_body_and_tabs_follow_the_skin(qapp):
    """
    The skin reaches past the panels: the body the editors are mounted on,
    and the tabs standing on it, are the skin's too.
    """
    from jdxi_editor.ui.style.editor_style import AppEditorStyle, CHASSIS_MARKER

    for skin in SKINS.values():
        set_active_skin(skin, remember=False)
        sheet = AppEditorStyle.editor_stylesheet()
        chassis = sheet[sheet.index(CHASSIS_MARKER) :]
        assert skin.chassis.body in chassis, skin.skin_id
        assert skin.chassis.surface_alt in chassis, skin.skin_id
        assert skin.chassis.accent in chassis, skin.skin_id


def test_the_drawn_instrument_follows_the_skin(qapp):
    """The picture of the JD-Xi wears the same faceplate as the editors."""
    from jdxi_editor.ui.image.instrument import draw_instrument_pixmap

    def instrument_colours() -> tuple:
        image = draw_instrument_pixmap().toImage()
        body = image.pixelColor(3, 3)
        panel = image.pixelColor(250, 120)
        return body.name(), panel.name()

    set_active_skin("glossy_black", remember=False)
    dark_body, dark_panel = instrument_colours()
    set_active_skin("tr909", remember=False)
    light_body, light_panel = instrument_colours()

    assert dark_body != light_body
    assert dark_panel != light_panel
    # the light skin really is light, rather than merely different
    assert QColor(light_panel).lightness() > QColor(dark_panel).lightness() + 100


def test_a_skin_may_drop_the_sheen(qapp):
    """
    The instrument's right-hand panel is drawn without the reflection, as on
    the JD-Xi, so the faceplate has to be paintable either way.
    """
    def render(sheen: bool) -> QImage:
        image = QImage(120, 60, QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.transparent)
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        JDXiSkin().paint_face(painter, QRectF(0.5, 0.5, 119, 59), sheen=sheen)
        painter.end()
        return image

    assert render(True) != render(False)
    # every skin accepts the flag, whether or not it has a reflection to drop
    for skin in SKINS.values():
        image = QImage(60, 40, QImage.Format.Format_ARGB32)
        painter = QPainter(image)
        skin.paint_face(painter, QRectF(0.5, 0.5, 59, 39), sheen=False)
        painter.end()


def test_the_keyboard_area_follows_the_skin(qapp):
    """
    The wheels, indicators and keys sit on the instrument's body, so the
    strip behind them is the skin's too, and its lettering is silkscreen.
    """
    from PySide6.QtWidgets import QMainWindow

    from jdxi_editor.ui.widgets.piano.keyboard import PianoKeyboard
    from jdxi_editor.ui.windows.jdxi.ui import JDXiWindow

    class Window(QMainWindow):
        apply_keyboard_area_skin = JDXiWindow.apply_keyboard_area_skin

        def __init__(self):
            super().__init__()
            self.piano_keyboard = PianoKeyboard(parent=self)
            self.statusBar().addPermanentWidget(self.piano_keyboard)

    window = Window()
    try:
        for skin in SKINS.values():
            set_active_skin(skin, remember=False)
            window.apply_keyboard_area_skin()
            assert skin.chassis.body in window.statusBar().styleSheet(), skin.skin_id
            label = window.piano_keyboard.drum_labels[0].styleSheet()
            assert skin.foreground.text_secondary in label, skin.skin_id
    finally:
        window.close()


def test_the_tool_windows_are_rack_mounted(qapp):
    """The monitor, the controller dialog and the log viewer wear a faceplate."""
    from jdxi_editor.ui.widgets.rack import RackPanel
    from jdxi_editor.ui.widgets.viewer.log import LogViewer
    from jdxi_editor.ui.windows.midi.controller_config import MidiControllerDialog
    from jdxi_editor.ui.windows.midi.monitor import MIDIMessageMonitor

    for factory in (MIDIMessageMonitor, MidiControllerDialog, LogViewer):
        window = factory()
        try:
            assert isinstance(window.centralWidget(), RackPanel), factory.__name__
        finally:
            window.close()


def test_the_keyboard_strip_wears_the_skins_ears(qapp):
    """
    The strip along the bottom is part of the instrument, so it takes the
    ears too -- and none at all from a skin that declares none.
    """
    from jdxi_editor.ui.widgets.rack import RackStatusBar

    bar = RackStatusBar()
    try:
        for skin in SKINS.values():
            set_active_skin(skin, remember=False)
            bar.apply_skin()
            margins = bar.contentsMargins()
            assert margins.left() == skin.ear_width, skin.skin_id
            assert margins.right() == skin.ear_width, skin.skin_id

        def strip() -> QImage:
            bar.resize(300, 60)
            image = QImage(300, 60, QImage.Format.Format_ARGB32)
            image.fill(Qt.GlobalColor.transparent)
            bar.render(image)
            return image

        set_active_skin("ivory_walnut", remember=False)
        bar.apply_skin()
        painted = strip()
        walnut = painted.pixelColor(4, 30)
        other = painted.pixelColor(290, 30)
        set_active_skin("glossy_black", remember=False)
        bar.apply_skin()
        plain = strip().pixelColor(4, 30)
        # the walnut cheek is there, and the skin without ears draws none
        assert walnut != plain
        assert walnut.red() > walnut.blue() + 30, walnut.name()
        # both ends are the same walnut, not the screw colour on the right
        assert abs(walnut.red() - other.red()) <= 12
        assert abs(walnut.green() - other.green()) <= 12
        assert other.red() > other.blue() + 30, other.name()
    finally:
        bar.close()


def test_widgets_added_to_the_rack_status_bar_stay_alive(qapp):
    """
    The Instrument window installs its status bar before filling it.

    setStatusBar deletes the bar it replaces; adding the MIDI indicators
    first and replacing the bar afterwards left them as live Python objects
    over dead C++ ones, and the window crashed on the next set_state.
    Installing first means nothing is ever replaced.
    """
    from PySide6.QtWidgets import QMainWindow

    from jdxi_editor.ui.widgets.indicator.led import LEDIndicator
    from jdxi_editor.ui.widgets.rack import RackStatusBar

    window = QMainWindow()
    window.setStatusBar(RackStatusBar(window))
    indicator = LEDIndicator()
    window.statusBar().addPermanentWidget(indicator)
    qapp.processEvents()

    indicator.set_state(True)  # the call that crashed
    assert indicator.parent() is not None
    window.close()


def test_the_window_installs_its_status_bar_before_filling_it(qapp):
    """
    The ordering cannot be exercised here -- the window's menu calls methods
    its subclass defines -- so the constructor is read instead. It is a
    constraint between two lines, and this is what guards it.
    """
    import inspect

    from jdxi_editor.ui.windows.jdxi.ui import JDXiWindow

    source = inspect.getsource(JDXiWindow.__init__)
    assert source.index("setStatusBar") < source.index("_create_status_bar()")


def test_the_display_follows_the_skin(qapp):
    from jdxi_editor.ui.widgets.digital.title import DigitalTitle

    title = DigitalTitle("Tone")
    set_active_skin("brushed_70s", remember=False)
    assert title.lcd.text == "#5BFF9B"
    set_active_skin("glossy_black", remember=False)
    assert title.lcd.text == "#FF6A00"


def test_meter_and_lane_styles_are_chosen_separately_from_the_material(qapp):
    """
    Any skin can take any meter or lanes: the Brushed 70s and the ARP 2600
    share the vintage VU meters, though one is aluminium and one black, and
    the Brushed 70s lays its punched cards on metal, the Minimoog on wood.
    """
    from picoui.skin import BrushedFill, WoodFill
    from jdxi_editor.ui.style.rack_skin import LaneStyle, MeterStyle

    for skin in SKINS.values():
        assert isinstance(skin.meter, MeterStyle)
        assert isinstance(skin.lanes, LaneStyle)
    brushed, arp, mini = (SKINS[i] for i in ("brushed_70s", "arp2600", "minimoog"))
    assert brushed.meter == arp.meter == MeterStyle.VINTAGE_VU
    assert isinstance(brushed.lanes.backing, BrushedFill)
    assert isinstance(mini.lanes.backing, WoodFill)
    assert not arp.lanes.cards


def test_the_skins_borrow_the_editors_own_accent():
    """EDITOR_ACCENT is the editor's illuminated red, not a copy that can drift."""
    from jdxi_editor.ui.style.editor_style import AppEditorStyle
    from jdxi_editor.ui.style.rack_skin import EDITOR_ACCENT

    assert EDITOR_ACCENT == AppEditorStyle.ACCENT
    for skin_id in ("jdxi_rack", "jdxi_white", "brushed_70s"):
        assert SKINS[skin_id].chassis.accent == EDITOR_ACCENT
