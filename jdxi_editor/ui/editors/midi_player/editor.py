"""
MIDI Player for JDXI Editor
"""

import time
from pathlib import Path
from typing import Any, Callable, Optional

import mido
from decologr import Decologr as log
from mido import Message, MidiFile, bpm2tempo
from PySide6.QtCore import QMargins, Qt, QTimer
from PySide6.QtGui import QCloseEvent, QDragEnterEvent, QDropEvent, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
)

from jdxi_editor.midi.channel.channel import MidiChannel
from jdxi_editor.midi.file.trim import trim_midi_file, trim_track
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
from jdxi_editor.midi.playback.transport import TransportController
from jdxi_editor.midi.sysex.composer import JDXiSysExComposer
from jdxi_editor.ui.editors.helpers.widgets import create_panel
from jdxi_editor.ui.style.editor_style import mark_editor_body
from jdxi_editor.ui.common import JDXi, QVBoxLayout, QWidget
from jdxi_editor.midi.bank import Bank
from jdxi_editor.ui.dialogs.trim import TrimDialog
from jdxi_editor.ui.dialogs.program_change import (
    ProgramChangeDialog,
    ProgramChangeSelection,
)
from jdxi_editor.ui.editors.helpers.widgets import (
    create_jdxi_button_from_spec,
    create_jdxi_row,
)
from jdxi_editor.ui.editors.midi_player.automation import AutomationWidget
from jdxi_editor.ui.editors.midi_player.helper import build_panel
from jdxi_editor.ui.editors.midi_player.midi_analyzer import MidiAnalyzer
from jdxi_editor.ui.editors.midi_player.track.category import (
    CATEGORY_META,
    STR_TO_TRACK_CATEGORY,
    TrackCategory,
)
from jdxi_editor.ui.editors.midi_player.utils import format_time, tempo2bpm
from jdxi_editor.ui.editors.midi_player.widgets import MidiPlayerWidgets
from jdxi_editor.ui.editors.synth.editor import SynthEditor
from jdxi_editor.ui.preset.helper import JDXiPresetHelper
from jdxi_editor.ui.preset.source import PresetSource
from jdxi_editor.ui.preset.tone.digital.list import JDXiPresetToneListDigital
from jdxi_editor.ui.widgets.digital.title import DigitalTitle
from jdxi_editor.ui.widgets.editor.base import EditorBaseWidget
from jdxi_editor.ui.widgets.editor.helper import (
    create_group_with_layout,
    create_layout_with_items,
    create_vertical_layout,
)
from jdxi_editor.ui.widgets.midi.file.viewer import MidiFileViewer
from jdxi_editor.ui.widgets.midi.utils import get_total_duration_in_seconds
from jdxi_editor.ui.widgets.classification_group import ClassificationGroup
from jdxi_editor.ui.widgets.event_suppression_group import EventSuppressionGroup
from jdxi_editor.ui.widgets.midi_file_group import MidiFileGroup
from jdxi_editor.ui.widgets.mute_channels_group import MuteChannelsGroup
from jdxi_editor.ui.preset.utils import convert_preset_dict_to_list
from jdxi_editor.ui.widgets.midi.time_ruler import RulerMarker
from jdxi_editor.ui.widgets.transport.playback_options import PlaybackOptionsWidget
from jdxi_editor.ui.widgets.transport.transport import TransportWidget
from jdxi_editor.ui.widgets.usb.recording import USBFileRecordingWidget
from jdxi_editor.ui.windows.jdxi.utils import show_message_box_from_spec
from picomidi.constant import Midi
from picomidi.message.type import MidoMessageType
from picomidi.playback.engine import PlaybackEngine, TransportState
from picomidi.ui.widget.transport.spec import TransportSpec
from picoui.helpers import create_layout_with_inner_layouts, create_widget_with_layout
from picoui.specs.widgets import (
    ButtonSpec,
    CheckBoxSpec,
    FileSelectionMode,
    FileSelectionSpec,
    MessageBoxSpec,
    get_file_save_from_spec,
)

# Expose Qt symbols for tests that patch via jdxi_editor.ui.editors.io.player
# Tests expect these names to exist at module level
QApplication = None  # alias placeholder for patching
QObject = None
Signal = None
Slot = None


class MidiFileAttrs:
    """Midi File Attributes"""

    TICKS_PER_BEAT = "ticks_per_beat"


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
        self.midi_helper = midi_helper
        self.tick_duration = None
        self.specs: dict | None = None
        self._last_position_label: QLabel | None = None
        self.parent: QWidget = parent
        self.preset_helper: JDXiPresetHelper = preset_helper
        # Midi-related
        self.midi_state: MidiPlaybackState = MidiPlaybackState()
        self._midi_file_path: Optional[str] = None
        self.on_midi_file_saved: Optional[Callable[[str], None]] = None
        self.midi_analyzer: MidiAnalyzer = MidiAnalyzer()
        self.midi_total_ticks: int | None = None
        self.midi_port = self.midi_helper.midi_out
        self.transport_controller = TransportController(
            send=lambda msg: self.midi_helper.midi_out.send_message(msg.bytes()),
            parent=self,
        )
        self.playback_engine: PlaybackEngine = self.transport_controller.engine
        self.transport_controller.state_changed.connect(self._on_transport_state_changed)
        self.transport_controller.position_changed.connect(
            self._on_transport_position_changed
        )
        self.transport_controller.tempo_changed.connect(self._on_transport_tempo_changed)
        self.current_tempo_bpm = None  # Store current tempo BPM for digital
        self._upper_display_text: str | None = None
        self.midi_preferred_channels = {
            MidiChannel.DIGITAL_SYNTH_1,
            MidiChannel.DIGITAL_SYNTH_2,
            MidiChannel.ANALOG_SYNTH,
            MidiChannel.DRUM_KIT,
        }  # MIDI channels 1, 2, 3, 10 (zero-based)
        # Initialize UI attributes
        self.usb_recorder = USBFileRecordingWidget(self.midi_state)
        self.automation = AutomationWidget(self.midi_state, parent=self)
        self.ui = MidiPlayerWidgets()
        self.transport: TransportWidget = TransportWidget(parent=self)
        self.playback_options = PlaybackOptionsWidget(parent=self)
        self._loop_points: tuple[Optional[float], Optional[float]] = (None, None)
        self._loading_file = False
        self._preset_names: dict[tuple[int, int, int], str] | None = None
        self.midi_file_group: MidiFileGroup = MidiFileGroup(
            parent=self, midi_state=self.midi_state
        )
        self.event_suppression_group: EventSuppressionGroup = EventSuppressionGroup(
            parent=self, midi_state=self.midi_state
        )
        self.classification_group: ClassificationGroup = ClassificationGroup(
            parent=self, midi_state=self.midi_state
        )
        self.mute_channels_group: MuteChannelsGroup = MuteChannelsGroup(
            parent=self, midi_state=self.midi_state
        )
        self.midi_file = MidiFileViewer(midi_state=self.midi_state, parent=self)
        track_viewer = self.midi_file.midi_track_viewer
        track_viewer.mute_changed.connect(self._sync_transport_settings)
        track_viewer.track_velocity_changed.connect(self._sync_transport_settings)
        track_viewer.file_changed.connect(self._on_track_viewer_file_changed)
        track_viewer.trim_track_requested.connect(self.midi_trim_track)
        track_viewer.ruler.seek_requested.connect(self.transport_controller.seek_seconds)
        track_viewer.ruler.marker_moved.connect(self._move_program_change)
        track_viewer.ruler.marker_delete_requested.connect(self._delete_program_change)
        track_viewer.ruler.marker_edit_requested.connect(self._edit_program_change)
        self.transport_controller.loop_changed.connect(self._on_transport_loop_changed)
        self.specs = self._build_specs()
        self.ui_init()
        self.transport.set_state(self.transport_controller.state)
        self._init_shortcuts()
        self.setAcceptDrops(True)

    def ui_init(self):
        """
        Initialize the UI for the MidiPlayer.
        """
        panel_widgets = [
            build_panel(self._build_left_panel),
            build_panel(self._build_right_panel),
        ]
        # --- Top horizontal layout: file title and right-hand controls
        header_layout = create_layout_with_items(
            items=panel_widgets,
            start_stretch=False,
            end_stretch=False,
            margins=JDXi.UI.MidiPlayer.MARGINS,
            spacing=JDXi.UI.MidiPlayer.SPACING_GROUP,
        )
        header_widget = create_widget_with_layout(header_layout)
        # --- Use EditorBaseWidget for consistent scrollable layout structure
        self.base_widget = EditorBaseWidget(parent=self, analog=False)
        self.base_widget.setup_scrollable_content(center_horizontally=False)
        # --- Create content widget
        centered_layout = create_layout_with_items(
            items=[
                self.transport,
                self.midi_file_group,
                self.event_suppression_group,
            ],
            vertical=False,
            start_stretch=False,
            end_stretch=False,
            margins=JDXi.UI.MidiPlayer.MARGINS,
            spacing=JDXi.UI.MidiPlayer.SPACING_GROUP,
        )
        centered_widget = create_widget_with_layout(centered_layout)

        # Vertical stack: header, ruler, track viewer (stretch), controls.
        # So MidiTrackViewer and its MidiTrackWidgets get space and are visible.
        main_layout = create_layout_with_items(
            margins=JDXi.UI.MidiPlayer.MARGINS,
            spacing=JDXi.UI.MidiPlayer.SPACING_RELATED,
            items=[],
            vertical=True
        )
        # Three panels, as the JD-Xi has a few large glossy ones: controls on
        # top, the timeline, transport and playback below. The groups inside a
        # panel draw as flat sections (see AppEditorStyle).

        main_layout_items = [
                (create_panel(header_widget), 0),
                (self.midi_file, 0), 
                (self.midi_file.midi_track_viewer, 1), 
                (create_panel(centered_widget, self.playback_options), 0)
            ]
        for item, spacing in main_layout_items:
            main_layout.addWidget(item, spacing)
        # Add content to base widget
        container_layout = self.base_widget.get_container_layout()
        content_widget = create_widget_with_layout(main_layout)
        content_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.midi_file.midi_track_viewer.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        container_layout.addWidget(content_widget, 1)
        self._add_base_widget_to_editor()
        self._apply_midi_player_style()

    def _apply_midi_player_style(self) -> None:
        """Override global editor QSS with player-scoped tokens (less idle red)."""
        mark_editor_body(self)
        self.setStyleSheet(JDXi.UI.MidiPlayer.editor_stylesheet())

    def _add_base_widget_to_editor(self):
        """Add base widget to editor's layout"""
        if not hasattr(self, "main_layout") or self.main_layout is None:
            self.main_layout = QVBoxLayout(self)
            self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.base_widget)

    def _build_left_panel(self) -> QVBoxLayout:
        """Build left panel"""
        # --- Create vertical layout for title and drum detection button
        self.ui.digital_title_file_name = DigitalTitle(
            tone_name="No file loaded", show_upper_text=True
        )
        layout = create_layout_with_items(
            items=[
                self.ui.digital_title_file_name,
                self.classification_group,
                self.mute_channels_group,
            ],
            vertical=True,
            start_stretch=False,
            end_stretch=False,
            margins=JDXi.UI.MidiPlayer.MARGINS,
            spacing=JDXi.UI.MidiPlayer.SPACING_RELATED,
        )
        return layout

    def _build_right_panel(self):
        """Build right panel"""
        right_panel_layout = create_layout_with_inner_layouts(
            inner_layouts=[self.init_automation_usb_grid()],
            vertical=True,
            stretch=False,
        )
        right_panel_layout.setContentsMargins(JDXi.UI.MidiPlayer.MARGINS)
        right_panel_layout.setSpacing(JDXi.UI.MidiPlayer.SPACING_GROUP)
        return right_panel_layout

    def detect_and_assign_drum_tracks(self) -> None:
        """
        Detect drum tracks in the loaded MIDI file and assign Channel 10 (1-based) to them.

        This analyzes all tracks using heuristics and automatically sets the channel
        spinboxes for tracks identified as drum tracks.
        """
        if not self._validate_midi_loaded():
            return

        try:
            drum_tracks = self.midi_analyzer.get_drum_tracks(
                self.midi_state.file, min_score=70.0
            )

            if not drum_tracks:
                show_message_box_from_spec(
                    self.specs["message_box"]["no_drum_tracks_found"]
                )
                return

            # --- Update the channel spinboxes for detected drum tracks
            # --- Channel 10 (1-based) = Channel 9 (0-based)
            drum_channel_display = 10  # 1-based digital channel
            drum_channel_binary = 9  # 0-based binary channel

            updated_tracks = []
            for track_index, analysis in drum_tracks:
                if track_index in self.midi_file.midi_track_viewer.track_channel_spins:
                    spin = self.midi_file.midi_track_viewer.track_channel_spins[
                        track_index
                    ]
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
                title="No MIDI File Loaded",
                message="Please load a MIDI file first before classifying tracks.",
            )
            return False
        return True

    def _detect_drum_tracks(self) -> list[int]:
        """Return track indices identified as drum tracks."""
        drum_tracks = self.midi_analyzer.get_drum_tracks(
            self.midi_state.file, min_score=70.0
        )
        return [idx for idx, _ in drum_tracks]

    def _classify_tracks(self, drum_indices: list[int]):
        """Classify non-drum tracks into Bass, Keys/Guitars, Strings."""
        return self.midi_analyzer.get_classifications(
            self.midi_state.file, exclude_drum_indices=drum_indices, min_score=30.0
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
                spin = self.midi_file.midi_track_viewer.track_channel_spins.get(
                    track_index
                )
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

    def _build_classification_message(self, updated: dict[str, list[str]]) -> str:
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

        parts.append("\n\nThe channels have been changed in the track list.")

        return "\n".join(parts)

    def _show_info_message(self, title: str, message: str) -> None:
        """show info dialog"""
        show_message_box_from_spec(
            self.specs["message_box"]["info"], title=title, message=message
        )

    def _show_warning(self, title: str, message: str) -> None:
        """show warning"""
        show_message_box_from_spec(
            self.specs["message_box"]["warning"], title=title, message=message
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
        grid.setContentsMargins(JDXi.UI.MidiPlayer.MARGINS)
        row = 0
        grid.addWidget(self.automation, row, 0, 1, 5)
        row += 1

        grid.addWidget(self.usb_recorder, row, 0, 1, 5)

        self.automation.populate_automation_programs(PresetSource.DIGITAL)
        return grid

    def insert_program_change_current_position(self) -> None:
        """
        Insert Bank Select (CC#0, CC#32) and Program Change at the current slider time.
        """
        if not self.midi_state.file:
            return

        # Insert at the playback position (optionally on the nearest bar line)
        current_seconds = self._snap_to_bar(self.transport_controller.position_seconds)
        # Channel (digital is 1-16, convert to 0-based)
        display_channel = int(self.automation.automation_channel_combo.currentData())
        channel = display_channel - 1

        # Selected program triple (msb, lsb, pc)
        data = self.automation.automation_program_combo.currentData()
        if not data:
            return
        msb, lsb, pc = data
        from jdxi_editor.midi.bank import Bank
        from jdxi_editor.ui.editors.helpers.preset import preset_to_jdxi_bank_pc
        from jdxi_editor.ui.midi.selection_info import MidiWireInfo

        bank_msb, bank_lsb, midi_pc = preset_to_jdxi_bank_pc(
            int(msb), int(lsb), int(pc)
        )

        if self.midi_helper and hasattr(self.midi_helper, "set_selection_expectation"):
            expected = MidiWireInfo(
                channel=channel,
                bank=Bank(msb=bank_msb, lsb=bank_lsb),
                program=midi_pc,
            )
            self.midi_helper.set_selection_expectation(
                expected, "midi_automation", data
            )

        # Convert seconds to absolute ticks using the file's tempo map
        abs_ticks = self.playback_engine.seconds_to_tick(current_seconds)

        # Find a target track that uses this channel, else use track 0
        track_index = self._find_track_for_channel(channel)
        target_track = self.midi_state.file.tracks[track_index]

        msgs = self._bank_program_messages(channel, bank_msb, bank_lsb, midi_pc)
        self._insert_messages_at_abs_tick(target_track, abs_ticks, msgs)

        # Refresh viewer; its file_changed updates playback and the PC markers
        self.midi_file.midi_track_viewer.set_midi_file(self.midi_state.file, keep_track_state=True)

    def _snap_to_bar(self, seconds: float) -> float:
        """Nearest bar line to *seconds* when Snap to bar is on."""
        if self.playback_options.snap_to_bar and self.transport_controller.is_loaded:
            return self.transport_controller.nearest_bar_seconds(seconds)
        return seconds

    def _on_track_viewer_file_changed(self, midi_file: MidiFile) -> None:
        """
        Keep playback and saving on the file the track viewer shows.

        Track edits (channels, names, presets, reorder, clone, delete, program
        changes) produce or modify the viewer's file; adopt it so it is heard
        and saved, keeping the playback position.
        """
        if self._loading_file:
            return
        previous = self.midi_state.file
        if midi_file is not previous and previous is not None:
            # Edited copies lose the path used for auto-generated WAV names
            if getattr(midi_file, "filename", None) is None:
                midi_file.filename = getattr(previous, "filename", None)
        self.midi_state.file = midi_file
        self.ticks_per_beat = midi_file.ticks_per_beat
        self.midi_extract_events()
        self.calculate_duration()
        self.transport_controller.load(midi_file, keep_position=True)
        self._sync_mute_buttons_from_track_viewer()
        self._sync_transport_settings()
        self.midi_file.position_slider.setRange(
            0, int(self.midi_state.file_duration_seconds)
        )
        self._refresh_program_change_markers()

    # --- Program change markers -------------------------------------------

    def _preset_name(self, msb: int, lsb: int, program: int) -> Optional[str]:
        """JD-Xi preset name for a bank select + program change, if known."""
        if self._preset_names is None:
            from jdxi_editor.ui.editors.helpers.preset import preset_to_jdxi_bank_pc

            self._preset_names = {}
            for source in (
                JDXi.UI.Preset.Digital.PROGRAM_CHANGE,
                JDXi.UI.Preset.Analog.PROGRAM_CHANGE,
                JDXi.UI.Preset.Drum.PROGRAM_CHANGE,
            ):
                for item in convert_preset_dict_to_list(source):
                    try:
                        wire = preset_to_jdxi_bank_pc(
                            int(item["msb"]), int(item["lsb"]), int(item["pc"])
                        )
                    except (KeyError, TypeError, ValueError):
                        continue
                    self._preset_names.setdefault(wire, item.get("name", ""))
        return self._preset_names.get((msb, lsb, program))

    def _refresh_program_change_markers(self) -> None:
        """Show every program change in the file as a draggable ruler marker."""
        ruler = self.midi_file.midi_track_viewer.ruler
        if not self.midi_state.file or not self.transport_controller.is_loaded:
            ruler.clear_markers()
            return
        markers = []
        for track_index, track in enumerate(self.midi_state.file.tracks):
            abs_tick = 0
            bank: dict[int, list[int]] = {}
            for msg in track:
                abs_tick += msg.time
                if msg.type == MidoMessageType.CONTROL_CHANGE.value and msg.control in (
                    0,
                    32,
                ):
                    bank.setdefault(msg.channel, [0, 0])[msg.control == 32] = msg.value
                elif msg.type == MidoMessageType.PROGRAM_CHANGE.value:
                    msb, lsb = bank.get(msg.channel, [0, 0])
                    name = self._preset_name(msb, lsb, msg.program)
                    label = f"Ch{msg.channel + 1} {name or f'PC {msg.program + 1}'}"
                    markers.append(
                        RulerMarker(
                            seconds=self.playback_engine.tick_to_seconds(abs_tick),
                            label=label,
                            key=(track_index, abs_tick, msg.channel),
                        )
                    )
        ruler.set_markers(markers)

    def _move_program_change(self, key: tuple[int, int, int], seconds: float) -> None:
        """Move a program change (and its bank select) to *seconds*."""
        track_index, abs_tick, channel = key
        if not self.midi_state.file or track_index >= len(self.midi_state.file.tracks):
            return
        track = self.midi_state.file.tracks[track_index]
        removed = self._remove_program_change(track, abs_tick, channel)
        if not removed:
            return
        new_tick = self.playback_engine.seconds_to_tick(self._snap_to_bar(seconds))
        self._insert_messages_at_abs_tick(track, new_tick, removed)
        self.midi_file.midi_track_viewer.set_midi_file(self.midi_state.file, keep_track_state=True)

    @staticmethod
    def _bank_program_messages(
        channel: int, bank_msb: int, bank_lsb: int, program: int
    ) -> list[mido.Message]:
        """CC#0, CC#32 and Program Change (JD-Xi wire values) at time 0."""
        return [
            mido.Message(
                type=MidoMessageType.CONTROL_CHANGE.value,
                control=0,
                value=bank_msb,
                channel=channel,
                time=0,
            ),
            mido.Message(
                type=MidoMessageType.CONTROL_CHANGE.value,
                control=32,
                value=bank_lsb,
                channel=channel,
                time=0,
            ),
            mido.Message(
                type=MidoMessageType.PROGRAM_CHANGE.value,
                program=program,
                channel=channel,
                time=0,
            ),
        ]

    @staticmethod
    def _program_change_at(
        track: mido.MidiTrack, abs_tick: int, channel: int
    ) -> Optional[tuple[int, int, int]]:
        """(bank MSB, bank LSB, program) of the program change at *abs_tick*, if any."""
        tick = 0
        bank = [0, 0]
        for msg in track:
            tick += msg.time
            if getattr(msg, "channel", None) != channel:
                continue
            if msg.type == MidoMessageType.CONTROL_CHANGE.value and msg.control in (
                0,
                32,
            ):
                bank[msg.control == 32] = msg.value
            elif msg.type == MidoMessageType.PROGRAM_CHANGE.value and tick == abs_tick:
                return bank[0], bank[1], msg.program
        return None

    def _ask_program_change(
        self, channel: int, bank_msb: int, bank_lsb: int, program: int
    ) -> Optional[ProgramChangeSelection]:
        """Show the Program Change dialog; the chosen values, or None if cancelled."""
        dialog = ProgramChangeDialog(
            channel=channel,
            bank=Bank(msb=bank_msb, lsb=bank_lsb),
            program=program,
            parent=self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return None
        return dialog.selection()

    def _edit_program_change(self, key: tuple[int, int, int]) -> None:
        """Double-clicked PC flag: choose a new preset/channel and write it back in place."""
        track_index, abs_tick, channel = key
        if not self.midi_state.file or track_index >= len(self.midi_state.file.tracks):
            return
        track = self.midi_state.file.tracks[track_index]
        current = self._program_change_at(track, abs_tick, channel)
        if current is None:
            return
        selection = self._ask_program_change(channel, *current)
        if selection is None:
            return
        if not self._remove_program_change(track, abs_tick, channel):
            return
        self._insert_messages_at_abs_tick(
            track,
            abs_tick,
            self._bank_program_messages(
                selection.channel,
                selection.bank.msb,
                selection.bank.lsb,
                selection.program,
            ),
        )
        self.midi_file.midi_track_viewer.set_midi_file(self.midi_state.file, keep_track_state=True)

    def _delete_program_change(self, key: tuple[int, int, int]) -> None:
        """Delete a program change (and its bank select)."""
        track_index, abs_tick, channel = key
        if not self.midi_state.file or track_index >= len(self.midi_state.file.tracks):
            return
        track = self.midi_state.file.tracks[track_index]
        if self._remove_program_change(track, abs_tick, channel):
            self.midi_file.midi_track_viewer.set_midi_file(self.midi_state.file, keep_track_state=True)

    @staticmethod
    def _remove_program_change(
        track: mido.MidiTrack, abs_tick: int, channel: int
    ) -> list[mido.Message]:
        """
        Remove the program change at *abs_tick* on *channel*, plus the bank
        select (CC#0/CC#32) directly before it, keeping other timing intact.

        :return: The removed messages (time=0), in order; empty if not found
        """
        timed = []
        tick = 0
        for msg in track:
            tick += msg.time
            timed.append((tick, msg))
        pc_index = next(
            (
                i
                for i, (t, m) in enumerate(timed)
                if t == abs_tick
                and m.type == MidoMessageType.PROGRAM_CHANGE.value
                and m.channel == channel
            ),
            None,
        )
        if pc_index is None:
            return []
        remove = {pc_index}
        i = pc_index - 1
        while i >= 0:
            t, m = timed[i]
            if not (
                t == abs_tick
                and m.type == MidoMessageType.CONTROL_CHANGE.value
                and m.control in (0, 32)
                and m.channel == channel
            ):
                break
            remove.add(i)
            i -= 1
        removed = [timed[i][1].copy(time=0) for i in sorted(remove)]
        track.clear()
        previous = 0
        for i, (t, m) in enumerate(timed):
            if i in remove:
                continue
            track.append(m.copy(time=t - previous))
            previous = t
        return removed

    def _build_message(
        self, message_type: str, channel: int, value: int = None, program: int = None
    ) -> Message:
        """Build message"""
        if program is None:
            message = mido.Message(
                type=message_type, control=0, value=int(value), channel=channel, time=0
            )
        else:
            message = mido.Message(
                type=message_type, program=program, channel=channel, time=0
            )
        return message

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
                        mido.Message(
                            MidoMessageType.NOTE_ON.value,
                            note=0,
                            velocity=0,
                            time=insert_delta,
                        )
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

    def _toggle_channel_mute(self, channel: int, is_muted: bool, btn) -> None:
        """
        Toggle mute state for a specific MIDI channel.
        Updates both the track viewer and the player's muted channels state.

        :param channel: int MIDI channel (1-16)
        :param is_muted: bool is the channel muted?
        """
        # Update track viewer's mute state (this will also update track viewer's buttons)
        if self.midi_file and self.midi_file.midi_track_viewer:
            self.midi_file.midi_track_viewer.toggle_channel_mute(channel, is_muted)
            # Sync the track viewer's mute buttons
            if channel in self.midi_file.midi_track_viewer.mute_buttons:
                self.midi_file.midi_track_viewer.mute_buttons[channel].setChecked(
                    is_muted
                )
                self.midi_file.midi_track_viewer.mute_buttons[channel].setStyleSheet(
                    JDXi.UI.MidiPlayer.sequencer_button_style(
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
        if not hasattr(self, "mute_channels_group") or not self.mute_channels_group:
            return

        mute_channel_buttons = self.mute_channels_group.mute_channel_buttons
        if self.midi_file and self.midi_file.midi_track_viewer:
            muted_channels = self.midi_file.midi_track_viewer.get_muted_channels()
            for channel, btn in mute_channel_buttons.items():
                btn.blockSignals(True)
                btn.setChecked(channel in muted_channels)
                btn.blockSignals(False)
        midi_file = self.midi_state.file
        if midi_file is not None:
            self.mute_channels_group.set_used_channels(
                {
                    msg.channel + Midi.channel.BINARY_TO_DISPLAY
                    for track in midi_file.tracks
                    for msg in track
                    if hasattr(msg, "channel") and not msg.is_meta
                }
            )

    def apply_channel_presets(self) -> None:
        """
        Send live MIDI Program Changes to the synth and insert presets into the MIDI file.
        Ch 1→Picked Bass, Ch 2→Piano, Ch 3→JP8 Strings.
        """
        log.message(
            scope=self.__class__.__name__,
            message="apply_channel_presets called (Apply Presets button)",
        )

        if self.midi_file and self.midi_file.midi_track_viewer:
            self.midi_file.midi_track_viewer.flush_pending_edits()
        if not self.midi_file or not self.midi_file.midi_track_viewer:
            log.message(
                scope=self.__class__.__name__,
                message="Early return: no midi_file or midi_track_viewer",
            )
            return

        tv = self.midi_file.midi_track_viewer
        channel_preset_map = tv._CHANNEL_PRESET_MAP
        pc_map = JDXiPresetToneListDigital.PROGRAM_CHANGE

        log.parameter(
            scope=self.__class__.__name__,
            message="midi_helper",
            parameter=self.midi_helper,
        )
        log.parameter(
            scope=self.__class__.__name__,
            message="track_channel_spins count",
            parameter=len(tv.track_channel_spins) if tv.track_channel_spins else 0,
        )
        if tv.track_channel_spins:
            ch_values = {
                i: tv.track_channel_spins[i].value()
                for i in sorted(tv.track_channel_spins)
            }
            log.parameter(
                scope=self.__class__.__name__,
                message="track_channel_spins (track_idx -> display_ch)",
                parameter=ch_values,
            )

        # Send live MIDI to synth for each channel with a preset mapping
        if self.midi_helper:
            seen_channels: set[int] = set()
            sent_count = 0
            for i in tv.track_channel_spins:
                display_ch = tv.track_channel_spins[i].value()
                if display_ch in seen_channels:
                    continue
                preset_num = channel_preset_map.get(display_ch)
                if preset_num is None or preset_num not in pc_map:
                    log.parameter(
                        scope=self.__class__.__name__,
                        message=f"Skip Ch {display_ch}: preset_num={preset_num}",
                        parameter=preset_num,
                    )
                    continue
                seen_channels.add(display_ch)
                spec = pc_map[preset_num]
                channel = display_ch + Midi.channel.DISPLAY_TO_BINARY  # 0-based
                log.message(
                    scope=self.__class__.__name__,
                    message=f"Sending live MIDI: Ch {display_ch} -> preset {preset_num} ({spec.get('Name', '?')})",
                )
                self.midi_helper.send_bank_select_and_program_change(
                    channel=channel,
                    bank_msb=spec["MSB"],
                    bank_lsb=spec["LSB"],
                    program=max(0, spec["PC"] - 1),
                )
                sent_count += 1
            log.parameter(
                scope=self.__class__.__name__,
                message="Live MIDI presets sent",
                parameter=sent_count,
            )
        else:
            log.message(
                scope=self.__class__.__name__,
                message="No midi_helper: skipping live MIDI send",
            )

        log.message(
            scope=self.__class__.__name__,
            message="Calling track_viewer.apply_channel_presets (file update)",
        )
        tv.apply_channel_presets()

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
            spec.icon, color=JDXi.UI.Style.FOREGROUND, size=20
        )
        label_row, text_label = create_jdxi_row(spec.text, icon_pixmap=pixmap)
        setattr(self.ui, f"{spec.name}_label", text_label)
        layout.addWidget(label_row)

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
        self._sync_transport_settings()

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
        self._sync_transport_settings()

    def _midi_file_dialog_path(self) -> str:
        """Last loaded/saved MIDI path for file dialog defaults."""
        if self._midi_file_path:
            return self._midi_file_path
        if self.midi_state.file and getattr(self.midi_state.file, "filename", None):
            return self.midi_state.file.filename
        return ""

    def _remember_midi_file_path(self, file_path: str) -> None:
        """Store MIDI path for subsequent load/save dialogs."""
        self._midi_file_path = file_path
        if self.midi_state.file is not None:
            self.midi_state.file.filename = file_path

    def _reload_saved_midi_file(self, file_path: str) -> None:
        """Reload a saved MIDI file from disk so the UI matches persisted state."""
        self.transport_controller.stop()
        # Defer reload so the save file handle is fully released before re-reading.
        QTimer.singleShot(
            0,
            lambda path=file_path: self.midi_load_file_from_path(
                path,
                title_prefix="Saved",
                notify_pattern_sequencer=False,
                update_recent_files=False,
            ),
        )

    def _after_midi_file_saved(self, file_path: str) -> None:
        """Invoke post-save callback; default reloads the file into the UI."""
        if self.on_midi_file_saved is not None:
            self.on_midi_file_saved(file_path)
        else:
            self._reload_saved_midi_file(file_path)

    def _save_midi_to_path(self, file_path: str) -> bool:
        """Write the current MIDI file to *file_path* and update UI state."""
        try:
            self.midi_file.midi_track_viewer.midi_file.save(file_path)
            self._remember_midi_file_path(file_path)
            self._after_midi_file_saved(file_path)
            return True
        except Exception as ex:
            show_message_box_from_spec(
                self.specs["message_box"]["error_saving_file"],
                message=str(ex),
            )
            return False

    def midi_save_file(self) -> None:
        """
        Save the current MIDI file to its existing path, or prompt if none is set.
        """
        if not self.midi_state.file:
            show_message_box_from_spec(self.specs["message_box"]["no_midi_file"])
            return

        file_path = self._midi_file_dialog_path()
        if file_path:
            self._save_midi_to_path(file_path)
        else:
            self.midi_save_file_as()

    def midi_save_file_as(self) -> None:
        """Save the current MIDI file via a file dialog."""
        if not self.midi_state.file:
            show_message_box_from_spec(self.specs["message_box"]["no_midi_file"])
            return

        save_file_spec = FileSelectionSpec(
            mode=FileSelectionMode.SAVE,
            caption="Save MIDI File As",
            default_name=self._midi_file_dialog_path(),
            filter="MIDI Files (*.mid)",
        )
        file_path, _ = get_file_save_from_spec(save_file_spec, parent=self)
        if file_path:
            self._save_midi_to_path(file_path)

    def midi_load_file(self) -> None:
        """
        Load a MIDI file and initialize parameters
        """
        load_file_spec = FileSelectionSpec(
            mode=FileSelectionMode.LOAD,
            caption="Open MIDI File",
            default_name=self._midi_file_dialog_path(),
            filter="MIDI Files (*.mid)",
        )
        file_path, _ = get_file_save_from_spec(load_file_spec, parent=self)
        if not file_path:
            return

        self.midi_load_file_from_path(file_path)

    def midi_load_file_from_path(
        self,
        file_path: str,
        *,
        title_prefix: str = "Loaded",
        notify_pattern_sequencer: bool = True,
        update_recent_files: bool = True,
        remember_path: bool = True,
    ) -> bool:
        """
        Load a MIDI file from a given path and initialize parameters.

        :param file_path: Path to the MIDI file
        :param title_prefix: Prefix for the file title display (e.g. Loaded/Saved)
        :param notify_pattern_sequencer: Push load to Pattern Sequencer when True
        :param update_recent_files: Add path to recent-files menu when True
        :param remember_path: Use this path for later Save / file dialogs when True
            (False for temporary files, e.g. extracted from a bundle)
        :return: True if the file was loaded
        """
        if not file_path:
            return False

        path = Path(file_path)
        if not path.is_file():
            show_message_box_from_spec(
                self.specs["message_box"]["warning"],
                title="MIDI File Not Found",
                message=f"The file could not be found:\n{file_path}",
            )
            return False

        self.transport_controller.stop()

        try:
            self.midi_state.file = MidiFile(str(path))
        except Exception as ex:
            log.error(f"Error loading MIDI file {file_path}: {ex}")
            show_message_box_from_spec(
                self.specs["message_box"]["warning"],
                title="Error Loading MIDI File",
                message=f"Could not load MIDI file:\n{path.name}\n\n{ex}",
            )
            return False

        resolved_path = str(path.resolve())
        if remember_path:
            self._remember_midi_file_path(resolved_path)
            self.midi_state.file.filename = resolved_path
        else:
            # No usable path: Save prompts instead of overwriting a temp/old file
            self._midi_file_path = None
            self.midi_state.file.filename = None
        file_name = f"{title_prefix}: {path.name}"
        self.ui.digital_title_file_name.setText(file_name)
        self.midi_file.midi_track_viewer.clear()
        # The rest of this method sets up playback; skip the file_changed handler
        self._loading_file = True
        try:
            self.midi_file.midi_track_viewer.set_midi_file(self.midi_state.file)
        finally:
            self._loading_file = False
        # Sync mute buttons after loading MIDI file
        self._sync_mute_buttons_from_track_viewer()

        # Auto-generate WAV filename if checkbox is enabled
        if self.usb_recorder.file_auto_generate_checkbox.isChecked():
            self.usb_recorder.update_auto_wav_filename()

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
        self.transport_controller.load(self.midi_state.file)
        self._sync_transport_settings()
        self._loop_points = (None, None)
        self.playback_options.set_loop_points(None, None)
        self._refresh_program_change_markers()
        self.calculate_duration()
        self.calculate_tick_duration()
        self.ui_position_slider_reset()

        # Notify Pattern Sequencer if it exists
        if notify_pattern_sequencer:
            self._notify_pattern_sequencer_file_loaded()

        # Add to recent files if parent has recent_files_manager
        if update_recent_files and (
            hasattr(self.parent, "recent_files_manager")
            and self.parent.recent_files_manager
        ):
            try:
                self.parent.recent_files_manager.add_file(resolved_path)
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
        return True

    def calculate_tick_duration(self):
        """
        calculate_tick_duration

        :return:
        Calculate the duration of a single MIDI tick in seconds.
        """
        # Guard: ensure ticks_per_beat is set
        if (
            not hasattr(self, MidiFileAttrs.TICKS_PER_BEAT)
            or self.ticks_per_beat is None
        ):
            # Fallback to current file's ticks_per_beat if available
            if self.midi_state.file is not None:
                self.ticks_per_beat = getattr(
                    self.midi_state.file, MidiFileAttrs.TICKS_PER_BEAT, 480
                )
            else:
                self.ticks_per_beat = 480
        self.tick_duration = (
            self.midi_state.tempo_at_position
            / Midi.tempo.MILLISECONDS_PER_SECOND
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
        Select a suitable MIDI channel for playback from the file.
        """
        selected_channel = self.midi_analyzer.get_preferred_channel(
            self.midi_state.file, self.midi_preferred_channels
        )
        if selected_channel is None:
            selected_channel = MidiChannel.DIGITAL_SYNTH_1
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
        if (
            not hasattr(self, MidiFileAttrs.TICKS_PER_BEAT)
            or self.ticks_per_beat is None
        ):
            self.ticks_per_beat = getattr(
                self.midi_state.file, MidiFileAttrs.TICKS_PER_BEAT, 480
            )
        self.calculate_tick_duration()
        self.midi_state.events = sorted(events, key=lambda x: x[0])

    def detect_initial_tempo(self) -> dict[int, int]:
        """
        Detect initial tempo from the file and set midi_state.tempo_initial.

        :return: dict[track_number, tempo_usec] for tracks that have set_tempo
        """
        tempo_initial, initial_track_tempos = self.midi_analyzer.get_initial_tempo(
            self.midi_state.file
        )
        self.midi_state.tempo_initial = tempo_initial
        log.parameter("self.tempo", self.midi_state.tempo_initial)
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

    def update_upper_display_with_tempo_and_bar(self) -> None:
        """
        Update the upper digital with tempo, plus the bar number while playing or paused.
        """
        if self.current_tempo_bpm is None:
            return

        speed = self.transport_controller.speed
        tempo_text = f"Tempo: {round(self.current_tempo_bpm * speed)} BPM"
        if abs(speed - 1.0) > 1e-6:
            tempo_text += f" ({round(speed * 100)}%)"
        if (
            self.transport_controller.is_loaded
            and self.transport_controller.state != TransportState.STOPPED
        ):
            bar, beat = self.current_bar_beat()
            tempo_text += f" | Bar {bar}.{beat}"

        if tempo_text != self._upper_display_text:
            self._upper_display_text = tempo_text
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
                Midi.value.ZERO,
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
        Play from the current position, or resume if paused.
        """
        if not self.midi_state.file:
            # Nothing to play: undo the click's own check toggle
            self.transport.set_state(self.transport_controller.state)
            return
        if self.transport_controller.state == TransportState.STOPPED:
            # Reload so track-viewer edits made since the last play are heard
            self.transport_controller.load(self.midi_state.file, keep_position=True)
            self._sync_transport_settings()
            remaining = (
                self.transport_controller.duration_seconds
                - self.transport_controller.position_seconds
            )
            self.usb_recorder.start_recording(
                duration_seconds=remaining / self.transport_controller.speed
            )
        self.transport_controller.play()

    def midi_playback_toggle(self) -> None:
        """Space: pause if playing, otherwise play (or resume)."""
        if self.transport_controller.state == TransportState.PLAYING:
            self.transport_controller.pause()
        else:
            self.midi_playback_start()

    def midi_playback_rewind(self) -> None:
        """Home: go back to the start, keeping play/pause/stop state."""
        if self.is_midi_ready():
            self.transport_controller.seek_seconds(0.0)

    def midi_playback_panic(self, *_args) -> None:
        """Silence the instrument without changing the transport state."""
        self.transport_controller.panic()

    # --- Loop, speed, clock -------------------------------------------------

    def midi_loop_toggled(self, checked: bool = False) -> None:
        """Loop button: loop the A–B range, or the whole song."""
        self.transport_controller.set_loop(bool(checked))

    def midi_loop_toggle_shortcut(self) -> None:
        """L: toggle looping."""
        self.transport_controller.set_loop(not self.transport_controller.loop_enabled)

    def midi_loop_set_a(self, *_args) -> None:
        """Set the loop start at the playback position."""
        self._set_loop_point(0)

    def midi_loop_set_b(self, *_args) -> None:
        """Set the loop end at the playback position."""
        self._set_loop_point(1)

    def _set_loop_point(self, which: int) -> None:
        if not self.is_midi_ready():
            return
        points = list(self._loop_points)
        points[which] = self._snap_to_bar(self.transport_controller.position_seconds)
        a, b = points
        if a is not None and b is not None and abs(a - b) > 1e-3:
            a, b = sorted((a, b))
            self._loop_points = (a, b)
            self.transport_controller.set_loop(True, a, b)
        else:
            self._loop_points = (a, b)
            self.playback_options.set_loop_points(a, b)

    # --- Trim ---------------------------------------------------------------

    def _ask_trim_range(self, title: str, description: str) -> Optional[tuple[int, int]]:
        """
        Ask for the range to keep, starting from the A–B range (else the whole
        file); (start, end) in ticks, or None if cancelled.
        """
        duration = self.transport_controller.duration_seconds
        a, b = self._loop_points
        start, end = (a, b) if a is not None and b is not None else (0.0, duration)
        dialog = TrimDialog(
            title=title,
            description=description,
            start=start,
            end=end,
            duration=duration,
            bar_beat=self.transport_controller.bar_beat_at_seconds,
            playhead=lambda: self._snap_to_bar(self.transport_controller.position_seconds),
            parent=self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return None
        start, end = dialog.range_seconds()
        return (
            self.playback_engine.seconds_to_tick(start),
            self.playback_engine.seconds_to_tick(end),
        )

    def midi_trim_file(self, *_args) -> None:
        """Trim button: keep only part of the file, moved to the start."""
        if not self.is_midi_ready():
            return
        ticks = self._ask_trim_range(
            "Trim MIDI File",
            "Keep only this part of every track; it then starts at 0:00. "
            "The tempo, programs and controllers in force at the start are kept. "
            "The file on disk changes only when you save.",
        )
        if ticks is None:
            return
        trimmed = trim_midi_file(self.midi_state.file, *ticks)
        self.midi_playback_stop()
        # The A–B range and the playback position refer to the old timing
        self.midi_loop_clear()
        self.midi_file.midi_track_viewer.set_midi_file(trimmed, keep_track_state=True)
        self.transport_controller.seek_seconds(0.0)
        log.message(f"Trimmed the MIDI file to ticks {ticks[0]}–{ticks[1]}")

    def midi_trim_track(self, track_index: int) -> None:
        """Trim Track… (track menu): remove the track's notes outside a range."""
        if not self.is_midi_ready() or not (
            0 <= track_index < len(self.midi_state.file.tracks)
        ):
            return
        track = self.midi_state.file.tracks[track_index]
        name = track.name or f"Track {track_index + 1}"
        ticks = self._ask_trim_range(
            f"Trim {name}",
            f"Remove the notes of '{name}' outside this range. The track keeps "
            "its timing, so it stays in step with the others. "
            "The file on disk changes only when you save.",
        )
        if ticks is None:
            return
        self.midi_file.midi_track_viewer.replace_track(
            track_index, trim_track(track, *ticks)
        )
        log.message(f"Trimmed track {track_index + 1} ({name}) to ticks {ticks[0]}–{ticks[1]}")

    def midi_loop_clear(self, *_args) -> None:
        """Forget the A–B range so Loop repeats the whole song."""
        self._loop_points = (None, None)
        self.transport_controller.clear_loop_range()

    def _on_transport_loop_changed(self) -> None:
        """Show loop on/off and the A–B range on the button, label and ruler."""
        loop_range = self.transport_controller.loop_range_seconds
        enabled = self.transport_controller.loop_enabled
        self.playback_options.set_loop_checked(enabled)
        if loop_range is not None:
            self._loop_points = loop_range
        self.playback_options.set_loop_points(*self._loop_points)
        self.midi_file.midi_track_viewer.ruler.set_loop_region(loop_range, enabled)

    def on_playback_speed_changed(self, percent: int) -> None:
        """Speed spin box (percent of the file's tempo)."""
        self.transport_controller.set_speed(percent / 100.0)
        self.update_upper_display_with_tempo_and_bar()

    def on_send_clock_toggled(self, checked: bool) -> None:
        """Send MIDI Clock / Start / Stop / Song Position to the JD-Xi."""
        self.transport_controller.set_send_clock(checked)

    # --- Keyboard and drag-and-drop -----------------------------------------

    def _init_shortcuts(self) -> None:
        """Space = play/pause, Home = back to start, L = loop on/off."""
        shortcuts = {
            Qt.Key.Key_Space: self.midi_playback_toggle,
            Qt.Key.Key_Home: self.midi_playback_rewind,
            Qt.Key.Key_L: self.midi_loop_toggle_shortcut,
        }
        self._shortcuts = []
        for key, slot in shortcuts.items():
            shortcut = QShortcut(QKeySequence(key), self)
            # Text fields keep these keys while they have focus
            shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
            shortcut.activated.connect(slot)
            self._shortcuts.append(shortcut)

    @staticmethod
    def _dropped_midi_path(event: QDragEnterEvent | QDropEvent) -> Optional[str]:
        """First local .mid/.midi file in a drag, if any."""
        if not event.mimeData().hasUrls():
            return None
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path and Path(path).suffix.lower() in (".mid", ".midi"):
                return path
        return None

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if self._dropped_midi_path(event):
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event: QDropEvent) -> None:
        path = self._dropped_midi_path(event)
        if path:
            event.acceptProposedAction()
            self.midi_load_file_from_path(path)
        else:
            super().dropEvent(event)

    def _sync_transport_settings(self) -> None:
        """Push mute, track velocity and event-suppression settings to the transport (applies live)."""
        self.midi_state.muted_tracks = self.get_muted_tracks()
        self.midi_state.muted_channels = self.get_muted_channels()
        self.transport_controller.set_mutes(
            muted_tracks=self.midi_state.muted_tracks,
            muted_channels={
                ch - Midi.channel.BINARY_TO_DISPLAY
                for ch in self.midi_state.muted_channels
            },
        )
        self.transport_controller.set_track_velocity_scales(
            self.midi_file.midi_track_viewer.get_track_velocity_scales()
        )
        self.transport_controller.set_suppression(
            program_changes=self.midi_state.suppress_program_changes,
            control_changes=self.midi_state.suppress_control_changes,
        )

    def _on_transport_state_changed(self, state: TransportState) -> None:
        """Reflect the transport state in the buttons and digital display."""
        self.transport.set_state(state)
        self.update_upper_display_with_tempo_and_bar()

    def _on_transport_position_changed(self, seconds: float) -> None:
        """Move the slider and position label to the playback position."""
        if not self.midi_file.position_slider.isSliderDown():
            self.midi_file.position_slider.setValue(int(seconds))
        self.midi_file.midi_track_viewer.set_playhead(seconds)
        self.ui_position_label_set_time(seconds)

    def _on_transport_tempo_changed(self, tempo_us: int) -> None:
        """Show the tempo in effect at the playback position."""
        self.ui_display_set_tempo_usecs(tempo_us)

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
            channel_index + Midi.channel.BINARY_TO_DISPLAY
            in self.midi_state.muted_channels
        )

    def get_muted_tracks(self):
        """
        get_muted_tracks

        :return: None
        Get the muted tracks from the MIDI track viewer.
        """
        muted_tracks_raw = self.midi_file.midi_track_viewer.get_muted_tracks()
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
        muted_channels_raw = self.midi_file.midi_track_viewer.get_muted_channels()
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

    def midi_scrub_position(self):
        """
        Seek to the slider position, keeping the current play/pause/stop state.
        """
        if not self.is_midi_ready():
            log.message("No MIDI file loaded, ignoring seek")
            return
        self.transport_controller.seek_seconds(
            float(self.midi_file.position_slider.value())
        )

    def is_midi_ready(self) -> bool:
        """
        Checks if a MIDI file is loaded into the transport.
        """
        return bool(self.midi_state.file and self.transport_controller.is_loaded)

    def midi_playback_stop(self):
        """
        Stop playback, silence the instrument and rewind to the beginning.
        """
        self.transport_controller.stop()
        self.usb_recorder.recorder.stop_recording()
        log.message("MIDI playback stopped and reset to beginning")

    def closeEvent(self, event: QCloseEvent) -> None:
        """Ensure the playback thread is stopped before widget destruction."""
        self.transport_controller.shutdown()
        super().closeEvent(event)

    def ui_position_slider_reset(self) -> None:
        """
        position_slider_reset

        :return: None
        Reset the position slider and label to initial state.
        """
        self.midi_file.position_slider.setEnabled(False)
        self.midi_file.position_slider.setValue(0)
        self.midi_file.position_slider.setEnabled(True)
        self.midi_file.position_slider.setRange(
            0, int(self.midi_state.file_duration_seconds)
        )
        self.ui_position_label_set_time()

    def midi_file_position_label_update_time(
        self, time_seconds: Optional[float] = None
    ) -> None:
        """
        midi_file_position_label_update_time

        :param time_seconds: float, optional
        :return: None
        """
        self.midi_file.position_label_update_time(time_seconds)

    def current_bar_beat(self) -> tuple[int, int]:
        """
        Current (bar, beat), 1-based, at the playback position, following the
        file's tempo map and time signatures.
        """
        return self.transport_controller.bar_beat_at_seconds(
            self.transport_controller.position_seconds
        )

    def ui_position_label_set_time(self, elapsed_time: Optional[float] = None) -> None:
        """
        Update the position label with formatted elapsed time and total duration.
        Caps elapsed_time to total duration to prevent overflow digital.
        Also updates the bar number in the DigitalTitle upper digital.
        """
        total = self.midi_state.file_duration_seconds
        elapsed_capped = 0.0 if elapsed_time is None else min(elapsed_time, total)
        self.update_position_text(
            format_time(elapsed_capped),
            format_time(total),
            format_time(max(0.0, total - elapsed_capped)),
        )
        self.update_upper_display_with_tempo_and_bar()

    def update_position_text(
        self, elapsed_str: str, total_str: str, remaining_str: Optional[str] = None
    ):
        """update position text"""
        label_text = f"Playback Position: {elapsed_str} / {total_str}"
        if remaining_str is not None:
            label_text += f"  (-{remaining_str})"
        if self.midi_file.position_label.text() != label_text:
            self.midi_file.position_label.setText(label_text)

    def midi_playback_pause_toggle(self):
        """
        midi_playback_pause_toggle

        :return: None
        Pause if playing, resume if paused; does nothing when stopped.
        """
        state = self.transport_controller.state
        if state == TransportState.PLAYING:
            self.transport_controller.pause()
        elif state == TransportState.PAUSED:
            self.transport_controller.play()
        else:
            # Nothing to pause: undo the click's own check toggle
            self.transport.set_state(state)

    def _get_pattern_sequencer_editor(self):
        """Return the Pattern Sequencer editor instance if available, else None."""
        if not self.parent:
            return None
        if hasattr(self.parent, "get_existing_editor"):
            try:
                from jdxi_editor.ui.editors.pattern.pattern import PatternSequenceEditor

                return self.parent.get_existing_editor(PatternSequenceEditor)
            except Exception:
                return None
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
            if hasattr(pattern_editor, MidoMessageType.SET_TEMPO.value):
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
        """build specs for the Midi file player"""
        return {
            "buttons": self._build_button_specs(),
            "message_box": self._build_message_box_specs(),
            "check_box": self._build_checkbox_specs(),
        }

    def _build_button_specs(self) -> dict[str, ButtonSpec]:
        return {
            "automation_insert": ButtonSpec(
                label="Insert Program Change Here",
                tooltip="Insert Program Change at current position",
                icon=JDXi.UI.Icon.ADD,
                slot=self.insert_program_change_current_position,
            ),
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
                title="Drum Tracks Detected", message="", type_attr="Information"
            ),
            "error_detect_drums": MessageBoxSpec(
                title="Error", message="", type_attr="Critical"
            ),
            "error_classify_tracks": MessageBoxSpec(
                title="Error", message="", type_attr="Critical"
            ),
            "tracks_classified": MessageBoxSpec(
                title="Tracks Classified", message="", type_attr="Information"
            ),
            "error_saving_file": MessageBoxSpec(
                title="Error Saving File", message="", type_attr="Critical"
            ),
            # Generic templates (pass title= and message= at call site):
            "info": MessageBoxSpec(title="", message="", type_attr="Information"),
            "warning": MessageBoxSpec(title="", message="", type_attr="Warning"),
        }

    def _build_checkbox_specs(self) -> dict[str, CheckBoxSpec]:
        """build check box specs (event suppression moved to EventSuppressionGroup)"""
        return {}
