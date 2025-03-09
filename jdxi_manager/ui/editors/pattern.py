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
import qtawesome as qta

from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QButtonGroup,
    QComboBox,
    QGroupBox,
    QSpinBox,
    QTabWidget,
    QWidget, QMessageBox
)
from PySide6.QtCore import Qt, QTimer, QEvent

from midiutil import MIDIFile
import mido
from mido import tempo2bpm, MidiFile, MidiTrack, Message
from rtmidi.midiconstants import CONTROLLER_CHANGE, CHANNEL_PRESSURE

from jdxi_manager.midi.constants import MIDI_CHANNEL_DIGITAL1, MIDI_CHANNEL_ANALOG, MIDI_CHANNEL_DIGITAL2, \
    MIDI_CHANNEL_DRUMS
from jdxi_manager.midi.io import MIDIHelper
from jdxi_manager.midi.preset.handler import PresetHandler
from jdxi_manager.midi.preset.loader import PresetLoader
from jdxi_manager.ui.editors.synth import SynthEditor
from jdxi_manager.ui.style import generate_sequencer_button_style, toggle_button_style, Style

# MIDI Constants
NOTE_OFF = 0x80
NOTE_ON = 0x90
POLY_AFTERTOUCH = 0xA0
CONTROL_CHANGE = 0xB0
PROGRAM_CHANGE = 0xC0
CHANNEL_PRESSURE = 0xD0
PITCH_BEND = 0xE0
SYSTEM_MESSAGE = 0xF0

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
        cc = CONTROLLER_CHANGE | self.channel
        self.midi_helper.send_message([cc, CHANNEL_PRESSURE, self.volume & 0x7F])

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

        self.midi_helper.send_message([cc, NOTE_OFF, 0])

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

        cc = CONTROLLER_CHANGE | self.channel
        if msb is not None:
            self.midi_helper.send_message([cc, NOTE_OFF, msb & 0x7F])

        if lsb is not None:
            self.midi_helper.send_message([cc, NOTE_OFF, lsb & 0x7F])

        if kit is not None and pc is not None:
            self.midi_helper.send_message([PROGRAM_CHANGE | self.channel, pc & 0x7F])


class PatternMeasure(QWidget):
    """Widget representing a single measure of the pattern"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.buttons = [[] for _ in range(4)]
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        
        # Create 16 buttons for each row (4 rows)
        for row in range(4):
            row_layout = QHBoxLayout()
            for i in range(16):
                button = QPushButton()
                button.setCheckable(True)
                button.setFixedSize(40, 40)
                button.row = row
                button.column = i
                button.note = None
                self.buttons[row].append(button)
                row_layout.addWidget(button)
            button_layout.addLayout(row_layout)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)


class PatternSequencer(SynthEditor):
    """Pattern Sequencer with MIDI Integration"""

    def __init__(self, midi_helper: Optional[MIDIHelper], preset_handler: Optional[PresetHandler],  parent=None):
        super().__init__(parent)
        self.midi_helper = midi_helper
        self.preset_handler = preset_handler
        self.buttons = []
        self.measures = []
        self.timer = None
        self.current_step = 0
        self.total_steps = 16
        self.beats_per_pattern = 4
        self.bpm = 120
        self.last_tap_time = None
        self.tap_times = []
        self.learned_pattern = [[None] * self.total_steps for _ in range(4)]
        self.active_notes = {}  # Track active notes
        self.midi_file = MidiFile()  # Initialize a new MIDI file
        self.midi_track = MidiTrack()  # Create a new track
        self.midi_file.tracks.append(self.midi_track)  # Add the track to the file
        self._setup_ui()
        self._init_midi_file()
            

    def _setup_ui(self):
        layout = QVBoxLayout()
        row_labels = ["Digital Synth 1", "Digital Synth 2", "Analog Synth", "Drums"]
        self.buttons = [[] for _ in range(4)]

        # Define synth options
        self.digital_options = [
            "C4", "C#4", "D4", "D#4", "E4", "F4", "F#4", "G4", "G#4", "A4", "A#4", "B4",
            "C5", "C#5", "D5", "D#5", "E5", "F5", "F#5", "G5", "G#5", "A5", "A#5", "B5",
            "C6", "C#6", "D6", "D#6", "E6", "F6", "F#6", "G6", "G#6", "A6", "A#6", "B6", "C7"
        ]
        
        self.analog_options = self.digital_options

        # Define drum kit options
        self.drum_options = [
            "BD1", "RIM", "BD2", "CLAP", "BD3", "SD1", "CHH", 
            "SD2", "PHH", "SD3", "OHH", "SD4", "TOM1", "PRC1", "TOM2", 
            "PRC2", "TOM3", "PRC3", "CYM1", "PRC4", "CYM2", "PRC5", "CYM3", 
            "HIT", "OTH1", "OTH2"
        ]

        # Add transport and file controls at the top
        control_panel = QHBoxLayout()
        
        # File operations area
        file_group = QGroupBox("Pattern")
        file_layout = QHBoxLayout()
        
        self.load_button = QPushButton(qta.icon("mdi.file-music-outline"), "Load")
        self.load_button.clicked.connect(self._load_pattern_dialog)
        self.save_button = QPushButton(qta.icon("fa.save"), "Save")
        self.save_button.clicked.connect(self._save_pattern_dialog)
        # Add the Clear Learned Pattern button
        self.clear_learn_button = QPushButton(qta.icon("ei.broom"),"Clear")
        self.clear_learn_button.clicked.connect(self._clear_learned_pattern)
        
        file_layout.addWidget(self.load_button)
        file_layout.addWidget(self.save_button)
        file_layout.addWidget(self.clear_learn_button)
        file_group.setLayout(file_layout)
        control_panel.addWidget(file_group)

        learn_group = QGroupBox("Learn Pattern")
        learn_layout = QHBoxLayout()
        
        # Add the Clear Learned Pattern button
        self.learn_button = QPushButton(qta.icon("ri.play-line"), "Start")
        self.learn_button.clicked.connect(self.on_learn_pattern_button_clicked)
        self.stop_learn_button = QPushButton(qta.icon("ri.stop-line"), "Stop")
        self.stop_learn_button.clicked.connect(self.on_stop_learn_pattern_button_clicked)
        learn_layout.addWidget(self.learn_button)
        learn_layout.addWidget(self.stop_learn_button)
        learn_group.setLayout(learn_layout)
        control_panel.addWidget(learn_group)
        
        # Tempo control area
        tempo_group = QGroupBox("Tempo")
        tempo_layout = QHBoxLayout()
        
        self.tempo_label = QLabel("BPM:")
        self.tempo_spinbox = QSpinBox()
        self.tempo_spinbox.setRange(20, 300)
        self.tempo_spinbox.setValue(120)
        self.tempo_spinbox.valueChanged.connect(self._on_tempo_changed)
        
        self.tap_tempo_button = QPushButton(qta.icon("fa5s.drum"), "Tap")
        self.tap_tempo_button.clicked.connect(self._on_tap_tempo)
        
        tempo_layout.addWidget(self.tempo_label)
        tempo_layout.addWidget(self.tempo_spinbox)
        tempo_layout.addWidget(self.tap_tempo_button)
        tempo_group.setLayout(tempo_layout)
        control_panel.addWidget(tempo_group)
        
        # Transport controls area
        transport_group = QGroupBox("Transport")
        transport_layout = QHBoxLayout()
        
        self.start_button = QPushButton(qta.icon("ri.play-line"),"Play")
        self.stop_button = QPushButton(qta.icon("ri.stop-line"),"Stop")
        self.start_button.clicked.connect(self.play_pattern)
        self.stop_button.clicked.connect(self.stop_pattern)
        
        transport_layout.addWidget(self.start_button)
        transport_layout.addWidget(self.stop_button)
        transport_group.setLayout(transport_layout)
        control_panel.addWidget(transport_group)
        
        layout.addLayout(control_panel)
        self.midi_helper.midi_incoming_message.connect(self._update_combo_boxes)

        for row_idx, label_text in enumerate(row_labels):
            row_layout = QVBoxLayout()
            header_layout = QHBoxLayout()

            if label_text == "Drums":
                icon_name = "fa5s.drum"
            else:
                icon_name = "msc.piano"
            # Create and add label
            icon_label = QLabel()
            icon_label.setPixmap(qta.icon(icon_name).pixmap(40, 40))
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            header_layout.addWidget(icon_label)
            label = QLabel(label_text)
            if label_text == "Analog Synth":
                color = Style.ACCENT_ANALOG
            else:
                color = Style.ACCENT
            label.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {color}")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            header_layout.addWidget(label)
            
            # Add appropriate selector combo box for each row
            if row_idx == 0:  # Digital Synth 1
                self.digital1_selector = QComboBox()
                self.digital1_selector.addItems(self.digital_options)
                header_layout.addWidget(self.digital1_selector)
            elif row_idx == 1:  # Digital Synth 2
                self.digital2_selector = QComboBox()
                self.digital2_selector.addItems(self.digital_options)
                header_layout.addWidget(self.digital2_selector)
            elif row_idx == 2:  # Analog Synth
                self.analog_selector = QComboBox()
                self.analog_selector.addItems(self.analog_options)
                header_layout.addWidget(self.analog_selector)
            elif row_idx == 3:  # Drums
                self.drum_selector = QComboBox()
                self.drum_selector.addItems(self.drum_options)
                header_layout.addWidget(self.drum_selector)
            
            row_layout.addLayout(header_layout)
            button_layout = QHBoxLayout()

            for i in range(16):
                button = QPushButton()
                button.setCheckable(True)
                button.setFixedSize(40, 40)
                button.setStyleSheet(self.generate_sequencer_button_style(False))
                
                # Store the row and column indices in the button
                button.row = row_idx
                button.column = i
                button.note = None
                
                button.clicked.connect(
                    lambda checked, btn=button: self._on_button_clicked(btn, checked)
                )
                
                self.buttons[row_idx].append(button)
                button_layout.addWidget(button)

            row_layout.addLayout(button_layout)
            layout.addLayout(row_layout)

        self.setLayout(layout)

    def on_learn_pattern_button_clicked(self):
        """Connect the MIDI input to the learn pattern function."""
        self.midi_helper.midi_incoming_message.connect(self._learn_pattern)
        self.midi_helper.midi_incoming_message.disconnect(self._update_combo_boxes)

    def on_stop_learn_pattern_button_clicked(self):
        """Disconnect the MIDI input from the learn pattern function and update combo boxes."""
        self.midi_helper.midi_incoming_message.disconnect(self._learn_pattern)
        self.midi_helper.midi_incoming_message.connect(self._update_combo_boxes)

    def _update_combo_boxes(self, message):
        """Update the combo box index to match the note for each channel."""
        logging.info(f"message note: {message.note} channel: {message.channel}")
        if message.type == "note_on":
            if message.channel == MIDI_CHANNEL_DIGITAL1:
                self.digital1_selector.setCurrentIndex(message.note - 36)
            elif message.channel == MIDI_CHANNEL_DIGITAL2:
                self.digital2_selector.setCurrentIndex(message.note - 36)
            elif message.channel == MIDI_CHANNEL_ANALOG:
                self.analog_selector.setCurrentIndex(message.note - 36)
            elif message.channel == MIDI_CHANNEL_DRUMS:
                self.drum_selector.setCurrentIndex(message.note - 36)

    def _midi_note_to_combo_index(self, row, midi_note):
        """Convert a MIDI note number to the corresponding combo box index."""
        if row == 0 or row == 1:  # Digital Synths
            note_list = self.digital_options
        elif row == 2:  # Analog Synth
            note_list = self.analog_options
        else:  # Drums
            return midi_note - 36  # Drum notes start at MIDI note 36

        note_name = self._midi_to_note_name(midi_note)
        return note_list.index(note_name)

    def _set_combo_box_index(self, row, index):
        """Set the combo box index for the specified row."""
        if row == 0:
            self.digital1_selector.setCurrentIndex(index)
        elif row == 1:
            self.digital2_selector.setCurrentIndex(index)
        elif row == 2:
            self.analog_selector.setCurrentIndex(index)
        elif row == 3:
            self.drum_selector.setCurrentIndex(index)

    def _add_measure(self):
        """Add a new measure tab"""
        measure = PatternMeasure()
        self.measures.append(measure)
        
        # Connect button signals
        for row in range(4):
            for button in measure.buttons[row]:
                button.clicked.connect(
                    lambda checked, btn=button: self._on_button_clicked(btn, checked)
                )
        
        self.tab_widget.addTab(measure, f"Measure {len(self.measures)}")

    def _clear_learned_pattern(self):
        """Clear the learned pattern and reset button states."""
        self.learned_pattern = [[None] * self.total_steps for _ in range(4)]
        
        # Reset the UI buttons
        for row in range(4):
            for button in self.buttons[row]:
                button.setChecked(False)
                button.note = None
                button.setStyleSheet(self.generate_sequencer_button_style(False))
        
        logging.info("Cleared learned pattern.")

    def _on_measure_count_changed(self, count: int):
        """Handle measure count changes"""
        current_count = len(self.measures)
        
        if count > current_count:
            # Add new measures
            for i in range(count - current_count):
                self._add_measure()
        else:
            # Remove measures from the end
            while len(self.measures) > count:
                measure = self.measures.pop()
                index = self.tab_widget.indexOf(measure)
                self.tab_widget.removeTab(index)
        
        self.total_measures = count
        self._update_pattern_length()

    def _update_pattern_length(self):
        """Update total pattern length based on measure count"""
        self.total_steps = self.total_measures * 16

    def _on_button_clicked(self, button, checked):
        """Handle button clicks and store the selected note"""
        if checked:
            # Store the currently selected note when button is activated
            if button.row == 0:  # Digital Synth 1
                note_name = self.digital1_selector.currentText()
                button.note = self._note_name_to_midi(note_name)
            elif button.row == 1:  # Digital Synth 2
                note_name = self.digital2_selector.currentText()
                button.note = self._note_name_to_midi(note_name)
            elif button.row == 2:  # Analog Synth
                note_name = self.analog_selector.currentText()
                button.note = self._note_name_to_midi(note_name)
            else:  # Drums
                button.note = 36 + self.drum_selector.currentIndex()
            note_name = self._midi_to_note_name(button.note)
            if button.row == 3:
                drums_note_name = self._midi_to_note_name(button.note, drums=True)
                button.setToolTip(f"Note: {drums_note_name}")
            else:
                button.setToolTip(f"Note: {note_name}")
        
        # Update button style
        button.setStyleSheet(self.generate_sequencer_button_style(checked, 
            self.current_step % self.total_steps == button.column))

    def _on_tempo_changed(self, bpm: int):
        """Handle tempo changes from the spinbox"""
        self.set_tempo(bpm)
        if self.timer and self.timer.isActive():
            # Update timer interval for running sequence
            ms_per_step = (60000 / bpm) / 4  # ms per 16th note
            self.timer.setInterval(int(ms_per_step))

    def _on_tap_tempo(self):
        """Handle tap tempo button clicks"""
        current_time = datetime.datetime.now()
        
        if self.last_tap_time is None:
            self.last_tap_time = current_time
            self.tap_times = []
            return
        
        # Calculate interval since last tap
        interval = (current_time - self.last_tap_time).total_seconds()
        self.last_tap_time = current_time
        
        # Ignore if too long between taps
        if interval > 2.0:
            self.tap_times = []
            return
        
        self.tap_times.append(interval)
        # Keep last 4 taps for averaging
        if len(self.tap_times) > 4:
            self.tap_times.pop(0)
        
        if len(self.tap_times) >= 2:
            # Calculate average interval and convert to BPM
            avg_interval = sum(self.tap_times) / len(self.tap_times)
            bpm = int(60 / avg_interval)
            # Constrain to valid range
            bpm = max(20, min(300, bpm))
            self.tempo_spinbox.setValue(bpm)

    def _save_pattern_dialog(self):
        """Open save file dialog and save pattern"""
        from PySide6.QtWidgets import QFileDialog
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Pattern",
            "",
            "MIDI Files (*.mid);;All Files (*.*)"
        )
        
        if filename:
            if not filename.lower().endswith('.mid'):
                filename += '.mid'
            try:
                self.save_pattern(filename)
                logging.info(f"Pattern saved to {filename}")
            except Exception as e:
                logging.error(f"Error saving pattern: {e}")
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.critical(self, "Error", f"Could not save pattern: {str(e)}")

    def _load_pattern_dialog(self):
        """Open load file dialog and load pattern"""
        from PySide6.QtWidgets import QFileDialog
        
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Load Pattern",
            "",
            "MIDI Files (*.mid);;All Files (*.*)"
        )

        if filename:
            try:
                self.load_pattern(filename)
                logging.info(f"Pattern loaded from {filename}")

                # Update tempo from loaded file
                if self.midi_file and self.midi_file.tracks:
                    for event in self.midi_file.tracks[0]:
                        if event.type == "set_tempo":  # Compare with the string "set_tempo"
                            bpm = int(tempo2bpm(event.tempo))  # Use .tempo instead of .data
                            self.tempo_spinbox.setValue(bpm)
                            break
            except Exception as e:
                logging.error(f"Error loading pattern: {e}")
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.critical(self, "Error", f"Could not load pattern: {str(e)}")

    def set_tempo(self, bpm: int):
        """Set the pattern tempo in BPM"""
        self.bpm = bpm
        if hasattr(self, 'midi_file'):
            self.midi_file.addTempo(0, 0, bpm)
        
        # Update playback speed if sequence is running
        if hasattr(self, 'timer') and self.timer and self.timer.isActive():
            ms_per_step = (60000 / bpm) / 4  # ms per 16th note
            self.timer.setInterval(int(ms_per_step))
        
        logging.info(f"Tempo set to {bpm} BPM")

    def _init_midi_file(self):
        """Initialize a new MIDI file with 4 tracks"""
        # Create MIDI file with 4 tracks (0-3)
        self.midi_file = MIDIFile(4, adjust_origin=True)
        
        # Set tempo
        self.midi_file.addTempo(0, 0, self.bpm)
        
        # Set time signature
        self.midi_file.addTimeSignature(0, 0, 4, 2, 24, 8)
        
        # Initialize track names
        track_names = ["Digital Synth 1", "Digital Synth 2", "Analog Synth", "Drums"]
        for i, name in enumerate(track_names):
            self.midi_file.addTrackName(i, 0, name)
            # Set initial program
            self.midi_file.addProgramChange(i, i if i < 3 else 9, 0, 0)

    def update_pattern(self):
        """Update the MIDI file with current pattern state"""
        self.midi_file = MIDIFile(4, adjust_origin=True)
        self.midi_file.addTempo(0, 0, self.bpm)
        self.midi_file.addTimeSignature(0, 0, 4, 2, 24, 8)
        
        for row in range(4):
            channel = row if row < 3 else 9
            for measure_index, measure in enumerate(self.measures):
                for step in range(16):
                    button = measure.buttons[row][step]
                    if button.isChecked() and button.note is not None:
                        time = (measure_index * 16 + step) * 0.25
                        self.midi_file.addNote(row, channel, button.note, time, 0.25, 100)
                        if row == 3:
                            drums_note_name = self._midi_to_note_name(button.note, drums=True)
                            button.setToolTip(f"Note: {drums_note_name}")
                        else:
                            note_name = self._midi_to_note_name(button.note)
                            button.setToolTip(f"Note: {note_name}")

    def save_pattern(self, filename: str):
        """Save the current pattern to a MIDI file"""
        self.update_pattern()
        with open(filename, 'wb') as output_file:
            self.midi_file.writeFile(output_file)

    def clear_pattern(self):
        """Clear the current pattern, resetting all steps."""
        for row in range(4):
            for step in range(self.total_steps):
                self.buttons[row][step].setChecked(False)
                self.buttons[row][step].note = None
                self.buttons[row][step].setStyleSheet(self.generate_sequencer_button_style(False))
                self.buttons[row][step].setToolTip(f"Note: {self.buttons[row][step].note}")

    # Your method that loads the pattern
    def load_pattern_old(self, filename: str):
        try:
            self.clear_pattern()

            self.midi_file = MidiFile(filename)
            # Check if the MIDI file is loaded and has tracks
            if self.midi_file and self.midi_file.tracks:
                # Iterate through the events in the first track
                for event in self.midi_file.tracks[0]:
                    if event.type == "set_tempo":  # Check for tempo event
                        # Convert microseconds per beat to BPM
                        microseconds_per_beat = event.tempo
                        bpm = 60000000 / microseconds_per_beat  # 60 million / tempo in microseconds
                        self.tempo_spinbox.setValue(int(bpm))  # Set BPM to the spinbox
                        break  # Stop after finding the first tempo change event
        except Exception as e:
            # Log the error if it occurs
            logging.error(f"Error loading pattern: {e}")
            from PySide6.QtWidgets import QMessageBox
            # Show an error message box
            QMessageBox.critical(self, "Error", f"Could not load pattern: {str(e)}")

    def load_pattern(self, filename: str):
        """Load a pattern from a MIDI file"""
        
        try:
            self.clear_pattern()
            
            midi_file = mido.MidiFile(filename)
            ppq = midi_file.ticks_per_beat
            
            for track_num, track in enumerate(midi_file.tracks[:4]):
                if not isinstance(track, mido.MidiTrack):
                    logging.error(f"Track {track_num} is not a MIDITrack")
                    continue
                absolute_time = 0
                for msg in track:  # Correctly iterate over messages in the track
                    absolute_time += msg.time
                    if msg.type == 'note_on' and msg.velocity > 0:
                        step = int((absolute_time / ppq) * 4) % self.total_steps
                        row = track_num
                        
                        button = self.buttons[row][step]
                        button.setChecked(True)
                        button.note = msg.note
                        if row == 3:
                            drums_note_name = self._midi_to_note_name(button.note, drums=True)
                            button.setToolTip(f"Note: {drums_note_name}")
                        else:
                            note_name = self._midi_to_note_name(button.note)
                            button.setToolTip(f"Note: {note_name}")

            for event in self.midi_file.tracks[0]:
                if event.type == "set_tempo":  # Check for tempo event
                    # Convert microseconds per beat to BPM
                    microseconds_per_beat = event.tempo
                    bpm = 60000000 / microseconds_per_beat  # 60 million / tempo in microseconds
                    self.tempo_spinbox.setValue(int(bpm))  # Set BPM to the spinbox
            
        except Exception as e:
            logging.error(f"Error loading pattern: {e}")
            QMessageBox.critical(self, "Error", f"Could not load pattern: {str(e)}")

    def play_pattern(self):
        """Start playing the pattern"""
        if hasattr(self, 'timer') and self.timer and self.timer.isActive():
            return  # Already playing
        
        self.current_step = 0
        
        # Calculate interval based on tempo (ms per 16th note)
        ms_per_step = (60000 / self.bpm) / 4
        
        # Create and start timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._play_step)
        self.timer.start(int(ms_per_step))
        
        # Update button states
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        
        logging.info("Pattern playback started")

    def stop_pattern(self):
        """Stop playing the pattern"""
        if hasattr(self, 'timer') and self.timer:
            self.timer.stop()
            self.timer = None
        
        # Reset step counter
        self.current_step = 0
        
        # Update button states
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        # Send all notes off
        if self.midi_helper:
            for channel in range(16):
                self.midi_helper.send_message([CONTROL_CHANGE | channel, 123, 0])
        
        logging.info("Pattern playback stopped")

    def _note_name_to_midi(self, note_name: str) -> int:
        """Convert note name (e.g., 'C4') to MIDI note number"""
        # Note name to semitone mapping
        note_to_semitone = {
            'C': 0,
            'C#': 1,
            'D': 2,
            'D#': 3,
            'E': 4,
            'F': 5,
            'F#': 6,
            'G': 7,
            'G#': 8,
            'A': 9,
            'A#': 10,
            'B': 11
        }
        
        # Split note name into note and octave
        if '#' in note_name:
            note = note_name[:-1]  # Everything except last character (octave)
            octave = int(note_name[-1])
        else:
            note = note_name[0]
            octave = int(note_name[1])
        
        # Calculate MIDI note number
        # MIDI note 60 is middle C (C4)
        # Each octave is 12 semitones
        # Formula: (octave + 1) * 12 + semitone
        midi_note = (octave + 1) * 12 + note_to_semitone[note]
        
        return midi_note

    def _midi_to_note_name(self, midi_note: int, drums=False) -> str:
        """Convert MIDI note number to note name (e.g., 60 -> 'C4')"""
        # Note mapping (reverse of note_to_semitone)
        semitone_to_note = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        # Calculate octave and note
        octave = (midi_note // 12) - 1
        note = semitone_to_note[midi_note % 12]
        
        if drums:
            return self.drum_options[midi_note - 36]
        else:
            return f"{note}{octave}"

    def _play_step(self):
        """Plays the current step and advances to the next one."""
        step = self.current_step % self.total_steps
        logging.info(f"Playing step {step}")

        # Check each row's button at the current step
        for row in range(4):
            button = self.buttons[row][step]
            if button.isChecked() and hasattr(button, 'note') and button.note is not None:
                # Determine channel based on row
                channel = row if row < 3 else 9  # channels 0,1,2 for synths, 9 for drums
                
                # Send Note On message using the stored note
                if self.midi_helper:
                    logging.info(f"Row {row} active at step {step}, sending note {button.note} on channel {channel}")
                    self.midi_helper.send_message([NOTE_ON | channel, button.note, 100])  # velocity 100
                    # Note Off message after a short delay
                    QTimer.singleShot(100, lambda ch=channel, n=button.note:
                        self.midi_helper.send_message([NOTE_ON | ch, n, 0]))
                else:
                    logging.warning("MIDI helper not available")

        # Advance to next step
        self.current_step = (self.current_step + 1) % self.total_steps

        # Update UI to show current step
        for row in range(4):
            for col in range(self.total_steps):
                button = self.buttons[row][col]
                button.setStyleSheet(self.generate_sequencer_button_style(
                    button.isChecked(), 
                    col == step
                ))

    def generate_sequencer_button_style(self, is_checked: bool, is_current: bool = False) -> str:
        """Generate button style based on state and current step"""
        base_color = "#3498db" if is_checked else "#2c3e50"
        border_color = "#e74c3c" if is_current else base_color
        
        return f"""
            QPushButton {{
                background-color: {base_color};
                border: 2px solid {border_color};
                border-radius: 5px;
                color: white;
                padding: 5px;
            }}
            QPushButton:hover {{
                background-color: {'#2980b9' if is_checked else '#34495e'};
            }}
            QPushButton:pressed {{
                background-color: {'#2472a4' if is_checked else '#2c3e50'};
            }}
        """

    def _learn_pattern(self, message):
        """Learn the pattern of incoming MIDI notes, preserving rests."""
        if message.type == 'note_on' and message.velocity > 0:
            note = message.note

            # Determine the correct row for the note
            for row in range(4):
                if note in self._get_note_range_for_row(row):
                    # Record the note in the current step
                    logging.info(f"Recording note: {note} at step {self.current_step}")
                    self.learned_pattern[row][self.current_step] = note
                    self.active_notes[note] = row  # Mark the note as active
                    self._apply_learned_pattern()

                    # Add the note_on message to the MIDI track
                    self.midi_track.append(Message('note_on', note=note, velocity=message.velocity, time=0))
                    break  # Stop checking once the note is assigned

        elif message.type == 'note_off':
            note = message.note
            if note in self.active_notes:
                # Advance step only if the note was previously turned on
                logging.info(f"Note off: {note} at step {self.current_step}")
                del self.active_notes[note]  # Remove the note from active notes

                # Add the note_off message to the MIDI track
                self.midi_track.append(Message('note_off', note=note, velocity=0, time=0))
                self.current_step = (self.current_step + 1) % self.total_steps

    def _apply_learned_pattern(self):
        """Apply the learned pattern to the sequencer UI."""
        for row in range(4):
            # Clear current button states for the row
            for button in self.buttons[row]:
                button.setChecked(False)
                button.note = None
                button.setStyleSheet(self.generate_sequencer_button_style(False))
                if row == 3:
                    drums_note_name = self._midi_to_note_name(button.note, drums=True)  
                    button.setToolTip(f"Note: {drums_note_name}")
                else:
                    note_name = self._midi_to_note_name(button.note)
                    button.setToolTip(f"Note: {note_name}")

            # Apply the learned pattern
            for time, note in enumerate(self.learned_pattern[row]):
                # Ensure only one button is activated per note
                if note is not None and 0 <= time < len(self.buttons[row]):
                    button = self.buttons[row][time]
                    button.setChecked(True)
                    button.note = note
                    button.setStyleSheet(self.generate_sequencer_button_style(True))
                    if row == 3:
                        drums_note_name = self._midi_to_note_name(button.note, drums=True)
                        button.setToolTip(f"Note: {drums_note_name}")
                    else:
                        note_name = self._midi_to_note_name(button.note)
                        button.setToolTip(f"Note: {note_name}")

    def _get_note_range_for_row(self, row):
        """Get the note range for a specific row."""
        if row == 0 or row == 1:
            return range(60, 72)  # C4 to B4
        elif row == 2:
            return range(48, 60)  # C3 to B3
        else:
            return range(36, 48)  # C2 to B2

    def _move_to_next_step(self):
        """Move to the next step in the pattern."""
        # Move to the next step
        self.current_step = (self.current_step + 1) % self.total_steps

        # Stop learning after 16 steps
        if self.current_step == 0:
            logging.info("Learning complete after 16 steps.")
            self.on_stop_learn_pattern_button_clicked()
            self.timer.stop()
            del self.timer
        else:
            logging.info(f"Moved to step {self.current_step}")

    def save_midi_file(self, filename: str):
        """Save the recorded MIDI messages to a file."""
        with open(filename, 'wb') as output_file:
            self.midi_file.save(output_file)
        logging.info(f"MIDI file saved to {filename}")
