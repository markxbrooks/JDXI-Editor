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
import sys

import qtawesome as qta
from decologr import Decologr as log
from picoui.specs.widgets import ButtonSpec
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
)

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.pattern.preset_list_provider import (
    get_hardware_interface,
    get_sf2_path,
    get_use_soundfont_list,
    set_hardware_interface,
    set_sf2_path,
    set_use_soundfont_list,
)
from jdxi_editor.ui.layout.helper import add_round_button_from_spec
from jdxi_editor.ui.style import JDXiUIDimensions
from jdxi_editor.ui.widgets.digital.title import DigitalTitle

# In-app FluidSynth defaults
HW_PORT_HINT = "Roland JDXi"  # adjust if your port name differs
SF2_PATH = os.path.expanduser("~/SoundFonts/FluidR3_GM.sf2")


def _get_output_devices() -> list[tuple[str, str]]:
    """
    Get list of (display_name, device_spec) for audio output devices.

    On macOS: device_spec is the name (for CoreAudio).
    On Windows/Linux: device_spec is "index:HostApi:Name" (for PortAudio).
    Requires sounddevice.
    """
    try:
        import sounddevice as sd

        devices = sd.query_devices()
        hostapis = sd.query_hostapis()
        output_devices = [
            (i, d) for i, d in enumerate(devices) if d["max_output_channels"] > 0
        ]
        result = []
        for idx, d in output_devices:
            name = d["name"]
            if sys.platform != "darwin":
                hostapi_idx = d.get("hostapi", 0)
                hostapi_name = hostapis[hostapi_idx].get("name", "Unknown")
                spec = f"{idx}:{hostapi_name}:{name}"
                result.append((name, spec))
            else:
                result.append((name, name))
        return result
    except Exception:
        return []


class MIDIConfigDialog(QDialog):
    def __init__(self, midi_helper=MidiIOHelper, parent=None):
        super().__init__(parent)
        self.setWindowTitle("MIDI Configuration")
        self.setMinimumSize(
            JDXiUIDimensions.Config.WIDTH, JDXiUIDimensions.Config.HEIGHT
        )
        self.setStyleSheet(JDXi.UI.Style.EDITOR)
        self.midi_helper = midi_helper
        self.input_ports = midi_helper.get_input_ports()
        self.output_ports = midi_helper.get_output_ports()
        self.current_in = midi_helper.current_in
        self.current_out = midi_helper.current_out
        # FluidSynth runtime state (optional)
        self.fs = None
        self.sfid = None
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
        layout = QVBoxLayout(self)

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
        self.input_combo.addItems(self.input_ports)
        if self.current_in and self.current_in in self.input_ports:
            self.input_combo.setCurrentText(self.current_in)
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
        self.output_combo.addItems(self.output_ports)
        if self.current_out and self.current_out in self.output_ports:
            self.output_combo.setCurrentText(self.current_out)
        self.output_combo.currentIndexChanged.connect(self._on_output_combo_changed)

        output_layout.addWidget(self.output_combo)
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
            "Use SoundFont drum names (GM percussion) for the Drums row "
            "in the Pattern editor instead of built-in JD-Xi names"
        )
        self.use_soundfont_list.setChecked(get_use_soundfont_list())
        synth_layout.addWidget(self.use_soundfont_list)

        # Hardware Interface (audio output device for FluidSynth)
        hw_row = QHBoxLayout()
        hw_row.addWidget(QLabel("Hardware Interface:"))
        self.hardware_interface_combo = QComboBox()
        self.hardware_interface_combo.setToolTip(
            "Audio output device for FluidSynth playback. "
            "Requires sounddevice (pip install sounddevice)."
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
        self.accept = add_round_button_from_spec(ok_btn_spec)
        cancel_btn_spec = ButtonSpec(
            label="Cancel",
            icon=JDXi.UI.Icon.CANCEL,
            slot=self.reject,
            layout=dialog_btn_row,
        )
        self.reject = add_round_button_from_spec(cancel_btn_spec)
        dialog_btn_row.addStretch()
        layout.addLayout(dialog_btn_row)

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
        self.hardware_interface_combo.clear()
        devices = _get_output_devices()
        if devices:
            self.hardware_interface_combo.addItem("(Default)", "")
            for display_name, device_spec in devices:
                self.hardware_interface_combo.addItem(display_name, device_spec)
            saved = get_hardware_interface()
            idx = self.hardware_interface_combo.findText(saved)
            self.hardware_interface_combo.setCurrentIndex(idx if idx >= 0 else 0)
        else:
            self.hardware_interface_combo.addItem(
                "(sounddevice not installed)",
                "",
            )

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
        self.input_combo.addItems(self.input_ports)
        self.output_combo.clear()
        self.output_combo.addItems(self.output_ports)

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
            # Add to combo if missing and select
            self._ensure_sf2_in_combo(file_path)
            self._select_sf2_in_combo(file_path)

    def _start_fluidsynth(self) -> None:
        try:
            from fluidsynth import Synth
        except Exception as ex:
            self.fs_status.setText("FluidSynth not installed: pip install pyfluidsynth")
            log.warning(f"FluidSynth import failed: {ex}")
            return

        try:
            sf_path = self.sf2_edit.text().strip()
            if not sf_path:
                self.fs_status.setText("Please select a SoundFont first.")
                return

            if self.fs is None:
                self.fs = Synth()
                device_name = self.hardware_interface_combo.currentText()
                if device_name and device_name not in (
                    "(Default)",
                    "(sounddevice not installed)",
                ):
                    if sys.platform == "darwin":
                        # macOS: use CoreAudio with specific device (accepts device name)
                        try:
                            self.fs.setting("audio.coreaudio.device", device_name)
                            self.fs.start(driver="coreaudio")
                        except Exception as ex:
                            log.warning(
                                f"Could not set CoreAudio device '{device_name}': {ex}"
                            )
                            self.fs.start(driver="coreaudio")  # fallback to default
                    else:
                        # Windows/Linux: use PortAudio with "index:HostApi:Name" format
                        device_spec = self.hardware_interface_combo.currentData()
                        try:
                            if isinstance(device_spec, str) and ":" in device_spec:
                                self.fs.setting("audio.driver", "portaudio")
                                self.fs.setting("audio.portaudio.device", device_spec)
                                self.fs.start(driver="portaudio")
                            else:
                                self.fs.start()
                        except Exception as ex:
                            log.warning(f"Could not set PortAudio device: {ex}")
                            self.fs.start()
                else:
                    self.fs.start(
                        driver="coreaudio" if sys.platform == "darwin" else None
                    )

            self.sfid = self.fs.sfload(sf_path)
            self.fs.program_select(0, self.sfid, 0, 0)
            self.fs_status.setText("FluidSynth: started")

        except Exception as ex:
            self.fs_status.setText(f"FluidSynth error: {ex}")
            log.error(f"FluidSynth error: {ex}")

    def _stop_fluidsynth(self) -> None:
        try:
            if self.fs is not None:
                self.fs.delete()
                self.fs = None
                self.fs_status.setText("FluidSynth: stopped")
        except Exception as ex:
            self.fs_status.setText(f"Stop error: {ex}")
            log.error(f"FluidSynth stop error: {ex}")

    def _test_fluidsynth(self) -> None:
        try:
            if self.fs is None:
                self.fs_status.setText("Start FluidSynth first.")
                return
            # Middle C test
            self.fs.noteon(0, 60, 110)
            self.fs.noteoff(0, 60)
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
        log.message(f"Reconnecting to: Midi In:\t'{input_port_text}'")
        log.message(f"Reconnecting to: Midi Out:\t'{output_port_text}'")
        success = self.midi_helper.reconnect_port_names(
            input_port_text, output_port_text
        )
        if not success:
            log.warning("Failed to reopen both MIDI ports")

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
