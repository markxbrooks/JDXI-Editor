import sys
from pathlib import Path
from typing import Optional

import mido
from mido import MidiFile, Message, open_output, tempo2bpm, bpm2tempo
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog, QLabel, QComboBox, QSlider, \
    QGroupBox
from PySide6.QtCore import QTimer, Qt
import qtawesome as qta
from jdxi_editor.midi.data.constants.constants import MIDI_CHANNEL_DIGITAL1
from jdxi_editor.midi.data.programs.presets import DIGITAL_PRESET_LIST
from jdxi_editor.midi.io import MidiIOHelper
from jdxi_editor.midi.preset.helper import PresetHelper
from jdxi_editor.ui.editors import SynthEditor
from jdxi_editor.ui.widgets.display.digital import DigitalDisplay, DigitalTitle

import sys
from pathlib import Path
from typing import Optional

import mido
from mido import MidiFile, Message, open_output
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog, QLabel, QComboBox
from PySide6.QtCore import QTimer

from jdxi_editor.midi.data.constants.constants import MIDI_CHANNEL_DIGITAL1
from jdxi_editor.midi.data.programs.presets import DIGITAL_PRESET_LIST
from jdxi_editor.midi.io import MidiIOHelper
from jdxi_editor.midi.preset.helper import PresetHelper
from jdxi_editor.ui.editors import SynthEditor
from jdxi_editor.ui.widgets.display.digital import DigitalDisplay, DigitalTitle

from midi_track_widget import MidiTrackWidget  # Import the new widget

class MidiPlayer(SynthEditor):
    def __init__(self,
                 midi_helper=Optional[MidiIOHelper],
                 parent=None,
                 preset_helper=None):
        super().__init__()
        self.init_ui()
        self.midi_helper = midi_helper if midi_helper else MidiIOHelper()
        self.preset_helper = preset_helper if preset_helper else PresetHelper(self.midi_helper,
                                                                              presets=DIGITAL_PRESET_LIST,
                                                                              channel=MIDI_CHANNEL_DIGITAL1)
        self.midi_file = None
        self.midi_port = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.play_next_event)
        self.midi_iterator = iter([])
        self.start_time = None
        self.current_time = 0

    def init_ui(self):
        layout = QVBoxLayout()

        self.file_label = DigitalTitle("No file loaded")
        layout.addWidget(self.file_label)

        self.load_button = QPushButton("Load MIDI File")
        self.load_button.clicked.connect(self.load_midi)
        layout.addWidget(self.load_button)

        self.port_select = QComboBox()
        self.port_select.addItems(mido.get_output_names())
        layout.addWidget(self.port_select)

        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.start_playback)
        layout.addWidget(self.play_button)

        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_playback)
        layout.addWidget(self.stop_button)

        self.midi_track_widget = MidiTrackWidget()
        layout.addWidget(self.midi_track_widget)

        self.setLayout(layout)

    def load_midi(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open MIDI File", "", "MIDI Files (*.mid)")
        if file_path:
            self.midi_file = MidiFile(file_path)
            self.file_label.setText(f"Loaded: {Path(file_path).name}")
            self.midi_iterator = iter(self.midi_file.tracks[0])
            self.midi_track_widget.set_midi_file(self.midi_file)

    def start_playback(self):
        if not self.midi_file:
            return

        port_name = self.port_select.currentText()
        if not port_name:
            return

        self.midi_port = open_output(port_name)
        self.current_time = 0
        self.midi_iterator = iter(self.midi_file.play())
        self.timer.start(1)

    def play_next_event(self):
        try:
            msg = next(self.midi_iterator)
            if isinstance(msg, Message):
                self.midi_port.send(msg)
        except StopIteration:
            self.stop_playback()

    def stop_playback(self):
        self.timer.stop()
        if self.midi_port:
            self.midi_port.close()


import time
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QVBoxLayout, QPushButton, QComboBox,
    QFileDialog, QLabel, QDoubleSpinBox
)

from mido import MidiFile, Message, open_output


class MidiPlayer(SynthEditor):
    def __init__(self,
                 midi_helper: Optional[MidiIOHelper] = None,
                 parent=None,
                 preset_helper=None):
        super().__init__()
        self.init_ui()
        self.midi_helper = midi_helper if midi_helper else MidiIOHelper()
        self.preset_helper = preset_helper if preset_helper else PresetHelper(
            self.midi_helper,
            presets=DIGITAL_PRESET_LIST,
            channel=MIDI_CHANNEL_DIGITAL1
        )

        self.midi_file = None
        self.midi_port = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.play_next_event)

        self.midi_events = []
        self.current_event_index = 0
        self.start_time = None
        self.duration_seconds = 0
        self.paused = False

    def init_ui(self):
        layout = QVBoxLayout()

        self.file_label = DigitalTitle("No file loaded")
        layout.addWidget(self.file_label)

        self.load_button = QPushButton("Load MIDI File")
        self.load_button.clicked.connect(self.load_midi)
        layout.addWidget(self.load_button)

        self.port_select = QComboBox()
        self.port_select.addItems(mido.get_output_names())
        layout.addWidget(self.port_select)

        self.tempo_spin = QDoubleSpinBox()
        self.tempo_spin.setRange(20, 300)
        self.tempo_spin.setValue(120)
        self.tempo_spin.setSuffix(" BPM")
        layout.addWidget(QLabel("Tempo"))
        layout.addWidget(self.tempo_spin)

        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setEnabled(False)
        self.position_slider.sliderReleased.connect(self.scrub_position)
        layout.addWidget(QLabel("Playback Position"))
        layout.addWidget(self.position_slider)

        self.position_label = QLabel("0:00 / 0:00")
        layout.addWidget(self.position_label)

        transport_group = QGroupBox("Transport")
        transport_layout = QVBoxLayout()
        transport_group.setLayout(transport_layout)
        # self.play_button = QPushButton("Play")
        self.play_button = QPushButton(qta.icon("ri.play-line"), "Play")
        self.play_button.clicked.connect(self.start_playback)
        transport_layout.addWidget(self.play_button)

        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_playback)
        transport_layout.addWidget(self.stop_button)
        layout.addWidget(transport_group)
        self.setLayout(layout)

    def format_time(self, seconds: float) -> str:
        mins = int(seconds) // 60
        secs = int(seconds) % 60
        return f"{mins}:{secs:02}"

    def load_midi(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open MIDI File", "", "MIDI Files (*.mid)"
        )
        if file_path:
            self.midi_file = MidiFile(file_path)
            self.file_label.setText(f"Loaded: {Path(file_path).name}")

            self.ticks_per_beat = self.midi_file.ticks_per_beat
            self.tempo = 500000  # default 120 BPM

            # Look for a tempo message in track 0
            for msg in self.midi_file.tracks[0]:
                if msg.type == "set_tempo":
                    self.tempo = msg.tempo
                    break

            bpm = tempo2bpm(self.tempo)
            self.tempo_spin.setValue(round(bpm))

            events = []
            for track in self.midi_file.tracks:
                abs_time = 0
                for msg in track:
                    abs_time += msg.time
                    events.append((abs_time, msg))

            self.midi_events = sorted(events, key=lambda x: x[0])

            # Compute total duration in seconds
            self.total_ticks = max(t for t, _ in self.midi_events)
            tempo = bpm2tempo(self.tempo_spin.value())
            self.tick_duration = tempo / 1_000_000 / self.ticks_per_beat
            self.duration_seconds = self.total_ticks * self.tick_duration

            self.position_slider.setEnabled(True)
            self.position_slider.setRange(0, int(self.duration_seconds))
            self.position_label.setText(f"0:00 / {self.format_time(self.duration_seconds)}")

    def start_playback(self):
        if not self.midi_file or not self.midi_events:
            return

        port_name = self.port_select.currentText()
        if not port_name:
            return

        self.midi_port = open_output(port_name)
        self.start_time = time.time()
        self.event_index = 0
        self.timer.start(10)  # check every 10ms

    def play_next_event(self):
        if self.event_index >= len(self.midi_events):
            self.stop_playback()
            return

        now = time.time()
        elapsed_time = now - self.start_time
        self.position_slider.setValue(int(elapsed_time))
        self.position_label.setText(
            f"{self.format_time(elapsed_time)} / {self.format_time(self.duration_seconds)}"
        )

        while self.event_index < len(self.midi_events):
            tick_time, msg = self.midi_events[self.event_index]
            scheduled_time = tick_time * self.tick_duration

            if elapsed_time >= scheduled_time:
                if not msg.is_meta:
                    self.midi_port.send(msg)
                self.event_index += 1
            else:
                break

    def scrub_position(self):
        new_seconds = self.position_slider.value()
        self.start_time = time.time() - new_seconds

        # Find the correct event index based on new time
        new_tick = new_seconds / self.tick_duration
        for i, (tick, _) in enumerate(self.midi_events):
            if tick >= new_tick:
                self.event_index = i
                break

    def stop_playback(self):
        self.timer.stop()
        if self.midi_port:
            self.midi_port.close()
        self.position_slider.setValue(0)
        self.position_label.setText(
            f"0:00 / {self.format_time(self.duration_seconds)}"
        )


class MidiPlayerNew(SynthEditor):
    def __init__(self,
                 midi_helper: Optional[MidiIOHelper] = None,
                 parent=None,
                 preset_helper=None):
        super().__init__()
        self.init_ui()
        self.midi_helper = midi_helper if midi_helper else MidiIOHelper()
        self.preset_helper = preset_helper if preset_helper else PresetHelper(
            self.midi_helper,
            presets=DIGITAL_PRESET_LIST,
            channel=MIDI_CHANNEL_DIGITAL1
        )

        self.midi_file = None
        self.midi_port = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.play_next_event)

        self.midi_events = []
        self.current_event_index = 0
        self.start_time = None

    def init_ui(self):
        layout = QVBoxLayout()

        self.file_label = DigitalTitle("No file loaded")
        layout.addWidget(self.file_label)

        self.load_button = QPushButton("Load MIDI File")
        self.load_button.clicked.connect(self.load_midi)
        layout.addWidget(self.load_button)

        self.port_select = QComboBox()
        self.port_select.addItems(mido.get_output_names())
        layout.addWidget(self.port_select)

        self.tempo_spin = QDoubleSpinBox()
        self.tempo_spin.setRange(20, 300)
        self.tempo_spin.setValue(120)
        self.tempo_spin.setSuffix(" BPM")
        layout.addWidget(QLabel("Tempo"))
        layout.addWidget(self.tempo_spin)

        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.start_playback)
        layout.addWidget(self.play_button)

        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_playback)
        layout.addWidget(self.stop_button)

        self.setLayout(layout)

    from mido import bpm2tempo, tempo2bpm

    def load_midi(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open MIDI File", "", "MIDI Files (*.mid)"
        )
        if file_path:
            self.midi_file = MidiFile(file_path)
            self.file_label.setText(f"Loaded: {Path(file_path).name}")

            self.ticks_per_beat = self.midi_file.ticks_per_beat
            self.tempo = 500000  # default 120 BPM

            # Find the first tempo in track 0
            for msg in self.midi_file.tracks[0]:
                if msg.type == "set_tempo":
                    self.tempo = msg.tempo
                    break

            # Update tempo spinbox in UI
            bpm = tempo2bpm(self.tempo)
            self.tempo_spin.setValue(round(bpm))

            # Convert events to absolute time (in ticks)
            events = []
            for track in self.midi_file.tracks:
                abs_time = 0
                for msg in track:
                    abs_time += msg.time
                    events.append((abs_time, msg))

            # Sort by time across all tracks
            self.midi_events = sorted(events, key=lambda x: x[0])

    def start_playback(self):
        if not self.midi_file or not self.midi_events:
            return

        port_name = self.port_select.currentText()
        if not port_name:
            return

        self.midi_port = open_output(port_name)
        self.start_time = time.time()
        self.event_index = 0
        self.timer.start(1)  # check every ms

    def play_next_event(self):
        if self.event_index >= len(self.midi_events):
            self.stop_playback()
            return

        now = time.time()
        elapsed_time = (now - self.start_time)

        ticks_per_beat = self.ticks_per_beat
        tempo = bpm2tempo(self.tempo_spin.value())  # microseconds per beat
        tick_duration = tempo / 1_000_000 / ticks_per_beat  # seconds per tick

        while self.event_index < len(self.midi_events):
            tick_time, msg = self.midi_events[self.event_index]
            scheduled_time = tick_time * tick_duration

            if elapsed_time >= scheduled_time:
                if not msg.is_meta:
                    self.midi_port.send(msg)
                self.event_index += 1
            else:
                break

    def stop_playback(self):
        self.timer.stop()
        if self.midi_port:
            self.midi_port.close()


class MidiPlayerOld(SynthEditor):
    def __init__(self,
                 midi_helper=Optional[MidiIOHelper],
                 parent=None,
                 preset_helper=None):
        super().__init__()
        self.init_ui()
        self.midi_helper = midi_helper if midi_helper else MidiIOHelper()
        self.preset_helper = preset_helper if preset_helper else PresetHelper(self.midi_helper,
                                                                              presets=DIGITAL_PRESET_LIST,
                                                                              channel=MIDI_CHANNEL_DIGITAL1)
        self.midi_file = None
        self.midi_port = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.play_next_event)
        self.midi_iterator = iter([])
        self.start_time = None
        self.current_time = 0

    def init_ui(self):
        layout = QVBoxLayout()

        self.file_label = DigitalTitle("No file loaded")
        layout.addWidget(self.file_label)

        self.load_button = QPushButton("Load MIDI File")
        self.load_button.clicked.connect(self.load_midi)
        layout.addWidget(self.load_button)

        self.port_select = QComboBox()
        self.port_select.addItems(mido.get_output_names())
        layout.addWidget(self.port_select)

        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.start_playback)
        layout.addWidget(self.play_button)

        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_playback)
        layout.addWidget(self.stop_button)

        self.setLayout(layout)

    def load_midi(self):
        file_path, _ = QFileDialog.getOpenFileName(self,
                                                   "Open MIDI File",
                                                   "",
                                                   "MIDI Files (*.mid)")
        if file_path:
            self.midi_file = MidiFile(file_path)
            self.file_label.setText(f"Loaded: {Path(file_path).name}")
            self.midi_iterator = iter(self.midi_file.tracks[0])

    def start_playback(self):
        if not self.midi_file:
            return

        port_name = self.port_select.currentText()
        if not port_name:
            return

        self.midi_port = open_output(port_name)
        self.current_time = 0
        self.midi_iterator = iter(self.midi_file.play())
        self.timer.start(1)

    def play_next_event(self):
        try:
            msg = next(self.midi_iterator)
            if isinstance(msg, Message):
                self.midi_port.send(msg)
        except StopIteration:
            self.stop_playback()

    def stop_playback(self):
        self.timer.stop()
        if self.midi_port:
            self.midi_port.close()
