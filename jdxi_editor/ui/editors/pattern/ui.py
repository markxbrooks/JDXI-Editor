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

from typing import Any, Callable, Optional

from decologr import Decologr as log
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.helpers.widgets import (
    create_jdxi_button,
    create_jdxi_button_from_spec,
    create_jdxi_button_with_label_from_spec,
    create_jdxi_row,
)
from jdxi_editor.ui.editors.midi_player.transport.spec import (
    TransportSpec,
)
from jdxi_editor.ui.editors.pattern.models import SequencerStyle
from jdxi_editor.ui.editors.pattern.options import DIGITAL_OPTIONS, DRUM_OPTIONS
from jdxi_editor.ui.editors.pattern.spec import SequencerRowSpec
from jdxi_editor.ui.editors.synth.editor import SynthEditor
from jdxi_editor.ui.preset.helper import JDXiPresetHelper
from jdxi_editor.ui.style import JDXiUIThemeManager
from jdxi_editor.ui.widgets.editor.base import EditorBaseWidget
from jdxi_editor.ui.widgets.editor.helper import create_group_with_layout
from jdxi_editor.ui.widgets.pattern.sequencer_button import SequencerButton
from picoui.helpers import create_layout_with_widgets, group_with_layout
from picoui.helpers.spinbox import spinbox_with_label_from_spec
from picoui.specs.widgets import (
    ButtonSpec,
    ComboBoxSpec,
    SpinBoxSpec,
)
from picoui.widget.helper import create_combo_box


def _combo_spec(items, tooltip: str = "") -> ComboBoxSpec:
    """Build ComboBoxSpec with items list, no slot."""
    return ComboBoxSpec(items=list(items), tooltip=tooltip, slot=None)


_EXPANDING = (
    QSizePolicy.Policy.Expanding,
    QSizePolicy.Policy.Expanding,
)


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
        # Use Qt translations: add .ts/.qm for locale (e.g. en_GB "Measure" -> "Measure", "Measures" -> "Measures")
        self.measure_name = self.tr("Measure")
        self.measure_name_plural = self.tr("Measures")
        self._state = None
        self.stop_button = None
        self.play_button = None
        self.analog_selector = None
        self.digital2_selector = None
        self.digital1_selector = None
        self.paste_button = None
        self.muted_channels = []
        self.total_measures = 1  # Start with 1 measure by default
        self.midi_helper = midi_helper
        self.preset_helper = preset_helper
        self.midi_file_editor = midi_file_editor  # Reference to MidiFileEditor
        self.buttons = []  # Main sequencer buttons (always 16 steps, one measure)
        self.button_layouts = []  # Store references to button layouts for each row
        self.measures = []  # Each measure stores its own notes
        self.current_measure_index = 0  # Currently selected measure (0-indexed)
        self.timer = None
        self.current_step = 0
        self.total_steps = (
            16  # Always 16 steps per measure (don't multiply by measures)
        )
        self.beats_per_pattern = 4
        self.measure_beats = 16  # Number of beats per measure (16 or 12)
        self.bpm = 120
        self.last_tap_time = None
        self.tap_times = []
        self.midi_file = None  # Set in _setup_ui from MidiFileController
        self.midi_track = None  # Set in _setup_ui from MidiFileController
        self.clipboard = None  # Store copied notes: {source_measure, rows, start_step, end_step, notes_data}
        self._pattern_paused = False
        self.row_specs = [
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
        self._setup_ui()

        JDXi.UI.Theme.apply_editor_style(self)

    def _setup_ui(self):
        """Use EditorBaseWidget for consistent scrollable layout structure"""
        self._init_base_widget()

        # Create content widget with main layout
        content_widget = QWidget()
        self.layout = QVBoxLayout(content_widget)
        self.row_labels = [
            "Digital Synth 1",
            "Digital Synth 2",
            "Analog Synth",
            "Drums",
        ]
        self.buttons = [[] for _ in range(4)]
        self.mute_buttons = []  # List to store mute buttons

        # Define synth options
        self.digital_options = DIGITAL_OPTIONS

        self.analog_options = self.digital_options

        # Define drum kit options
        self.drum_options = DRUM_OPTIONS

        # Assemble all specs for buttons and combos (used below)
        self.specs = self._build_specs()

        # Add transport and file controls at the top
        control_panel = QHBoxLayout()

        file_group = self._create_file_group()

        measure_group = self._create_measure_group()
        control_panel.addWidget(measure_group)

        learn_group = self._create_learn_group()
        # not adding this for now

        tempo_group = self._create_tempo_group()
        control_panel.addWidget(tempo_group)

        beats_group = self._create_beats_group()
        control_panel.addWidget(beats_group)

        velocity_group = self._create_velocity_group()
        control_panel.addWidget(velocity_group)

        duration_group = self._create_duration_group()
        control_panel.addWidget(duration_group)

        self.layout.addLayout(control_panel)

        # Create splitter for measures list and sequencer (builds measures group + sequencer widget)
        self._build_splitter_section()

        self.channel_map = self._build_channel_map()

        # Transport at bottom, centered (stretch on both sides)
        transport_bottom_layout = create_layout_with_widgets(
            [
                self._init_transport_controls(),
                file_group,
            ]
        )
        self.layout.addLayout(transport_bottom_layout)

        # Add content to scrollable area so the widget tree is retained
        self._container_layout.addWidget(content_widget)

    def _build_splitter_section(self):
        """Build splitter section for the list of measures/measures"""
        splitter = QSplitter(Qt.Orientation.Horizontal)

        splitter.addWidget(self._create_measures_group())
        splitter.addWidget(self._create_sequencer_widget())

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizePolicy(*_EXPANDING)

        self.layout.addWidget(splitter)

    def _create_sequencer_widget(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        widget.setSizePolicy(*_EXPANDING)

        for row_idx, label in enumerate(self.row_labels):
            layout.addLayout(self._create_sequencer_row(row_idx, label))

        layout.addStretch()
        return widget

    def _create_row_header(self, row_idx: int, label_text: str) -> QHBoxLayout:
        """create row header"""

        icon_label = QLabel()
        icon_label.setPixmap(self._get_row_icon(row_idx).pixmap(40, 40))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label = QLabel(label_text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet(self._get_row_label_style(row_idx))

        layout = create_layout_with_widgets([icon_label, label])

        selector = self._create_selector_for_row(row_idx)
        if selector:
            layout.addWidget(selector)

        return layout

    def _get_row_icon(self, row_idx: int):
        """get row icon"""
        icon_map = {
            0: JDXi.UI.Icon.PIANO,
            1: JDXi.UI.Icon.PIANO,
            2: JDXi.UI.Icon.PIANO,
            3: JDXi.UI.Icon.DRUM,
        }

        icon_key = icon_map.get(row_idx, JDXi.UI.Icon.PIANO)

        return JDXi.UI.Icon.get_icon(
            icon_key,
            color=JDXi.UI.Style.FOREGROUND,
        )

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

    def _create_row_buttons(self, row_idx: int) -> QHBoxLayout:
        """Create the mute button + step buttons layout for one sequencer row."""
        row_buttons_layout = QHBoxLayout()

        # Mute button (round button + icon label) for this row
        mute_btn_layout = QHBoxLayout()
        mute_btn_layout.addStretch()
        mute_btn = self._add_round_action_button(
            JDXi.UI.Icon.MUTE,
            self.tr("Mute"),
            None,
            mute_btn_layout,
            checkable=True,
            append_to=self.mute_buttons,
        )
        mute_btn.toggled.connect(
            lambda checked, row=row_idx: self._toggle_mute(row, checked)
        )
        mute_btn_layout.addStretch()
        row_buttons_layout.addLayout(mute_btn_layout)

        # Step buttons for this row
        step_buttons_layout = self.ui_generate_button_row(row_idx, visible=True)
        self.button_layouts.append(step_buttons_layout)
        row_buttons_layout.addLayout(step_buttons_layout)

        return row_buttons_layout

    def _create_sequencer_row(self, row_idx: int, label_text: str) -> QVBoxLayout:
        row_layout = QVBoxLayout()

        header = self._create_row_header(row_idx, label_text)
        buttons = self._create_row_buttons(row_idx)

        row_layout.addLayout(header)
        row_layout.addLayout(buttons)

        return row_layout

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

    def _create_measures_group(self) -> QGroupBox:
        """Measures list widget"""
        measures_group = QGroupBox(f"{self.measure_name}")
        measures_layout = QVBoxLayout()
        self.measures_list = QListWidget()
        self.measures_list.setMaximumWidth(150)
        self.measures_list.itemClicked.connect(self._on_measure_selected)
        measures_layout.addWidget(self.measures_list)
        measures_group.setLayout(measures_layout)
        return measures_group

    def _create_duration_group(self) -> QGroupBox:
        """Duration control area"""
        duration_group = QGroupBox("Duration")
        duration_layout = QHBoxLayout()

        self.duration_label = QLabel("Dur:")
        self.duration_combo = create_combo_box(spec=self.specs["combos"]["duration"])
        self.duration_combo.setCurrentIndex(0)  # Default to 16th note
        self.duration_combo.currentIndexChanged.connect(self._on_duration_changed)

        duration_layout.addWidget(self.duration_label)
        duration_layout.addWidget(self.duration_combo)
        duration_group.setLayout(duration_layout)
        return duration_group

    def _create_velocity_group(self) -> QGroupBox:
        """Velocity control area"""
        velocity_group = QGroupBox("Velocity")
        velocity_layout = QHBoxLayout()

        self.velocity_label, self.velocity_spinbox = spinbox_with_label_from_spec(
            self.specs["spinboxes"]["velocity"]
        )

        velocity_layout.addWidget(self.velocity_label)
        velocity_layout.addWidget(self.velocity_spinbox)
        velocity_group.setLayout(velocity_layout)
        return velocity_group

    def _create_beats_group(self) -> QGroupBox:
        """Beats per measure control area"""
        beats_group = QGroupBox("Beats per Measure")
        beats_layout = QHBoxLayout()

        self.beats_per_measure_combo = create_combo_box(
            spec=self.specs["combos"]["beats_per_measure"]
        )
        self.beats_per_measure_combo.setCurrentIndex(0)  # Default to 16 beats
        self.beats_per_measure_combo.currentIndexChanged.connect(
            self._on_beats_per_measure_changed
        )

        beats_layout.addWidget(self.beats_per_measure_combo)
        beats_group.setLayout(beats_layout)
        return beats_group

    def _create_tempo_group(self) -> QGroupBox:
        """Tempo control area"""
        tempo_group = QGroupBox("Tempo")
        tempo_layout = QHBoxLayout()

        self.tempo_label, self.tempo_spinbox = spinbox_with_label_from_spec(
            self.specs["spinboxes"]["tempo"]
        )
        self.tempo_spinbox.valueChanged.connect(self._on_tempo_changed)

        tempo_layout.addWidget(self.tempo_label)
        tempo_layout.addWidget(self.tempo_spinbox)
        self._add_button_with_label_from_spec(
            "tap_tempo",
            self.specs["buttons"]["tap_tempo"],
            tempo_layout,
        )
        tempo_group.setLayout(tempo_layout)
        return tempo_group

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
        """Measure management area (separate row for Add Measure button and checkbox)"""

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

        step_layout_widgets = [
            step_label,
            start_label,
            self.start_step_spinbox,
            to_label,
            end_label,
            self.end_step_spinbox,
        ]
        step_range_layout = create_layout_with_widgets(
            widgets=step_layout_widgets, start_stretch=False, end_stretch=False
        )
        measure_group, measure_layout = create_group_with_layout(
            label=self.measure_name_plural, vertical=True
        )
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
            button.setStyleSheet(JDXi.UI.Style.generate_sequencer_button_style(False))
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

    def _build_channel_map(self) -> dict[int, QComboBox]:
        channel_map = {
            0: self.digital1_selector,
            1: self.digital2_selector,
            2: self.analog_selector,
            3: self.drum_selector,
        }
        return channel_map

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
                    items=["16 beats per measure", "12 beats per measure"],
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
                "digital1": _combo_spec(self.digital_options),
                "digital2": _combo_spec(self.digital_options),
                "analog": _combo_spec(self.analog_options),
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

    def _on_button_clicked(self, btn, checked):
        raise NotImplementedError("To be implemented in subclass")
