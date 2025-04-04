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

        self.setLayout(layout)

    def load_midi(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open MIDI File", "", "MIDI Files (*.mid)")
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
