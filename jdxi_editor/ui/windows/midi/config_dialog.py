"""
config_dialog module
====================

MIDIConfigDialog is a dialog class that allows users to configure MIDI input and output ports.

It provides the following functionality:
- Display available MIDI input and output ports in combo boxes (the JD-Xi first).
- Allow users to select and change MIDI input and output ports.
- Refresh the list of available MIDI ports.
- Test the connection: an Identity Request, and what answered.
- Retrieve the selected MIDI port settings.

The dialog opens at once: the MIDI ports, the audio outputs and the SoundFonts
are listed on a worker thread, and FluidSynth starts there too (loading a
SoundFont of 140 MB kept Windows from drawing the dialog for seconds).

Attributes:
    input_ports (list): List of available MIDI input ports.
    output_ports (list): List of available MIDI output ports.
    current_in (str): Currently selected MIDI input port (optional).
    current_out (str): Currently selected MIDI output port (optional).
    midi_helper (MidiIOHelper): Instance of the MIDIHelper class to interact with MIDI devices.

Methods:
    refresh_ports() : Refresh the list of available MIDI ports.
    get_input_port() : Returns the currently selected MIDI input port.
    get_output_port() : Returns the currently selected MIDI output port.
    get_settings() : Returns a dictionary containing the selected MIDI input and output ports.

"""

import os
import threading
from typing import Callable, Optional

import qtawesome as qta
import shiboken6
from decologr import Decologr as log
from PySide6.QtCore import QObject, Qt, QTimer, Signal, Slot
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
)

from jdxi_editor.audio.soundfont_output import (
    MIDI_PORT_NAME,
    SoundfontOutput,
    chosen_output,
    opened_output_name,
    output_devices,
    sounddevice_available,
)
from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.io.connection import ROLAND, is_jdxi_identity
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.io.data_requests import (
    data_requests_enabled,
    set_data_requests_enabled,
    stored_data_requests_setting,
)
from jdxi_editor.ui.editors.pattern.preset_list_provider import (
    get_hardware_interface,
    get_sf2_path,
    get_use_soundfont_list,
    set_hardware_interface,
    set_sf2_path,
    set_use_soundfont_list,
    soundfont_list_problem,
)
from jdxi_editor.ui.editors.helpers.widgets import create_panel
from jdxi_editor.ui.layout.helper import add_round_button_from_spec
from jdxi_editor.ui.style import JDXiUIDimensions
from jdxi_editor.ui.widgets.digital.title import DigitalTitle
from jdxi_editor.ui.windows.jdxi.helpers.port import (
    filter_excluded_ports,
    find_jdxi_port,
    is_excluded_port,
)
from picoui.specs.widgets import ButtonSpec

# In-app FluidSynth defaults
HW_PORT_HINT = "Roland JDXi"  # adjust if your port name differs
SF2_DIR = os.path.expanduser("~/SoundFonts")
SF2_PATH = os.path.join(SF2_DIR, "FluidR3_GM.sf2")

IDENTITY_REQUEST = [0xF0, 0x7E, 0x7F, 0x06, 0x01, 0xF7]
IDENTITY_TIMEOUT_MS = 1500
JDXI_MARK = "★ "

# Top-level imports so py2app/modulegraph includes these in the bundle
# (lazy imports inside functions are not traced by the dependency analyzer)
from jdxi_editor.midi.fluidsynth_library import (
    import_error_message,
    prepare_fluidsynth_library,
)

_fluidsynth_err_msg = ""
prepare_fluidsynth_library()  # Windows: point the DLL search at FluidSynth
try:
    import fluidsynth as _fluidsynth_module
except Exception as _fluidsynth_err:
    _fluidsynth_module = None
    _fluidsynth_err_msg = str(_fluidsynth_err)


def _get_output_devices() -> list[tuple[str, int]]:
    """
    Output devices as (display name, sounddevice index).

    :return: list
    """
    return output_devices()


class _Relay(QObject):
    """
    Delivers a background result on the UI thread, if its owner still exists.

    Not a child of the owner: the dialog may be deleted (closed) while the work
    runs, and the worker must never emit on a deleted object.
    """

    finished = Signal(object, object)  # result, exception

    def __init__(self, callback: Callable, owner: QObject):
        super().__init__()
        self._callback = callback
        self._owner = owner
        self.finished.connect(self._deliver, Qt.ConnectionType.QueuedConnection)

    @Slot(object, object)
    def _deliver(self, result, error) -> None:
        try:
            if shiboken6.isValid(self._owner):
                self._callback(result, error)
        finally:
            self._owner = self._callback = None
            _RELAYS.discard(self)


_RELAYS: set = set()  # alive until delivered


def run_in_background(fn: Callable, callback: Callable, parent: QObject) -> None:
    """
    fn() on a worker thread, then callback(result, error) on parent's thread.

    A plain Python thread (not a QRunnable, whose wrapper PySide may free while
    it runs); the result crosses back through a queued Qt signal.
    """
    relay = _Relay(callback, parent)
    _RELAYS.add(relay)

    def work() -> None:
        try:
            result, error = fn(), None
        except Exception as ex:  # reported to the callback
            result, error = None, ex
        relay.finished.emit(result, error)

    threading.Thread(target=work, name="MIDIConfigDialog", daemon=True).start()


def list_midi_ports(midi_helper) -> tuple[list[str], list[str]]:
    """
    The MIDI ports, listed through ports of its own.

    This runs in the background while the app uses the helper's ports (rtmidi
    is not thread-safe, and with a device gone Windows crashed listing through
    them). Without a MIDI backend the helper's lists are used.
    """
    import rtmidi

    from jdxi_editor.midi.io.backend import NoMidiBackend, open_rtmidi

    inputs, outputs = [], []
    for factory, kind, names, fallback in (
        (rtmidi.MidiIn, "input", inputs, midi_helper.get_input_ports),
        (rtmidi.MidiOut, "output", outputs, midi_helper.get_output_ports),
    ):
        port = open_rtmidi(factory, kind)
        try:
            names.extend(fallback() if isinstance(port, NoMidiBackend) else port.get_ports())
        finally:
            delete = getattr(port, "delete", None)
            if callable(delete):
                try:
                    delete()
                except Exception:
                    pass
    return filter_excluded_ports(inputs), filter_excluded_ports(outputs)


def list_audio_outputs() -> Optional[list[tuple[str, int]]]:
    """The audio outputs FluidSynth can play on; None without sounddevice."""
    if not sounddevice_available():
        return None
    return _get_output_devices()


def find_soundfonts(folder: str = SF2_DIR) -> list[str]:
    """The .sf2 and .sf3 files under *folder*."""
    found = []
    try:
        if os.path.isdir(folder):
            for root, _dirs, files in os.walk(folder):
                found += [
                    os.path.join(root, f)
                    for f in files
                    if f.lower().endswith((".sf2", ".sf3"))
                ]
    except OSError:
        pass
    return sorted(found)


def parse_identity_reply(data) -> Optional[dict]:
    """Identity Reply (mido sysex data, without F0/F7) -> details, else None."""
    data = [int(b) for b in data]
    if len(data) < 7 or data[0] != 0x7E or data[2] != 0x06 or data[3] != 0x02:
        return None
    return {
        "manufacturer": data[4],
        "is_jdxi": is_jdxi_identity(data),
        "version": ".".join(str(b) for b in data[9:13]) if len(data) >= 13 else "",
    }


class _SoundfontRouteWatch(QObject):
    """Reopen a SoundFont that follows the system output when that route changes."""

    def __init__(self, helper):
        super().__init__(helper)
        self._helper = helper
        self._busy = False
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._check)

    def sync(self) -> None:
        """Run while the open SoundFont is following the system output."""
        player = getattr(self._helper, "soundfont_output", None)
        if player is not None and player.follows_default and player._stream is not None:
            if not self._timer.isActive():
                self._timer.start()
        else:
            self._timer.stop()

    def _check(self) -> None:
        if self._busy:
            return
        player = getattr(self._helper, "soundfont_output", None)
        if player is None or not player.follows_default:
            self._timer.stop()
            return
        if not player.take_route_change():
            return
        self._busy = True
        try:
            player.reopen()
            self._helper.soundfont_synth = player.synth
            self._helper.soundfont_sfid = player.sfid
            callback = player.on_reopened
            if callback is not None:
                callback()
        except Exception as ex:
            log.error(f"SoundFont output did not follow the new route: {ex}")
        finally:
            self._busy = False


class MIDIConfigDialog(QDialog):
    def __init__(self, midi_helper=MidiIOHelper, parent=None):
        super().__init__(parent)
        self.setWindowTitle("MIDI Configuration")
        self.setMinimumSize(
            JDXiUIDimensions.Config.WIDTH, JDXiUIDimensions.Config.HEIGHT
        )
        JDXi.UI.Theme.apply_editor_style(self)
        self.midi_helper = midi_helper
        self.current_in = getattr(midi_helper, "current_in", None)
        self.current_out = getattr(midi_helper, "current_out", None)
        # What is known now, at once; the fresh lists follow from the background
        self.input_ports = [p for p in [self.current_in] if p]
        self.output_ports = [p for p in [self.current_out] if p]
        # FluidSynth runtime state (optional), shared with MIDI input forwarding.
        self.fs = getattr(midi_helper, "soundfont_synth", None)
        self.sfid = getattr(midi_helper, "soundfont_sfid", None)
        self._refreshing_outputs = False
        self._outputs_listed = False
        self._start_when_listed = False
        self._busy_synth = False
        self._identity_timer = QTimer(self)
        self._identity_timer.setSingleShot(True)
        self._identity_timer.timeout.connect(self._identity_timed_out)
        self._listening = False
        self.status_kind = "idle"
        self.sf2_path = ""
        self._create_ui()
        # Prefill SoundFont path: prefer saved path, else default if file exists
        try:
            saved_path = get_sf2_path()
            if saved_path and os.path.isfile(saved_path):
                self.sf2_edit.setText(saved_path)
                self.sf2_path = saved_path
            elif os.path.isfile(SF2_PATH):
                self.sf2_edit.setText(SF2_PATH)
                self.sf2_path = SF2_PATH
        except Exception:
            pass
        # Default to enabling in-app synth option (it starts once the audio
        # outputs are listed, in the background)
        self.fluidsynth_enable.setChecked(True)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        QTimer.singleShot(0, self, self.refresh_ports)
        QTimer.singleShot(0, self, self._load_synth_choices)
        if self._ports_open():
            QTimer.singleShot(150, self, self.test_connection)
        else:
            self._set_status(
                "idle", "Not connected. Choose the JD-Xi's ports, then Test connection."
            )

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self, self._bring_to_front)

    def _bring_to_front(self):
        self.raise_()
        self.activateWindow()
        self.setFocus()

    def _create_ui(self):
        """Create the dialog UI"""
        # Everything sits on one glossy black panel (its groups sections on it)
        outer_layout = QVBoxLayout(self)
        self.panel = create_panel()
        outer_layout.addWidget(self.panel)
        layout = self.panel.layout()

        status_row = QHBoxLayout()
        self.status_dot = QLabel("●")
        self.status_dot.setFixedWidth(18)
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        # Room for three lines, so a longer message does not get cut
        self.status_label.setMinimumHeight(
            self.status_label.fontMetrics().lineSpacing() * 3
        )
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        status_row.addWidget(self.status_dot, 0, Qt.AlignmentFlag.AlignTop)
        status_row.addWidget(self.status_label, 1)
        layout.addLayout(status_row)

        # Input port selection
        input_group = QGroupBox("MIDI Input")
        input_layout = QVBoxLayout(input_group)

        self.input_display = DigitalTitle(
            self.current_in or "No input",
            show_upper_text=False,
        )
        # input_layout.addWidget(self.input_display) @@@

        icons_hlayout = QHBoxLayout()
        for icon in ["mdi6.midi-port"]:
            icon_label = QLabel()
            icon = qta.icon(icon, color=JDXi.UI.Style.FOREGROUND)
            pixmap = icon.pixmap(
                JDXi.UI.Style.ICON_SIZE, JDXi.UI.Style.ICON_SIZE
            )  # Set the desired size
            icon_label.setPixmap(pixmap)
            icon_label.setAlignment(Qt.AlignHCenter)
            icons_hlayout.addWidget(icon_label)
        input_layout.addLayout(icons_hlayout)

        self.input_combo = QComboBox()
        self._update_midi_port_combo(self.input_combo, self.input_ports, self.current_in)
        self.input_combo.currentIndexChanged.connect(self._on_input_combo_changed)
        self.input_combo.currentIndexChanged.connect(self._on_port_choice_changed)

        input_layout.addWidget(self.input_combo)
        layout.addWidget(input_group)

        # Output port selection
        output_group = QGroupBox("MIDI Output")
        output_layout = QVBoxLayout(output_group)

        self.output_display = DigitalTitle(
            self.current_out or "No output",
            show_upper_text=False,
        )

        icons_hlayout = QHBoxLayout()
        for icon in ["mdi6.midi-port"]:
            icon_label = QLabel()
            icon = qta.icon(icon, color=JDXi.UI.Style.FOREGROUND)
            pixmap = icon.pixmap(
                JDXi.UI.Style.ICON_SIZE, JDXi.UI.Style.ICON_SIZE
            )  # Set the desired size
            icon_label.setPixmap(pixmap)
            icon_label.setAlignment(Qt.AlignHCenter)
            icons_hlayout.addWidget(icon_label)
        output_layout.addLayout(icons_hlayout)

        self.output_combo = QComboBox()
        self._update_midi_port_combo(self.output_combo, self.output_ports, self.current_out)
        self.output_combo.currentIndexChanged.connect(self._on_output_combo_changed)
        self.output_combo.currentIndexChanged.connect(self._on_port_choice_changed)

        output_layout.addWidget(self.output_combo)

        self.data_requests_check = QCheckBox("Request data from the JD-Xi")
        JDXi.UI.Theme.apply_button_mini_style(self.data_requests_check)
        self.data_requests_check.setToolTip(
            "Ask the JD-Xi for its current settings when editors open, on "
            "program changes and on Refresh. Turn off in SoundFont mode or "
            "when no JD-Xi is connected: nothing would answer. Parameter "
            "changes are still sent, and an explicit Read still asks."
        )
        self.data_requests_check.setChecked(data_requests_enabled())
        output_layout.addWidget(self.data_requests_check)
        layout.addWidget(output_group)

        # Software Synth (FluidSynth)
        synth_group = QGroupBox("Software Synth (FluidSynth)")
        synth_layout = QVBoxLayout(synth_group)

        self.fluidsynth_enable = QCheckBox("Enable FluidSynth for local playback")
        JDXi.UI.Theme.apply_button_mini_style(self.fluidsynth_enable)
        self.fluidsynth_enable.toggled.connect(self._toggle_fluidsynth_controls)
        synth_layout.addWidget(self.fluidsynth_enable)

        self.use_soundfont_list = QCheckBox("Use SoundFont List")
        JDXi.UI.Theme.apply_button_mini_style(self.use_soundfont_list)
        self.use_soundfont_list.setToolTip(
            "List the SoundFont's presets in the Digital, Analog and Drums "
            "preset lists (and GM percussion names in the Pattern editor) "
            "instead of the built-in JD-Xi presets. Needs the sf2utils package."
        )
        self.use_soundfont_list.setChecked(get_use_soundfont_list())
        self.use_soundfont_list.toggled.connect(self._on_soundfont_list_toggled)
        synth_layout.addWidget(self.use_soundfont_list)

        # Audio output for FluidSynth, distinct from the MIDI Output port
        hw_row = QHBoxLayout()
        hw_row.addWidget(QLabel("Audio output:"))
        self.hardware_interface_combo = QComboBox()
        self.hardware_interface_combo.setToolTip(
            "Where FluidSynth plays. Changing this while it is running "
            "reopens that output."
        )
        self.hardware_interface_combo.addItem("Listing…", None)
        self.hardware_interface_combo.currentIndexChanged.connect(
            self._on_audio_output_changed
        )
        hw_row.addWidget(self.hardware_interface_combo)
        synth_layout.addLayout(hw_row)

        sf_row = QHBoxLayout()
        sf_row.addWidget(QLabel("SoundFont (SF2/SF3):"))
        self.sf2_edit = QLineEdit()
        self.sf2_edit.setPlaceholderText("FluidR3_GM.sf2")  # default SoundFont
        sf_row.addWidget(self.sf2_edit)
        browse_btn_layout = QHBoxLayout()
        browse_button_spec = ButtonSpec(
            icon=JDXi.UI.Icon.FOLDER_NOTCH_OPEN,
            label="Browse",
            slot=self._browse_sf2,
            layout=browse_btn_layout,
        )
        add_round_button_from_spec(spec=browse_button_spec)
        sf_row.addLayout(browse_btn_layout)
        synth_layout.addLayout(sf_row)

        # Available SoundFonts selector
        combo_row = QHBoxLayout()
        combo_row.addWidget(QLabel("Available:"))
        self.sf2_combo = QComboBox()
        self.sf2_combo.currentIndexChanged.connect(self._on_sf2_combo_changed)
        combo_row.addWidget(self.sf2_combo)
        synth_layout.addLayout(combo_row)

        btn_row = QHBoxLayout()
        button_row_button_specs = self._create_button_row_specs(btn_row)
        buttons = []
        for btn_spec in button_row_button_specs:
            button = add_round_button_from_spec(btn_spec)
            buttons.append(button)
        self.fs_start_btn, self.fs_stop_btn, self.fs_test_btn = buttons
        synth_layout.addLayout(btn_row)

        self.fs_status = QLabel("")
        synth_layout.addWidget(self.fs_status)

        layout.addWidget(synth_group)

        # Initially disable subordinate controls
        self._toggle_fluidsynth_controls(False)

        # Find, Refresh and Test (round + label)
        refresh_row = QHBoxLayout()
        refresh_row.addStretch()
        self.find_button = add_round_button_from_spec(
            ButtonSpec(
                label="Find the JD-Xi",
                icon=JDXi.UI.Icon.USB,
                tooltip="Choose the ports whose name contains JD-Xi",
                slot=self.select_jdxi_ports,
                layout=refresh_row,
            )
        )
        refresh_ports_spec = ButtonSpec(
            label="Refresh Ports",
            icon=JDXi.UI.Icon.REFRESH,
            tooltip="List the MIDI ports again, e.g. after connecting the JD-Xi",
            slot=self.refresh_ports,
            layout=refresh_row,
        )
        self.refresh = add_round_button_from_spec(refresh_ports_spec)
        self.test_button = add_round_button_from_spec(
            ButtonSpec(
                label="Test connection",
                icon=JDXi.UI.Icon.MIDI_PORT,
                tooltip="Connect to the chosen ports and ask the instrument who it is",
                slot=self.test_connection,
                layout=refresh_row,
            )
        )
        refresh_row.addStretch()
        layout.addLayout(refresh_row)
        self.help_label = QLabel(
            "No JD-Xi in the list? Connect it by USB, switch it on and press "
            "Refresh Ports. Without it the editor works offline."
        )
        self.help_label.setWordWrap(True)
        self.help_label.setVisible(False)
        layout.addWidget(self.help_label)

        # Dialog buttons (round + labels, Transport style)
        dialog_btn_row = QHBoxLayout()
        dialog_btn_row.addStretch()
        ok_btn_spec = ButtonSpec(
            label="OK", icon=JDXi.UI.Icon.SAVE, slot=self.accept, layout=dialog_btn_row
        )
        self.ok_button = add_round_button_from_spec(ok_btn_spec)
        cancel_btn_spec = ButtonSpec(
            label="Cancel",
            icon=JDXi.UI.Icon.CANCEL,
            slot=self.reject,
            layout=dialog_btn_row,
        )
        self.cancel_button = add_round_button_from_spec(cancel_btn_spec)
        dialog_btn_row.addStretch()
        layout.addLayout(dialog_btn_row)

    def _update_midi_port_combo(self, midi_port_combo: QComboBox, midi_ports: list, current_port: str) -> None:
        """
        Populate a MIDI port combo box, omitting virtual/loopback ports.

        The JD-Xi comes first, marked, so it is easy to spot; it is chosen when
        *current_port* is not listed.
        """
        midi_ports = filter_excluded_ports(midi_ports)
        jdxi = find_jdxi_port(midi_ports)
        for port in sorted(midi_ports, key=lambda p: p != jdxi):
            midi_port_combo.addItem(f"{JDXI_MARK}{port}" if port == jdxi else port, port)
        index = midi_port_combo.findData(current_port) if current_port else -1
        if index < 0 and jdxi:
            index = midi_port_combo.findData(jdxi)
        if midi_port_combo.count():
            midi_port_combo.setCurrentIndex(max(index, 0))

    def _create_button_row_specs(self, btn_row: QHBoxLayout) -> list[ButtonSpec]:
        """create button row specs"""
        fs_start_btn_spec = ButtonSpec(
            label="Start",
            icon=JDXi.UI.Icon.PLAY,
            slot=self._start_fluidsynth,
            layout=btn_row,
        )
        fs_stop_btn_spec = ButtonSpec(
            label="Stop",
            icon=JDXi.UI.Icon.STOP,
            slot=self._stop_fluidsynth,
            layout=btn_row,
        )
        fs_test_btn_spec = ButtonSpec(
            label="Test Note",
            icon=JDXi.UI.Icon.MUSIC_NOTE,
            slot=self._test_fluidsynth,
            layout=btn_row,
        )
        button_row_button_specs = [
            fs_start_btn_spec,
            fs_stop_btn_spec,
            fs_test_btn_spec,
        ]
        return button_row_button_specs

    def _refresh_hardware_devices(self, devices: Optional[list] = None) -> None:
        """
        Fill the audio outputs.

        :param devices: (name, index) as list_audio_outputs() gives them (None:
            sounddevice not installed)
        """
        combo = self.hardware_interface_combo
        current = combo.currentText()
        self._refreshing_outputs = True
        try:
            combo.clear()
            if devices is None:
                combo.addItem("(sounddevice not installed)", None)
                return
            combo.addItem("(Default)", None)
            for display_name, device_index in devices:
                combo.addItem(display_name, device_index)
            chosen = chosen_output(
                current,
                get_hardware_interface(),
                [name for name, _index in devices],
            )
            idx = combo.findText(chosen) if chosen else 0
            combo.setCurrentIndex(idx if idx >= 0 else 0)
        finally:
            self._refreshing_outputs = False

    def _on_audio_output_changed(self, index: int) -> None:
        """Remember the output, and reopen it when playback is already running."""
        if self._refreshing_outputs or index < 0:
            return
        name = self.hardware_interface_combo.currentText()
        if name in ("(Default)", "(sounddevice not installed)", ""):
            set_hardware_interface("")
        else:
            set_hardware_interface(name)
        if self.fs is not None:
            self._start_fluidsynth()

    def _on_input_combo_changed(self) -> None:
        """On input ComboBox changed, set the DigitalTitle text."""
        if hasattr(self, "input_display") and hasattr(self, "input_combo"):
            self.input_display.setText(self.input_combo.currentText() or "No input")

    def _on_output_combo_changed(self) -> None:
        """On output ComboBox changed, set the DigitalTitle text."""
        if hasattr(self, "output_display") and hasattr(self, "output_combo"):
            self.output_display.setText(self.output_combo.currentText() or "No output")

    def refresh_ports(self):
        """List the MIDI ports again, in the background."""
        self.refresh.setEnabled(False)
        run_in_background(
            lambda: list_midi_ports(self.midi_helper), self._ports_listed, self
        )

    def _ports_listed(self, result, error) -> None:
        self.refresh.setEnabled(True)
        if error is not None:
            log.error(f"Listing MIDI ports failed: {error}", scope="MIDIConfigDialog")
            self._set_status("error", f"Could not list the MIDI ports: {error}")
            return
        self._fill_ports(*result)

    def _fill_ports(self, inputs: list[str], outputs: list[str]) -> None:
        """The ports listed, keeping the ports chosen in the dialog where they still exist."""
        chosen_in = self.get_input_port() or self.current_in
        chosen_out = self.get_output_port() or self.current_out
        self.input_ports, self.output_ports = list(inputs), list(outputs)
        for combo, ports, chosen in (
            (self.input_combo, self.input_ports, chosen_in),
            (self.output_combo, self.output_ports, chosen_out),
        ):
            combo.blockSignals(True)
            combo.clear()
            self._update_midi_port_combo(combo, ports, chosen)
            combo.blockSignals(False)
        # Keep DigitalTitle in sync with current selection
        self._on_input_combo_changed()
        self._on_output_combo_changed()
        found = bool(find_jdxi_port(self.input_ports) and find_jdxi_port(self.output_ports))
        self.find_button.setEnabled(found)
        self.help_label.setVisible(not found)
        # Only when no test is running or has answered: its result says more
        if not found and self.status_kind == "idle":
            self._set_status("error", "No JD-Xi among the MIDI ports.")

    def select_jdxi_ports(self) -> None:
        """Choose the ports whose name contains JD-Xi."""
        for combo, ports in (
            (self.input_combo, self.input_ports),
            (self.output_combo, self.output_ports),
        ):
            port = find_jdxi_port(ports)
            if port:
                combo.setCurrentIndex(combo.findData(port))

    def _on_port_choice_changed(self, _index: int = 0) -> None:
        if self._ports_changed():
            self._set_status("idle", "Ports changed: Test connection, or OK to use them.")

    def _ports_changed(self) -> bool:
        return (self.get_input_port() or None) != (self.current_in or None) or (
            self.get_output_port() or None
        ) != (self.current_out or None)

    def _ports_open(self) -> bool:
        h = self.midi_helper
        return bool(getattr(h, "is_input_open", False) and getattr(h, "is_output_open", False))

    def _set_status(self, kind: str, text: str) -> None:
        colours = {"ok": "#3cc98a", "busy": "#f2c94c", "error": "#f0483e", "idle": "#8a8d94"}
        self.status_dot.setStyleSheet(
            f"color: {colours.get(kind, '#8a8d94')}; font-size: 16px;"
        )
        self.status_label.setText(text)
        self.status_kind = kind

    def _apply_ports(self) -> bool:
        """Open the chosen ports (an excluded one stays closed)."""
        in_port = self.get_undesirable_midi_port(self.get_input_port())
        out_port = self.get_undesirable_midi_port(self.get_output_port())
        self.midi_helper.close_ports()
        log.message(f"Reconnecting to: Midi In:\t'{in_port}'")
        log.message(f"Reconnecting to: Midi Out:\t'{out_port}'")
        ok = self.midi_helper.reconnect_port_names(in_port, out_port)
        if ok:
            self.current_in, self.current_out = in_port, out_port
        else:
            log.warning("Failed to reopen both MIDI ports")
        return ok

    def test_connection(self) -> None:
        """Use the chosen ports and send an Identity Request; the reply arrives later."""
        if (self._ports_changed() or not self._ports_open()) and not self._apply_ports():
            self._set_status("error", "Could not open the chosen ports.")
            return
        signal = getattr(self.midi_helper, "midi_message_incoming", None)
        if signal is None or not self._ports_open():
            self._set_status("error", "The MIDI ports are not open.")
            return
        if not self._listening:
            signal.connect(self._on_midi_message)
            self._listening = True
        self._set_status("busy", "Asking the instrument…")
        self.test_button.setEnabled(False)
        self._identity_timer.start(IDENTITY_TIMEOUT_MS)
        try:
            self.midi_helper.send_raw_message(IDENTITY_REQUEST)
        except Exception as ex:
            self._identity_timer.stop()
            self.test_button.setEnabled(True)
            self._set_status("error", f"Could not send to the MIDI output: {ex}")

    @Slot(object)
    def _on_midi_message(self, message) -> None:
        if not self._identity_timer.isActive() or getattr(message, "type", "") != "sysex":
            return
        reply = parse_identity_reply(getattr(message, "data", ()))
        if reply is None:
            return
        self._identity_timer.stop()
        self.test_button.setEnabled(True)
        if reply["is_jdxi"]:
            self._set_status("ok", "Connected: the JD-Xi replies.")
        elif reply["manufacturer"] == ROLAND:
            self._set_status(
                "error", "Another Roland instrument replied. Choose the JD-Xi's ports."
            )
        else:
            self._set_status(
                "error",
                f"A different instrument replied (manufacturer {reply['manufacturer']:02X}h). "
                "Choose the JD-Xi's ports.",
            )

    def _identity_timed_out(self) -> None:
        self.test_button.setEnabled(True)
        self._set_status(
            "error",
            "No reply. Check that the JD-Xi is on and that both ports are the "
            "JD-Xi's (not, e.g., Microsoft GS Wavetable Synth).",
        )

    def _stop_listening(self) -> None:
        self._identity_timer.stop()
        if self._listening:
            try:
                self.midi_helper.midi_message_incoming.disconnect(self._on_midi_message)
            except (RuntimeError, TypeError):
                pass
            self._listening = False

    def _load_synth_choices(self) -> None:
        """Audio outputs and SoundFonts, listed in the background."""
        run_in_background(
            lambda: (list_audio_outputs(), find_soundfonts()),
            self._synth_choices_loaded,
            self,
        )

    def _synth_choices_loaded(self, result, error) -> None:
        if error is not None:
            self.fs_status.setText(f"Could not list the audio outputs: {error}")
            return
        outputs, soundfonts = result
        self._refresh_hardware_devices(outputs)
        self._populate_sf2_combo(soundfonts)
        if self.sf2_edit.text().strip():
            self._ensure_sf2_in_combo(self.sf2_edit.text().strip())
            self._select_sf2_in_combo(self.sf2_edit.text().strip())
        self._outputs_listed = True
        if self._start_when_listed:
            self._start_when_listed = False
            self._start_fluidsynth()

    def _toggle_fluidsynth_controls(self, enabled: bool) -> None:
        controls_enabled = bool(self.fluidsynth_enable.isChecked())
        for w in [
            self.hardware_interface_combo,
            self.sf2_edit,
            self.fs_start_btn,
            self.fs_stop_btn,
            self.fs_test_btn,
        ]:
            w.setEnabled(controls_enabled)
        if not controls_enabled:
            self.fs_status.setText("")
        else:
            # Auto-start if a valid SoundFont is already set and synth not
            # running: on the audio output chosen, once the outputs are listed
            try:
                if (
                    self.fs is None
                    and self.sf2_edit.text().strip()
                    and os.path.isfile(self.sf2_edit.text().strip())
                ):
                    if self._outputs_listed:
                        self._start_fluidsynth()
                    else:
                        self._start_when_listed = True
            except Exception:
                pass

    def _on_soundfont_list_toggled(self, checked: bool) -> None:
        """Handle SoundFont list checkbox toggle - save immediately and notify listeners.

        Data requests follow the mode until chosen: off for SoundFont, on for
        the JD-Xi lists; the box can still be changed afterwards."""
        if stored_data_requests_setting() is None:
            self.data_requests_check.setChecked(not checked)
        sf_path = self.sf2_edit.text().strip()
        if sf_path and os.path.isfile(sf_path):
            set_sf2_path(sf_path)
        set_use_soundfont_list(checked)
        problem = soundfont_list_problem() if checked else None
        if problem:
            log.warning(scope="MIDIConfigDialog", message=f"SoundFont list unavailable: {problem}")
            QMessageBox.warning(
                self,
                "SoundFont List",
                f"{problem}\n\nThe preset lists will stay as JD-Xi until this is fixed.",
            )

    def _browse_sf2(self) -> None:
        start_dir = os.path.expanduser("~/SoundFonts")
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select SoundFont",
            start_dir if os.path.isdir(start_dir) else "",
            "SoundFonts (*.sf2 *.sf3)",
        )
        if file_path:
            self.sf2_edit.setText(file_path)
            self.sf2_path = file_path
            set_sf2_path(file_path)
            # Add to combo if missing and select
            self._ensure_sf2_in_combo(file_path)
            self._select_sf2_in_combo(file_path)

    def _start_fluidsynth(self) -> None:
        """Start FluidSynth and load the SoundFont, in the background."""
        if self._busy_synth:
            return
        if _fluidsynth_module is None:
            self.fs_status.setText(import_error_message(_fluidsynth_err_msg))
            return
        if not sounddevice_available():
            self.fs_status.setText("sounddevice is not installed")
            return
        sf_path = self.sf2_edit.text().strip()
        if not sf_path:
            self.fs_status.setText("Please select a SoundFont first.")
            return
        device = self.hardware_interface_combo.currentData()
        if not isinstance(device, int):
            device = None
        self._close_soundfont()
        self._busy_synth = True
        self._set_synth_buttons_enabled(False)
        self.fs_status.setText("Starting FluidSynth and loading the SoundFont…")
        lock = self.midi_helper.soundfont_lock

        def start():
            player = SoundfontOutput(lock)
            try:
                return player, player.start(sf_path, device)
            except Exception:
                try:
                    player.stop()
                except Exception:
                    pass
                raise

        run_in_background(start, self._fluidsynth_started, self)

    def _set_synth_buttons_enabled(self, enabled: bool) -> None:
        for button in (self.fs_start_btn, self.fs_stop_btn, self.fs_test_btn):
            button.setEnabled(enabled and self.fluidsynth_enable.isChecked())

    def _fluidsynth_started(self, result, error) -> None:
        self._busy_synth = False
        self._set_synth_buttons_enabled(True)
        if error is not None:
            self.fs_status.setText(f"FluidSynth error: {error}")
            log.error(f"FluidSynth error: {error}")
            return
        player, sfid = result
        self.midi_helper.soundfont_output = player
        self.midi_helper.soundfont_synth = player.synth
        self.midi_helper.soundfont_sfid = sfid
        self.fs = player.synth
        self.sfid = sfid
        player.on_reopened = self._note_opened_output
        self._note_opened_output()
        self._ensure_route_watch()
        # The SoundFont's MIDI port has just appeared
        self.refresh_ports()

    def _note_opened_output(self) -> None:
        """Name the output PortAudio actually opened."""
        player = getattr(self.midi_helper, "soundfont_output", None)
        if player is None:
            return
        where = opened_output_name(player.opened_device(), output_devices())
        where = where or "the default output"
        if player.midi_port is not None:
            self.fs_status.setText(
                f"FluidSynth: started on {where} · MIDI Output '{MIDI_PORT_NAME}' available"
            )
        else:
            self.fs_status.setText(
                f"FluidSynth: started on {where} (no MIDI port on this system)"
            )

    def _ensure_route_watch(self) -> None:
        watch = getattr(self.midi_helper, "_soundfont_route_watch", None)
        if watch is None:
            watch = _SoundfontRouteWatch(self.midi_helper)
            self.midi_helper._soundfont_route_watch = watch
        watch.sync()

    def closeEvent(self, event):
        self._stop_listening()
        player = getattr(self.midi_helper, "soundfont_output", None)
        if player is not None and player.on_reopened == self._note_opened_output:
            player.on_reopened = None
        super().closeEvent(event)

    def _close_soundfont(self) -> None:
        player = getattr(self.midi_helper, "soundfont_output", None)
        if player is not None:
            player.stop()
        else:
            fs = getattr(self.midi_helper, "soundfont_synth", None)
            if fs is not None:
                fs.delete()
        self.midi_helper.soundfont_output = None
        self.midi_helper.soundfont_synth = None
        self.midi_helper.soundfont_sfid = None
        self.fs = None
        self.sfid = None
        self._ensure_route_watch()

    def _stop_fluidsynth(self) -> None:
        try:
            self._close_soundfont()
            self.fs_status.setText("FluidSynth: stopped")
            self.refresh_ports()
        except Exception as ex:
            self.fs_status.setText(f"Stop error: {ex}")
            log.error(f"FluidSynth stop error: {ex}")

    def _test_fluidsynth(self) -> None:
        try:
            fs = getattr(self.midi_helper, "soundfont_synth", None)
            if fs is None:
                self.fs_status.setText("Start FluidSynth first.")
                return
            lock = self.midi_helper.soundfont_lock

            def play(on: bool) -> None:
                current = getattr(self.midi_helper, "soundfont_synth", None)
                if current is not fs:
                    return
                with lock:
                    if on:
                        fs.noteon(0, 60, 110)
                    else:
                        fs.noteoff(0, 60)

            play(True)
            QTimer.singleShot(300, lambda: play(False))
            self.fs_status.setText("Test note triggered.")
        except Exception as ex:
            self.fs_status.setText(f"Test error: {ex}")
            log.error(f"FluidSynth test error: {ex}")

    def _populate_sf2_combo(self, found: list[str]) -> None:
        """Fill the combo box with the SoundFonts found (find_soundfonts)."""
        if not hasattr(self, "sf2_combo"):
            return
        self.sf2_combo.blockSignals(True)
        self.sf2_combo.clear()
        # Add items (digital basename, store full path)
        for path in sorted(found):
            self.sf2_combo.addItem(os.path.basename(path), path)
        self.sf2_combo.blockSignals(False)

    def _on_sf2_combo_changed(self, index: int) -> None:
        if index < 0:
            return
        path = self.sf2_combo.currentData()
        if isinstance(path, str) and path:
            self.sf2_edit.setText(path)
            self.sf2_path = path
            set_sf2_path(path)

    def _ensure_sf2_in_combo(self, path: str) -> None:
        if not hasattr(self, "sf2_combo"):
            return
        # If already present, do nothing
        for i in range(self.sf2_combo.count()):
            if self.sf2_combo.itemData(i) == path:
                return
        self.sf2_combo.addItem(os.path.basename(path), path)

    def _select_sf2_in_combo(self, path: str) -> None:
        if not hasattr(self, "sf2_combo"):
            return
        for i in range(self.sf2_combo.count()):
            if self.sf2_combo.itemData(i) == path:
                self.sf2_combo.setCurrentIndex(i)
                return

    def accept(self):
        set_use_soundfont_list(self.use_soundfont_list.isChecked())
        set_data_requests_enabled(self.data_requests_check.isChecked())
        sf_path = self.sf2_edit.text().strip()
        if sf_path:
            set_sf2_path(sf_path)
        if self._outputs_listed:
            hw_name = self.hardware_interface_combo.currentText()
            if hw_name in ("(Default)", "(sounddevice not installed)", ""):
                set_hardware_interface("")
            else:
                set_hardware_interface(hw_name)
        self._stop_listening()
        reopen = self._ports_changed() or not self._ports_open()
        super().accept()
        if reopen:
            self._apply_ports()  # after the dialog has closed

    def reject(self):
        self._stop_listening()
        super().reject()

    def get_undesirable_midi_port(self, midi_port_text: str) -> str:
        if is_excluded_port(midi_port_text):
            log.warning("Detected excluded MIDI port. Ignoring.")
            midi_port_text = ""
        return midi_port_text

    def get_input_port(self) -> str:
        """Get selected input port name

        Returns:
            Selected input port name or empty string if none selected
        """
        return self.input_combo.currentData() or self.input_combo.currentText().removeprefix(JDXI_MARK)

    def get_output_port(self) -> str:
        """Get selected output port name

        Returns:
            Selected output port name or empty string if none selected
        """
        return self.output_combo.currentData() or self.output_combo.currentText().removeprefix(JDXI_MARK)

    def get_settings(self) -> dict:
        """Get all selected settings

        Returns:
            Dictionary containing input_port and output_port selections
        """
        return {
            "input_port": self.get_input_port(),
            "output_port": self.get_output_port(),
        }
