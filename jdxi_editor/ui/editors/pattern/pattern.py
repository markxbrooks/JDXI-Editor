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
from mido import Message, MetaMessage, MidiFile, MidiTrack, bpm2tempo, tempo2bpm

from jdxi_editor.midi.conversion.note import MidiNoteConverter
from jdxi_editor.midi.file.controller import MidiFileControllerConfig, MidiFileController
from jdxi_editor.midi.playback.controller import PlaybackConfig, PatternPlaybackController, SequencerEvent
from jdxi_editor.ui.editors.pattern.helper import sync_button_note_spec, get_button_note_spec, reset_button, \
    update_button_state, reset_measure, set_sequencer_style
from jdxi_editor.ui.editors.pattern.learner import PatternLearnerConfig, PatternLearnerEvent, PatternLearner
from jdxi_editor.ui.editors.pattern.models import ClipboardData, ButtonAttrs
from jdxi_editor.ui.editors.pattern.sequencer.row import SequencerRow
from jdxi_editor.ui.editors.pattern.spec import SequencerRowSpec
from jdxi_editor.ui.editors.pattern.timing.config import TimingConfig
from jdxi_editor.ui.editors.pattern.ui import PatternUI
from jdxi_editor.ui.sequencer.button.manager import SequencerButtonManager, NoteButtonAttrs
from jdxi_editor.ui.style import JDXiUIThemeManager
from jdxi_editor.ui.widgets.combo_box.synchronizer import ComboBoxUpdateConfig, ComboBoxSynchronizer
from jdxi_editor.ui.widgets.editor.helper import create_group_with_layout
from picomidi import MidiTempo
from picomidi.core.tempo import milliseconds_per_note, convert_absolute_time_to_delta_time
from picomidi.message.type import MidoMessageType
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QWidget,
)
from rtmidi.midiconstants import CONTROL_CHANGE, NOTE_ON

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.channel.channel import MidiChannel
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.helpers.widgets import (
    create_jdxi_button,
    create_jdxi_button_from_spec,
    create_jdxi_button_with_label_from_spec,
    create_jdxi_row,
)
from jdxi_editor.ui.editors.midi_player.playback.engine import (
    PlaybackEngine,
    TransportState,
)
from jdxi_editor.ui.editors.midi_player.transport.spec import (
    TransportSpec, NoteButtonSpec,
)
from jdxi_editor.ui.preset.helper import JDXiPresetHelper
from jdxi_editor.ui.widgets.pattern.measure import PatternMeasure
from jdxi_editor.ui.widgets.pattern.measure_widget import PatternMeasureWidget
from jdxi_editor.ui.widgets.pattern.sequencer_button import SequencerButton
from picoui.helpers import create_layout_with_items, group_with_layout
from picoui.helpers.spinbox import spinbox_with_label_from_spec
from picoui.specs.widgets import (
    ButtonSpec,
    FileSelectionSpec,
    SpinBoxSpec,
)
from picoui.widget.helper import create_combo_box, get_file_path_from_spec
from picoui.widget.setters import set_spinbox_value

TICKS_PER_STEP = 120
SECONDS_PER_MINUTE = 60
PPQ = 480


class MeasureBeats:
    """Measure Beats"""
    PER_MEASURE_4_4 = 16
    PER_MEASURE_3_4 = 12


# MIDI channel -> sequencer row: 0=Digital1, 1=Digital2, 2=Analog, 9=Drum
CHANNEL_TO_ROW = {
    MidiChannel.DIGITAL_SYNTH_1: 0,
    MidiChannel.DIGITAL_SYNTH_2: 1,
    MidiChannel.ANALOG_SYNTH: 2,
    MidiChannel.DRUM_KIT: 3,
}


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
        self.paste_button: QPushButton | None = None
        self.pause_button: QPushButton | None = None
        self.stop_button: QPushButton | None = None
        self.play_button: QPushButton | None = None
        self._state: TransportState | None = None
        self.measure_name: str = self.tr("Measure")
        self.measure_name_plural: str = self.tr("Measures")
        self.muted_channels: list[int] = []
        self.total_measures: int = 1  # Start with 1 bar by default
        self.midi_helper: Optional[MidiIOHelper] = midi_helper
        self.preset_helper: Optional[JDXiPresetHelper] = preset_helper
        self.midi_file_editor: Optional[Any] = midi_file_editor  # Reference to MidiFileEditor
        # self.buttons populated by parent PatternUI._setup_ui() - do not overwrite
        self.button_layouts: list[QHBoxLayout] = []  # Store references to button layouts for each row
        self.current_measure_index = 0  # Currently selected bar (0-indexed)
        self.timer: Optional[QTimer] = None
        self.current_step: int = 0  # Currently selected step (0-indexed)
        self.timing_bpm: int = 120  # Beats per minute
        self.timing = TimingConfig()
        self.total_steps = 16  # Always 16 steps per bar (don't multiply by measures)
        self.beats_per_pattern: int = 4  # Number of beats per pattern
        self.measure_beats: int = 16  # Number of beats per bar (16 or 12)
        self.last_tap_time: Optional[datetime] = None  # Last tap time
        self.tap_times: list[float] = []  # List of tap times
        self.learned_pattern: list[list[Optional[int]]] = [[None] * self.total_steps for _ in
                                                           range(
                                                               self.sequencer_rows)]  # Learned pattern (row -> step -> midi_note)
        self.active_notes: dict[int, int] = {}  # Track active notes (midi_note -> row index)
        self.midi_file: MidiFile = MidiFile()  # Initialize a new MIDI file
        self.midi_track: MidiTrack = MidiTrack()  # Create a new track
        self.midi_file.tracks.append(self.midi_track)  # Add the track to the file
        self.clipboard: Optional[dict[
            str, Any]] | None = None  # Store copied notes: {source_bar, rows, start_step, end_step, notes_data}
        """self.measures = [
            PatternMeasure(rows=4, steps_per_bar=self.timing.steps_per_bar)
            for _ in range(number_of_bars)
        ]"""
        self.measure_widgets: list[PatternMeasureWidget] = []  # Each measure stores its own notes
        self.measures: list[PatternMeasure] = []  # Each measure stores its own notes
        self._pattern_paused: bool = False
        self.playback_engine: PlaybackEngine = PlaybackEngine()
        self.row_specs: list[SequencerRowSpec] = [
            SequencerRowSpec(
                "Digital Synth 1", JDXi.UI.Icon.PIANO, JDXi.UI.Style.ACCENT
            ),
            SequencerRowSpec(
                "Digital Synth 2", JDXi.UI.Icon.PIANO, JDXi.UI.Style.ACCENT
            ),
            SequencerRowSpec(
                "Analog Synth", JDXi.UI.Icon.PIANO, JDXi.UI.Style.ACCENT_ANALOG
            ),
            SequencerRowSpec("Drums", JDXi.UI.Icon.DRUM, JDXi.UI.Style.ACCENT),
        ]
        # self._init_midi_file()
        self._initialize_default_measure()

        JDXi.UI.Theme.apply_editor_style(self)
        self._init_playing_controllers()
        self._connect_midi_signals()
        self._init_midi_file()
        self._initialize_default_measure()

        JDXi.UI.Theme.apply_editor_style(self)

        self._load_from_midi_file_editor_if_available()

        # If MidiFileEditor is provided and has a loaded file, load it
        if self.midi_file_editor and hasattr(self.midi_file_editor, "midi_state"):
            if self.midi_file_editor.midi_state.file:
                self.load_from_midi_file_editor()

    def on_button_toggled(self, row: int, step: int, checked: bool):
        measure = self.measures[self.current_measure_index]
        step_data = measure.steps[row][step]
        step_data.active = checked

    def sync_ui_to_measure(self, bar_index: int):
        measure = self.measures[bar_index]
        widget = self.measure_widgets[bar_index]

        for row in range(self.sequencer_rows):
            for step in range(self.timing.steps_per_bar):
                step_data = measure.steps[row][step]
                button = widget.buttons[row][step]

                button.setChecked(step_data.active)
                button.set_note(step_data.note)
                button.set_velocity(step_data.velocity)

    def _update_timer_interval(self):
        interval = self.timing.ms_per_step
        self.timer.setInterval(int(interval))

    def _load_from_midi_file_editor_if_available(self) -> None:
        """Load from MidiFileEditor if it has a file."""
        self.clear_pattern()
        if self.midi_file_editor and hasattr(self.midi_file_editor, "midi_state"):
            if self.midi_file_editor.midi_state.file:
                self.load_from_midi_file_editor()

    def _on_learner_note_learned(self, event: PatternLearnerEvent) -> None:
        """Update measure/sequencer from learned note; append NOTE_ON to midi_track."""
        step_in_measure = event.step
        row = event.row
        if self.current_measure_index < len(self.measure_widgets):
            measure = self.measure_widgets[self.current_measure_index]
            if step_in_measure < len(measure.buttons[row]):
                measure_button = measure.buttons[row][step_in_measure]
                update_button_state(measure_button, True)
                measure_button.note = event.note
                measure_button.note_velocity = event.velocity
                measure_button.note_duration = event.duration_ms
                sync_button_note_spec(measure_button)
        if step_in_measure < len(self.buttons[row]):
            seq_btn = self.buttons[row][step_in_measure]
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
        """Create MIDI/playback/learn controllers and wire to UI (Pattern Playing)."""
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
            ticks_per_beat=PPQ,
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
        ms_per_step = int(self._calculate_step_duration())
        playback_config = PlaybackConfig(
            ticks_per_beat=PPQ,
            beats_per_measure=4,
            measure_beats=self.measure_beats,
            default_bpm=self.timing.bpm,
            playback_interval_ms=ms_per_step,
        )
        self._playback_controller = PatternPlaybackController(
            config=playback_config,
            playback_engine=self.playback_engine,
            scope=self.__class__.__name__,
        )
        self._playback_controller.on_playback_started = (
            self._on_playback_controller_started
        )
        self._playback_controller.on_playback_stopped = (
            self._on_playback_controller_stopped
        )
        self._playback_controller.on_playback_paused = (
            self._on_playback_controller_paused
        )
        self._playback_controller.on_bar_changed = self._on_playback_measure_changed
        self._playback_controller.on_step_changed = self._on_playback_step_changed
        if self.midi_helper:
            self._playback_controller.on_midi_event = (
                lambda msg: self.midi_helper.send_raw_message(msg.bytes())
            )

    def _on_playback_controller_started(self) -> None:
        """Update play/stop buttons when playback controller starts."""
        self.update_transport_buttons(TransportState.PLAYING)

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

    def _on_playback_controller_paused(self) -> None:
        """Update play/pause buttons when playback controller pauses."""
        self.update_transport_buttons(TransportState.PAUSED)
        self._pattern_paused = True

    def _on_playback_controller_stopped(self) -> None:
        """Update play/stop buttons when playback controller stops."""
        self.update_transport_buttons(TransportState.STOPPED)
        self.current_step = 0
        self._pattern_paused = False

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
        self.current_measure_index = measure_index
        self._sync_sequencer_with_measure(measure_index)
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
            if 0 <= last_step < len(self.buttons[row]):
                btn = self.buttons[row][last_step]
                set_sequencer_style(btn=btn, is_current=False, checked=btn.isChecked())
            if step_in_measure < len(self.buttons[row]):
                btn = self.buttons[row][step_in_measure]
                set_sequencer_style(btn=btn, is_current=True, checked=btn.isChecked())
        self._playback_last_step_in_measure = step_in_measure

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
        measure_number = len(self.measure_widgets) + 1

        # Check if we should copy the previous measure
        copy_previous = self.copy_previous_measure_checkbox.isChecked()

        if copy_previous and len(self.measure_widgets) > 0:
            measure = PatternMeasureWidget()
            # Copy notes from the previous measure (most recently added measure)
            previous_measure = self.measure_widgets[-1]
            for row in range(self.sequencer_rows):
                for step in range(self.measure_beats):
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
            self.measure_widgets.append(measure)
        else:
            measure = self.add_and_reset_new_measure()

        # Add to measures list
        item = QListWidgetItem(f"{self.measure_name} {measure_number}")
        item.setData(
            Qt.ItemDataRole.UserRole, len(self.measure_widgets) - 1
        )  # Store measure index
        self.measures_list.addItem(item)

        # Select the new measure and sync sequencer digital
        self.measures_list.setCurrentItem(item)
        self.current_measure_index = len(self.measure_widgets) - 1

        # Update total measures (but keep total_steps at 16)
        self.total_measures = len(self.measure_widgets)
        self._update_pattern_length()

        # Sync sequencer buttons with the new (empty) measure
        self._sync_sequencer_with_measure(self.current_measure_index)

        log.message(
            message=(
                f"Added measure {measure_number}. "
                f"Total: {self.total_measures}"
            ),
            scope=self.__class__.__name__,
        )

    def _connect_midi_signals(self):
        combo = getattr(self, "_combo_synchronizer", None)
        if combo:
            self._reconnect_combo_synchronizer()
            self.midi_helper.midi_message_outgoing.connect(combo.process_outgoing_midi)

    def _init_model_structures(self):
        self.row_labels = [
            "Digital Synth 1",
            "Digital Synth 2",
            "Analog Synth",
            "Drums",
        ]
        self.buttons = [[] for _ in range(self.sequencer_rows)]
        self.mute_buttons = []
        self.specs = self._build_specs()

    def _create_spinbox_specs(self) -> dict[str, SpinBoxSpec]:
        """create spin box specs"""
        return {
            "velocity": SpinBoxSpec(
                label="Vel:",
                min_val=1,
                max_val=127,
                value=100,
                tooltip="Default velocity for new notes (1-127)",
            ),
            "tempo": SpinBoxSpec(
                label="BPM:",
                min_val=20,
                max_val=300,
                value=120,
                tooltip=self.tr("Tempo in beats per minute (20–300)"),
            ),
            "start": SpinBoxSpec(
                label=self.tr("Start"),
                min_val=0,
                max_val=15,
                value=0,
                tooltip=self.tr("Start step (0–15)"),
            ),
            "end": SpinBoxSpec(
                label=self.tr("End"),
                min_val=0,
                max_val=15,
                value=15,
                tooltip=self.tr("End step (0–15)"),
            ),
        }

    def _create_learn_group(self) -> QGroupBox:
        """create learn group"""
        learn_group = QGroupBox("Learn Pattern")
        learn_layout = QHBoxLayout()

        self._add_button_with_label_from_spec(
            "learn",
            self.specs["buttons"]["learn"],
            learn_layout,
        )
        self._add_button_with_label_from_spec(
            "stop_learn",
            self.specs["buttons"]["stop_learn"],
            learn_layout,
        )
        learn_group.setLayout(learn_layout)
        return learn_group

    def _create_measure_group(self) -> QGroupBox:
        """Bar management area (separate row for Add Measure button and checkbox)"""

        # First row: Add Measure button and Copy checkbox
        measure_controls_layout = QHBoxLayout()
        self._add_button_with_label_from_spec(
            "add_measure",
            self.specs["buttons"]["add_measure"],
            measure_controls_layout,
        )
        self.copy_previous_measure_checkbox = QCheckBox(
            f"Copy previous {self.measure_name.lower()}"
        )
        self.copy_previous_measure_checkbox.setChecked(False)
        JDXiUIThemeManager.apply_button_mini_style(self.copy_previous_measure_checkbox)

        measure_controls_layout.addWidget(self.copy_previous_measure_checkbox)
        measure_controls_layout.addStretch()  # Push controls to the left

        # Copy/Paste controls (round buttons + icon labels)
        copy_paste_layout = QHBoxLayout()
        self._add_button_with_label_from_spec(
            "copy",
            self.specs["buttons"]["copy"],
            copy_paste_layout,
        )
        self._add_button_with_label_from_spec(
            "paste",
            self.specs["buttons"]["paste"],
            copy_paste_layout,
        )
        self.paste_button.setEnabled(False)  # Disabled until something is copied

        # Step range selection (use SpinBoxSpec for both start and end)
        start_label, self.start_step_spinbox = spinbox_with_label_from_spec(
            self.specs["spinboxes"]["start"]
        )
        end_label, self.end_step_spinbox = spinbox_with_label_from_spec(
            self.specs["spinboxes"]["end"]
        )
        step_label = QLabel(self.tr("Steps:"))
        to_label = QLabel(self.tr("to"))

        step_layout_widgets = [step_label,
                               start_label,
                               self.start_step_spinbox,
                               to_label,
                               end_label,
                               self.end_step_spinbox
                               ]
        step_range_layout = create_layout_with_items(items=step_layout_widgets,
                                                     start_stretch=False,
                                                     end_stretch=False)
        measure_group, measure_layout = create_group_with_layout(label=self.measure_name_plural, vertical=True)
        measure_group_layouts = [
            measure_controls_layout,
            copy_paste_layout,
            step_range_layout,
        ]
        for layout in measure_group_layouts:
            measure_layout.addLayout(layout)
        measure_group.setLayout(measure_layout)
        return measure_group

    def _create_file_group(self) -> QGroupBox:
        """File operations area (round buttons + icon labels, same style as Transport)"""
        file_group = QGroupBox("Pattern")
        file_layout = QHBoxLayout()
        self._add_button_with_label_from_spec(
            "load",
            self.specs["buttons"]["load"],
            file_layout,
        )
        self._add_button_with_label_from_spec(
            "save",
            self.specs["buttons"]["save"],
            file_layout,
        )
        self._add_button_with_label_from_spec(
            "clear_learn",
            self.specs["buttons"]["clear_learn"],
            file_layout,
        )

        self.drum_selector = create_combo_box(spec=self.specs["combos"]["drum"])
        self.drum_selector.currentIndexChanged.connect(self._update_drum_rows)

        file_group.setLayout(file_layout)
        return file_group

    def ui_generate_button_row(self, row_index: int, visible: bool = False):
        """Generate sequencer button row using SequencerButton."""
        button_row_layout = QHBoxLayout()
        for i in range(self.measure_beats):
            button = SequencerButton(row=row_index, column=i)
            set_sequencer_style(button)
            button.clicked.connect(
                lambda checked, btn=button: self._on_button_clicked(btn, checked)
            )
            self.buttons[row_index].append(button)
            button.setVisible(visible)  # Initially hide all drum buttons
            button_row_layout.addWidget(button)
        return button_row_layout

    def _log_and_return(self, ok: bool, msg: str) -> bool:
        """log and return"""
        if not ok:
            log.debug(msg, scope=self.__class__.__name__)
        return ok

    def reset_all_measures(self):
        """reset all measures"""
        for measure in self.measure_widgets:
            reset_measure(measure)

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

        measure = self.measure_widgets[self.current_measure_index]
        notes_data = {}

        # Copy all rows and selected steps (use NoteButtonSpec for note data)
        for row in range(self.sequencer_rows):
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

        if self.current_measure_index >= len(self.measure_widgets):
            QMessageBox.warning(self, "Paste", "No bar selected")
            return

        measure = self.measure_widgets[self.current_measure_index]
        notes_data = self.clipboard["notes_data"]
        start_step = self.start_step_spinbox.value()
        source_start = self.clipboard["start_step"]
        source_end = self.clipboard["end_step"]
        num_steps = source_end - source_start + 1

        # Paste notes starting at the selected start step
        for row in range(self.sequencer_rows):
            if row in notes_data:
                for source_step, button_data in notes_data[row].items():
                    # Calculate destination step
                    dest_step = start_step + (source_step - source_start)

                    if dest_step < 0 or dest_step >= self.measure_beats:
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
        Sync the main sequencer buttons with the notes from the specified measure.
        This displays the measure's notes in the sequencer grid.

        :param bar_index: int Index of the bar to digital (0-indexed)
        """
        if bar_index < 0 or bar_index >= len(self.measure_widgets):
            return

        measure = self.measure_widgets[bar_index]

        # Copy note data from the measure to the main sequencer buttons
        for row in range(self.sequencer_rows):
            for step in range(MeasureBeats.PER_MEASURE_4_4):
                if step < len(self.buttons[row]) and step < len(measure.buttons[row]):
                    sequencer_button = self.buttons[row][step]
                    measure_button: SequencerButton = measure.buttons[row][step]

                    # Sync checked state and note
                    update_button_state(sequencer_button, measure_button.isChecked())
                    sequencer_button.note = measure_button.note
                    # Copy duration if available
                    if hasattr(measure_button, NoteButtonAttrs.NOTE_DURATION):
                        sequencer_button.note_duration = measure_button.note_duration
                    else:
                        sequencer_button.note_duration = None
                    # Copy velocity if available
                    if hasattr(measure_button, NoteButtonAttrs.NOTE_VELOCITY):
                        sequencer_button.note_velocity = measure_button.note_velocity
                    else:
                        sequencer_button.note_velocity = None
                    sync_button_note_spec(sequencer_button)

                    self._update_tooltip(row, sequencer_button)

                    self._update_sequencer_button_style(sequencer_button, step)

    def _update_tooltip(self, row: int, sequencer_button):
        """Update tooltip"""
        if sequencer_button.note is not None:
            if row == SequencerRow.DRUMS:  # Drums
                note_name = self._midi_to_note_name(
                    sequencer_button.note, drums=True
                )
            else:
                note_name = self._midi_to_note_name(sequencer_button.note)
            sequencer_button.setToolTip(f"Note: {note_name}")
        else:
            sequencer_button.setToolTip("")

    def _highlight_bar(self, bar_index: int):
        """Update button styles to highlight the current step in the selected bar"""
        if bar_index < 0 or bar_index >= len(self.measure_widgets):
            return

        # Update all sequencer buttons to show current step
        for row in range(self.sequencer_rows):
            for step in range(MeasureBeats.PER_MEASURE_4_4):
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
        self.learned_pattern = [[None] * self.total_steps for _ in range(self.sequencer_rows)]

        for row in range(self.sequencer_rows):
            for button in self.buttons[row]:
                reset_button(button)
                set_sequencer_style(button)

        log.message(message="Cleared learned pattern.", scope=self.__class__.__name__)

    def _on_measure_count_changed(self, count: int):
        """Handle measure count changes"""
        current_count = len(self.measure_widgets)

        if count > current_count:
            # Add new measures
            for _ in range(count - current_count):
                self._add_measure()
        else:
            # Remove measures from the end
            while len(self.measure_widgets) > count:
                self.measure_widgets.pop()
                # the plan is to add more measures via tab 2, 3 & 4
                # index = self.tab_widget.indexOf(measure)
                # self.tab_widget.removeTab(index)

        self.total_measures = count
        self._update_pattern_length()

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

        if checked:
            # Store the currently selected note when button is activated
            selector = self.row_map.get(button.row)
            if selector is not None:
                note_name = selector.currentText()
                midi_note = self._note_name_to_midi(note_name)
                button.note = midi_note
            # Set default duration for manually created notes
            if (
                    not hasattr(button, NoteButtonAttrs.NOTE_DURATION)
                    or button.note_duration is None
            ):
                button.note_duration = self._get_duration_ms()
            # Set default velocity for manually created notes
            if (
                    not hasattr(button, NoteButtonAttrs.NOTE_VELOCITY)
                    or button.note_velocity is None
            ):
                button.note_velocity = self.velocity_spinbox.value()
            sync_button_note_spec(button)
            note_name = self._midi_to_note_name(button.note)
            if button.row == 3:
                drums_note_name = self._midi_to_note_name(button.note, drums=True)
                button.setToolTip(f"Note: {drums_note_name}")
            else:
                button.setToolTip(f"Note: {note_name}")

        # Store the note in the currently selected bar's measure
        if len(self.measure_widgets) > 0 and self.current_measure_index < len(self.measure_widgets):
            self._store_note_in_measures(button, checked)

        self._update_button_style(button, checked)

    def _store_note_in_measures(self, button: SequencerButton, checked: bool):
        """sore notes in measures"""
        measure = self.measure_widgets[self.current_measure_index]
        step_in_bar = button.column  # button.column is 0-15 for sequencer buttons

        if button.row < len(measure.buttons) and step_in_bar < len(
                measure.buttons[button.row]
        ):
            measure_button = measure.buttons[button.row][step_in_bar]
            update_button_state(measure_button, checked)
            if checked:
                measure_button.note = button.note
                # Copy duration if available
                if hasattr(button, NoteButtonAttrs.NOTE_DURATION):
                    measure_button.note_duration = button.note_duration
                # Copy velocity if available
                if hasattr(button, NoteButtonAttrs.NOTE_VELOCITY):
                    measure_button.note_velocity = button.note_velocity
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
        set_sequencer_style(sequencer_button, checked=sequencer_button.isChecked, is_current=is_current)
        sequencer_button.setStyleSheet(
            JDXi.UI.Style.generate_sequencer_button_style(
                sequencer_button.isChecked(),
                is_current,
                is_selected_bar=True,  # All displayed buttons are from selected bar
            )
        )

    def _build_row_map(self) -> dict[int, QComboBox]:
        """build row map"""
        return {
            0: self.digital1_selector,
            1: self.digital2_selector,
            2: self.analog_selector,
            3: self.drum_selector,
        }

    def _on_beats_per_bar_changed(self, index: int):
        """Handle beats per bar changes from the combobox"""
        if index == 0:
            self.measure_beats = MeasureBeats.PER_MEASURE_4_4
        else:
            self.measure_beats = MeasureBeats.PER_MEASURE_3_4

        # Update button states based on beats per bar
        self._update_button_states_for_beats_per_bar()
        log.message(f"Beats per bar changed to {self.measure_beats}")

    def _update_button_states_for_beats_per_bar(self) -> None:
        """Enable/disable sequencer buttons based on beats per bar setting."""

        active_steps = (
            MeasureBeats.PER_MEASURE_3_4
            if self.measure_beats == MeasureBeats.PER_MEASURE_3_4
            else MeasureBeats.PER_MEASURE_4_4
        )

        for row in range(self.sequencer_rows):
            for step in range(MeasureBeats.PER_MEASURE_4_4):
                if step >= len(self.buttons[row]):
                    continue

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
        log.message(f"Beats per measure changed to {self.measure_beats}")

    def _update_measure_beats(self, beats: int):
        self.measure_beats = beats

    def _update_button_states_for_beats_per_measure(self):
        """Enable/disable sequencer buttons based on beats per measure setting"""
        # Steps 12-15 disabled when beats_per_measure is 12
        for row in range(self.sequencer_rows):
            for step in range(self.measure_beats):
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

        # Sync sequencer digital after updating button states
        if self.current_measure_index < len(self.measure_widgets):
            self._sync_sequencer_with_measure(self.current_measure_index)

    def _get_duration_ms(self) -> float:
        """Get the default duration in milliseconds based on the duration combo selection"""
        # Duration multipliers: 16th=1, 8th=2, dotted 8th=3, quarter=4, dotted quarter=6, half=8, dotted half=12, whole=16
        duration_multipliers = [1, 2, 3, 4, 6, 8, 12, 16]
        index = self.duration_combo.currentIndex()
        steps = duration_multipliers[index] if index < len(duration_multipliers) else 1
        # Each step is a 16th note, so duration = steps * (beat_duration / 4)
        # beat_duration in ms = 60000 / bpm
        step_duration_ms = self._calculate_step_duration()
        return step_duration_ms * steps

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
        if self.timer and self.timer.isActive():
            ms_per_step = milliseconds_per_note(bpm)
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
            bpm = int(SECONDS_PER_MINUTE / avg_interval)
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
        """Set the pattern tempo in BPM using mido."""
        self.timing_bpm = bpm
        # Calculate microseconds per beat
        microseconds_per_beat = int(MidiTempo.MICROSECONDS_PER_MINUTE / bpm)

        # Create a set_tempo MetaMessage
        tempo_message = MetaMessage(
            MidoMessageType.SET_TEMPO, tempo=microseconds_per_beat
        )

        # Add the tempo message to the first track
        if self.midi_file.tracks:
            self.midi_file.tracks[0].insert(0, tempo_message)

        # Update playback speed if sequence is running
        if hasattr(self, "timer") and self.timer and self.timer.isActive():
            ms_per_step = milliseconds_per_note(bpm)  # ms per 16th note
            self.timer.setInterval(int(ms_per_step))

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

        track.append(MetaMessage("set_tempo", tempo=bpm2tempo(self.timing_bpm)))
        track.append(MetaMessage("time_signature", numerator=4, denominator=4))

        events = []

        for measure_index, measure in enumerate(self.measure_widgets):
            for step in range(MeasureBeats.PER_MEASURE_4_4):
                absolute_tick = (
                        measure_index * ticks_per_bar
                        + step * ticks_per_step
                )

                for row in range(self.sequencer_rows):
                    channel = self.get_channel_for_row(row)
                    button = measure.buttons[row][step]
                    spec = get_button_note_spec(button)

                    if button.isChecked() and spec.is_active:
                        events.append((
                            absolute_tick,
                            Message(
                                MidoMessageType.NOTE_ON,
                                note=spec.note,
                                velocity=spec.velocity,
                                time=0,
                                channel=channel,
                            ),
                        ))

                        events.append((
                            absolute_tick + ticks_per_step,
                            Message(
                                MidoMessageType.NOTE_OFF,
                                note=spec.note,
                                velocity=spec.velocity,
                                time=0,
                                channel=channel,
                            ),
                        ))

        # Sort events by absolute time
        events.sort(key=lambda e: e[0])

        convert_absolute_time_to_delta_time(events, track)

    def get_channel_for_row(self, row: int) -> int:
        """Get idi channel for each row"""
        channel = row if row < 3 else 9
        return channel

    def set_midi_file_editor(self, midi_file_editor: Any) -> None:
        """
        Set reference to MidiFileEditor for shared MIDI file editing.

        :param midi_file_editor: MidiFileEditor instance
        """
        self.midi_file_editor = midi_file_editor
        # --- If MidiFileEditor already has a loaded file, load it
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
        """Load pattern from a MidiFile object (internal method)."""
        try:
            ppq = midi_file.ticks_per_beat
            beats_per_bar = 4
            ticks_per_bar = ppq * beats_per_bar

            # --- Detect number of bars
            num_bars = self._detect_bars_from_midi(midi_file)
            log.message(
                message=f"Detected {num_bars} bars in MIDI file",
                scope=self.__class__.__name__,
            )

            self._clear_measures_and_measures_list()

            self._create_new_measures(num_bars)

            self.total_measures = len(self.measure_widgets)
            self._update_pattern_length()

            notes_loaded = self._load_notes_from_tracks_to_channels(midi_file, ticks_per_bar)

            self._update_spinbox_from_file_tempo(midi_file)

            self._select_first_measure_and_sync(notes_loaded)
        except Exception as ex:
            log.error(
                message=f"Error loading from MidiFileEditor: {ex}",
                scope=self.__class__.__name__,
            )
            import traceback

            log.debug(traceback.format_exc())

    def _create_new_measures(self, num_bars: int):
        """Create new bars"""
        for measure_num in range(num_bars):
            measure = PatternMeasureWidget()
            reset_measure(measure)
            self.measure_widgets.append(measure)
            item = QListWidgetItem(f"measure {measure_num + 1}")
            item.setData(Qt.ItemDataRole.UserRole, measure_num)
            self.measures_list.addItem(item)

    def _load_notes_from_tracks_to_channels(self, midi_file: MidiFile, ticks_per_bar: int) -> int:
        """Load notes from all tracks, mapping by MIDI channel"""
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

                    while bar_index >= len(self.measure_widgets):
                        measure = PatternMeasureWidget()
                        reset_measure(measure)
                        self.measure_widgets.append(measure)
                        item = QListWidgetItem(
                            f"{self.measure_name} {len(self.measure_widgets)}"
                        )
                        item.setData(
                            Qt.ItemDataRole.UserRole, len(self.measure_widgets) - 1
                        )
                        self.measures_list.addItem(item)

                    if bar_index < len(self.measure_widgets) and step_in_bar < 16:
                        measure = self.measure_widgets[bar_index]
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
        return notes_loaded

    def _select_first_measure_and_sync(self, notes_loaded: int):
        # Select first bar and sync
        if self.measures_list.count() > 0:
            self.current_measure_index = 0
            self.measures_list.setCurrentRow(0)
            self._sync_sequencer_with_measure(0)
            log.message(
                message=f"Loaded {notes_loaded} notes from MidiFileEditor's MIDI file in {len(self.measure_widgets)} bars",
                scope=self.__class__.__name__,
            )
        else:
            log.warning(
                message="No bars were created from MIDI file",
                scope=self.__class__.__name__,
            )

    def _update_spinbox_from_file_tempo(self, midi_file: MidiFile):
        """update spinbox from file tempo"""
        tempo_bpm = None
        for track in midi_file.tracks:
            for event in track:
                if event.type == MidoMessageType.SET_TEMPO:
                    tempo_bpm = int(tempo2bpm(event.tempo))
                    break
            if tempo_bpm is not None:
                break
        if tempo_bpm is not None:
            set_spinbox_value(self.tempo_spinbox, tempo_bpm)
            self.set_tempo(tempo_bpm)

    def _clear_measures_and_measures_list(self):
        """Clear existing bars and bars list"""
        self.measures_list.clear()
        self.measure_widgets.clear()

    def save_pattern(self, filename: str):
        """Save the current pattern to a MIDI file using mido."""
        midi_file = MidiFile()

        self._create_tracks_per_row(midi_file)

        self._save_midi_file(filename, midi_file)

        self._update_midi_file_editor_with_file(filename)

    def _create_tracks_per_row(self, midi_file: MidiFile):
        """Create tracks for each row"""
        for row in range(self.sequencer_rows):
            track = MidiTrack()
            midi_file.tracks.append(track)

            # Add track name and program change
            track.append(Message(MidoMessageType.PROGRAM_CHANGE, program=0, time=0))

            self._add_motes_from_all_bars_to_track(row, track)

    def _add_motes_from_all_bars_to_track(self, row: int, track: MidiTrack[Any]):
        """Add notes from all bars to the track"""
        for bar_index, measure in enumerate(self.measure_widgets):
            for step in range(MeasureBeats.PER_MEASURE_4_4):
                if step < len(measure.buttons[row]):
                    measure_button = measure.buttons[row][step]
                    spec = get_button_note_spec(measure_button)
                    if measure_button.isChecked() and spec.is_active:
                        time = self._calculate_note_on_time(bar_index, step)
                        self._append_note_on_and_off(spec, time, track)

    def _calculate_note_on_time(self, bar_index: int, step: int) -> int:
        """Calculate the time for the note_on event (across all bars)"""
        ppq = self.midi_file.ticks_per_beat
        ticks_per_step = ppq // 4  # 16th note
        steps_per_bar = self.measure_beats

        global_step = bar_index * steps_per_bar + step
        return global_step * ticks_per_step

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

    def _append_note_on_and_off(self, spec: NoteButtonSpec, time: int, track: MidiTrack):
        """Append Note on and Off"""
        track.append(
            Message(
                MidoMessageType.NOTE_ON,
                note=spec.note,
                velocity=spec.velocity,
                time=time,
            )
        )
        # Add a note_off event after a short duration
        track.append(
            Message(
                MidoMessageType.NOTE_OFF,
                note=spec.note,
                velocity=0,
                time=time + 120,
            )
        )

    def clear_pattern(self):
        """Clear the current bar's pattern, resetting all steps in the selected bar."""
        if self.current_measure_index < len(self.measure_widgets):
            measure = self.measure_widgets[self.current_measure_index]
            for row in range(self.sequencer_rows):
                for step in range(MeasureBeats.PER_MEASURE_4_4):
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
            num_measures = self._detect_bars_from_midi(midi_file)
            log.message(
                message=f"Detected {num_measures} bars in MIDI file",
                scope=self.__class__.__name__,
            )

            self._clear_measures_and_measures_list()

            # Create new bars without selecting them (to avoid UI flicker)
            for bar_num in range(num_measures):
                measure = PatternMeasureWidget()
                reset_measure(measure)
                self.measure_widgets.append(measure)

                # Add to bars list
                item = QListWidgetItem(f"{self.measure_name} {bar_num + 1}")
                item.setData(Qt.ItemDataRole.UserRole, bar_num)  # Store bar index
                self.measures_list.addItem(item)

            # Update total measures
            self.total_measures = len(self.measure_widgets)
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

            note_events = self._collect_notes_with_times_and_tempos_from_file(midi_file)

            note_durations = self._collect_note_on_and_off_to_calculate_durations(note_events, ppq)

            self._assign_notes_and_durations_to_buttons(channel_to_row,
                                                        note_durations,
                                                        note_events,
                                                        notes_loaded,
                                                        ppq,
                                                        ticks_per_bar)

            self._update_spinbox_from_file_tempo(midi_file)

            self._set_to_first_measure(num_measures)

        except Exception as ex:
            log.error(
                message=f"Error loading pattern: {ex}", scope=self.__class__.__name__
            )
            QMessageBox.critical(self, "Error", f"Could not load pattern: {str(ex)}")

    def _set_to_first_measure(self, num_bars: int):
        """Select first bar and sync sequencer"""
        if self.measures_list.count() > 0:
            self.current_measure_index = 0
            self.measures_list.setCurrentRow(0)
            self._sync_sequencer_with_measure(0)
            log.message(
                message=f"Loaded {num_bars} bars from MIDI file. Bars are displayed in the side panel.",
                scope=self.__class__.__name__,
            )

    def _assign_notes_and_durations_to_buttons(self,
                                               channel_to_row: dict[MidiChannel, int],
                                               note_durations: dict[Any, Any],
                                               note_events: list[Any],
                                               notes_loaded: int,
                                               ppq: int,
                                               ticks_per_bar: int):
        """Third pass: assign notes and durations to buttons"""
        for abs_time, msg, channel, tempo in note_events:
            if msg.type == MidoMessageType.NOTE_ON and msg.velocity > 0:
                # --- Map channel to row (skip channels we don't support)
                if channel not in channel_to_row:
                    continue

                row = channel_to_row[channel]

                # Calculate which bar and step this note belongs to
                bar_index = int(abs_time / ticks_per_bar)
                step_in_bar = int((abs_time % ticks_per_bar) / (ticks_per_bar / 16))

                # Ensure we have enough bars (safety check)
                while bar_index >= len(self.measure_widgets):
                    measure = PatternMeasureWidget()
                    reset_measure(measure)
                    self.measure_widgets.append(measure)
                    item = QListWidgetItem(
                        f"[{self.measure_name} {len(self.measure_widgets)}"
                    )
                    item.setData(Qt.ItemDataRole.UserRole, len(self.measure_widgets) - 1)
                    self.measures_list.addItem(item)

                if bar_index < len(self.measure_widgets) and step_in_bar < 16:
                    measure = self.measure_widgets[bar_index]
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

    def _collect_note_on_and_off_to_calculate_durations(self, note_events: list[Any], ppq: int) -> dict[Any, Any]:
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
        return note_durations

    def _collect_notes_with_times_and_tempos_from_file(self, midi_file: MidiFile) -> list[Any]:
        """First pass: collect all note events with their absolute times and tempos"""
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
        return note_events

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

    def _pattern_transport_play(self) -> None:
        """Start pattern playback (delegate to play_pattern)."""
        self.play_pattern()

    def _pattern_transport_stop(self) -> None:
        """Stop pattern playback (delegate to stop_pattern)."""
        self.stop_pattern()

    def _pattern_transport_pause_toggle(self) -> None:
        """Pause or resume pattern playback."""
        if self._pattern_paused:
            # Resume: restart engine from current position, then restart timer.
            # Must call engine.start(current_tick) to reset _start_time so process_until_now
            # does not think a long pause elapsed (which would cause a burst of notes).
            if hasattr(self, "playback_engine") and self.playback_engine:
                events = self.playback_engine.events
                idx = self.playback_engine.event_index
                if events and idx < len(events):
                    current_tick = events[idx].absolute_tick
                else:
                    current_tick = self.playback_engine.start_tick
                self.playback_engine.start(current_tick)
            if hasattr(self, "timer") and self.timer and not self.timer.isActive():
                playback_interval_ms = 20
                self.timer.start(playback_interval_ms)
            self._pattern_paused = False
            log.message(
                message="Pattern playback resumed", scope=self.__class__.__name__
            )
        else:
            # Pause: stop timer and pause engine so no events advance during pause.
            if hasattr(self, "timer") and self.timer and self.timer.isActive():
                self.timer.stop()
            if hasattr(self, "playback_engine") and self.playback_engine:
                self.playback_engine.pause()
            self._pattern_paused = True
            log.message(
                message="Pattern playback paused", scope=self.__class__.__name__
            )

    def _pattern_shuffle_play(self) -> None:
        """Select a random bar and start playback."""
        if not self.measure_widgets:
            return
        idx = random.randint(0, len(self.measure_widgets) - 1)
        self.current_measure_index = idx
        if self.measures_list and idx < self.measures_list.count():
            self.measures_list.setCurrentRow(idx)
        self._sync_sequencer_with_measure(idx)
        self.play_pattern()

    def _ms_to_ticks(self, duration_ms: int, ticks_per_beat: int) -> int:
        """
        Convert milliseconds to MIDI ticks.
        1 beat = 60000 / bpm ms = ticks_per_beat ticks
        """
        if duration_ms <= 0:
            return 0

        ticks = duration_ms * self.timing_bpm * ticks_per_beat / MidiTempo.MILLISECONDS_PER_MINUTE
        return max(1, int(ticks))

    def _collect_sequencer_events(self, ticks_per_beat: int) -> list[SequencerEvent]:
        """collect sequencer events"""
        ticks_per_step = ticks_per_beat // 4  # 16th
        events: list[SequencerEvent] = []

        for bar_index, measure in enumerate(self.measure_widgets):
            for step in range(min(self.measure_beats, 16)):

                tick = (bar_index * self.measure_beats + step) * ticks_per_step

                for row in range(self.sequencer_rows):
                    if step >= len(measure.buttons[row]):
                        continue

                    if row in self.muted_channels:
                        continue

                    btn = measure.buttons[row][step]
                    if not btn.isChecked():
                        continue
                    spec = get_button_note_spec(btn)

                    if not spec.is_active:
                        continue

                    channel = self.get_channel_for_row(row)
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
        ticks_per_beat = PPQ
        tempo_us = int(MidiTempo.MICROSECONDS_PER_MINUTE / self.timing_bpm)

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
        events = []

        for absolute_tick in seq_events:
            events.append(
                (
                    absolute_tick.tick,
                    Message(
                        MidoMessageType.NOTE_ON,
                        note=absolute_tick.note,
                        velocity=absolute_tick.velocity,
                        channel=absolute_tick.channel,
                        time=0,
                    ),
                )
            )
            events.append(
                (
                    absolute_tick.tick + absolute_tick.duration_ticks,
                    Message(
                        MidoMessageType.NOTE_OFF,
                        note=absolute_tick.note,
                        velocity=0,
                        channel=absolute_tick.channel,
                        time=0,
                    ),
                )
            )

        events.sort(key=lambda x: x[0])

        prev_tick = 0
        for tick, msg in events:
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
        """Start playing the pattern via PlaybackEngine."""
        if hasattr(self, "timer") and self.timer and self.timer.isActive():
            return  # Already playing
        if not self.measure_widgets:
            return

        mid = self._build_midi_file_for_playback()
        # Engine needs at least one note event to be useful
        if len(mid.tracks[0]) <= 1:
            log.message(
                message="Pattern has no notes to play", scope=self.__class__.__name__
            )
            return

        self.playback_engine.load_file(mid)
        for ch in range(MeasureBeats.PER_MEASURE_4_4):
            self.playback_engine.mute_channel(ch, ch in self.muted_channels)
        if self.midi_helper:
            self.playback_engine.on_event = (
                lambda msg: self.midi_helper.send_raw_message(msg.bytes())
            )
        self.playback_engine.start(0)
        self._playback_last_bar_index = -1
        self._playback_last_step_in_bar = -1

        # Use a short, precise interval so process_until_now() runs often; the engine
        # sends events by wall-clock time, so this reduces stutter from timer jitter.
        playback_interval_ms = 20
        self.timer = QTimer(self)
        self.timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.timer.timeout.connect(self._on_playback_tick)
        self.timer.start(playback_interval_ms)

        if hasattr(self, "play_button") and self.play_button:
            update_button_state(
                self.play_button, checked_state=True, enabled_state=False
            )
        if hasattr(self, "stop_button") and self.stop_button:
            update_button_state(
                self.stop_button, checked_state=False, enabled_state=True
            )

        log.message(message="Pattern playback started", scope=self.__class__.__name__)

    def _on_playback_tick(self):
        """Drive PlaybackEngine and sync UI to current position."""
        self.playback_engine.process_until_now()
        # Sync bar/step highlight from engine position
        if self.playback_engine.events:
            idx = self.playback_engine.event_index
            if idx > 0 and idx <= len(self.playback_engine.events):
                tick = self.playback_engine.events[idx - 1].absolute_tick
            else:
                tick = self.playback_engine.start_tick
        else:
            tick = 0
        ticks_per_step = PPQ // 4
        total_steps = len(self.measure_widgets) * self.measure_beats if self.measure_widgets else 0
        global_step = (tick // ticks_per_step) % total_steps if total_steps > 0 else 0
        self.current_step = global_step
        bar_index = global_step // self.measure_beats
        step_in_bar = global_step % self.measure_beats
        last_bar = getattr(self, "_playback_last_bar_index", -1)
        last_step = getattr(self, "_playback_last_step_in_bar", -1)

        if bar_index < len(self.measure_widgets):
            self.current_measure_index = bar_index
            self._sync_sequencer_on_step_change(bar_index, last_bar)
            # Only update step highlight when the current step changes (at most 2 columns)
            if step_in_bar != last_step:
                n_cols = len(self.buttons[0]) if self.buttons else 0
                for row in range(self.sequencer_rows):
                    if 0 <= last_step < len(self.buttons[row]):
                        btn = self.buttons[row][last_step]
                        is_current = False
                        set_sequencer_style(btn=btn, is_current=is_current, checked=btn.isChecked())
                    if step_in_bar < len(self.buttons[row]):
                        btn = self.buttons[row][step_in_bar]
                        is_current = True
                        set_sequencer_style(btn=btn, is_current=is_current, checked=btn.isChecked())
                self._playback_last_step_in_bar = step_in_bar

        if self.playback_engine.state == TransportState.STOPPED:
            self._apply_transport_state(TransportState.STOPPED)
            log.message(
                message="Pattern playback finished", scope=self.__class__.__name__
            )

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

    def _update_transport_ui(self):
        """update ui regarding playing state"""
        state = TransportState.STOPPED
        self.update_transport_buttons(state)

    def _sync_ui_to_stopped(self) -> None:
        """Sync UI to stopped state: stop timer, update play/stop buttons."""
        if hasattr(self, "timer") and self.timer:
            self.timer.stop()
            self.timer = None
        self._pattern_paused = False
        self._apply_transport_state(TransportState.STOPPED)

    def stop_pattern(self):
        """Stop playing the pattern"""
        self.playback_engine.stop()
        self._sync_ui_to_stopped()

        # Reset step counter
        self.current_step = 0

        # Send all notes off
        if self.midi_helper:
            for channel in range(MeasureBeats.PER_MEASURE_4_4):
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
        measure_beats = self.measure_beats
        total_pattern_beats = len(self.measure_widgets) * self.measure_beats
        global_step = (
            self.current_step % total_pattern_beats if total_pattern_beats > 0 else 0
        )
        measure_index = global_step // measure_beats
        step_in_measure = global_step % measure_beats

        log.message(
            message=f"Playing step {step_in_measure} in bar {measure_index + 1} "
                    f"(global step {global_step}"
                    f" {self.measure_beats} beats per bar)",
            scope=self.__class__.__name__,
        )

        # Sync sequencer with the current bar being played
        if measure_index < len(self.measure_widgets):
            self.current_measure_index = measure_index
            self._sync_sequencer_with_measure(measure_index)

            # Highlight the current bar in the bars list
            if measure_index < self.measures_list.count():
                self.measures_list.setCurrentRow(measure_index)
                # Ensure the item is visible (scroll to it if needed)
                item = self.measures_list.item(measure_index)
                if item:
                    self.measures_list.scrollToItem(item)

            self._play_notes_from_current_measure(measure_index, step_in_measure)

        self._advance_to_next_step()

        self._update_ui_for_current_step(step_in_measure)

    def _update_ui_for_current_step(self, step_in_measure: int):
        """Update UI to show current step"""
        for row in range(self.sequencer_rows):
            for col in range(MeasureBeats.PER_MEASURE_4_4):  # Always 16 steps in sequencer
                if col < len(self.buttons[row]):
                    button = self.buttons[row][col]
                    is_checked = button.isChecked()
                    is_current = (
                            step_in_measure == col
                    )  # Current step within the displayed bar
                    button.setStyleSheet(
                        JDXi.UI.Style.generate_sequencer_button_style(
                            is_checked, is_current, is_selected_bar=True
                        )
                    )

    def _advance_to_next_step(self):
        """Advance to next step (across all measures)"""
        measure_beats = self.measure_beats
        total_pattern_beats = len(self.measure_widgets) * measure_beats
        self.current_step = (
            (self.current_step + 1) % total_pattern_beats
            if total_pattern_beats > 0
            else 0
        )

    def _play_notes_from_current_measure(self, measure_index: int, step_in_measure: int):
        """Play notes from the current measure"""
        measure = self.measure_widgets[measure_index]
        for row in range(self.sequencer_rows):
            if step_in_measure < len(measure.buttons[row]):
                measure_button = measure.buttons[row][step_in_measure]
                play_spec = get_button_note_spec(measure_button)
                if measure_button.isChecked() and play_spec.is_active:
                    # Determine channel based on row
                    channel = self.get_channel_for_row(row)

                    # Send Note On message using the stored note
                    if self.midi_helper:
                        if channel not in self.muted_channels:
                            log.message(
                                message=f"Row {row} active at step {step_in_measure} in bar {measure_index + 1}, sending note {play_spec.note} on channel {channel}",
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
                                    (float(MidiTempo.MILLISECONDS_PER_MINUTE) / self.timing_bpm) / 4.0
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

    def _learn_pattern(self, message):
        """Learn the pattern of incoming MIDI notes, preserving rests."""
        if message.type == MidoMessageType.NOTE_ON and message.velocity > 0:
            note = message.note  # mido uses lowercase 'note'

            # Determine the correct row for the note
            for row in range(self.sequencer_rows):
                if note in self._get_note_range_for_row(row):
                    # Calculate step within current bar (0 to beats_per_bar-1)
                    step_in_bar = self.current_step % self.measure_beats

                    # Store note in the current bar's measure
                    if self.current_measure_index < len(self.measure_widgets):
                        measure = self.measure_widgets[self.current_measure_index]
                        if step_in_bar < len(measure.buttons[row]):
                            measure_button = measure.buttons[row][step_in_bar]
                            update_button_state(measure_button, True)
                            measure_button.note = note
                            # Store velocity from MIDI input
                            measure_button.note_velocity = message.velocity
                            # Set default duration for MIDI-learned notes
                            measure_button.note_duration = self._get_duration_ms()
                            sync_button_note_spec(measure_button)

                            # Also update sequencer digital
                            if step_in_bar < len(self.buttons[row]):
                                seq_btn = self.buttons[row][step_in_bar]
                                update_button_state(seq_btn, True)
                                seq_btn.note = note
                                seq_btn.note_velocity = message.velocity
                                seq_btn.note_duration = self._get_duration_ms()
                                sync_button_note_spec(seq_btn)

                    # Record the note in the learned pattern (for compatibility)
                    self.learned_pattern[row][step_in_bar] = note
                    self.active_notes[note] = row  # Mark the note as active

                    # Add the note_on message to the MIDI track
                    self.midi_track.append(
                        Message(
                            MidoMessageType.NOTE_ON,
                            note=note,
                            velocity=message.velocity,
                            time=0,
                        )
                    )
                    break  # Stop checking once the note is assigned

        elif message.type == MidoMessageType.NOTE_OFF:
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
                    Message(MidoMessageType.NOTE_OFF, note=note, velocity=0, time=0)
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
                    button.note_duration = self._get_duration_ms()
                    # Set default velocity for learned pattern notes
                    button.note_velocity = self.velocity_spinbox.value()
                    sync_button_note_spec(button)
                    button.setStyleSheet(
                        JDXi.UI.Style.generate_sequencer_button_style(True)
                    )
                    self._update_tooltip(row, button)

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
        channel = self.get_channel_for_row(row)
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
        # Ensure UI updates properly
        self.update()
