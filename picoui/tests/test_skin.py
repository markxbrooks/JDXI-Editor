"""
picoui.skin works on its own: an application's skins, a registry that
remembers the choice and tells listeners, and widgets that follow it. No
JD-Xi code is imported here.
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QImage, QPainter
from PySide6.QtWidgets import QApplication, QLabel

from picoui.skin import (
    GradientColorStops,
    GradientStop,
    LcdPalette,
    Skin,
    SkinRegistry,
    default_registry,
    set_default_registry,
)
from picoui.skin.textures import WALNUT, brushed_tile, wood_tile
from picoui.skin.widgets import RackEars, RackPanel

_APP = QApplication.instance() or QApplication([])

import picoui.skin.gradient as _gradient_module  # noqa: E402

GRADIENT_FILE = _gradient_module.__file__

import picoui.skin.spec as _spec_module  # noqa: E402

SPEC_FILE = _spec_module.__file__


class Plain(Skin):
    skin_id, label = "plain", "Plain"


class Racked(Skin):
    skin_id, label = "racked", "Racked"
    ear_width, bezel, rail_height = 12, 5, 4
    lcd = LcdPalette("#000000", "#111111", "#222222", "#00FF00", "#008800")

    def paint_ear(self, painter, rect):
        painter.fillRect(rect, QColor("#FF0000"))


class MemoryStore:
    def __init__(self, value=None):
        self.value = value

    def load(self):
        return self.value

    def save(self, skin_id):
        self.value = skin_id


@pytest.fixture
def registry():
    previous = default_registry()
    registry = set_default_registry(SkinRegistry([Plain(), Racked()], default_id="plain"))
    yield registry
    set_default_registry(previous)


def test_unknown_ids_fall_back_to_the_default(registry):
    assert registry.ids() == ["plain", "racked"]
    assert registry.get("racked").label == "Racked"
    assert registry.get("nope").skin_id == "plain"
    assert registry.get(None).skin_id == "plain"


def test_the_saved_choice_is_read_once_and_saved_on_change():
    store = MemoryStore("racked")
    registry = SkinRegistry([Plain(), Racked()], default_id="plain", store=store)
    assert registry.active().skin_id == "racked"
    registry.set_active("plain")
    assert store.value == "plain"
    registry.set_active("racked", remember=False)
    assert store.value == "plain" and registry.active().skin_id == "racked"


def test_listeners_hear_of_each_change_unless_told_not_to():
    registry = SkinRegistry([Plain(), Racked()])
    heard = []
    registry.add_listener(lambda skin: heard.append(skin.skin_id))
    registry.set_active("racked")
    registry.set_active("plain", notify=False)
    assert heard == ["racked"]
    registry.remove_listener(registry._listeners[0])
    registry.set_active("racked")
    assert heard == ["racked"]


def test_margins_are_exactly_what_the_skin_declares():
    margins = Racked().content_margins()
    assert (margins.left(), margins.top(), margins.right(), margins.bottom()) == (17, 5, 17, 9)


def test_a_panel_follows_the_registry_or_its_pinned_skin(registry):
    panel = RackPanel(QLabel("content"))
    assert panel.skin.skin_id == "plain"
    registry.set_active("racked")
    panel.refresh_skin()
    assert panel.layout().contentsMargins().left() == 17
    pinned = RackPanel(QLabel("content"), skin="plain")
    assert pinned.skin.skin_id == "plain"
    panel.close(), pinned.close()


def test_ears_paint_the_skins_cheeks(registry):
    registry.set_active("racked")
    strip = RackEars(QLabel("x"))
    strip.resize(200, 40)
    strip.show()
    _APP.processEvents()
    image = strip.grab().toImage()
    assert image.pixelColor(3, 20).name() == "#ff0000"
    assert strip.layout().contentsMargins().left() == 12
    strip.close()


def test_a_widget_can_use_its_own_registry(registry):
    own = SkinRegistry([Racked()])
    panel = RackPanel(QLabel("x"), registry=own)
    assert panel.skin.skin_id == "racked"  # not the default registry's "plain"
    panel.close()


def test_the_base_skin_paints_an_opaque_face():
    image = QImage(200, 80, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    Skin().paint(painter, QRectF(0.5, 0.5, 199, 79))
    painter.end()
    assert image.pixelColor(100, 40).alpha() == 255


GREY = GradientColorStops((GradientStop(0.0, (200, 200, 200)), GradientStop(1.0, (120, 120, 120))))


def test_textures_are_cached_and_the_same_every_time():
    assert wood_tile(40, WALNUT) is wood_tile(40, WALNUT)
    first = brushed_tile(30, GREY).toImage()
    brushed_tile.cache_clear()
    again = brushed_tile(30, GREY).toImage()
    assert first == again


def test_paint_ears_tells_each_cheek_its_side():
    """A strip (no full panel) still tells the two cheeks apart."""
    sides = []

    class Sided(Skin):
        skin_id, ear_width = "sided", 10

        def paint_ear(self, painter, rect):
            sides.append((self.ear_side, rect.left()))

    image = QImage(200, 30, QImage.Format.Format_ARGB32)
    painter = QPainter(image)
    Sided().paint_ears(painter, QRectF(50, 0, 100, 30))
    painter.end()
    assert sides == [("left", 50), ("right", 140)]


def test_gradient_stops_are_position_colour_pairs_in_order():
    from PySide6.QtGui import QLinearGradient

    from picoui.skin import GradientColorStops, GradientStop, apply_gradient_stops

    metal = GradientColorStops((
        GradientStop(0.0, "#8A8A87"),
        GradientStop(0.35, (184, 184, 180)),
        GradientStop(0.65, "#A6A6A3"),
        GradientStop(1.0, "#777875"),
    ))
    gradient = QLinearGradient(0, 0, 0, 10)
    apply_gradient_stops(gradient, metal)
    assert [(round(p, 2), c.name()) for p, c in gradient.stops()] == [
        (0.0, "#8a8a87"), (0.35, "#b8b8b4"), (0.65, "#a6a6a3"), (1.0, "#777875")
    ]


@pytest.mark.parametrize("build", [
    lambda: GradientStop(1.5, "#000000"),             # off the gradient
    lambda: GradientStop(0.5, "not a colour"),
    lambda: GradientStop(0.5, "#FF000080"),           # #AARRGGBB or #RRGGBBAA?
    lambda: GradientStop(0.5, (256, 0, 0)),           # off the scale
    lambda: GradientStop(0.5, (1.0, 0.5, 0.0)),       # 0-1 floats, as OpenGL takes
    lambda: GradientColorStops((GradientStop(0.0, "#000000"),)),  # only one
    lambda: GradientColorStops((GradientStop(0.8, "#000000"), GradientStop(0.2, "#FFFFFF"))),
])
def test_bad_gradients_are_refused(build):
    with pytest.raises(ValueError):
        build()



def test_gradients_and_specs_are_plain_data_without_qt():
    """
    A gradient and a whole face or ear spec build, compare and hash with no
    Qt imported: Qt only meets them when they are painted.
    """
    import subprocess
    import sys

    code = (
        "import sys\n"
        "from picoui.skin.gradient import GradientColorStops, GradientStop\n"
        "from picoui.skin.spec import (Band, EarSpec, FaceSpec, GradientFill,\n"
        "    PatchCord, Rule, SolidFill, StepButtons, StepLights)\n"
        "g = GradientColorStops((GradientStop(0, '#000000'), GradientStop(1, (255, 255, 255, 128))))\n"
        "assert g.stops[1].color == (255, 255, 255, 128) and hash(g)\n"
        "face = FaceSpec(GradientFill(g), (Rule('top', 0.5, '#FF0000'),\n"
        "    StepButtons(6, 16, ('#E8E6DC',), (74, 74, 71), lights=StepLights(2, '#FF3A20', '#3A1410'))),\n"
        "    rim=(6, 6, 6))\n"
        "ear = EarSpec(SolidFill('#262626'), details=(PatchCord(('#D23A2E', '#E8B828')),), rim='#080808')\n"
        "assert face.rim == (6, 6, 6, 255) and face.decorations[0].color == (255, 0, 0, 255)\n"
        "assert hash(face) and hash(ear) and face == FaceSpec(GradientFill(g), face.decorations, rim='#060606')\n"
        "assert not any(m.startswith('PySide6') for m in sys.modules), 'Qt was imported'\n"
    )
    # picoui.skin's own __init__ imports the widgets' Qt; load the two
    # modules alone
    loader = (
        "import importlib.util, sys, types\n"
        "pkg = types.ModuleType('picoui'); pkg.__path__ = []; sys.modules['picoui'] = pkg\n"
        "sub = types.ModuleType('picoui.skin'); sub.__path__ = []; sys.modules['picoui.skin'] = sub\n"
        "for name, path in (('gradient', %r), ('spec', %r)):\n"
        "    spec = importlib.util.spec_from_file_location('picoui.skin.' + name, path)\n"
        "    mod = importlib.util.module_from_spec(spec); sys.modules['picoui.skin.' + name] = mod\n"
        "    spec.loader.exec_module(mod)\n"
    ) % (GRADIENT_FILE, SPEC_FILE)
    subprocess.run([sys.executable, "-c", loader + code], check=True)


def test_equal_gradients_share_a_cached_tile():
    """Stops compare by value, so an equal gradient built anew hits the cache."""
    again = GradientColorStops((GradientStop(0.0, "#C8C8C8"), GradientStop(1.0, "#787878")))
    assert again == GREY and hash(again) == hash(GREY)
    assert brushed_tile(30, again) is brushed_tile(30, GREY)
