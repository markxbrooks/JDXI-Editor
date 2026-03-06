"""
USB Recording Widget
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Optional

import pyaudio
from PySide6.QtCore import Qt, QMargins
from PySide6.QtWidgets import QLabel, QPushButton, QCheckBox, QComboBox, QGridLayout, QHBoxLayout

from decologr import Decologr as log
from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.playback.state import MidiPlaybackState
from jdxi_editor.midi.utils.helpers import start_recording
from jdxi_editor.midi.utils.usb_recorder import USBRecorder
from jdxi_editor.ui.editors.helpers.widgets import create_jdxi_button_from_spec
from jdxi_editor.ui.editors.midi_player.helper import create_widget_cell_with_button_spec
from jdxi_editor.ui.widgets.editor.helper import create_icon_and_label
from jdxi_editor.ui.widgets.jdxi.widget import JDXiMidiGrid
from jdxi_editor.ui.windows.jdxi.utils import show_message_box_from_spec
from picoui.specs.widgets import ButtonSpec, FileSelectionSpec, FileSelectionMode, get_file_save_from_spec


class USBFileRecordingWidget(JDXiMidiGrid):
    """USB File Recording Widget"""

    def __init__(self, midi_state: MidiPlaybackState, parent=None):
        super().__init__(midi_state=midi_state, parent=parent)
        """constructor"""
        self.grid_title: str = "USB Recorder"
        self.recorder: USBRecorder = USBRecorder(channels=1)
        self.file_select: QPushButton = QPushButton()
        self.file_output_name: str = ""
        self.file_record_checkbox: QCheckBox = QCheckBox()
        self.port_refresh_devices_label: QLabel | None = None
        self.file_auto_generate_checkbox: QCheckBox | None = None
        self.port_select_combo: QComboBox = QComboBox()
        self.port_refresh_devices_button: QPushButton = QPushButton()
        self.setup_ui()

    def _build_button_specs(self) -> dict[str, ButtonSpec]:
        return {
            "usb_port_refresh": ButtonSpec(
                label="Refresh",
                tooltip="Refresh list of USB devices",
                icon=JDXi.UI.Icon.REFRESH,
                slot=self.populate_devices,
            ),
        }

    def _build_layout(self, grid: QGridLayout, row: int):
        """build layout"""
        # --- Row 1: USB Port
        usb_port_layout, usb_port_label = create_icon_and_label(
            label="Port", icon=JDXi.UI.Icon.USB
        )
        grid.addLayout(usb_port_layout, row, 0)
        self.port_select_combo = QComboBox()
        self.populate_devices()
        grid.addWidget(self.port_select_combo, row, 1, 1, 2)
        spec = self.specs["buttons"]["usb_port_refresh"]
        self.port_refresh_devices_button = create_jdxi_button_from_spec(
            spec, checkable=False
        )
        refresh_usb_cell, self.port_refresh_devices_label = (
            create_widget_cell_with_button_spec(
                spec, self.port_refresh_devices_button
            )
        )
        grid.addWidget(refresh_usb_cell, row, 3)
        row += 1

        # --- Row 2: File to save recording
        file_layout, file_label = create_icon_and_label(
            label="File", icon=JDXi.UI.Icon.SAVE
        )
        grid.addLayout(file_layout, row, 0)
        self.file_select = QPushButton("No File Selected")
        self.file_select.clicked.connect(self.select_recording_file)
        grid.addWidget(self.file_select, row, 1, 1, 2)  # 2 = colspan I guess
        # row += 1

        # --- Row 2 still: Save USB recording checkbox
        self.file_record_checkbox = QCheckBox("Save")
        JDXi.UI.Theme.apply_button_mini_style(self.file_record_checkbox)
        self.file_record_checkbox.setChecked(
            self.recorder.file_save_recording
        )
        self.file_record_checkbox.stateChanged.connect(
            self.on_usb_save_recording_toggled
        )
        grid.addWidget(self.file_record_checkbox, row, 3)
        # row += 1

        # --- Row 3: Auto-generate WAV filename checkbox
        self.file_auto_generate_checkbox = QCheckBox(
            "Auto-filename"
        )
        JDXi.UI.Theme.apply_button_mini_style(self.file_auto_generate_checkbox)
        self.file_auto_generate_checkbox.setChecked(False)
        self.file_auto_generate_checkbox.stateChanged.connect(
            self.on_usb_file_auto_generate_toggled
        )
        grid.addWidget(self.file_auto_generate_checkbox, row, 4)

    def start_recording(self):
        """start usb recording"""
        if self.recorder.file_save_recording:
            recording_rate = "32bit"  # Default to 32-bit recording
            try:
                rate = self.recorder.usb_recording_rates.get(
                    recording_rate, pyaudio.paInt16
                )
                self._start_recording(recording_rate=rate)
            except Exception as ex:
                log.error(f"Error {ex} occurred starting USB recording")

    def on_usb_save_recording_toggled(self, state: Qt.CheckState):
        """
        on_usb_save_recording_toggled

        :param state: Qt.CheckState
        :return:
        """
        self.recorder.file_save_recording = state == JDXi.UI.Constants.CHECKED
        log.message(f"save USB recording = {self.recorder.file_save_recording}")

    def on_usb_file_auto_generate_toggled(self, state: Qt.CheckState):
        """
        on_usb_file_auto_generate_toggled

        :param state: Qt.CheckState
        :return:
        """
        self.file_auto_generate_checkbox.setChecked(
            state == JDXi.UI.Constants.CHECKED
        )
        is_enabled = self.file_auto_generate_checkbox.isChecked()
        log.message(
            f"Auto generate filename based on current date and time and Midi file = {is_enabled}"
        )
        self.update_auto_wav_filename()

    def populate_devices(self) -> list:
        """
        usb_populate_devices

        usb port selection

        :return: list List of USB devices
        """
        usb_devices = self.recorder.list_devices()
        self.port_select_combo.clear()
        self.port_select_combo.addItems(usb_devices)
        self.port_jdxi_auto_connect(usb_devices)
        return usb_devices

    def port_jdxi_auto_connect(self, usb_devices: list) -> None:
        """
        usb_port_jdxi_auto_connect

        :param usb_devices: list
        :return: None

        Auto-select the first matching device
        """
        pattern = re.compile(r"jd-?xi", re.IGNORECASE)
        for i, item in enumerate(usb_devices):
            if pattern.search(item):
                self.port_select_combo.setCurrentIndex(i)
                self.recorder.usb_port_input_device_index = i
                log.message(f"Auto-selected {item}")
                break

    def on_usb_file_output_name_changed(self, state: Qt.CheckState):
        """
        on_usb_file_output_name_changed

        :param state: Qt.CheckState
        :return:
        """
        self.file_auto_generate_checkbox.setChecked(
            state == JDXi.UI.Constants.CHECKED
        )
        log.message(
            f"Auto generate filename based on current date and time and Midi file = {self.file_auto_generate_checkbox.isChecked()}"
        )

    def _start_recording(self, recording_rate: int = pyaudio.paInt16):
        """
        usb_start_recording

        :param recording_rate: int
        :return: None
        Start recording in a separate thread
        """
        try:
            # If auto-generate is enabled, regenerate filename with fresh timestamp
            if self.file_auto_generate_checkbox.isChecked():
                self.update_auto_wav_filename()

            if not self.file_output_name:
                log.warning(
                    "⚠️ No output file selected for WAV recording. Please select a file or enable auto-generate."
                )
                show_message_box_from_spec(self.specs["message_box"]["no_output_file"])
                return

            log.message(f"🎙️ Starting WAV recording to: {self.file_output_name}")
            log.message(
                f"🎙️ Recording duration: {self.midi_state.file_duration_seconds} seconds"
            )

            selected_index = self.port_select_combo.currentIndex()
            log.message(f"🎙️ Using USB input device index: {selected_index}")

            start_recording(
                self.recorder,
                self.midi_state.file_duration_seconds,
                self.file_output_name,
                recording_rate,
                selected_index,
            )
        except Exception as ex:
            log.error(f"❌ Error {ex} occurred starting recording")
            import traceback

            log.error(traceback.format_exc())
            show_message_box_from_spec(
                self.specs["message_box"]["error_saving_file"],
                message=f"Error {ex} occurred starting recording",
            )

    def generate_auto_wav_filename(self) -> Optional[str]:
        """
        Generate an automatic WAV filename based on current date/time and MIDI file name.

        :return: Generated filename path or None if no MIDI file is loaded
        """
        if (
            not self.midi_state.file
            or not hasattr(self.midi_state.file, "filename")
            or not self.midi_state.file.filename
        ):
            return None

        # Get MIDI file path
        midi_path = Path(self.midi_state.file.filename)
        midi_stem = midi_path.stem  # filename without extension

        # Generate timestamp: YYYYMMDD_HHMMSS
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create WAV filename: YYYYMMDD_HHMMSS_<midi_filename>.wav
        wav_filename = f"{timestamp}_{midi_stem}.wav"

        # Use the same directory as the MIDI file, or current directory if no path
        if midi_path.parent:
            wav_path = midi_path.parent / wav_filename
        else:
            wav_path = Path(wav_filename)

        return str(wav_path)

    def update_auto_wav_filename(self) -> None:
        """
        Update the WAV filename automatically if auto-generate is enabled.
        """
        if self.file_auto_generate_checkbox.isChecked():
            auto_filename = self.generate_auto_wav_filename()
            if auto_filename:
                self.file_output_name = auto_filename
                self.file_select.setText(Path(auto_filename).name)
                log.message(f"Auto-generated WAV filename: {auto_filename}")
            else:
                log.warning("⚠️ Cannot auto-generate filename: No MIDI file loaded")

    def select_recording_file(self):
        """Open a file picker dialog to select output .wav file."""
        file_name_spec = FileSelectionSpec(
            mode=FileSelectionMode.SAVE,
            filter="WAV files (*.wav)",
            caption="Save Recording As",
        )
        file_name = get_file_save_from_spec(file_name_spec, parent=self)
        if file_name:
            self.file_select.setText(file_name)
            self.file_output_name = file_name
        else:
            self.file_output_name = ""
