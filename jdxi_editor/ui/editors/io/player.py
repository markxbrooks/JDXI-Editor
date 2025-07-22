"""
MIDI Player for JDXI Editor
"""

import cProfile
import io
import pstats
import re

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
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.utils.usb_recorder import USBRecorder
from jdxi_editor.ui.editors import SynthEditor
from jdxi_editor.ui.editors.io.midi_playback_state import MidiPlaybackState
from jdxi_editor.ui.editors.io.playback_worker import MidiPlaybackWorker
from jdxi_editor.ui.editors.io.recording_thread import WavRecordingThread
from jdxi_editor.ui.editors.io.ui_midi_player import UiMidi
from jdxi_editor.ui.editors.io.utils import format_time, tempo2bpm
from jdxi_editor.ui.widgets.display.digital import DigitalTitle
from jdxi_editor.ui.widgets.midi.track_viewer import MidiTrackViewer
from jdxi_editor.ui.widgets.midi.utils import get_total_duration_in_seconds
from jdxi_editor.ui.windows.jdxi.utils import show_message_box


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
        self._last_position_label = None
        self.parent = parent
        self.preset_helper = preset_helper
        self.profiler = None
        # Midi-related
        self.midi_state = MidiPlaybackState()
        if self.midi_state.custom_tempo_force:
            self.midi_state.tempo_at_position = self.midi_state.custom_tempo  # Use custom tempo if forced
        else:
            self.midi_state.tempo_at_position = MidiConstant.TEMPO_DEFAULT_120_BPM  # Default of 120 bpm
        self.midi_playback_worker = MidiPlaybackWorker(parent=self)
        self.midi_playback_worker.set_tempo.connect(self.update_tempo_us_from_worker)
        self.midi_port = self.midi_helper.midi_out
        self.midi_timer_init()
        # USB-related attributes
        self.usb_recording_rates = None
        self.usb_file_save_recording = True
        self.usb_port_input_device_index = None
        # self.usb_recording_thread = None
        self.usb_recorder = USBRecorder()
        # Initialize UI attributes
        self.ui = UiMidi()
        self.ui_init()

    def midi_timer_init(self):
        """
        Initialize or reinitialize the MIDI playback timer.
        Ensures previous connections are safely removed.
        """
        try:
            if self.midi_state.timer:
                self.midi_state.timer.stop()
                self.midi_state.timer.timeout.disconnect()
        except Exception as ex:
            log.warning(f"⚠️ Failed to disconnect old midi.timer: {ex}")

        timer = QTimer(self)
        timer.timeout.connect(self.midi_play_next_event)
        self.midi_state.timer = timer

    def ui_ensure_timer_connected(self):
        """
        ui_ensure_timer_connected

        :return:
        Ensure the midi_play_next_event is connected to midi.timer.timeout
        """

        try:
            self.midi_state.timer.timeout.disconnect(self.midi_play_next_event)
        except TypeError:
            pass  # Already disconnected
        except Exception as ex:
            log.warning(f"⚠️ Could not disconnect midi_play_next_event: {ex}")

        try:
            self.midi_state.timer.timeout.connect(self.midi_play_next_event)
        except Exception as ex:
            log.error(f"❌ Failed to connect midi_play_next_event: {ex}")

    def ui_init(self):
        """
        Initialize the UI for the MidiPlayer.
        """
        # Top horizontal layout: file title and right-hand controls
        header_layout = QHBoxLayout()
        self.ui.digital_title_file_name = DigitalTitle("No file loaded")
        header_layout.addWidget(self.ui.digital_title_file_name)

        right_panel_layout = QVBoxLayout()
        header_layout.addLayout(right_panel_layout)

        # Modular control sections
        right_panel_layout.addLayout(self.init_midi_file_controls())
        right_panel_layout.addLayout(self.init_usb_port_controls())
        right_panel_layout.addLayout(self.init_usb_file_controls())

        # Main vertical layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(header_layout)
        main_layout.addWidget(self.init_ruler())
        main_layout.addWidget(self.ui.midi_track_viewer)
        main_layout.addWidget(self.init_transport_controls())

        self.setLayout(main_layout)

    def init_ruler(self) -> QWidget:
        ruler_container = QWidget()
        ruler_layout = QHBoxLayout(ruler_container)
        ruler_layout.setContentsMargins(0, 0, 0, 0)
        ruler_layout.setSpacing(0)

        self.ui.position_label = QLabel("Playback Position: 0:00 / 0:00")
        self.ui.midi_track_viewer = MidiTrackViewer()
        self.ui.position_label.setFixedWidth(self.ui.midi_track_viewer.get_track_controls_width())
        ruler_layout.addWidget(self.ui.position_label)

        self.ui.midi_file_position_slider = QSlider(Qt.Horizontal)
        self.ui.midi_file_position_slider.setEnabled(False)
        self.ui.midi_file_position_slider.sliderReleased.connect(self.midi_scrub_position)
        ruler_layout.addWidget(self.ui.midi_file_position_slider, stretch=1)

        return ruler_container

    def init_midi_file_controls(self) -> QHBoxLayout:
        layout = QHBoxLayout()

        self.ui.load_button = QPushButton(qta.icon("mdi.midi-port", color=JDXiStyle.FOREGROUND), "Load MIDI File")
        self.ui.load_button.clicked.connect(self.midi_load_file)
        layout.addWidget(self.ui.load_button)

        self.ui.save_button = QPushButton(qta.icon("mdi.midi-port", color=JDXiStyle.FOREGROUND), "Save MIDI File")
        self.ui.save_button.clicked.connect(self.midi_save_file)
        layout.addWidget(self.ui.save_button)

        layout.addWidget(QLabel("Suppress MIDI Events:"))

        self.ui.midi_suppress_program_changes_checkbox = QCheckBox("Program Changes")
        self.ui.midi_suppress_program_changes_checkbox.setChecked(self.midi_state.suppress_program_changes)
        self.ui.midi_suppress_program_changes_checkbox.stateChanged.connect(self.on_suppress_program_changes_toggled)
        layout.addWidget(self.ui.midi_suppress_program_changes_checkbox)

        self.ui.midi_suppress_control_changes_checkbox = QCheckBox("Control Changes")
        self.ui.midi_suppress_control_changes_checkbox.setChecked(self.midi_state.suppress_control_changes)
        self.ui.midi_suppress_control_changes_checkbox.stateChanged.connect(self.on_suppress_control_changes_toggled)
        layout.addWidget(self.ui.midi_suppress_control_changes_checkbox)

        return layout

    def init_usb_port_controls(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.addWidget(QLabel("USB Port for recording"))

        self.ui.usb_port_select_combo = QComboBox()
        self.usb_populate_devices()
        layout.addWidget(self.ui.usb_port_select_combo)

        self.ui.usb_port_refresh_devices_button = QPushButton("Refresh USB device list")
        self.ui.usb_port_refresh_devices_button.pressed.connect(self.usb_populate_devices)
        layout.addWidget(self.ui.usb_port_refresh_devices_button)

        return layout

    def init_usb_file_controls(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.addWidget(QLabel("USB file to save recording"))

        self.ui.usb_file_select = QPushButton("No File Selected")
        self.ui.usb_file_select.clicked.connect(self.usb_select_recording_file)
        layout.addWidget(self.ui.usb_file_select)

        self.ui.usb_file_record_checkbox = QCheckBox("Save USB recording to file")
        self.ui.usb_file_record_checkbox.setChecked(self.usb_file_save_recording)
        self.ui.usb_file_record_checkbox.stateChanged.connect(self.on_usb_save_recording_toggled)
        layout.addWidget(self.ui.usb_file_record_checkbox)

        self.ui.usb_file_output_name = ""  # Set externally

        return layout

    def init_transport_controls(self) -> QGroupBox:
        group = QGroupBox("Transport")
        layout = QHBoxLayout(group)

        self.ui.play_button = QPushButton(qta.icon("ri.play-line", color=JDXiStyle.FOREGROUND), "Play")
        self.ui.play_button.clicked.connect(self.midi_playback_start)
        layout.addWidget(self.ui.play_button)

        self.ui.stop_button = QPushButton(qta.icon("ri.stop-line", color=JDXiStyle.FOREGROUND), "Stop")
        self.ui.stop_button.clicked.connect(self.midi_stop_playback)
        layout.addWidget(self.ui.stop_button)

        self.ui.pause_button = QPushButton(qta.icon("ri.pause-line", color=JDXiStyle.FOREGROUND), "Pause")
        self.ui.pause_button.clicked.connect(self.midi_playback_pause_toggle)
        layout.addWidget(self.ui.pause_button)

        return group

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
        if self.midi_state.playback_thread:
            self.midi_state.playback_thread.quit()
            self.midi_state.playback_thread.wait()
            self.midi_state.playback_thread.deleteLater()
            self.midi_playback_worker = None

        self.midi_playback_worker = MidiPlaybackWorker(parent=self)
        # self.midi_playback_worker.set_editor(self)

        self.midi_state.playback_thread = QThread()
        self.midi_playback_worker.moveToThread(self.midi_state.playback_thread)
        self.midi_playback_worker.result_ready.connect(self.midi_playback_worker_handle_result)  # optional for UI update

        # QTimer lives in the main thread, but calls worker.do_work()
        self.midi_state.timer = QTimer(self)
        self.midi_state.timer.setInterval(JDXiConstant.TIMER_INTERVAL)
        self.midi_state.timer.timeout.connect(self.midi_playback_worker.do_work)

        self.midi_state.playback_thread.start()

    def midi_playback_worker_stop(self):
        """
        stop_worker

        :return:
        """
        if self.midi_state.timer.isActive():
            self.midi_state.timer.stop()

        if self.midi_playback_worker:
            self.midi_playback_worker.stop()  # signal to stop processing

        if self.midi_state.playback_thread:
            self.midi_state.playback_thread.quit()
            self.midi_state.playback_thread.wait()
            self.midi_state.playback_thread.deleteLater()
            self.midi_state.playback_thread = None
            self.midi_playback_worker = None

    def on_suppress_program_changes_toggled(self, state: Qt.CheckState):
        """
        on_suppress_program_changes_toggled

        :param state: : Qt.CheckState
        :return:
        """
        self.midi_state.suppress_program_changes = (state == JDXiConstant.CHECKED)
        print(f"Suppress MIDI Program Changes = {self.midi_state.suppress_program_changes}")

    def on_suppress_control_changes_toggled(self, state: Qt.CheckState):
        """
        on_suppress_control_changes_toggled

        :param state: : Qt.CheckState
        :return:
        """
        self.midi_state.suppress_control_changes = (state == JDXiConstant.CHECKED)
        print(f"Suppress MIDI Control Changes = {self.midi_state.suppress_control_changes}")

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
        self.ui.usb_port_select_combo.clear()
        self.ui.usb_port_select_combo.addItems(usb_devices)
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
                self.ui.usb_port_select_combo.setCurrentIndex(i)
                self.usb_port_input_device_index = i
                log.message(f"Auto-selected {item}")
                break

    def usb_start_recording(self, recording_rate=pyaudio.paInt16):
        """Start recording in a separate thread."""
        try:
            if not self.ui.usb_file_output_name:
                log.message("No output file selected.")
                return

            selected_index = self.ui.usb_port_select_combo.currentIndex()
            self.usb_recorder.input_device_index = selected_index  # self.input_device_index
            self.usb_recording_thread = WavRecordingThread(recorder=self.usb_recorder,
                                                           duration=self.midi_state.file_duration_seconds + 10,
                                                           output_file=self.ui.usb_file_output_name,
                                                           recording_rate=recording_rate,  # e.g. pyaudio.paInt16
                                                           )
            self.usb_recording_thread.recording_finished.connect(self.on_usb_recording_finished)
            self.usb_recording_thread.recording_error.connect(self.on_usb_recording_error)
            self.usb_recording_thread.start()
            print("Recording started in background thread.")
        except Exception as ex:
            log.error(f"Error {ex} occurred starting recording")
            show_message_box("Error Saving File", f"Error {ex} occurred starting recording")

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
            self.ui.usb_file_select.setText(file_name)
            self.ui.usb_file_output_name = file_name
        else:
            self.ui.usb_file_output_name = ""

    def midi_save_file(self):
        """
        Save a MIDI file
        """
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save MIDI File", "", "MIDI Files (*.mid)"
        )
        if file_path:
            self.ui.midi_track_viewer.midi_file.save(file_path)
            self.ui.digital_title_file_name.setText(f"Saved: {Path(file_path).name}")

    def midi_load_file(self):
        """
        Load a MIDI file and initialize parameters
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open MIDI File", "", "MIDI Files (*.mid)"
        )
        if not file_path:
            return

        self.midi_state.file = MidiFile(file_path)
        self.ui.digital_title_file_name.setText(f"Loaded: {Path(file_path).name}")
        self.ui.midi_track_viewer.clear()
        self.ui.midi_track_viewer.set_midi_file(self.midi_state.file)

        self.ticks_per_beat = self.midi_state.file.ticks_per_beat

        # === Detect Initial Tempo ===
        self.midi_state.tempo_initial = MidiConstant.TEMPO_120_BPM_USEC
        initial_track_tempos = dict()
        for track_number, track in enumerate(self.midi_state.file.tracks):
            for msg in track:
                if msg.type == "set_tempo":
                    self.midi_state.tempo_initial = msg.tempo
                    log.parameter("self.tempo", self.midi_state.tempo_initial)
                    initial_track_tempos[track_number] = self.midi_state.tempo_initial
                    break
            else:
                continue  # no tempo message in this track
            break  # found tempo, break outer loop

        self.ui_display_set_tempo_usecs(self.midi_state.tempo_initial)
        self.midi_state.tempo_at_position = self.midi_state.tempo_initial  # Set initial tempo for playback
        log.parameter("Initial track tempos", initial_track_tempos)
        # === Detect a "reasonable" playback channel ===
        preferred_channels = {MidiChannel.DIGITAL_SYNTH_1,
                              MidiChannel.DIGITAL_SYNTH_2,
                              MidiChannel.ANALOG_SYNTH, 
                              MidiChannel.DRUM_KIT}  # MIDI channels 1, 2, 3, 10 (zero-based)
        selected_channel = None

        for track in self.midi_state.file.tracks:
            for msg in track:
                if hasattr(msg, "channel") and msg.channel in preferred_channels:
                    selected_channel = msg.channel
                    break
            if selected_channel is not None:
                break

        if selected_channel is None:
            selected_channel = 0  # default to channel 1 if nothing suitable found
            log.warning("No suitable channel found; defaulting to channel 1")

        self.midi_state.channel_selected = selected_channel
        log.parameter("Selected MIDI playback channel", self.midi_state.channel_selected)

        # === MIDI Event Collection ===
        events = []
        for track_index, track in enumerate(self.midi_state.file.tracks):
            abs_time = 0
            for msg in track:
                abs_time += msg.time
                events.append((abs_time, msg, track_index))
        self.tick_duration = self.midi_state.tempo_at_position / MidiConstant.TEMPO_CONVERT_SEC_TO_USEC / self.ticks_per_beat
        self.midi_state.events = sorted(events, key=lambda x: x[0])
        self.setup_worker()

        # === Accurate Total Duration Calculation ===
        self.total_ticks = max(t for t, _, _ in self.midi_state.events)
        self.midi_state.file_duration_seconds = get_total_duration_in_seconds(self.midi_state.file)

        self.tick_duration = self.midi_state.tempo_at_position / MidiConstant.TEMPO_CONVERT_SEC_TO_USEC / self.ticks_per_beat

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
        self.ui.digital_title_file_name.set_upper_display_text(
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
        if not output_file:
            log.error("Recording finished, but no output file returned.")
            return
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
            self.midi_state.timer.timeout.disconnect()  # optional: avoid duplicate connections
        except Exception as ex:
            log.error(f"error {ex} disconnecting timeout")
        try:
            self.midi_state.timer.timeout.connect(self.midi_playback_worker.do_work)
            log.message("Success: Connected midi_playback_worker.do_work to timeout")
        except Exception as ex:
            log.error(f"Error {ex} connecting timeout")
        try:
            self.midi_play_next_event_disconnect()
        except Exception as ex:
            log.error(f"Error {ex} connecting timeout")
        try:
            self.midi_state.timer.timeout.connect(self.midi_play_next_event)
            log.message("Success: Connected midi_play_next_event to timeout")
        except Exception as ex:
            log.error(f"Error {ex} connecting timeout")

        if not self.midi_state.file or not self.midi_state.events:
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
            self.midi_state.event_buffer.clear()
            self.midi_state.buffer_end_time = 0
            self.midi_state.event_index = 0
            self.midi_state.playback_start_time = time.time()

            self.setup_and_start_playback_worker()

        except Exception as ex:
            log.error(f"Error {ex} occurred starting playback")

    def setup_and_start_playback_worker(self):
        """
        setup_and_start_playback_worker

        :return: None
        Setup the MIDI playback worker and start the timer.
        """
        # Setup worker if not already initialized
        if not self.midi_state.playback_thread or not self.midi_playback_worker:
            self.setup_worker()
        self.ui_ensure_timer_connected()
        # === Prepare the buffered events for the worker ===
        self.midi_state.muted_channels = self.get_muted_channels()
        self.midi_state.muted_tracks = self.get_muted_tracks()
        self.midi_message_buffer_refill()
        self.midi_playback_worker.setup(
            buffered_msgs=self.midi_state.buffered_msgs,
            midi_out_port=self.midi_helper.midi_out,
            ticks_per_beat=self.midi_state.file.ticks_per_beat,
            play_program_changes=not self.midi_state.suppress_program_changes,
            start_time=self.midi_state.playback_start_time,
        )
        self.midi_state.timer.start()
        
    def midi_message_buffer_refill(self) -> None:
        """
        Preprocess MIDI tracks into a sorted list of (absolute_ticks, raw_bytes, tempo) tuples.
        Meta messages are excluded except for set_tempo.
        """
        self.initialize_midi_state()
        
        start_tick = self.calculate_start_tick()
        if start_tick is None:
            return
    
        self.process_tracks(start_tick)

    def initialize_midi_state(self) -> None:
        """
        Initialize muted tracks, muted channels, and buffered messages.
        """
        if self.midi_state.muted_tracks is None:
            self.midi_state.muted_tracks = set()
        if self.midi_state.muted_channels is None:
            self.midi_state.muted_channels = set()
        self.midi_state.buffered_msgs = []

    def calculate_start_tick(self) -> Optional[int]:
        """
        Calculate the start tick based on elapsed playback time.
        :return: Start tick or None if an error occurs.
        """
        try:
            elapsed_time_secs = time.time() - self.midi_state.playback_start_time
            return int(mido.second2tick(
                second=elapsed_time_secs,
                ticks_per_beat=self.midi_state.file.ticks_per_beat,
                tempo=self.midi_state.tempo_at_position
            ))
        except Exception as ex:
            log.error(f"Error converting playback start time to ticks: {ex}")
            return None
    
    def process_tracks(self, start_tick: int) -> None:
        """
        Process each MIDI track to populate the buffered messages.
        :param start_tick: The tick from which to start processing messages.
        """
        for i, track in enumerate(self.midi_state.file.tracks):
            if self.is_track_muted(i):
                log.message(f"🚫 Skipping muted track {i + MidiConstant.CHANNEL_DISPLAY_TO_BINARY} ({track.name})")
                continue
    
            self.process_track_messages(track, start_tick)
    
    def is_track_muted(self, track_index: int) -> bool:
        """
        Check if the track is muted.
        :param track_index: Index of the track to check.
        :return: True if the track is muted, otherwise False.
        """
        return track_index + MidiConstant.CHANNEL_DISPLAY_TO_BINARY in self.midi_state.muted_tracks
    
    def process_track_messages(self, track: mido.MidiTrack, start_tick: int) -> None:
        """
        Process messages in a MIDI track.
        :param track: The MIDI track to process.
        :param start_tick: The tick from which to start processing messages.
        """
        absolute_time_ticks = 0
        for msg in track:
            absolute_time_ticks += msg.time
    
            if absolute_time_ticks < start_tick:
                continue  # Skip messages before the start time
    
            if msg.type == 'set_tempo':
                self.handle_set_tempo(msg)
            else:
                self.buffer_message(absolute_time_ticks, msg)
    
    def handle_set_tempo(self, msg: mido.Message) -> None:
        """
        Handle 'set_tempo' messages in a MIDI track.
        :param msg: The MIDI message to process.
        """
        if self.midi_state.custom_tempo_force:
            self.midi_state.tempo_at_position = self.midi_state.custom_tempo
            log.message(f"🔄 Forcing custom tempo: {self.midi_state.tempo_at_position} usec")
        else:
            self.midi_state.tempo_at_position = msg.tempo

    def buffer_message(self, absolute_time_ticks: int, msg: mido.Message) -> None:
        """
        Add a MIDI message to the buffer.
        :param absolute_time_ticks: Absolute tick of the message.
        :param msg: The MIDI message to buffer.
        """
        self.midi_state.buffered_msgs.append((absolute_time_ticks, msg.bytes(), self.midi_state.tempo_at_position))
    
    def midi_message_buffer_refill_old(self) -> None:
        """
        midi_message_buffer_refill

        :return: None
        Preprocess MIDI tracks into a sorted list of (absolute_ticks, raw_bytes, tempo) tuples.
        Meta messages are excluded except for set_tempo.
        """
        if self.midi_state.muted_tracks is None:
            self.midi_state.muted_tracks = set()
        if self.midi_state.muted_channels is None:
            self.midi_state.muted_channels = set()
        self.midi_state.buffered_msgs = []

        try:
            elapsed_time_secs = time.time() - self.midi_state.playback_start_time
            start_tick = int(mido.second2tick(
                second=elapsed_time_secs,
                ticks_per_beat=self.midi_state.file.ticks_per_beat,
                tempo=self.midi_state.tempo_at_position
            ))
            log.parameter("start_tick", start_tick)
        except Exception as ex:
            log.error(f"Error converting playback start time to ticks: {ex}")
            return

        for i, track in enumerate(self.midi_state.file.tracks):
            if i + MidiConstant.CHANNEL_DISPLAY_TO_BINARY in self.midi_state.muted_tracks:
                log.message(f"🚫 Skipping muted track {i + MidiConstant.CHANNEL_DISPLAY_TO_BINARY} ({track.name})")
                continue
            absolute_time_ticks = 0

            for msg in track:
                absolute_time_ticks += msg.time

                if absolute_time_ticks < start_tick:
                    continue  # Skip messages before the start time

                if msg.type == 'set_tempo':
                    if self.midi_state.custom_tempo_force:
                        self.midi_state.tempo_at_position = self.midi_state.custom_tempo
                        log.message(f"🔄 Forcing custom tempo: {self.midi_state.tempo_at_position} usec")
                    else:
                        self.midi_state.tempo_at_position = msg.tempo
                    self.update_playback_worker_tempo_us(self.midi_state.tempo_at_position)
                    self.midi_state.buffered_msgs.append((absolute_time_ticks, None, self.midi_state.tempo_at_position))  # Store tempo change
                elif not msg.is_meta:
                    if hasattr(msg, "channel"):
                        # log.message(
                        #    f"🔍 Checking msg.channel={msg.channel +
                        #    MidiConstant.CHANNEL_BINARY_TO_DISPLAY} in
                        #    muted_channels={self.midi_state.muted_channels}")
                        if msg.channel + MidiConstant.CHANNEL_BINARY_TO_DISPLAY in self.midi_state.muted_channels:
                            # log.message(f"🚫 Skipping muted channel {msg.channel}")
                            continue
                    # log.message(f"🎵 Adding midi msg to buffer: {msg}")
                    raw_bytes = msg.bytes()
                    # log.message(f"Tick: {absolute_time_ticks}, Tempo: {self.midi_state.tempo_at_position}")
                    self.midi_state.buffered_msgs.append((absolute_time_ticks, raw_bytes, self.midi_state.tempo_at_position))

        self.midi_state.buffered_msgs.sort(key=lambda x: x[0])

    def get_muted_tracks(self):
        """
        get_muted_tracks

        :return: None
        Get the muted tracks from the MIDI track viewer.
        """
        muted_tracks_raw = self.ui.midi_track_viewer.get_muted_tracks()
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
        muted_channels_raw = self.ui.midi_track_viewer.get_muted_channels()
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
        self.midi_state.tempo_at_position = tempo

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
            elapsed_time = now - self.midi_state.playback_start_time
            self.ui_midi_file_position_slider_set_position(elapsed_time)
        except Exception as ex:
            log.error(f"Error {ex} occurred updating playback UI")

    def ui_midi_file_position_slider_set_position(self, elapsed_time: float) -> None:
        """
        ui.midi_file_position_slider_set_position

        :param elapsed_time: float
        :return: None
        Update the slider position and label based on elapsed time.
        """
        if self.ui.midi_file_position_slider.isSliderDown():
            return  # Don't update while user is dragging

        new_value = int(elapsed_time)
        current_value = self.ui.midi_file_position_slider.value()

        if abs(new_value - current_value) >= 1:  # Only update if full second has passed
            self.ui.midi_file_position_slider.setValue(new_value)
            self.ui_position_label_set_time(elapsed_time)
            
    def midi_scrub_position(self):
        """
        Updates the MIDI playback state based on the scrub position.
        """
        if not self.is_midi_ready():
            log.message("Either self.midi.file or self.midi.events not present, returning")
            return
    
        self.stop_playback()
        target_time = self.get_target_time()
        self.update_event_index(target_time)
        self.update_playback_start_time(target_time)
        self.stop_all_notes()
        self.prepare_for_playback()
    
    def is_midi_ready(self) -> bool:
        """
        Checks if the MIDI file and events are available.
        """
        return bool(self.midi_state.file and self.midi_state.events)

    def stop_playback(self) -> None:
        """
        Stops playback and resets the paused state.
        """
        self.midi_playback_worker_stop()
        self.midi_playback_worker_disconnect()
        self.midi_state.playback_paused = False  # Optional: reset paused state
    
    def get_target_time(self) -> float:
        """
        Retrieves the target time from the slider and logs it.
        """
        target_time = self.ui.midi_file_position_slider.value()
        log.parameter("target_time", target_time)
        return target_time

    def update_event_index(self, target_time: float) -> None:
        """
        Finds and updates the event index based on the target time.
        """
        for i, (tick, _, _) in enumerate(self.midi_state.events):
            if tick * self.tick_duration >= target_time:
                self.midi_state.event_index = i
                log.parameter("self.midi_state.event_index now", self.midi_state.event_index)
                return
        self.midi_state.event_index = 0  # Default to the start if no match
        
    def update_playback_start_time(self, target_time: float) -> None:
        """
        Adjusts the playback start time based on the scrub position.
        """
        scrub_tick = self.midi_state.events[self.midi_state.event_index][0]
        scrub_time = scrub_tick * self.tick_duration
        self.midi_state.playback_start_time = time.time() - scrub_time
        
    def stop_all_notes(self) -> None:
        """
        Stops all active MIDI notes.
        """
        if not self.midi_helper:
            return
    
        for ch in range(MidiConstant.MIDI_CHANNELS_NUMBER):
            self.midi_helper.midi_out.send_message(
                mido.Message("control_change", control=123, value=0, channel=ch).bytes()
            )
            for note in range(MidiConstant.MIDI_NOTES_NUMBER):
                self.midi_helper.midi_out.send_message(
                    mido.Message("note_off", note=note, velocity=0, channel=ch).bytes()
                )
    
    def prepare_for_playback(self) -> None:
        """
        Clears the event buffer and starts the playback worker.
        """
        self.midi_state.event_buffer.clear()
        self.setup_and_start_playback_worker()

    def midi_scrub_position_old(self):
        if not self.midi_state.file or not self.midi_state.events:
            log.message("Either self.midi.file or self.midi.events not present, returning")
            return

        # ❗ Stop playback before seeking
        self.midi_playback_worker_stop()
        self.midi_playback_worker_disconnect()
        self.midi_state.playback_paused = False  # Optional: reset paused state

        # Get new scrub position
        target_time = self.ui.midi_file_position_slider.value()
        log.parameter("target_time", target_time)

        # Update playback state
        # Get new scrub position from slider (in seconds)
        target_time = self.ui.midi_file_position_slider.value()
        log.parameter("target_time", target_time)

        # Find event index at or after target_time
        self.midi_state.event_index = 0
        for i, (tick, _, _) in enumerate(self.midi_state.events):
            if tick * self.tick_duration >= target_time:
                self.midi_state.event_index = i
                break

        # Calculate time offset from beginning of selected event
        scrub_tick = self.midi_state.events[self.midi_state.event_index][0]
        scrub_time = scrub_tick * self.tick_duration

        # Adjust playback_start_time so that:
        # current_time - playback_start_time == scrub_time
        self.midi_state.playback_start_time = time.time() - scrub_time

        self.midi_state.event_index = 0

        for i, (tick, _, _) in enumerate(self.midi_state.events):
            if tick * self.tick_duration >= target_time:
                self.midi_state.event_index = i
                log.parameter("self.midi_state.event_index now", self.midi_state.event_index)
                break

        # Stop all notes
        if self.midi_helper:
            for ch in range(MidiConstant.MIDI_CHANNELS_NUMBER):
                self.midi_helper.midi_out.send_message(
                    mido.Message("control_change", control=123, value=0, channel=ch).bytes())
                for note in range(MidiConstant.MIDI_NOTES_NUMBER):
                    self.midi_helper.midi_out.send_message(
                        mido.Message("note_off", note=note, velocity=0, channel=ch).bytes())

        self.midi_state.event_buffer.clear()
        self.setup_and_start_playback_worker()

    def midi_stop_playback(self):
        """
        Stop the playback and reset everything.
        """
        self.ui_position_slider_reset()
        self.midi_playback_worker_stop()
        self.midi_playback_worker_disconnect()
        self.midi_play_next_event_disconnect()
        self.midi_state.playback_paused = False
        self.midi_state.event_index = 0

        # Turn off all notes just in case
        if self.midi_helper:
            for ch in range(16):
                for note in range(128):
                    self.midi_helper.midi_out.send_message(mido.Message("note_off", note=note, velocity=0, channel=ch).bytes())

        self.ui_display_set_tempo_usecs(self.midi_state.tempo_initial)
        self.midi_state.active_notes.clear()
        self.usb_stop_recording()

        log.parameter("self.midi.event_buffer", self.midi_state.event_buffer)
        for t, msg in self.midi_state.event_buffer[:20]:
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
            self.midi_state.timer.timeout.disconnect(self.midi_play_next_event)
        except TypeError:
            log.warning("⚠️ midi_play_next_event was not connected to timeout signal.")
        except Exception as ex:
            log.warning(f"⚠️ Could not disconnect midi_play_next_event: {ex}")

    def midi_playback_worker_disconnect(self):
        # Disconnect do_work safely
        try:
            if hasattr(self, "midi_playback_worker") and self.midi_playback_worker is not None:
                self.midi_state.timer.timeout.disconnect(self.midi_playback_worker.do_work)
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
        self.ui.midi_file_position_slider.setEnabled(False)
        self.ui.midi_file_position_slider.setValue(0)
        self.ui.midi_file_position_slider.setEnabled(True)
        self.ui.midi_file_position_slider.setRange(0, int(self.midi_state.file_duration_seconds))
        self.ui_position_label_set_time()

    def ui_position_label_update_time(self, time_seconds: Optional[float] = None) -> None:
        """
        ui_position_label_update_time

        :param time_seconds: float, optional
        :return: None
        """
        if time_seconds is None:
            self.ui.position_label.setText(f"Playback Position: 0:00 / {format_time(self.midi_state.file_duration_seconds)}")

    def ui_position_label_set_time(self, elapsed_time: Optional[float] = None) -> None:
        """
        Update the position label with formatted elapsed time and total duration.
        Caps elapsed_time to total duration to prevent overflow display.
        """
        total = self.midi_state.file_duration_seconds
        if elapsed_time is None:
            elapsed_str = "0:00"
        else:
            elapsed_capped = min(elapsed_time, total)
            elapsed_str = format_time(elapsed_capped)

        total_str = format_time(total)
        label_text = f"Playback Position: {elapsed_str} / {total_str}"
        if getattr(self, "_last_position_label", "") != label_text:
            self.ui.position_label.setText(label_text)
            self._last_position_label = label_text

    def midi_playback_pause_toggle(self):
        """
        midi_playback_pause_toggle

        :return: None
        Toggle pause and resume playback.
        """
        if not self.midi_state.file or not self.midi_state.timer:
            return

        if not self.midi_state.playback_paused:
            # Pausing playback
            self.midi_state.playback_paused_time = time.time()
            self.midi_state.timer.stop()
            self.midi_state.playback_paused = True
            self.ui.pause_button.setText("Resume")
        else:
            # Resuming playback
            if self.midi_state.playback_paused_time and self.midi_state.playback_start_time:
                pause_duration = time.time() - self.midi_state.playback_paused_time
                self.midi_state.playback_start_time += pause_duration  # Adjust start time
            self.midi_state.timer.start()
            self.midi_state.playback_paused = False
            self.ui.pause_button.setText("Pause")

    def midi_playback_worker_handle_result(self, result=None):
        """
        Handle the result from the worker.
        This can be used to update the UI or perform further actions.
        :param result: The result from the worker
        """
        pass
