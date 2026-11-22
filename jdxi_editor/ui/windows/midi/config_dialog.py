"""
config_dialog module
====================

MIDIConfigDialog is a dialog class that allows users to configure MIDI input and output ports.

It provides the following functionality:
- Display available MIDI input and output ports in combo boxes.
- Allow users to select and change MIDI input and output ports.
- Refresh the list of available MIDI ports.
- Retrieve the selected MIDI port settings.

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

import qtawesome as qta
from decologr import Decologr as log
from PySide6.QtCore import QObject, Qt, QTimer
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
    is_excluded_port,
)
from picoui.specs.widgets import ButtonSpec

# In-app FluidSynth defaults
HW_PORT_HINT = "Roland JDXi"  # adjust if your port name differs
SF2_PATH = os.path.expanduser("~/SoundFonts/FluidR3_GM.sf2")

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
        self.input_ports = midi_helper.get_input_ports()
        self.output_ports = midi_helper.get_output_ports()
        self.current_in = midi_helper.current_in
        self.current_out = midi_helper.current_out
        # FluidSynth runtime state (optional), shared with MIDI input forwarding.
        self.fs = getattr(midi_helper, "soundfont_synth", None)
        self.sfid = getattr(midi_helper, "soundfont_sfid", None)
        self._refreshing_outputs = False
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
        # Default to enabling in-app synth option
        self.fluidsynth_enable.setChecked(True)
        # Populate soundfont combo and sync with field
        self._populate_sf2_combo()
        if self.sf2_edit.text().strip():
            self._select_sf2_in_combo(self.sf2_edit.text().strip())
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self._bring_to_front)

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
        self.hardware_interface_combo.currentIndexChanged.connect(
            self._on_audio_output_changed
        )
        self._refresh_hardware_devices()
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

        # Refresh button (round + label)
        refresh_row = QHBoxLayout()
        refresh_row.addStretch()
        refresh_ports_spec = ButtonSpec(
            label="Refresh Ports",
            icon=JDXi.UI.Icon.REFRESH,
            slot=self.refresh_ports,
            layout=refresh_row,
        )
        self.refresh = add_round_button_from_spec(refresh_ports_spec)
        refresh_row.addStretch()
        layout.addLayout(refresh_row)

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
        """Populate a MIDI port combo box, omitting virtual/loopback ports."""
        midi_ports = filter_excluded_ports(midi_ports)
        midi_port_combo.addItems(midi_ports)
        if current_port and current_port in midi_ports:
            midi_port_combo.setCurrentText(current_port)

    def _update_output_port_combo(self):
        self.output_ports = filter_excluded_ports(self.output_ports)
        self.output_combo.addItems(self.output_ports)
        if self.current_out and self.current_out in self.output_ports:
            self.output_combo.setCurrentText(self.current_out)

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

    def _refresh_hardware_devices(self, event=None):
        """refresh hardware devices"""
        combo = self.hardware_interface_combo
        current = combo.currentText()
        self._refreshing_outputs = True
        try:
            combo.clear()
            if not sounddevice_available():
                combo.addItem("(sounddevice not installed)", None)
                return
            devices = _get_output_devices()
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
        """Refresh the list of MIDI ports"""
        # Use the MIDIHelper instance to get the updated port lists
        self.input_ports = self.midi_helper.get_input_ports()
        self.output_ports = self.midi_helper.get_output_ports()
        self._refresh_hardware_devices()

        # Update the combo boxes
        self.input_combo.clear()
        self._update_midi_port_combo(self.input_combo, self.input_ports, self.current_in)
        self.output_combo.clear()
        self._update_midi_port_combo(self.output_combo, self.output_ports, self.current_out)

        # Keep DigitalTitle in sync with current selection
        self._on_input_combo_changed()
        self._on_output_combo_changed()

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
            # Auto-start if a valid SoundFont is already set and synth not running
            try:
                if (
                    self.fs is None
                    and self.sf2_edit.text().strip()
                    and os.path.isfile(self.sf2_edit.text().strip())
                ):
                    self._start_fluidsynth()
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
        try:
            self._close_soundfont()
            player = SoundfontOutput(self.midi_helper.soundfont_lock)
            sfid = player.start(sf_path, device)
        except Exception as ex:
            self._close_soundfont()
            self.fs_status.setText(f"FluidSynth error: {ex}")
            log.error(f"FluidSynth error: {ex}")
            return
        self.midi_helper.soundfont_output = player
        self.midi_helper.soundfont_synth = player.synth
        self.midi_helper.soundfont_sfid = sfid
        self.fs = player.synth
        self.sfid = sfid
        player.on_reopened = self._note_opened_output
        self._note_opened_output()
        self._ensure_route_watch()
        # The SoundFont's MIDI port has just appeared
        self._refresh_ports_keeping_selection()

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
        player = getattr(self.midi_helper, "soundfont_output", None)
        if player is not None and player.on_reopened == self._note_opened_output:
            player.on_reopened = None
        super().closeEvent(event)

    def _refresh_ports_keeping_selection(self) -> None:
        """Re-list the ports (the SoundFont's comes and goes with FluidSynth),
        keeping the ports chosen in the dialog where they still exist."""
        chosen_in = self.input_combo.currentText()
        chosen_out = self.output_combo.currentText()
        self.refresh_ports()
        for combo, chosen in ((self.input_combo, chosen_in), (self.output_combo, chosen_out)):
            index = combo.findText(chosen)
            if chosen and index >= 0:
                combo.setCurrentIndex(index)

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
            self._refresh_ports_keeping_selection()
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

    def _populate_sf2_combo(self) -> None:
        """Scan ~/SoundFonts for .sf2/.sf3 files and populate the combo box."""
        if not hasattr(self, "sf2_combo"):
            return
        self.sf2_combo.blockSignals(True)
        self.sf2_combo.clear()
        base_dir = os.path.expanduser("~/SoundFonts")
        found = []
        try:
            if os.path.isdir(base_dir):
                for root, dirs, files in os.walk(base_dir):
                    for f in files:
                        if f.lower().endswith((".sf2", ".sf3")):
                            full = os.path.join(root, f)
                            found.append(full)
        except Exception:
            pass
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
        hw_name = self.hardware_interface_combo.currentText()
        if hw_name in ("(Default)", "(sounddevice not installed)", ""):
            set_hardware_interface("")
        else:
            set_hardware_interface(hw_name)
        super().accept()
        self.midi_helper.close_ports()
        input_port_text = self.get_input_port()
        output_port_text = self.get_output_port()
        input_port_text = self.get_undesirable_midi_port(input_port_text)
        output_port_text = self.get_undesirable_midi_port(output_port_text)
        if is_excluded_port(output_port_text):
            log.warning("Detected excluded MIDI output port. Ignoring.")
            output_port_text = ""
        log.message(f"Reconnecting to: Midi In:\t'{input_port_text}'")
        log.message(f"Reconnecting to: Midi Out:\t'{output_port_text}'")
        success = self.midi_helper.reconnect_port_names(
            input_port_text, output_port_text
        )
        if not success:
            log.warning("Failed to reopen both MIDI ports")

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
        return self.input_combo.currentText()

    def get_output_port(self) -> str:
        """Get selected output port name

        Returns:
            Selected output port name or empty string if none selected
        """
        return self.output_combo.currentText()

    def get_settings(self) -> dict:
        """Get all selected settings

        Returns:
            Dictionary containing input_port and output_port selections
        """
        return {
            "input_port": self.get_input_port(),
            "output_port": self.get_output_port(),
        }
