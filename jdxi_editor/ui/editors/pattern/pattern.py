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
from typing import Any, Callable, Optional

from decologr import Decologr as log
from mido import Message, MetaMessage, MidiFile, MidiTrack, bpm2tempo, tempo2bpm

from jdxi_editor.ui.editors.pattern.helper import reset_button, reset_measure, get_button_note_spec, \
    sync_button_note_spec, update_button_state
from jdxi_editor.ui.editors.pattern.learner import (
    PatternLearner,
    PatternLearnerConfig,
    PatternLearnerEvent,
)
from jdxi_editor.ui.editors.pattern.models import NoteButtonAttrs, ButtonAttrs, ClipboardData, SequencerEvent
from jdxi_editor.ui.editors.pattern.ui import PatternUI
from jdxi_editor.ui.widgets.pattern.sequencer_button import SequencerButton
from picomidi import MidiTempo
from picomidi.message.type import MidoMessageType
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QHBoxLayout,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QWidget,
)
from rtmidi.midiconstants import CONTROL_CHANGE, NOTE_OFF, NOTE_ON

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.globals import silence_midi_note_logging
from jdxi_editor.midi.channel.channel import MidiChannel
from jdxi_editor.midi.conversion.note import MidiNoteConverter
from jdxi_editor.midi.file.controller import (
    MidiFileController,
    MidiFileControllerConfig,
)
from jdxi_editor.ui.widgets.combo_box.synchronizer import (
    ComboBoxSynchronizer,
    ComboBoxUpdateConfig,
)
from jdxi_editor.ui.sequencer.button.manager import SequencerButtonManager
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.message import MidiMessage
from jdxi_editor.ui.editors.helpers.widgets import (
    create_jdxi_button_with_label_from_spec
)
from jdxi_editor.midi.playback.controller import (
    PlaybackConfig,
    PatternPlaybackController,
)
from jdxi_editor.ui.editors.midi_player.playback.engine import (
    PlaybackEngine,
    TransportState,
)
from jdxi_editor.ui.editors.midi_player.transport.spec import (
    TransportSpec,
)
from jdxi_editor.ui.preset.helper import JDXiPresetHelper
from jdxi_editor.ui.widgets.pattern.measure import PatternMeasure
from picoui.specs.widgets import (
    ButtonSpec,
    ComboBoxSpec,
    FileSelectionSpec,
)
from picoui.widget.helper import get_file_path_from_spec


class PatternSequenceEditor(PatternUI):
    """Pattern Sequencer with MIDI Integration using mido"""

    def __init__(
            self,
            midi_helper: Optional[MidiIOHelper],
            preset_helper: Optional[JDXiPresetHelper],
            parent: Optional[QWidget] = None,
            midi_file_editor: Optional[Any] = None,
    ):
        super().__init__(parent=parent,
                         midi_helper=midi_helper,
                         preset_helper=preset_helper,
                         midi_file_editor=midi_file_editor)
        self._init_playing_controllers()
        self._connect_midi_signals()
        self._init_midi_file()
        self._initialize_default_bar()

        JDXi.UI.Theme.apply_editor_style(self)

        if self.midi_file_editor and hasattr(self.midi_file_editor, "midi_state"):
            if self.midi_file_editor.midi_state.file:
                self.load_from_midi_file_editor()

    def _init_playing_controllers(self) -> None:
        """Create MIDI/playback/learn controllers and wire them to the UI (Pattern Playing responsibility)."""
        self.playback_engine = PlaybackEngine()
        self._note_converter = MidiNoteConverter(drum_options=list(self.drum_options))

        combo_config = ComboBoxUpdateConfig()
        self._combo_synchronizer = ComboBoxSynchronizer(
            config=combo_config,
            midi_converter=self._note_converter,
            scope=self.__class__.__name__,
        )
        self._combo_synchronizer.set_all_selectors(
            self.digital1_selector,
            self.digital2_selector,
            self.analog_selector,
            self.drum_selector,
        )
        self._combo_synchronizer.set_selector_options(0, list(self.digital_options))
        self._combo_synchronizer.set_selector_options(1, list(self.digital_options))
        self._combo_synchronizer.set_selector_options(2, list(self.analog_options))
        self._combo_synchronizer.set_selector_options(3, list(self.drum_options))

        learner_config = PatternLearnerConfig(
            total_steps=self.measure_beats,
            total_rows=4,
            default_velocity=100,
            default_duration_ms=120.0,
        )
        self._pattern_learner = PatternLearner(
            config=learner_config,
            midi_converter=self._note_converter,
            scope=self.__class__.__name__,
        )
        self._pattern_learner.on_note_learned = self._on_learner_note_learned
        self._pattern_learner.on_step_advance = self._on_learner_step_advance
        self._pattern_learner.on_learning_stopped = self._on_learner_stopped

        midi_controller_config = MidiFileControllerConfig(
            ticks_per_beat=480,
            beats_per_bar=4,
            default_bpm=self.bpm,
            default_velocity=100,
        )
        self._midi_file_controller = MidiFileController(
            config=midi_controller_config,
            midi_converter=self._note_converter,
            scope=self.__class__.__name__,
        )
        self._midi_file_controller.create_new_file()
        self.midi_file = self._midi_file_controller.midi_file
        self.midi_track = self._midi_file_controller.midi_file.tracks[0]
        self.bpm = self._midi_file_controller.get_tempo()

        playback_config = PlaybackConfig(
            ticks_per_beat=480,
            beats_per_bar=4,
            measure_beats=self.measure_beats,
            default_bpm=self.bpm,
            playback_interval_ms=20,
        )
        self._playback_controller = PatternPlaybackController(
            config=playback_config,
            playback_engine=self.playback_engine,
            scope=self.__class__.__name__,
        )
        self._playback_controller.on_playback_started = self._on_playback_controller_started
        self._playback_controller.on_playback_stopped = self._on_playback_controller_stopped
        self._playback_controller.on_bar_changed = self._on_playback_bar_changed
        self._playback_controller.on_step_changed = self._on_playback_step_changed
        if self.midi_helper:
            self._playback_controller.on_midi_event = (
                lambda msg: self.midi_helper.send_raw_message(msg.bytes())
            )

        self._button_manager = SequencerButtonManager(
            midi_converter=self._note_converter,
            scope=self.__class__.__name__,
        )
        self._button_manager.set_buttons(self.buttons)
        self._button_manager.set_channel_map(self.channel_map)
        self._button_manager.set_style_generator(
            JDXi.UI.Style.generate_sequencer_button_style
        )
        self._button_manager.total_steps = self.total_steps
        self._button_manager.default_velocity = 100
        self._button_manager.default_duration_ms = 120.0
        self._button_manager.get_current_duration = self._get_duration_ms
        self._button_manager.get_current_velocity = (
            lambda: self.velocity_spinbox.value()
        )

    def _connect_midi_signals(self):
        if self._combo_synchronizer:
            self.midi_helper.midi_message_incoming.connect(
                self._combo_synchronizer.process_incoming_midi
            )
            self.midi_helper.midi_message_outgoing.connect(
                self._combo_synchronizer.process_outgoing_midi
            )

    def reset_all_measures(self):
        """reset all measures"""
        for measure in self.measures:
            reset_measure(measure)

    def add_and_reset_new_measure(self):
        """add and reset new measure"""
        measure = PatternMeasure()
        reset_measure(measure)
        self.measures.append(measure)
        return measure

    def on_learn_pattern_button_clicked(self):
        """Connect the MIDI input to the learn pattern function and start the learner."""
        if self._combo_synchronizer:
            self.midi_helper.midi_message_incoming.disconnect(
                self._combo_synchronizer.process_incoming_midi
            )
        self.midi_helper.midi_message_incoming.connect(self._learn_pattern)
        self._pattern_learner.start_learning()
        self.current_step = self._pattern_learner.current_step

    def on_stop_learn_pattern_button_clicked(self):
        """Disconnect the MIDI input from the learn pattern function and stop the learner."""
        self.midi_helper.midi_message_incoming.disconnect(self._learn_pattern)
        self._pattern_learner.stop_learning()
        if self._combo_synchronizer:
            self.midi_helper.midi_message_incoming.connect(
                self._combo_synchronizer.process_incoming_midi
            )
        self._sync_midi_track_from_learner()

    def _on_learner_note_learned(self, event: PatternLearnerEvent) -> None:
        """Update measure and sequencer buttons from a learned note event; append NOTE_ON to midi_track."""
        step_in_bar = event.step
        row = event.row
        if self.current_measure_index < len(self.measures):
            measure = self.measures[self.current_measure_index]
            if step_in_bar < len(measure.buttons[row]):
                measure_button = measure.buttons[row][step_in_bar]
                update_button_state(measure_button, True)
                measure_button.note = event.note
                measure_button.note_velocity = event.velocity
                measure_button.note_duration = event.duration_ms
                sync_button_note_spec(measure_button)
        if step_in_bar < len(self.buttons[row]):
            seq_btn = self.buttons[row][step_in_bar]
            update_button_state(seq_btn, True)
            seq_btn.note = event.note
            seq_btn.note_velocity = event.velocity
            seq_btn.note_duration = event.duration_ms
            sync_button_note_spec(seq_btn)
        self.midi_track.append(
            Message(
                MidoMessageType.NOTE_ON,
                note=event.note,
                velocity=event.velocity,
                time=0,
            )
        )

    def _on_learner_step_advance(self, step: int) -> None:
        """Keep editor current_step in sync with the learner."""
        self.current_step = step

    def _on_learner_stopped(self) -> None:
        """When learner stops (e.g. after 16 steps): disconnect learn handler and reconnect combo updates."""
        self.midi_helper.midi_message_incoming.disconnect(self._learn_pattern)
        if self._combo_synchronizer:
            self.midi_helper.midi_message_incoming.connect(
                self._combo_synchronizer.process_incoming_midi
            )
        self._sync_midi_track_from_learner()

    def _sync_midi_track_from_learner(self) -> None:
        """Copy learned MIDI messages into the editor's midi_track for saving."""
        self.midi_track.clear()
        self.midi_track.extend(self._pattern_learner.get_midi_track())

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
                if (status_byte & MidiMessage.MIDI_STATUS_MASK) in (
                        NOTE_ON,
                        NOTE_OFF,
                ):  # Note On or Note Off
                    channel = status_byte & MidiMessage.MIDI_STATUS_MASK
                    msg_type = (
                        MidoMessageType.NOTE_ON
                        if (status_byte & MidiMessage.MIDI_STATUS_MASK) == NOTE_ON
                           and velocity > 0
                        else MidoMessageType.NOTE_OFF
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
        if message.type == MidoMessageType.NOTE_ON and message.velocity > 0:
            note = message.note  # mido uses lowercase 'note'
            channel = message.channel
            if not silence_midi_note_logging():
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

            channel_map = {
                MidiChannel.DIGITAL_SYNTH_1: self.digital1_selector,
                MidiChannel.DIGITAL_SYNTH_2: self.digital2_selector,
                MidiChannel.ANALOG_SYNTH: self.analog_selector,
                MidiChannel.DRUM_KIT: self.drum_selector,
            }
            selector = channel_map.get(channel)
            if selector is not None:
                if combo_index < selector.count():
                    selector.setCurrentIndex(combo_index)

    def _midi_note_to_combo_index(self, row: int, midi_note: int):
        """Convert a MIDI note number to the corresponding combo box index."""
        row_options = {
            0: list(self.digital_options),
            1: list(self.digital_options),
            2: list(self.analog_options),
            3: list(self.drum_options),
        }.get(row)
        return self._note_converter.midi_note_to_combo_index(
            row, midi_note, row_options=row_options
        )

    def _set_combo_box_index(self, row, index):
        """Set the combo box index for the specified row."""
        self.channel_map = self._build_channel_map()
        self._button_manager.set_channel_map(self.channel_map)
        selector = self.channel_map.get(row)
        if selector is not None:
            selector.setCurrentIndex(index)

    def _initialize_default_bar(self):
        """Initialize with one default bar"""
        self._add_measure()

    def _add_measure(self):
        """Add a new measure to the pattern, optionally copying from the previous bar"""
        measure_number = len(self.measures) + 1

        # Check if we should copy the previous bar
        copy_previous = self.copy_previous_measure_checkbox.isChecked()

        if copy_previous and len(self.measures) > 0:
            measure = PatternMeasure()
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
                        update_button_state(new_button, previous_button.isChecked())
                        new_button.note = previous_button.note
                        # Copy duration if available
                        if hasattr(previous_button, NoteButtonAttrs.NOTE_DURATION):
                            new_button.note_duration = previous_button.note_duration
                        else:
                            new_button.note_duration = None
                        # Copy velocity if available
                        if hasattr(previous_button, NoteButtonAttrs.NOTE_VELOCITY):
                            new_button.note_velocity = previous_button.note_velocity
                        else:
                            new_button.note_velocity = None
            self.measures.append(measure)
        else:
            measure = self.add_and_reset_new_measure()

        # Add to bars list
        item = QListWidgetItem(f"{self.measure_name} {measure_number}")
        item.setData(
            Qt.ItemDataRole.UserRole, len(self.measures) - 1
        )  # Store bar index
        self.measures_list.addItem(item)

        # Select the new bar and sync sequencer digital
        self.measures_list.setCurrentItem(item)
        self.current_measure_index = len(self.measures) - 1

        # Update total measures (but keep total_steps at 16)
        self.total_measures = len(self.measures)
        self._update_pattern_length()

        # Sync sequencer buttons with the new (empty) bar
        self._sync_sequencer_with_measure(self.current_measure_index)

        log.message(
            message=f"Added measure {measure_number}. Total bars: {self.total_measures}",
            scope=self.__class__.__name__,
        )

    def _on_measure_selected(self, item: QListWidgetItem):
        """Handle measure selection from list"""
        measure_index = item.data(Qt.ItemDataRole.UserRole)
        if measure_index is not None:
            self.current_measure_index = measure_index
            # Sync sequencer buttons with the selected bar's notes
            self._sync_sequencer_with_measure(measure_index)
            log.message(
                message=f"Selected bar {measure_index + 1}",
                scope=self.__class__.__name__,
            )

    def _copy_section(self):
        """Copy a section of notes from the current bar"""
        if self.current_measure_index >= len(self.measures):
            QMessageBox.warning(self, "Copy", "No bar selected")
            return

        start_step = self.start_step_spinbox.value()
        end_step = self.end_step_spinbox.value()

        if start_step > end_step:
            QMessageBox.warning(self, "Copy", "Start step must be <= end step")
            return

        measure = self.measures[self.current_measure_index]
        notes_data = {}

        # Copy all rows and selected steps (use NoteButtonSpec for note data)
        for row in range(4):
            notes_data[row] = {}
            for step in range(start_step, end_step + 1):
                if step < len(measure.buttons[row]):
                    button = measure.buttons[row][step]
                    spec = get_button_note_spec(button)
                    notes_data[row][step] = {
                        ButtonAttrs.CHECKED: button.isChecked(),
                        ButtonAttrs.NOTE: spec.note,
                        ButtonAttrs.DURATION: (
                            spec.duration_ms if spec.is_active else None
                        ),
                        ButtonAttrs.VELOCITY: spec.velocity if spec.is_active else None,
                    }

        self.clipboard = {
            ClipboardData.SOURCE_BAR: self.current_measure_index,
            ClipboardData.START_STEP: start_step,
            ClipboardData.END_STEP: end_step,
            ClipboardData.NOTES_DATA: notes_data,
        }

        update_button_state(self.paste_button, self.paste_button.isChecked())
        log.message(
            message=f"Copied steps {start_step}-{end_step} from bar {self.current_measure_index + 1}",
            scope=self.__class__.__name__,
        )

    def _paste_section(self):
        """Paste copied section to the current bar"""
        if self.clipboard is None:
            QMessageBox.warning(
                self, "Paste", "Nothing copied. Use Copy Section first."
            )
            return

        if self.current_measure_index >= len(self.measures):
            QMessageBox.warning(self, "Paste", "No bar selected")
            return

        measure = self.measures[self.current_measure_index]
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
                        update_button_state(button, button_data[ButtonAttrs.CHECKED])
                        button.note = button_data[ButtonAttrs.NOTE]
                        button.note_duration = button_data[ButtonAttrs.DURATION]
                        button.note_velocity = button_data[ButtonAttrs.VELOCITY]
                        sync_button_note_spec(button)

        # Sync sequencer digital
        self._sync_sequencer_with_measure(self.current_measure_index)
        log.message(
            message=f"Pasted {num_steps} steps to bar {self.current_measure_index + 1} starting at step {start_step}",
            scope=self.__class__.__name__,
        )

    def _sync_sequencer_with_measure(self, bar_index: int):
        """
        Sync the main sequencer buttons with the notes from the specified bar
        via SequencerButtonManager.
        """
        if bar_index < 0 or bar_index >= len(self.measures):
            return
        self._button_manager.current_measure_index = self.current_measure_index
        self._button_manager.current_step = self.current_step
        self._button_manager.total_steps = self.total_steps
        self._button_manager.sync_sequencer_with_measure(bar_index, self.measures)

    def _highlight_bar(self, bar_index: int):
        """Update button styles to highlight the current step in the selected bar."""
        if bar_index < 0 or bar_index >= len(self.measures):
            return
        self._button_manager.current_step = self.current_step
        self._button_manager.total_steps = self.total_steps
        self._button_manager.highlight_bar(bar_index)

    def _clear_learned_pattern(self):
        """Clear the learned pattern and reset sequencer button states via manager."""
        self._pattern_learner.clear_learned_pattern()
        self.midi_track.clear()
        self._button_manager.reset_all_buttons()
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

    def _on_button_clicked(self, button: SequencerButton, checked_state: bool):
        """Handle button clicks via SequencerButtonManager."""
        self._button_manager.current_measure_index = self.current_measure_index
        self._button_manager.current_step = self.current_step
        self._button_manager.total_steps = self.total_steps
        self._button_manager.handle_button_click(button, checked_state, self.measures)

    def _on_beats_per_bar_changed(self, index: int):
        """Handle beats per bar changes from the combobox"""
        if index == 0:
            self.measure_beats = 16
        else:
            self.measure_beats = 12

        # Update button states based on beats per bar
        self._update_button_states_for_beats_per_bar()
        log.message(f"Beats per bar changed to {self.measure_beats}")

    def _update_button_states_for_beats_per_bar(self):
        """Enable/disable sequencer buttons based on beats per bar setting"""
        # Steps 0-11 are always enabled, steps 12-15 are disabled when beats_per_bar is 12
        for row in range(4):
            for step in range(16):
                if step < len(self.buttons[row]):
                    button = self.buttons[row][step]
                    if self.measure_beats == 12:
                        # Disable last 4 buttons (steps 12-15)
                        button.setEnabled(step < 12)
                        if step >= 12:
                            button.setEnabled(False)
                            button.setChecked(False)  # Uncheck disabled buttons
                            for measure in self.measures:
                                if step < len(measure.buttons[row]):
                                    reset_button(measure.buttons[row][step])
                    else:
                        # Enable all 16 buttons
                        update_button_state(button, button.isChecked())

        # Sync sequencer digital after updating button states
        if self.current_measure_index < len(self.measures):
            self._sync_sequencer_with_measure(self.current_measure_index)

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
        spec = FileSelectionSpec(
            mode="save",
            caption="Save Pattern",
            default_name="",
            filter="MIDI Files (*.mid);;All Files (*.*)",
        )
        filename = get_file_path_from_spec(self, spec)

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
        spec = FileSelectionSpec(
            mode="open",
            caption="Load Pattern",
            filter="MIDI Files (*.mid);;All Files (*.*)",
        )
        filename = get_file_path_from_spec(self, spec)

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
        """Set the pattern tempo in BPM using the MIDI file controller."""
        self._midi_file_controller.set_tempo(bpm)
        self.bpm = self._midi_file_controller.get_tempo()

        # Update playback speed if sequence is running
        if hasattr(self, "timer") and self.timer and self.timer.isActive():
            ms_per_step = (60000 / self.bpm) / 4  # ms per 16th note
            self.timer.setInterval(int(ms_per_step))

        log.message(
            message=f"Tempo set to {self.bpm} BPM", scope=self.__class__.__name__
        )

    def _init_midi_file(self):
        """Initialize a new MIDI file using the MIDI file controller."""
        self._midi_file_controller.create_new_file()
        self.midi_file = self._midi_file_controller.midi_file
        self.midi_track = self._midi_file_controller.midi_file.tracks[0]
        self.bpm = self._midi_file_controller.get_tempo()

    def update_pattern(self):
        """Update the MIDI file with current pattern state"""
        self.midi_file = MidiFile()
        track = MidiTrack()
        self.midi_file.tracks.append(track)

        track.append(MetaMessage(MidoMessageType.SET_TEMPO, tempo=bpm2tempo(self.bpm)))
        track.append(MetaMessage("time_signature", numerator=4, denominator=4))

        for row in range(4):
            channel = row if row < 3 else 9
            for measure_index, measure in enumerate(self.measures):
                for step in range(16):
                    button = measure.buttons[row][step]
                    spec = get_button_note_spec(button)
                    if button.isChecked() and spec.is_active:
                        time = int(
                            (measure_index * 16 + step) * 120
                        )  # Convert to ticks
                        track.append(
                            Message(
                                MidoMessageType.NOTE_ON,
                                note=spec.note,
                                velocity=spec.velocity,
                                time=time,
                                channel=channel,
                            )
                        )
                        track.append(
                            Message(
                                MidoMessageType.NOTE_OFF,
                                note=spec.note,
                                velocity=spec.velocity,
                                time=time + 120,
                                channel=channel,
                            )
                        )

                        note_name = (
                            self._midi_to_note_name(spec.note, drums=True)
                            if row == 3
                            else self._midi_to_note_name(spec.note)
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
            self.measures_list.clear()
            self.measures.clear()

            # Create new bars
            for measure_num in range(num_bars):
                measure = PatternMeasure()
                reset_measure(measure)
                self.measures.append(measure)
                item = QListWidgetItem(f"measure {measure_num + 1}")
                item.setData(Qt.ItemDataRole.UserRole, measure_num)
                self.measures_list.addItem(item)

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
                    if msg.type == MidoMessageType.NOTE_ON and msg.velocity > 0:
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
                            reset_measure(measure)
                            self.measures.append(measure)
                            item = QListWidgetItem(
                                f"{self.measure_name} {len(self.measures)}"
                            )
                            item.setData(
                                Qt.ItemDataRole.UserRole, len(self.measures) - 1
                            )
                            self.measures_list.addItem(item)

                        if bar_index < len(self.measures) and step_in_bar < 16:
                            measure = self.measures[bar_index]
                            if step_in_bar < len(measure.buttons[row]):
                                button = measure.buttons[row][step_in_bar]
                                update_button_state(button, True)
                                button.note = msg.note
                                # Store velocity from MIDI file editor
                                button.note_velocity = (
                                    msg.velocity
                                    if hasattr(msg, "velocity")
                                    else self.velocity_spinbox.value()
                                )
                                # Set default duration for MIDI file editor loaded notes
                                button.note_duration = self._get_duration_ms()
                                sync_button_note_spec(button)
                                notes_loaded += 1

            # Update tempo from file: search all tracks for first set_tempo
            tempo_bpm = None
            for track in midi_file.tracks:
                for event in track:
                    if event.type == MidoMessageType.SET_TEMPO:
                        tempo_bpm = int(tempo2bpm(event.tempo))
                        break
                if tempo_bpm is not None:
                    break
            if tempo_bpm is not None:
                self.set_spinbox_value(self.tempo_spinbox, tempo_bpm)
                self.set_tempo(tempo_bpm)

            # Select first bar and sync
            if self.measures_list.count() > 0:
                self.current_measure_index = 0
                self.measures_list.setCurrentRow(0)
                self._sync_sequencer_with_measure(0)
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
        """Save the current pattern to a MIDI file using the MIDI file controller."""
        success = self._midi_file_controller.save_pattern(
            filename, self.measures, pattern_name=None
        )
        if not success:
            log.warning(
                message=f"Failed to save pattern to {filename}",
                scope=self.__class__.__name__,
            )
            return

        # Keep editor references in sync with controller's current file
        self.midi_file = self._midi_file_controller.midi_file
        self.midi_track = (
            self.midi_file.tracks[0] if self.midi_file.tracks else None
        )

        log.message(
            message=f"Pattern saved to {filename}", scope=self.__class__.__name__
        )

        # If MidiFileEditor is connected, update its file too
        if self.midi_file_editor and hasattr(self.midi_file_editor, "midi_state"):
            try:
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
        if self.current_measure_index < len(self.measures):
            measure = self.measures[self.current_measure_index]
            for row in range(4):
                for step in range(16):
                    if step < len(measure.buttons[row]):
                        reset_button(measure.buttons[row][step])

            # Sync sequencer digital
            self._sync_sequencer_with_measure(self.current_measure_index)

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
            self.measures_list.clear()
            self.measures.clear()

            # Create new bars without selecting them (to avoid UI flicker)
            for bar_num in range(num_bars):
                measure = PatternMeasure()
                reset_measure(measure)
                self.measures.append(measure)

                # Add to bars list
                item = QListWidgetItem(f"{self.measure_name} {bar_num + 1}")
                item.setData(Qt.ItemDataRole.UserRole, bar_num)  # Store bar index
                self.measures_list.addItem(item)

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
                    if msg.type == MidoMessageType.SET_TEMPO:
                        current_tempo = msg.tempo

                    # Collect note_on and note_off events
                    if hasattr(msg, "channel") and (
                            msg.type == MidoMessageType.NOTE_ON
                            or msg.type == MidoMessageType.NOTE_OFF
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

                if msg.type == MidoMessageType.NOTE_ON and msg.velocity > 0:
                    # Store note_on event
                    active_notes[note_key] = (abs_time, tempo)
                elif msg.type == MidoMessageType.NOTE_OFF or (
                        msg.type == MidoMessageType.NOTE_ON and msg.velocity == 0
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
                if msg.type == MidoMessageType.NOTE_ON and msg.velocity > 0:
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
                        reset_measure(measure)
                        self.measures.append(measure)
                        item = QListWidgetItem(
                            f"[{self.measure_name} {len(self.measures)}"
                        )
                        item.setData(Qt.ItemDataRole.UserRole, len(self.measures) - 1)
                        self.measures_list.addItem(item)

                    if bar_index < len(self.measures) and step_in_bar < 16:
                        measure = self.measures[bar_index]
                        if step_in_bar < len(measure.buttons[row]):
                            button = measure.buttons[row][step_in_bar]
                            update_button_state(button, True)
                            button.note = msg.note  # mido uses lowercase 'note'

                            # Store note velocity from MIDI file
                            button.note_velocity = msg.velocity

                            # Store note duration if available
                            duration_key = (channel, msg.note, abs_time)
                            if duration_key in note_durations:
                                button.note_duration = note_durations[duration_key]
                            else:
                                # Default to step duration if no note_off found
                                # Step duration = (ticks_per_bar / 16) / ppq * tempo / 1000
                                step_duration_ms = (ticks_per_bar / 16.0 / ppq) * (
                                        tempo / 1000.0
                                )
                                button.note_duration = step_duration_ms

                            sync_button_note_spec(button)
                            notes_loaded += 1

            log.message(
                message=f"Loaded {notes_loaded} notes from MIDI file across all tracks and channels",
                scope=self.__class__.__name__,
            )

            # Update tempo from file: search all tracks for first set_tempo (many files put it in track 0, some in another track)
            tempo_bpm = None
            for track in midi_file.tracks:
                for event in track:
                    if event.type == MidoMessageType.SET_TEMPO:
                        tempo_bpm = int(tempo2bpm(event.tempo))
                        break
                if tempo_bpm is not None:
                    break
            if tempo_bpm is not None:
                self.set_spinbox_value(self.tempo_spinbox, tempo_bpm)
                self.set_tempo(tempo_bpm)

            # Select first bar and sync sequencer digital
            if self.measures_list.count() > 0:
                self.current_measure_index = 0
                self.measures_list.setCurrentRow(0)
                self._sync_sequencer_with_measure(0)
                log.message(
                    message=f"Loaded {num_bars} bars from MIDI file. Bars are displayed in the side panel.",
                    scope=self.__class__.__name__,
                )

        except Exception as ex:
            log.error(
                message=f"Error loading pattern: {ex}", scope=self.__class__.__name__
            )
            QMessageBox.critical(self, "Error", f"Could not load pattern: {str(ex)}")

    def set_spinbox_value(self, spinbox: QSpinBox, value: int):
        """set spinbox value safely"""
        spinbox.blockSignals(True)
        spinbox.setValue(value)
        spinbox.blockSignals(False)

    def _add_button_with_label_from_spec(
            self,
            name: str,
            spec: ButtonSpec,
            layout: QHBoxLayout,
            slot: Optional[Callable[[], None]] = None,
    ) -> QPushButton:
        """Create a round button + label row from a ButtonSpec and add to layout."""
        label_row, btn = create_jdxi_button_with_label_from_spec(spec, checkable=False)
        setattr(self, f"{name}_button", btn)
        layout.addWidget(btn)
        layout.addWidget(label_row)
        if slot is not None:
            btn.clicked.connect(slot)
        return btn

    def _on_playback_controller_started(self) -> None:
        """Update play/stop buttons when playback controller starts."""
        if hasattr(self, "play_button") and self.play_button:
            update_button_state(self.play_button, checked_state=True)
        if hasattr(self, "stop_button") and self.stop_button:
            update_button_state(self.stop_button, checked_state=False)

    def _on_playback_controller_stopped(self) -> None:
        """Sync UI when playback controller stops (timer already stopped by controller)."""
        self._pattern_paused = False
        if hasattr(self, "play_button") and self.play_button:
            update_button_state(self.play_button, checked_state=False)
        if hasattr(self, "stop_button") and self.stop_button:
            update_button_state(self.stop_button, checked_state=True)
        self.current_step = 0

    def _on_playback_bar_changed(self, bar_index: int) -> None:
        """Sync sequencer and measure list to the current bar during playback."""
        self.current_measure_index = bar_index
        self._sync_sequencer_with_measure(bar_index)
        if self.measures_list and bar_index < self.measures_list.count():
            self.measures_list.setCurrentRow(bar_index)
            item = self.measures_list.item(bar_index)
            if item:
                self.measures_list.scrollToItem(item)

    def _on_playback_step_changed(self, step_in_bar: int) -> None:
        """Update step highlight during playback."""
        last_step = getattr(self, "_playback_last_step_in_bar", -1)
        for row in range(4):
            if last_step >= 0 and last_step < len(self.buttons[row]):
                btn = self.buttons[row][last_step]
                btn.setStyleSheet(
                    JDXi.UI.Style.generate_sequencer_button_style(
                        btn.isChecked(), False, is_selected_bar=True
                    )
                )
            if step_in_bar < len(self.buttons[row]):
                btn = self.buttons[row][step_in_bar]
                btn.setStyleSheet(
                    JDXi.UI.Style.generate_sequencer_button_style(
                        btn.isChecked(), True, is_selected_bar=True
                    )
                )
        self._playback_last_step_in_bar = step_in_bar

    def _pattern_transport_play(self) -> None:
        """Start pattern playback via PatternPlaybackController."""
        self.play_pattern()

    def _pattern_transport_stop(self) -> None:
        """Stop pattern playback via PatternPlaybackController."""
        self.stop_pattern()

    def _pattern_transport_pause_toggle(self) -> None:
        """Pause or resume pattern playback via PatternPlaybackController."""
        if self._playback_controller:
            self._playback_controller.toggle_pause()
            self._pattern_paused = self._playback_controller.is_paused

    def _pattern_shuffle_play(self) -> None:
        """Select a random bar and start playback via PatternPlaybackController."""
        if not self.measures or not self._playback_controller:
            return
        self._playback_controller.shuffle_play(self.measures, self.bpm)

    def _ms_to_ticks(self, duration_ms: int, ticks_per_beat: int) -> int:
        """
        Convert milliseconds to MIDI ticks.
        1 beat = 60000 / bpm ms = ticks_per_beat ticks
        """
        if duration_ms <= 0:
            return 0

        ticks = duration_ms * self.bpm * ticks_per_beat / 60000
        return max(1, int(ticks))

    def _collect_sequencer_events(self, ticks_per_beat: int) -> list[SequencerEvent]:
        """collect sequencer events"""
        ticks_per_step = ticks_per_beat // 4  # 16th
        events: list[SequencerEvent] = []

        for bar_index, measure in enumerate(self.measures):
            for step in range(min(self.measure_beats, 16)):

                tick = (bar_index * self.measure_beats + step) * ticks_per_step

                for row in range(4):
                    if step >= len(measure.buttons[row]):
                        continue

                    channel = row if row < 3 else 9
                    if channel in self.muted_channels:
                        continue

                    btn = measure.buttons[row][step]
                    if not btn.isChecked():
                        continue
                    spec = get_button_note_spec(btn)

                    if not spec.is_active:
                        continue

                    channel = row if row < 3 else 9
                    velocity = max(0, min(127, spec.velocity))
                    duration_ticks = (
                            self._ms_to_ticks(spec.duration_ms, ticks_per_beat)
                            or ticks_per_step
                    )

                    events.append(
                        SequencerEvent(
                            tick=tick,
                            note=spec.note,
                            velocity=velocity,
                            channel=channel,
                            duration_ticks=duration_ticks,
                        )
                    )

        return events

    def _build_midi_file_for_playback(self) -> MidiFile:
        """Build a MidiFile from the current pattern for PlaybackEngine."""
        ticks_per_beat = 480
        tempo_us = int(MidiTempo.MICROSECONDS_PER_MINUTE / self.bpm)

        seq_events = self._collect_sequencer_events(ticks_per_beat)

        mid = MidiFile(type=1, ticks_per_beat=ticks_per_beat)
        track = MidiTrack()
        mid.tracks.append(track)

        track.append(
            MetaMessage(
                MidoMessageType.SET_TEMPO,
                tempo=tempo_us,
                time=0,
            )
        )

        if not seq_events:
            return mid

        # Expand note_on / note_off
        midi_events = []

        for e in seq_events:
            midi_events.append(
                (
                    e.tick,
                    Message(
                        MidoMessageType.NOTE_ON,
                        note=e.note,
                        velocity=e.velocity,
                        channel=e.channel,
                        time=0,
                    ),
                )
            )
            midi_events.append(
                (
                    e.tick + e.duration_ticks,
                    Message(
                        MidoMessageType.NOTE_OFF,
                        note=e.note,
                        velocity=0,
                        channel=e.channel,
                        time=0,
                    ),
                )
            )

        midi_events.sort(key=lambda x: x[0])

        prev_tick = 0
        for tick, msg in midi_events:
            delta = tick - prev_tick
            track.append(
                Message(
                    msg.type,
                    note=msg.note,
                    velocity=msg.velocity,
                    channel=msg.channel,
                    time=delta,
                )
            )
            prev_tick = tick

        return mid

    def play_pattern(self):
        """Start playing the pattern via PatternPlaybackController."""
        if not self._playback_controller or not self.measures:
            return

        # Sync mute state into controller
        self._playback_controller.muted_channels = list(self.muted_channels)
        self._playback_controller.current_bpm = self.bpm

        if not self._playback_controller.start_playback(self.measures, self.bpm):
            return

        # Controller creates timer but does not start it; we connect and start
        ctrl = self._playback_controller
        if ctrl.timer:
            ctrl.timer.setParent(self)
            ctrl.timer.timeout.connect(self._on_playback_tick)
            ctrl.timer.start(ctrl.config.playback_interval_ms)
        self._playback_last_bar_index = -1
        self._playback_last_step_in_bar = -1

    def _on_playback_tick(self):
        """Drive PatternPlaybackController and sync position; callbacks handle bar/step UI."""
        if not self._playback_controller:
            return
        total_steps = (
            len(self.measures) * self.measure_beats if self.measures else 0
        )
        pos = self._playback_controller.process_playback_tick(total_steps)
        if pos is not None:
            self.current_step = pos.global_step
        else:
            # Playback stopped; controller already called on_playback_stopped
            log.message(
                message="Pattern playback finished",
                scope=self.__class__.__name__,
            )

    def _sync_ui_to_stopped(self) -> None:
        """Sync UI to stopped state (e.g. when engine stops without controller)."""
        if hasattr(self, "timer") and self.timer:
            self.timer.stop()
            self.timer = None
        self._pattern_paused = False
        if hasattr(self, "play_button") and self.play_button:
            update_button_state(self.play_button, checked_state=False)
        if hasattr(self, "stop_button") and self.stop_button:
            update_button_state(
                self.stop_button, checked_state=True, enabled_state=False
            )
        self.current_step = 0

    def _update_transport_ui(self):
        """update ui regarding playing state"""
        is_playing = self._state == TransportState.PLAYING
        is_stopped = self._state == TransportState.STOPPED
        if hasattr(self, "play_button"):
            update_button_state(
                self.play_button, checked_state=is_playing, enabled_state=not is_playing
            )
        update_button_state(
            self.stop_button, checked_state=is_stopped, enabled_state=not is_stopped
        )

    def stop_pattern(self):
        """Stop playing the pattern via PatternPlaybackController."""
        if self._playback_controller:
            self._playback_controller.stop_playback()
        else:
            self.playback_engine.stop()
        self._on_playback_controller_stopped()

        # Send all notes off
        if self.midi_helper:
            for channel in range(16):
                self.midi_helper.send_raw_message([CONTROL_CHANGE | channel, 123, 0])

        log.message(message="Pattern playback stopped", scope=self.__class__.__name__)

    def _note_name_to_midi(self, note_name: str) -> int:
        """Convert note name (e.g., 'C4') to MIDI note number."""
        return self._note_converter.note_name_to_midi(note_name)

    def _midi_to_note_name(self, midi_note: int, drums: bool = False) -> str:
        """Convert MIDI note number to note name (e.g., 60 -> 'C4') or drum name."""
        return self._note_converter.midi_to_note_name(midi_note, drums=drums)

    def _play_step(self):
        """Plays the current step and advances to the next one."""
        # Calculate which bar and step within that bar
        # Use beats_per_bar to determine steps per bar
        steps_per_bar = self.measure_beats
        total_pattern_steps = len(self.measures) * steps_per_bar
        global_step = (
            self.current_step % total_pattern_steps if total_pattern_steps > 0 else 0
        )
        bar_index = global_step // steps_per_bar
        step_in_bar = global_step % steps_per_bar

        log.message(
            message=f"Playing step {step_in_bar} in bar {bar_index + 1} "
                    f"(global step {global_step}"
                    f" {self.measure_beats} beats per bar)",
            scope=self.__class__.__name__,
        )

        # Sync sequencer with the current bar being played
        if bar_index < len(self.measures):
            self.current_measure_index = bar_index
            self._sync_sequencer_with_measure(bar_index)

            # Highlight the current bar in the bars list
            if bar_index < self.measures_list.count():
                self.measures_list.setCurrentRow(bar_index)
                # Ensure the item is visible (scroll to it if needed)
                item = self.measures_list.item(bar_index)
                if item:
                    self.measures_list.scrollToItem(item)

            # Play notes from the current bar
            measure = self.measures[bar_index]
            for row in range(4):
                if step_in_bar < len(measure.buttons[row]):
                    measure_button = measure.buttons[row][step_in_bar]
                    play_spec = get_button_note_spec(measure_button)
                    if measure_button.isChecked() and play_spec.is_active:
                        # Determine channel based on row
                        channel = (
                            row if row < 3 else 9
                        )  # channels 0,1,2 for synths, 9 for drums

                        # Send Note On message using the stored note
                        if self.midi_helper:
                            if channel not in self.muted_channels:
                                log.message(
                                    message=f"Row {row} active at step {step_in_bar} in bar {bar_index + 1}, sending note {play_spec.note} on channel {channel}",
                                    scope=self.__class__.__name__,
                                )
                                self.midi_helper.send_raw_message(
                                    [
                                        NOTE_ON | channel,
                                        play_spec.note,
                                        play_spec.velocity,
                                    ]
                                )

                                # Note Off after stored duration (NoteButtonSpec.duration_ms) or step default
                                note_duration_ms = play_spec.duration_ms or (
                                        (60000.0 / self.bpm) / 4.0
                                )

                                QTimer.singleShot(
                                    int(note_duration_ms),
                                    lambda ch=channel, n=play_spec.note: self.midi_helper.send_raw_message(
                                        [NOTE_ON | ch, n, 0]
                                    ),
                                )
                        else:
                            log.warning(
                                message="MIDI helper not available",
                                scope=self.__class__.__name__,
                            )

        # Advance to next step (across all bars)
        steps_per_bar = self.measure_beats
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
        """Delegate incoming MIDI to the pattern learner; UI updates happen in _on_learner_note_learned."""
        self._pattern_learner.process_midi_message(message)

    def _apply_learned_pattern(self):
        """Apply the learned pattern to the sequencer UI."""
        learned = self._pattern_learner.get_learned_pattern()
        for row in range(4):
            for button in self.buttons[row]:
                reset_button(button)
                button.setStyleSheet(
                    JDXi.UI.Style.generate_sequencer_button_style(False)
                )
                button.setToolTip("")

            # Apply the learned pattern
            for time, note in enumerate(learned[row]):
                # Ensure only one button is activated per note
                if note is not None and 0 <= time < len(self.buttons[row]):
                    button = self.buttons[row][time]
                    update_button_state(button, True)
                    button.note = note
                    # Set default duration for learned pattern notes
                    button.note_duration = self._get_duration_ms()
                    # Set default velocity for learned pattern notes
                    button.note_velocity = self.velocity_spinbox.value()
                    sync_button_note_spec(button)
                    button.setStyleSheet(
                        JDXi.UI.Style.generate_sequencer_button_style(True)
                    )
                    if row == 3:
                        drums_note_name = self._midi_to_note_name(
                            button.note, drums=True
                        )
                        button.setToolTip(f"Note: {drums_note_name}")
                    else:
                        note_name = self._midi_to_note_name(button.note)
                        button.setToolTip(f"Note: {note_name}")

    def _get_note_range_for_row(self, row: int) -> range:
        """Get the note range for a specific row."""
        return self._note_converter.get_note_range_for_row(row)

    def save_midi_file(self, filename: str):
        """Save the recorded MIDI messages to a file."""
        with open(filename, "wb") as output_file:
            self.midi_file.save(output_file)
        log.message(
            message=f"MIDI file saved to {filename}", scope=self.__class__.__name__
        )

    def _toggle_mute(self, row, checked):
        """Toggle mute for a specific row; keep PatternPlaybackController in sync."""
        channel = row if row < 3 else 9  # channels 0,1,2 for synths, 9 for drums
        if checked:
            log.message(message=f"Row {row} muted", scope=self.__class__.__name__)
            self.muted_channels.append(channel)
        else:
            log.message(message=f"Row {row} unmuted", scope=self.__class__.__name__)
            self.muted_channels.remove(channel)
        if self._playback_controller:
            self._playback_controller.mute_row(row, checked)

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

    def _build_specs(self) -> dict[str, Any]:
        """Assemble all pattern editor button and combo specs for use in _setup_ui."""
        return {
            "buttons": {
                "load": ButtonSpec(
                    label="Load",
                    icon=JDXi.UI.Icon.MUSIC,
                    tooltip="Load pattern from file",
                    slot=self._load_pattern_dialog,
                ),
                "save": ButtonSpec(
                    label="Save",
                    icon=JDXi.UI.Icon.SAVE,
                    tooltip="Save pattern to file",
                    slot=self._save_pattern_dialog,
                ),
                "clear_learn": ButtonSpec(
                    label="Clear",
                    icon=JDXi.UI.Icon.CLEAR,
                    tooltip="Clear learned pattern",
                    slot=self._clear_learned_pattern,
                ),
                "add_measure": ButtonSpec(
                    label="Add Measure",
                    icon=JDXi.UI.Icon.ADD,
                    tooltip="Add a new Measure",
                    slot=self._add_measure,
                ),
                "copy": ButtonSpec(
                    label="Copy Section",
                    icon=JDXi.UI.Icon.FILE_DOCUMENT,
                    tooltip="Copy selected steps from current bar",
                    slot=self._copy_section,
                ),
                "paste": ButtonSpec(
                    label="Paste Section",
                    icon=JDXi.UI.Icon.ADD,
                    tooltip="Paste copied steps to current bar",
                    slot=self._paste_section,
                ),
                "learn": ButtonSpec(
                    label="Start",
                    icon=JDXi.UI.Icon.PLAY,
                    tooltip="Start learning pattern",
                    slot=self.on_learn_pattern_button_clicked,
                ),
                "stop_learn": ButtonSpec(
                    label="Stop",
                    icon=JDXi.UI.Icon.STOP,
                    tooltip="Stop learning pattern",
                    slot=self.on_stop_learn_pattern_button_clicked,
                ),
                "tap_tempo": ButtonSpec(
                    label="Tap",
                    icon=JDXi.UI.Icon.DRUM,
                    tooltip="Tap to set tempo",
                    slot=self._on_tap_tempo,
                ),
            },
            "combos": {
                "drum": ComboBoxSpec(
                    items=list(self.drum_options),
                    tooltip="",
                    slot=None,
                ),
                "beats_per_bar": ComboBoxSpec(
                    items=["16 beats per bar", "12 beats per bar"],
                    tooltip="",
                    slot=None,
                ),
                "duration": ComboBoxSpec(
                    items=[
                        "16th (1 step)",
                        "8th (2 steps)",
                        "Dotted 8th (3 steps)",
                        "Quarter (4 steps)",
                        "Dotted Quarter (6 steps)",
                        "Half (8 steps)",
                        "Dotted Half (12 steps)",
                        "Whole (16 steps)",
                    ],
                    tooltip="Default note duration for new notes",
                    slot=None,
                ),
                "digital1": ComboBoxSpec(
                    items=list(self.digital_options),
                    tooltip="",
                    slot=None,
                ),
                "digital2": ComboBoxSpec(
                    items=list(self.digital_options),
                    tooltip="",
                    slot=None,
                ),
                "analog": ComboBoxSpec(
                    items=list(self.analog_options),
                    tooltip="",
                    slot=None,
                ),
            },
            "spinboxes": self._create_spinbox_specs(),
            "transport": [
                TransportSpec(
                    name="play",
                    icon=JDXi.UI.Icon.PLAY,
                    text="Play",
                    slot=self._pattern_transport_play,
                    grouped=True,
                ),
                TransportSpec(
                    name="stop",
                    icon=JDXi.UI.Icon.STOP,
                    text="Stop",
                    slot=self._pattern_transport_stop,
                    grouped=True,
                ),
                TransportSpec(
                    name="pause",
                    icon=JDXi.UI.Icon.PAUSE,
                    text="Pause",
                    slot=self._pattern_transport_pause_toggle,
                    grouped=False,
                ),
                TransportSpec(
                    name="shuffle",
                    icon=JDXi.UI.Icon.SHUFFLE,
                    text="Shuffle Play",
                    slot=self._pattern_shuffle_play,
                    grouped=True,
                ),
            ],
        }
