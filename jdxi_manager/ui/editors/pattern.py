"""

Module: Pattern Sequencer with MIDI Integration

This module implements a Pattern Sequencer using PySide6, allowing users to toggle
sequence steps using a grid of buttons. It supports MIDI input to control button states
using note keys (e.g., C4, C#4, etc.).

Features:
- 4 rows of buttons labeled as Digital Synth 1, Digital Synth 2, Analog Synth, and Drums.
- MIDI note-to-button mapping for real-time control.
- Toggle button states programmatically or via MIDI.
- Styled buttons with illumination effects.
- Each button stores an associated MIDI note and its on/off state.
- Start/Stop playback buttons for sequence control. ..

"""

import logging
import threading

from typing import Optional
from rtmidi.midiconstants import (
    ALL_SOUND_OFF,
    BANK_SELECT_LSB,
    BANK_SELECT_MSB,
    CHANNEL_VOLUME,
    CONTROL_CHANGE,
    NOTE_ON,
    PROGRAM_CHANGE,
)

from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QButtonGroup,
)
from PySide6.QtCore import Qt, QTimer

from jdxi_manager.midi import MIDIHelper
from jdxi_manager.ui.editors.base_editor import BaseEditor
from jdxi_manager.ui.style import sequencer_button_style, toggle_button_style

instrument_icon_folder = "patterns"


class Drumpattern(object):
    """Container and iterator for a multi-track step sequence."""

    velocities = {
        "-": None,  # continue note
        ".": 0,  # off
        "+": 10,  # ghost
        "s": 60,  # soft
        "m": 100,  # medium
        "x": 120,  # hard
    }

    def __init__(self, pattern, kit=0, humanize=0):
        self.instruments = []
        self.kit = kit
        self.humanize = humanize

        pattern = (line.strip() for line in pattern.splitlines())
        pattern = (line for line in pattern if line and line[0] != "#")

        for line in pattern:
            parts = line.split(" ", 2)

            if len(parts) == 3:
                patch, strokes, description = parts
                patch = int(patch)
                self.instruments.append((patch, strokes))
                self.steps = len(strokes)

        self.step = 0
        self._notes = {}

    def reset(self):
        self.step = 0

    def play_step(self, midiout, channel=9):
        for note, strokes in self.instruments:
            char = strokes[self.step]
            velocity = self.velocities.get(char)

            if velocity is not None:
                if self._notes.get(note):
                    midiout.send_message([NOTE_ON | channel, note, 0])
                    self._notes[note] = 0
                if velocity > 0:
                    if self.humanize:
                        velocity += int(round(gauss(0, velocity * self.humanize)))

                    midiout.send_message([NOTE_ON | channel, note, max(1, velocity)])
                    self._notes[note] = velocity

        self.step += 1

        if self.step >= self.steps:
            self.step = 0


class Sequencer(threading.Thread):
    """MIDI output and scheduling thread."""

    def __init__(self, midiout, pattern, bpm, channel=9, volume=127):
        super(Sequencer, self).__init__()
        self.midiout = midiout
        self.bpm = max(20, min(bpm, 400))
        self.interval = 15.0 / self.bpm
        self.pattern = pattern
        self.channel = channel
        self.volume = volume
        self.start()

    def run(self):
        self.done = False
        self.callcount = 0
        self.activate_drumkit(self.pattern.kit)
        cc = CONTROL_CHANGE | self.channel
        self.midiout.send_message([cc, CHANNEL_VOLUME, self.volume & 0x7F])

        # give MIDI instrument some time to activate drumkit
        sleep(0.3)
        self.started = timenow()

        while not self.done:
            self.worker()
            self.callcount += 1
            # Compensate for drift:
            # calculate the time when the worker should be called again.
            nexttime = self.started + self.callcount * self.interval
            timetowait = max(0, nexttime - timenow())
            if timetowait:
                sleep(timetowait)
            else:
                print("Oops!")

        self.midiout.send_message([cc, ALL_SOUND_OFF, 0])

    def worker(self):
        """Variable time worker function.

        i.e., output notes, emtpy queues, etc.

        """
        self.pattern.play_step(self.midiout, self.channel)

    def activate_drumkit(self, kit):
        if isinstance(kit, (list, tuple)):
            msb, lsb, pc = kit
        elif kit is not None:
            msb = lsb = None
            pc = kit

        cc = CONTROL_CHANGE | self.channel
        if msb is not None:
            self.midiout.send_message([cc, BANK_SELECT_MSB, msb & 0x7F])

        if lsb is not None:
            self.midiout.send_message([cc, BANK_SELECT_LSB, lsb & 0x7F])

        if kit is not None and pc is not None:
            self.midiout.send_message([PROGRAM_CHANGE | self.channel, pc & 0x7F])


class PatternSequencer(BaseEditor):
    """Pattern Sequencer with MIDI Integration"""

    def __init__(self, midi_helper: MIDIHelper, parent=None):
        super().__init__(parent)
        self.midi_helper = midi_helper
        self.buttons = []
        self.timer = None
        self.current_step = 0
        self.sequence = None
        self.beats_per_pattern = 16  # Default to 16 beats
        self.measures = 1  # Default to 1 measure
        self.total_steps = self.beats_per_pattern * self.measures
        self.button_notes = [[None for _ in range(16)] for _ in range(4)]
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()
        row_labels = ["Digital Synth 1", "Digital Synth 2", "Analog Synth", "Drums"]
        self.buttons = [[] for _ in range(4)]

        for row_idx, label_text in enumerate(row_labels):
            row_layout = QVBoxLayout()
            label = QLabel(label_text)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            row_layout.addWidget(label)
            button_layout = QHBoxLayout()

            for i in range(16):
                button = QPushButton()
                button.setCheckable(True)
                button.setFixedSize(40, 40)
                button.setStyleSheet(sequencer_button_style(False))
                button.toggled.connect(
                    lambda checked, btn=button: toggle_button_style(btn, checked)
                )
                self.buttons[row_idx].append(button)
                button_layout.addWidget(button)
                self.button_notes[row_idx][i] = 60 + row_idx * 16 + i

            row_layout.addLayout(button_layout)
            layout.addLayout(row_layout)

        # Measure Selection Controls
        measure_layout = QHBoxLayout()
        self.measure_buttons = []
        self.measure_group = QButtonGroup()
        for i in range(1, 5):
            btn = QPushButton(f"{i} Measure{'s' if i > 1 else ''}")
            btn.setCheckable(True)
            btn.clicked.connect(lambda _, m=i: self.set_measures(m))
            self.measure_buttons.append(btn)
            self.measure_group.addButton(btn)
            measure_layout.addWidget(btn)
        layout.addLayout(measure_layout)

        # Playback Controls
        control_layout = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.start_button.clicked.connect(self.play_pattern)
        self.stop_button.clicked.connect(self.stop_pattern)
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)
        layout.addLayout(control_layout)

        self.setLayout(layout)

    def set_measures(self, measures):
        """Updates the measure count and recalculates the total steps."""
        self.measures = measures
        self.total_steps = self.beats_per_pattern * self.measures
        for i, btn in enumerate(self.measure_buttons):
            btn.setChecked(i + 1 == measures)

    def play_pattern(self):
        """Plays the stored pattern in a loop using a QTimer."""
        self.current_step = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._play_step)
        self.timer.start(500)

    def _play_step(self):
        """Plays the current step and advances to the next one."""
        step = self.current_step % self.total_steps
        for i, btn in enumerate(self.measure_buttons):
            btn.setChecked(i == step // self.beats_per_pattern)
        self.current_step = (self.current_step + 1) % self.total_steps

    def stop_pattern(self):
        """Stops the pattern playback."""
        if self.timer:
            self.timer.stop()


class PatternSequencerOld(BaseEditor):
    """Pattern Sequencer with MIDI Integration"""

    def __init__(self, midi_helper: Optional[MIDIHelper], parent=None):
        super().__init__(parent)
        self.midi_helper = midi_helper
        self.buttons = []
        self.timer = None
        self.current_step = 0
        self.sequence = None
        self.button_notes = [
            [None for _ in range(16)] for _ in range(4)
        ]  # Store notes per button
        self._setup_ui()
        if self.midi_helper:
            self.midi_helper.midi_note_received.connect(self._handle_midi_note)

    def _setup_ui(self):
        layout = QVBoxLayout()
        row_labels = ["Digital Synth 1", "Digital Synth 2", "Analog Synth", "Drums"]
        self.buttons = [[] for _ in range(4)]

        for row_idx, label_text in enumerate(row_labels):
            row_layout = QVBoxLayout()
            label = QLabel(label_text)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            row_layout.addWidget(label)
            button_layout = QHBoxLayout()

            for i in range(16):  # 16 buttons per row
                button = QPushButton()
                button.setCheckable(True)
                button.setFixedSize(40, 40)
                button.setStyleSheet(sequencer_button_style(False))
                # button.clicked.connect(partial(self.toggle_button, row_idx, i))
                button.toggled.connect(
                    lambda checked, btn=button: toggle_button_style(btn, checked)
                )
                self.buttons[row_idx].append(button)
                button_layout.addWidget(button)

                self.button_notes[row_idx][i] = (
                    60 + row_idx * 16 + i
                )  # Assign MIDI note

            row_layout.addLayout(button_layout)
            layout.addLayout(row_layout)

        # Playback Controls
        control_layout = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.start_button.clicked.connect(self.play_pattern)
        self.stop_button.clicked.connect(self.stop_pattern)
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)
        layout.addLayout(control_layout)

        self.setLayout(layout)

    def toggle_button(self, row, index):
        button = self.buttons[row][index]
        button.setChecked(not button.isChecked())
        button.setStyleSheet(sequencer_button_style(button.isChecked()))

    def select_buttons(self, indices):
        for row, index in indices:
            if 0 <= row < len(self.buttons) and 0 <= index < len(self.buttons[row]):
                self.toggle_button(row, index)

    def _handle_midi_note(self, note, velocity):
        for row in range(4):
            for index in range(16):
                if (
                    self.button_notes[row][index] == note and velocity > 0
                ):  # Note-on event
                    self.toggle_button(row, index)

    def _send_message(self, message):
        """Send a SysEx message using the MIDI helper"""
        if self.midi_helper:
            self.midi_helper.send_message(message)
        else:
            logging.error("MIDI helper not initialized")

    def play_pattern(self):
        """Plays the stored pattern in a loop using a QTimer."""
        if not hasattr(self, "sequence"):
            logging.error("Sequence is not defined.")
            return

        self.current_step = 0  # Track step position
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._play_step)
        self.timer.start(500)  # Adjust tempo (500ms per step)

    def _play_step(self):
        """Plays the current step and advances to the next one."""
        if not self.sequence:
            self.timer.stop()
            return

        message = self.sequence[self.current_step]
        self._send_message(message)

        self.current_step = (self.current_step + 1) % len(self.sequence)  # Loop back

    def stop_pattern(self):
        """Stops the pattern playback."""
        if self.timer:
            self.timer.stop()
