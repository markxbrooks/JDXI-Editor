"""Stored controller mappings, and the MIDI Controller dialog that edits them."""

from __future__ import annotations

import os

import mido
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QObject, QSettings, Signal  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from jdxi_editor.midi.io import controller_settings  # noqa: E402
from jdxi_editor.midi.io.controller_map import (  # noqa: E402
    MINILAB3_FILTER_MAP,
    FilterControl,
)
from jdxi_editor.midi.io.controller_settings import (  # noqa: E402
    clear_filter_map,
    load_filter_map,
    save_filter_map,
)
from jdxi_editor.ui.windows.midi.controller_config import (  # noqa: E402
    AUTOMATIC_PORTS,
    MidiControllerDialog,
)


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def store(tmp_path, monkeypatch):
    """A settings store of its own, so the user's real settings are untouched."""
    settings = QSettings(str(tmp_path / "controller.ini"), QSettings.IniFormat)
    monkeypatch.setattr(controller_settings, "_settings", lambda: settings)
    return settings


class StubController(QObject):
    """An ExternalControllerInput that needs no hardware."""

    message_received = Signal(str, object)
    control_changed = Signal(int, int, int)
    ports_changed = Signal(list)

    def __init__(self, ports=("Minilab3 MIDI", "JD-Xi")):
        super().__init__()
        self.ports = list(ports)
        self.port_names: list[str] = []
        self.port_name = None
        self.connected_to = None

    @property
    def is_open(self):
        return bool(self.port_names)

    def available_ports(self):
        return list(self.ports)

    def auto_connect(self):
        self.port_names = [p for p in self.ports if "minilab" in p.lower()]
        self.port_name = next(iter(self.port_names), None)
        self.connected_to = AUTOMATIC_PORTS
        return self.is_open

    def connect_port(self, name):
        self.port_names = [name]
        self.port_name = name
        self.connected_to = name
        return True

    def rescan(self):
        return self.port_names

    def close(self):
        self.port_names = []
        self.port_name = None


class StubRemote:
    """Stands in for FilterRemote; only its cc_map matters here."""

    def __init__(self, cc_map):
        self.cc_map = dict(cc_map)


@pytest.fixture
def dialog(qapp, store):
    controller = StubController()
    remote = StubRemote(load_filter_map())
    window = MidiControllerDialog(external_controller=controller, filter_remote=remote)
    window.controller = controller
    window.remote = remote
    yield window
    window.close()


# ----------------------------------------------------------------------
# Stored mappings
# ----------------------------------------------------------------------
def test_defaults_are_used_when_nothing_is_stored(store):
    assert load_filter_map() == MINILAB3_FILTER_MAP


def test_a_saved_map_is_read_back(store):
    save_filter_map({102: FilterControl.CUTOFF, 103: FilterControl.RESONANCE})
    loaded = load_filter_map()
    assert loaded[102] is FilterControl.CUTOFF
    assert loaded[103] is FilterControl.RESONANCE


def test_controls_not_saved_keep_their_default(store):
    save_filter_map({102: FilterControl.CUTOFF})
    loaded = load_filter_map()
    # CUTOFF was learnt; the rest still work off the built-in map
    assert loaded[102] is FilterControl.CUTOFF
    assert 74 not in loaded
    assert loaded[71] is FilterControl.RESONANCE


def test_clearing_restores_the_defaults(store):
    save_filter_map({102: FilterControl.CUTOFF})
    clear_filter_map()
    assert load_filter_map() == MINILAB3_FILTER_MAP


def test_an_unusable_stored_value_is_ignored(store):
    # The settings file can be edited by hand
    store.setValue(f"{controller_settings.MAPPING_GROUP}/CUTOFF", "not a number")
    store.setValue(f"{controller_settings.MAPPING_GROUP}/RESONANCE", 999)
    loaded = load_filter_map()
    assert loaded[74] is FilterControl.CUTOFF
    assert loaded[71] is FilterControl.RESONANCE


# ----------------------------------------------------------------------
# The dialog
# ----------------------------------------------------------------------
def test_the_dialog_has_the_three_tabs(dialog):
    tabs = [dialog.tabs.tabText(i) for i in range(dialog.tabs.count())]
    assert tabs == ["Connection", "Monitor", "Mappings"]


def test_every_filter_control_has_a_row(dialog):
    assert dialog.mappings_table.rowCount() == len(list(FilterControl))
    assert dialog.cc_for(FilterControl.CUTOFF) == 74


def test_ports_are_listed_with_automatic_first(dialog):
    assert dialog.port_combo.itemText(0) == AUTOMATIC_PORTS
    assert dialog.port_combo.findText("Minilab3 MIDI") > 0


def test_connecting_and_disconnecting(dialog):
    dialog.connect_controller()
    assert dialog.controller.connected_to == AUTOMATIC_PORTS
    assert dialog.status_label.text() == "Connected"

    dialog.port_combo.setCurrentIndex(dialog.port_combo.findText("Minilab3 MIDI"))
    dialog.connect_controller()
    assert dialog.controller.connected_to == "Minilab3 MIDI"

    dialog.disconnect_controller()
    assert dialog.status_label.text() == "Not connected"


def test_learning_takes_the_next_cc(dialog):
    dialog.start_learn(FilterControl.CUTOFF)
    dialog.controller.message_received.emit(
        "Minilab3 MIDI", mido.Message("control_change", control=102, value=55)
    )
    assert dialog.cc_for(FilterControl.CUTOFF) == 102
    # the control's old CC is released, so that knob no longer drives it
    assert 74 not in dialog.cc_map
    # and it reaches the running remote and the settings
    assert dialog.remote.cc_map[102] is FilterControl.CUTOFF
    assert load_filter_map()[102] is FilterControl.CUTOFF


def test_learning_stops_after_one_message(dialog):
    dialog.start_learn(FilterControl.CUTOFF)
    dialog.controller.message_received.emit(
        "Minilab3 MIDI", mido.Message("control_change", control=102, value=55)
    )
    dialog.controller.message_received.emit(
        "Minilab3 MIDI", mido.Message("control_change", control=103, value=7)
    )
    assert dialog.cc_for(FilterControl.CUTOFF) == 102


def test_learning_a_cc_another_control_uses_takes_it_over(dialog):
    # One CC must not drive two sliders at once
    dialog.start_learn(FilterControl.CUTOFF)
    dialog.controller.message_received.emit(
        "Minilab3 MIDI", mido.Message("control_change", control=71, value=5)
    )
    assert dialog.cc_map[71] is FilterControl.CUTOFF
    assert dialog.cc_for(FilterControl.RESONANCE) is None


def test_cancelling_a_learn(dialog):
    dialog.start_learn(FilterControl.CUTOFF)
    dialog.cancel_learn()
    dialog.controller.message_received.emit(
        "Minilab3 MIDI", mido.Message("control_change", control=102, value=55)
    )
    assert dialog.cc_for(FilterControl.CUTOFF) == 74


def test_non_cc_messages_are_logged_but_never_learnt(dialog):
    dialog.start_learn(FilterControl.CUTOFF)
    dialog.controller.message_received.emit(
        "Minilab3 MIDI", mido.Message("note_on", note=60, velocity=100)
    )
    assert dialog.cc_for(FilterControl.CUTOFF) == 74
    assert "note_on" in dialog.monitor_text.toPlainText()


def test_the_monitor_shows_the_port_and_the_last_cc(dialog):
    dialog.controller.message_received.emit(
        "Minilab3 ALV", mido.Message("control_change", control=82, value=9)
    )
    text = dialog.monitor_text.toPlainText()
    assert "[Minilab3 ALV]" in text
    assert "control=82" in text
    assert "82" in dialog.last_cc_label.text()


def test_resetting_restores_the_built_in_map(dialog):
    dialog.assign_cc(FilterControl.CUTOFF, 102)
    dialog.reset_mappings()
    assert dialog.cc_map == MINILAB3_FILTER_MAP
    assert dialog.remote.cc_map == MINILAB3_FILTER_MAP
    assert load_filter_map() == MINILAB3_FILTER_MAP


def test_every_control_has_one_table_row_and_sources_match_defaults():
    """The Mappings table covers each control once; a source means a default CC."""
    from jdxi_editor.midi.io.controller_map import MINILAB3_FILTER_MAP, FilterControl
    from jdxi_editor.ui.windows.midi.controller_config import (
        CONTROL_SOURCES,
        CONTROL_SPECS,
    )

    controls = [spec.control for spec in CONTROL_SPECS]
    assert sorted(controls, key=lambda c: c.name) == sorted(
        FilterControl, key=lambda c: c.name
    )
    assert set(CONTROL_SOURCES) == set(MINILAB3_FILTER_MAP.values())
    assert len(set(CONTROL_SOURCES.values())) == len(CONTROL_SOURCES)
