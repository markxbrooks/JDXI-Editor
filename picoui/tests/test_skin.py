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
    LcdPalette,
    Skin,
    SkinRegistry,
    default_registry,
    set_default_registry,
)
from picoui.skin.textures import WALNUT, brushed_tile, wood_tile
from picoui.skin.widgets import RackEars, RackPanel

_APP = QApplication.instance() or QApplication([])


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


def test_textures_are_cached_and_the_same_every_time():
    assert wood_tile(40, WALNUT) is wood_tile(40, WALNUT)
    first = brushed_tile(30, ((0.0, 200, 200, 200), (1.0, 120, 120, 120))).toImage()
    brushed_tile.cache_clear()
    again = brushed_tile(30, ((0.0, 200, 200, 200), (1.0, 120, 120, 120))).toImage()
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
