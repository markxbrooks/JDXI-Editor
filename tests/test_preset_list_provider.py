"""The SoundFont preset-list option says why it cannot work instead of
silently keeping the JD-Xi lists. The user's saved settings are not touched."""

import sys

from jdxi_editor.ui.editors.pattern import preset_list_provider as provider


def test_missing_sf2utils_is_reported(monkeypatch, tmp_path):
    sf2 = tmp_path / "x.sf2"
    sf2.write_bytes(b"")
    monkeypatch.setattr(provider, "_sf2_path", lambda: str(sf2))
    monkeypatch.setitem(sys.modules, "sf2utils", None)  # import fails
    problem = provider.soundfont_list_problem()
    assert problem and "sf2utils" in problem


def test_missing_or_unset_soundfont_is_reported(monkeypatch, tmp_path):
    monkeypatch.setitem(sys.modules, "sf2utils", type(sys)("sf2utils"))  # importable
    monkeypatch.setattr(provider, "_sf2_path", lambda: "")
    assert "No SoundFont" in provider.soundfont_list_problem()
    gone = tmp_path / "gone.sf2"
    monkeypatch.setattr(provider, "_sf2_path", lambda: str(gone))
    assert "not found" in provider.soundfont_list_problem()


def test_a_usable_setup_reports_nothing(monkeypatch, tmp_path):
    sf2 = tmp_path / "ok.sf2"
    sf2.write_bytes(b"")
    monkeypatch.setitem(sys.modules, "sf2utils", type(sys)("sf2utils"))
    monkeypatch.setattr(provider, "_sf2_path", lambda: str(sf2))
    assert provider.soundfont_list_problem() is None


def test_soundfont_drum_kits_use_a_valid_bank_select(monkeypatch, tmp_path):
    sf2 = tmp_path / "gm.sf2"
    sf2.write_bytes(b"")
    monkeypatch.setattr(provider, "_use_soundfont_list", lambda: True)
    monkeypatch.setattr(provider, "_sf2_path", lambda: str(sf2))
    monkeypatch.setattr(provider, "_load_sf2_presets", lambda path: [(0, 0, "Piano"), (128, 0, "Standard"), (128, 8, "Room")])
    kits = provider.get_preset_list_for_synth_type("Drums")
    assert [k["name"] for k in kits] == ["Standard", "Room"]
    assert all(0 <= int(k["msb"]) <= 127 and 0 <= int(k["lsb"]) <= 127 for k in kits)
    assert [k["pc"] for k in kits] == ["1", "9"]


def test_an_out_of_range_bank_gives_no_info_instead_of_an_error():
    from jdxi_editor.ui.midi.selection_info import resolve_tone_midi

    bad = [{"id": "001", "name": "Kit", "category": "SoundFont", "msb": "128", "lsb": "0", "pc": "1"}]
    assert resolve_tone_midi(1, bad, channel=9) is None
