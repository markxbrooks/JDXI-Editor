"""
MIDI Player for JDXI Editor
"""

import cProfile
import io
import pstats
import re
from collections import defaultdict
import mido
import time
from pathlib import Path
from typing import Optional
import pyaudio
from mido import MidiFile, bpm2tempo

from PySide6.QtCore import Qt, QTimer, QThread
from PySide6.QtWidgets import (
    QVBoxLayout,
    QPushButton,
    QComboBox,
    QFileDialog,
    QLabel,
    QDoubleSpinBox,
    QSlider,
    QGroupBox, QHBoxLayout, QWidget, QCheckBox,
)
import qtawesome as qta

from jdxi_editor.globals import PROFILING
from jdxi_editor.jdxi.midi.constant import JDXiConstant, MidiConstant
from jdxi_editor.jdxi.preset.helper import JDXiPresetHelper
from jdxi_editor.jdxi.style import JDXiStyle
from jdxi_editor.log.logger import Logger as log
from jdxi_editor.midi.channel.channel import MidiChannel
from jdxi_editor.midi.data.programs.digital import DIGITAL_PRESET_LIST
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.utils.usb_recorder import USBRecorder
from jdxi_editor.ui.editors import SynthEditor
from jdxi_editor.ui.editors.io.playback_worker import MidiPlaybackWorker
from jdxi_editor.ui.editors.io.recording_thread import WavRecordingThread
from jdxi_editor.ui.editors.io.utils import format_time
from jdxi_editor.ui.widgets.display.digital import DigitalTitle
from jdxi_editor.ui.widgets.midi.track_viewer import MidiTrackViewer
from jdxi_editor.ui.widgets.midi.utils import get_total_duration_in_seconds


def tempo2bpm(tempo: int) -> float:
    """
    tempo2bpm

    :param tempo: float
    :return: float
    """
    return 60_000_000 / tempo


def get_last_tempo(midi_file: MidiFile) -> int:
    """
    get_last_tempo

    :param midi_file: MidiFile
    :return: int
    """
    tempo = MidiConstant.TEMPO_120_BPM_USEC  # 500_000 default
    for track in midi_file.tracks:
        for msg in track:
            if msg.type == 'set_tempo':
                tempo = msg.tempo
    return tempo


class MidiFileEditor(SynthEditor):
    """
    Midi File Editor
    """

    BUFFER_WINDOW_SECONDS = 30.0

    def __init__(
            self,
            midi_helper: Optional[MidiIOHelper] = None,
            parent: QWidget = None,
            preset_helper: JDXiPresetHelper = None,
    ):
        """
        Initialize the MidiPlayer

        :param midi_helper: Optional[MidiIOHelper]
        :param parent: Optional[QWidget]
        :param preset_helper: Optional[JDXIPresetHelper]
        """
        super().__init__()
        self.parent = parent
        self.preset_helper = preset_helper
        self.profiler = None
        # Midi-related
        self.midi_active_notes = defaultdict(set)
        self.midi_buffer_end_time = 0
        self.midi_buffered_msgs = None
        self.midi_custom_tempo_force = False
        self.midi_custom_tempo = MidiConstant.TEMPO_162_BPM_USEC  # Default custom tempo in microseconds
        self.midi_channel_selected = MidiChannel.DIGITAL_SYNTH_1  # Default channel for playback
        if self.midi_custom_tempo_force:
            self.midi_tempo_at_position = self.midi_custom_tempo  # Use custom tempo if forced
        else:
            self.midi_tempo_at_position = MidiConstant.TEMPO_DEFAULT_120_BPM  # Default of 120 bpm
        self.midi_events = []
        self.midi_event_index_current = 0
        self.midi_event_index = None
        self.midi_event_buffer = []
        self.midi_file = None
        self.midi_file_duration_seconds = 0
        self.midi_helper = midi_helper if midi_helper else MidiIOHelper()
        self.midi_muted_tracks = None
        self.midi_muted_channels = None
        self.midi_playback_worker = None
        self.midi_playback_thread = None
        self.midi_playback_paused_time = None
        self.midi_playback_start_time = None
        self.midi_playback_paused = False
        self.midi_playback_worker = MidiPlaybackWorker(parent=self)
        self.midi_playback_worker.set_tempo.connect(self.update_tempo_us_from_worker)
        self.midi_port = self.midi_helper.midi_out
        self.midi_suppress_control_changes = True
        self.midi_suppress_program_changes = True
        self.midi_tempo_initial = MidiConstant.TEMPO_120_BPM_USEC  # Default tempo in microseconds
        self.midi_tempo_at_position = MidiConstant.TEMPO_120_BPM_USEC  # Default tempo in microseconds
        self.midi_timer = None
        self.midi_timer_init()
        # USB-related attributes
        self.usb_recording_rates = None
        self.usb_file_save_recording = True
        self.usb_port_input_device_index = None
        # self.usb_recording_thread = None
        self.usb_recorder = USBRecorder()
        # Initialize UI attributes
        self.ui_digital_title_file_name = None
        self.ui_load_button = None
        self.ui_midi_file_position_slider = None
        self.ui_midi_suppress_program_changes_checkbox = None
        self.ui_midi_suppress_control_changes_checkbox = None
        self.ui_midi_track_viewer = None
        self.ui_play_button = None
        self.ui_position_label = None
        self.ui_stop_button = None
        self.ui_save_button = None
        self.ui_tempo_spin = None
        self.ui_usb_file_select = None
        self.ui_usb_file_output_name = None
        self.ui_usb_file_record_checkbox = None
        self.ui_usb_port_select_combo = None
        self.ui_usb_port_refresh_devices_button = None
        self.ui_init()

    def midi_timer_init(self):
        """
        Initialize or reinitialize the MIDI playback timer.
        Ensures previous connections are safely removed.
        """
        try:
            if hasattr(self, "midi_timer") and self.midi_timer:
                self.midi_timer.stop()
                self.midi_timer.timeout.disconnect()
        except Exception as ex:
            log.warning(f"⚠️ Failed to disconnect old midi_timer: {ex}")

        self.midi_timer = QTimer(self)
        self.midi_timer.timeout.connect(self.midi_play_next_event)

    def ui_ensure_timer_connected(self):
        """
        ui_ensure_timer_connected

        :return:
        Ensure the midi_play_next_event is connected to midi_timer.timeout
        """

        try:
            self.midi_timer.timeout.disconnect(self.midi_play_next_event)
        except TypeError:
            pass  # Already disconnected
        except Exception as ex:
            log.warning(f"⚠️ Could not disconnect midi_play_next_event: {ex}")

        try:
            self.midi_timer.timeout.connect(self.midi_play_next_event)
        except Exception as ex:
            log.error(f"❌ Failed to connect midi_play_next_event: {ex}")

    def ui_init(self):
        """
        Initialize the UI for the MidiPlayer
        """
        midi_player_hlayout = QHBoxLayout()
        self.ui_digital_title_file_name = DigitalTitle("No file loaded")
        midi_player_hlayout.addWidget(self.ui_digital_title_file_name)

        midi_player_vlayout = QVBoxLayout()
        midi_player_hlayout.addLayout(midi_player_vlayout)

        # file load / save selection
        midi_file_layout = QHBoxLayout()
        midi_player_vlayout.addLayout(midi_file_layout)
        self.ui_load_button = QPushButton(
            qta.icon("mdi.midi-port", color=JDXiStyle.FOREGROUND), "Load MIDI File"
        )
        self.ui_load_button.clicked.connect(self.midi_load_file)
        midi_file_layout.addWidget(self.ui_load_button)

        self.ui_save_button = QPushButton("Save MIDI File")
        self.ui_save_button = QPushButton(
            qta.icon("mdi.midi-port", color=JDXiStyle.FOREGROUND), "Save MIDI File"
        )
        self.ui_save_button.clicked.connect(self.midi_save_file)
        midi_file_layout.addWidget(self.ui_save_button)

        midi_file_layout.addWidget(QLabel("Suppress MIDI Events:"))
        self.ui_midi_suppress_program_changes_checkbox = QCheckBox("Program Changes")
        self.ui_midi_suppress_program_changes_checkbox.setChecked(self.midi_suppress_program_changes)
        midi_file_layout.addWidget(self.ui_midi_suppress_program_changes_checkbox)
        self.ui_midi_suppress_program_changes_checkbox.stateChanged.connect(
            self.on_suppress_program_changes_toggled
        )

        self.ui_midi_suppress_control_changes_checkbox = QCheckBox("Control Changes")
        self.ui_midi_suppress_control_changes_checkbox.setChecked(self.midi_suppress_control_changes)
        midi_file_layout.addWidget(self.ui_midi_suppress_control_changes_checkbox)
        # Then connect signals to these methods:

        self.ui_midi_suppress_control_changes_checkbox.stateChanged.connect(
            self.on_suppress_control_changes_toggled
        )

        ui_usb_port_layout = QHBoxLayout()
        midi_player_vlayout.addLayout(ui_usb_port_layout)
        ui_usb_port_layout.addWidget(QLabel("USB Port for recording"))
        self.ui_usb_port_select_combo = QComboBox()
        self.usb_populate_devices()
        ui_usb_port_layout.addWidget(self.ui_usb_port_select_combo)

        self.ui_usb_port_refresh_devices_button = QPushButton("Refresh USB device list")
        self.ui_usb_port_refresh_devices_button.pressed.connect(self.usb_populate_devices)
        # self.usb_port_jdxi_auto_connect(usb_devices)
        ui_usb_port_layout.addWidget(self.ui_usb_port_refresh_devices_button)

        # usb port and file selection
        ui_usb_file_layout = QHBoxLayout()
        midi_player_vlayout.addLayout(ui_usb_file_layout)
        ui_usb_file_layout.addWidget(QLabel("USB file to save recording"))
        self.ui_usb_file_select = QPushButton("No File Selected")
        ui_usb_file_layout.addWidget(self.ui_usb_file_select)
        self.ui_usb_file_record_checkbox = QCheckBox("Save USB recording to file")
        self.ui_usb_file_record_checkbox.setChecked(self.usb_file_save_recording)
        ui_usb_file_layout.addWidget(self.ui_usb_file_record_checkbox)

        self.ui_usb_file_select.clicked.connect(self.usb_select_recording_file)
        self.ui_usb_file_record_checkbox.stateChanged.connect(self.on_usb_save_recording_toggled)
        self.ui_usb_file_output_name = ""

        self.ui_midi_file_position_slider = QSlider(Qt.Horizontal)
        self.ui_midi_file_position_slider.setEnabled(False)
        self.ui_midi_file_position_slider.sliderReleased.connect(self.midi_scrub_position)
        layout = QVBoxLayout()
        layout.addLayout(midi_player_hlayout)
        # layout.addWidget(QLabel("Playback Position"))
        # layout.addWidget(self.position_slider)
        ruler_container = QWidget()
        ruler_layout = QHBoxLayout(ruler_container)
        ruler_layout.setContentsMargins(0, 0, 0, 0)
        ruler_layout.setSpacing(0)

        self.ui_position_label = QLabel("Playback Position: 0:00 / 0:00")
        self.ui_midi_track_viewer = MidiTrackViewer()
        self.ui_position_label.setFixedWidth(self.ui_midi_track_viewer.get_track_controls_width())  # same width as controls
        ruler_layout.addWidget(self.ui_position_label)

        ruler_layout.addWidget(self.ui_midi_file_position_slider, stretch=1)

        layout.addWidget(ruler_container)
        layout.addWidget(self.ui_midi_track_viewer)

        transport_group = QGroupBox("Transport")
        transport_layout = QHBoxLayout()
        transport_group.setLayout(transport_layout)
        # self.play_button = QPushButton("Play")
        self.ui_play_button = QPushButton(
            qta.icon("ri.play-line", color=JDXiStyle.FOREGROUND), "Play"
        )
        self.ui_play_button.clicked.connect(self.midi_playback_start)
        transport_layout.addWidget(self.ui_play_button)

        self.ui_stop_button = QPushButton(
            qta.icon("ri.stop-line", color=JDXiStyle.FOREGROUND), "Stop"
        )
        self.ui_pause_button = QPushButton(
            qta.icon("ri.pause-line", color=JDXiStyle.FOREGROUND), "Pause"
        )
        self.ui_stop_button.clicked.connect(self.midi_stop_playback)
        self.ui_pause_button.clicked.connect(self.midi_playback_pause_toggle)
        transport_layout.addWidget(self.ui_stop_button)
        transport_layout.addWidget(self.ui_pause_button)
        layout.addWidget(transport_group)
        self.setLayout(layout)

    def update_tempo_us_from_worker(self, tempo_us: int) -> None:
        """
        update_tempo_us

        :param tempo_us: tempo in microseconds e.g  500_000
        :return: None
        """
        log.parameter("tempo_us", tempo_us)
        log.message(f"Updating tempo to {tempo_us} microseconds from worker")
        # self.refill_midi_message_buffer()
        self.ui_display_set_tempo_usecs(tempo_us)

    def update_playback_worker_tempo_us(self, tempo_us: int) -> None:
        """
        update_tempo_us

        :param tempo_us: tempo in microseconds e.g  500_000
        :return: None
        """
        log.parameter("tempo_us", tempo_us)
        log.message(f"Updating tempo to {tempo_us} microseconds from editor")
        if self.midi_playback_worker:
            self.midi_playback_worker.update_tempo(tempo_us)

    def setup_worker(self):
        """
        Setup the worker and thread for threaded playback using QTimer
        """
        # Clean up any previous worker/thread
        if self.midi_playback_thread:
            self.midi_playback_thread.quit()
            self.midi_playback_thread.wait()
            self.midi_playback_thread.deleteLater()
            self.midi_playback_worker = None

        self.midi_playback_worker = MidiPlaybackWorker(parent=self)
        # self.midi_playback_worker.set_editor(self)

        self.midi_playback_thread = QThread()
        self.midi_playback_worker.moveToThread(self.midi_playback_thread)
        self.midi_playback_worker.result_ready.connect(self.midi_playback_worker_handle_result)  # optional for UI update

        # QTimer lives in the main thread, but calls worker.do_work()
        self.midi_timer = QTimer(self)
        self.midi_timer.setInterval(JDXiConstant.TIMER_INTERVAL)
        self.midi_timer.timeout.connect(self.midi_playback_worker.do_work)

        self.midi_playback_thread.start()

    def midi_playback_worker_stop(self):
        """
        stop_worker

        :return:
        """
        if self.midi_timer.isActive():
            self.midi_timer.stop()

        if self.midi_playback_worker:
            self.midi_playback_worker.stop()  # signal to stop processing

        if self.midi_playback_thread:
            self.midi_playback_thread.quit()
            self.midi_playback_thread.wait()
            self.midi_playback_thread.deleteLater()
            self.midi_playback_thread = None
            self.midi_playback_worker = None

    def on_suppress_program_changes_toggled(self, state: Qt.CheckState):
        """
        on_suppress_program_changes_toggled

        :param state: : Qt.CheckState
        :return:
        """
        self.midi_suppress_program_changes = (state == JDXiConstant.CHECKED)
        print(f"Suppress MIDI Program Changes = {self.midi_suppress_program_changes}")

    def on_suppress_control_changes_toggled(self, state: Qt.CheckState):
        """
        on_suppress_control_changes_toggled

        :param state: : Qt.CheckState
        :return:
        """
        self.midi_suppress_control_changes = (state == JDXiConstant.CHECKED)
        print(f"Suppress MIDI Control Changes = {self.midi_suppress_control_changes}")

    def on_usb_save_recording_toggled(self, state: Qt.CheckState):
        """
        on_usb_save_recording_toggled

        :param state: : Qt.CheckState
        :return:
        """
        self.usb_file_save_recording = (state == JDXiConstant.CHECKED)
        print(f"save USB recording = {self.usb_file_save_recording}")

    def usb_populate_devices(self) -> None:
        """
        midi port selection

        :return: None
        """
        usb_devices = self.usb_recorder.list_devices()
        self.ui_usb_port_select_combo.clear()
        self.ui_usb_port_select_combo.addItems(usb_devices)
        self.usb_port_jdxi_auto_connect(usb_devices)
        return usb_devices

    def usb_port_jdxi_auto_connect(self, usb_devices: list) -> None:
        """
        usb_port_jdxi_auto_connect

        :param usb_devices:
        :return: None
        Auto-select the first matching device
        """
        pattern = re.compile(r'jd-?xi', re.IGNORECASE)
        for i, item in enumerate(usb_devices):
            if pattern.search(item):
                self.ui_usb_port_select_combo.setCurrentIndex(i)
                self.usb_port_input_device_index = i
                log.message(f"Auto-selected {item}")
                break

    def usb_start_recording(self, recording_rate=pyaudio.paInt16):
        """Start recording in a separate thread."""
        try:
            if not self.ui_usb_file_output_name:
                log.message("No output file selected.")
                return

            selected_index = self.ui_usb_port_select_combo.currentIndex()
            self.usb_recorder.input_device_index = selected_index  # self.input_device_index
            self.usb_recording_thread = WavRecordingThread(recorder=self.usb_recorder,
                                                           duration=self.midi_file_duration_seconds + 10,
                                                           output_file=self.ui_usb_file_output_name,
                                                           recording_rate=recording_rate,  # e.g. pyaudio.paInt16
                                                           )
            self.usb_recording_thread.recording_finished.connect(self.on_usb_recording_finished)
            self.usb_recording_thread.recording_error.connect(self.on_usb_recording_error)
            self.usb_recording_thread.start()
            print("Recording started in background thread.")
        except Exception as ex:
            log.error(f"Error {ex} occurred starting recording")

    def usb_stop_recording(self):
        """
        stop_recording

        :return: None
        """
        try:
            if hasattr(self, "usb_recording_thread"):
                self.usb_recording_thread.stop_recording()
        except Exception as ex:
            log.error(f"Error {ex} occurred stopping USB recording")

    def usb_select_recording_file(self):
        """Open a file picker dialog to select output .wav file."""
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save Recording As",
            "",  # starting directory
            "WAV files (*.wav)",  # filter
        )
        if file_name:
            self.ui_usb_file_select.setText(file_name)
            self.ui_usb_file_output_name = file_name
        else:
            self.ui_usb_file_output_name = ""

    def midi_save_file(self):
        """
        Save a MIDI file
        """
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save MIDI File", "", "MIDI Files (*.mid)"
        )
        if file_path:
            self.ui_midi_track_viewer.midi_file.save(file_path)
            self.ui_digital_title_file_name.setText(f"Saved: {Path(file_path).name}")

    def midi_load_file(self):
        """
        Load a MIDI file and initialize parameters
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open MIDI File", "", "MIDI Files (*.mid)"
        )
        if not file_path:
            return

        self.midi_file = MidiFile(file_path)
        self.ui_digital_title_file_name.setText(f"Loaded: {Path(file_path).name}")
        self.ui_midi_track_viewer.clear()
        self.ui_midi_track_viewer.set_midi_file(self.midi_file)

        self.ticks_per_beat = self.midi_file.ticks_per_beat

        # === Detect Initial Tempo ===
        self.midi_tempo_initial = MidiConstant.TEMPO_120_BPM_USEC
        initial_track_tempos = dict()
        for track_number, track in enumerate(self.midi_file.tracks):
            for msg in track:
                if msg.type == "set_tempo":
                    self.midi_tempo_initial = msg.tempo
                    log.parameter("self.tempo", self.midi_tempo_initial)
                    initial_track_tempos[track_number] = self.midi_tempo_initial
                    break
            else:
                continue  # no tempo message in this track
            break  # found tempo, break outer loop

        self.ui_display_set_tempo_usecs(self.midi_tempo_initial)
        self.midi_tempo_at_position = self.midi_tempo_initial  # Set initial tempo for playback
        log.parameter("Initial track tempos", initial_track_tempos)
        # === Detect a "reasonable" playback channel ===
        preferred_channels = {MidiChannel.DIGITAL_SYNTH_1,
                              MidiChannel.DIGITAL_SYNTH_2,
                              MidiChannel.ANALOG_SYNTH, 
                              MidiChannel.DRUM_KIT}  # MIDI channels 1, 2, 3, 10 (zero-based)
        selected_channel = None

        for track in self.midi_file.tracks:
            for msg in track:
                if hasattr(msg, "channel") and msg.channel in preferred_channels:
                    selected_channel = msg.channel
                    break
            if selected_channel is not None:
                break

        if selected_channel is None:
            selected_channel = 0  # default to channel 1 if nothing suitable found
            log.warning("No suitable channel found; defaulting to channel 1")

        self.midi_channel_selected = selected_channel
        log.parameter("Selected MIDI playback channel", self.midi_channel_selected)

        # === MIDI Event Collection ===
        events = []
        for track_index, track in enumerate(self.midi_file.tracks):
            abs_time = 0
            for msg in track:
                abs_time += msg.time
                events.append((abs_time, msg, track_index))
        self.tick_duration = self.midi_tempo_at_position / MidiConstant.TEMPO_CONVERT_SEC_TO_USEC / self.ticks_per_beat
        self.midi_events = sorted(events, key=lambda x: x[0])
        self.setup_worker()

        # === Accurate Total Duration Calculation ===
        self.total_ticks = max(t for t, _, _ in self.midi_events)
        self.midi_file_duration_seconds = get_total_duration_in_seconds(self.midi_file)

        self.tick_duration = self.midi_tempo_at_position / MidiConstant.TEMPO_CONVERT_SEC_TO_USEC / self.ticks_per_beat

        # === UI Updates ===
        self.ui_position_slider_reset()

    def ui_display_set_tempo_usecs(self, tempo_usecs: int) -> None:
        """
        set_display_tempo

        :param tempo_usecs: int tempo in microseconds
        :return: None
        Set the tempo in the UI and log it.
        """
        log.message(f"Setting tempo to {tempo_usecs} microseconds on UI")
        self.on_tempo_usecs_changed(tempo_usecs)
        bpm = tempo2bpm(tempo_usecs)
        log.parameter("tempo_bpm", bpm)
        log.message(f"Setting tempo to {bpm} BPM on UI")
        self.set_display_tempo_bpm(bpm)

    def set_display_tempo_bpm(self, tempo_bpm: float) -> None:
        """
        set_display_tempo_bpm

        :param tempo_bpm: int tempo in microseconds
        :return: None
        Set the tempo in the UI and log it.
        """
        self.ui_digital_title_file_name.set_upper_display_text(
            f"Tempo: {round(tempo_bpm)} BPM"
        )
        log.parameter("tempo_bpm", tempo_bpm)
        return None

    def on_usb_recording_finished(self, output_file: str):
        """
        on_recording_finished

        :param output_file: str
        :return: None
        """
        log.message(f"Recording finished. File successfully saved to {output_file}")

    def on_usb_recording_error(self, message: str):
        """
        on_recording_error

        :param message: str
        :return: None
        """
        log.error(f"Error during recording: {message}")

    def midi_playback_start(self):
        """
        Start playback of the MIDI file
        """
        # In setup_worker or midi_start_playback
        self.ui_position_slider_reset()

        if PROFILING:
            self.profiler = cProfile.Profile()
            self.profiler.enable()

        try:
            self.midi_timer.timeout.disconnect()  # optional: avoid duplicate connections
        except Exception as ex:
            log.error(f"error {ex} disconnecting timeout")
        try:
            self.midi_timer.timeout.connect(self.midi_playback_worker.do_work)
            log.message("Success: Connected midi_playback_worker.do_work to timeout")
        except Exception as ex:
            log.error(f"Error {ex} connecting timeout")
        try:
            self.midi_play_next_event_disconnect()
        except Exception as ex:
            log.error(f"Error {ex} connecting timeout")
        try:
            self.midi_timer.timeout.connect(self.midi_play_next_event)
            log.message("Success: Connected midi_play_next_event to timeout")
        except Exception as ex:
            log.error(f"Error {ex} connecting timeout")

        if not self.midi_file or not self.midi_events:
            return

        if self.usb_file_save_recording:
            recording_rate = "32bit"  # Default to 32-bit recording
            try:
                self.usb_recording_rates = {
                    "16bit": pyaudio.paInt16,
                    "32bit": pyaudio.paInt32
                }
                rate = self.usb_recording_rates.get(recording_rate, pyaudio.paInt16)
                self.usb_start_recording(recording_rate=rate)
            except Exception as ex:
                log.error(f"Error {ex} occurred starting USB recording")

        try:
            # Clear buffer and reset playback position
            self.midi_event_buffer.clear()
            self.midi_buffer_end_time = 0
            self.midi_event_index = 0

            # Setup worker if not already initialized
            if not self.midi_playback_thread or not self.midi_playback_worker:
                self.setup_worker()
            self.ui_ensure_timer_connected()

            # === Prepare the buffered events for the worker ===
            self.midi_muted_channels = self.get_muted_channels()

            self.midi_muted_tracks = self.get_muted_tracks()
            self.midi_message_buffer_refill()
            self.midi_playback_worker.setup(
                buffered_msgs=self.midi_buffered_msgs,
                midi_out_port=self.midi_helper.midi_out,
                ticks_per_beat=self.midi_file.ticks_per_beat,
                play_program_changes=not self.midi_suppress_program_changes
            )
            self.midi_playback_start_time = time.time()
            self.midi_timer.start()

        except Exception as ex:
            log.error(f"Error {ex} occurred starting playback")

    def midi_message_buffer_refill(self) -> None:
        """
        midi_message_buffer_refill

        :return: None
        Preprocess MIDI tracks into a sorted list of (absolute_ticks, raw_bytes, tempo) tuples.
        Meta messages are excluded except for set_tempo.
        """
        if self.midi_muted_tracks is None:
            self.midi_muted_tracks = set()
        if self.midi_muted_channels is None:
            self.midi_muted_channels = set()

        self.midi_buffered_msgs = []

        for i, track in enumerate(self.midi_file.tracks):
            if i + MidiConstant.CHANNEL_DISPLAY_TO_BINARY in self.midi_muted_tracks:
                log.message(f"🚫 Skipping muted track {i + MidiConstant.CHANNEL_DISPLAY_TO_BINARY} ({track.name})")
                continue
            absolute_time_ticks = 0

            for msg in track:
                absolute_time_ticks += msg.time

                if msg.type == 'set_tempo':
                    if self.midi_custom_tempo_force:
                        self.midi_tempo_at_position = self.midi_custom_tempo
                        log.message(f"🔄 Forcing custom tempo: {self.midi_tempo_at_position} usec")
                    else:
                        self.midi_tempo_at_position = msg.tempo
                    self.update_playback_worker_tempo_us(self.midi_tempo_at_position)
                    self.midi_buffered_msgs.append((absolute_time_ticks, None, self.midi_tempo_at_position))  # Store tempo change
                elif not msg.is_meta:
                    if hasattr(msg, "channel"):
                        log.message(
                            f"🔍 Checking msg.channel={msg.channel + MidiConstant.CHANNEL_BINARY_TO_DISPLAY} in muted_channels={self.midi_muted_channels}")
                        if msg.channel + MidiConstant.CHANNEL_BINARY_TO_DISPLAY in self.midi_muted_channels:
                            log.message(f"🚫 Skipping muted channel {msg.channel}")
                            continue
                    log.message(f"🎵 Adding midi msg to buffer: {msg}")
                    raw_bytes = msg.bytes()
                    log.message(f"Tick: {absolute_time_ticks}, Tempo: {self.midi_tempo_at_position}")
                    self.midi_buffered_msgs.append((absolute_time_ticks, raw_bytes, self.midi_tempo_at_position))

        self.midi_buffered_msgs.sort(key=lambda x: x[0])

    def get_muted_tracks(self):
        """
        get_muted_tracks

        :return: None
        Get the muted tracks from the MIDI track viewer.
        """
        muted_tracks_raw = self.ui_midi_track_viewer.get_muted_tracks()
        muted_tracks = {int(t) for t in muted_tracks_raw if not isinstance(t, set)}
        for track in muted_tracks:
            log.parameter("Muted track", track)
        return muted_tracks

    def get_muted_channels(self):
        """
        get_muted_channels

        :return: None
        Get the muted channels from the MIDI track viewer.
        """
        muted_channels_raw = self.ui_midi_track_viewer.get_muted_channels()
        muted_channels = {int(c) for c in muted_channels_raw if not isinstance(c, set)}
        log.parameter("Muted channels", muted_channels)
        for channel in muted_channels:
            log.parameter("Muted channel", channel)
        return muted_channels

    def on_tempo_usecs_changed(self, tempo: int):
        """
        on_tempo_usecs_changed

        :param tempo: int
        :return: None
        """
        self.midi_tempo_at_position = tempo

    def on_tempo_bpm_changed(self, bpm: float):
        """
        on_tempo_bpm_changed

        :param bpm: float
        :return: None
        """
        tempo = bpm2tempo(bpm)
        self.on_tempo_usecs_changed(tempo)

    def midi_play_next_event(self):
        """
        UI update: Update slider and label to reflect playback progress.
        """
        try:
            now = time.time()
            elapsed_time = now - self.midi_playback_start_time
            self.ui_midi_file_position_slider_set_position(elapsed_time)
        except Exception as ex:
            log.error(f"Error {ex} occurred updating playback UI")

    def ui_midi_file_position_slider_set_position(self, elapsed_time: float) -> None:
        """
        ui_midi_file_position_slider_set_position

        :param elapsed_time: float
        :return: None
        Update the slider position and label based on elapsed time.
        """
        if self.ui_midi_file_position_slider.isSliderDown():
            return  # Don't update while user is dragging

        new_value = int(elapsed_time)
        current_value = self.ui_midi_file_position_slider.value()

        if abs(new_value - current_value) >= 1:  # Only update if full second has passed
            self.ui_midi_file_position_slider.setValue(new_value)
            self.ui_position_label.setText(
                f"Playback Position: {format_time(elapsed_time)} / {format_time(self.midi_file_duration_seconds)}"
            )

    def midi_scrub_position(self):
        """
        Scrub to a new position in the file using the slider.
        Resets start time and event index to match new slider position.
        """
        if not self.midi_file or not self.midi_events:
            log.message("Either self.midi_file or self.midi_events not present, returning")
            return

        target_time = self.ui_midi_file_position_slider.value()
        log.parameter("target_time", target_time)
        self.midi_playback_start_time = time.time() - target_time
        self.midi_event_index = 0

        log.parameter("self.midi_event_index was", self.midi_event_index)
        for i, (tick, _, _) in enumerate(self.midi_events):
            if tick * self.tick_duration >= target_time:
                self.midi_event_index = i
                log.parameter("self.midi_event_index now", self.midi_event_index)
                break

        # Stop all notes to avoid hanging
        if self.midi_helper:
            for ch in range(16):
                for note in range(128):
                    self.midi_helper.midi_out.send_message(mido.Message("note_off", note=note, velocity=0, channel=ch).bytes())
        # Clear the event buffer and refill it
        self.midi_event_buffer.clear()
        self.midi_message_buffer_refill()

    def midi_stop_playback(self):
        """
        Stop the playback and reset everything.
        """
        self.ui_position_slider_reset()
        self.midi_playback_worker_stop()
        self.midi_playback_worker_disconnect()
        self.midi_play_next_event_disconnect()
        self.midi_playback_paused = False
        self.midi_event_index = 0

        # Turn off all notes just in case
        if self.midi_helper:
            for ch in range(16):
                for note in range(128):
                    self.midi_helper.midi_out.send_message(mido.Message("note_off", note=note, velocity=0, channel=ch).bytes())

        self.ui_display_set_tempo_usecs(self.midi_tempo_initial)
        self.midi_active_notes.clear()
        self.usb_stop_recording()

        log.parameter("self.midi_event_buffer", self.midi_event_buffer)
        for t, msg in self.midi_event_buffer[:20]:
            log.message(f"Queued @ {t:.3f}s: {msg}")

        if PROFILING:
            self.profiler.disable()
            s = io.StringIO()
            sortby = 'cumtime'  # or 'tottime'
            ps = pstats.Stats(self.profiler, stream=s).sort_stats(sortby)
            ps.print_stats(50)  # Top 50 entries
            log.message(s.getvalue())

    def midi_play_next_event_disconnect(self):
        """
        midi_play_next_event_disconnect

        :return: None
        Disconnect the midi_play_next_event from the timer's timeout signal.
        """
        # Disconnect midi_play_next_event safely
        try:
            self.midi_timer.timeout.disconnect(self.midi_play_next_event)
        except TypeError:
            log.warning("⚠️ midi_play_next_event was not connected to timeout signal.")
        except Exception as ex:
            log.warning(f"⚠️ Could not disconnect midi_play_next_event: {ex}")

    def midi_playback_worker_disconnect(self):
        # Disconnect do_work safely
        try:
            if hasattr(self, "midi_playback_worker") and self.midi_playback_worker is not None:
                self.midi_timer.timeout.disconnect(self.midi_playback_worker.do_work)
        except TypeError:
            log.warning("⚠️ do_work was not connected to timeout signal.")
        except Exception as ex:
            log.warning(f"⚠️ Could not disconnect do_work: {ex}")

    def ui_position_slider_reset(self) -> None:
        """
        position_slider_reset

        :return: None
        Reset the position slider and label to initial state.
        """
        self.ui_midi_file_position_slider.setEnabled(False)
        self.ui_midi_file_position_slider.setValue(0)
        self.ui_midi_file_position_slider.setEnabled(True)
        self.ui_midi_file_position_slider.setRange(0, int(self.midi_file_duration_seconds))
        self.ui_position_label.setText(f"Playback Position: 0:00 / {format_time(self.midi_file_duration_seconds)}")

    def midi_playback_pause_toggle(self):
        """
        midi_playback_pause_toggle

        :return: None
        Toggle pause and resume playback.
        """
        if not self.midi_file or not self.midi_timer:
            return

        if not self.midi_playback_paused:
            # Pausing playback
            self.midi_playback_paused_time = time.time()
            self.midi_timer.stop()
            self.midi_playback_paused = True
            self.ui_pause_button.setText("Resume")
        else:
            # Resuming playback
            if self.midi_playback_paused_time and self.midi_playback_start_time:
                pause_duration = time.time() - self.midi_playback_paused_time
                self.midi_playback_start_time += pause_duration  # Adjust start time
            self.midi_timer.start()
            self.midi_playback_paused = False
            self.ui_pause_button.setText("Pause")

    def midi_playback_worker_handle_result(self, result=None):
        """
        Handle the result from the worker.
        This can be used to update the UI or perform further actions.
        :param result: The result from the worker
        """
        pass
