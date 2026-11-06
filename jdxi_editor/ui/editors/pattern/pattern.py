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
import random
from typing import Any, Callable, Optional

from decologr import Decologr as log
from mido import Message, MetaMessage, MidiFile, MidiTrack, bpm2tempo
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QGroupBox,
    QHBoxLayout,
    QListWidgetItem,
    QMenu,
    QMessageBox,
    QPushButton,
    QWidget,
)

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.conversion.note import MidiNoteConverter
from jdxi_editor.midi.file.controller import (
    MidiFileController,
    MidiFileControllerConfig,
)
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.pattern.compiler import (
    PatternNote,
    PatternRow,
    PatternSpec,
    compile_pattern,
)
from jdxi_editor.midi.pattern.importer import PatternImport, import_pattern
from jdxi_editor.midi.playback.state import MidiPlaybackState
from jdxi_editor.midi.playback.transport import TransportController
from jdxi_editor.ui.editors.helpers.widgets import (
    create_jdxi_button,
    create_jdxi_button_from_spec,
    create_jdxi_button_with_label_from_spec,
    create_jdxi_row,
)
from jdxi_editor.ui.editors.pattern.helper import (
    get_button_note_spec,
    reset_button,
    reset_measure,
    set_sequencer_style,
    sync_button_note_spec,
    update_button_state,
)
from jdxi_editor.ui.editors.pattern.learner import (
    PatternLearner,
    PatternLearnerConfig,
    PatternLearnerEvent,
)
from jdxi_editor.ui.editors.pattern.sequencer.row import SequencerRow
from jdxi_editor.ui.editors.pattern.step_note import (
    ChordNote,
    StepNoteEvent,
    ms_per_step,
)
from jdxi_editor.ui.editors.pattern.timing.config import TimingConfig
from jdxi_editor.ui.editors.pattern.ui import PatternUI
from jdxi_editor.ui.preset.helper import JDXiPresetHelper
from jdxi_editor.ui.sequencer.button.manager import (
    NoteButtonAttrs,
    SequencerButtonManager,
)
from jdxi_editor.ui.style.factory import generate_sequencer_button_style
from jdxi_editor.ui.widgets.combo_box.synchronizer import (
    ComboBoxSynchronizer,
    ComboBoxUpdateConfig,
)
from jdxi_editor.ui.widgets.pattern.measure_widget import PatternMeasureWidget
from jdxi_editor.ui.widgets.pattern.sequencer_button import SequencerButton
from jdxi_editor.ui.widgets.usb.recording import USBFileRecordingWidget
from picomidi import MidiTempo
from picomidi.core.tempo import (
    MeasureBeats,
    convert_absolute_time_to_delta_time,
    milliseconds_per_note,
    ms_to_ticks,
)
from picomidi.message.type import MidoMessageType, MidoMetaMessageType
from picomidi.messages.note import MidiNote
from picomidi.playback.engine import (
    PlaybackEngine,
    TransportState,
)
from picomidi.ui.widget.transport.spec import TransportSpec
from picoui.helpers import group_with_layout
from picoui.specs.widgets import (
    ButtonSpec,
    FileSelectionSpec,
)
from picoui.widget.helper import get_file_path_from_spec
from picoui.widget.setters import set_spinbox_value


def copy_note_attrs_from_event(button: SequencerButton, event: PatternLearnerEvent):
    """copy note attributes"""
    button.note = event.note
    button.note_velocity = event.velocity
    button.note_duration = event.duration_ms


def update_button_from_learned_event(
    button: SequencerButton, event: PatternLearnerEvent
):
    """update button from learned event"""
    update_button_state(button, checked_state=True)
    copy_note_attrs_from_event(button, event)
    sync_button_note_spec(button)


def copy_note_attrs(prev: SequencerButton, new: SequencerButton):
    """copy note attrs"""
    new.note = prev.note
    for a in NoteButtonAttrs.COPYABLE:
        setattr(new, a, getattr(prev, a, None))


def get_channel_for_row(row: int) -> int:
    """Get idi channel for each row"""
    channel = row if row < 3 else 9
    return channel


class PatternSequenceEditor(PatternUI):
    """Pattern Sequencer with MIDI Integration using mido"""

    def __init__(
        self,
        midi_helper: Optional[MidiIOHelper],
        preset_helper: Optional[JDXiPresetHelper],
        parent: Optional[QWidget] = None,
        midi_file_editor: Optional[Any] = None,
    ):
        super().__init__(
            parent=parent,
            midi_helper=midi_helper,
            preset_helper=preset_helper,
            midi_file_editor=midi_file_editor,
        )
        # Use Qt translations: add .ts/.qm for locale (e.g. en_GB "Measure" -> "Bar", "Measures" -> "Bars")

        self.ppq: int = 480
        StepNoteEvent.tempo_bpm = self.timing_bpm  # Step lengths follow the pattern tempo
        self.last_import: Optional[PatternImport] = None
        self._state: TransportState | None = None
        self.timing = TimingConfig()
        self.beats_per_pattern: int = 4  # Number of beats per pattern
        self.last_tap_time: Optional[datetime] = None  # Last tap time
        self.tap_times: list[float] = []  # List of tap times
        # Learned pattern (row -> step -> midi_note)
        self.learned_pattern: list[list[Optional[int]]] = [
            [None] * self.total_steps for _ in range(self.sequencer_rows)
        ]
        self.active_notes: dict[int, int] = (
            {}
        )  # Track active notes (midi_note -> row index)
        self._pattern_paused: bool = False
        self._pattern_loop_enabled: bool = True  # Loop by default; toggle via future UI
        self._pattern_file_path: Optional[str] = (
            None  # Last saved/loaded path for USB auto-filename
        )
        # Same transport as the MIDI File Player: scheduler thread, loop, mutes, clock
        self.transport_controller = TransportController(
            send=self._send_playback_message, parent=self
        )
        self.playback_engine: PlaybackEngine = self.transport_controller.engine
        self.transport_controller.state_changed.connect(self._on_transport_state_changed)
        self.transport_controller.position_changed.connect(
            self._on_transport_position_changed
        )
        # Edits while playing are coalesced into one recompile per event-loop pass
        self._recompile_timer = QTimer(self)
        self._recompile_timer.setSingleShot(True)
        self._recompile_timer.setInterval(0)
        self._recompile_timer.timeout.connect(self._recompile_if_loaded)
        self._wire_pattern_widget()
        self._init_style()
        self._init_playing_controllers()
        self._connect_midi_signals()
        self.clear_pattern()
        # --- Load file
        self._load_from_midi_file_editor_if_available()
        # If MidiFileEditor is provided and has a loaded file, load it
        if self.midi_file_editor and hasattr(self.midi_file_editor, "midi_state"):
            if self.midi_file_editor.midi_state.file:
                self.load_from_midi_file_editor()

    def _wire_pattern_widget(self) -> None:
        """Wire PatternWidget callbacks for measure selection and button clicks."""
        if self.pattern_widget:
            self.pattern_widget.on_measure_selected = self._on_pattern_measure_selected
            self.pattern_widget.set_button_click_handler(self._on_button_clicked)
            self.pattern_widget.set_button_context_handler(self._on_step_context_menu)

    def _on_pattern_measure_selected(self, measure_index: int) -> None:
        """Called when user selects a measure in PatternWidget."""
        self._button_manager.set_buttons(self.buttons)
        step_in_measure = self.current_step % self.measure_beats
        self._on_playback_step_changed(step_in_measure)

    def _init_style(self):
        """init style"""
        JDXi.UI.Theme.apply_editor_style(self)

    def _load_from_midi_file_editor_if_available(self) -> None:
        """Load from MidiFileEditor if it has a file."""
        self.clear_pattern()
        if self.midi_file_editor and hasattr(self.midi_file_editor, "midi_state"):
            if self.midi_file_editor.midi_state.file:
                self.load_from_midi_file_editor()

    def _on_learner_note_learned(self, event: PatternLearnerEvent) -> None:
        """Update measure/sequencer from learned note; append NOTE_ON/OFF."""

        step_in_measure = event.step
        row = event.row

        for btn in self._get_step_buttons(row, step_in_measure):
            update_button_from_learned_event(btn, event)

        duration_ticks = ms_to_ticks(event.duration_ms, self.bpm, self.ppq)

        self._add_note_on_off_pair(duration_ticks, event)

    def _add_note_on_off_pair(self, duration_ticks: int, event: PatternLearnerEvent):
        """add note on off pair to track"""
        midi_note = MidiNote(
            note=event.note, velocity=event.velocity, duration_ms=duration_ticks
        )
        on_msg, off_msg = midi_note.to_on_off_pair()
        self.midi_track.extend([on_msg, off_msg])

    def _on_learner_step_advance(self, step: int) -> None:
        """Keep editor current_step in sync with the learner."""
        self.current_step = step

    def _on_learner_stopped(self) -> None:
        """When learner stops: disconnect learn handler, reconnect combo updates."""
        self.midi_helper.midi_message_incoming.disconnect(self._learn_pattern)
        self._reconnect_combo_synchronizer()
        self._sync_midi_track_from_learner()

    def on_stop_learn_pattern_button_clicked(self):
        """Disconnect MIDI from learn pattern and stop the learner."""
        self.midi_helper.midi_message_incoming.disconnect(self._learn_pattern)
        self._pattern_learner.stop_learning()
        self._reconnect_combo_synchronizer()
        self._sync_midi_track_from_learner()

    def _reconnect_combo_synchronizer(self) -> None:
        """Reconnect MIDI incoming to combo synchronizer."""
        if self._combo_synchronizer:
            self.midi_helper.midi_message_incoming.connect(
                self._combo_synchronizer.process_incoming_midi
            )

    def _sync_midi_track_from_learner(self) -> None:
        """Copy learned MIDI messages into the editor's midi_track for saving."""
        self.midi_track.clear()
        self.midi_track.extend(self._pattern_learner.get_midi_track())

    def _init_playing_controllers(self) -> None:
        """Create MIDI/learn controllers and wire to UI (Pattern Playing)."""
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

        self._init_pattern_learner()

        self._init_midi_file_controller()
        self._init_button_manager()

    def _init_button_manager(self) -> None:
        """Create and configure SequencerButtonManager for playback/MIDI."""
        self._button_manager = SequencerButtonManager(
            midi_converter=self._note_converter,
            scope=self.__class__.__name__,
        )
        self._button_manager.set_buttons(self.buttons)
        self._button_manager.set_channel_map(self.row_map)
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

    def _init_midi_file_controller(self):
        """init midi file controller"""
        midi_controller_config = MidiFileControllerConfig(
            ticks_per_beat=self.ppq,
            beats_per_measure=4,
            default_bpm=self.timing.bpm,
            default_velocity=100,
        )
        self._midi_file_controller = MidiFileController(
            config=midi_controller_config,
            midi_converter=self._note_converter,
            scope=self.__class__.__name__,
        )
        self._midi_file_controller.create_new_file()
        self._sync_from_midi_file_controller()

    def _init_pattern_learner(self):
        """init pattern learner"""
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

    def _refresh_preset_options(self) -> None:
        """Override to also update note converter and combo synchronizer."""
        super()._refresh_preset_options()
        if hasattr(self, "_note_converter"):
            self._note_converter.update_drum_options(list(self.drum_options))
        if hasattr(self, "_combo_synchronizer"):
            self._combo_synchronizer.set_selector_options(0, list(self.digital_options))
            self._combo_synchronizer.set_selector_options(1, list(self.digital_options))
            self._combo_synchronizer.set_selector_options(2, list(self.analog_options))
            self._combo_synchronizer.set_selector_options(3, list(self.drum_options))

    def update_transport_buttons(self, state: TransportState) -> None:
        """Update play, pause and stop buttons."""

        config = {
            TransportState.STOPPED: {
                self.play_button: {"checked_state": False, "enabled_state": True},
                self.pause_button: {"checked_state": False, "enabled_state": False},
                self.stop_button: {"checked_state": True, "enabled_state": False},
            },
            TransportState.PLAYING: {
                self.play_button: {"checked_state": True, "enabled_state": False},
                self.pause_button: {"checked_state": False, "enabled_state": True},
                self.stop_button: {"checked_state": False, "enabled_state": True},
            },
            TransportState.PAUSED: {
                self.play_button: {"checked_state": False, "enabled_state": True},
                self.pause_button: {"checked_state": True, "enabled_state": True},
                self.stop_button: {"checked_state": False, "enabled_state": True},
            },
        }

        for button, kwargs in config[state].items():
            if button is not None:
                update_button_state(button, **kwargs)

    def _apply_transport_state(self, state: TransportState) -> None:
        """Apply transport state to the UI."""
        self.update_transport_buttons(state)

        if state == TransportState.STOPPED:
            self.current_step = 0
            self._pattern_paused = False

        if state == TransportState.PAUSED:
            self._pattern_paused = True

    def _log_traceback(self) -> None:
        """Log current exception traceback at debug level."""
        import traceback

        log.debug(traceback.format_exc())

    def _on_playback_measure_changed(self, measure_index: int) -> None:
        """Sync sequencer and measure list to the current measure during playback."""
        if self.pattern_widget and self.pattern_widget.select_measure(measure_index):
            self._button_manager.set_buttons(self.buttons)
        self._scroll_measures_list_to(measure_index)

    def _scroll_measures_list_to(self, measure_index: int) -> None:
        """Select and scroll measures list to the given index."""
        if self.measures_list and measure_index < self.measures_list.count():
            self.measures_list.setCurrentRow(measure_index)
            item = self.measures_list.item(measure_index)
            if item:
                self.measures_list.scrollToItem(item)

    def _on_playback_step_changed(self, step_in_measure: int) -> None:
        """Update step highlight during playback."""
        last_step = getattr(self, "_playback_last_step_in_measure", -1)
        for row in range(self.sequencer_rows):
            for btn in self._get_step_buttons(row, last_step) if 0 <= last_step else []:
                set_sequencer_style(btn=btn, is_current=False, checked=btn.isChecked())
            for btn in self._get_step_buttons(row, step_in_measure):
                set_sequencer_style(btn=btn, is_current=True, checked=btn.isChecked())
        self._playback_last_step_in_measure = step_in_measure

    def _initialize_default_measure(self):
        """Initialize with one default measure"""
        self._add_measure()

    def _sync_from_midi_file_controller(self) -> None:
        """Sync midi_file, midi_track, bpm from the MIDI file controller."""
        self.midi_file = self._midi_file_controller.midi_file
        self.midi_track = self._midi_file_controller.midi_file.tracks[0]
        self.timing_bpm = self._midi_file_controller.get_tempo()

    def _add_measure(self):
        """Add measure, optionally copying from the previous one."""
        if not self.pattern_widget:
            return
        copy_previous = self.copy_previous_measure_checkbox.isChecked()
        self.pattern_widget.add_measure(copy_previous=copy_previous)
        self.total_measures = self.pattern_widget.get_measure_count()
        self._sync_pattern_length()
        self._button_manager.set_buttons(self.buttons)
        self.schedule_recompile()
        log.message(
            message=f"Added measure. Total: {self.total_measures}",
            scope=self.__class__.__name__,
        )

    def _sync_pattern_length(self):
        """Update total measures (but keep total_steps at 16)"""
        self.total_measures = len(self.measure_widgets)
        self._update_pattern_length()

    def _connect_midi_signals(self):
        combo = getattr(self, "_combo_synchronizer", None)
        if combo:
            self._reconnect_combo_synchronizer()
            self.midi_helper.midi_message_outgoing.connect(combo.process_outgoing_midi)

    def _init_model_structures(self):
        self.mute_buttons = []
        self.specs = self._build_specs()

    def reset_all_measures(self):
        """reset all measures"""
        for measure in self.measure_widgets:
            reset_measure(measure)
        self.schedule_recompile()

    def add_and_reset_new_measure(self):
        """add and reset new measure"""
        measure = PatternMeasureWidget()
        reset_measure(measure)
        self.measure_widgets.append(measure)
        return measure

    def on_learn_pattern_button_clicked(self):
        """Connect MIDI to learn pattern and start the learner."""
        if self._combo_synchronizer:
            self.midi_helper.midi_message_incoming.disconnect(
                self._combo_synchronizer.process_incoming_midi
            )
        self.midi_helper.midi_message_incoming.connect(self._learn_pattern)
        self._pattern_learner.start_learning()
        self.current_step = self._pattern_learner.current_step

    def _midi_note_to_combo_index(self, row, midi_note):
        """Convert a MIDI note number to the corresponding combo box index."""
        note_list = {
            0: self.digital_options,
            1: self.digital_options,
            2: self.analog_options,
            3: self.drum_options,
        }
        note_list = note_list.get(row)
        if note_list is not None:
            note_name = self._midi_to_note_name(midi_note)
            return note_list.index(note_name)
        return None

    def _set_combo_box_index(self, row, index):
        """Set the combo box index for the specified row."""
        self.row_map = self._build_row_map()
        selector = self.row_map.get(row)
        if selector is not None:
            selector.setCurrentIndex(index)

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
        if self.current_measure_index >= len(self.measure_widgets):
            QMessageBox.warning(self, "Copy", "No bar selected")
            return

        start_step = self.start_step_spinbox.value()
        end_step = self.end_step_spinbox.value()

        if start_step > end_step:
            QMessageBox.warning(self, "Copy", "Start step must be <= end step")
            return

        self.clipboard = self.pattern_widget.copy_measure_section(
            self.current_measure_index, start_step, end_step
        )
        if self.paste_button:
            self.paste_button.setEnabled(True)
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

        if self.current_measure_index >= len(self.measure_widgets):
            QMessageBox.warning(self, "Paste", "No bar selected")
            return

        start_step = self.start_step_spinbox.value()
        ok = self.pattern_widget.paste_measure_section(
            self.current_measure_index, start_step, self.clipboard
        )
        if not ok:
            QMessageBox.warning(self, "Paste", "Invalid clipboard data")
            return

        num_steps = self.clipboard["end_step"] - self.clipboard["start_step"] + 1
        log.message(
            message=f"Pasted {num_steps} steps to bar {self.current_measure_index + 1} starting at step {start_step}",
            scope=self.__class__.__name__,
        )
        self.schedule_recompile()

    def _sync_sequencer_with_measure(self, bar_index: int):
        """Sync visible sequencer with measure data. No-op when using PatternWidget (display is direct)."""
        if self.pattern_widget:
            return
        if bar_index < 0 or bar_index >= len(self.measure_widgets):
            return

        measure = self.measure_widgets[bar_index]
        self._for_each_button(lambda r, s: self._sync_measure(measure, r, s))

    def _sync_measure(self, measure: PatternMeasureWidget, row: int, step: int):
        if step < len(self.buttons[row]) and step < len(measure.buttons[row]):
            sequencer_button = self.buttons[row][step]
            measure_button: SequencerButton = measure.buttons[row][step]

            # Sync checked state and note
            update_button_state(sequencer_button, measure_button.isChecked())
            copy_note_attrs(new=sequencer_button, prev=measure_button)
            sync_button_note_spec(sequencer_button)

            self._update_tooltip(row, sequencer_button)
            self._update_sequencer_button_style(sequencer_button, step)

    def _update_tooltip(self, row: int, sequencer_button):
        """Tooltip lists every note on the step; the button shows the count for chords."""
        spec = get_button_note_spec(sequencer_button)
        notes = self._step_notes(spec) if spec.is_active else []
        if notes:
            names = ", ".join(self._note_label(row, n.note) for n in notes)
            label = "Notes" if len(notes) > 1 else "Note"
            sequencer_button.setToolTip(
                f"{label}: {names}\nShift+click: add/remove the selected note · "
                "Right-click: edit notes"
            )
        else:
            sequencer_button.setToolTip("")
        if hasattr(sequencer_button, "refresh_note_count"):
            sequencer_button.refresh_note_count()

    @staticmethod
    def _step_notes(spec) -> list[ChordNote]:
        """All notes on a step (main note first), for any note spec type."""
        if isinstance(spec, StepNoteEvent):
            return spec.notes()
        if not spec.is_active:
            return []
        steps = (spec.duration_ms or 0) / ms_per_step(StepNoteEvent.tempo_bpm) or 1
        return [ChordNote(spec.note, spec.velocity, steps)]

    def _note_label(self, row: int, note: int) -> str:
        return self._midi_to_note_name(note, drums=row == SequencerRow.DRUMS)

    def _selected_note_for_row(self, row: int) -> Optional[int]:
        """MIDI note currently chosen in the row's note selector."""
        selector = self.row_map.get(row)
        if selector is None:
            return None
        return self._note_name_to_midi(selector.currentText())

    def _step_menu_actions(self, button) -> list[tuple[str, str, Optional[int]]]:
        """(label, action, note) entries for a step's right-click menu."""
        actions: list[tuple[str, str, Optional[int]]] = []
        spec = get_button_note_spec(button)
        selected = self._selected_note_for_row(button.row)
        if selected is not None and not (
            spec.is_active and isinstance(spec, StepNoteEvent) and spec.has_note(selected)
        ):
            actions.append((f"Add {self._note_label(button.row, selected)}", "add", selected))
        for chord_note in self._step_notes(spec) if spec.is_active else []:
            actions.append(
                (
                    f"Remove {self._note_label(button.row, chord_note.note)} "
                    f"(vel {chord_note.velocity})",
                    "remove",
                    chord_note.note,
                )
            )
        if spec.is_active:
            actions.append(("Clear step", "clear", None))
        return actions

    def _on_step_context_menu(self, button, global_pos) -> None:
        """Right-click on a step: add the selected note, remove notes, or clear."""
        if not button.isEnabled():
            return
        menu = QMenu(self)
        chosen = {}
        for label, action, note in self._step_menu_actions(button):
            if action == "clear":
                menu.addSeparator()
            chosen[menu.addAction(label)] = (action, note)
        picked = menu.exec(global_pos)
        if picked in chosen:
            self._apply_step_action(button, *chosen[picked])

    def _apply_step_action(self, button, action: str, note: Optional[int]) -> None:
        """Add or remove one note on a step, or clear it."""
        if not isinstance(button.note_spec, StepNoteEvent):
            sync_button_note_spec(button)
        spec = button.note_spec
        if action == "add" and note is not None:
            spec.add_note(note, self.velocity_spinbox.value(), self._get_duration_steps())
        elif action == "remove" and note is not None:
            spec.remove_note(note)
        elif action == "clear":
            spec.note = None
            spec.extra_notes = []

        if spec.is_active:
            update_button_state(button, True)
        else:
            reset_button(button)
        self._update_tooltip(button.row, button)
        if self.pattern_widget and self.current_measure_index < len(self.measure_widgets):
            self.pattern_widget.sync_measure_to_ui(self.current_measure_index)
        self._update_button_style(button, button.isChecked())
        self.schedule_recompile()

    def _highlight_bar(self, bar_index: int):
        """Update button styles to highlight the current step in the selected bar"""
        if bar_index < 0 or bar_index >= len(self.measure_widgets):
            return

        if self.pattern_widget:
            current_step_in_bar = self.current_step % self.total_steps
            self.pattern_widget.for_each_button(
                lambda r, s, btn: self.pattern_widget.highlight_step(
                    r, s, btn.isChecked(), current_step_in_bar == s
                )
            )
        else:
            self._for_each_button(self._highlight_step)

    def _highlight_step(self, row: int, step: int):
        """Legacy: used when pattern_widget is None."""
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
        self.learned_pattern = [
            [None] * self.total_steps for _ in range(self.sequencer_rows)
        ]

        self._clear_sequencer()

        log.message(message="Cleared learned pattern.", scope=self.__class__.__name__)

    def _clear_sequencer(self):
        if self.pattern_widget:
            self.pattern_widget.clear_buttons(reset_button, set_sequencer_style)
        else:
            for row in range(self.sequencer_rows):
                for button in self.buttons[row]:
                    reset_button(button)
                    set_sequencer_style(button)

    def clear_pattern(self):
        """Clear the learned pattern and reset button states."""
        self._pattern_file_path = None
        self._init_midi_file()
        if self.pattern_widget:
            self.pattern_widget.clear_and_reset(1)
            self._button_manager.set_buttons(self.buttons)
        log.message(message="Cleared pattern.", scope=self.__class__.__name__)
        self.schedule_recompile()

    def _on_measure_count_changed(self, count: int):
        """Handle measure count changes"""
        if self.pattern_widget:
            self.pattern_widget.ensure_measure_count(count)
        self.total_measures = count
        self._update_pattern_length()
        self.schedule_recompile()

    def _update_pattern_length(self):
        """Update total pattern length based on measure count"""
        # Keep total_steps at 16 (one bar) - sequencer always shows one bar at a time
        # Playback will iterate through all bars
        self.total_steps = MeasureBeats.PER_MEASURE_4_4

    def _on_button_clicked(self, button, checked):
        """Handle button clicks and store the selected note"""
        # Don't allow checking disabled buttons
        if not button.isEnabled():
            return

        shift = bool(
            QApplication.keyboardModifiers() & Qt.KeyboardModifier.ShiftModifier
        )
        if shift and not checked and get_button_note_spec(button).is_active:
            # Shift+click on a used step adds/removes the row's selected note
            # (chords, extra drum hits) instead of clearing the step
            update_button_state(button, True)
            note = self._selected_note_for_row(button.row)
            if note is not None:
                action = "remove" if button.note_spec.has_note(note) else "add"
                self._apply_step_action(button, action, note)
            return

        if checked:
            # Store the currently selected note when button is activated
            selector = self.row_map.get(button.row)
            if selector is not None:
                note_name = selector.currentText()
                midi_note = self._note_name_to_midi(note_name)
                button.note = midi_note
            # A step entered by hand takes the current Velocity and Duration
            button.velocity = self.velocity_spinbox.value()
            button.note_steps = self._get_duration_steps()
            sync_button_note_spec(button)
            self._update_tooltip(button.row, button)

        self.schedule_recompile()

        # Store the note in the currently selected bar's measure
        if len(self.measure_widgets) > 0 and self.current_measure_index < len(
            self.measure_widgets
        ):
            self._store_note_in_measures(button, checked)
            # Sync UI to PatternMeasure for data consistency (Phase 2)
            if self.pattern_widget:
                self.pattern_widget.sync_measure_to_ui(self.current_measure_index)

        self._update_button_style(button, checked)

    def _store_note_in_measures(self, button: SequencerButton, checked: bool):
        """sore notes in measures"""
        step_in_bar = button.column  # button.column is 0-15 for sequencer buttons
        step_buttons = self._get_step_buttons(button.row, step_in_bar)

        if step_buttons:
            measure_button = step_buttons[0]
            update_button_state(measure_button, checked)
            if checked:
                measure_button.note = button.note
                # Copy duration if available
                if button.note_steps is not None:
                    measure_button.note_steps = button.note_steps
                # Copy velocity if available
                if hasattr(button, NoteButtonAttrs.NOTE_VELOCITY):
                    measure_button.velocity = button.note_velocity
                sync_button_note_spec(measure_button)
            else:
                reset_button(measure_button)

    def _update_button_style(self, button: SequencerButton, checked: bool):
        """Update button style"""
        is_current = (self.current_step % self.total_steps) == button.column
        is_selected_bar = (
            len(self.measure_widgets) > 0
            and (button.column // self.measure_beats) == self.current_measure_index
        )
        button.setStyleSheet(
            JDXi.UI.Style.generate_sequencer_button_style(
                checked, is_current, is_selected_bar=is_selected_bar and checked
            )
        )

    def _update_sequencer_button_style(self, sequencer_button, step: int):
        """Update style"""
        is_current = (self.current_step % self.total_steps) == step
        set_sequencer_style(
            sequencer_button, checked=sequencer_button.isChecked, is_current=is_current
        )
        sequencer_button.setStyleSheet(
            JDXi.UI.Style.generate_sequencer_button_style(
                sequencer_button.isChecked(),
                is_current,
                is_selected_bar=True,  # All displayed buttons are from selected bar
            )
        )

    def _on_beats_per_bar_changed(self, index: int):
        """Handle beats per bar changes from the combobox"""
        if index == 0:
            self.measure_beats = MeasureBeats.PER_MEASURE_4_4
        else:
            self.measure_beats = MeasureBeats.PER_MEASURE_3_4

        # Update button states based on beats per bar
        self._update_button_states_for_beats_per_bar()
        self.schedule_recompile()
        log.message(f"Beats per bar changed to {self.measure_beats}")

    def _update_button_states_for_beats_per_bar(self) -> None:
        """Enable/disable sequencer buttons based on beats per bar setting."""

        active_steps = (
            MeasureBeats.PER_MEASURE_3_4
            if self.measure_beats == MeasureBeats.PER_MEASURE_3_4
            else MeasureBeats.PER_MEASURE_4_4
        )

        def update_state(r, s):
            if s < len(self.buttons[r]):
                self._update_button_state(active_steps, r, s)

        self._for_each_button(update_state)

    def _for_each_button(self, func):
        """Apply func(row, step) to each sequencer position."""
        if self.pattern_widget:
            self.pattern_widget.for_each_button(lambda r, s, _b: func(r, s))
        else:
            for row in range(self.sequencer_rows):
                self._each_measure_beat_row(func, row)

    def _each_measure_beat_row(self, func, row: int):
        for step in range(self.measure_beats):
            func(row, step)

    def _update_button_state(self, active_steps: int, row: int, step: int):
        button = self.buttons[row][step]

        is_active = step < active_steps

        button.setEnabled(is_active)

        if not is_active:
            button.setChecked(False)

            for measure in self.measure_widgets:
                if step < len(measure.buttons[row]):
                    reset_button(measure.buttons[row][step])

    def _on_beats_per_measure_changed(self, index: int):
        """Handle beats per measure changes from the combobox"""
        if index == 0:
            self._update_measure_beats(MeasureBeats.PER_MEASURE_4_4)
        else:
            self._update_measure_beats(MeasureBeats.PER_MEASURE_3_4)

        # Update button states based on beats per measure
        self._update_button_states_for_beats_per_measure()
        self.schedule_recompile()
        log.message(f"Beats per measure changed to {self.measure_beats}")

    def _update_measure_beats(self, beats: int):
        self.measure_beats = beats

    def _update_button_states_for_beats_per_measure(self):
        """Enable/disable sequencer buttons based on beats per measure setting"""
        # Steps 12-15 disabled when beats_per_measure is 12
        for row in range(self.sequencer_rows):
            func = self._update_button_states_measure
            self._each_measure_beat_row(func=func, row=row)

        # Sync sequencer digital after updating button states
        if self.current_measure_index < len(self.measure_widgets):
            self._sync_sequencer_with_measure(self.current_measure_index)

    def _update_button_states_measure(self, row: int, step: int):
        """update button states measure"""
        if step < len(self.buttons[row]):
            button = self.buttons[row][step]
            if self.measure_beats == MeasureBeats.PER_MEASURE_3_4:
                # Disable last 4 buttons (steps 12-15)
                button.setEnabled(step < MeasureBeats.PER_MEASURE_3_4)
                if step >= MeasureBeats.PER_MEASURE_3_4:
                    button.setEnabled(False)
                    button.setChecked(False)  # Uncheck disabled buttons
                    for measure in self.measure_widgets:
                        if step < len(measure.buttons[row]):
                            reset_button(measure.buttons[row][step])
            else:
                # Enable all 16 buttons
                update_button_state(button, button.isChecked())

    def _get_step_buttons(self, row: int, step: int):
        """get step buttons"""
        buttons = []

        if self.current_measure_index < len(self.measure_widgets):
            measure = self.measure_widgets[self.current_measure_index]
            if step < len(measure.buttons[row]):
                buttons.append(measure.buttons[row][step])

        if step < len(self.buttons[row]):
            buttons.append(self.buttons[row][step])

        return buttons

    def _get_duration_steps(self) -> int:
        """Length in steps chosen in the Duration combo (16th = 1 step)."""
        # 16th=1, 8th=2, dotted 8th=3, quarter=4, dotted quarter=6, half=8, dotted half=12, whole=16
        duration_multipliers = [1, 2, 3, 4, 6, 8, 12, 16]
        index = self.duration_combo.currentIndex()
        return duration_multipliers[index] if 0 <= index < len(duration_multipliers) else 1

    def _get_duration_ms(self) -> float:
        """Duration combo length in milliseconds at the current tempo."""
        return self._get_duration_steps() * ms_per_step(self.timing_bpm)

    def _calculate_step_duration(self) -> float:
        """calculate step duration"""
        return float(milliseconds_per_note(self.timing_bpm))

    def _on_duration_changed(self, index: int):
        """Handle duration changes from the combo box"""
        # Duration change doesn't affect existing notes, only new ones
        # This is just a placeholder for potential future functionality
        pass

    def _on_tempo_changed(self, bpm: int):
        """Handle tempo changes from the spinbox"""
        self.set_tempo(bpm)

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
            bpm = int(MidiTempo.SECONDS_PER_MINUTE / avg_interval)
            # Constrain to valid range
            bpm = max(20, min(300, bpm))
            self.tempo_spinbox.setValue(bpm)

    def save_pattern_dialog(self):
        """Open save file dialog and save pattern.
        When a file was previously loaded (from MidiFileEditor or Load), the dialog
        opens with that path pre-filled so the user can save back to the same file.
        """
        spec = FileSelectionSpec(
            mode="save",
            caption="Save Pattern",
            default_name="",
            filter="MIDI Files (*.mid);;All Files (*.*)",
        )
        start_path = self._pattern_file_path or ""
        filename = get_file_path_from_spec(self, spec, start_dir=start_path)

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

    def load_pattern_dialog(self):
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
                if self.last_import and self.last_import.dropped_total:
                    QMessageBox.information(
                        self, "Pattern Loaded", self.last_import.summary()
                    )
            except Exception as ex:
                log.error(
                    message=f"Error loading pattern: {ex}",
                    scope=self.__class__.__name__,
                )
                QMessageBox.critical(
                    self, "Error", f"Could not load pattern: {str(ex)}"
                )

    def set_tempo(self, bpm: int):
        """Set the pattern tempo in BPM; a playing pattern follows on the same beat."""
        self.timing_bpm = bpm
        StepNoteEvent.tempo_bpm = bpm  # note lengths are steps; their ms follow
        microseconds_per_beat = int(MidiTempo.MICROSECONDS_PER_MINUTE / bpm)

        # Keep one tempo message at the start of the recording/learn file
        if self.midi_file.tracks:
            track = self.midi_file.tracks[0]
            for msg in track:
                if msg.type == MidoMessageType.SET_TEMPO.value and msg.time == 0:
                    msg.tempo = microseconds_per_beat
                    break
            else:
                track.insert(
                    0,
                    MetaMessage(
                        MidoMessageType.SET_TEMPO.value, tempo=microseconds_per_beat
                    ),
                )

        self.schedule_recompile()
        log.message(message=f"Tempo set to {bpm} BPM", scope=self.__class__.__name__)

    def _init_midi_file(self):
        """Initialize a new MIDI file with 4 tracks"""
        self.midi_file = MidiFile()
        for _ in range(self.sequencer_rows):
            track = MidiTrack()
            self.midi_file.tracks.append(track)

    def update_pattern(self):
        """update pattern"""
        self.midi_file = MidiFile()
        track = MidiTrack()
        self.midi_file.tracks.append(track)

        ppq = self.midi_file.ticks_per_beat
        beats_per_bar = 4
        ticks_per_bar = ppq * beats_per_bar
        ticks_per_step = ppq // 4  # 16th notes

        track.append(
            MetaMessage(MidoMetaMessageType.SET_TEMPO, tempo=bpm2tempo(self.timing_bpm))
        )
        track.append(
            MetaMessage(MidoMetaMessageType.TIME_SIGNATURE, numerator=4, denominator=4)
        )

        events = []

        for measure_index, measure in enumerate(self.measure_widgets):
            for step in range(self.measure_beats):
                self._add_event_to_pattern(
                    events, measure, measure_index, step, ticks_per_bar, ticks_per_step
                )

        # Sort events by absolute time
        events.sort(key=lambda e: e[0])

        convert_absolute_time_to_delta_time(events, track)

    def _add_event_to_pattern(
        self,
        events: list[Any],
        measure: PatternMeasureWidget,
        measure_index: int,
        step: int,
        ticks_per_bar: int,
        ticks_per_step: int,
    ):
        absolute_tick = measure_index * ticks_per_bar + step * ticks_per_step

        for row in range(self.sequencer_rows):
            channel = get_channel_for_row(row)
            button = measure.buttons[row][step]
            spec = get_button_note_spec(button)

            if button.isChecked() and spec.is_active and spec.midi_note is not None:
                on_msg, off_msg = spec.midi_note.to_on_off_pair()
                on_msg.channel = channel
                on_msg.time = 0
                off_msg.channel = channel
                off_msg.time = 0
                events.append((absolute_tick, on_msg))
                events.append((absolute_tick + ticks_per_step, off_msg))

    def set_midi_file_editor(self, midi_file_editor: Any) -> str | None:
        """
        Set reference to MidiFileEditor for shared MIDI file editing.

        :param midi_file_editor: MidiFileEditor instance
        """
        self.midi_file_editor = midi_file_editor
        # --- If MidiFileEditor already has a loaded file, load it
        if self.midi_file_editor and hasattr(self.midi_file_editor, "midi_state"):
            if self.midi_file_editor.midi_state.file:
                self.load_from_midi_file_editor()
                return self.midi_file_editor.midi_state.file.filename
            else:
                log.debug(
                    message="No MIDI file loaded in MidiFileEditor",
                    scope=self.__class__.__name__,
                )
                return None
        return None

    def load_from_midi_file_editor(
        self, midi_file_editor: Optional[Any] = None
    ) -> None:
        """
        Load pattern from the MidiFileEditor's current MIDI file.

        :param midi_file_editor: Optional MidiFileEditor instance. If not provided, uses self.midi_file_editor
        """
        try:
            # --- Use provided instance or fall back to stored reference
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
                self.set_midi_file_editor(editor)
                log.debug(
                    message="Stored MidiFileEditor reference in Pattern Sequencer",
                    scope=self.__class__.__name__,
                )

            midi_file = self.midi_file_editor.midi_state.file
            if not midi_file:
                log.debug(
                    message="No MIDI file loaded in MidiFileEditor",
                    scope=self.__class__.__name__,
                )
                return

            self._get_filename_from_available_locations(editor, midi_file)
        except Exception as ex:
            log.error(
                message=f"Error loading from MidiFileEditor: {ex}",
                scope=self.__class__.__name__,
            )
            import traceback

            log.debug(traceback.format_exc())

    def _get_filename_from_available_locations(self, editor: Any | None, midi_file):
        """Try to get filename from multiple possible locations"""
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
            # --- Load from the MidiFile object directly
            log.message(
                message="Loading pattern from MidiFileEditor's MidiFile object (no filename available)",
                scope=self.__class__.__name__,
            )
            self._load_from_midi_file_object(midi_file)

    def _load_from_midi_file_object(self, midi_file: MidiFile) -> None:
        """Load pattern from a MidiFile object (the MIDI File Player's file)."""
        try:
            self._apply_pattern_import(midi_file)
            # Set path for save-back when loaded from MidiFileEditor (Phase 4 T9)
            if hasattr(midi_file, "filename") and midi_file.filename:
                self._pattern_file_path = midi_file.filename
        except Exception as ex:
            log.error(
                message=f"Error loading from MidiFileEditor: {ex}",
                scope=self.__class__.__name__,
            )
            import traceback

            log.debug(traceback.format_exc())
        self.schedule_recompile()

    def _apply_pattern_import(self, midi_file: MidiFile) -> PatternImport:
        """
        Replace the pattern with the notes of *midi_file* (shared by Load Pattern
        and loading from the MIDI File Player).
        """
        steps_per_bar = min(self.measure_beats, MeasureBeats.PER_MEASURE_4_4)
        imported = import_pattern(midi_file, self.channel_to_row, steps_per_bar)
        self.last_import = imported

        # Tempo first, so lengths shown in ms are right as notes arrive
        if imported.bpm:
            bpm = int(round(imported.bpm))
            set_spinbox_value(self.tempo_spinbox, bpm)
            self.set_tempo(bpm)
        self.ppq = midi_file.ticks_per_beat

        self._clear_measures_and_measures_list()
        self._create_new_measures(imported.bars)
        self.total_measures = len(self.measure_widgets)
        self._update_pattern_length()

        for note in imported.notes:
            if note.bar >= len(self.measure_widgets):
                continue
            row_buttons = self.measure_widgets[note.bar].buttons[note.row]
            if note.step >= len(row_buttons):
                continue
            button = row_buttons[note.step]
            if button.isChecked() and get_button_note_spec(button).is_active:
                # Another note on the same step: part of a chord / extra hit
                button.note_spec.extra_notes.append(
                    ChordNote(note.note, note.velocity, note.duration_steps)
                )
                continue
            update_button_state(button, True)
            button.note = note.note
            button.note_velocity = note.velocity
            button.note_steps = note.duration_steps
            sync_button_note_spec(button)

        self._sync_loaded_buttons_to_measure_data()
        self._update_tooltips_for_loaded_notes()
        self._select_first_measure_and_sync(len(imported.notes))
        self._update_button_states_for_beats_per_measure()
        log.message(message=imported.summary(), scope=self.__class__.__name__)
        return imported

    def _create_new_measures(self, num_bars: int):
        """Create new bars"""
        if self.pattern_widget:
            self.pattern_widget.ensure_measure_count(num_bars)
            self.total_measures = self.pattern_widget.get_measure_count()

    def _sync_midi_state_from_loaded_file(self, midi_file: MidiFile) -> None:
        """Sync PPQ from loaded file for correct save/playback timing (Phase 3).
        Uses loaded file's ticks_per_beat; keeps midi_file/midi_track for learner compatibility.
        """
        self.ppq = midi_file.ticks_per_beat
        log.message(
            message=f"[Phase3] Synced PPQ from loaded file: {self.ppq} ticks/beat",
            scope=self.__class__.__name__,
        )

    def _sync_loaded_buttons_to_measure_data(self) -> None:
        """Sync button state to PatternMeasure.steps after load (Phase 2 data consistency)."""
        if not self.pattern_widget:
            return
        count = self.pattern_widget.get_measure_count()
        for i in range(count):
            self.pattern_widget.sync_measure_to_ui(i)
        log.message(
            message=f"[Phase2] Synced {count} measures to PatternMeasure data",
            scope=self.__class__.__name__,
        )

    def _update_tooltips_for_loaded_notes(self) -> None:
        """Set tooltips on all measure buttons so active notes show their note names."""
        for measure in self.measure_widgets:
            for row in range(self.sequencer_rows):
                if row >= len(measure.buttons):
                    continue
                for button in measure.buttons[row]:
                    self._update_tooltip(row, button)

    def _select_first_measure_and_sync(self, notes_loaded: int):
        """Select first bar and sync button manager after measures exist."""
        if self.pattern_widget and self.pattern_widget.get_measure_count() > 0:
            self.pattern_widget.select_measure(0)
            self._button_manager.set_buttons(self.buttons)
            log.message(
                message=f"Loaded {notes_loaded} notes from MidiFileEditor's MIDI file in {len(self.measure_widgets)} bars",
                scope=self.__class__.__name__,
            )
        else:
            log.warning(
                message="No bars were created from MIDI file",
                scope=self.__class__.__name__,
            )

    def _clear_measures_and_measures_list(self):
        """Clear existing bars and bars list"""
        if self.pattern_widget:
            self.pattern_widget.clear_and_reset(0)

    def save_pattern(self, filename: str):
        """Save the pattern: the same file that playback uses."""
        midi_file = self._build_midi_file_for_playback()
        self._save_midi_file(filename, midi_file)
        self._pattern_file_path = filename

        self._update_midi_file_editor_with_file(filename)

    def _update_midi_file_editor_with_file(self, filename: str):
        """f MidiFileEditor is connected, update its file too"""
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

    def _save_midi_file(self, filename: str, midi_file: MidiFile):
        """Save the MIDI file"""
        midi_file.save(filename)
        log.message(
            message=f"Pattern saved to {filename}", scope=self.__class__.__name__
        )

    def clear_pattern(self):
        """Clear the current bar's pattern, resetting all steps in the selected bar."""
        if self.current_measure_index < len(self.measure_widgets):
            measure = self.measure_widgets[self.current_measure_index]

            def reset_if_present(r, s):
                if s < len(measure.buttons[r]):
                    reset_button(measure.buttons[r][s])

            self._for_each_button(reset_if_present)

            # Sync sequencer digital
            self._sync_sequencer_with_measure(self.current_measure_index)
        self.schedule_recompile()

    def load_pattern(self, filename: str):
        """Load a pattern from a MIDI file"""
        try:
            self._pattern_file_path = filename
            self._apply_pattern_import(MidiFile(filename))
        except Exception as ex:
            log.error(
                message=f"Error loading pattern: {ex}", scope=self.__class__.__name__
            )
            QMessageBox.critical(self, "Error", f"Could not load pattern: {str(ex)}")
        self.schedule_recompile()

    def _add_button_with_label_from_spec(
        self,
        name: str,
        spec: ButtonSpec,
        layout: QHBoxLayout,
        slot: Optional[Callable[[], None]] = None,
    ) -> QPushButton:
        """Create a round button + label row from a ButtonSpec and add to layout."""
        label_row, btn = create_jdxi_button_with_label_from_spec(
            spec=spec, checkable=False
        )
        setattr(self, f"{name}_button", btn)
        layout.addWidget(btn)
        layout.addWidget(label_row)
        if slot is not None:
            btn.clicked.connect(slot)
        return btn

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
        btn_spec = ButtonSpec(
            icon=icon_enum,
            label="",
            slot=slot,
            layout=layout,
            append_to=append_to,
            name=name,
            checkable=checkable,
        )
        btn = self._create_round_action_button_from_spec(btn_spec, icon_enum, text)
        return btn

    def _create_round_action_button_from_spec(
        self, btn_spec: ButtonSpec, icon_enum, text: str
    ) -> QPushButton:
        """create round button from spec"""
        btn = create_jdxi_button(btn_spec.label)
        btn.setCheckable(btn_spec.checkable)
        if btn_spec.slot is not None:
            btn.clicked.connect(btn_spec.slot)
        if btn_spec.name:
            setattr(self, f"{btn_spec.name}_button", btn)
        if btn_spec.append_to is not None:
            btn_spec.append_to.append(btn)
        btn_spec.layout.addWidget(btn)
        pixmap = JDXi.UI.Icon.get_icon_pixmap(
            icon_name=icon_enum, color=JDXi.UI.Style.FOREGROUND, size=20
        )
        label_row, _ = create_jdxi_row(label=text, icon_pixmap=pixmap)
        btn_spec.layout.addWidget(label_row)
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
        group, layout = group_with_layout(label="Transport")
        transport_layout = QHBoxLayout()
        layout.addStretch()
        layout.addLayout(transport_layout)
        layout.addStretch()

        transport_button_group = QButtonGroup(self)
        transport_button_group.setExclusive(True)

        for spec in self.specs["transport"]:
            self._create_transport_control(
                spec, transport_layout, transport_button_group
            )
        return group

    def pattern_transport_play(self) -> None:
        """Start pattern playback (delegate to play_pattern)."""
        self.play_pattern()

    def pattern_transport_stop(self) -> None:
        """Stop pattern playback (delegate to stop_pattern)."""
        self.stop_pattern()

    def pattern_transport_pause_toggle(self) -> None:
        """Pause or resume pattern playback."""
        state = self.transport_controller.state
        if state == TransportState.PLAYING:
            self.transport_controller.pause()
        elif state == TransportState.PAUSED:
            self.transport_controller.play()
        else:
            # Nothing to pause: undo the click's own check toggle
            self.update_transport_buttons(state)

    def pattern_shuffle_play(self) -> None:
        """Jump to a random bar and play from there."""
        if not self.measure_widgets:
            return
        idx = random.randint(0, len(self.measure_widgets) - 1)
        if not self._prepare_playback():
            return
        bar_seconds = self.playback_engine.tick_to_seconds(self._pattern_spec().step_tick(idx, 0))
        self.transport_controller.seek_seconds(bar_seconds)
        self.transport_controller.play()

    def _pattern_rows(self) -> list[PatternRow]:
        return [
            PatternRow(name=label, channel=get_channel_for_row(row))
            for row, label in enumerate(self.row_labels[: self.sequencer_rows])
        ]

    def _pattern_spec(self) -> PatternSpec:
        """Snapshot of the pattern as data for the compiler."""
        spec = PatternSpec(
            bars=max(1, len(self.measure_widgets)),
            steps_per_bar=min(self.measure_beats, MeasureBeats.PER_MEASURE_4_4),
            bpm=self.timing_bpm,
            rows=self._pattern_rows(),
            ticks_per_beat=self.ppq,
        )
        for bar_index, measure in enumerate(self.measure_widgets):
            for row in range(self.sequencer_rows):
                for step in range(min(spec.steps_per_bar, len(measure.buttons[row]))):
                    button = measure.buttons[row][step]
                    if not button.isChecked():
                        continue
                    note_spec = get_button_note_spec(button)
                    if not note_spec.is_active:
                        continue
                    for chord_note in self._step_notes(note_spec):
                        duration_ticks = round(
                            (chord_note.duration_steps or 1) * spec.ticks_per_step
                        )
                        spec.notes.append(
                            PatternNote(
                                bar=bar_index,
                                step=step,
                                row=row,
                                note=chord_note.note,
                                velocity=chord_note.velocity,
                                duration_ticks=max(1, duration_ticks),
                            )
                        )
        return spec

    def _build_midi_file_for_playback(self) -> MidiFile:
        """Compile the current pattern (used for playback and Save)."""
        return compile_pattern(self._pattern_spec())

    def play_pattern(self, *, restart_loop: bool = False):
        """
        Play the pattern through the shared transport (loops whole bars).

        :param restart_loop: Ignored; kept for callers of the old timer-based loop.
        """
        state = self.transport_controller.state
        if state == TransportState.PLAYING:
            return
        if state == TransportState.PAUSED:
            self.transport_controller.play()
            return
        if not self._prepare_playback():
            self.update_transport_buttons(self.transport_controller.state)
            return
        # Record from Play until Stop
        self.midi_state.file = self.playback_engine.midi_file
        self.midi_state.file.filename = self._pattern_file_path or "pattern"
        self.midi_state.file_duration_seconds = 3600.0
        if self.usb_recorder.file_auto_generate_checkbox.isChecked():
            self.usb_recorder.update_auto_wav_filename()
        self.usb_recorder.start_recording()
        self.transport_controller.play()
        log.message(message="Pattern playback started", scope=self.__class__.__name__)

    def _prepare_playback(self) -> bool:
        """Compile and load the pattern if stopped; False if there is nothing to play."""
        if not self.measure_widgets:
            return False
        spec = self._pattern_spec()
        if not spec.notes:
            log.message(
                message="Pattern has no notes to play", scope=self.__class__.__name__
            )
            return False
        if self.transport_controller.state == TransportState.STOPPED:
            self.transport_controller.load(compile_pattern(spec), keep_position=True)
            self.transport_controller.set_loop(self._pattern_loop_enabled)
            self._sync_transport_mutes()
        return True

    def schedule_recompile(self) -> None:
        """Recompile after the current edit so a playing pattern picks it up."""
        controller = getattr(self, "transport_controller", None)  # None during UI setup
        if controller is not None and controller.state != TransportState.STOPPED:
            self._recompile_timer.start()

    def _recompile_if_loaded(self) -> None:
        if self.transport_controller.state == TransportState.STOPPED:
            return  # The next Play compiles
        self.transport_controller.load(
            self._build_midi_file_for_playback(), keep_position=True
        )
        self._sync_transport_mutes()

    def _sync_transport_mutes(self) -> None:
        """Apply row mutes (stored as channels) to the transport immediately."""
        if getattr(self, "transport_controller", None) is None:
            return  # UI setup
        self.transport_controller.set_mutes(
            muted_tracks=set(), muted_channels=set(self.muted_channels)
        )

    def _send_playback_message(self, msg) -> None:
        """Send straight to the port, like the MIDI File Player (no per-message logging)."""
        if self.midi_helper and self.midi_helper.midi_out:
            self.midi_helper.midi_out.send_message(msg.bytes())

    def _on_transport_state_changed(self, state: TransportState) -> None:
        """Transport buttons follow the transport, including at the end of the pattern."""
        self._apply_transport_state(state)
        if state == TransportState.STOPPED:
            self._show_playback_step(None)

    def _on_transport_position_changed(self, _seconds: float) -> None:
        """Highlight the step under the playback position (also over empty steps)."""
        if self.transport_controller.state == TransportState.STOPPED:
            return
        ticks_per_step = max(1, self.ppq // 4)
        self._show_playback_step(self.transport_controller.position_tick // ticks_per_step)

    def _show_playback_step(self, global_step: Optional[int]) -> None:
        """Move the bar/step highlight to *global_step* (None clears it)."""
        last_step = getattr(self, "_playback_last_step_in_bar", -1)
        if global_step is None:
            for row in range(self.sequencer_rows):
                for btn in self._get_step_buttons(row, last_step) if last_step >= 0 else []:
                    set_sequencer_style(btn=btn, is_current=False, checked=btn.isChecked())
            self._playback_last_step_in_bar = -1
            self._playback_last_bar_index = -1
            return
        steps_per_bar = self.measure_beats
        total_steps = len(self.measure_widgets) * steps_per_bar
        if total_steps <= 0:
            return
        global_step %= total_steps
        self.current_step = global_step
        bar_index = global_step // steps_per_bar
        step_in_bar = global_step % steps_per_bar
        last_bar = getattr(self, "_playback_last_bar_index", -1)
        if bar_index >= len(self.measure_widgets):
            return
        self.current_measure_index = bar_index
        self._sync_sequencer_on_step_change(bar_index, last_bar)
        if step_in_bar == last_step and bar_index == last_bar:
            return
        for row in range(self.sequencer_rows):
            for btn in self._get_step_buttons(row, last_step) if last_step >= 0 else []:
                set_sequencer_style(btn=btn, is_current=False, checked=btn.isChecked())
            for btn in self._get_step_buttons(row, step_in_bar):
                set_sequencer_style(btn=btn, is_current=True, checked=btn.isChecked())
        self._playback_last_step_in_bar = step_in_bar

    def closeEvent(self, event) -> None:
        """Stop the playback thread before the editor goes away."""
        self.transport_controller.shutdown()
        super().closeEvent(event)

    def _sync_sequencer_on_step_change(self, bar_index: int, last_bar: int | Any):
        """Only sync sequencer and bar list when the displayed bar changes"""
        if bar_index != last_bar:
            self._sync_sequencer_with_measure(bar_index)
            self._playback_last_bar_index = bar_index
            if self.measures_list and bar_index < self.measures_list.count():
                self.measures_list.setCurrentRow(bar_index)
                item = self.measures_list.item(bar_index)
                if item:
                    self.measures_list.scrollToItem(item)

    def stop_pattern(self):
        """Stop the pattern, silence the instrument and rewind."""
        self.transport_controller.stop()

        # Stop USB recording (pattern records until user stops manually)
        if hasattr(self.usb_recorder, "recorder") and hasattr(
            self.usb_recorder.recorder, "stop_recording"
        ):
            self.usb_recorder.recorder.stop_recording()

        self.current_step = 0
        log.message(message="Pattern playback stopped", scope=self.__class__.__name__)

    def _note_name_to_midi(self, note_name: str) -> int:
        """Convert note name (e.g., 'C4') to MIDI note number."""
        return self._note_converter.note_name_to_midi(note_name)

    def _midi_to_note_name(self, midi_note: int, drums: bool = False) -> str:
        """Convert MIDI note number to note name (e.g., 60 -> 'C4') or drum name."""
        return self._note_converter.midi_to_note_name(midi_note, drums=drums)

    def _learn_pattern(self, message):
        """Learn the pattern of incoming MIDI notes, preserving rests."""
        if message.type == MidoMessageType.NOTE_ON.value and message.velocity > 0:
            note = message.note  # mido uses lowercase 'note'

            # Determine the correct row for the note
            for row in range(self.sequencer_rows):
                if note in self._get_note_range_for_row(row):
                    # Calculate step within current bar (0 to beats_per_bar-1)
                    step_in_bar = self.current_step % self.measure_beats

                    # Store note in the current bar's measure and sequencer
                    for btn in self._get_step_buttons(row, step_in_bar):
                        update_button_state(btn, True)
                        btn.note = note
                        btn.velocity = message.velocity
                        btn.duration_ms = self._get_duration_ms()
                        sync_button_note_spec(btn)

                    # Record the note in the learned pattern (for compatibility)
                    self.learned_pattern[row][step_in_bar] = note
                    self.active_notes[note] = row  # Mark the note as active

                    # Add the note_on message to the MIDI track
                    self.midi_track.append(
                        Message(
                            MidoMessageType.NOTE_ON.value,
                            note=note,
                            velocity=message.velocity,
                            time=0,
                        )
                    )
                    break  # Stop checking once the note is assigned

        elif message.type == MidoMessageType.NOTE_OFF.value:
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
                    Message(
                        MidoMessageType.NOTE_OFF.value, note=note, velocity=0, time=0
                    )
                )
                # Advance step within current bar (0 to beats_per_bar-1)
                self.current_step = (self.current_step + 1) % self.measure_beats

    def _apply_learned_pattern(self):
        """Apply the learned pattern to the sequencer UI."""
        for row in range(self.sequencer_rows):
            for button in self.buttons[row]:
                reset_button(button)
                set_sequencer_style(button)
                button.setToolTip("")

            # Apply the learned pattern
            for time, note in enumerate(self.learned_pattern[row]):
                # Ensure only one button is activated per note
                if note is not None and 0 <= time < len(self.buttons[row]):
                    button = self.buttons[row][time]
                    update_button_state(button, True)
                    button.note = note
                    # Set default duration for learned pattern notes
                    button.duration_ms = self._get_duration_ms()
                    # Set default velocity for learned pattern notes
                    button.velocity = self.velocity_spinbox.value()
                    sync_button_note_spec(button)
                    button.setStyleSheet(
                        JDXi.UI.Style.generate_sequencer_button_style(True)
                    )
                    self._update_tooltip(row, button)
        self.schedule_recompile()

    def _get_note_range_for_row(self, row: int) -> range:
        """Get the note range for a specific row."""
        return self._note_converter.get_note_range_for_row(row)

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
        channel = get_channel_for_row(row)
        if checked:
            log.message(message=f"Row {row} muted", scope=self.__class__.__name__)
            self.muted_channels.append(channel)
        else:
            log.message(message=f"Row {row} unmuted", scope=self.__class__.__name__)
            self.muted_channels.remove(channel)

        # Synth-style: unmuted=lit, muted=dark
        if row < len(self.mute_buttons):
            self.mute_buttons[row].setStyleSheet(
                generate_sequencer_button_style(
                    not checked, checked_means_inactive=True
                )
            )

        # Update the UI or internal state to reflect the mute status
        for button in self.buttons[row]:
            button.setEnabled(not checked)
        self._sync_transport_mutes()

    def update_drum_rows(self):
        """Update displayed buttons based on the selected drum option."""
        self.drum_selector.currentText()
        # Ensure UI updates properly
        self.update()

    def _build_row_map(self):
        return {
            0: self.digital1_selector,
            1: self.digital2_selector,
            2: self.analog_selector,
            3: self.drum_selector,
        }
