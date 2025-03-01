"""

Module: Pattern Sequencer with MIDI Integration

This module implements address Pattern Sequencer using PySide6, allowing users to toggle
sequence steps using address grid of buttons. It supports MIDI input to control button states
using note keys (e.g., C4, C#4, etc.).

Features:
- 4 rows of buttons labeled as Digital Synth 1, Digital Synth 2, Analog Synth, and Drums.
- MIDI note-to-button mapping for real-time control.
- Toggle button states programmatically or via MIDI.
- Styled buttons with illumination effects.
- Each button stores an associated MIDI note and its on/off state.
- Start/Stop playback buttons for sequence control. ..

"""

import datetime
import logging
import threading
from random import gauss
from time import sleep

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
    QComboBox,
)
from PySide6.QtCore import Qt, QTimer

from jdxi_manager.midi.io import MIDIHelper
from jdxi_manager.ui.editors.base import BaseEditor
from jdxi_manager.ui.style import generate_sequencer_button_style, toggle_button_style

instrument_icon_folder = "patterns"

# Add white keys C1 to F5
white_notes = [
    36,
    38,
    40,
    41,
    43,
    45,
    47,  # C1 to B1
    48,
    50,
    52,
    53,
    55,
    57,
    59,  # C2 to B2
    60,
    62,
    64,
    65,
    67,
    69,
    71,  # C3 to B3
    72,
    74,
    76,
    77,
    79,
    81,
    83,  # C4 to B4
    84,
    86,
    88,
    89,  # C5 to F5
]

black_notes = [
    37,
    39,
    None,
    42,
    44,
    46,  # C#1 to B1
    49,
    51,
    None,
    54,
    56,
    58,  # C#2 to B2
    61,
    63,
    None,
    66,
    68,
    70,  # C#3 to B3
    73,
    75,
    None,
    78,
    80,
    82,  # C#4 to B4
    85,
    87,
    None,
    90,  # C#5 to F#5
]

black_positions = [
    0,
    1,
    3,
    4,
    5,
    7,
    8,
    10,
    11,
    12,
    14,
    15,
    17,
    18,
    19,
    21,
    22,
    24,
    25,
    26,
    28,
    29,
    31,
    32,
]  # Extended positions


class DrumPattern(object):
    """Container and iterator for address multi-track step sequence."""

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

    def play_step(self, midi_helper, channel=9):
        for note, strokes in self.instruments:
            char = strokes[self.step]
            velocity = self.velocities.get(char)

            if velocity is not None:
                if self._notes.get(note):
                    midi_helper.send_message([NOTE_ON | channel, note, 0])
                    self._notes[note] = 0
                if velocity > 0:
                    if self.humanize:
                        velocity += int(round(gauss(0, velocity * self.humanize)))

                    midi_helper.send_message(
                        [NOTE_ON | channel, note, max(1, velocity)]
                    )
                    self._notes[note] = velocity

        self.step += 1

        if self.step >= self.steps:
            self.step = 0


def time_now():
    return int(datetime.datetime.now().timestamp())


class Sequencer(threading.Thread):
    """MIDI output and scheduling thread."""

    def __init__(self, midi_helper: MIDIHelper, pattern, bpm, channel=9, volume=127):
        super().__init__()
        self.started = None
        self.done = None
        self.call_count = None
        self.midi_helper = midi_helper
        self.bpm = max(20, min(bpm, 400))
        self.interval = 15.0 / self.bpm
        self.pattern = pattern
        self.channel = channel
        self.volume = volume
        self.start()

    def run(self):
        self.done = False
        self.call_count = 0
        self.activate_drum_kit(self.pattern.kit)
        cc = CONTROL_CHANGE | self.channel
        self.midi_helper.send_message([cc, CHANNEL_VOLUME, self.volume & 0x7F])

        # give MIDI instrument some time to activate drumkit
        sleep(0.3)
        self.started = time_now()

        while not self.done:
            self.worker()
            self.call_count += 1
            # Compensate for drift:
            # calculate the time when the worker should be called again.
            next_time = self.started + self.call_count * self.interval
            time_to_wait = max(0, next_time - time_now())
            if time_to_wait:
                sleep(time_to_wait)
            else:
                logging.warning("Timing drift detected in Sequencer.")

        self.midi_helper.send_message([cc, ALL_SOUND_OFF, 0])

    def worker(self):
        """Variable time worker function.

        i.e., output notes, empty queues, etc.

        """
        self.pattern.play_step(self.midi_helper, self.channel)

    def activate_drum_kit(self, kit):
        if isinstance(kit, (list, tuple)):
            msb, lsb, pc = kit
        elif kit is not None:
            msb = lsb = None
            pc = kit

        cc = CONTROL_CHANGE | self.channel
        if msb is not None:
            self.midi_helper.send_message([cc, BANK_SELECT_MSB, msb & 0x7F])

        if lsb is not None:
            self.midi_helper.send_message([cc, BANK_SELECT_LSB, lsb & 0x7F])

        if kit is not None and pc is not None:
            self.midi_helper.send_message([PROGRAM_CHANGE | self.channel, pc & 0x7F])


class PatternSequencer(BaseEditor):
    """Pattern Sequencer with MIDI Integration"""

    def __init__(self, midi_helper: MIDIHelper, parent=None):
        super().__init__(parent)
        self.midi_helper = midi_helper
        self.buttons = []
        self.timer = None
        self.current_step = 0
        self.sequence = None
        self.beats_per_pattern = 16
        self.measures = 1
        self.total_steps = self.beats_per_pattern * self.measures
        self.button_notes = [[None for _ in range(16)] for _ in range(4)]
        self.is_playing = False  # Add state tracking
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()
        row_labels = ["Digital Synth 1", "Digital Synth 2", "Analog Synth", "Drums"]
        self.buttons = [[] for _ in range(4)]

        # Define drum kit options
        self.drum_options = [
            "BD1", "RIM", "BD2", "CLAP", "BD3", "SD1", "CHH", 
            "SD2", "PHH", "SD3", "OHH", "SD4", "TOM1", "PRC1", "TOM2", 
            "PRC2", "TOM3", "PRC3", "CYM1", "PRC4", "CYM2", "PRC5", "CYM3", 
            "HIT", "OTH1", "OTH2"
        ]

        for row_idx, label_text in enumerate(row_labels):
            row_layout = QVBoxLayout()
            header_layout = QHBoxLayout()
            
            # Create and add label
            label = QLabel(label_text)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            header_layout.addWidget(label)
            
            # Add drum selector combo box for the drums row
            if row_idx == 3:  # Drums row
                self.drum_selector = QComboBox()
                self.drum_selector.addItems(self.drum_options)
                # self.drum_selector.currentIndexChanged.connect(self._on_drum_changed)
                header_layout.addWidget(self.drum_selector)
            
            row_layout.addLayout(header_layout)
            button_layout = QHBoxLayout()

            for i in range(16):
                button = QPushButton()
                button.setCheckable(True)
                button.setFixedSize(40, 40)
                button.setStyleSheet(generate_sequencer_button_style(False))
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

        # Direct connection without lambda
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
        """Plays the stored pattern in address loop using address QTimer."""
        logging.info("play_pattern called")
        if self.is_playing:
            logging.info("Already playing, returning")
            return

        self.is_playing = True
        self.current_step = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self._play_step)
        self.timer.start(500)  # 500ms per step
        logging.info("Timer started")

    def _play_step(self):
        """Plays the current step and advances to the next one."""
        step = self.current_step % self.total_steps
        logging.info(f"Playing step {step}")

        # Check each row's button at the current step
        for row in range(4):
            button = self.buttons[row][step]
            if button.isChecked():
                # Determine channel based on row
                channel = row if row < 3 else 9  # channels 0,1,2 for synths, 9 for drums

                # Send Note On message for C4 (note 60)
                if self.midi_helper:
                    logging.info(f"Row {row} active at step {step}, sending note on channel {channel}")
                    # Note On message: [Status byte (Note On + channel), note number, velocity]
                    self.midi_helper.send_message([0x90 | channel, 60, 100])  # velocity 100
                    # Note Off message after address short delay
                    QTimer.singleShot(100, lambda ch=channel:
                        self.midi_helper.send_message([0x90 | ch, 60, 0]))
                else:
                    logging.warning("MIDI helper not available")

        # Update measure button highlighting
        for i, btn in enumerate(self.measure_buttons):
            btn.setChecked(i == step // self.beats_per_pattern)

        # Advance to next step
        self.current_step = (self.current_step + 1) % self.total_steps

    def stop_pattern(self):
        """Stops the pattern playback."""
        logging.info("stop_pattern called")
        self.is_playing = False
        if self.timer:
            self.timer.stop()
            self.timer = None
        logging.info("Timer stopped")


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
                button.setStyleSheet(generate_sequencer_button_style(False))
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
        button.setStyleSheet(generate_sequencer_button_style(button.isChecked()))

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
        """Send address SysEx message using the MIDI helper"""
        if self.midi_helper:
            self.midi_helper.send_message(message)
        else:
            logging.error("MIDI helper not initialized")

    def play_pattern(self):
        """Plays the stored pattern in address loop using address QTimer."""
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