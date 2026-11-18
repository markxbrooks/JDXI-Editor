"""Rack skins and the panel that wears them."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QRectF, Qt  # noqa: E402
from PySide6.QtGui import QImage, QPainter  # noqa: E402
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
        "jdxi_rack",
        "tr808",
        "brushed_70s",
        "ivory_walnut",
    ]


def test_lettering_is_legible_on_every_faceplate(qapp):
    """
    Near-white lettering on satin aluminium was 1.96:1, which is why a skin
    carries its own foreground: a faceplate has to be legible whatever it is
    made of.
    """
    for skin in SKINS.values():
        face = face_colour(skin)
        with subtest_name(skin):
            assert contrast(skin.foreground.text, face) >= 4.5
            assert contrast(skin.foreground.text_secondary, face) >= 3.0


def subtest_name(skin):
    """Name the skin in a failure, without needing pytest-subtests."""
    import contextlib

    @contextlib.contextmanager
    def named():
        try:
            yield
        except AssertionError as error:
            raise AssertionError(f"{skin.skin_id}: {error}") from None

    return named()


def test_each_face_is_distinct(qapp):
    # The complaint that started this: two skins that render the same
    faces = {skin.skin_id: face_colour(skin) for skin in SKINS.values()}
    assert len(set(faces.values())) == len(faces), faces


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
        "jdxi_rack": "#CFEEFF",      # the rack unit's blue backlit screen
        "tr808": "#FF4A33",          # the 808's red step LEDs
        "brushed_70s": "#5BFF9B",    # a green fluorescent display
        "ivory_walnut": "#FFB545",   # warm amber on painted studio gear
    }
    assert len(set(texts.values())) == len(texts)


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
    Its ears can only be drawn by a RackPanel, so the stripe has to be part
    of the face: otherwise the skin is identical to the plain glossy one
    everywhere the faceplate arrives as a stylesheet image.
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


def test_the_display_follows_the_skin(qapp):
    from jdxi_editor.ui.widgets.digital.title import DigitalTitle

    title = DigitalTitle("Tone")
    set_active_skin("brushed_70s", remember=False)
    assert title.lcd.text == "#5BFF9B"
    set_active_skin("glossy_black", remember=False)
    assert title.lcd.text == "#FF6A00"
