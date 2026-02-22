"""
MIDI Player for JDXI Editor
"""

import cProfile
import io
import pstats
import re
import time
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from turtledemo.penrose import start
from typing import Any, Optional

import mido
import pyaudio
from decologr import Decologr as log
from mido import MidiFile, bpm2tempo

from jdxi_editor.ui.editors.midi_player.track.category import (
    TrackCategory,
    STR_TO_TRACK_CATEGORY,
    CATEGORY_META,
)
from jdxi_editor.ui.preset.source import PresetSource
from picomidi.constant import Midi
from PySide6.QtCore import Qt, QThread, QTimer, QMargins
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.globals import PROFILING
from jdxi_editor.midi.channel.channel import MidiChannel
from jdxi_editor.midi.data.address.address import (
    JDXiSysExAddress,
    JDXiSysExAddressStartMSB,
    JDXiSysExOffsetProgramLMB,
    JDXiSysExOffsetSystemUMB,
)
from jdxi_editor.midi.data.parameter.effects.effects import (
    DelayParam,
    Effect1Param,
    Effect2Param,
    ReverbParam,
)
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.playback.state import MidiPlaybackState
from jdxi_editor.midi.playback.worker import MidiPlaybackWorker
from jdxi_editor.midi.sysex.composer import JDXiSysExComposer
from jdxi_editor.midi.track.classification import classify_tracks
from jdxi_editor.midi.utils.drum_detection import detect_drum_tracks
from jdxi_editor.midi.utils.helpers import start_recording
from jdxi_editor.midi.utils.usb_recorder import USBRecorder
from jdxi_editor.ui.editors.helpers.widgets import (
    create_jdxi_button_from_spec,
    create_jdxi_button_with_label_from_spec,
    create_jdxi_row,
)
from jdxi_editor.ui.editors.midi_player.transport.spec import TransportSpec
from jdxi_editor.ui.editors.midi_player.utils import format_time, tempo2bpm
from jdxi_editor.ui.editors.midi_player.widgets import MidiPlayerWidgets
from jdxi_editor.ui.editors.synth.editor import SynthEditor
from jdxi_editor.ui.preset.helper import JDXiPresetHelper
from jdxi_editor.ui.style import JDXiUIDimensions, JDXiUIStyle
from jdxi_editor.ui.style.factory import generate_sequencer_button_style
from jdxi_editor.ui.widgets.digital.title import DigitalTitle
from jdxi_editor.ui.widgets.editor.base import EditorBaseWidget
from jdxi_editor.ui.widgets.editor.helper import (
    create_checkbox_from_spec,
    create_group_with_layout,
    create_icon_and_label,
    create_layout_with_widgets,
    create_vertical_layout,
)
from jdxi_editor.ui.widgets.midi.track_viewer import MidiTrackViewer
from jdxi_editor.ui.widgets.midi.utils import get_total_duration_in_seconds
from jdxi_editor.ui.windows.jdxi.utils import show_message_box_from_spec
from picoui.helpers import create_layout_with_inner_layouts, create_widget_with_layout
from picoui.specs.widgets import ButtonSpec, CheckBoxSpec, MessageBoxSpec

# Expose Qt symbols for tests that patch via jdxi_editor.ui.editors.io.player
# Tests expect these names to exist at module level
QApplication = None  # alias placeholder for patching
QObject = None
Signal = None
Slot = None



class MidiFilePlayer(SynthEditor):
    """
    Midi File Editor
    """

    BUFFER_WINDOW_SECONDS = 30.0

    def __init__(
            self,
            midi_helper: Optional[MidiIOHelper] = None,
            parent: QWidget = None,
            preset_helper: JDXiPresetHelper = None,
    ):
        """
        Initialize the MidiPlayer

        :param midi_helper: Optional[MidiIOHelper]
        :param parent: Optional[QWidget]
        :param preset_helper: Optional[JDXIPresetHelper]
        """
        super().__init__()
        self.specs: dict | None = None
        self._last_position_label: QLabel | None = None
        self.parent: QWidget = parent
        self.preset_helper: JDXiPresetHelper = preset_helper
        self.profiler = None
        # Midi-related
        self.midi_state: MidiPlaybackState = MidiPlaybackState()
        self.midi_playback_worker: MidiPlaybackWorker = MidiPlaybackWorker(parent=self)
        self.midi_playback_worker.set_tempo.connect(self.update_tempo_us_from_worker)
        self.midi_total_ticks: int | None = None
        self.midi_port = self.midi_helper.midi_out
        self.midi_timer_init()
        self.current_tempo_bpm = None  # Store current tempo BPM for digital
        self.midi_preferred_channels = {
            MidiChannel.DIGITAL_SYNTH_1,
            MidiChannel.DIGITAL_SYNTH_2,
            MidiChannel.ANALOG_SYNTH,
            MidiChannel.DRUM_KIT,
        }  # MIDI channels 1, 2, 3, 10 (zero-based)
        # self.usb_recording_thread = None
        self.usb_recorder = USBRecorder(channels=1)
        # Initialize UI attributes
        self.ui = MidiPlayerWidgets()
        self.specs = self._build_specs()
        self.ui_init()

    def midi_timer_init(self):
        """
        Initialize or reinitialize the MIDI playback timer.
        Ensures previous connections are safely removed.
        """
        try:
            if self.midi_state.timer:
                self.midi_state.timer.stop()
                self.midi_state.timer.timeout.disconnect()
        except Exception as ex:
            log.warning(f"⚠️ Failed to disconnect old midi.timer: {ex}")

        timer = QTimer(self)
        timer.timeout.connect(self.midi_play_next_event)
        self.midi_state.timer = timer

    def ui_ensure_timer_connected(self):
        """
        ui_ensure_timer_connected

        :return:
        Ensure the midi_play_next_event is connected to midi.timer.timeout
        """

        try:
            self.midi_state.timer.timeout.disconnect(self.midi_play_next_event)
        except TypeError:
            pass  # Already disconnected
        except Exception as ex:
            log.warning(f"⚠️ Could not disconnect midi_play_next_event: {ex}")

        try:
            self.midi_state.timer.timeout.connect(self.midi_play_next_event)
        except Exception as ex:
            log.error(f"❌ Failed to connect midi_play_next_event: {ex}")

    def ui_init(self):
        """
        Initialize the UI for the MidiPlayer.
        """

        panel_widgets = [self.build_panel(self._build_left_panel),
                         self.build_panel(self._build_right_panel)]

        # --- Top horizontal layout: file title and right-hand controls
        header_layout = create_layout_with_widgets(widgets=panel_widgets,
                                                   start_stretch=False,
                                                   end_stretch=False)

        # --- Use EditorBaseWidget for consistent scrollable layout structure
        self.base_widget = EditorBaseWidget(parent=self, analog=False)
        self.base_widget.setup_scrollable_content()
        # Create content widget
        content_widget = QWidget()
        main_layout = QVBoxLayout(content_widget)
        main_layout.addLayout(header_layout)
        main_layout.addWidget(self.init_ruler())
        main_layout.addWidget(self.ui.midi_track_viewer)
        centered_layout = create_layout_with_widgets(
            [
                self.init_transport_controls(),
                self.init_midi_file_controls(),
                self.init_event_suppression_controls(),
            ]
        )
        main_layout.addLayout(centered_layout)
        # Add content to base widget
        container_layout = self.base_widget.get_container_layout()
        container_layout.addWidget(content_widget)
        self._add_base_widget_to_editor()

    def build_panel(self, builder: Callable) -> QWidget:
        """build the appropriate panel"""
        panel_layout = builder()
        panel_widget = create_widget_with_layout(panel_layout)
        return panel_widget

    def _add_base_widget_to_editor(self):
        """Add base widget to editor's layout"""
        if not hasattr(self, "main_layout") or self.main_layout is None:
            self.main_layout = QVBoxLayout(self)
            self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.base_widget)

    def _build_left_panel(self) -> QVBoxLayout:
        """Build left panel"""
        # Create vertical layout for title and drum detection button
        self.ui.digital_title_file_name = DigitalTitle(
            tone_name="No file loaded", show_upper_text=True
        )
        classification_widget = self._create_classify_tracks_widget()
        layout = create_layout_with_widgets(
            widgets=[
                self.ui.digital_title_file_name,
                classification_widget
            ],
            vertical=False
        )
        return layout

    def _create_classify_tracks_widget(self) -> QWidget:
        """create classify tracks widget"""
        classify_tracks_widgets = self._build_classify_tracks_widgets()
        classification_hlayout = create_layout_with_widgets(widgets=classify_tracks_widgets, spacing=5)
        classification_widget = QWidget()
        classification_vlayout = create_layout_with_inner_layouts(inner_layouts=[classification_hlayout],
                                                                  vertical=True,
                                                                  stretch=False)
        classification_widget.setLayout(classification_vlayout)
        apply_all_label_row = self.create_apply_all_button_and_label()
        classification_vlayout.addWidget(apply_all_label_row)
        return classification_widget

    def _build_right_panel(self):
        """Build right panel"""
        right_panel_layout = create_layout_with_inner_layouts(
            inner_layouts=[
                self.init_automation_usb_grid(),
                self.init_mute_controls()
            ],
            vertical=True, stretch=False
        )
        return right_panel_layout

    def _build_classify_tracks_widgets(self) -> list[QPushButton | QWidget]:
        """build classify tracks widgets"""
        # ---- Drum detection button
        detect_drums_label_row, self.ui.detect_drums_button = create_jdxi_button_with_label_from_spec(
            self.specs["buttons"]["detect_drums"])
        # --- Classify Tracks Button
        classify_tracks_label_row, self.ui.classify_tracks_button = create_jdxi_button_with_label_from_spec(
            self.specs["buttons"]["classify_tracks"])
        widgets = [
            self.ui.detect_drums_button,
            detect_drums_label_row,
            self.ui.classify_tracks_button,
            classify_tracks_label_row,
        ]
        return widgets

    def init_ruler(self) -> QWidget:
        """
        init_ruler

        :return: QWidget
        """
        self.init_midi_file_position_label()
        self.init_midi_file_position_slider()
        widgets = [self.ui.position_label, self.ui.midi_file_position_slider]
        ruler_layout = create_layout_with_widgets(widgets=widgets,
                                                  margins=QMargins(0, 0, 0, 0),
                                                  spacing=0,
                                                  start_stretch=False,
                                                  end_stretch=False)
        ruler_container = create_widget_with_layout(layout=ruler_layout)
        return ruler_container

    def init_midi_file_position_label(self):
        """Midi File position label"""
        self.ui.position_label = QLabel("Playback Position: 0:00 / 0:00")
        self.ui.midi_track_viewer = MidiTrackViewer()
        self.ui.position_label.setFixedWidth(
            self.ui.midi_track_viewer.get_track_controls_width()
        )

    def init_midi_file_position_slider(self):
        """Midi File position slider"""
        self.ui.midi_file_position_slider = QSlider(Qt.Horizontal)
        self.ui.midi_file_position_slider.setEnabled(False)
        self.ui.midi_file_position_slider.sliderReleased.connect(
            self.midi_scrub_position
        )

    def init_event_suppression_controls(self) -> QGroupBox:
        """
        init_midi_file_controls

        :return: QHBoxLayout
        """

        midi_suppress_pc_spec = CheckBoxSpec(
            label="Program Changes",
            checked_state=self.midi_state.suppress_program_changes,
            slot=self.on_suppress_program_changes_toggled,
            style=JDXiUIStyle.PARTIAL_SWITCH,
        )

        midi_suppress_cc_spec = CheckBoxSpec(
            label="Control Changes",
            checked_state=self.midi_state.suppress_control_changes,
            slot=self.on_suppress_control_changes_toggled,
            style=JDXiUIStyle.PARTIAL_SWITCH,
        )

        # Use the spec-created checkboxes (they have callbacks); replace UI refs so layout and theme use them
        self.ui.midi_suppress_program_changes_checkbox = create_checkbox_from_spec(
            spec=midi_suppress_pc_spec
        )
        self.ui.midi_suppress_control_changes_checkbox = create_checkbox_from_spec(
            spec=midi_suppress_cc_spec
        )

        pc_label = QLabel("Program Change")
        cc_label = QLabel("Control Change")
        widgets = [
            pc_label,
            self.ui.midi_suppress_program_changes_checkbox,
            cc_label,
            self.ui.midi_suppress_control_changes_checkbox,
        ]
        JDXi.UI.Theme.apply_partial_switch(
            self.ui.midi_suppress_program_changes_checkbox
        )
        JDXi.UI.Theme.apply_partial_switch(
            self.ui.midi_suppress_control_changes_checkbox
        )
        layout = create_layout_with_widgets(widgets=widgets, vertical=False)
        group, _ = create_group_with_layout(
            label="MIDI Event Suppression", layout=layout
        )
        return group

    def init_midi_file_controls(self) -> QGroupBox:
        """
        init_midi_file_controls

        :return: QHBoxLayout
        """
        spec = self.specs["buttons"]["load_midi_file"]
        self.ui.load_button = create_jdxi_button_from_spec(spec, checkable=False)
        load_icon_pixmap = JDXi.UI.Icon.get_icon_pixmap(
            spec.icon, color=JDXi.UI.Style.FOREGROUND, size=20
        )
        load_label_row, self.ui.load_label = create_jdxi_row(
            label=spec.label, icon_pixmap=load_icon_pixmap
        )
        spec = self.specs["buttons"]["save_midi_file"]
        self.ui.save_button = create_jdxi_button_from_spec(spec, checkable=False)

        save_icon_pixmap = JDXi.UI.Icon.get_icon_pixmap(
            spec.icon, color=JDXi.UI.Style.FOREGROUND, size=20
        )
        save_label_row, self.ui.save_label = create_jdxi_row(
            spec.label, icon_pixmap=save_icon_pixmap
        )

        layout = create_layout_with_widgets(
            widgets=[
                self.ui.load_button,
                load_label_row,
                self.ui.save_button,
                save_label_row
            ],
            vertical=False
        )

        group = QGroupBox("MIDI File")
        group.setLayout(layout)
        return group

    def detect_and_assign_drum_tracks(self) -> None:
        """
        Detect drum tracks in the loaded MIDI file and assign Channel 10 (1-based) to them.

        This analyzes all tracks using heuristics and automatically sets the channel
        spinboxes for tracks identified as drum tracks.
        """
        if not self._validate_midi_loaded():
            return

        try:
            # Detect drum tracks (returns list of (track_index, analysis_dict) tuples)
            drum_tracks = detect_drum_tracks(self.midi_state.file, min_score=70.0)

            if not drum_tracks:
                show_message_box_from_spec(
                    self.specs["message_box"]["no_drum_tracks_found"]
                )
                return

            # Update the channel spinboxes for detected drum tracks
            # Channel 10 (1-based) = Channel 9 (0-based)
            drum_channel_display = 10  # 1-based digital channel
            drum_channel_binary = 9  # 0-based binary channel

            updated_tracks = []
            for track_index, analysis in drum_tracks:
                if track_index in self.ui.midi_track_viewer._track_channel_spins:
                    spin = self.ui.midi_track_viewer._track_channel_spins[track_index]
                    spin.setValue(drum_channel_display)
                    track_name = (
                            analysis.get("track_name") or f"Track {track_index + 1}"
                    )
                    updated_tracks.append(
                        f"Track {track_index + 1} ({track_name}) - Score: {analysis['score']:.1f}"
                    )

            # --- Show success message
            tracks_list = "\n".join(f"  • {t}" for t in updated_tracks)
            message = (
                f"🎵 Detected {len(updated_tracks)} drum track(s) and set to Channel 10"
            )
            show_message_box_from_spec(
                self.specs["message_box"]["drum_tracks_detected"], message=message
            )
            log.message(message=message)

        except Exception as ex:
            log.error(f"❌ Error detecting drum tracks: {ex}")
            import traceback

            log.error(traceback.format_exc())
            show_message_box_from_spec(
                self.specs["message_box"]["error_detect_drums"],
                message=f"An error occurred while detecting drum tracks:\n\n{ex}",
            )

    def classify_and_assign_tracks(self) -> None:
        """classify and assign tracks"""
        if not self._validate_midi_loaded():
            return

        try:
            drum_indices = self._detect_drum_tracks()
            classifications = self._classify_tracks(drum_indices)

            updated_tracks = self._apply_channel_assignments(classifications)

            if not self._has_classified_tracks(updated_tracks):
                self._show_no_tracks_message()
                return

            message = self._build_classification_message(updated_tracks)
            self._show_info_message("Tracks Classified", message)

            log.message("🎵 Track classification completed")

        except Exception as ex:
            self._handle_classification_error(ex)

    def _validate_midi_loaded(self) -> bool:
        """validate that a MIDI file is loaded"""
        if not self.midi_state.file:
            self._show_warning(
                "No MIDI File Loaded",
                "Please load a MIDI file first before classifying tracks.",
            )
            return False
        return True

    def _detect_drum_tracks(self) -> list[int]:
        """detect drum tracks"""
        drum_tracks = detect_drum_tracks(self.midi_state.file, min_score=70.0)
        return [idx for idx, _ in drum_tracks]

    def _classify_tracks(self, drum_indices: list[int]):
        """classify tracks"""
        return classify_tracks(
            self.midi_state.file,
            exclude_drum_tracks=drum_indices,
            min_score=30.0,
        )

    def _apply_channel_assignments(self, classifications) -> dict[str, list[str]]:
        """apply channel assignments"""
        updated: dict[str, list[str]] = {
            TrackCategory.BASS: [],
            TrackCategory.KEYS_GUITARS: [],
            TrackCategory.STRINGS: [],
            TrackCategory.UNCLASSIFIED: [],
        }

        for category_str, tracks in classifications.items():
            category = STR_TO_TRACK_CATEGORY.get(
                category_str, TrackCategory.UNCLASSIFIED
            )

            if category == TrackCategory.UNCLASSIFIED:
                continue

            meta = CATEGORY_META[category]

            for track_index, analysis in tracks:
                spin = self.ui.midi_track_viewer._track_channel_spins.get(track_index)
                if not spin:
                    continue

                spin.setValue(meta.channel)

                track_name = (
                        getattr(analysis, "track_name", None) or f"Track {track_index + 1}"
                )
                score = analysis.scores[category]

                updated[category].append(
                    f"Track {track_index + 1} ({track_name}) - Score: {score:.1f}"
                )

        self._handle_unclassified_tracks(classifications, updated)

        return updated

    def _handle_unclassified_tracks(
            self, classifications, updated: dict[str, list[str]]
    ):
        """Handle unclassified"""
        for track_index, analysis in classifications.get("unclassified", []):
            track_name = (
                    getattr(analysis, "track_name", None) or f"Track {track_index + 1}"
            )
            scores = analysis.scores

            max_category, max_score = max(scores.items(), key=lambda x: x[1])

            updated[TrackCategory.UNCLASSIFIED].append(
                f"Track {track_index + 1} ({track_name}) - Best: {max_category} ({max_score:.1f})"
            )

    def _has_classified_tracks(self, updated_tracks: dict) -> bool:
        """Return True if at least one track was classified (excluding unclassified)."""
        return (
                sum(
                    len(v)
                    for k, v in updated_tracks.items()
                    if k != TrackCategory.UNCLASSIFIED
                )
                > 0
        )

    def _show_no_tracks_message(self) -> None:
        """Show the no-tracks-classified message box."""
        show_message_box_from_spec(self.specs["message_box"]["no_tracks_classified"])

    def _build_classification_message(
            self,
            updated: dict[str, list[str]],
    ) -> str:
        """build classification message"""
        total_classified = sum(
            len(v) for k, v in updated.items() if k != TrackCategory.UNCLASSIFIED
        )

        parts = [f"Classified {total_classified} track(s):\n"]

        for category in CATEGORY_META:
            tracks = updated[category]
            if not tracks:
                continue

            meta = CATEGORY_META[category]
            parts.append(
                f"\n{meta.emoji} {meta.label} "
                f"(Channel {meta.channel} - {meta.engine}):"
            )

            for track in tracks:
                parts.append(f"  • {track}")

        unclassified = updated[TrackCategory.UNCLASSIFIED]
        if unclassified:
            parts.append(f"\n❓ Unclassified ({len(unclassified)} track(s)):")
            for track in unclassified[:5]:
                parts.append(f"  • {track}")
            if len(unclassified) > 5:
                parts.append(f"  ... and {len(unclassified) - 5} more")

        parts.append("\n\nClick 'Apply All Track Changes' to save the changes.")

        return "\n".join(parts)

    def _show_info_message(self, title: str, message: str) -> None:
        """show info dialog"""
        show_message_box_from_spec(
            self.specs["message_box"]["info"],
            title=title,
            message=message,
        )

    def _show_warning(self, title: str, message: str) -> None:
        """show warning"""
        show_message_box_from_spec(
            self.specs["message_box"]["warning"],
            title=title,
            message=message,
        )

    def _handle_classification_error(self, ex: Exception) -> None:
        """handle classification error"""
        log.error(f"❌ Error classifying tracks: {ex}")
        import traceback

        log.error(traceback.format_exc())

        show_message_box_from_spec(
            self.specs["message_box"]["error_classify_tracks"],
            message=f"An error occurred while classifying tracks:\n\n{ex}",
        )

    def init_automation_usb_grid(self) -> QGridLayout:
        """
        Create a grid layout containing Automation, USB Port, and USB File controls.
        """
        grid = QGridLayout()
        row = 0

        automation_layout, automation_label = create_icon_and_label(
            label="Automation:", icon=JDXi.UI.Icon.MAGIC
        )
        grid.addLayout(automation_layout, row, 0)
        self.ui.automation_channel_combo = QComboBox()
        for ch in range(1, 17):
            self.ui.automation_channel_combo.addItem(f"Ch {ch}", ch)
        grid.addWidget(self.ui.automation_channel_combo, row, 1)
        self.ui.automation_type_combo = QComboBox()
        self.ui.automation_type_combo.addItems(["Digital", "Analog", "Drums"])
        self.ui.automation_type_combo.currentIndexChanged.connect(
            self.on_automation_type_changed
        )
        grid.addWidget(self.ui.automation_type_combo, row, 2)
        self.ui.automation_program_combo = QComboBox()
        grid.addWidget(self.ui.automation_program_combo, row, 3)
        spec = self.specs["buttons"]["automation_insert"]
        self.ui.automation_insert_button = create_jdxi_button_from_spec(
            spec, checkable=False
        )
        insert_cell, self.ui.automation_insert_label = (
            self.create_widget_cell_with_button_spec(
                spec, self.ui.automation_insert_button
            )
        )
        grid.addWidget(insert_cell, row, 4)
        row += 1

        # --- Row 1: USB Port
        usb_port_layout, usb_port_label = create_icon_and_label(
            label="USB Port for recording", icon=JDXi.UI.Icon.USB
        )
        grid.addLayout(usb_port_layout, row, 0)
        self.ui.usb_port_select_combo = QComboBox()
        self.usb_populate_devices()
        grid.addWidget(self.ui.usb_port_select_combo, row, 1, 1, 2)
        spec = self.specs["buttons"]["usb_port_refresh"]
        self.ui.usb_port_refresh_devices_button = create_jdxi_button_from_spec(
            spec, checkable=False
        )
        refresh_usb_cell, self.ui.usb_port_refresh_devices_label = (
            self.create_widget_cell_with_button_spec(
                spec, self.ui.usb_port_refresh_devices_button
            )
        )
        grid.addWidget(refresh_usb_cell, row, 3)
        row += 1

        # --- Row 2: File to save recording
        file_layout, file_label = create_icon_and_label(
            label="File to save recording", icon=JDXi.UI.Icon.SAVE
        )
        grid.addLayout(file_layout, row, 0)
        self.ui.usb_file_select = QPushButton("No File Selected")
        self.ui.usb_file_select.clicked.connect(self.usb_select_recording_file)
        grid.addWidget(self.ui.usb_file_select, row, 1, 1, 2)  # 2 = colspan I guess
        # row += 1

        # --- Row 2 still: Save USB recording checkbox
        self.ui.usb_file_record_checkbox = QCheckBox("Save USB recording to file")
        JDXi.UI.Theme.apply_partial_switch(self.ui.usb_file_record_checkbox)
        self.ui.usb_file_record_checkbox.setChecked(
            self.usb_recorder.file_save_recording
        )
        self.ui.usb_file_record_checkbox.stateChanged.connect(
            self.on_usb_save_recording_toggled
        )
        grid.addWidget(self.ui.usb_file_record_checkbox, row, 3)
        # row += 1

        # --- Row 3: Auto-generate WAV filename checkbox
        self.ui.usb_file_auto_generate_checkbox = QCheckBox(
            "Generate .Wav filename based on date, time and Midi file"
        )
        JDXi.UI.Theme.apply_partial_switch(self.ui.usb_file_auto_generate_checkbox)
        self.ui.usb_file_auto_generate_checkbox.setChecked(False)
        self.ui.usb_file_auto_generate_checkbox.stateChanged.connect(
            self.on_usb_file_auto_generate_toggled
        )
        grid.addWidget(self.ui.usb_file_auto_generate_checkbox, row, 4)

        self.populate_automation_programs(PresetSource.DIGITAL)
        return grid

    def create_widget_cell_with_button_spec(
            self, spec: ButtonSpec, button
    ) -> tuple[QWidget, QLabel]:
        """Create Widget With Button Spec"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.addWidget(button)
        icon_pixmap = JDXi.UI.Icon.get_icon_pixmap(
            spec.icon, color=JDXi.UI.Style.FOREGROUND, size=20
        )
        row_widget, label = create_jdxi_row(spec.label, icon_pixmap=icon_pixmap)
        layout.addWidget(row_widget)
        return widget, label

    def populate_automation_programs(self, source: PresetSource) -> None:
        """
        Populate the program combo based on source list.
        source: "Digital" | "Analog" | "Drums"
        """
        self.ui.automation_program_combo.clear()

        # Helper function to convert dictionary format to list format
        def convert_preset_dict_to_list(preset_dict):
            """Convert PROGRAM_CHANGE dictionary to list format."""
            if isinstance(preset_dict, dict):
                return [
                    {
                        "id": f"{preset_id:03d}",
                        "name": preset_data.get("Name", ""),
                        "category": preset_data.get("Category", ""),
                        "msb": preset_data.get("MSB", 0),
                        "lsb": preset_data.get("LSB", 0),
                        "pc": preset_data.get("PC", preset_id),
                    }
                    for preset_id, preset_data in sorted(preset_dict.items())
                ]
            else:
                # Already a list (Drum format)
                return preset_dict

        preset_list_sources = {
            PresetSource.DIGITAL: JDXi.UI.Preset.Digital.PROGRAM_CHANGE,
            PresetSource.ANALOG: JDXi.UI.Preset.Analog.PROGRAM_CHANGE,
            PresetSource.DRUMS: JDXi.UI.Preset.Drum.PROGRAM_CHANGE,
        }
        preset_list_source = preset_list_sources.get(
            source, JDXi.UI.Preset.Drum.PROGRAM_CHANGE
        )
        preset_list = convert_preset_dict_to_list(preset_list_source)
        self._add_items_items_combo(preset_list)

    def _add_items_items_combo(self, preset_list: list[dict[str, str | Any]] | Any):
        """items to combo box"""
        for item in preset_list:
            label = f"{str(item.get('id')).zfill(3)}  {item.get('name')}"
            msb = int(item.get("msb"))
            lsb = int(item.get("lsb"))
            pc = int(item.get("pc"))
            self.ui.automation_program_combo.addItem(label, (msb, lsb, pc))

    def on_automation_type_changed(self, _: int) -> None:
        """Handle automation type selection change."""
        source = self.ui.automation_type_combo.currentText()
        self.populate_automation_programs(source)

    def insert_program_change_current_position(self) -> None:
        """
        Insert Bank Select (CC#0, CC#32) and Program Change at the current slider time.
        """
        if not self.midi_state.file:
            return

        # Time in seconds from slider
        current_seconds = float(self.ui.midi_file_position_slider.value())
        # Channel (digital is 1-16, convert to 0-based)
        display_channel = int(self.ui.automation_channel_combo.currentData())
        channel = display_channel - 1

        # Selected program triple (msb, lsb, pc)
        data = self.ui.automation_program_combo.currentData()
        if not data:
            return
        msb, lsb, pc = data

        # Convert seconds to absolute ticks (approx using current tempo at position)
        try:
            tempo_usecs = self.midi_state.tempo_at_position or Midi.TEMPO.BPM_120_USEC
            abs_ticks = int(
                mido.second2tick(
                    current_seconds, self.midi_state.file.ticks_per_beat, tempo_usecs
                )
            )
        except Exception:
            abs_ticks = int(current_seconds / max(self.tick_duration, 1e-9))

        # Find a target track that uses this channel, else use track 0
        track_index = self._find_track_for_channel(channel)
        target_track = self.midi_state.file.tracks[track_index]

        # Build messages: CC#0, CC#32, Program Change (PC is 0-based in MIDI spec)
        msgs = [
            mido.Message(
                "control_change", control=0, value=int(msb), channel=channel, time=0
            ),
            mido.Message(
                "control_change", control=32, value=int(lsb), channel=channel, time=0
            ),
            mido.Message(
                "program_change", program=max(0, int(pc) - 1), channel=channel, time=0
            ),
        ]

        self._insert_messages_at_abs_tick(target_track, abs_ticks, msgs)

        # Refresh viewer and internal state
        self.ui.midi_track_viewer.set_midi_file(self.midi_state.file)
        # Sync mute buttons after setting MIDI file
        self._sync_mute_buttons_from_track_viewer()
        self.midi_extract_events()
        self.calculate_duration()
        self.ui_position_label_update_time()

        # Add a visual marker to the time ruler
        try:
            preset_label = self.ui.automation_program_combo.currentText()
            short_label = (
                preset_label.split("  ")[1] if "  " in preset_label else preset_label
            )
            self.ui.midi_track_viewer.ruler.add_marker(
                current_seconds, label=short_label
            )
        except Exception:
            # Fail-safe: add without label
            self.ui.midi_track_viewer.ruler.add_marker(current_seconds)

    def _find_track_for_channel(self, channel: int) -> int:
        for i, track in enumerate(self.midi_state.file.tracks):
            for msg in track:
                if hasattr(msg, "channel") and msg.channel == channel:
                    return i
        return 0

    def _insert_messages_at_abs_tick(
            self, track: mido.MidiTrack, abs_tick_target: int, new_msgs: list[mido.Message]
    ) -> None:
        """
        Insert a list of messages at a given absolute tick, preserving delta times.
        """
        # Compute absolute ticks for each existing message, then rebuild with adjusted deltas
        abs_tick = 0
        rebuilt: list[mido.Message] = []
        inserted = False

        for msg in track:
            next_abs = abs_tick + msg.time
            if not inserted and next_abs >= abs_tick_target:
                # Insert right before this message
                # Delta from current abs_tick to target
                insert_delta = max(0, abs_tick_target - abs_tick)
                # First, push any time before insertion
                if insert_delta > 0:
                    rebuilt.append(
                        mido.Message("note_on", note=0, velocity=0, time=insert_delta)
                    )
                    # Replace the placeholder with zero-time; we will discard it below
                    rebuilt.pop()
                # Append new messages with proper delta times
                first = True
                for nm in new_msgs:
                    nm_copy = nm.copy(time=insert_delta if first else 0)
                    rebuilt.append(nm_copy)
                    first = False
                    insert_delta = 0
                # Now adjust the current message's delta to account for insertion at target
                adjusted_time = max(0, next_abs - abs_tick_target)
                msg = msg.copy(time=adjusted_time)
                inserted = True
            rebuilt.append(msg)
            abs_tick = next_abs

        if not inserted:
            # Append at end; ensure the first inserted msg gets appropriate delta
            first = True
            for nm in new_msgs:
                nm_copy = nm.copy(
                    time=0 if not first else max(0, abs_tick_target - abs_tick)
                )
                rebuilt.append(nm_copy)
                first = False

        # --- Write back
        track.clear()
        for m in rebuilt:
            track.append(m)

    def init_mute_controls(self) -> QHBoxLayout:
        """
        init_mute_controls

        :return: QHBoxLayout
        """
        layout_widgets: list[QWidget] = [QLabel("Mute Channels:")]
        # --- Create mute buttons for channels 1-16
        self.mute_channel_buttons = {}
        for ch in range(1, 17):
            btn = QPushButton(f"{ch}")
            btn.setCheckable(True)
            btn.setFixedWidth(JDXiUIDimensions.SEQUENCER.SQUARE_SIZE)
            btn.setFixedHeight(JDXiUIDimensions.SEQUENCER.SQUARE_SIZE)
            btn.toggled.connect(
                lambda checked, c=ch: self._toggle_channel_mute(c, checked, btn)
            )
            btn.setStyleSheet(JDXiUIStyle.BUTTON_SEQUENCER_SMALL)
            btn.setCheckable(True)
            btn.setChecked(False)
            btn.setStyleSheet(
                generate_sequencer_button_style(
                    not btn.isChecked(), checked_means_inactive=True
                )
            )
            self.mute_channel_buttons[ch] = btn
            layout_widgets.append(btn)

        layout = create_layout_with_widgets(layout_widgets)
        return layout

    def create_apply_all_button_and_label(self) -> QWidget:
        """Add "Apply All Track Changes" button"""
        spec = self.specs["buttons"]["apply_all_track_changes"]
        self.ui.apply_all_track_changes_button = create_jdxi_button_from_spec(
            spec, checkable=False
        )
        apply_all_icon_pixmap = JDXi.UI.Icon.get_icon_pixmap(
            spec.icon, color=JDXi.UI.Style.FOREGROUND, size=20
        )
        apply_all_label_row = QWidget()
        row_widget, self.ui.apply_all_track_changes_label = create_jdxi_row(
            spec.label, icon_pixmap=apply_all_icon_pixmap
        )
        apply_all_label_layout = create_layout_with_widgets(
            widgets=[self.ui.apply_all_track_changes_button, row_widget], spacing=4
        )
        apply_all_label_row.setLayout(apply_all_label_layout)
        return apply_all_label_row

    def _toggle_channel_mute(self, channel: int, is_muted: bool, btn) -> None:
        """
        Toggle mute state for a specific MIDI channel.
        Updates both the track viewer and the player's muted channels state.

        :param channel: int MIDI channel (1-16)
        :param is_muted: bool is the channel muted?
        """
        # Update track viewer's mute state (this will also update track viewer's buttons)
        if hasattr(self.ui, "midi_track_viewer") and self.ui.midi_track_viewer:
            self.ui.midi_track_viewer.toggle_channel_mute(channel, is_muted)
            # Sync the track viewer's mute buttons
            if channel in self.ui.midi_track_viewer.mute_buttons:
                self.ui.midi_track_viewer.mute_buttons[channel].setChecked(is_muted)
                self.ui.midi_track_viewer.mute_buttons[channel].setStyleSheet(
                    generate_sequencer_button_style(
                        not is_muted, checked_means_inactive=True
                    )
                )

        # Update player's muted channels state
        self.midi_state.muted_channels = self.get_muted_channels()

    def _sync_mute_buttons_from_track_viewer(self) -> None:
        """
        Sync mute channel buttons in the USB file controls with the track viewer's state.
        Called when MIDI file is loaded or track viewer's mute state changes.
        """
        if not hasattr(self, "mute_channel_buttons"):
            return

        if hasattr(self.ui, "midi_track_viewer") and self.ui.midi_track_viewer:
            muted_channels = self.ui.midi_track_viewer.get_muted_channels()
            for channel, btn in self.mute_channel_buttons.items():
                btn.blockSignals(True)
                btn.setChecked(channel in muted_channels)
                btn.blockSignals(False)

    def _apply_all_track_changes(self) -> None:
        """
        Apply all Track Name and MIDI Channel changes.
        Calls the track viewer's apply_all_track_changes method.
        """
        if hasattr(self.ui, "midi_track_viewer") and self.ui.midi_track_viewer:
            self.ui.midi_track_viewer.apply_all_track_changes()

    def generate_auto_wav_filename(self) -> Optional[str]:
        """
        Generate an automatic WAV filename based on current date/time and MIDI file name.

        :return: Generated filename path or None if no MIDI file is loaded
        """
        if (
                not self.midi_state.file
                or not hasattr(self.midi_state.file, "filename")
                or not self.midi_state.file.filename
        ):
            return None

        # Get MIDI file path
        midi_path = Path(self.midi_state.file.filename)
        midi_stem = midi_path.stem  # filename without extension

        # Generate timestamp: YYYYMMDD_HHMMSS
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create WAV filename: YYYYMMDD_HHMMSS_<midi_filename>.wav
        wav_filename = f"{timestamp}_{midi_stem}.wav"

        # Use the same directory as the MIDI file, or current directory if no path
        if midi_path.parent:
            wav_path = midi_path.parent / wav_filename
        else:
            wav_path = Path(wav_filename)

        return str(wav_path)

    def update_auto_wav_filename(self) -> None:
        """
        Update the WAV filename automatically if auto-generate is enabled.
        """
        if self.ui.usb_file_auto_generate_checkbox.isChecked():
            auto_filename = self.generate_auto_wav_filename()
            if auto_filename:
                self.ui.usb_file_output_name = auto_filename
                self.ui.usb_file_select.setText(Path(auto_filename).name)
                log.message(f"Auto-generated WAV filename: {auto_filename}")
            else:
                log.warning("⚠️ Cannot auto-generate filename: No MIDI file loaded")

    def on_usb_file_auto_generate_toggled(self, state: Qt.CheckState):
        """
        on_usb_file_auto_generate_toggled

        :param state: Qt.CheckState
        :return:
        """
        self.ui.usb_file_auto_generate_checkbox.setChecked(
            state == JDXi.UI.Constants.CHECKED
        )
        is_enabled = self.ui.usb_file_auto_generate_checkbox.isChecked()
        log.message(
            f"Auto generate filename based on current date and time and Midi file = {is_enabled}"
        )

        # If enabled, generate filename immediately
        if is_enabled:
            self.update_auto_wav_filename()

    def on_usb_file_output_name_changed(self, state: Qt.CheckState):
        """
        on_usb_file_output_name_changed

        :param state: Qt.CheckState
        :return:
        """
        self.ui.usb_file_auto_generate_checkbox.setChecked(
            state == JDXi.UI.Constants.CHECKED
        )
        log.message(
            f"Auto generate filename based on current date and time and Midi file = {self.ui.usb_file_auto_generate_checkbox.isChecked()}"
        )

    def _create_transport_control(
            self,
            spec: TransportSpec,
            layout: QHBoxLayout,
            button_group: QButtonGroup | None,
    ) -> None:
        """Create a transport button + label row"""

        # ---- Button
        btn = create_jdxi_button_from_spec(spec, button_group)
        setattr(self.ui, f"{spec.name}_button", btn)
        layout.addWidget(btn)

        # ---- Label row
        pixmap = JDXi.UI.Icon.get_icon_pixmap(
            spec.icon,
            color=JDXi.UI.Style.FOREGROUND,
            size=20,
        )
        label_row, text_label = create_jdxi_row(spec.text, icon_pixmap=pixmap)
        setattr(self.ui, f"{spec.name}_label", text_label)
        layout.addWidget(label_row)

    def transport_set_state(self, state: str):
        self.ui.play_button.blockSignals(True)
        self.ui.stop_button.blockSignals(True)

        self.ui.play_button.setChecked(state == "play")
        self.ui.stop_button.setChecked(state == "stop")

        self.ui.play_button.blockSignals(False)
        self.ui.stop_button.blockSignals(False)

    def init_transport_controls(self) -> QGroupBox:
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
                "play", JDXi.UI.Icon.PLAY, "Play", self.midi_playback_start, True
            ),
            TransportSpec(
                "stop", JDXi.UI.Icon.STOP, "Stop", self.midi_playback_stop, True
            ),
            TransportSpec(
                "pause",
                JDXi.UI.Icon.PAUSE,
                "Pause",
                self.midi_playback_pause_toggle,
                False,
            ),
        ]

        for spec in controls:
            self._create_transport_control(
                spec, transport_layout, transport_button_group
            )

        return group

    def update_tempo_us_from_worker(self, tempo_us: int) -> None:
        """
        update_tempo_us_from_worker

        :param tempo_us: int tempo in microseconds e.g  500_000
        :return: None
        """
        log.parameter("tempo_us", tempo_us)
        log.message(f"Updating tempo to {tempo_us} microseconds from worker")
        # self.refill_midi_message_buffer()
        self.ui_display_set_tempo_usecs(tempo_us)

    def update_playback_worker_tempo_us(self, tempo_us: int) -> None:
        """
        update_playback_worker_tempo_us

        :param tempo_us: tempo in microseconds e.g  500_000
        :return: None
        """
        log.parameter("tempo_us", tempo_us)
        log.message(f"Updating tempo to {tempo_us} microseconds from editor")
        if self.midi_playback_worker:
            self.midi_playback_worker.update_tempo(tempo_us)

    def setup_worker(self):
        """
        setup_worker

        :return: None

        Setup the worker and thread for threaded playback using QTimer
        """
        # Clean up any previous worker/thread
        if self.midi_state.playback_thread:
            self.midi_state.playback_thread.quit()
            self.midi_state.playback_thread.wait()
            self.midi_state.playback_thread.deleteLater()
            self.midi_playback_worker = None

        # Create worker with correct initial tempo if available
        initial_tempo = getattr(
            self.midi_state, "tempo_at_position", Midi.TEMPO.BPM_120_USEC
        )
        self.midi_playback_worker = MidiPlaybackWorker(parent=self)
        self.midi_playback_worker.set_tempo.connect(self.update_tempo_us_from_worker)
        self.midi_playback_worker.position_tempo = initial_tempo
        self.midi_playback_worker.initial_tempo = initial_tempo
        log.message(f"self.midi_playback_worker: {self.midi_playback_worker}")
        # self.midi_playback_worker.set_editor(self)

        self.midi_state.playback_thread = QThread()
        self.midi_playback_worker.moveToThread(self.midi_state.playback_thread)
        self.midi_playback_worker.result_ready.connect(
            self.midi_playback_worker_handle_result
        )  # optional for UI update

        # QTimer lives in the main thread, but calls worker.do_work()
        self.midi_state.timer = QTimer(self)
        self.midi_state.timer.setInterval(JDXi.UI.Constants.TIMER_INTERVAL)
        # Note: Worker connection is handled in midi_playback_start() to avoid conflicts

        self.midi_state.playback_thread.start()

    def midi_playback_worker_stop(self):
        """
        midi_playback_worker_stop

        :return: None
        """
        if self.midi_state.timer.isActive():
            self.midi_state.timer.stop()

        if self.midi_playback_worker:
            self.midi_playback_worker.stop()  # signal to stop processing

        if self.midi_state.playback_thread:
            self.midi_state.playback_thread.quit()
            self.midi_state.playback_thread.wait()
            self.midi_state.playback_thread.deleteLater()
            self.midi_state.playback_thread = None
            self.midi_playback_worker = None

    def on_suppress_program_changes_toggled(self, state: Qt.CheckState) -> None:
        """
        on_suppress_program_changes_toggled

        :param state: Qt.CheckState
        :return:    None
        """
        self.midi_state.suppress_program_changes = state == JDXi.UI.Constants.CHECKED
        log.message(
            f"Suppress MIDI Program Changes = {self.midi_state.suppress_program_changes}"
        )

    def on_suppress_control_changes_toggled(self, state: Qt.CheckState):
        """
        on_suppress_control_changes_toggled

        :param state: Qt.CheckState
        :return:
        """
        self.midi_state.suppress_control_changes = state == JDXi.UI.Constants.CHECKED
        log.message(
            f"Suppress MIDI Control Changes = {self.midi_state.suppress_control_changes}"
        )

    def on_usb_save_recording_toggled(self, state: Qt.CheckState):
        """
        on_usb_save_recording_toggled

        :param state: Qt.CheckState
        :return:
        """
        self.usb_recorder.file_save_recording = state == JDXi.UI.Constants.CHECKED
        log.message(f"save USB recording = {self.usb_recorder.file_save_recording}")

    def usb_populate_devices(self) -> list:
        """
        usb_populate_devices

        usb port selection

        :return: list List of USB devices
        """
        usb_devices = self.usb_recorder.list_devices()
        self.ui.usb_port_select_combo.clear()
        self.ui.usb_port_select_combo.addItems(usb_devices)
        self.usb_port_jdxi_auto_connect(usb_devices)
        return usb_devices

    def usb_port_jdxi_auto_connect(self, usb_devices: list) -> None:
        """
        usb_port_jdxi_auto_connect

        :param usb_devices: list
        :return: None

        Auto-select the first matching device
        """
        pattern = re.compile(r"jd-?xi", re.IGNORECASE)
        for i, item in enumerate(usb_devices):
            if pattern.search(item):
                self.ui.usb_port_select_combo.setCurrentIndex(i)
                self.usb_recorder.usb_port_input_device_index = i
                log.message(f"Auto-selected {item}")
                break

    def usb_start_recording(self, recording_rate: int = pyaudio.paInt16):
        """
        usb_start_recording

        :param recording_rate: int
        :return: None
        Start recording in a separate thread
        """
        try:
            # If auto-generate is enabled, regenerate filename with fresh timestamp
            if self.ui.usb_file_auto_generate_checkbox.isChecked():
                self.update_auto_wav_filename()

            if not self.ui.usb_file_output_name:
                log.warning(
                    "⚠️ No output file selected for WAV recording. Please select a file or enable auto-generate."
                )
                show_message_box_from_spec(self.specs["message_box"]["no_output_file"])
                return

            log.message(f"🎙️ Starting WAV recording to: {self.ui.usb_file_output_name}")
            log.message(
                f"🎙️ Recording duration: {self.midi_state.file_duration_seconds} seconds"
            )

            selected_index = self.ui.usb_port_select_combo.currentIndex()
            log.message(f"🎙️ Using USB input device index: {selected_index}")

            start_recording(
                self.usb_recorder,
                self.midi_state.file_duration_seconds,
                self.ui.usb_file_output_name,
                recording_rate,
                selected_index,
            )
        except Exception as ex:
            log.error(f"❌ Error {ex} occurred starting recording")
            import traceback

            log.error(traceback.format_exc())
            show_message_box_from_spec(
                self.specs["message_box"]["error_saving_file"],
                message=f"Error {ex} occurred starting recording",
            )

    def usb_select_recording_file(self):
        """Open a file picker dialog to select output .wav file."""
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save Recording As",
            "",  # starting directory
            "WAV files (*.wav)",  # filter
        )
        if file_name:
            self.ui.usb_file_select.setText(file_name)
            self.ui.usb_file_output_name = file_name
        else:
            self.ui.usb_file_output_name = ""

    def midi_save_file(self) -> None:
        """
        midi_save_file

        :return: None
        Save the current MIDI file to disk.
        """

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save MIDI File", "", "MIDI Files (*.mid)"
        )
        if file_path:
            self.ui.midi_track_viewer.midi_file.save(file_path)
            file_name = f"Saved: {Path(file_path).name}"
            self.ui.digital_title_file_name.setText(file_name)
            # Update digital to show tempo only (no bar when not playing)
            if self.current_tempo_bpm is not None:
                self.ui.digital_title_file_name.set_upper_display_text(
                    f"Tempo: {round(self.current_tempo_bpm)} BPM"
                )

    def midi_load_file(self) -> None:
        """
        Load a MIDI file and initialize parameters
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open MIDI File", "", "MIDI Files (*.mid)"
        )
        if not file_path:
            return

        self.midi_load_file_from_path(file_path)

    def midi_load_file_from_path(self, file_path: str) -> None:
        """
        Load a MIDI file from a given path and initialize parameters.

        :param file_path: Path to the MIDI file
        """
        if not file_path:
            return

        self.midi_state.file = MidiFile(file_path)
        # Store filename in the MidiFile object for later use
        self.midi_state.file.filename = file_path
        file_name = f"Loaded: {Path(file_path).name}"
        self.ui.digital_title_file_name.setText(file_name)
        # Update digital to show tempo only (no bar when not playing)
        if self.current_tempo_bpm is not None:
            self.ui.digital_title_file_name.set_upper_display_text(
                f"Tempo: {round(self.current_tempo_bpm)} BPM"
            )
        self.ui.midi_track_viewer.clear()
        self.ui.midi_track_viewer.set_midi_file(self.midi_state.file)
        # Sync mute buttons after loading MIDI file
        self._sync_mute_buttons_from_track_viewer()

        # Auto-generate WAV filename if checkbox is enabled
        if self.ui.usb_file_auto_generate_checkbox.isChecked():
            self.update_auto_wav_filename()

        # Ensure ticks_per_beat is available early
        self.ticks_per_beat = self.midi_state.file.ticks_per_beat

        initial_track_tempos = self.detect_initial_tempo()

        self.ui_display_set_tempo_usecs(self.midi_state.tempo_initial)
        self.midi_state.tempo_at_position = (
            self.midi_state.tempo_initial
        )  # Set initial tempo for playback
        log.parameter("Initial track tempos", initial_track_tempos)
        self.midi_channel_select()
        self.midi_extract_events()
        self.setup_worker()
        self.calculate_duration()
        self.calculate_tick_duration()
        self.ui_position_slider_reset()

        # Notify Pattern Sequencer if it exists
        self._notify_pattern_sequencer_file_loaded()

        # Add to recent files if parent has recent_files_manager
        if (
                hasattr(self.parent, "recent_files_manager")
                and self.parent.recent_files_manager
        ):
            try:
                self.parent.recent_files_manager.add_file(file_path)
                if hasattr(self.parent, "_update_recent_files_menu"):
                    # Check if menu still exists before updating
                    if (
                            hasattr(self.parent, "recent_files_menu")
                            and self.parent.recent_files_menu is not None
                    ):
                        try:
                            self.parent._update_recent_files_menu()
                        except RuntimeError:
                            # Menu was deleted, skip update
                            log.debug("Recent files menu was deleted, skipping update")
            except Exception as ex:
                log.debug(f"Error updating recent files menu: {ex}")

    def calculate_tick_duration(self):
        """
        calculate_tick_duration

        :return:
        Calculate the duration of a single MIDI tick in seconds.
        """
        # Guard: ensure ticks_per_beat is set
        if not hasattr(self, "ticks_per_beat") or self.ticks_per_beat is None:
            # Fallback to current file's ticks_per_beat if available
            if self.midi_state.file is not None:
                self.ticks_per_beat = getattr(
                    self.midi_state.file, "ticks_per_beat", 480
                )
            else:
                self.ticks_per_beat = 480
        self.tick_duration = (
                self.midi_state.tempo_at_position
                / Midi.TEMPO.CONVERT_SEC_TO_USEC
                / self.ticks_per_beat
        )

    def calculate_duration(self) -> None:
        """
        calculate_duration

        :return: None
        Accurate Total Duration Calculation
        """
        # Handle empty events list gracefully
        if not getattr(self.midi_state, "events", None):
            self.midi_total_ticks = 0
        else:
            self.midi_total_ticks = max(t for t, _, _ in self.midi_state.events)
        self.midi_state.file_duration_seconds = get_total_duration_in_seconds(
            self.midi_state.file
        )

    def midi_channel_select(self) -> None:
        """
        midi_channel_select

        :return: None

        Select a suitable MIDI channel for playback - detects a "reasonable" playback channel
        """
        selected_channel = None
        for track in self.midi_state.file.tracks:
            for msg in track:
                if (
                        hasattr(msg, "channel")
                        and msg.channel in self.midi_preferred_channels
                ):
                    selected_channel = msg.channel
                    break
            if selected_channel is not None:
                break
        if selected_channel is None:
            selected_channel = 0  # default to channel 1 if nothing suitable found
            log.warning("No suitable channel found; defaulting to channel 1")
        self.midi_state.channel_selected = selected_channel

    def midi_extract_events(self) -> None:
        """
        midi_extract_events

        :return: None
        Extract events from the MIDI file and store them in the midi_state.
        """
        events = []
        for track_index, track in enumerate(self.midi_state.file.tracks):
            abs_time = 0
            for msg in track:
                abs_time += msg.time
                events.append((abs_time, msg, track_index))
        # Ensure ticks_per_beat is set before calculations
        if not hasattr(self, "ticks_per_beat") or self.ticks_per_beat is None:
            self.ticks_per_beat = getattr(self.midi_state.file, "ticks_per_beat", 480)
        self.calculate_tick_duration()
        self.midi_state.events = sorted(events, key=lambda x: x[0])

    def detect_initial_tempo(self) -> dict[int, int]:
        """
        detect_initial_tempo

        :return: dict[int, int]
        Detect Initial Tempo from the UI
        """
        self.midi_state.tempo_initial = Midi.TEMPO.BPM_120_USEC
        initial_track_tempos = {}
        for track_number, track in enumerate(self.midi_state.file.tracks):
            for msg in track:
                if msg.type == "set_tempo":
                    self.midi_state.tempo_initial = msg.tempo
                    log.parameter("self.tempo", self.midi_state.tempo_initial)
                    initial_track_tempos[track_number] = self.midi_state.tempo_initial
                    break
            else:
                continue  # no tempo message in this track
            break  # found tempo, break outer loop
        return initial_track_tempos

    def ui_display_set_tempo_usecs(self, tempo_usecs: int) -> None:
        """
        ui_display_set_tempo_usecs

        :param tempo_usecs: int tempo in microseconds
        :return: None
        Set the tempo in the UI and log it.
        """
        log.message(f"Setting tempo to {tempo_usecs} microseconds on UI")
        self.on_tempo_usecs_changed(tempo_usecs)
        bpm = tempo2bpm(tempo_usecs)
        log.parameter("tempo_bpm", bpm)
        log.message(f"Setting tempo to {bpm} BPM on UI")
        self.set_display_tempo_bpm(bpm)

    def set_display_tempo_bpm(self, tempo_bpm: float) -> None:
        """
        set_display_tempo_bpm

        :param tempo_bpm: float tempo in BPM
        :return: None
        Set the tempo in the UI and log it. Also pushes tempo to Pattern Sequencer
        so both editors stay in sync when using the same playback pipeline.
        """
        self.current_tempo_bpm = tempo_bpm
        self.update_upper_display_with_tempo_and_bar()
        log.parameter("tempo_bpm", tempo_bpm)
        self._push_tempo_to_pattern_sequencer(tempo_bpm)

    def update_upper_display_with_tempo_and_bar(
            self, elapsed_time: Optional[float] = None
    ) -> None:
        """
        Update the upper digital with tempo and optionally bar number.

        :param elapsed_time: Optional elapsed time for bar calculation. If None, uses current playback state.
        """
        if self.current_tempo_bpm is None:
            return

        tempo_text = f"Tempo: {round(self.current_tempo_bpm)} BPM"

        # Append bar number if playing or paused
        if elapsed_time is not None or (
                self.midi_state.timer
                and (self.midi_state.timer.isActive() or self.midi_state.playback_paused)
        ):
            if elapsed_time is None and self.midi_state.playback_start_time:
                elapsed_time = time.time() - self.midi_state.playback_start_time

            if elapsed_time is not None and self.midi_state.file:
                current_bar = self.calculate_current_bar(elapsed_time)
                if current_bar is not None:
                    tempo_text += f" | Bar {int(current_bar)}"

        self.ui.digital_title_file_name.set_upper_display_text(tempo_text)

    def turn_off_effects(self) -> None:
        """
        Turn off all effects (Effect 1, Effect 2, Delay, Reverb) when starting playback.
        This prevents distortion and other effects from being accidentally enabled.
        """
        if not self.midi_helper:
            return

        try:
            # Create SysEx composer and address for effects
            sysex_composer = JDXiSysExComposer()
            address = JDXiSysExAddress(
                JDXiSysExAddressStartMSB.TEMPORARY_PROGRAM,
                JDXiSysExOffsetSystemUMB.COMMON,
                JDXiSysExOffsetProgramLMB.COMMON,
                Midi.VALUE.ZERO,
            )

            # Turn off Effect 1: Set level to 0 and type to Thru (0)
            efx1_address = address.add_offset((0, 2, 0))
            efx1_level_msg = sysex_composer.compose_message(
                address=efx1_address, param=Effect1Param.EFX1_LEVEL, value=0
            )
            efx1_type_msg = sysex_composer.compose_message(
                address=efx1_address,
                param=Effect1Param.EFX1_TYPE,
                value=0,  # Thru (no effect)
            )

            # Turn off Effect 2: Set level to 0 and type to OFF (0)
            efx2_address = address.add_offset((0, 4, 0))
            efx2_level_msg = sysex_composer.compose_message(
                address=efx2_address, param=Effect2Param.EFX2_LEVEL, value=0
            )
            efx2_type_msg = sysex_composer.compose_message(
                address=efx2_address, param=Effect2Param.EFX2_TYPE, value=0  # OFF
            )

            # Turn off Delay: Set level to 0
            delay_address = address.add_offset((0, 6, 0))
            delay_level_msg = sysex_composer.compose_message(
                address=delay_address, param=DelayParam.DELAY_LEVEL, value=0
            )

            # Turn off Reverb: Set level to 0
            reverb_address = address.add_offset((0, 8, 0))
            reverb_level_msg = sysex_composer.compose_message(
                address=reverb_address, param=ReverbParam.REVERB_LEVEL, value=0
            )

            # Send all messages
            messages = [
                efx1_level_msg,
                efx1_type_msg,
                efx2_level_msg,
                efx2_type_msg,
                delay_level_msg,
                reverb_level_msg,
            ]

            for msg in messages:
                self.midi_helper.send_midi_message(msg)
                time.sleep(0.01)  # Small delay between messages

            log.message(
                "🎛️ Turned off all effects (Effect 1, Effect 2, Delay, Reverb) at playback start"
            )

        except Exception as ex:
            log.error(f"❌ Error turning off effects: {ex}")
            import traceback

            log.error(traceback.format_exc())

    def midi_playback_start(self):
        """
        Start playback of the MIDI file from the beginning (or resume if paused).
        """
        # Reset position slider to beginning
        self.transport_set_state("play")
        self.ui_position_slider_reset()

        # Turn off all effects when starting playback (prevents accidental distortion)
        # if not self.midi_state.playback_paused:
        #    self.turn_off_effects()

        if PROFILING:
            self.profiler = cProfile.Profile()
            self.profiler.enable()

        if not self.midi_state.file or not self.midi_state.events:
            return

        # If not paused, reset everything to start from beginning
        if not self.midi_state.playback_paused:
            # Clear buffer and reset playback position to beginning
            self.midi_state.event_buffer.clear()
            self.midi_state.buffer_end_time = 0
            self.midi_state.event_index = 0
            self.midi_state.playback_start_time = time.time()
        # If paused, resume from current position (pause logic handles this)

        # Ensure worker is properly set up before connecting
        self.setup_playback_worker()

        # Disconnect all existing connections first
        try:
            self.midi_state.timer.timeout.disconnect()  # Disconnect all
            log.debug("Disconnected all timeout signals")
        except Exception as ex:
            log.debug(f"Disconnecting all timeout signals: {ex}")

        # Connect worker if available
        try:
            if self.midi_playback_worker is not None:
                self.midi_state.timer.timeout.connect(self.midi_playback_worker.do_work)
                log.message(
                    "Success: Connected midi_playback_worker.do_work to timeout"
                )
            else:
                log.warning("⚠️ midi_playback_worker is None, skipping connection")
        except Exception as ex:
            log.error(f"Error {ex} connecting worker to timeout")

        # Connect UI update
        try:
            self.midi_state.timer.timeout.connect(self.midi_play_next_event)
            log.message("Success: Connected midi_play_next_event to timeout")
        except Exception as ex:
            log.error(f"Error {ex} connecting midi_play_next_event to timeout")

        if self.usb_recorder.file_save_recording:
            recording_rate = "32bit"  # Default to 32-bit recording
            try:
                rate = self.usb_recorder.usb_recording_rates.get(
                    recording_rate, pyaudio.paInt16
                )
                self.usb_start_recording(recording_rate=rate)
            except Exception as ex:
                log.error(f"Error {ex} occurred starting USB recording")

        try:
            # Start the playback worker (already set up above)
            self.start_playback_worker()

        except Exception as ex:
            log.error(f"Error {ex} occurred starting playback")

    def setup_playback_worker(self):
        """
        setup_playback_worker

        :return: None
        Setup the MIDI playback worker (prepare buffered messages, etc.)
        """
        # Setup worker if not already initialized
        if not self.midi_state.playback_thread or not self.midi_playback_worker:
            self.setup_worker()
        self.ui_ensure_timer_connected()
        # === Prepare the buffered events for the worker ===
        self.midi_state.muted_channels = self.get_muted_channels()
        self.midi_state.muted_tracks = self.get_muted_tracks()
        self.midi_message_buffer_refill()
        self.midi_playback_worker.setup(
            buffered_msgs=self.midi_state.buffered_msgs,
            midi_out_port=self.midi_helper.midi_out,
            ticks_per_beat=self.midi_state.file.ticks_per_beat,
            play_program_changes=not self.midi_state.suppress_program_changes,
            start_time=self.midi_state.playback_start_time,
            initial_tempo=self.midi_state.tempo_at_position,
        )

    def start_playback_worker(self):
        """
        start_playback_worker

        :return: None
        Start the timer for actual playback.
        """
        self.midi_state.timer.start()

    def setup_and_start_playback_worker(self):
        """
        setup_and_start_playback_worker

        :return: None
        Setup the MIDI playback worker and start the timer.
        """
        self.setup_playback_worker()
        self.start_playback_worker()

    def initialize_midi_state(self) -> None:
        """
        Initialize muted tracks, muted channels, and buffered messages.
        """
        if self.midi_state.muted_tracks is None:
            self.midi_state.muted_tracks = set()
        if self.midi_state.muted_channels is None:
            self.midi_state.muted_channels = set()
        if self.midi_state.playback_start_time is None:
            self.midi_state.playback_start_time = time.time()
        self.midi_state.buffered_msgs = []

    def calculate_start_tick(self) -> Optional[int]:
        """
        Calculate the start tick based on elapsed playback time.
        :return: Start tick or None if an error occurs.
        """
        try:
            # Check if playback_start_time is initialized
            if self.midi_state.playback_start_time is None:
                log.debug("playback_start_time not initialized, using 0")
                return 0

            elapsed_time_secs = time.time() - self.midi_state.playback_start_time
            return int(
                mido.second2tick(
                    second=elapsed_time_secs,
                    ticks_per_beat=self.midi_state.file.ticks_per_beat,
                    tempo=self.midi_state.tempo_at_position,
                )
            )
        except Exception as ex:
            log.error(f"Error converting playback start time to ticks: {ex}")
            return None

    def is_track_muted(self, track_index: int) -> bool:
        """
        is_track_muted

        :param track_index: Index of the track to check.
        :return: True if the track is muted, otherwise False.

        Check if the track is muted.
        """
        return track_index in self.midi_state.muted_tracks

    def is_channel_muted(self, channel_index: int) -> bool:
        """
        is_channel_muted

        :param channel_index: Index of the track to check.
        :return: True if the channel is muted, otherwise False.

        Check if the channel is muted.
        """
        return (
                channel_index + Midi.CHANNEL.BINARY_TO_DISPLAY
                in self.midi_state.muted_channels
        )

    def handle_set_tempo(self, msg: mido.Message, absolute_time_ticks: int) -> None:
        """
        handle_set_tempo

        :param absolute_time_ticks: int
        :param msg: The MIDI message to process.
        Handle 'set_tempo' messages in a MIDI track.
        """
        if self.midi_state.custom_tempo_force:
            self.midi_state.tempo_at_position = self.midi_state.custom_tempo
            log.message(
                f"🔄 Forcing custom tempo: {self.midi_state.tempo_at_position} usec / quarter note"
            )
        else:
            self.midi_state.tempo_at_position = msg.tempo

        # Store tempo change for later playback - don't update worker immediately
        self.midi_state.buffered_msgs.append(
            (absolute_time_ticks, None, self.midi_state.tempo_at_position)
        )  # Store tempo change

    def buffer_message(self, absolute_time_ticks: int, msg: mido.Message) -> None:
        """
        Add a MIDI message to the buffer.
        :param absolute_time_ticks: Absolute tick of the message.
        :param msg: The MIDI message to buffer.
        """
        self.midi_state.buffered_msgs.append(
            (absolute_time_ticks, msg.bytes(), self.midi_state.tempo_at_position)
        )

    def buffer_message_with_tempo(
            self, absolute_time_ticks: int, msg: mido.Message, tempo: int
    ) -> None:
        """
        Add a MIDI message to the buffer with a specific tempo.
        :param absolute_time_ticks: Absolute tick of the message.
        :param msg: The MIDI message to buffer.
        :param tempo: The tempo that was active when this message was created.
        """
        self.midi_state.buffered_msgs.append((absolute_time_ticks, msg.bytes(), tempo))

    def midi_message_buffer_refill(self) -> None:
        """
        midi_message_buffer_refill

        :return: None
        Preprocess MIDI tracks into a sorted list of (absolute_ticks, raw_bytes, tempo) tuples.
        Meta messages are excluded except for set_tempo.
        """

        self.initialize_midi_state()

        start_tick = self.calculate_start_tick()
        log.message(f"🎵 calculate_start_tick returned: {start_tick}")
        if start_tick is None:
            log.error("🎵 calculate_start_tick returned None, skipping buffer refill")
            return

        self.process_tracks(start_tick)

        self.midi_state.buffered_msgs.sort(key=lambda x: x[0])

        # Fix tempo assignments - each message should use the tempo that was active at its tick
        self._fix_buffer_tempo_assignments()

        # Print segment statistics
        self._print_segment_statistics()

        # Debug logging
        log.message(
            f"🎵 Buffered {len(self.midi_state.buffered_msgs)} messages for playback"
        )
        if len(self.midi_state.buffered_msgs) > 0:
            log.message(f"🎵 First few messages: {self.midi_state.buffered_msgs[:3]}")

    def process_tracks(self, start_tick: int) -> None:
        """
        process_tracks

        :param start_tick: int
        :return:
        """
        log.message(
            f"🎵 Processing {len(self.midi_state.file.tracks)} tracks, start_tick: {start_tick}"
        )
        for i, track in enumerate(self.midi_state.file.tracks):
            if self.is_track_muted(i):
                log.message(
                    f"🚫 Muted track {i + Midi.CHANNEL.DISPLAY_TO_BINARY} ({track.name}): "
                    "buffering only program change and bank select so instrument still receives them"
                )
                self.process_track_messages(
                    start_tick, track, only_program_and_bank_select=True
                )
                continue
            log.message(f"🎵 Processing track {i} with {len(track)} messages")
            self.process_track_messages(start_tick, track)

    def _is_program_or_bank_select(self, msg: mido.Message) -> bool:
        """True if message is program change or bank select (CC#0, CC#32)."""
        if msg.type == "program_change":
            return True
        if msg.type == "control_change" and msg.control in (0, 32):
            return True
        return False

    def process_track_messages(
            self,
            start_tick: int,
            track: mido.MidiTrack,
            only_program_and_bank_select: bool = False,
    ) -> None:
        """
        process_track_messages

        :param start_tick: int The starting tick from which to begin processing.
        :param track: mido.MidiTrack The MIDI track to process.
        :param only_program_and_bank_select: If True, only buffer program_change and CC#0/CC#32 (used for muted tracks).
        :return: None

        Process messages in a MIDI track from a given starting tick.
        """
        absolute_time_ticks = 0
        messages_processed = 0
        messages_buffered = 0
        current_tempo = self.midi_state.tempo_at_position  # Track tempo as we go

        for msg in track:
            absolute_time_ticks += msg.time
            messages_processed += 1

            if absolute_time_ticks < start_tick:
                continue  # Skip messages before the start tick

            if msg.type == "set_tempo":
                self.handle_set_tempo(msg, absolute_time_ticks)
                current_tempo = (
                    self.midi_state.tempo_at_position
                )  # Update current tempo
                messages_buffered += 1
            elif not msg.is_meta:
                if only_program_and_bank_select:
                    if not self._is_program_or_bank_select(msg):
                        continue
                    # Buffer PC and bank select from muted tracks so instrument receives them
                elif hasattr(msg, "channel") and self.is_channel_muted(msg.channel):
                    # Always buffer program change and bank select so instrument receives them even when channel is muted
                    if not self._is_program_or_bank_select(msg):
                        continue
                self.buffer_message_with_tempo(absolute_time_ticks, msg, current_tempo)
                messages_buffered += 1

        log.message(
            f"🎵 Track processed: {messages_processed} messages, {messages_buffered} buffered"
        )

    def get_muted_tracks(self):
        """
        get_muted_tracks

        :return: None
        Get the muted tracks from the MIDI track viewer.
        """
        muted_tracks_raw = self.ui.midi_track_viewer.get_muted_tracks()
        muted_tracks = {int(t) for t in muted_tracks_raw if not isinstance(t, set)}
        for track in muted_tracks:
            log.parameter("Muted track", track)
        return muted_tracks

    def get_muted_channels(self):
        """
        get_muted_channels

        :return: None
        Get the muted channels from the MIDI track viewer.
        """
        muted_channels_raw = self.ui.midi_track_viewer.get_muted_channels()
        muted_channels = {int(c) for c in muted_channels_raw if not isinstance(c, set)}
        log.parameter("Muted channels", muted_channels)
        for channel in muted_channels:
            log.parameter("Muted channel", channel)
        return muted_channels

    def on_tempo_usecs_changed(self, tempo: int):
        """
        on_tempo_usecs_changed

        :param tempo: int
        :return: None
        """
        self.midi_state.tempo_at_position = tempo

    def on_tempo_bpm_changed(self, bpm: float):
        """
        on_tempo_bpm_changed

        :param bpm: float
        :return: None
        """
        tempo = bpm2tempo(bpm)
        self.on_tempo_usecs_changed(tempo)

    def midi_play_next_event(self):
        """
        UI update: Update slider and label to reflect playback progress.
        """
        try:
            if self.midi_state.playback_start_time is None:
                return
            now = time.time()
            elapsed_time = now - self.midi_state.playback_start_time
            self.ui_midi_file_position_slider_set_position(elapsed_time)
        except Exception as ex:
            log.error(f"Error {ex} occurred updating playback UI")

    def ui_midi_file_position_slider_set_position(self, elapsed_time: float) -> None:
        """
        ui.midi_file_position_slider_set_position

        :param elapsed_time: float
        :return: None
        Update the slider position and label based on elapsed time.
        """
        if self.ui.midi_file_position_slider.isSliderDown():
            return  # Don't update while user is dragging

        new_value = int(elapsed_time)
        current_value = self.ui.midi_file_position_slider.value()

        if abs(new_value - current_value) >= 1:  # Only update if full second has passed
            self.ui.midi_file_position_slider.setValue(new_value)
            self.ui_position_label_set_time(elapsed_time)

    def midi_scrub_position(self):
        """
        Updates the MIDI playback state based on the scrub position.
        """
        if not self.is_midi_ready():
            log.message(
                "Either self.midi.file or self.midi.events not present, returning"
            )
            return

        self.stop_playback()
        target_time = self.get_target_time()
        self.update_event_index(target_time)
        self.update_playback_start_time(target_time)
        self.stop_all_notes()
        self.prepare_for_playback()

        # Update digital with tempo and bar for scrubbed position
        self.update_upper_display_with_tempo_and_bar(target_time)

    def is_midi_ready(self) -> bool:
        """
        Checks if the MIDI file and events are available.
        """
        return bool(self.midi_state.file and self.midi_state.events)

    def stop_playback(self) -> None:
        """
        Stops playback and resets the paused state.
        """
        self.midi_playback_worker_stop()
        self.midi_playback_worker_disconnect()
        self.midi_state.playback_paused = False  # Optional: reset paused state

    def get_target_time(self) -> float:
        """
        Retrieves the target time from the slider and logs it.
        """
        target_time = self.ui.midi_file_position_slider.value()
        log.parameter("target_time", target_time)
        return target_time

    def update_event_index(self, target_time: float) -> None:
        """
        Finds and updates the event index based on the target time.
        """
        for i, (tick, _, _) in enumerate(self.midi_state.events):
            if tick * self.tick_duration >= target_time:
                self.midi_state.event_index = i
                log.parameter(
                    "self.midi_state.event_index now", self.midi_state.event_index
                )
                return
        self.midi_state.event_index = 0  # Default to the start if no match

    def update_playback_start_time(
            self, target_time: float
    ) -> None:  # pylint: disable=unused-argument
        """
        Adjusts the playback start time based on the scrub position.
        """
        scrub_tick = self.midi_state.events[self.midi_state.event_index][0]
        scrub_time = scrub_tick * self.tick_duration
        self.midi_state.playback_start_time = time.time() - scrub_time

    def stop_all_notes(self) -> None:
        """
        Sends Control Change 123 and note_off messages to silence all notes.
        """
        if not self.midi_helper:
            return

        for ch in range(16):
            # CC 123 = All Notes Off
            self.midi_helper.midi_out.send_message(
                mido.Message("control_change", control=123, value=0, channel=ch).bytes()
            )

            # Extra safety in case the synth ignores CC123
            for note in range(128):
                self.midi_helper.midi_out.send_message(
                    mido.Message("note_off", note=note, velocity=0, channel=ch).bytes()
                )

    def prepare_for_playback(self) -> None:
        """
        Clears the event buffer and starts the playback worker.
        """
        self.midi_state.event_buffer.clear()
        self.setup_playback_worker()

        # Reconnect worker and UI update signals to timer (needed after scrubbing)
        try:
            # Disconnect all existing connections first
            self.midi_state.timer.timeout.disconnect()
        except Exception:
            pass  # Already disconnected or not connected

        # Connect worker if available
        if self.midi_playback_worker is not None:
            try:
                self.midi_state.timer.timeout.connect(self.midi_playback_worker.do_work)
                log.message(
                    "Success: Reconnected midi_playback_worker.do_work to timeout after scrub"
                )
            except Exception as ex:
                log.error(f"Error {ex} reconnecting worker to timeout")

        # Connect UI update
        try:
            self.midi_state.timer.timeout.connect(self.midi_play_next_event)
            log.message(
                "Success: Reconnected midi_play_next_event to timeout after scrub"
            )
        except Exception as ex:
            log.error(f"Error {ex} reconnecting midi_play_next_event to timeout")

        self.start_playback_worker()

    def midi_playback_stop(self):
        """
        Stops playback and resets everything to the beginning.
        """
        self.transport_set_state("stop")
        # Reset the worker's index before stopping (if it exists)
        if self.midi_playback_worker:
            self.midi_playback_worker.index = 0
            self.midi_playback_worker.should_stop = True

        # Stop the playback worker
        self.stop_playback_worker()

        # Reset all MIDI state (including event_index and playback_start_time)
        self.reset_midi_state()

        # Reset UI position slider to beginning
        self.ui_position_slider_reset()

        # Stop all notes and reset tempo
        self.stop_all_notes()
        self.reset_tempo()
        self.clear_active_notes()

        # Clear event buffer to ensure clean state
        self.midi_state.event_buffer.clear()
        self.midi_state.buffer_end_time = 0

        # Stop USB recording if active
        self.usb_recorder.stop_recording()

        # Update digital to show tempo only (no bar when stopped)
        if self.current_tempo_bpm is not None:
            self.ui.digital_title_file_name.set_upper_display_text(
                f"Tempo: {round(self.current_tempo_bpm)} BPM"
            )

        # Logging and profiling
        self.log_event_buffer()
        self.perform_profiling()

        log.message("MIDI playback stopped and reset to beginning")

    def stop_playback_worker(self):
        """
        Stops and disconnects the playback worker.
        """
        self.midi_playback_worker_stop()
        self.midi_playback_worker_disconnect()
        self.midi_play_next_event_disconnect()

    def reset_midi_state(self):
        """
        Resets MIDI state variables.
        """
        self.midi_state.playback_paused = False
        self.midi_state.event_index = 0
        self.midi_state.playback_start_time = (
            None  # Reset start time so playback starts from beginning
        )
        self.midi_state.playback_paused_time = None  # Clear paused time

    def reset_tempo(self):
        """
        Resets the tempo to the initial value.
        """
        self.ui_display_set_tempo_usecs(self.midi_state.tempo_initial)

    def clear_active_notes(self) -> None:
        """
        Clears the active notes.
        """
        self.midi_state.active_notes.clear()

    def log_event_buffer(self) -> None:
        """
        log_event_buffer

        :return: None

        Logs the event buffer for debugging.
        """
        log.parameter("self.midi.event_buffer", self.midi_state.event_buffer)
        for t, msg in self.midi_state.event_buffer[:20]:
            log.message(f"Queued @ {t:.3f}s: {msg}")

    def perform_profiling(self) -> None:
        """
        perform_profiling

        :return: None
        Performs profiling and logs the results.
        """
        if PROFILING:
            self.profiler.disable()
            s = io.StringIO()
            sortby = "cumtime"  # or 'tottime'
            ps = pstats.Stats(self.profiler, stream=s).sort_stats(sortby)
            ps.print_stats(50)  # Top 50 entries
            log.message(s.getvalue())

    def midi_play_next_event_disconnect(self) -> None:
        """
        midi_play_next_event_disconnect

        :return: None
        Disconnect the midi_play_next_event from the timer's timeout signal.
        """
        # Check if timer is initialized
        if not hasattr(self.midi_state, "timer") or self.midi_state.timer is None:
            log.debug("Timer not initialized, skipping disconnect")
            return

        # Disconnect midi_play_next_event safely
        try:
            self.midi_state.timer.timeout.disconnect(self.midi_play_next_event)
            log.debug(
                "Successfully disconnected midi_play_next_event from timeout signal"
            )
        except TypeError:
            # Signal was not connected
            log.debug("midi_play_next_event was not connected to timeout signal")
        except Exception as ex:
            log.debug(f"Could not disconnect midi_play_next_event: {ex}")

    def midi_playback_worker_disconnect(self) -> None:
        """
        midi_playback_worker_disconnect

        :return: None
        Disconnect the midi_playback_worker.do_work from the timer's timeout signal.
        """
        try:
            if (
                    hasattr(self, "midi_playback_worker")
                    and self.midi_playback_worker is not None
            ):
                self.midi_state.timer.timeout.disconnect(
                    self.midi_playback_worker.do_work
                )
        except TypeError:
            log.warning("⚠️ do_work was not connected to timeout signal.")
        except Exception as ex:
            log.warning(f"⚠️ Could not disconnect do_work: {ex}")

    def ui_position_slider_reset(self) -> None:
        """
        position_slider_reset

        :return: None
        Reset the position slider and label to initial state.
        """
        self.ui.midi_file_position_slider.setEnabled(False)
        self.ui.midi_file_position_slider.setValue(0)
        self.ui.midi_file_position_slider.setEnabled(True)
        self.ui.midi_file_position_slider.setRange(
            0, int(self.midi_state.file_duration_seconds)
        )
        self.ui_position_label_set_time()
        # Update digital to show tempo only (no bar when resetting)
        if self.current_tempo_bpm is not None:
            self.ui.digital_title_file_name.set_upper_display_text(
                f"Tempo: {round(self.current_tempo_bpm)} BPM"
            )

    def ui_position_label_update_time(
            self, time_seconds: Optional[float] = None
    ) -> None:
        """
        ui_position_label_update_time

        :param time_seconds: float, optional
        :return: None
        """
        if time_seconds is None:
            self.ui.position_label.setText(
                f"Playback Position: 0:00 / {format_time(self.midi_state.file_duration_seconds)}"
            )

    def calculate_current_bar(
            self, elapsed_time: Optional[float] = None
    ) -> Optional[float]:
        """
        Calculate the current bar number based on elapsed playback time.

        :param elapsed_time: Optional elapsed time in seconds. If None, calculates from current playback state.
        :return: Current bar number (1-based) or None if calculation fails.
        """
        try:
            if (
                    not self.midi_state.file
                    or not hasattr(self, "ticks_per_beat")
                    or self.ticks_per_beat is None
            ):
                return None

            if elapsed_time is None:
                if self.midi_state.playback_start_time is None:
                    return None
                elapsed_time = time.time() - self.midi_state.playback_start_time

            # Cap elapsed time to file duration
            elapsed_time = min(elapsed_time, self.midi_state.file_duration_seconds)

            # Convert elapsed time to ticks
            current_tick = mido.second2tick(
                second=elapsed_time,
                ticks_per_beat=self.midi_state.file.ticks_per_beat,
                tempo=self.midi_state.tempo_at_position,
            )

            # Calculate bar number (assuming 4/4 time signature: 4 beats per bar)
            # Bar number is 1-based
            current_bar = (current_tick / (4 * self.ticks_per_beat)) + 1

            return max(1.0, current_bar)  # Ensure at least bar 1
        except Exception as ex:
            log.debug(f"Error calculating current bar: {ex}")
            return None

    def ui_position_label_set_time(self, elapsed_time: Optional[float] = None) -> None:
        """
        Update the position label with formatted elapsed time and total duration.
        Caps elapsed_time to total duration to prevent overflow digital.
        Also updates the bar number in the DigitalTitle upper digital.
        """
        total = self.midi_state.file_duration_seconds
        if elapsed_time is None:
            elapsed_str = "0:00"
        else:
            elapsed_capped = min(elapsed_time, total)
            elapsed_str = format_time(elapsed_capped)

        total_str = format_time(total)
        label_text = f"Playback Position: {elapsed_str} / {total_str}"
        if getattr(self, "_last_position_label", "") != label_text:
            self.ui.position_label.setText(label_text)
            self._last_position_label = label_text

        # Update upper digital with tempo and bar number during active playback or when paused
        if elapsed_time is not None and self.midi_state.file and self.midi_state.timer:
            # Update digital with tempo and bar if timer was active (playing or paused)
            if self.midi_state.timer.isActive() or self.midi_state.playback_paused:
                self.update_upper_display_with_tempo_and_bar(elapsed_time)

    def midi_playback_pause_toggle(self):
        """
        midi_playback_pause_toggle

        :return: None
        Toggle pause and resume playback.
        """
        if not self.midi_state.file or not self.midi_state.timer:
            return

        if not self.midi_state.playback_paused:
            # Pausing playback
            self.midi_state.playback_paused_time = time.time()
            self.midi_state.timer.stop()
            self.midi_state.playback_paused = True
            self.ui.pause_label.setText("Resume")
        else:
            # Resuming playback
            if (
                    self.midi_state.playback_paused_time
                    and self.midi_state.playback_start_time
            ):
                pause_duration = time.time() - self.midi_state.playback_paused_time
                self.midi_state.playback_start_time += (
                    pause_duration  # Adjust start time
                )
            self.midi_state.timer.start()
            self.midi_state.playback_paused = False
            self.ui.pause_label.setText("Pause")

    def midi_playback_worker_handle_result(self, result=None):
        """
        Handle the result from the worker.
        This can be used to update the UI or perform further actions.
        :param result: The result from the worker
        """
        pass

    def _print_segment_statistics(self):
        """Print segment statistics for the buffered MIDI file."""
        if not self.midi_state.buffered_msgs:
            return

        # Extract tempo changes from buffered messages
        tempo_changes = []
        for tick, raw_bytes, tempo in self.midi_state.buffered_msgs:
            if raw_bytes is None:  # This is a tempo change message
                tempo_changes.append((tick, tempo))

        if not tempo_changes:
            log.message("🎵 No tempo changes found in MIDI file")
            return

        # Find the last MIDI event to calculate total duration
        last_event_tick = 0
        for tick, raw_bytes, tempo in self.midi_state.buffered_msgs:
            if raw_bytes is not None:  # This is a regular MIDI message
                last_event_tick = max(last_event_tick, tick)

        # Calculate segment statistics
        total_duration = 0
        current_tempo = 967745  # Start with default tempo
        current_tick = 0

        log.message("🎵 MIDI File Segment Statistics:")

        for i, (tick, tempo) in enumerate(tempo_changes):
            # Calculate duration of this segment
            segment_duration = mido.tick2second(
                tick - current_tick, self.ticks_per_beat, current_tempo
            )
            total_duration += segment_duration

            bar_start = current_tick / (4 * self.ticks_per_beat)
            bar_end = tick / (4 * self.ticks_per_beat)
            bpm = 60000000 / current_tempo

            log.message(
                f"  Segment {i + 1}: Bars {bar_start:.1f}-{bar_end:.1f} "
                f"at {bpm:.1f} BPM = {segment_duration:.2f}s"
            )

            current_tick = tick
            current_tempo = tempo

        # Add duration of final segment (from last tempo change to end)
        if last_event_tick > current_tick:
            final_segment_duration = mido.tick2second(
                last_event_tick - current_tick, self.ticks_per_beat, current_tempo
            )
            total_duration += final_segment_duration

            bar_start = current_tick / (4 * self.ticks_per_beat)
            bar_end = last_event_tick / (4 * self.ticks_per_beat)
            bpm = 60000000 / current_tempo

            log.message(
                f"  Final segment: Bars {bar_start:.1f}-{bar_end:.1f} "
                f"at {bpm:.1f} BPM = {final_segment_duration:.2f}s"
            )

        log.message(
            f"Total duration by segments: {total_duration:.2f}s ({total_duration / 60:.2f} minutes)"
        )

        # Also print tempo changes summary
        log.message(f"Found {len(tempo_changes)} tempo changes:")
        for i, (tick, tempo) in enumerate(tempo_changes):
            bpm = 60000000 / tempo
            time_sec = mido.tick2second(tick, self.ticks_per_beat, tempo)
            bar = tick / (4 * self.ticks_per_beat)
            log.message(
                f"  {i + 1}: Tick {tick}, Bar {bar:.1f}, Tempo {tempo} ({bpm:.1f} BPM), Time {time_sec:.2f}s"
            )

    def _fix_buffer_tempo_assignments(self):
        """Fix tempo assignments in the buffer - each message should use the tempo that was active at its tick."""
        if not self.midi_state.buffered_msgs:
            return

        # Process messages in chronological order and assign correct tempo
        fixed_msgs = []
        current_tempo = 967745  # Start with initial tempo (62 BPM)

        for tick, raw_bytes, tempo in self.midi_state.buffered_msgs:
            if raw_bytes is None:
                # This is a tempo change - update current tempo
                current_tempo = tempo
                fixed_msgs.append((tick, raw_bytes, tempo))
            else:
                # This is a regular message - use the current tempo
                fixed_msgs.append((tick, raw_bytes, current_tempo))

        # Replace the buffer with the fixed messages
        self.midi_state.buffered_msgs = fixed_msgs

    def _get_pattern_sequencer_editor(self):
        """Return the Pattern Sequencer editor instance if available, else None."""
        if not self.parent:
            return None
        if hasattr(self.parent, "get_existing_editor"):
            try:
                from jdxi_editor.ui.editors.pattern.pattern import (
                    PatternSequenceEditor,
                )

                return self.parent.get_existing_editor(PatternSequenceEditor)
            except Exception:
                return None
        if hasattr(self.parent, "patternsequenceeditor_instance"):
            return self.parent.patternsequenceeditor_instance
        return None

    def _push_tempo_to_pattern_sequencer(self, tempo_bpm: float) -> None:
        """Push current display tempo to Pattern Sequencer so it stays in sync with playback pipeline."""
        try:
            pattern_editor = self._get_pattern_sequencer_editor()
            if not pattern_editor:
                return
            bpm_int = int(round(tempo_bpm))
            if (
                    hasattr(pattern_editor, "tempo_spinbox")
                    and pattern_editor.tempo_spinbox
            ):
                pattern_editor.tempo_spinbox.blockSignals(True)
                pattern_editor.tempo_spinbox.setValue(bpm_int)
                pattern_editor.tempo_spinbox.blockSignals(False)
            if hasattr(pattern_editor, "set_tempo"):
                pattern_editor.set_tempo(bpm_int)
        except Exception as ex:
            log.debug(f"Could not push tempo to Pattern Sequencer: {ex}")

    def _notify_pattern_sequencer_file_loaded(self) -> None:
        """Notify Pattern Sequencer that a MIDI file has been loaded."""
        try:
            pattern_editor = self._get_pattern_sequencer_editor()
            log.debug(
                f"Found Pattern Sequencer for file load: {pattern_editor is not None}"
            )
            if pattern_editor:
                if hasattr(pattern_editor, "_load_from_midi_file_editor"):
                    log.message("Notifying Pattern Sequencer of MIDI file load")
                    # Pass self (MidiFileEditor) directly to ensure the reference is available
                    pattern_editor._load_from_midi_file_editor(midi_file_editor=self)
                elif hasattr(pattern_editor, "set_midi_file_editor"):
                    # If Pattern Sequencer doesn't have the reference, set it first
                    log.message("Setting MidiFileEditor reference in Pattern Sequencer")
                    pattern_editor.set_midi_file_editor(self)
                    if hasattr(pattern_editor, "_load_from_midi_file_editor"):
                        pattern_editor._load_from_midi_file_editor(
                            midi_file_editor=self
                        )
                else:
                    log.debug("Pattern Sequencer found but missing required methods")
            else:
                log.debug("Pattern Sequencer not found - it may not be initialized yet")
        except Exception as ex:
            log.error(f"Error notifying Pattern Sequencer: {ex}")
            import traceback

            log.debug(traceback.format_exc())

    def _build_specs(self) -> dict[str, Any]:
        return {
            "buttons": {
                "apply_all_track_changes": ButtonSpec(
                    label="Apply All Track Changes",
                    tooltip="Apply all Track Name and MIDI Channel changes",
                    icon=JDXi.UI.Icon.SAVE,
                    slot=self._apply_all_track_changes,
                ),
                "automation_insert": ButtonSpec(
                    label="Insert Program Change Here",
                    tooltip="Insert Program Change at current position",
                    icon=JDXi.UI.Icon.ADD,
                    slot=self.insert_program_change_current_position,
                ),
                "classify_tracks": ButtonSpec(
                    label="Classify Tracks",
                    tooltip="Classify non-drum tracks into Bass (Ch 1), Keys/Guitars (Ch 2), and Strings (Ch 3)",
                    icon=JDXi.UI.Icon.MUSIC_NOTES,
                    slot=self.classify_and_assign_tracks,
                ),
                "detect_drums": ButtonSpec(
                    label="Detect Drums",
                    tooltip="Analyze MIDI file and assign Channel 10 to detected drum tracks",
                    icon=JDXi.UI.Icon.DRUM,
                    slot=self.detect_and_assign_drum_tracks,
                ),
                "load_midi_file": ButtonSpec(
                    label="Load MIDI File",
                    tooltip="Load MIDI File",
                    icon=JDXi.UI.Icon.FOLDER_OPENED,
                    slot=self.midi_load_file,
                ),
                "save_midi_file": ButtonSpec(
                    label="Save MIDI File",
                    tooltip="Save MIDI file",
                    icon=JDXi.UI.Icon.FLOPPY_DISK,
                    slot=self.midi_save_file,
                ),
                "usb_port_refresh": ButtonSpec(
                    label="Refresh USB Device List",
                    tooltip="Refresh USB devices",
                    icon=JDXi.UI.Icon.REFRESH,
                    slot=self.usb_populate_devices,
                ),
            },
            "message_box": self._build_message_box_specs()
        }

    def _build_message_box_specs(self) -> dict[str, MessageBoxSpec]:
        """Assemble all static message box specs for the MIDI player."""
        return {
            "no_midi_file": MessageBoxSpec(
                title="No MIDI File Loaded",
                message="Please load a MIDI file first before detecting drum tracks.",
                type_attr="Warning",
            ),
            "no_midi_file_classify": MessageBoxSpec(
                title="No MIDI File Loaded",
                message="Please load a MIDI file first before classifying tracks.",
                type_attr="Warning",
            ),
            "no_drum_tracks_found": MessageBoxSpec(
                title="No Drum Tracks Found",
                message=(
                    "No tracks were identified as drum tracks with high confidence (score >= 70).\n\n"
                    "Try lowering the threshold or manually assign channels."
                ),
                type_attr="Information",
            ),
            "no_tracks_classified": MessageBoxSpec(
                title="No Tracks Classified",
                message=(
                    "No tracks were classified with sufficient confidence (score >= 30).\n\n"
                    "Tracks may need manual assignment."
                ),
                type_attr="Information",
            ),
            "no_output_file": MessageBoxSpec(
                title="No Output File",
                message="Please select a WAV output file or enable auto-generate filename.",
                type_attr="Warning",
            ),
            # Dynamic message (pass message= at call site):
            "drum_tracks_detected": MessageBoxSpec(
                title="Drum Tracks Detected",
                message="",
                type_attr="Information",
            ),
            "error_detect_drums": MessageBoxSpec(
                title="Error",
                message="",
                type_attr="Critical",
            ),
            "error_classify_tracks": MessageBoxSpec(
                title="Error",
                message="",
                type_attr="Critical",
            ),
            "tracks_classified": MessageBoxSpec(
                title="Tracks Classified",
                message="",
                type_attr="Information",
            ),
            "error_saving_file": MessageBoxSpec(
                title="Error Saving File",
                message="",
                type_attr="Critical",
            ),
            # Generic templates (pass title= and message= at call site):
            "info": MessageBoxSpec(
                title="",
                message="",
                type_attr="Information",
            ),
            "warning": MessageBoxSpec(
                title="",
                message="",
                type_attr="Warning",
            ),
        }
