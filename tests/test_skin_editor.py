"""The Skin Editor: make a skin from another, see it, save it as a user skin."""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402
from PySide6.QtWidgets import QApplication, QMessageBox  # noqa: E402

from picoui.skin.loader import read_skin_file  # noqa: E402
from jdxi_editor.ui.style.rack_skin import REGISTRY, MeterStyle, set_active_skin  # noqa: E402
from jdxi_editor.ui.style.user_skins import load_user_skin  # noqa: E402
from jdxi_editor.ui.windows.skin.editor import SkinEditorWindow  # noqa: E402

EXAMPLE = Path(__file__).resolve().parents[1] / "doc" / "skins" / "tr1000_user.toml"


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def editor(qapp, tmp_path, monkeypatch):
    """A Skin Editor saving into a scratch folder, starting from the TR-909."""
    set_active_skin("tr909", remember=False)
    before = set(REGISTRY.skins)
    worn = []
    saved = []
    window = SkinEditorWindow(
        wear=lambda skin, remember: worn.append((skin.skin_id, remember)),
        saved=saved.append,
        folder=tmp_path,
    )
    window.worn, window.saved_skins = worn, saved
    monkeypatch.setattr(QMessageBox, "warning", lambda *a, **k: None)
    yield window
    window._trying = False
    window.close()
    for skin_id in set(REGISTRY.skins) - before:  # leave the real menu as it was
        REGISTRY.skins.pop(skin_id)
    set_active_skin("glossy_black", remember=False)


def test_a_new_skin_starts_from_the_skin_being_worn(editor):
    tables = editor.tables()
    assert tables["skin"] == {"id": "my_tr_909", "label": "My TR-909", "based_on": "tr909"}
    assert editor.based_on.currentData() == "tr909"
    assert editor.preview.panel.skin.face == REGISTRY.get("tr909").face
    assert 'based_on = "tr909"' in editor.toml.toPlainText()
    # inherited values are shown, and have nothing to reset
    assert editor._color_buttons[("chassis", "accent")].color() == "#2C6AB0"
    assert not editor._resets[("chassis", "accent")].isEnabled()


def test_a_changed_colour_is_written_shown_and_can_be_reset(editor):
    editor._edited("chassis", "accent", "#E64A32")
    editor._build()
    assert editor.tables()["chassis"] == {"accent": "#E64A32"}
    assert editor.preview.panel.skin.chassis.accent == "#E64A32"
    assert editor._resets[("chassis", "accent")].isEnabled()

    editor._reset("chassis", "accent")
    editor._build()
    assert "chassis" not in editor.tables()
    assert editor.preview.panel.skin.chassis.accent == "#2C6AB0"


def test_repainting_the_panel_replaces_only_its_finish(editor):
    editor.repaint_face.setChecked(True)
    editor._build()
    material = editor.tables()["face"]["material"]
    assert material["type"] == "gradient" and len(material["stops"]) == 3
    face = editor.preview.panel.skin.face
    assert face.decorations == REGISTRY.get("tr909").face.decorations  # the steps stay
    editor.repaint_face.setChecked(False)
    editor._build()
    assert "face" not in editor.tables()


def test_meters_lanes_and_sizes(editor):
    editor.meter.setCurrentIndex(editor.meter.findData("vintage_vu"))
    editor.lanes.setCurrentIndex(2)  # cards on walnut
    editor._spins["ear_width"].setValue(22)
    editor._build()
    skin = editor.preview.panel.skin
    assert skin.meter == MeterStyle.VINTAGE_VU
    assert skin.lanes.cards
    assert skin.ear_width == 22 and editor.tables()["skin"]["ear_width"] == 22


def test_a_mistake_is_shown_and_the_last_good_preview_kept(editor):
    good = editor.preview.panel.skin
    editor._table("face")["rim"] = "not a colour"
    editor._build()
    assert "face.rim" in editor.status.text()
    assert editor.preview.panel.skin is good


def test_a_built_in_id_cannot_be_saved(editor, tmp_path):
    editor._id_edited("tr808")
    editor._build()
    assert "built-in" in editor.status.text()
    assert editor.save() is None
    assert not list(tmp_path.iterdir())


def test_saving_writes_a_file_offers_the_skin_and_wears_it(editor, tmp_path):
    editor._label_edited("Blue 909")
    editor._edited("chassis", "accent", "#2F6FD0")
    editor._build()
    path = editor.save()
    assert path == tmp_path / "blue_909.toml"
    assert read_skin_file(path) == editor.tables()
    assert load_user_skin(path).chassis.accent == "#2F6FD0"
    assert REGISTRY.get("blue_909").label == "Blue 909"
    assert [skin.skin_id for skin in editor.saved_skins] == ["blue_909"]


def test_an_opened_file_keeps_what_the_form_does_not_show(editor, tmp_path):
    editor.open_file(EXAMPLE)
    editor._edited("chassis", "accent", "#00AA88")
    editor._build()
    tables = editor.tables()
    original = read_skin_file(EXAMPLE)
    assert tables["face"]["decorations"] == original["face"]["decorations"]
    assert tables["colors"] == original["colors"] and tables["gradients"] == original["gradients"]
    assert tables["chassis"]["accent"] == "#00AA88"
    assert editor.based_on.currentData() is None  # a complete skin


def test_a_skin_tried_on_comes_off_when_the_editor_closes_unsaved(editor):
    editor._edited("chassis", "accent", "#E64A32")
    editor._build()
    editor._try_on()
    editor.close()
    assert editor.worn == [("my_tr_909", False), ("tr909", False)]
