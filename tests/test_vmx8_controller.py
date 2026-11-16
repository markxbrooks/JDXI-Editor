"""SINCO VMX8: map translated from the MiniLab 3 through ElMo's presets."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QObject, QSettings, Signal  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from jdxi_editor.midi.io import controller_settings  # noqa: E402
from jdxi_editor.midi.io.controller_map import (  # noqa: E402
    MINILAB3,
    MINILAB3_FILTER_MAP,
    VMX8,
    VMX8_FILTER_MAP,
    FilterControl,
    detect_profile,
    find_controller_ports,
    profile_by_id,
)
from jdxi_editor.midi.io.controller_settings import (  # noqa: E402
    load_filter_map,
    mapping_group,
    save_filter_map,
)

#: ElMo's presets (elmo/midi/presets.py): ElMo function -> CC on channel 1
ELMO_MINILAB3 = {
    "zoom": 74, "rotation_x": 71, "rotation_y": 76, "rotation_z": 77,
    "translate_x": 18, "translate_y": 19, "connolly_transparency": 85,
    "connolly_probe_radius": 17, "fog_density": 73, "isosurface_level": 75,
    "isosurface_transparency": 86, "fog_near": 114, "fog_far": 115,
    "clip_z": 116, "clip_depth": 117,
}  # fmt: skip
ELMO_VMX8 = {
    "zoom": 32, "rotation_x": 33, "rotation_y": 34, "rotation_z": 35,
    "translate_x": 36, "translate_y": 37, "connolly_transparency": 38,
    "connolly_probe_radius": 39, "fog_density": 40, "isosurface_level": 41,
    "isosurface_transparency": 46, "fog_near": 42, "fog_far": 43,
    "clip_z": 44, "clip_depth": 45,
}  # fmt: skip

VMX8_PORTS = ["JD-Xi", "SINCO VMX8-Private", "SINCO VMX8-Master", "Logic Pro Virtual Out"]


def test_translation_follows_elmo_presets():
    minilab_cc_to_function = {cc: name for name, cc in ELMO_MINILAB3.items()}
    translated = {
        ELMO_VMX8[minilab_cc_to_function[cc]]: control
        for cc, control in MINILAB3_FILTER_MAP.items()
        if cc in minilab_cc_to_function
    }
    assert len(translated) == 8
    assert {cc: VMX8_FILTER_MAP[cc] for cc in translated} == translated


def test_untranslatable_controls_take_free_ccs_of_elmos_block():
    translated_ccs = {32, 33, 34, 35, 36, 37, 38, 39}
    filled = {cc: c for cc, c in VMX8_FILTER_MAP.items() if cc not in translated_ccs}
    assert set(filled) <= set(ELMO_VMX8.values()) - translated_ccs
    assert set(filled.values()) == {
        FilterControl.EFFECT1_LEVEL,
        FilterControl.REVERB_LEVEL,
        FilterControl.ENV_ATTACK,
        FilterControl.ENV_DECAY,
    }


def test_vmx8_drives_the_same_controls_as_the_minilab():
    assert set(VMX8_FILTER_MAP.values()) == set(MINILAB3_FILTER_MAP.values())
    assert len(VMX8_FILTER_MAP) == len(set(VMX8_FILTER_MAP.values()))


def test_only_one_vmx8_port_is_opened():
    # it repeats every message on Private and Master; both would double each move
    assert find_controller_ports(VMX8_PORTS) == ["SINCO VMX8-Private"]
    assert find_controller_ports(["SINCO VMX8-Master"]) == ["SINCO VMX8-Master"]


def test_connected_controller_is_detected():
    assert detect_profile(VMX8_PORTS) is VMX8
    assert detect_profile(["Minilab3 MIDI", "Minilab3 ALV"]) is MINILAB3
    assert detect_profile(["JD-Xi"]) is None
    assert profile_by_id("vmx8") is VMX8
    assert profile_by_id("unknown") is MINILAB3


@pytest.fixture
def store(tmp_path, monkeypatch):
    settings = QSettings(str(tmp_path / "controller.ini"), QSettings.IniFormat)
    monkeypatch.setattr(controller_settings, "_settings", lambda: settings)
    return settings


def test_each_controller_keeps_its_own_learnt_map(store):
    assert load_filter_map(profile=VMX8) == VMX8_FILTER_MAP
    save_filter_map({50: FilterControl.CUTOFF}, profile=VMX8)
    assert load_filter_map(profile=VMX8)[50] is FilterControl.CUTOFF
    assert load_filter_map(profile=MINILAB3) == MINILAB3_FILTER_MAP
    # MiniLab mappings learnt before VMX8 support stay where they were
    assert mapping_group(MINILAB3) == controller_settings.MAPPING_GROUP
    assert mapping_group(VMX8) != mapping_group(MINILAB3)


class StubController(QObject):
    """External controller with a VMX8 plugged in."""

    message_received = Signal(str, object)
    ports_changed = Signal(list)

    def __init__(self, profile):
        super().__init__()
        self.profile = profile
        self.port_name = None
        self.port_names = []
        self.is_open = False

    def available_ports(self):
        return VMX8_PORTS

    def rescan(self):
        return []


class StubRemote:
    def __init__(self, cc_map):
        self.cc_map = dict(cc_map)


@pytest.fixture
def qapp():
    return QApplication.instance() or QApplication([])


def test_dialog_edits_the_connected_controllers_map(qapp, store):
    from jdxi_editor.ui.windows.midi.controller_config import MidiControllerDialog

    remote = StubRemote(load_filter_map(profile=VMX8))
    dialog = MidiControllerDialog(
        external_controller=StubController(VMX8), filter_remote=remote
    )
    try:
        assert dialog.preset_combo.currentData() == "vmx8"
        assert dialog.cc_map == VMX8_FILTER_MAP
        # VMX8 physical controls are not known, so the "Usually" column is blank
        assert dialog.mappings_table.item(0, 1).text() == ""
        dialog.reset_mappings()
        assert remote.cc_map == VMX8_FILTER_MAP

        # browsing the MiniLab map must not change what the VMX8 drives
        dialog.preset_combo.setCurrentIndex(dialog.preset_combo.findData("minilab3"))
        assert dialog.cc_map == MINILAB3_FILTER_MAP
        assert dialog.mappings_table.item(0, 1).text() == "Knob 1"
        dialog.reset_mappings()
        assert remote.cc_map == VMX8_FILTER_MAP
    finally:
        dialog.close()


def test_status_information_is_shown_in_the_window(qapp, store):
    from jdxi_editor.ui.windows.midi.controller_config import MidiControllerDialog

    controller = StubController(VMX8)
    dialog = MidiControllerDialog(external_controller=controller)
    try:
        dialog.show()
        # the text update_status() writes must be inside the window, not orphaned
        assert dialog.information_text.window() is dialog
        assert dialog.information_text.isVisible()
        controller.is_open, controller.port_names = True, ["SINCO VMX8-Private"]
        dialog.update_status()
        assert dialog.status_label.text() == "Connected"
        assert "Listening to: SINCO VMX8-Private" in dialog.information_text.toPlainText()
    finally:
        dialog.close()
