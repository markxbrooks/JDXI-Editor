"""Controller profiles are read from JSON, and the user's file overrides them."""

from __future__ import annotations

import json

from jdxi_editor.midi.io.controller_map import (
    BUILTIN_CONFIG_PATH,
    CONFIG_ENV_VAR,
    MINILAB3,
    VMX8,
    FilterControl,
    install_user_config,
    load_controller_profiles,
    user_config_path,
)


def _write(path, controllers):
    path.write_text(json.dumps({"version": 1, "controllers": controllers}))
    return path


def test_builtin_file_defines_both_controllers():
    ids = [p.profile_id for p in load_controller_profiles()]
    assert ids == ["minilab3", "vmx8"]
    assert MINILAB3.sources[FilterControl.ENV_ATTACK] == "Fader 1"
    assert VMX8.single_port and not VMX8.sources


def test_user_file_replaces_and_adds_controllers(tmp_path):
    user = _write(
        tmp_path / "midi_controllers.json",
        [
            {
                "id": "vmx8",
                "label": "My VMX8",
                "port_names": ["VMX8"],
                "single_port": True,
                "mappings": [{"cc": 7, "control": "CUTOFF", "source": "Fader 1"}],
            },
            {
                "id": "nano",
                "label": "nanoKONTROL",
                "port_names": ["nano"],
                "mappings": [{"cc": 0, "control": "RESONANCE"}],
            },
        ],
    )
    profiles = {p.profile_id: p for p in load_controller_profiles(user)}
    assert list(profiles) == ["minilab3", "vmx8", "nano"]
    assert profiles["vmx8"].cc_map == {7: FilterControl.CUTOFF}
    assert profiles["vmx8"].port_names == ("vmx8",)  # matched case-insensitively
    assert profiles["nano"].matches("nanoKONTROL2 SLIDER/KNOB")
    assert profiles["minilab3"].cc_map == MINILAB3.cc_map


def test_bad_entries_and_bad_files_fall_back_to_builtins(tmp_path):
    user = _write(
        tmp_path / "a.json",
        [
            {"id": "x", "port_names": ["x"], "mappings": [{"cc": 1, "control": "NOPE"}]},
            {"id": "y", "port_names": ["y"], "mappings": [{"cc": 200, "control": "CUTOFF"}]},
            {"id": "z", "port_names": ["z"], "mappings": [{"cc": 1, "control": "CUTOFF"}]},
        ],
    )
    assert [p.profile_id for p in load_controller_profiles(user)][-1:] == ["z"]
    broken = tmp_path / "broken.json"
    broken.write_text("{not json")
    assert len(load_controller_profiles(broken)) == 2
    assert len(load_controller_profiles(tmp_path / "missing.json")) == 2


def test_user_copy_is_written_once(tmp_path):
    target = tmp_path / ".jdxi_editor" / "midi_controllers.json"
    assert install_user_config(target) == target
    assert target.read_text() == BUILTIN_CONFIG_PATH.read_text()
    target.write_text("edited")
    install_user_config(target)
    assert target.read_text() == "edited"  # never overwritten


def test_environment_variable_chooses_or_disables_the_user_file(monkeypatch, tmp_path):
    monkeypatch.setenv(CONFIG_ENV_VAR, "")
    assert user_config_path() is None and install_user_config() is None
    monkeypatch.setenv(CONFIG_ENV_VAR, str(tmp_path / "c.json"))
    assert user_config_path() == tmp_path / "c.json"
    monkeypatch.delenv(CONFIG_ENV_VAR)
    assert user_config_path().parts[-2:] == (".jdxi_editor", "midi_controllers.json")


def test_older_user_copy_keeps_the_builtin_transport_buttons(tmp_path):
    """A copy written before transport support overrides only what it lists."""
    builtin = json.loads(BUILTIN_CONFIG_PATH.read_text())
    for entry in builtin["controllers"]:
        entry.pop("transport")
    entry["mappings"] = [{"cc": 7, "control": "CUTOFF"}]  # the VMX8 entry, edited
    user = tmp_path / "midi_controllers.json"
    user.write_text(json.dumps(builtin))
    vmx8 = {p.profile_id: p for p in load_controller_profiles(user)}["vmx8"]
    assert vmx8.cc_map == {7: FilterControl.CUTOFF}
    assert vmx8.transport == VMX8.transport
    assert {(t.kind, t.number) for t in vmx8.transport} >= {("cc", 52), ("note", 94)}


def test_bad_transport_entry_skips_only_that_controller(tmp_path):
    user = _write(
        tmp_path / "t.json",
        [{"id": "vmx8", "transport": [{"action": "EJECT", "cc": 60}]}],
    )
    ids = [p.profile_id for p in load_controller_profiles(user)]
    assert ids == ["minilab3"]
