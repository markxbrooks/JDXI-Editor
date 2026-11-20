"""
A skin from a TOML file (picoui.skin.loader): what a user writes without
code becomes a skin that paints, and a mistake says where it is.
"""

import os
import re

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor, QImage, QPainter
from PySide6.QtWidgets import QApplication

import picoui.skin.loader as loader
from picoui.skin import Skin, SkinFileError, load_skin_file, skin_from_data
from picoui.skin.spec import FaceSpec, GradientFill, Rule

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib

_APP = QApplication.instance() or QApplication([])

#: The example in the loader's own documentation, so it stays true
EXAMPLE = re.search(r"Example file::\n\n(.*?)\n\nA palette table", loader.__doc__, re.S).group(1)
EXAMPLE = "\n".join(line[4:] for line in EXAMPLE.splitlines())


def _paint(skin, width=300, height=120) -> QImage:
    image = QImage(width, height, QImage.Format.Format_ARGB32)
    image.fill(QColor(255, 0, 255))
    painter = QPainter(image)
    skin.paint(painter, QRectF(0, 0, width, height))
    painter.end()
    return image


def test_the_documented_example_loads_and_paints(tmp_path):
    path = tmp_path / "mine.toml"
    path.write_text(EXAMPLE)
    skin = load_skin_file(path)
    assert isinstance(skin, Skin)
    assert (skin.skin_id, skin.label, skin.ear_width) == ("my_tr1000", "My TR-1000", 14)
    assert skin.chassis.accent == "#E64A32"  # "$accent"
    assert skin.lcd.text == "#F0EEE8"
    rule, steps = skin.face.decorations
    assert rule.color == (230, 74, 50, 255)
    assert steps.background == (53, 56, 59, 255) and steps.lights.on == (240, 68, 48, 255)
    assert skin.ear.material.stops.stops[0].color == (53, 56, 59, 255)  # "$cheek_light" in a gradient
    image = _paint(skin)
    assert image.pixelColor(150, 60).name() != "#ff00ff"  # the face is painted
    assert image.pixelColor(150, 2).name() == "#e64a32"  # the accent rule


def test_a_file_can_start_from_a_skin_and_change_only_some_of_it():
    class Base(Skin):
        skin_id, label, ear_width = "base", "Base", 12
        face = FaceSpec(GradientFill(loader.WALNUT), (Rule("top", 1, "#FFFFFF"),), rim="#000000")

    data = tomllib.loads('''
        [skin]
        id = "tweaked"
        based_on = "base"
        bezel = 4
        [chassis]
        accent = "#00FF00"
        [face]
        rim = [255, 0, 0]
    ''')
    skin = skin_from_data(data, bases={"base": Base()})
    assert isinstance(skin, Base) and skin.skin_id == "tweaked"
    assert skin.bezel == 4 and skin.ear_width == 12  # changed, and kept
    assert skin.chassis.accent == "#00FF00"
    assert skin.chassis.body == Skin.chassis.body  # the rest of the chassis kept
    assert skin.face.rim == (255, 0, 0, 255)
    assert skin.face.decorations == Base.face.decorations  # the rest of the face kept


def test_simple_settings_reach_the_skins_own_init():
    class Coloured(Skin):
        skin_id = "coloured"
        body = "#000000"

        def __init__(self):
            self.face = FaceSpec(GradientFill(loader.GradientColorStops((
                loader.GradientStop(0, self.body), loader.GradientStop(1, self.body)))))

    data = tomllib.loads('[skin]\nid = "blue"\nbased_on = "coloured"\nbody = "#0000FF"\n')
    skin = skin_from_data(data, bases={"coloured": Coloured()})
    assert skin.face.material.stops.stops[0].color == (0, 0, 255, 255)


def test_application_settings_and_tables_can_be_added():
    data = tomllib.loads('''
        [skin]
        id = "x"
        meter = "needles"
        [lanes]
        cards = true
        backing = { type = "wood", stops = "teak" }
    ''')
    skin = skin_from_data(
        data,
        attributes={"meter": str.upper},
        sections={"lanes": lambda table, r: (table["cards"], r.material(table["backing"], "lanes.backing"))},
    )
    assert skin.meter == "NEEDLES"
    assert skin.lanes[0] is True and skin.lanes[1].stops == loader.TEAK


@pytest.mark.parametrize(
    "text, message",
    [
        ('[skin]\nlabel = "no id"', "skin.id"),
        ('[skin]\nid = "x"\n[face]\nmaterial = { type = "plush" }', "face.material: type 'plush'"),
        ('[skin]\nid = "x"\n[face]\nrim = "red"', "face.rim: Not a colour"),
        ('[skin]\nid = "x"\n[face]\nrim = "$missing"', "no colour '$missing'"),
        ('[skin]\nid = "x"\n[[face.decorations]]\ntype = "rule"\nedge = "top"\noffset = 1\ncolour = "#FFFFFF"',
         "face.decorations[0]: unknown colour"),
        ('[skin]\nid = "x"\n[ear]\nmaterial = { type = "wood", stops = "oak" }', "no gradient 'oak'"),
        ('[skin]\nid = "x"\nbased_on = "nope"', "skin.based_on: no skin 'nope'"),
        ('[skin]\nid = "x"\near_width = "wide"', "skin.ear_width: expected int"),
        ('[skin]\nid = "x"\nshininess = 3', "skin.shininess: not a setting"),
        ('[skin]\nid = "x"\n[sounds]\nclick = 1', "unknown table sounds"),
        ('[skin]\nid = "x"\n[gradients]\nflat = [[0.0, "#000000"]]', "gradients.flat: A gradient needs at least two stops"),
    ],
)
def test_mistakes_say_where_they_are(text, message):
    with pytest.raises(SkinFileError, match=re.escape(message)):
        skin_from_data(tomllib.loads(text))


def test_a_file_that_is_not_toml_is_named(tmp_path):
    path = tmp_path / "broken.toml"
    path.write_text("[skin\nid = 1")
    with pytest.raises(SkinFileError, match="broken.toml: not valid TOML"):
        load_skin_file(path)


def test_a_stored_choice_waits_for_a_skin_loaded_later():
    from picoui.skin import SkinRegistry

    class Store:
        def load(self):
            return "later"

        def save(self, skin_id):
            pass

    class Plain(Skin):
        skin_id = "plain"

    registry = SkinRegistry([Plain()], store=Store())
    assert registry.active().skin_id == "plain"  # not there yet: the default
    later = skin_from_data({"skin": {"id": "later"}})
    registry.register(later)
    assert registry.active() is later


def test_a_spec_written_as_a_table_loads_as_the_same_spec():
    from picoui.skin.spec import Band, Grille, Keyboard, PatchCord, StepButtons, StepLights, Wash
    from picoui.skin.writer import dumps, spec_table

    resolver = loader.Resolver({}, loader.BUILTIN_GRADIENTS)
    decorations = (
        Rule("top", 2.5, (230, 74, 50, 128)),
        Band("bottom", 3, ("#111111", "#222222")),
        Keyboard(10, 3, "#F0F0E8", "#101010"),
        StepButtons(6, 16, ("#E6E3DB",), "#35383B", group=4, lights=StepLights(2, "#F04430", "#351914")),
        Wash(loader.GradientColorStops((loader.GradientStop(0, (0, 0, 0, 0)), loader.GradientStop(1, (0, 0, 0, 90))))),
    )
    details = (PatchCord(("#FF0000", "#0000FF")), Grille("#333333", "#000000", "#555555"))
    assert spec_table(decorations[0]) == {"type": "rule", "edge": "top", "offset": 2.5, "color": [230, 74, 50, 128]}
    text = dumps({"face": {"decorations": [spec_table(d) for d in decorations]},
                  "ear": {"details": [spec_table(d) for d in details]}})
    data = tomllib.loads(text)
    assert resolver.field("decorations", data["face"]["decorations"], "face") == decorations
    assert resolver.field("details", data["ear"]["details"], "ear") == details
