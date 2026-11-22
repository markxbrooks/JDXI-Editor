"""User skins: TOML files in ~/.jdxi_editor/skins, offered beside the built-in skins."""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402
from PySide6.QtCore import QRectF  # noqa: E402
from PySide6.QtGui import QColor, QImage, QPainter  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from picoui.skin import BrushedFill, SkinFileError, SkinRegistry, WoodFill  # noqa: E402
from jdxi_editor.ui.style.rack_skin import (  # noqa: E402
    REGISTRY,
    JDXiSkin,
    MeterStyle,
    Tr909Skin,
    Tr1000Skin,
)
from jdxi_editor.ui.style.user_skins import (  # noqa: E402
    MINI_WOOD,
    load_user_skin,
    load_user_skins,
)

EXAMPLE = Path(__file__).resolve().parents[1] / "doc" / "skins" / "tr1000_user.toml"


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def registry():
    """A copy of the editor's skins, so a test never adds to the real menu."""
    return SkinRegistry(list(REGISTRY.skins.values()), default_id="glossy_black")


def _paint(skin) -> QImage:
    image = QImage(400, 160, QImage.Format.Format_ARGB32)
    image.fill(QColor(255, 0, 255))
    painter = QPainter(image)
    skin.paint(painter, QRectF(0.5, 0.5, 399, 159))
    painter.end()
    return image


def test_the_example_file_is_the_tr1000(qapp, registry):
    """The documented example describes a real skin completely: the same
    data, and the same pixels, as the built-in TR-1000 written in code."""
    skin = load_user_skin(EXAMPLE, registry)
    built_in = Tr1000Skin()
    assert isinstance(skin, JDXiSkin)
    assert (skin.lcd, skin.foreground, skin.chassis) == (built_in.lcd, built_in.foreground, built_in.chassis)
    assert (skin.face, skin.ear) == (built_in.face, built_in.ear)
    assert skin.meter == MeterStyle.BARS
    assert _paint(skin) == _paint(built_in)


def test_skins_in_the_folder_are_offered_and_bad_ones_skipped(qapp, registry, tmp_path):
    (tmp_path / "a_blue_909.toml").write_text(
        '[skin]\nid = "blue_909"\nlabel = "TR-909 Blue"\nbased_on = "tr909"\n'
        '[chassis]\naccent = "#2F6FD0"\n'
    )
    (tmp_path / "b_broken.toml").write_text('[skin]\nid = "broken"\n[face]\nrim = "red"\n')
    (tmp_path / "c_impostor.toml").write_text('[skin]\nid = "tr808"\n')
    (tmp_path / "notes.txt").write_text("not a skin")

    loaded = load_user_skins(tmp_path, registry)

    assert [skin.skin_id for skin in loaded] == ["blue_909"]
    blue = registry.get("blue_909")
    assert isinstance(blue, Tr909Skin) and blue.label == "TR-909 Blue"
    assert blue.chassis.accent == "#2F6FD0"
    assert blue.face == Tr909Skin.face  # everything else is the 909's
    assert "broken" not in registry.skins
    assert type(registry.get("tr808")).__name__ == "Tr808Skin"  # not replaced


def test_a_missing_folder_offers_nothing(registry, tmp_path):
    assert load_user_skins(tmp_path / "none", registry) == []


def test_meter_and_lanes(qapp, registry, tmp_path):
    path = tmp_path / "vintage.toml"
    path.write_text(
        '[skin]\nid = "vintage"\nbased_on = "glossy_black"\nmeter = "vintage_vu"\n'
        '[lanes]\ncards = true\nbacking = { type = "wood", stops = "mini_wood" }\n'
    )
    skin = load_user_skin(path, registry)
    assert skin.meter == MeterStyle.VINTAGE_VU
    assert skin.lanes.cards and skin.lanes.backing == WoodFill(MINI_WOOD)

    path.write_text(
        '[skin]\nid = "metal"\n[lanes]\ncards = true\n'
        'backing = { type = "brushed", stops = "aluminium", grain = 4, coverage = 0.35 }\n'
    )
    assert isinstance(load_user_skin(path, registry).lanes.backing, BrushedFill)


@pytest.mark.parametrize(
    "text, message",
    [
        ('[skin]\nid = "x"\nmeter = "lava_lamp"', 'skin.meter: meter \'lava_lamp\' is not one of "bars"'),
        ('[skin]\nid = "x"\n[lanes]\ncards = "yes"', "lanes.cards: expected true or false"),
        ('[skin]\nid = "x"\n[lanes]\nwood = 1', "lanes: unknown wood"),
    ],
)
def test_the_editors_own_settings_say_what_is_wrong(registry, tmp_path, text, message):
    path = tmp_path / "x.toml"
    path.write_text(text)
    with pytest.raises(SkinFileError, match=message):
        load_user_skin(path, registry)


def test_a_remembered_user_skin_is_worn_once_it_is_loaded(qapp, tmp_path):
    class Store:
        def load(self):
            return "mine"

        def save(self, skin_id):
            pass

    registry = SkinRegistry([JDXiSkin()], default_id="glossy_black", store=Store())
    assert registry.active().skin_id == "glossy_black"  # asked for before loading
    (tmp_path / "mine.toml").write_text('[skin]\nid = "mine"\nbased_on = "glossy_black"\n')
    load_user_skins(tmp_path, registry)
    assert registry.active().skin_id == "mine"
