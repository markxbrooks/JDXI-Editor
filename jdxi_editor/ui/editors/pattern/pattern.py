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
import random
from typing import Any, Optional

from decologr import Decologr as log
from mido import Message, MetaMessage, MidiFile, MidiTrack, bpm2tempo, tempo2bpm
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QSplitter,
    QVBoxLayout,
    QWidget,
)
from rtmidi.midiconstants import CONTROL_CHANGE, NOTE_ON

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.channel.channel import MidiChannel
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.helpers.widgets import (
    create_jdxi_button,
    create_jdxi_button_from_spec,
    create_jdxi_row,
)
from jdxi_editor.ui.editors.midi_player.transport.spec import TransportSpec
from jdxi_editor.ui.editors.pattern.options import DIGITAL_OPTIONS, DRUM_OPTIONS
from jdxi_editor.ui.editors.synth.editor import SynthEditor
from jdxi_editor.ui.preset.helper import JDXiPresetHelper
from jdxi_editor.ui.style import JDXiUIDimensions, JDXiUIStyle
from jdxi_editor.ui.widgets.editor.base import EditorBaseWidget
from jdxi_editor.ui.widgets.pattern.measure import PatternMeasure


class PatternSequenceEditor(SynthEditor):
    """Pattern Sequencer with MIDI Integration using mido"""

    def __init__(
        self,
        midi_helper: Optional[MidiIOHelper],
        preset_helper: Optional[JDXiPresetHelper],
        parent: Optional[QWidget] = None,
        midi_file_editor: Optional[Any] = None,
    ):
        super().__init__(parent=parent)
        """
        Initialize the PatternSequencer

        :param midi_helper: Optional[MidiIOHelper]
        :param preset_helper: Optional[JDXiPresetHelper]
        :param parent: Optional[QWidget]
        :param midi_file_editor: Optional[MidiFileEditor] Reference to MidiFileEditor for shared MIDI file
        """
        self.muted_channels = []
        self.total_measures = 1  # Start with 1 bar by default
        self.midi_helper = midi_helper
        self.preset_helper = preset_helper
        self.midi_file_editor = midi_file_editor  # Reference to MidiFileEditor
        self.buttons = []  # Main sequencer buttons (always 16 steps, one bar)
        self.button_layouts = []  # Store references to button layouts for each row
        self.measures = []  # Each measure stores its own notes
        self.current_bar_index = 0  # Currently selected bar (0-indexed)
        self.timer = None
        self.current_step = 0
        self.total_steps = 16  # Always 16 steps per bar (don't multiply by measures)
        self.beats_per_pattern = 4
        self.beats_per_bar = 16  # Number of beats per bar (16 or 12)
        self.bpm = 120
        self.last_tap_time = None
        self.tap_times = []
        self.learned_pattern = [[None] * self.total_steps for _ in range(4)]
        self.active_notes = {}  # Track active notes
        self.midi_file = MidiFile()  # Initialize a new MIDI file
        self.midi_track = MidiTrack()  # Create a new track
        self.midi_file.tracks.append(self.midi_track)  # Add the track to the file
        self.clipboard = None  # Store copied notes: {source_bar, rows, start_step, end_step, notes_data}
        self._pattern_paused = False
        self._setup_ui()
        self._init_midi_file()
        self._initialize_default_bar()

        JDXi.UI.Theme.apply_editor_style(self)

        # If MidiFileEditor is provided and has a loaded file, load it
        if self.midi_file_editor and hasattr(self.midi_file_editor, "midi_state"):
            if self.midi_file_editor.midi_state.file:
                self.load_from_midi_file_editor()

    def _setup_ui(self):
        # Use EditorBaseWidget for consistent scrollable layout structure
        self.base_widget = EditorBaseWidget(parent=self, analog=False)
        self.base_widget.setup_scrollable_content()
        container_layout = self.base_widget.get_container_layout()

        # Create content widget with main layout
        content_widget = QWidget()
        self.layout = QVBoxLayout(content_widget)
        row_labels = ["Digital Synth 1", "Digital Synth 2", "Analog Synth", "Drums"]
        self.buttons = [[] for _ in range(4)]
        self.mute_buttons = []  # List to store mute buttons

        # Define synth options
        self.digital_options = DIGITAL_OPTIONS

        self.analog_options = self.digital_options

        # Define drum kit options
        self.drum_options = DRUM_OPTIONS

        # Add transport and file controls at the top
        control_panel = QHBoxLayout()

        # File operations area (round buttons + icon labels, same style as Transport)
        file_group = QGroupBox("Pattern")
        file_layout = QHBoxLayout()

        self._add_round_action_button(
            JDXi.UI.Icon.MUSIC,
            "Load",
            self._load_pattern_dialog,
            file_layout,
            name="load",
        )
        self._add_round_action_button(
            JDXi.UI.Icon.SAVE,
            "Save",
            self._save_pattern_dialog,
            file_layout,
            name="save",
        )
        self._add_round_action_button(
            JDXi.UI.Icon.CLEAR,
            "Clear",
            self._clear_learned_pattern,
            file_layout,
            name="clear_learn",
        )

        self.drum_selector = QComboBox()
        self.drum_selector.addItems(self.drum_options)
        self.drum_selector.currentIndexChanged.connect(self._update_drum_rows)

        file_group.setLayout(file_layout)
        # control_panel.addWidget(file_group)

        # Bar management area (separate row for Add Bar button and checkbox)
        bar_group = QGroupBox("Bars")
        bar_layout = QVBoxLayout()

        # First row: Add Bar button and Copy checkbox
        bar_controls_layout = QHBoxLayout()
        self._add_round_action_button(
            JDXi.UI.Icon.ADD,
            "Add Bar",
            self._add_bar,
            bar_controls_layout,
            name="add_bar",
        )
        self.copy_previous_bar_checkbox = QCheckBox("Copy previous bar")
        self.copy_previous_bar_checkbox.setChecked(False)

        bar_controls_layout.addWidget(self.copy_previous_bar_checkbox)
        bar_controls_layout.addStretch()  # Push controls to the left

        bar_layout.addLayout(bar_controls_layout)

        # Copy/Paste controls (round buttons + icon labels)
        copy_paste_layout = QHBoxLayout()
        self._add_round_action_button(
            JDXi.UI.Icon.FILE_DOCUMENT,
            "Copy Section",
            self._copy_section,
            copy_paste_layout,
            name="copy",
        )
        self.copy_button.setToolTip("Copy selected steps from current bar")
        self._add_round_action_button(
            JDXi.UI.Icon.ADD,
            "Paste Section",
            self._paste_section,
            copy_paste_layout,
            name="paste",
        )
        self.paste_button.setToolTip("Paste copied steps to current bar")
        self.paste_button.setEnabled(False)  # Disabled until something is copied

        # Step range selection
        step_range_layout = QHBoxLayout()
        step_range_layout.addWidget(QLabel("Steps:"))
        self.start_step_spinbox = QSpinBox()
        self.start_step_spinbox.setRange(0, 15)
        self.start_step_spinbox.setValue(0)
        self.start_step_spinbox.setToolTip("Start step (0-15)")

        step_range_layout.addWidget(QLabel("to"))
        self.end_step_spinbox = QSpinBox()
        self.end_step_spinbox.setRange(0, 15)
        self.end_step_spinbox.setValue(15)
        self.end_step_spinbox.setToolTip("End step (0-15)")

        step_range_layout.addWidget(self.start_step_spinbox)
        step_range_layout.addWidget(QLabel("-"))
        step_range_layout.addWidget(self.end_step_spinbox)

        bar_layout.addLayout(copy_paste_layout)
        bar_layout.addLayout(step_range_layout)
        bar_group.setLayout(bar_layout)
        control_panel.addWidget(bar_group)

        learn_group = QGroupBox("Learn Pattern")
        learn_layout = QHBoxLayout()

        self._add_round_action_button(
            JDXi.UI.Icon.PLAY,
            "Start",
            self.on_learn_pattern_button_clicked,
            learn_layout,
            name="learn",
        )
        self._add_round_action_button(
            JDXi.UI.Icon.STOP,
            "Stop",
            self.on_stop_learn_pattern_button_clicked,
            learn_layout,
            name="stop_learn",
        )
        learn_group.setLayout(learn_layout)
        # control_panel.addWidget(learn_group)

        # Tempo control area
        tempo_group = QGroupBox("Tempo")
        tempo_layout = QHBoxLayout()

        self.tempo_label = QLabel("BPM:")
        self.tempo_spinbox = QSpinBox()
        self.tempo_spinbox.setRange(20, 300)
        self.tempo_spinbox.setValue(120)
        self.tempo_spinbox.valueChanged.connect(self._on_tempo_changed)

        tempo_layout.addWidget(self.tempo_label)
        tempo_layout.addWidget(self.tempo_spinbox)
        self._add_round_action_button(
            JDXi.UI.Icon.DRUM, "Tap", self._on_tap_tempo, tempo_layout, name="tap_tempo"
        )
        tempo_group.setLayout(tempo_layout)
        control_panel.addWidget(tempo_group)

        # Beats per bar control area
        beats_group = QGroupBox("Beats per Bar")
        beats_layout = QHBoxLayout()

        self.beats_per_bar_combo = QComboBox()
        self.beats_per_bar_combo.addItems(["16 beats per bar", "12 beats per bar"])
        self.beats_per_bar_combo.setCurrentIndex(0)  # Default to 16 beats
        self.beats_per_bar_combo.currentIndexChanged.connect(
            self._on_beats_per_bar_changed
        )

        beats_layout.addWidget(self.beats_per_bar_combo)
        beats_group.setLayout(beats_layout)
        control_panel.addWidget(beats_group)

        # Velocity control area
        velocity_group = QGroupBox("Velocity")
        velocity_layout = QHBoxLayout()

        self.velocity_label = QLabel("Vel:")
        self.velocity_spinbox = QSpinBox()
        self.velocity_spinbox.setRange(1, 127)
        self.velocity_spinbox.setValue(100)
        self.velocity_spinbox.setToolTip("Default velocity for new notes (1-127)")

        velocity_layout.addWidget(self.velocity_label)
        velocity_layout.addWidget(self.velocity_spinbox)
        velocity_group.setLayout(velocity_layout)
        control_panel.addWidget(velocity_group)

        # Duration control area
        duration_group = QGroupBox("Duration")
        duration_layout = QHBoxLayout()

        self.duration_label = QLabel("Dur:")
        self.duration_combo = QComboBox()
        # Duration options as fractions of a beat (16th note = 0.25, 8th = 0.5, quarter = 1.0, etc.)
        self.duration_combo.addItems(
            [
                "16th (1 step)",
                "8th (2 steps)",
                "Dotted 8th (3 steps)",
                "Quarter (4 steps)",
                "Dotted Quarter (6 steps)",
                "Half (8 steps)",
                "Dotted Half (12 steps)",
                "Whole (16 steps)",
            ]
        )
        self.duration_combo.setCurrentIndex(0)  # Default to 16th note
        self.duration_combo.setToolTip("Default note duration for new notes")
        self.duration_combo.currentIndexChanged.connect(self._on_duration_changed)

        duration_layout.addWidget(self.duration_label)
        duration_layout.addWidget(self.duration_combo)
        duration_group.setLayout(duration_layout)
        control_panel.addWidget(duration_group)

        self.layout.addLayout(control_panel)

        # Create splitter for bars list and sequencer (play_button/stop_button set in _init_transport_controls)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Bars list widget
        bars_group = QGroupBox("Bars")
        bars_layout = QVBoxLayout()
        self.bars_list = QListWidget()
        self.bars_list.setMaximumWidth(150)
        self.bars_list.itemClicked.connect(self._on_bar_selected)
        bars_layout.addWidget(self.bars_list)
        bars_group.setLayout(bars_layout)
        splitter.addWidget(bars_group)

        # Sequencer area
        sequencer_widget = QWidget()
        sequencer_layout = QVBoxLayout()
        sequencer_widget.setLayout(sequencer_layout)
        # Allow sequencer widget to expand vertically in full screen
        sequencer_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        # Connect to incoming MIDI messages (from hardware keyboard)
        self.midi_helper.midi_message_incoming.connect(self._update_combo_boxes)

        # Connect to outgoing MIDI messages (from virtual instrument)
        self.midi_helper.midi_message_outgoing.connect(
            self._update_combo_boxes_from_outgoing
        )

        for row_idx, label_text in enumerate(row_labels):
            row_layout = QVBoxLayout()
            header_layout = QHBoxLayout()

            if label_text == "Drums":
                icon = JDXi.UI.Icon.get_icon(
                    JDXi.UI.Icon.DRUM, color=JDXi.UI.Style.FOREGROUND
                )
            else:
                icon = JDXi.UI.Icon.get_icon(
                    JDXi.UI.Icon.PIANO, color=JDXi.UI.Style.FOREGROUND
                )
            # Create and add label
            icon_label = QLabel()
            icon_label.setPixmap(icon.pixmap(40, 40))

            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            header_layout.addWidget(icon_label)
            label = QLabel(label_text)
            if label_text == "Analog Synth":
                color = JDXi.UI.Style.ACCENT_ANALOG
            else:
                color = JDXi.UI.Style.ACCENT
            icon_label.setStyleSheet(f"color: {color}")
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
                header_layout.addWidget(self.drum_selector)

            row_layout.addLayout(header_layout)
            button_row_layout = QHBoxLayout()
            mute_btn_layout = QHBoxLayout()
            mute_btn_layout.addStretch()
            # Add mute button (round style + icon + label)
            mute_btn = self._add_round_action_button(
                JDXi.UI.Icon.MUTE,
                "Mute",
                None,
                mute_btn_layout,
                checkable=True,
                append_to=self.mute_buttons,
            )
            mute_btn.toggled.connect(
                lambda checked, row=row_idx: self._toggle_mute(row, checked)
            )
            button_row_layout.addLayout(mute_btn_layout)
            mute_btn_layout.addStretch()
            step_buttons_layout = self.ui_generate_button_row(row_idx, True)
            button_row_layout.addLayout(step_buttons_layout)
            self.button_layouts.append(step_buttons_layout)  # Store layout reference
            row_layout.addLayout(button_row_layout)
            sequencer_layout.addLayout(row_layout)

        # Add stretch to push content to top, but allow expansion
        sequencer_layout.addStretch()
        # Set size policy on splitter to allow expansion
        splitter.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        splitter.addWidget(sequencer_widget)
        splitter.setStretchFactor(0, 0)  # Bars list doesn't stretch
        splitter.setStretchFactor(1, 1)  # Sequencer stretches

        self.layout.addWidget(splitter)

        # Transport at bottom, centered (stretch on both sides)
        transport_bottom_layout = QHBoxLayout()
        transport_bottom_layout.addStretch()
        transport_bottom_layout.addWidget(self._init_transport_controls())
        transport_bottom_layout.addWidget(file_group)
        transport_bottom_layout.addStretch()
        self.layout.addLayout(transport_bottom_layout)

        # Add content widget to base widget
        container_layout.addWidget(content_widget)

        # Add base widget to editor's layout
        if not hasattr(self, "main_layout") or self.main_layout is None:
            self.main_layout = QVBoxLayout(self)
            self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.base_widget)

    def ui_generate_button_row(self, row_index: int, visible: bool = False):
        """generate sequencer button row"""
        button_row_layout = QHBoxLayout()
        for i in range(16):
            button = QPushButton()
            button.setCheckable(True)
            button.setFixedSize(40, 40)
            button.setStyleSheet(JDXi.UI.Style.generate_sequencer_button_style(False))
            # Store the row and column indices in the button
            button.row = row_index
            button.column = i
            button.note = None
            button.clicked.connect(
                lambda checked, btn=button: self._on_button_clicked(btn, checked)
            )
            self.buttons[row_index].append(button)
            button.setVisible(visible)  # Initially hide all drum buttons
            button_row_layout.addWidget(button)
        return button_row_layout

    def on_learn_pattern_button_clicked(self):
        """Connect the MIDI input to the learn pattern function."""
        self.midi_helper.midi_message_incoming.connect(self._learn_pattern)
        self.midi_helper.midi_message_incoming.disconnect(self._update_combo_boxes)

    def on_stop_learn_pattern_button_clicked(self):
        """Disconnect the MIDI input from the learn pattern function and update combo boxes."""
        self.midi_helper.midi_message_incoming.disconnect(self._learn_pattern)
        self.midi_helper.midi_message_incoming.connect(self._update_combo_boxes)

    def _update_combo_boxes_from_outgoing(self, message):
        """
        Update combo boxes from outgoing MIDI messages (sent from virtual instrument).
        Converts raw message list to mido Message and calls _update_combo_boxes.

        :param message: List[int] or mido.Message Raw MIDI message bytes or mido Message
        """
        try:
            # If it's already a mido Message, use it directly
            if isinstance(message, Message):
                self._update_combo_boxes(message)
                return

            # Convert raw message list to mido Message
            if isinstance(message, (list, tuple)) and len(message) >= 2:
                status_byte = message[0]
                note = message[1]
                velocity = message[2] if len(message) > 2 else 0

                # Extract channel from status byte
                # Note On: 0x90-0x9F, Note Off: 0x80-0x8F
                if (status_byte & 0xF0) in (0x90, 0x80):  # Note On or Note Off
                    channel = status_byte & 0x0F
                    msg_type = (
                        "note_on"
                        if (status_byte & 0xF0) == 0x90 and velocity > 0
                        else "note_off"
                    )

                    # Create mido Message
                    mido_msg = Message(
                        msg_type, note=note, velocity=velocity, channel=channel
                    )
                    self._update_combo_boxes(mido_msg)
        except Exception as ex:
            log.debug(
                f"Error updating combo boxes from outgoing message: {ex}",
                scope=self.__class__.__name__,
            )

    def _update_combo_boxes(self, message):
        """Update the combo box index to match the note for each channel."""
        if message.type == "note_on" and message.velocity > 0:
            note = message.note  # mido uses lowercase 'note'
            channel = message.channel
            log.message(
                message=f"message note: {note} channel: {channel}",
                scope=self.__class__.__name__,
            )

            # Calculate combo box index (notes start at MIDI note 36 = C2)
            combo_index = note - 36

            # Ensure index is valid
            if combo_index < 0:
                log.debug(
                    message=f"Note {note} is below C2 (36), skipping combo box update",
                    scope=self.__class__.__name__,
                )
                return

            # Update the appropriate combo box based on channel
            if channel == MidiChannel.DIGITAL_SYNTH_1:
                if combo_index < self.digital1_selector.count():
                    self.digital1_selector.setCurrentIndex(combo_index)
            elif channel == MidiChannel.DIGITAL_SYNTH_2:
                if combo_index < self.digital2_selector.count():
                    self.digital2_selector.setCurrentIndex(combo_index)
            elif channel == MidiChannel.ANALOG_SYNTH:
                if combo_index < self.analog_selector.count():
                    self.analog_selector.setCurrentIndex(combo_index)
            elif channel == MidiChannel.DRUM_KIT:
                if combo_index < self.drum_selector.count():
                    self.drum_selector.setCurrentIndex(combo_index)

    def _midi_note_to_combo_index(self, row, midi_note):
        """Convert a MIDI note number to the corresponding combo box index."""
        if row in [0, 1]:  # Digital Synths
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

    def _initialize_default_bar(self):
        """Initialize with one default bar"""
        self._add_bar()

    def _add_bar(self):
        """Add a new bar to the pattern, optionally copying from the previous bar"""
        bar_number = len(self.measures) + 1
        measure = PatternMeasure()

        # Check if we should copy the previous bar
        copy_previous = self.copy_previous_bar_checkbox.isChecked()

        if copy_previous and len(self.measures) > 0:
            # Copy notes from the previous bar (most recently added bar)
            previous_measure = self.measures[-1]
            for row in range(4):
                for step in range(16):
                    if step < len(previous_measure.buttons[row]) and step < len(
                        measure.buttons[row]
                    ):
                        previous_button = previous_measure.buttons[row][step]
                        new_button = measure.buttons[row][step]

                        # Copy button state and note
                        new_button.row = row
                        new_button.column = step
                        new_button.setChecked(previous_button.isChecked())
                        new_button.NOTE = previous_button.NOTE
                        # Copy duration if available
                        if hasattr(previous_button, "NOTE_DURATION"):
                            new_button.NOTE_DURATION = previous_button.NOTE_DURATION
                        else:
                            new_button.NOTE_DURATION = None
                        # Copy velocity if available
                        if hasattr(previous_button, "NOTE_VELOCITY"):
                            new_button.NOTE_VELOCITY = previous_button.NOTE_VELOCITY
                        else:
                            new_button.NOTE_VELOCITY = None
        else:
            # Initialize all buttons in the new measure as unchecked with no notes
            for row in range(4):
                for button in measure.buttons[row]:
                    button.row = row
                    button.column = button.column  # Keep local column (0-15)
                    button.NOTE = None
                    button.NOTE_DURATION = None
                    button.setChecked(False)

        self.measures.append(measure)

        # Add to bars list
        item = QListWidgetItem(f"Bar {bar_number}")
        item.setData(
            Qt.ItemDataRole.UserRole, len(self.measures) - 1
        )  # Store bar index
        self.bars_list.addItem(item)

        # Select the new bar and sync sequencer digital
        self.bars_list.setCurrentItem(item)
        self.current_bar_index = len(self.measures) - 1

        # Update total measures (but keep total_steps at 16)
        self.total_measures = len(self.measures)
        self._update_pattern_length()

        # Sync sequencer buttons with the new (empty) bar
        self._sync_sequencer_with_bar(self.current_bar_index)

        log.message(
            message=f"Added bar {bar_number}. Total bars: {self.total_measures}",
            scope=self.__class__.__name__,
        )

    def _on_bar_selected(self, item: QListWidgetItem):
        """Handle bar selection from list"""
        bar_index = item.data(Qt.ItemDataRole.UserRole)
        if bar_index is not None:
            self.current_bar_index = bar_index
            # Sync sequencer buttons with the selected bar's notes
            self._sync_sequencer_with_bar(bar_index)
            log.message(
                message=f"Selected bar {bar_index + 1}", scope=self.__class__.__name__
            )

    def _copy_section(self):
        """Copy a section of notes from the current bar"""
        if self.current_bar_index >= len(self.measures):
            QMessageBox.warning(self, "Copy", "No bar selected")
            return

        start_step = self.start_step_spinbox.value()
        end_step = self.end_step_spinbox.value()

        if start_step > end_step:
            QMessageBox.warning(self, "Copy", "Start step must be <= end step")
            return

        measure = self.measures[self.current_bar_index]
        notes_data = {}

        # Copy all rows and selected steps
        for row in range(4):
            notes_data[row] = {}
            for step in range(start_step, end_step + 1):
                if step < len(measure.buttons[row]):
                    button = measure.buttons[row][step]
                    notes_data[row][step] = {
                        "checked": button.isChecked(),
                        "note": button.NOTE if hasattr(button, "NOTE") else None,
                        "duration": (
                            button.NOTE_DURATION
                            if hasattr(button, "NOTE_DURATION")
                            else None
                        ),
                        "velocity": (
                            button.NOTE_VELOCITY
                            if hasattr(button, "NOTE_VELOCITY")
                            else None
                        ),
                    }

        self.clipboard = {
            "source_bar": self.current_bar_index,
            "start_step": start_step,
            "end_step": end_step,
            "notes_data": notes_data,
        }

        self.paste_button.setEnabled(True)
        log.message(
            message=f"Copied steps {start_step}-{end_step} from bar {self.current_bar_index + 1}",
            scope=self.__class__.__name__,
        )

    def _paste_section(self):
        """Paste copied section to the current bar"""
        if self.clipboard is None:
            QMessageBox.warning(
                self, "Paste", "Nothing copied. Use Copy Section first."
            )
            return

        if self.current_bar_index >= len(self.measures):
            QMessageBox.warning(self, "Paste", "No bar selected")
            return

        measure = self.measures[self.current_bar_index]
        notes_data = self.clipboard["notes_data"]
        start_step = self.start_step_spinbox.value()
        source_start = self.clipboard["start_step"]
        source_end = self.clipboard["end_step"]
        num_steps = source_end - source_start + 1

        # Paste notes starting at the selected start step
        for row in range(4):
            if row in notes_data:
                for source_step, button_data in notes_data[row].items():
                    # Calculate destination step
                    dest_step = start_step + (source_step - source_start)

                    if dest_step < 0 or dest_step >= 16:
                        continue  # Skip if out of bounds

                    if dest_step < len(measure.buttons[row]):
                        button = measure.buttons[row][dest_step]
                        button.setChecked(button_data["checked"])
                        button.NOTE = button_data["note"]
                        button.NOTE_DURATION = button_data["duration"]
                        button.NOTE_VELOCITY = button_data["velocity"]

        # Sync sequencer digital
        self._sync_sequencer_with_bar(self.current_bar_index)
        log.message(
            message=f"Pasted {num_steps} steps to bar {self.current_bar_index + 1} starting at step {start_step}",
            scope=self.__class__.__name__,
        )

    def _sync_sequencer_with_bar(self, bar_index: int):
        """
        Sync the main sequencer buttons with the notes from the specified bar.
        This displays the bar's notes in the sequencer grid.

        :param bar_index: int Index of the bar to digital (0-indexed)
        """
        if bar_index < 0 or bar_index >= len(self.measures):
            return

        measure = self.measures[bar_index]

        # Copy note data from the measure to the main sequencer buttons
        for row in range(4):
            for step in range(16):
                if step < len(self.buttons[row]) and step < len(measure.buttons[row]):
                    sequencer_button = self.buttons[row][step]
                    measure_button = measure.buttons[row][step]

                    # Sync checked state and note
                    sequencer_button.setChecked(measure_button.isChecked())
                    sequencer_button.NOTE = measure_button.NOTE
                    # Copy duration if available
                    if hasattr(measure_button, "NOTE_DURATION"):
                        sequencer_button.NOTE_DURATION = measure_button.NOTE_DURATION
                    else:
                        sequencer_button.NOTE_DURATION = None
                    # Copy velocity if available
                    if hasattr(measure_button, "NOTE_VELOCITY"):
                        sequencer_button.NOTE_VELOCITY = measure_button.NOTE_VELOCITY
                    else:
                        sequencer_button.NOTE_VELOCITY = None

                    # Update tooltip
                    if sequencer_button.NOTE is not None:
                        if row == 3:  # Drums
                            note_name = self._midi_to_note_name(
                                sequencer_button.NOTE, drums=True
                            )
                        else:
                            note_name = self._midi_to_note_name(sequencer_button.NOTE)
                        sequencer_button.setToolTip(f"Note: {note_name}")
                    else:
                        sequencer_button.setToolTip("")

                    # Update style
                    is_current = (self.current_step % self.total_steps) == step
                    sequencer_button.setStyleSheet(
                        JDXi.UI.Style.generate_sequencer_button_style(
                            sequencer_button.isChecked(),
                            is_current,
                            is_selected_bar=True,  # All displayed buttons are from selected bar
                        )
                    )

    def _highlight_bar(self, bar_index: int):
        """Update button styles to highlight the current step in the selected bar"""
        if bar_index < 0 or bar_index >= len(self.measures):
            return

        # Update all sequencer buttons to show current step
        for row in range(4):
            for step in range(16):
                if step < len(self.buttons[row]):
                    button = self.buttons[row][step]
                    is_checked = button.isChecked()
                    is_current = (self.current_step % self.total_steps) == step
                    button.setStyleSheet(
                        JDXi.UI.Style.generate_sequencer_button_style(
                            is_checked, is_current, is_selected_bar=True
                        )
                    )

    def _clear_learned_pattern(self):
        """Clear the learned pattern and reset button states."""
        self.learned_pattern = [[None] * self.total_steps for _ in range(4)]

        # Reset the UI buttons
        for row in range(4):
            for button in self.buttons[row]:
                button.setChecked(False)
                button.NOTE = None
                button.NOTE_DURATION = None
                button.setStyleSheet(
                    JDXi.UI.Style.generate_sequencer_button_style(False)
                )

        log.message(message="Cleared learned pattern.", scope=self.__class__.__name__)

    def _on_measure_count_changed(self, count: int):
        """Handle measure count changes"""
        current_count = len(self.measures)

        if count > current_count:
            # Add new measures
            for _ in range(count - current_count):
                self._add_measure()
        else:
            # Remove measures from the end
            while len(self.measures) > count:
                self.measures.pop()
                # the plan is to add more measures via tab 2, 3 & 4
                # index = self.tab_widget.indexOf(measure)
                # self.tab_widget.removeTab(index)

        self.total_measures = count
        self._update_pattern_length()

    def _update_pattern_length(self):
        """Update total pattern length based on measure count"""
        # Keep total_steps at 16 (one bar) - sequencer always shows one bar at a time
        # Playback will iterate through all bars
        self.total_steps = 16

    def _on_button_clicked(self, button, checked):
        """Handle button clicks and store the selected note"""
        # Don't allow checking disabled buttons
        if not button.isEnabled():
            return

        if checked:
            # Store the currently selected note when button is activated
            if button.row == 0:  # Digital Synth 1
                note_name = self.digital1_selector.currentText()
                button.NOTE = self._note_name_to_midi(note_name)
            elif button.row == 1:  # Digital Synth 2
                note_name = self.digital2_selector.currentText()
                button.NOTE = self._note_name_to_midi(note_name)
            elif button.row == 2:  # Analog Synth
                note_name = self.analog_selector.currentText()
                button.NOTE = self._note_name_to_midi(note_name)
            else:  # Drums
                button.NOTE = 36 + self.drum_selector.currentIndex()
            # Set default duration for manually created notes
            if not hasattr(button, "NOTE_DURATION") or button.NOTE_DURATION is None:
                button.NOTE_DURATION = self._get_duration_ms()
            # Set default velocity for manually created notes
            if not hasattr(button, "NOTE_VELOCITY") or button.NOTE_VELOCITY is None:
                button.NOTE_VELOCITY = self.velocity_spinbox.value()
            note_name = self._midi_to_note_name(button.NOTE)
            if button.row == 3:
                drums_note_name = self._midi_to_note_name(button.NOTE, drums=True)
                button.setToolTip(f"Note: {drums_note_name}")
            else:
                button.setToolTip(f"Note: {note_name}")

        # Store the note in the currently selected bar's measure
        if len(self.measures) > 0 and self.current_bar_index < len(self.measures):
            measure = self.measures[self.current_bar_index]
            step_in_bar = button.column  # button.column is 0-15 for sequencer buttons

            if button.row < len(measure.buttons) and step_in_bar < len(
                measure.buttons[button.row]
            ):
                measure_button = measure.buttons[button.row][step_in_bar]
                measure_button.setChecked(checked)
                if checked:
                    measure_button.NOTE = button.NOTE
                    # Copy duration if available
                    if hasattr(button, "NOTE_DURATION"):
                        measure_button.NOTE_DURATION = button.NOTE_DURATION
                    # Copy velocity if available
                    if hasattr(button, "NOTE_VELOCITY"):
                        measure_button.NOTE_VELOCITY = button.NOTE_VELOCITY
                else:
                    measure_button.NOTE = None
                    measure_button.NOTE_DURATION = None
                    measure_button.NOTE_VELOCITY = None

        # Update button style
        is_current = (self.current_step % self.total_steps) == button.column
        is_selected_bar = (
            len(self.measures) > 0 and (button.column // 16) == self.current_bar_index
        )
        button.setStyleSheet(
            JDXi.UI.Style.generate_sequencer_button_style(
                checked, is_current, is_selected_bar=is_selected_bar and checked
            )
        )

    def _on_beats_per_bar_changed(self, index: int):
        """Handle beats per bar changes from the combobox"""
        if index == 0:
            self.beats_per_bar = 16
        else:
            self.beats_per_bar = 12

        # Update button states based on beats per bar
        self._update_button_states_for_beats_per_bar()
        log.message(f"Beats per bar changed to {self.beats_per_bar}")

    def _update_button_states_for_beats_per_bar(self):
        """Enable/disable sequencer buttons based on beats per bar setting"""
        # Steps 0-11 are always enabled, steps 12-15 are disabled when beats_per_bar is 12
        for row in range(4):
            for step in range(16):
                if step < len(self.buttons[row]):
                    button = self.buttons[row][step]
                    if self.beats_per_bar == 12:
                        # Disable last 4 buttons (steps 12-15)
                        button.setEnabled(step < 12)
                        if step >= 12:
                            button.setChecked(False)  # Uncheck disabled buttons
                            # Also clear notes in measures for disabled steps
                            for measure in self.measures:
                                if step < len(measure.buttons[row]):
                                    measure.buttons[row][step].setChecked(False)
                                    measure.buttons[row][step].NOTE = None
                                    measure.buttons[row][step].NOTE_DURATION = None
                    else:
                        # Enable all 16 buttons
                        button.setEnabled(True)

        # Sync sequencer digital after updating button states
        if self.current_bar_index < len(self.measures):
            self._sync_sequencer_with_bar(self.current_bar_index)

    def _get_duration_ms(self) -> float:
        """Get the default duration in milliseconds based on the duration combo selection"""
        # Duration multipliers: 16th=1, 8th=2, dotted 8th=3, quarter=4, dotted quarter=6, half=8, dotted half=12, whole=16
        duration_multipliers = [1, 2, 3, 4, 6, 8, 12, 16]
        index = self.duration_combo.currentIndex()
        steps = duration_multipliers[index] if index < len(duration_multipliers) else 1
        # Each step is a 16th note, so duration = steps * (beat_duration / 4)
        # beat_duration in ms = 60000 / bpm
        step_duration_ms = (60000.0 / self.bpm) / 4.0
        return step_duration_ms * steps

    def _on_duration_changed(self, index: int):
        """Handle duration changes from the combo box"""
        # Duration change doesn't affect existing notes, only new ones
        # This is just a placeholder for potential future functionality
        pass

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
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Pattern", "", "MIDI Files (*.mid);;All Files (*.*)"
        )

        if filename:
            if not filename.lower().endswith(".mid"):
                filename += ".mid"
            try:
                self.save_pattern(filename)
                log.message(
                    message=f"Pattern saved to {filename}",
                    scope=self.__class__.__name__,
                )
            except Exception as ex:
                log.error(
                    message=f"Error saving pattern: {ex}", scope=self.__class__.__name__
                )
                QMessageBox.critical(
                    self, "Error", f"Could not save pattern: {str(ex)}"
                )

    def _load_pattern_dialog(self):
        """Open load file dialog and load pattern"""

        filename, _ = QFileDialog.getOpenFileName(
            self, "Load Pattern", "", "MIDI Files (*.mid);;All Files (*.*)"
        )

        if filename:
            try:
                self.load_pattern(filename)
                log.message(
                    message=f"Pattern loaded from {filename}",
                    scope=self.__class__.__name__,
                )

                # Update tempo from loaded file (already handled in load_pattern)
                # Tempo is set in load_pattern() method
                pass
            except Exception as ex:
                log.error(
                    message=f"Error loading pattern: {ex}",
                    scope=self.__class__.__name__,
                )
                QMessageBox.critical(
                    self, "Error", f"Could not load pattern: {str(ex)}"
                )

    def set_tempo(self, bpm: int):
        """Set the pattern tempo in BPM using mido."""
        self.bpm = bpm
        # Calculate microseconds per beat
        microseconds_per_beat = int(60000000 / bpm)

        # Create a set_tempo MetaMessage
        tempo_message = MetaMessage("set_tempo", tempo=microseconds_per_beat)

        # Add the tempo message to the first track
        if self.midi_file.tracks:
            self.midi_file.tracks[0].insert(0, tempo_message)

        # Update playback speed if sequence is running
        if hasattr(self, "timer") and self.timer and self.timer.isActive():
            ms_per_step = (60000 / bpm) / 4  # ms per 16th note
            self.timer.setInterval(int(ms_per_step))

        log.message(message=f"Tempo set to {bpm} BPM", scope=self.__class__.__name__)

    def _init_midi_file(self):
        """Initialize a new MIDI file with 4 tracks"""
        self.midi_file = MidiFile()
        for _ in range(4):
            track = MidiTrack()
            self.midi_file.tracks.append(track)

    def update_pattern(self):
        """Update the MIDI file with current pattern state"""
        self.midi_file = MidiFile()
        track = MidiTrack()
        self.midi_file.tracks.append(track)

        track.append(MetaMessage("set_tempo", tempo=bpm2tempo(self.bpm)))
        track.append(MetaMessage("time_signature", numerator=4, denominator=4))

        for row in range(4):
            channel = row if row < 3 else 9
            for measure_index, measure in enumerate(self.measures):
                for step in range(16):
                    button = measure.buttons[row][step]
                    if button.isChecked() and button.NOTE is not None:
                        time = int(
                            (measure_index * 16 + step) * 120
                        )  # Convert to ticks
                        # Get velocity from button if available, otherwise use default
                        velocity = (
                            button.NOTE_VELOCITY
                            if hasattr(button, "NOTE_VELOCITY")
                            and button.NOTE_VELOCITY is not None
                            else 100
                        )
                        track.append(
                            Message(
                                "note_on",
                                note=button.NOTE,
                                velocity=velocity,
                                time=time,
                                channel=channel,
                            )
                        )
                        track.append(
                            Message(
                                "note_off",
                                note=button.NOTE,
                                velocity=velocity,
                                time=time + 120,
                                channel=channel,
                            )
                        )

                        note_name = (
                            self._midi_to_note_name(button.NOTE, drums=True)
                            if row == 3
                            else self._midi_to_note_name(button.NOTE)
                        )
                        button.setToolTip(f"Note: {note_name}")

    def set_midi_file_editor(self, midi_file_editor: Any) -> None:
        """
        Set reference to MidiFileEditor for shared MIDI file editing.

        :param midi_file_editor: MidiFileEditor instance
        """
        self.midi_file_editor = midi_file_editor
        # If MidiFileEditor already has a loaded file, load it
        if self.midi_file_editor and hasattr(self.midi_file_editor, "midi_state"):
            if self.midi_file_editor.midi_state.file:
                self.load_from_midi_file_editor()

    def load_from_midi_file_editor(
        self, midi_file_editor: Optional[Any] = None
    ) -> None:
        """
        Load pattern from the MidiFileEditor's current MIDI file.

        :param midi_file_editor: Optional MidiFileEditor instance. If not provided, uses self.midi_file_editor
        """
        try:
            # Use provided instance or fall back to stored reference
            editor = midi_file_editor or self.midi_file_editor

            if not editor:
                log.debug(
                    message="Editor not available - no reference provided and self.midi_file_editor is None",
                    scope=self.__class__.__name__,
                )
                return

            if not hasattr(editor, "midi_state"):
                log.debug(
                    message="Editor missing midi_state attribute",
                    scope=self.__class__.__name__,
                )
                return

            # Store the reference if it wasn't set before
            if not self.midi_file_editor:
                self.midi_file_editor = editor
                log.debug(
                    message="Stored MidiFileEditor reference in Pattern Sequencer",
                    scope=self.__class__.__name__,
                )

            midi_file = editor.midi_state.file
            if not midi_file:
                log.debug(
                    message="No MIDI file loaded in MidiFileEditor",
                    scope=self.__class__.__name__,
                )
                return

            # Try to get filename from multiple possible locations
            filename = None
            if hasattr(midi_file, "filename"):
                filename = midi_file.filename
            elif hasattr(editor.midi_state, "file") and hasattr(
                editor.midi_state.file, "filename"
            ):
                filename = editor.midi_state.file.filename

            if filename:
                log.message(
                    message=f"Loading pattern from MidiFileEditor file: {filename}",
                    scope=self.__class__.__name__,
                )
                self.load_pattern(filename)
            else:
                # Load from the MidiFile object directly
                log.message(
                    message="Loading pattern from MidiFileEditor's MidiFile object (no filename available)",
                    scope=self.__class__.__name__,
                )
                self._load_from_midi_file_object(midi_file)
        except Exception as ex:
            log.error(
                message=f"Error loading from MidiFileEditor: {ex}",
                scope=self.__class__.__name__,
            )
            import traceback

            log.debug(traceback.format_exc())

    def _load_from_midi_file_object(self, midi_file: MidiFile) -> None:
        """Load pattern from a MidiFile object (internal method)."""
        try:
            ppq = midi_file.ticks_per_beat
            beats_per_bar = 4
            ticks_per_bar = ppq * beats_per_bar

            # Detect number of bars
            num_bars = self._detect_bars_from_midi(midi_file)
            log.message(
                message=f"Detected {num_bars} bars in MIDI file",
                scope=self.__class__.__name__,
            )

            # Clear existing bars and bars list
            self.bars_list.clear()
            self.measures.clear()

            # Create new bars
            for bar_num in range(num_bars):
                measure = PatternMeasure()
                for row in range(4):
                    for button in measure.buttons[row]:
                        button.row = row
                        button.column = button.column
                        button.NOTE = None
                        button.NOTE_DURATION = None
                        button.NOTE_VELOCITY = None
                        button.setChecked(False)
                self.measures.append(measure)
                item = QListWidgetItem(f"Bar {bar_num + 1}")
                item.setData(Qt.ItemDataRole.UserRole, bar_num)
                self.bars_list.addItem(item)

            self.total_measures = len(self.measures)
            self._update_pattern_length()

            # Load notes from all tracks, mapping by MIDI channel
            # Channel mapping: 0 -> Digital Synth 1 (row 0), 1 -> Digital Synth 2 (row 1),
            #                  2 -> Analog Synth (row 2), 9 -> Drums (row 3)
            notes_loaded = 0
            channel_to_row = {
                0: 0,  # Channel 0 -> Digital Synth 1 (row 0)
                1: 1,  # Channel 1 -> Digital Synth 2 (row 1)
                2: 2,  # Channel 2 -> Analog Synth (row 2)
                9: 3,  # Channel 9 -> Drums (row 3)
            }

            for track in midi_file.tracks:
                absolute_time = 0
                for msg in track:
                    absolute_time += msg.time
                    # Check if message is a note_on with velocity > 0 and has a channel attribute
                    if msg.type == "note_on" and msg.velocity > 0:
                        # Get channel - note messages always have channel attribute
                        if not hasattr(msg, "channel"):
                            continue
                        channel = msg.channel
                        if channel not in channel_to_row:
                            continue
                        row = channel_to_row[channel]
                        bar_index = int(absolute_time / ticks_per_bar)
                        step_in_bar = int(
                            (absolute_time % ticks_per_bar) / (ticks_per_bar / 16)
                        )

                        while bar_index >= len(self.measures):
                            measure = PatternMeasure()
                            for r in range(4):
                                for button in measure.buttons[r]:
                                    button.row = r
                                    button.column = button.column
                                    button.NOTE = None
                                    button.NOTE_DURATION = None
                                    button.NOTE_VELOCITY = None
                                    button.setChecked(False)
                            self.measures.append(measure)
                            item = QListWidgetItem(f"Bar {len(self.measures)}")
                            item.setData(
                                Qt.ItemDataRole.UserRole, len(self.measures) - 1
                            )
                            self.bars_list.addItem(item)

                        if bar_index < len(self.measures) and step_in_bar < 16:
                            measure = self.measures[bar_index]
                            if step_in_bar < len(measure.buttons[row]):
                                button = measure.buttons[row][step_in_bar]
                                button.setChecked(True)
                                button.NOTE = msg.note
                                # Store velocity from MIDI file editor
                                button.NOTE_VELOCITY = (
                                    msg.velocity
                                    if hasattr(msg, "velocity")
                                    else self.velocity_spinbox.value()
                                )
                                # Set default duration for MIDI file editor loaded notes
                                button.NOTE_DURATION = self._get_duration_ms()
                                notes_loaded += 1

            # Update tempo from file: search all tracks for first set_tempo
            tempo_bpm = None
            for track in midi_file.tracks:
                for event in track:
                    if event.type == "set_tempo":
                        tempo_bpm = int(tempo2bpm(event.tempo))
                        break
                if tempo_bpm is not None:
                    break
            if tempo_bpm is not None:
                self.tempo_spinbox.blockSignals(True)
                self.tempo_spinbox.setValue(tempo_bpm)
                self.tempo_spinbox.blockSignals(False)
                self.set_tempo(tempo_bpm)

            # Select first bar and sync
            if self.bars_list.count() > 0:
                self.current_bar_index = 0
                self.bars_list.setCurrentRow(0)
                self._sync_sequencer_with_bar(0)
                log.message(
                    message=f"Loaded {notes_loaded} notes from MidiFileEditor's MIDI file in {len(self.measures)} bars",
                    scope=self.__class__.__name__,
                )
            else:
                log.warning(
                    message="No bars were created from MIDI file",
                    scope=self.__class__.__name__,
                )
        except Exception as ex:
            log.error(
                message=f"Error loading from MidiFileEditor: {ex}",
                scope=self.__class__.__name__,
            )
            import traceback

            log.debug(traceback.format_exc())

    def save_pattern(self, filename: str):
        """Save the current pattern to a MIDI file using mido."""
        midi_file = MidiFile()

        # Create tracks for each row
        for row in range(4):
            track = MidiTrack()
            midi_file.tracks.append(track)

            # Add track name and program change
            track.append(Message("program_change", program=0, time=0))

            # Add notes from all bars to the track
            for bar_index, measure in enumerate(self.measures):
                for step in range(16):
                    if step < len(measure.buttons[row]):
                        measure_button = measure.buttons[row][step]
                        if (
                            measure_button.isChecked()
                            and measure_button.NOTE is not None
                        ):
                            # Calculate the time for the note_on event (across all bars)
                            global_step = bar_index * 16 + step
                            time = global_step * 480  # Assuming 480 ticks per beat
                            # Get velocity from button if available, otherwise use default
                            velocity = (
                                measure_button.NOTE_VELOCITY
                                if hasattr(measure_button, "NOTE_VELOCITY")
                                and measure_button.NOTE_VELOCITY is not None
                                else 100
                            )
                            track.append(
                                Message(
                                    "note_on",
                                    note=measure_button.NOTE,
                                    velocity=velocity,
                                    time=time,
                                )
                            )
                            # Add a note_off event after a short duration
                            track.append(
                                Message(
                                    "note_off",
                                    note=measure_button.NOTE,
                                    velocity=0,
                                    time=time + 120,
                                )
                            )

        # Save the MIDI file
        midi_file.save(filename)
        log.message(
            message=f"Pattern saved to {filename}", scope=self.__class__.__name__
        )

        # If MidiFileEditor is connected, update its file too
        if self.midi_file_editor and hasattr(self.midi_file_editor, "midi_state"):
            try:
                # Reload the saved file into MidiFileEditor
                self.midi_file_editor.midi_load_file_from_path(filename)
                log.message(
                    message="Updated MidiFileEditor with saved pattern",
                    scope=self.__class__.__name__,
                )
            except Exception as ex:
                log.warning(
                    message=f"Could not update MidiFileEditor: {ex}",
                    scope=self.__class__.__name__,
                )

    def clear_pattern(self):
        """Clear the current bar's pattern, resetting all steps in the selected bar."""
        if self.current_bar_index < len(self.measures):
            measure = self.measures[self.current_bar_index]
            for row in range(4):
                for step in range(16):
                    if step < len(measure.buttons[row]):
                        measure.buttons[row][step].setChecked(False)
                        measure.buttons[row][step].NOTE = None
                        measure.buttons[row][step].NOTE_DURATION = None

            # Sync sequencer digital
            self._sync_sequencer_with_bar(self.current_bar_index)

    def _detect_bars_from_midi(self, midi_file: MidiFile) -> int:
        """Detect number of bars in MIDI file"""
        ppq = midi_file.ticks_per_beat
        beats_per_bar = 4  # Assuming 4/4 time signature
        ticks_per_bar = ppq * beats_per_bar

        max_time = 0
        for track in midi_file.tracks:
            absolute_time = 0
            for msg in track:
                absolute_time += msg.time
                if not msg.is_meta:
                    max_time = max(max_time, absolute_time)

        # Calculate number of bars (round up)
        num_bars = int((max_time / ticks_per_bar) + 1) if max_time > 0 else 1
        return max(1, num_bars)  # At least 1 bar

    def load_pattern(self, filename: str):
        """Load a pattern from a MIDI file"""
        try:
            midi_file = MidiFile(filename)
            ppq = midi_file.ticks_per_beat
            beats_per_bar = 4
            ticks_per_bar = ppq * beats_per_bar

            # Detect number of bars
            num_bars = self._detect_bars_from_midi(midi_file)
            log.message(
                message=f"Detected {num_bars} bars in MIDI file",
                scope=self.__class__.__name__,
            )

            # Clear existing bars and bars list
            self.bars_list.clear()
            self.measures.clear()

            # Create new bars without selecting them (to avoid UI flicker)
            for bar_num in range(num_bars):
                measure = PatternMeasure()

                # Initialize all buttons in the new measure as unchecked with no notes
                for row in range(4):
                    for button in measure.buttons[row]:
                        button.row = row
                        button.column = button.column  # Keep local column (0-15)
                        button.NOTE = None
                        button.NOTE_DURATION = None
                        button.NOTE_VELOCITY = None
                        button.setChecked(False)

                self.measures.append(measure)

                # Add to bars list
                item = QListWidgetItem(f"Bar {bar_num + 1}")
                item.setData(Qt.ItemDataRole.UserRole, bar_num)  # Store bar index
                self.bars_list.addItem(item)

            # Update total measures
            self.total_measures = len(self.measures)
            self._update_pattern_length()

            # Load notes from ALL tracks, mapping by MIDI channel (like Midi Editor)
            # Channel mapping: 0 -> Digital Synth 1 (row 0), 1 -> Digital Synth 2 (row 1),
            #                  2 -> Analog Synth (row 2), 9 -> Drums (row 3)
            notes_loaded = 0
            channel_to_row = {
                MidiChannel.DIGITAL_SYNTH_1: 0,  # Channel 0
                MidiChannel.DIGITAL_SYNTH_2: 1,  # Channel 1
                MidiChannel.ANALOG_SYNTH: 2,  # Channel 2
                MidiChannel.DRUM_KIT: 3,  # Channel 9
            }

            # First pass: collect all note events with their absolute times and tempos
            note_events = []  # List of (absolute_time, msg, channel, tempo_at_time)
            current_tempo = 500000  # Default tempo (120 BPM in microseconds)

            for track in midi_file.tracks:
                absolute_time = 0
                for msg in track:
                    absolute_time += msg.time

                    # Track tempo changes
                    if msg.type == "set_tempo":
                        current_tempo = msg.tempo

                    # Collect note_on and note_off events
                    if hasattr(msg, "channel") and (
                        msg.type == "note_on" or msg.type == "note_off"
                    ):
                        note_events.append(
                            (absolute_time, msg, msg.channel, current_tempo)
                        )

            # Second pass: match note_on with note_off to calculate durations
            # Dictionary to track active notes: (channel, note) -> (on_time, on_tempo)
            active_notes = {}
            note_durations = {}  # (channel, note, on_time) -> duration_ms

            for abs_time, msg, channel, tempo in note_events:
                note_key = (channel, msg.note)

                if msg.type == "note_on" and msg.velocity > 0:
                    # Store note_on event
                    active_notes[note_key] = (abs_time, tempo)
                elif msg.type == "note_off" or (
                    msg.type == "note_on" and msg.velocity == 0
                ):
                    # Find matching note_on
                    if note_key in active_notes:
                        on_time, on_tempo = active_notes[note_key]
                        duration_ticks = abs_time - on_time

                        # Convert ticks to milliseconds using the tempo at note_on time
                        # tempo is in microseconds per quarter note
                        # duration_ms = (duration_ticks / ticks_per_beat) * (tempo / 1000)
                        duration_ms = (duration_ticks / ppq) * (on_tempo / 1000.0)

                        note_durations[(channel, msg.note, on_time)] = duration_ms
                        del active_notes[note_key]

            # Third pass: assign notes and durations to buttons
            for abs_time, msg, channel, tempo in note_events:
                if msg.type == "note_on" and msg.velocity > 0:
                    # Map channel to row (skip channels we don't support)
                    if channel not in channel_to_row:
                        continue

                    row = channel_to_row[channel]

                    # Calculate which bar and step this note belongs to
                    bar_index = int(abs_time / ticks_per_bar)
                    step_in_bar = int((abs_time % ticks_per_bar) / (ticks_per_bar / 16))

                    # Ensure we have enough bars (safety check)
                    while bar_index >= len(self.measures):
                        measure = PatternMeasure()
                        for r in range(4):
                            for button in measure.buttons[r]:
                                button.row = r
                                button.column = button.column
                                button.NOTE = None
                                button.NOTE_DURATION = None
                                button.NOTE_VELOCITY = None
                                button.setChecked(False)
                        self.measures.append(measure)
                        item = QListWidgetItem(f"Bar {len(self.measures)}")
                        item.setData(Qt.ItemDataRole.UserRole, len(self.measures) - 1)
                        self.bars_list.addItem(item)

                    if bar_index < len(self.measures) and step_in_bar < 16:
                        measure = self.measures[bar_index]
                        if step_in_bar < len(measure.buttons[row]):
                            button = measure.buttons[row][step_in_bar]
                            button.setChecked(True)
                            button.NOTE = msg.note  # mido uses lowercase 'note'

                            # Store note velocity from MIDI file
                            button.NOTE_VELOCITY = msg.velocity

                            # Store note duration if available
                            duration_key = (channel, msg.note, abs_time)
                            if duration_key in note_durations:
                                button.NOTE_DURATION = note_durations[duration_key]
                            else:
                                # Default to step duration if no note_off found
                                # Step duration = (ticks_per_bar / 16) / ppq * tempo / 1000
                                step_duration_ms = (ticks_per_bar / 16.0 / ppq) * (
                                    tempo / 1000.0
                                )
                                button.NOTE_DURATION = step_duration_ms

                            notes_loaded += 1

            log.message(
                message=f"Loaded {notes_loaded} notes from MIDI file across all tracks and channels",
                scope=self.__class__.__name__,
            )

            # Update tempo from file: search all tracks for first set_tempo (many files put it in track 0, some in another track)
            tempo_bpm = None
            for track in midi_file.tracks:
                for event in track:
                    if event.type == "set_tempo":
                        tempo_bpm = int(tempo2bpm(event.tempo))
                        break
                if tempo_bpm is not None:
                    break
            if tempo_bpm is not None:
                self.tempo_spinbox.blockSignals(True)
                self.tempo_spinbox.setValue(tempo_bpm)
                self.tempo_spinbox.blockSignals(False)
                self.set_tempo(tempo_bpm)

            # Select first bar and sync sequencer digital
            if self.bars_list.count() > 0:
                self.current_bar_index = 0
                self.bars_list.setCurrentRow(0)
                self._sync_sequencer_with_bar(0)
                log.message(
                    message=f"Loaded {num_bars} bars from MIDI file. Bars are displayed in the side panel.",
                    scope=self.__class__.__name__,
                )

        except Exception as ex:
            log.error(
                message=f"Error loading pattern: {ex}", scope=self.__class__.__name__
            )
            QMessageBox.critical(self, "Error", f"Could not load pattern: {str(ex)}")

    def _add_round_action_button(
        self,
        icon_enum: Any,
        text: str,
        slot: Any,
        layout: QHBoxLayout,
        *,
        name: Optional[str] = None,
        checkable: bool = False,
        append_to: Optional[list] = None,
    ) -> QPushButton:
        """Create a round button with icon + text label (same style as Transport)."""
        btn = create_jdxi_button("")
        btn.setCheckable(checkable)
        if slot is not None:
            btn.clicked.connect(slot)
        if name:
            setattr(self, f"{name}_button", btn)
        if append_to is not None:
            append_to.append(btn)
        layout.addWidget(btn)
        pixmap = JDXi.UI.Icon.get_icon_pixmap(
            icon_enum, color=JDXi.UI.Style.FOREGROUND, size=20
        )
        label_row, _ = create_jdxi_row(text, icon_pixmap=pixmap)
        layout.addWidget(label_row)
        return btn

    def _create_transport_control(
        self,
        spec: TransportSpec,
        layout: QHBoxLayout,
        button_group: Optional[QButtonGroup],
    ) -> None:
        """Create a transport button + label row (same pattern as Midi File Player)."""
        btn = create_jdxi_button_from_spec(spec, button_group)
        setattr(self, f"{spec.name}_button", btn)
        layout.addWidget(btn)

        pixmap = JDXi.UI.Icon.get_icon_pixmap(
            spec.icon, color=JDXi.UI.Style.FOREGROUND, size=20
        )
        label_row, _ = create_jdxi_row(spec.text, icon_pixmap=pixmap)
        layout.addWidget(label_row)

    def _init_transport_controls(self) -> QGroupBox:
        """Build Transport group with Play, Stop, Pause, Shuffle Play (same style as Midi File Player)."""
        group = QGroupBox("Transport")
        centered_layout = QHBoxLayout(group)
        transport_layout = QHBoxLayout()
        centered_layout.addStretch()
        centered_layout.addLayout(transport_layout)
        centered_layout.addStretch()

        transport_button_group = QButtonGroup(self)
        transport_button_group.setExclusive(True)

        controls = [
            TransportSpec(
                "play", JDXi.UI.Icon.PLAY, "Play", self._pattern_transport_play, True
            ),
            TransportSpec(
                "stop", JDXi.UI.Icon.STOP, "Stop", self._pattern_transport_stop, True
            ),
            TransportSpec(
                "pause",
                JDXi.UI.Icon.PAUSE,
                "Pause",
                self._pattern_transport_pause_toggle,
                False,
            ),
            TransportSpec(
                "shuffle",
                JDXi.UI.Icon.SHUFFLE,
                "Shuffle Play",
                self._pattern_shuffle_play,
                True,
            ),
        ]
        for spec in controls:
            self._create_transport_control(
                spec, transport_layout, transport_button_group
            )
        return group

    def _pattern_transport_play(self) -> None:
        """Start pattern playback (delegate to play_pattern)."""
        self.play_pattern()

    def _pattern_transport_stop(self) -> None:
        """Stop pattern playback (delegate to stop_pattern)."""
        self.stop_pattern()

    def _pattern_transport_pause_toggle(self) -> None:
        """Pause or resume pattern playback."""
        if self._pattern_paused:
            if hasattr(self, "timer") and self.timer and not self.timer.isActive():
                ms_per_step = (60000 / self.bpm) / 4
                self.timer.start(int(ms_per_step))
            self._pattern_paused = False
            log.message(
                message="Pattern playback resumed", scope=self.__class__.__name__
            )
        else:
            if hasattr(self, "timer") and self.timer and self.timer.isActive():
                self.timer.stop()
            self._pattern_paused = True
            log.message(
                message="Pattern playback paused", scope=self.__class__.__name__
            )

    def _pattern_shuffle_play(self) -> None:
        """Select a random bar and start playback."""
        if not self.measures:
            return
        idx = random.randint(0, len(self.measures) - 1)
        self.current_bar_index = idx
        if self.bars_list and idx < self.bars_list.count():
            self.bars_list.setCurrentRow(idx)
        self._sync_sequencer_with_bar(idx)
        self.play_pattern()

    def play_pattern(self):
        """Start playing the pattern"""
        if hasattr(self, "timer") and self.timer and self.timer.isActive():
            return  # Already playing

        self.current_step = 0

        # Calculate interval based on tempo (ms per 16th note)
        ms_per_step = (60000 / self.bpm) / 4

        # Create and start timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._play_step)
        self.timer.start(int(ms_per_step))

        # Update button states (match transport group selection to playback state)
        if hasattr(self, "play_button") and self.play_button:
            self.play_button.blockSignals(True)
            self.play_button.setChecked(True)
            self.play_button.setEnabled(False)
            self.play_button.blockSignals(False)
        if hasattr(self, "stop_button") and self.stop_button:
            self.stop_button.setChecked(False)
            self.stop_button.setEnabled(True)

        log.message(message="Pattern playback started", scope=self.__class__.__name__)

    def stop_pattern(self):
        """Stop playing the pattern"""
        if hasattr(self, "timer") and self.timer:
            self.timer.stop()
            self.timer = None
        self._pattern_paused = False

        # Reset step counter
        self.current_step = 0

        # Update button states (match transport group selection to playback state)
        if hasattr(self, "play_button") and self.play_button:
            self.play_button.setEnabled(True)
            self.play_button.blockSignals(True)
            self.play_button.setChecked(False)
            self.play_button.blockSignals(False)
        if hasattr(self, "stop_button") and self.stop_button:
            self.stop_button.setChecked(True)
            self.stop_button.setEnabled(False)

        # Send all notes off
        if self.midi_helper:
            for channel in range(16):
                self.midi_helper.send_raw_message([CONTROL_CHANGE | channel, 123, 0])

        log.message(message="Pattern playback stopped", scope=self.__class__.__name__)

    def _note_name_to_midi(self, note_name: str) -> int:
        """Convert note name (e.g., 'C4') to MIDI note number"""
        # Note name to semitone mapping
        note_to_semitone = {
            "C": 0,
            "C#": 1,
            "D": 2,
            "D#": 3,
            "E": 4,
            "F": 5,
            "F#": 6,
            "G": 7,
            "G#": 8,
            "A": 9,
            "A#": 10,
            "B": 11,
        }

        # Split note name into note and octave
        if "#" in note_name:
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
        # Handle None or invalid input
        if midi_note is None:
            return "N/A"

        # Note mapping (reverse of note_to_semitone)
        semitone_to_note = [
            "C",
            "C#",
            "D",
            "D#",
            "E",
            "F",
            "F#",
            "G",
            "G#",
            "A",
            "A#",
            "B",
        ]

        if drums:
            # Drum notes should be in range 36-60 (mapping to indices 0-24)
            if midi_note < 36 or midi_note >= 36 + len(self.drum_options):
                # Out of range, return a fallback
                return f"Drum({midi_note})"
            return self.drum_options[midi_note - 36]

        # Calculate octave and note for non-drum notes
        # Ensure midi_note is within valid MIDI range (0-127)
        if midi_note < 0 or midi_note > 127:
            return f"Note({midi_note})"

        octave = (midi_note // 12) - 1
        note = semitone_to_note[midi_note % 12]
        return f"{note}{octave}"

    def _play_step(self):
        """Plays the current step and advances to the next one."""
        # Calculate which bar and step within that bar
        # Use beats_per_bar to determine steps per bar
        steps_per_bar = self.beats_per_bar
        total_pattern_steps = len(self.measures) * steps_per_bar
        global_step = (
            self.current_step % total_pattern_steps if total_pattern_steps > 0 else 0
        )
        bar_index = global_step // steps_per_bar
        step_in_bar = global_step % steps_per_bar

        log.message(
            message=f"Playing step {step_in_bar} in bar {bar_index + 1} "
            f"(global step {global_step}"
            f" {self.beats_per_bar} beats per bar)",
            scope=self.__class__.__name__,
        )

        # Sync sequencer with the current bar being played
        if bar_index < len(self.measures):
            self.current_bar_index = bar_index
            self._sync_sequencer_with_bar(bar_index)

            # Highlight the current bar in the bars list
            if bar_index < self.bars_list.count():
                self.bars_list.setCurrentRow(bar_index)
                # Ensure the item is visible (scroll to it if needed)
                item = self.bars_list.item(bar_index)
                if item:
                    self.bars_list.scrollToItem(item)

            # Play notes from the current bar
            measure = self.measures[bar_index]
            for row in range(4):
                if step_in_bar < len(measure.buttons[row]):
                    measure_button = measure.buttons[row][step_in_bar]
                    if (
                        measure_button.isChecked()
                        and hasattr(measure_button, "NOTE")
                        and measure_button.NOTE is not None
                    ):
                        # Determine channel based on row
                        channel = (
                            row if row < 3 else 9
                        )  # channels 0,1,2 for synths, 9 for drums

                        # Send Note On message using the stored note
                        if self.midi_helper:
                            if channel not in self.muted_channels:
                                log.message(
                                    message=f"Row {row} active at step {step_in_bar} in bar {bar_index + 1}, sending note {measure_button.NOTE} on channel {channel}",
                                    scope=self.__class__.__name__,
                                )
                                # Get velocity from button if available, otherwise use default
                                if (
                                    hasattr(measure_button, "NOTE_VELOCITY")
                                    and measure_button.NOTE_VELOCITY is not None
                                ):
                                    velocity = measure_button.NOTE_VELOCITY
                                else:
                                    velocity = self.velocity_spinbox.value()

                                self.midi_helper.send_raw_message(
                                    [NOTE_ON | channel, measure_button.NOTE, velocity]
                                )

                                # Calculate note duration
                                # Use stored duration if available, otherwise calculate default based on step length
                                if (
                                    hasattr(measure_button, "NOTE_DURATION")
                                    and measure_button.NOTE_DURATION is not None
                                ):
                                    note_duration_ms = measure_button.NOTE_DURATION
                                else:
                                    # Default: use step duration (ms per step)
                                    # ms_per_step = (60000 / bpm) / 4 (for 16th notes)
                                    note_duration_ms = (60000.0 / self.bpm) / 4.0

                                # Note Off message after the calculated duration
                                QTimer.singleShot(
                                    int(note_duration_ms),
                                    lambda ch=channel, n=measure_button.NOTE: self.midi_helper.send_raw_message(
                                        [NOTE_ON | ch, n, 0]
                                    ),
                                )
                        else:
                            log.warning(
                                message="MIDI helper not available",
                                scope=self.__class__.__name__,
                            )

        # Advance to next step (across all bars)
        steps_per_bar = self.beats_per_bar
        total_pattern_steps = len(self.measures) * steps_per_bar
        self.current_step = (
            (self.current_step + 1) % total_pattern_steps
            if total_pattern_steps > 0
            else 0
        )

        # Update UI to show current step
        for row in range(4):
            for col in range(16):  # Always 16 steps in sequencer
                if col < len(self.buttons[row]):
                    button = self.buttons[row][col]
                    is_checked = button.isChecked()
                    is_current = (
                        step_in_bar == col
                    )  # Current step within the displayed bar
                    button.setStyleSheet(
                        JDXi.UI.Style.generate_sequencer_button_style(
                            is_checked, is_current, is_selected_bar=True
                        )
                    )

    def _learn_pattern(self, message):
        """Learn the pattern of incoming MIDI notes, preserving rests."""
        if message.type == "note_on" and message.velocity > 0:
            note = message.note  # mido uses lowercase 'note'

            # Determine the correct row for the note
            for row in range(4):
                if note in self._get_note_range_for_row(row):
                    # Calculate step within current bar (0 to beats_per_bar-1)
                    step_in_bar = self.current_step % self.beats_per_bar

                    # Store note in the current bar's measure
                    if self.current_bar_index < len(self.measures):
                        measure = self.measures[self.current_bar_index]
                        if step_in_bar < len(measure.buttons[row]):
                            measure_button = measure.buttons[row][step_in_bar]
                            measure_button.setChecked(True)
                            measure_button.NOTE = note
                            # Store velocity from MIDI input
                            measure_button.NOTE_VELOCITY = message.velocity
                            # Set default duration for MIDI-learned notes
                            measure_button.NOTE_DURATION = self._get_duration_ms()

                            # Also update sequencer digital
                            if step_in_bar < len(self.buttons[row]):
                                self.buttons[row][step_in_bar].setChecked(True)
                                self.buttons[row][step_in_bar].NOTE = note

                    # Record the note in the learned pattern (for compatibility)
                    self.learned_pattern[row][step_in_bar] = note
                    self.active_notes[note] = row  # Mark the note as active

                    # Add the note_on message to the MIDI track
                    self.midi_track.append(
                        Message("note_on", note=note, velocity=message.velocity, time=0)
                    )
                    break  # Stop checking once the note is assigned

        elif message.type == "note_off":
            note = message.note  # mido uses lowercase 'note'
            if note in self.active_notes:
                # Advance step only if the note was previously turned on
                log.message(
                    message=f"Note off: {note} at step {self.current_step}",
                    scope=self.__class__.__name__,
                )
                del self.active_notes[note]  # Remove the note from active notes

                # Add the note_off message to the MIDI track
                self.midi_track.append(
                    Message("note_off", note=note, velocity=0, time=0)
                )
                # Advance step within current bar (0 to beats_per_bar-1)
                self.current_step = (self.current_step + 1) % self.beats_per_bar

    def _apply_learned_pattern(self):
        """Apply the learned pattern to the sequencer UI."""
        for row in range(4):
            # Clear current button states for the row
            for button in self.buttons[row]:
                button.setChecked(False)
                button.NOTE = None
                button.NOTE_DURATION = None
                button.setStyleSheet(
                    JDXi.UI.Style.generate_sequencer_button_style(False)
                )
                if row == 3:
                    drums_note_name = self._midi_to_note_name(button.NOTE, drums=True)
                    button.setToolTip(f"Note: {drums_note_name}")
                else:
                    note_name = self._midi_to_note_name(button.NOTE)
                    button.setToolTip(f"Note: {note_name}")

            # Apply the learned pattern
            for time, note in enumerate(self.learned_pattern[row]):
                # Ensure only one button is activated per note
                if note is not None and 0 <= time < len(self.buttons[row]):
                    button = self.buttons[row][time]
                    button.setChecked(True)
                    button.NOTE = note
                    # Set default duration for learned pattern notes
                    button.NOTE_DURATION = self._get_duration_ms()
                    # Set default velocity for learned pattern notes
                    button.NOTE_VELOCITY = self.velocity_spinbox.value()
                    button.setStyleSheet(
                        JDXi.UI.Style.generate_sequencer_button_style(True)
                    )
                    if row == 3:
                        drums_note_name = self._midi_to_note_name(
                            button.NOTE, drums=True
                        )
                        button.setToolTip(f"Note: {drums_note_name}")
                    else:
                        note_name = self._midi_to_note_name(button.NOTE)
                        button.setToolTip(f"Note: {note_name}")

    def _get_note_range_for_row(self, row):
        """Get the note range for a specific row."""
        if row in [0, 1]:
            return range(60, 72)  # C4 to B4
        if row == 2:
            return range(48, 60)  # C3 to B3
        return range(36, 48)  # C2 to B2

    def _move_to_next_step(self):
        """Move to the next step in the pattern."""
        # Move to the next step
        self.current_step = (self.current_step + 1) % self.total_steps

        # Stop learning after 16 steps
        if self.current_step == 0:
            log.message(
                message="Learning complete after 16 steps.",
                scope=self.__class__.__name__,
            )
            self.on_stop_learn_pattern_button_clicked()
            self.timer.stop()
            del self.timer
        else:
            log.message(
                message=f"Moved to step {self.current_step}",
                scope=self.__class__.__name__,
            )

    def save_midi_file(self, filename: str):
        """Save the recorded MIDI messages to a file."""
        with open(filename, "wb") as output_file:
            self.midi_file.save(output_file)
        log.message(
            message=f"MIDI file saved to {filename}", scope=self.__class__.__name__
        )

    def _toggle_mute(self, row, checked):
        """Toggle mute for a specific row."""
        channel = row if row < 3 else 9  # channels 0,1,2 for synths, 9 for drums
        if checked:
            log.message(message=f"Row {row} muted", scope=self.__class__.__name__)
            self.muted_channels.append(channel)
        else:
            log.message(message=f"Row {row} unmuted", scope=self.__class__.__name__)
            self.muted_channels.remove(channel)

        # Update the UI or internal state to reflect the mute status
        # For example, you might want to disable the buttons in the row
        for button in self.buttons[row]:
            button.setEnabled(not checked)

    def _update_drum_rows(self):
        """Update displayed buttons based on the selected drum option."""
        self.drum_selector.currentText()

        """
        for option, layout in self.drum_row_layouts.items():
            is_visible = option == selected_option

            # Iterate over widgets inside the QHBoxLayout
            for i in range(layout.count()):
                button = layout.itemAt(i).widget()
                if button:
                    button.setVisible(is_visible)
        """

        # Ensure UI updates properly
        self.update()

    def _add_measure(self):
        pass  # TODO: Add a measure
