"""
A skin's face and ears as data (picoui.skin.spec), painted by
picoui.skin.render: a skin that only declares specs paints what they say.
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QColor, QImage, QPainter
from PySide6.QtWidgets import QApplication

from picoui.skin import (
    Band,
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
    GradientColorStops,
    GradientFill,
    GradientStop,
    InsetRim,
    MaterialBand,
    Rule,
    Skin,
    WoodFill,
)
from picoui.skin import render
from picoui.skin.textures import WALNUT

_APP = QApplication.instance() or QApplication([])

GREY = GradientColorStops((GradientStop(0.0, "#808080"), GradientStop(1.0, "#808080")))
RED, BLUE = "#FF0000", "#0000FF"


def _paint(fn, width=100, height=60) -> QImage:
    image = QImage(width, height, QImage.Format.Format_ARGB32)
    image.fill(QColor(255, 0, 255))
    painter = QPainter(image)
    fn(painter, QRectF(0, 0, width, height))
    painter.end()
    return image


def _rgb(image: QImage, x: int, y: int) -> str:
    return image.pixelColor(x, y).name()


class Declared(Skin):
    skin_id, label = "declared", "Declared"
    ear_width = 12
    face = FaceSpec(
        material=GradientFill(GREY),
        decorations=(Band("bottom", 4, (RED, BLUE)), Rule("top", 3.5, "#00FF00")),
        rim="#000000",
    )
    ear = EarSpec(WoodFill(WALNUT), seam="#FFFFFF", screw="#C0C0C0")


def test_a_declared_face_paints_its_material_and_decorations():
    image = _paint(lambda p, r: Declared().paint_face(p, r))
    assert _rgb(image, 50, 30) == "#808080"  # the material
    assert _rgb(image, 20, 58) == RED.lower()  # the band's first block
    assert _rgb(image, 80, 58) == BLUE.lower()  # and its second
    assert _rgb(image, 50, 3) == "#00ff00"  # the rule


def test_a_seam_runs_along_the_edge_facing_the_face():
    skin = Declared()
    image = _paint(lambda p, r: skin.paint_ears(p, r), width=100, height=60)
    assert _rgb(image, 12, 30) == "#ffffff"  # left cheek: its right edge
    assert _rgb(image, 88, 30) == "#ffffff"  # right cheek: its left edge
    assert _rgb(image, 1, 30) != "#ffffff"


def test_screws_are_left_off_a_short_cheek():
    ear = EarSpec(GradientFill(GREY), screw="#FF0000", screw_inset=6)
    tall = _paint(lambda p, r: render.paint_ear(ear, p, r), 12, 60)
    short = _paint(lambda p, r: render.paint_ear(ear, p, r), 12, 20)
    assert _rgb(tall, 6, 6) != "#808080"
    assert all(_rgb(short, 3, y) == "#808080" for y in range(20))


def test_a_face_without_material_is_the_glossy_panel_with_its_overlays():
    class Inset(Skin):
        face = FaceSpec(overlays=(InsetRim(RED, 2),))

    plain = _paint(lambda p, r: Skin().paint_face(p, r))
    inset = _paint(lambda p, r: Inset().paint_face(p, r))
    assert _rgb(plain, 50, 30) == _rgb(inset, 50, 30)  # same glossy middle
    assert _rgb(inset, 50, 1) == RED.lower()


def test_a_material_band_shades_like_the_whole_face():
    stops = GradientColorStops((GradientStop(0.0, "#000000"), GradientStop(1.0, "#FFFFFF")))
    face = FaceSpec(
        material=GradientFill(GREY),
        decorations=(MaterialBand("top", 10, GradientFill(stops)),),
    )
    image = _paint(lambda p, r: render.paint_face(face, p, r), 100, 100)
    # the band holds the top tenth of the black-to-white gradient: dark
    assert image.pixelColor(50, 5).lightness() < 30
    assert _rgb(image, 50, 50) == "#808080"


@pytest.mark.parametrize(
    "build",
    [
        lambda: Band("left", 2, (RED,)),
        lambda: Band("top", 2, ()),
        lambda: Rule("top", 1, "not a colour"),
        lambda: GradientFill(GREY, direction="diagonal"),
    ],
)
def test_bad_specs_are_refused(build):
    with pytest.raises(ValueError):
        build()


def test_specs_are_values():
    assert Rule("top", 1, "#FF0000") == Rule("top", 1, (255, 0, 0))
    with pytest.raises(Exception):
        Declared.face.rim = QColor("#FFFFFF")


def test_new_decorations_can_be_registered():
    from dataclasses import dataclass

    @dataclass(frozen=True)
    class Dot:
        color: str

    @render.paint_decoration.register
    def _(dot: Dot, painter: QPainter, rect: QRectF) -> None:
        painter.setPen(QColor(dot.color))
        painter.drawPoint(QPointF(rect.center()))

    face = FaceSpec(material=GradientFill(GREY), decorations=(Dot("#00FFFF"),))
    image = _paint(lambda p, r: render.paint_face(face, p, r))
    assert _rgb(image, 50, 30) == "#00ffff"


# --- Machine details ---------------------------------------------------------


def _face(*decorations, rim=None):
    return FaceSpec(material=SolidFill("#808080"), decorations=decorations, rim=rim)


def test_a_keyboard_has_black_keys_over_the_gaps_after_c_d_f_g_and_a():
    face = _face(Keyboard(10, 1, "#FFFFFF", "#000000", divider="#FFFFFF"))
    image = _paint(lambda p, r: render.paint_face(face, p, r), 70, 60)
    # seven 10px white keys: black keys centred on x = 10, 20, 40, 50, 60
    tops = [_rgb(image, x, 52) for x in (10, 20, 30, 40, 50, 60)]
    assert tops == ["#000000", "#000000", "#ffffff", "#000000", "#000000", "#000000"]
    assert _rgb(image, 15, 58) == "#ffffff"  # the black keys stop short


def test_step_buttons_take_their_colours_in_turn_with_lights_over_them():
    row = StepButtons(
        6, 4, (RED, BLUE), "#000000", group=2, gap=1, group_gap=3,
        button_top=2, lights=StepLights(2, "#00FF00", "#004400", every=2),
    )
    image = _paint(lambda p, r: render.paint_face(_face(row), p, r), 80, 60)
    assert [_rgb(image, x, 57) for x in (10, 30, 50, 70)] == ["#ff0000", "#0000ff"] * 2
    assert _rgb(image, 10, 55) == "#00ff00"  # lit on the first of a group
    assert _rgb(image, 30, 55) == "#004400"
    assert _rgb(image, 1, 57) == "#000000"  # the group gap shows the strip
    assert _rgb(image, 1, 50) == "#808080"  # and the face above the row


def test_frame_and_wash():
    shade = GradientColorStops((GradientStop(0.0, (0, 0, 0, 0)), GradientStop(1.0, (0, 0, 0, 255))))
    image = _paint(
        lambda p, r: render.paint_face(_face(Wash(shade), Frame(RED, (5, 5, 5, 5))), p, r),
        100, 100,
    )
    assert _rgb(image, 50, 5) == "#ff0000"
    assert image.pixelColor(50, 20).lightness() > image.pixelColor(50, 80).lightness()


def test_a_face_can_go_without_a_rim():
    with_rim = _paint(lambda p, r: render.paint_face(_face(rim="#000000"), p, r))
    without = _paint(lambda p, r: render.paint_face(_face(), p, r))
    assert _rgb(with_rim, 50, 0) == "#000000"
    assert _rgb(without, 50, 0) == "#808080"


def test_each_cheek_takes_its_own_patch_cord_colour():
    class Corded(Skin):
        ear_width = 20
        ear = EarSpec(SolidFill("#202020"), details=(PatchCord((RED, BLUE)),))

    image = _paint(lambda p, r: Corded().paint_ears(p, r), 200, 120)

    def has(colour, x0, x1):
        target = QColor(colour)
        return any(
            image.pixelColor(x, y).red() > 150 and target.red() > 150
            or image.pixelColor(x, y).blue() > 150 and target.blue() > 150
            for x in range(x0, x1) for y in range(120)
        )

    assert has(RED, 0, 20) and has(BLUE, 180, 200)
    assert render.jack_points(QRectF(0, 0, 20, 120), 28)[0].y() == pytest.approx(24)
    assert len(render.jack_points(QRectF(0, 0, 20, 20), 28)) == 1


def test_a_grille_is_punched_with_holes_and_left_off_a_small_cheek():
    ear = EarSpec(SolidFill("#202020"), details=(Grille("#808080", "#000000", "#808080"),))
    image = _paint(lambda p, r: render.paint_ear(ear, p, r), 26, 80)
    row = {_rgb(image, x, 40) for x in range(5, 21)}
    assert {"#808080", "#000000"} <= row
    small = _paint(lambda p, r: render.paint_ear(ear, p, r), 8, 80)
    assert all(_rgb(small, x, 40) == "#202020" for x in range(8))


def test_a_rail_with_a_cable_sagging_along_it():
    class Railed(Skin):
        rail_height = 12
        rail = RailSpec(
            SolidFill("#262626"), line="#FF00FF",
            details=(SaggingCable(BLUE, width=3, inset=10, jack_size=15),),
        )

    image = _paint(lambda p, r: Railed().paint_rail(p, r), 200, 12)
    assert _rgb(image, 100, 0) == "#ff00ff"
    # sagging: lowest in the middle
    blue = [image.pixelColor(100, y).blue() for y in range(1, 12)]
    assert 1 + max(range(11), key=blue.__getitem__) >= 6


def test_pebble_paint_is_speckled():
    face = FaceSpec(material=PebbleFill("#282828"), rim=None)
    image = _paint(lambda p, r: render.paint_face(face, p, r))
    assert len({image.pixel(x, 30) for x in range(100)}) > 3


@pytest.mark.parametrize(
    "build",
    [
        lambda: Keyboard(5, 0, "#FFFFFF", "#000000"),
        lambda: StepButtons(4, 0, (RED,), "#000000"),
        lambda: StepButtons(4, 4, (), "#000000"),
        lambda: PatchCord((RED,)),
        lambda: PebbleFill("nope"),
    ],
)
def test_bad_details_are_refused(build):
    with pytest.raises(ValueError):
        build()
