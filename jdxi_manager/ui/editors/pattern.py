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
- Start/Stop playback buttons for sequence control.

"""

import logging
from functools import partial
from typing import Optional

from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
)
from PySide6.QtCore import Qt, QTimer
from jdxi_manager.midi import MIDIHelper
from jdxi_manager.ui.editors.base_editor import BaseEditor
from jdxi_manager.ui.style import sequencer_button_style, toggle_button_style

instrument_icon_folder = "patterns"


class PatternSequencer(BaseEditor):
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
            label.setAlignment(Qt.AlignCenter)
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
