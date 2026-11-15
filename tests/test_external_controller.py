"""The controller input listens to every port a controller exposes."""

from __future__ import annotations

import os

import mido
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402

from jdxi_editor.midi.io.controller_map import (  # noqa: E402
    find_controller_port,
    find_controller_ports,
)
from jdxi_editor.midi.io.external_controller import (  # noqa: E402
    ExternalControllerInput,
)

MINILAB_PORTS = [
    "JD-Xi",
    "Minilab3 MIDI",
    "Minilab3 DIN THRU",
    "Minilab3 MCU/HUI",
    "Minilab3 ALV",
    "Logic Pro Virtual Out",
]


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


class StubController(ExternalControllerInput):
    """Controller input with the ports it sees, and opening them, stubbed out."""

    def __init__(self, ports: list[str]) -> None:
        super().__init__()
        self.ports = list(ports)
        self.opened: list[str] = []
        self.closed: list[str] = []

    def available_ports(self) -> list[str]:
        return list(self.ports)

    def connect_ports(self, port_names: list[str]) -> bool:
        # Keep tests synchronous; the real class staggers opens on a QTimer.
        for name in self.port_names:
            if name not in port_names:
                self._close_port(name)
        for name in port_names:
            self._open_port(name, install_callback=False)
        self.port_name = next(iter(self._inputs), None)
        self._ports_to_open = []
        return self.is_open

    def _open_port(self, port_name: str, *, install_callback: bool = True) -> bool:
        if port_name in self._inputs:
            return True
        self.opened.append(port_name)
        self._inputs[port_name] = object()
        self._parsers[port_name] = mido.Parser()
        return True

    def _install_callback(self, port_name: str) -> None:
        return

    def _close_port(self, port_name: str) -> None:
        self.closed.append(port_name)
        self._inputs.pop(port_name, None)
        self._parsers.pop(port_name, None)
        if self.port_name == port_name:
            self.port_name = next(iter(self._inputs), None)


def test_every_controller_port_is_found_main_first():
    # Which port carries the knobs depends on the MiniLab's mode, so all of
    # them are listened to rather than guessed at.
    assert find_controller_ports(MINILAB_PORTS) == [
        "Minilab3 MIDI",
        "Minilab3 DIN THRU",
        "Minilab3 MCU/HUI",
        "Minilab3 ALV",
    ]


def test_no_controller_yields_no_ports():
    assert find_controller_ports(["JD-Xi", "Logic Pro Virtual Out"]) == []
    assert find_controller_port(["JD-Xi"]) is None


def test_auto_connect_opens_all_controller_ports(qapp):
    controller = StubController(MINILAB_PORTS)
    assert controller.auto_connect() is True
    assert controller.opened == [
        "Minilab3 MIDI",
        "Minilab3 DIN THRU",
        "Minilab3 MCU/HUI",
        "Minilab3 ALV",
    ]
    assert controller.port_name == "Minilab3 MIDI"
    assert controller.is_open is True


def test_auto_connect_without_a_controller(qapp):
    controller = StubController(["JD-Xi"])
    assert controller.auto_connect() is False
    assert controller.is_open is False
    assert controller.port_name is None


def test_rescan_picks_up_a_controller_plugged_in_late(qapp):
    controller = StubController(["JD-Xi"])
    controller.auto_connect()
    changed: list[list[str]] = []
    controller.ports_changed.connect(changed.append)

    controller.ports = MINILAB_PORTS
    ports = controller.rescan()

    assert "Minilab3 MIDI" in ports
    assert changed == [ports]


def test_rescan_is_quiet_when_nothing_changed(qapp):
    controller = StubController(MINILAB_PORTS)
    controller.auto_connect()
    changed: list[list[str]] = []
    controller.ports_changed.connect(changed.append)

    controller.rescan()

    assert changed == []


def test_rescan_drops_a_controller_that_went_away(qapp):
    controller = StubController(MINILAB_PORTS)
    controller.auto_connect()

    controller.ports = ["JD-Xi"]
    assert controller.rescan() == []
    assert controller.is_open is False
    assert controller.port_name is None


def test_messages_are_tagged_with_the_port_they_came_from(qapp):
    controller = StubController(MINILAB_PORTS)
    controller.auto_connect()
    received: list[tuple[str, object]] = []
    changes: list[tuple[int, int, int]] = []
    controller.message_received.connect(lambda port, msg: received.append((port, msg)))
    controller.control_changed.connect(lambda *args: changes.append(args))

    knob = mido.Message("control_change", control=74, value=90)
    fader = mido.Message("control_change", control=82, value=7)
    # RtMidi hands the port name back as the callback's user data
    controller._on_midi((knob.bytes(), 0.0), "Minilab3 MIDI")
    controller._on_midi((fader.bytes(), 0.0), "Minilab3 ALV")
    controller._emit_pending()

    assert [port for port, _ in received] == ["Minilab3 MIDI", "Minilab3 ALV"]
    assert changes == [(0, 74, 90), (0, 82, 7)]


def test_each_port_is_parsed_separately(qapp):
    # One shared parser would splice two streams together; a message split
    # across callbacks must still arrive intact while another port is active.
    controller = StubController(MINILAB_PORTS)
    controller.auto_connect()
    changes: list[tuple[int, int, int]] = []
    controller.control_changed.connect(lambda *args: changes.append(args))

    raw = mido.Message("control_change", control=74, value=90).bytes()
    controller._on_midi((raw[:1], 0.0), "Minilab3 MIDI")  # status byte only
    controller._on_midi(
        (mido.Message("control_change", control=82, value=7).bytes(), 0.0),
        "Minilab3 ALV",
    )
    controller._on_midi((raw[1:], 0.0), "Minilab3 MIDI")  # rest of the message
    controller._emit_pending()

    assert changes == [(0, 82, 7), (0, 74, 90)]


def test_close_releases_every_port(qapp):
    controller = StubController(MINILAB_PORTS)
    controller.auto_connect()

    controller.close()

    assert controller.is_open is False
    assert controller.port_name is None
    assert sorted(controller.closed) == sorted(
        ["Minilab3 MIDI", "Minilab3 DIN THRU", "Minilab3 MCU/HUI", "Minilab3 ALV"]
    )
