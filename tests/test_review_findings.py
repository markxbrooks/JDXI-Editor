"""Findings of JD-Xi Studio's code review of 2026-11-16, each with the case that showed it."""

from __future__ import annotations

import io
import zipfile
from pathlib import Path
from unittest.mock import Mock

import mido
from PySide6.QtWidgets import QApplication

from jdxi_editor.midi.io.synth_memory import SynthMemory, build_dt1
from jdxi_editor.midi.sysex.patch_bundle import (
    BUNDLE_MIDI_NAME,
    extract_bundle_midi,
    write_memory_sections,
)

APP = QApplication.instance() or QApplication([])
MIDI = b"MThd\x00\x00\x00\x06\x00\x00\x00\x01\x00\x60MTrk\x00\x00\x00\x04\x00\xff\x2f\x00"


def _bundle(name: str) -> zipfile.ZipFile:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as z:
        z.writestr("jdxi_tone_data_19420000.json", "{}")
        z.writestr(name, MIDI)
    buffer.seek(0)
    return zipfile.ZipFile(buffer)


# 1. A .msz bundle cannot write its MIDI file outside the temporary folder (zip slip)
def test_bundle_midi_stays_in_the_folder(tmp_path):
    folder = tmp_path / "temp" / "bundle"
    for name in ("../../evil.mid", "/tmp/evil.mid", "..\\..\\evil.mid", "C:/evil.mid", "song.mid"):
        written = extract_bundle_midi(_bundle(name), folder)
        assert written == (folder / BUNDLE_MIDI_NAME).resolve()
        assert written.read_bytes() == MIDI
    outside = [p for p in tmp_path.rglob("*.mid") if p.parent.resolve() != folder.resolve()]
    assert outside == []
    assert not Path("/tmp/evil.mid").exists() or Path("/tmp/evil.mid").stat().st_size != len(MIDI)


def test_a_bundle_without_midi_gives_none(tmp_path):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as z:
        z.writestr("jdxi_tone_data_19420000.json", "{}")
    buffer.seek(0)
    assert extract_bundle_midi(zipfile.ZipFile(buffer), tmp_path) is None


# 2. After a partial read only the sections it confirmed come from the memory mirror
def test_only_confirmed_sections_come_from_memory(tmp_path):
    memory = SynthMemory()
    memory.record_dt1(build_dt1([0x19, 0x42, 0x00, 0x00], [1] * 0x40))  # read now
    memory.record_dt1(build_dt1([0x18, 0x00, 0x02, 0x00], [2] * 0x11))  # from before
    (tmp_path / "all").mkdir()
    (tmp_path / "some").mkdir()
    everything = write_memory_sections(memory, tmp_path / "all")
    assert everything == {"19420000", "18000200"}
    confirmed = write_memory_sections(memory, tmp_path / "some", only={"19420000"})
    assert confirmed == {"19420000"}
    assert [p.name for p in (tmp_path / "some").iterdir()] == ["jdxi_tone_data_19420000.json"]


def test_a_program_chosen_on_the_jdxi_clears_the_memory_mirror():
    from jdxi_editor.midi.io.device import device_for
    from jdxi_editor.midi.io.helper import MidiIOHelper

    helper = MidiIOHelper()
    memory = device_for(helper).memory
    memory.record_dt1(build_dt1([0x18, 0x00, 0x02, 0x00], [2] * 0x11))
    assert memory.sections()
    helper._handle_midi_message(mido.Message("program_change", channel=15, program=3))
    assert memory.sections() == []


# 3. A connection that did not open is not reported as made
def test_half_a_connection_is_not_a_connection(monkeypatch):
    from jdxi_editor.midi.io.helper import MidiIOHelper

    helper = MidiIOHelper()
    midi_in = Mock()
    midi_in.is_port_open.return_value = True
    monkeypatch.setattr(helper, "midi_in", midi_in, raising=False)
    monkeypatch.setattr(helper, "open_input_port", lambda name: True)
    monkeypatch.setattr(helper, "open_output_port", lambda name: False)
    identify = Mock()
    monkeypatch.setattr(helper, "identify_device", identify)
    monkeypatch.setattr(helper, "close_ports", lambda: None)
    assert helper.set_midi_ports("JD-Xi", "JD-Xi") is False
    midi_in.close_port.assert_called_once()  # the input that did open is closed
    assert helper.connect_port_names("JD-Xi", "JD-Xi") is False
    identify.assert_not_called()
    assert helper.reconnect_port_names("JD-Xi", "JD-Xi") is False
    monkeypatch.setattr(helper, "get_input_ports", lambda: ["JD-Xi"])
    monkeypatch.setattr(helper, "get_output_ports", lambda: ["JD-Xi"])
    assert helper.auto_connect_jdxi() is False


# 4. A malformed message does not raise again while its error is logged
def test_a_malformed_message_is_logged_not_raised(monkeypatch):
    from jdxi_editor.midi.io import input_handler
    from jdxi_editor.midi.io.helper import MidiIOHelper

    errors = []
    monkeypatch.setattr(input_handler.log, "error", lambda *a, **k: errors.append(k.get("message", a[0] if a else "")))
    helper = MidiIOHelper()
    helper.midi_callback(([0x90, 60], 0.0, "extra"), None)  # not (bytes, delta): unpacking fails
    assert errors and "Error in MIDI handler" in errors[0]
