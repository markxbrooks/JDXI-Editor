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
from mido import MidiFile, MidiTrack
from PySide6.QtCore import QEvent, Qt, QTimer
from PySide6.QtWidgets import (
    QAbstractButton,
    QCheckBox,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QSplitter,
)

from jdxi_editor.midi.channel.channel import MidiChannel
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.playback.state import MidiPlaybackState
from jdxi_editor.ui.style.editor_style import mark_editor_body
from jdxi_editor.ui.common import JDXi, QVBoxLayout, QWidget
from jdxi_editor.ui.editors.helpers.widgets import (
    create_panel,
    create_round_button_with_label,
    create_jdxi_button,
    create_jdxi_button_from_spec,
    create_jdxi_button_with_label_from_spec,
    create_jdxi_row,
)
from jdxi_editor.ui.editors.pattern.models import ClipboardData, SequencerStyle
from jdxi_editor.ui.editors.pattern.options import DIGITAL_OPTIONS, DRUM_OPTIONS
from jdxi_editor.ui.editors.pattern.preset_list_provider import (
    get_analog_options,
    get_digital_options,
    get_drum_options,
    get_preset_signals,
)
from jdxi_editor.ui.editors.pattern.spec import SequencerRowSpec
from jdxi_editor.ui.editors.synth.editor import SynthEditor
from jdxi_editor.ui.preset.helper import JDXiPresetHelper
from jdxi_editor.ui.widgets.digital.title import DigitalTitle
from jdxi_editor.ui.widgets.editor.base import EditorBaseWidget
from jdxi_editor.ui.widgets.editor.helper import create_group_with_layout
from jdxi_editor.ui.widgets.pattern_file_group import PatternFileGroup
from jdxi_editor.ui.widgets.transport.transport import PatternTransportWidget
from jdxi_editor.ui.widgets.pattern.measure_widget import ROW_SPACING, PatternMeasureWidget
from jdxi_editor.ui.widgets.pattern.sequencer_button import SequencerButton
from jdxi_editor.ui.widgets.pattern.widget import PatternConfig, PatternWidget
from jdxi_editor.ui.style import JDXiUIDimensions
from jdxi_editor.ui.widgets.usb.recording import USBFileRecordingWidget
from picoui.helpers import create_layout_with_items
from picoui.helpers.spinbox import spinbox_with_label_from_spec
from picoui.specs.widgets import ButtonSpec, ComboBoxSpec, SpinBoxSpec
from picoui.widget.helper import create_combo_box


def _combo_spec(items, tooltip: str = "") -> ComboBoxSpec:
    """Build ComboBoxSpec with items list, no slot."""
    return ComboBoxSpec(items=list(items), tooltip=tooltip, slot=None)


_EXPANDING = (QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)


class PatternUI(SynthEditor):
    """Pattern Sequencer with MIDI Integration using mido"""

    def __init__(
        self,
        midi_helper: Optional[MidiIOHelper],
        preset_helper: Optional[JDXiPresetHelper],
        parent: Optional[QWidget] = None,
        midi_file_editor: Optional[Any] = None,
    ):
        super().__init__(parent=parent)
        self.paste_button: QPushButton | None = None
        self.pause_button: QPushButton | None = None
        self.stop_button: QPushButton | None = None
        self.play_button: QPushButton | None = None
        self.channel_to_row = {
            MidiChannel.DIGITAL_SYNTH_1: 0,  # Channel 0
            MidiChannel.DIGITAL_SYNTH_2: 1,  # Channel 1
            MidiChannel.ANALOG_SYNTH: 2,  # Channel 2
            MidiChannel.DRUM_KIT: 3,  # Channel 9
        }
        self.row_labels = [
            "Digital Synth 1",
            "Digital Synth 2",
            "Analog Synth",
            "Drums",
        ]
        self._build_row_specs()
        self.sequencer_rows: int = 4
        # Use Qt translations: add .ts/.qm for locale (e.g. en_GB "Measure" -> "Measure", "Measures" -> "Measures")
        self.measure_name: str = self.tr("Measure")
        self.measure_name_plural: str = self.tr("Measures")
        self.muted_channels: list[int] = []
        self.total_measures: int = 1  # Start with 1 bar by default
        self.midi_helper: Optional[MidiIOHelper] = midi_helper
        self.preset_helper: Optional[JDXiPresetHelper] = preset_helper
        self.midi_file_editor: Optional[Any] = (
            midi_file_editor  # Reference to MidiFileEditor
        )
        self.measure_beats: int = 16  # Number of beats per bar (16 or 12)
        self.pattern_widget: Optional[PatternWidget] = None  # Set in _setup_ui
        self.timer: Optional[QTimer] = None
        self.current_step: int = 0  # Currently selected step (0-indexed)
        self.total_steps: int = (
            16  # Always 16 steps per measure (don't multiply by measures)
        )
        self.clipboard: Optional[dict[str, Any]] | None = (
            None  # Store copied notes: {source_bar, rows, start_step, end_step, notes_data}
        )
        self.beats_per_pattern: int = 4
        self.timing_bpm: int = 120
        self.last_tap_time: Optional[datetime] = None
        self.tap_times: list[float] = []
        self.midi_file: Optional[MidiFile] = (
            None  # Set in _setup_ui from MidiFileController
        )
        self.midi_track: Optional[MidiTrack] = (
            None  # Set in _setup_ui from MidiFileController
        )
        self.clipboard: Optional[dict[str, Any]] | None = (
            None  # Store copied notes: {source_measure, rows, start_step, end_step, notes_data}
        )
        self._pattern_paused: bool = False
        self.midi_state: MidiPlaybackState = MidiPlaybackState()
        self.usb_recorder = USBFileRecordingWidget(self.midi_state)
        self._setup_ui()
        self._apply_pattern_editor_style()

    def _apply_pattern_editor_style(self) -> None:
        """Player-aligned chrome: grey GroupBoxes; accent only when active."""
        mark_editor_body(self)
        self.setStyleSheet(JDXi.UI.PatternEditor.editor_stylesheet())

    def _build_row_specs(self):
        """build row specs"""
        self.row_specs: list[SequencerRowSpec] = [
            SequencerRowSpec(
                "Digital Synth 1", JDXi.UI.Icon.PIANO, SequencerStyle.DIGITAL
            ),
            SequencerRowSpec(
                "Digital Synth 2", JDXi.UI.Icon.PIANO, SequencerStyle.DIGITAL_2
            ),
            SequencerRowSpec(
                "Analog Synth", JDXi.UI.Icon.PIANO, SequencerStyle.ANALOG
            ),
            SequencerRowSpec("Drums", JDXi.UI.Icon.DRUM, SequencerStyle.DRUMS),
        ]

    def showEvent(self, event: QEvent) -> None:
        """Refresh preset options when shown (e.g. after MIDI config change)."""
        super().showEvent(event)
        self._refresh_preset_options()

    def _refresh_preset_options(self) -> None:
        """Reload options from provider and update combo boxes if changed."""
        new_digital = get_digital_options()
        new_analog = get_analog_options()
        new_drum = get_drum_options()
        if (
            new_digital != self.digital_options
            or new_analog != self.analog_options
            or new_drum != self.drum_options
        ):
            self.digital_options = new_digital
            self.analog_options = new_analog
            self.drum_options = new_drum
            self._reload_combo_options()

    def _setup_ui(self):
        """Use EditorBaseWidget for consistent scrollable layout structure"""
        self._init_base_widget()

        # Create content widget with main layout
        content_widget = QWidget()
        self.layout = QVBoxLayout(content_widget)
        self.mute_buttons = []  # List to store mute buttons

        # Define synth options (from built-in or SoundFont via MIDI config)
        self.digital_options = get_digital_options()
        self.analog_options = get_analog_options()
        self.drum_options = get_drum_options()
        
        # Connect to preset list change signal for dynamic refresh
        get_preset_signals().soundfont_list_changed.connect(self._refresh_preset_options)

        # Assemble all specs for buttons and combos (used below)
        self.specs = self._build_specs()

        self.pattern_file_group = PatternFileGroup(parent=self)
        self.drum_selector = self.pattern_file_group.drum_selector

        learn_group = self._create_learn_group()
        # not adding this for now

        # Compact lines above the grid:
        #   ▶ Play  ■ Stop  ❙❙ Pause  ⤮ Shuffle                Load  Save    Clear…
        #   BPM [120] Tap · Steps [16] · Vel [100] · Dur [16th]      [USB Recorder]
        #   + Add Measure  ☐ Copy previous  ·  Steps [1] to [16]  Copy  Paste
        self.pattern_transport = PatternTransportWidget(parent=self)
        self.play_button = self.pattern_transport.play_button
        self.stop_button = self.pattern_transport.stop_button
        self.pause_button = self.pattern_transport.pause_button
        self.shuffle_button = self.pattern_transport.shuffle_button
        transport_row = QHBoxLayout()
        transport_row.addWidget(self.pattern_transport)
        transport_row.addStretch()
        transport_row.addWidget(self.pattern_file_group)

        # Display at the left of the three lines, as in the MIDI File Player:
        # tempo (and bar.step while playing) above, the pattern's file below
        self.digital_title = DigitalTitle(tone_name="New pattern", show_upper_text=True)
        rows = QVBoxLayout()
        rows.addLayout(transport_row)
        rows.addLayout(self._create_toolbar_row())
        rows.addLayout(self._create_edit_row())
        header = QHBoxLayout()
        header.setSpacing(JDXi.UI.PatternEditor.SPACING_GROUP)
        header.addWidget(self.digital_title, 0, Qt.AlignmentFlag.AlignTop)
        header.addLayout(rows, 1)
        # USB Recorder: shown on demand (recording works while it is hidden)
        self.usb_recorder.setVisible(False)
        # Two glossy panels, as in the MIDI File Player: the controls (the
        # Transport, Pattern and USB groups draw as sections on it) and the
        # sequencer (measure strip and steps)
        self.layout.addWidget(create_panel(header, self.usb_recorder))

        # Create splitter for measures list and sequencer (builds measures group + sequencer widget)
        self._build_splitter_section()

        self.row_map = {
            0: self.digital1_selector,
            1: self.digital2_selector,
            2: self.analog_selector,
            3: self.drum_selector,
        }

        self.layout.addStretch()

        # Add content to scrollable area so the widget tree is retained
        self._container_layout.addWidget(content_widget)

    def _build_splitter_section(self):
        """Build splitter section with PatternWidget (measures list + sequencer)."""
        self.pattern_widget = PatternWidget(
            config=PatternConfig(
                rows=4, steps_per_measure=self.measure_beats, initial_measures=1
            )
        )
        self.pattern_widget.set_header_widget(self._create_headers_widget())
        self.layout.addWidget(create_panel(self.pattern_widget))

    def _create_headers_widget(self) -> QWidget:
        """
        Row headers beside the step grid: one per part, as tall as its row.

            [icon] Digital Synth 1  [C4 ▾] [mute]
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(ROW_SPACING)
        for row_idx, label in enumerate(self.row_labels):
            layout.addWidget(self._create_header_row(row_idx, label))
        return widget

    def _create_header_row(self, row_idx: int, label_text: str) -> QWidget:
        """One part's header: icon, name, note for new steps, mute."""
        mp = JDXi.UI.PatternEditor
        row = QWidget()
        row.setFixedHeight(JDXiUIDimensions.SEQUENCER.LARGE_SQUARE_SIZE)
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(mp.SPACING_RELATED)

        color = self.row_specs[row_idx].accent_color
        icon_label = QLabel()
        icon_label.setPixmap(
            JDXi.UI.Icon.get_icon(self.row_specs[row_idx].icon, color=color).pixmap(
                mp.TRACK_ICON_SIZE + 4, mp.TRACK_ICON_SIZE + 4
            )
        )
        row_layout.addWidget(icon_label)

        label = QLabel(label_text)
        label.setFixedWidth(110)
        label.setStyleSheet(self._get_row_label_style(row_idx))
        row_layout.addWidget(label)

        selector = self._create_selector_for_row(row_idx)
        if selector:
            selector.setFixedWidth(84)
            selector.setToolTip(
                "Drum sound for new steps" if row_idx == 3 else "Note for new steps"
            )
            row_layout.addWidget(selector)

        mute_btn = QPushButton()
        mute_btn.setIcon(
            JDXi.UI.Icon.get_icon(JDXi.UI.Icon.MUTE, color=JDXi.UI.Style.FOREGROUND)
        )
        mute_btn.setToolTip(f"Mute {label_text}")
        mute_btn.setCheckable(True)
        size = JDXi.UI.Style.BUTTON_TRACK_WIDTH + 6
        mute_btn.setFixedSize(size, size)
        mute_btn.setStyleSheet(mp.track_toggle_stylesheet(mp.ACCENT))
        mute_btn.toggled.connect(
            lambda checked, r=row_idx: self._toggle_mute(r, checked)
        )
        self.mute_buttons.append(mute_btn)
        row_layout.addWidget(mute_btn)
        return row

    def _get_row_label_style(self, row_idx: int) -> str:
        spec = self.row_specs[row_idx]
        return SequencerStyle.row_label(spec.accent_color)

    def _create_selector_for_row(self, row_idx: int):
        """Create and return the combo selector for this row; assign to self for channel_map / _update_combo_boxes."""
        if row_idx == 0:
            self.digital1_selector = create_combo_box(
                spec=self.specs["combos"]["digital1"]
            )
            return self.digital1_selector
        if row_idx == 1:
            self.digital2_selector = create_combo_box(
                spec=self.specs["combos"]["digital2"]
            )
            return self.digital2_selector
        if row_idx == 2:
            self.analog_selector = create_combo_box(spec=self.specs["combos"]["analog"])
            return self.analog_selector
        if row_idx == 3:
            return self.drum_selector
        return None

    def _build_top_controls(self):
        self.content_widget = QWidget()
        self.layout = QVBoxLayout(self.content_widget)

        control_panel = QHBoxLayout()

        measure_group = self._create_measure_group()
        tempo_group = self._create_tempo_group()
        beats_group = self._create_beats_group()
        velocity_group = self._create_velocity_group()
        duration_group = self._create_duration_group()

        for group in (
            measure_group,
            tempo_group,
            beats_group,
            velocity_group,
            duration_group,
        ):
            control_panel.addWidget(group)

        self.layout.addLayout(control_panel)

    def _init_base_widget(self):
        """init base widget"""
        self.base_widget = EditorBaseWidget(parent=self, analog=False)
        self.base_widget.setup_scrollable_content()
        self._container_layout = self.base_widget.get_container_layout()

        if not hasattr(self, "main_layout") or self.main_layout is None:
            self.main_layout = QVBoxLayout(self)
            self.setLayout(self.main_layout)

        self.main_layout.addWidget(self.base_widget)

    @property
    def buttons(self):
        """Delegate to current measure's buttons for playback/display."""
        if self.pattern_widget:
            w = self.pattern_widget.get_current_measure_widget()
            return w.buttons if w else [[] for _ in range(4)]
        return [[] for _ in range(4)]

    @property
    def measure_widgets(self):
        """Delegate to pattern_widget measure widgets."""
        if self.pattern_widget:
            return self.pattern_widget.get_measure_widgets()
        return []

    @property
    def current_measure_index(self):
        """Delegate to pattern_widget current measure index."""
        if self.pattern_widget:
            return self.pattern_widget.current_measure_index
        return 0

    @current_measure_index.setter
    def current_measure_index(self, value: int):
        if self.pattern_widget:
            self.pattern_widget.current_measure_index = value

    def _create_toolbar_row(self) -> QHBoxLayout:
        """BPM + Tap · Steps · Vel · Dur, and the USB Recorder toggle."""
        mp = JDXi.UI.PatternEditor
        row = QHBoxLayout()
        row.setSpacing(mp.SPACING_RELATED)

        self.tempo_label, self.tempo_spinbox = spinbox_with_label_from_spec(
            self.specs["spinboxes"]["tempo"]
        )
        self.tempo_spinbox.valueChanged.connect(self._on_tempo_changed)
        row.addWidget(self.tempo_label)
        row.addWidget(self.tempo_spinbox)
        self._add_tool_button("tap_tempo", self.specs["buttons"]["tap_tempo"], row)
        row.addSpacing(mp.SPACING_GROUP)

        row.addWidget(QLabel(self.tr("Steps:")))
        self.beats_per_measure_combo = create_combo_box(
            spec=self.specs["combos"]["beats_per_measure"]
        )
        self.beats_per_measure_combo.setCurrentIndex(0)  # 16 steps (4/4)
        self.beats_per_measure_combo.currentIndexChanged.connect(
            self._on_beats_per_measure_changed
        )
        row.addWidget(self.beats_per_measure_combo)
        row.addSpacing(mp.SPACING_GROUP)

        self.velocity_label, self.velocity_spinbox = spinbox_with_label_from_spec(
            self.specs["spinboxes"]["velocity"]
        )
        row.addWidget(self.velocity_label)
        row.addWidget(self.velocity_spinbox)
        row.addSpacing(mp.SPACING_GROUP)

        self.duration_label = QLabel("Dur:")
        self.duration_combo = create_combo_box(spec=self.specs["combos"]["duration"])
        self.duration_combo.setCurrentIndex(0)  # Default to 16th note
        self.duration_combo.currentIndexChanged.connect(self._on_duration_changed)
        row.addWidget(self.duration_label)
        row.addWidget(self.duration_combo)
        row.addStretch()

        usb_item, self.usb_recorder_toggle = create_round_button_with_label(
            self.tr("USB Recorder"),
            JDXi.UI.Icon.SAVE,
            tooltip=self.tr("Show the USB audio recorder"),
            checkable=True,
        )
        self.usb_recorder_toggle.toggled.connect(self.usb_recorder.setVisible)
        row.addWidget(usb_item)
        return row

    def _create_edit_row(self) -> QHBoxLayout:
        """Add Measure · Copy previous · step range · Copy · Paste."""
        mp = JDXi.UI.PatternEditor
        row = QHBoxLayout()
        row.setSpacing(mp.SPACING_RELATED)

        self._add_tool_button("add_measure", self.specs["buttons"]["add_measure"], row)
        self.copy_previous_measure_checkbox = QCheckBox(
            f"Copy previous {self.measure_name.lower()}"
        )
        self.copy_previous_measure_checkbox.setChecked(False)
        JDXi.UI.Theme.apply_button_mini_style(self.copy_previous_measure_checkbox)
        row.addWidget(self.copy_previous_measure_checkbox)
        row.addSpacing(mp.SPACING_GROUP)

        start_label, self.start_step_spinbox = spinbox_with_label_from_spec(
            self.specs["spinboxes"]["start"]
        )
        _, self.end_step_spinbox = spinbox_with_label_from_spec(
            self.specs["spinboxes"]["end"]
        )
        row.addWidget(start_label)
        row.addWidget(self.start_step_spinbox)
        row.addWidget(QLabel(self.tr("to")))
        row.addWidget(self.end_step_spinbox)
        self._add_tool_button("copy", self.specs["buttons"]["copy"], row)
        self._add_tool_button("paste", self.specs["buttons"]["paste"], row)
        self.paste_button.setEnabled(False)  # Disabled until something is copied
        row.addStretch()
        return row

    def _add_tool_button(
        self, name: str, spec: ButtonSpec, layout: QHBoxLayout
    ) -> QPushButton:
        """Round button + label from a ButtonSpec (sets self.<name>_button)."""
        item, button = create_round_button_with_label(
            spec.label, spec.icon, spec.slot, spec.tooltip or ""
        )
        setattr(self, f"{name}_button", button)
        layout.addWidget(item)
        return button

    def _on_beats_per_measure_changed(self, index):
        raise NotImplementedError

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
                label=self.tr("Steps"),
                min_val=1,
                max_val=16,
                value=1,
                tooltip=self.tr("First step to copy, or where to paste (1–16)"),
            ),
            "end": SpinBoxSpec(
                label=self.tr("to"),
                min_val=1,
                max_val=16,
                value=16,
                tooltip=self.tr("Last step to copy (1–16)"),
            ),
        }

    def _create_learn_group(self) -> QGroupBox:
        """create learn group"""
        learn_group = QGroupBox("Learn Pattern")
        learn_layout = QHBoxLayout()

        self._add_button_with_label_from_spec(
            "learn", self.specs["buttons"]["learn"], learn_layout
        )
        self._add_button_with_label_from_spec(
            "stop_learn", self.specs["buttons"]["stop_learn"], learn_layout
        )
        learn_group.setLayout(learn_layout)
        return learn_group

    def _log_and_return(self, ok: bool, msg: str) -> bool:
        """log and return"""
        if not ok:
            log.debug(msg, scope=self.__class__.__name__)
        return ok

    def _reload_combo_options(self) -> None:
        """Reload combo box options from current digital/analog/drum_options."""
        if not hasattr(self, "row_map") or not self.row_map:
            return
        row_options = [
            self.digital_options,
            self.digital_options,
            self.analog_options,
            self.drum_options,
        ]
        for row, selector in self.row_map.items():
            if row >= len(row_options):
                continue
            opts = row_options[row]
            prev_text = selector.currentText()
            selector.blockSignals(True)
            selector.clear()
            selector.addItems(opts)
            idx = selector.findText(prev_text)
            selector.setCurrentIndex(idx if idx >= 0 else 0)
            selector.blockSignals(False)

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

    def _build_specs(self) -> dict[str, Any]:
        """Assemble all pattern editor button and combo specs for use in _setup_ui."""
        return {
            "buttons": {
                "add_measure": ButtonSpec(
                    label="Add Measure",
                    icon=JDXi.UI.Icon.ADD,
                    tooltip="Add a new Measure",
                    slot=self._add_measure,
                ),
                "copy": ButtonSpec(
                    label="Copy Section",
                    icon=JDXi.UI.Icon.FILE_DOCUMENT,
                    tooltip="Copy selected steps from current measure",
                    slot=self._copy_section,
                ),
                "paste": ButtonSpec(
                    label="Paste Section",
                    icon=JDXi.UI.Icon.ADD,
                    tooltip="Paste copied steps to current measure",
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
                "drum": _combo_spec(self.drum_options),
                "beats_per_measure": ComboBoxSpec(
                    items=["16 steps", "12 steps"],
                    tooltip="Steps per measure: 16 (4/4) or 12 (3/4), in 16th notes",
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
                "digital1": _combo_spec(self.digital_options),
                "digital2": _combo_spec(self.digital_options),
                "analog": _combo_spec(self.analog_options),
            },
            "spinboxes": self._create_spinbox_specs(),
        }

    def _on_button_clicked(self, btn, checked):
        raise NotImplementedError("To be implemented in subclass")

    def _toggle_mute(self, row, checked):
        pass
