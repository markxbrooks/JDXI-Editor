"""Rack skins and the panel that wears them."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QRectF, Qt  # noqa: E402
from PySide6.QtGui import QColor, QImage, QPainter  # noqa: E402
from PySide6.QtWidgets import QApplication, QLabel  # noqa: E402

from jdxi_editor.ui.style import rack_skin  # noqa: E402
from jdxi_editor.ui.style.rack_skin import (  # noqa: E402
    SKINS,
    Brushed70sSkin,
    JdxiRackSkin,
    RackSkin,
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
    saved = rack_skin._active
    rack_skin._active = rack_skin.SKINS["glossy_black"]
    yield
    rack_skin._active = saved


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
        "jupiter8",
        "juno106",
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
    skinned = render_face(RackSkin().paint_face)
    assert original == skinned


def test_an_unknown_skin_falls_back_to_the_default():
    assert skin_by_id("no-such-skin").skin_id == "glossy_black"
    assert skin_by_id(None).skin_id == "glossy_black"


def test_the_default_skin_claims_no_more_room_than_the_old_panel():
    # The glossy panel is a drop-in: 7px of bezel, no ears, no stripe
    margins = RackSkin().content_margins()
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
        "jupiter8": "#FF2A14",       # the JP-8's patch number display
        "juno106": "#C5D8EA",        # a cool grey-blue, the Juno has no screen
        "brushed_70s": "#5BFF9B",    # a green fluorescent display
        "ivory_walnut": "#FFB545",   # warm amber on painted studio gear
    }
    # Displays are not unique across skins and should not be: the red JD-Xi
    # has the same screen as the black one. What keeps the skins apart is
    # their faceplates (see test_each_face_is_distinct).


def test_setting_the_active_skin(qapp):
    set_active_skin("brushed_70s", remember=False)
    assert active_skin().skin_id == "brushed_70s"
    set_active_skin(RackSkin(), remember=False)
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
        (c.red(), c.green(), c.blue()) == rail for c in bottom_rows(RackSkin())
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
        RackSkin().paint_face(painter, QRectF(0.5, 0.5, 119, 59), sheen=sheen)
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
