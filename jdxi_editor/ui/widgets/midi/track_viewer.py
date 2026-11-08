"""
Midi Track Viewer
"""

from copy import deepcopy

import mido
import qtawesome as qta
from decologr import Decologr as log
from PySide6.QtCore import QPoint, Qt, QEvent, QTimer, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLayout,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSlider,
    QSizePolicy,
)

from jdxi_editor.ui.common import JDXi, QVBoxLayout, QWidget
from jdxi_editor.ui.preset.tone.digital.list import JDXiPresetToneListDigital
from jdxi_editor.ui.widgets.midi.draggable_track_row import DraggableTrackRow
from jdxi_editor.ui.widgets.midi.slider.track_velocity import TrackVelocitySlider
from jdxi_editor.ui.widgets.midi.spin_box.spin_box import MidiSpinBox
from jdxi_editor.ui.widgets.midi.time_ruler import TimeRulerWidget
from jdxi_editor.ui.widgets.midi.track import MidiTrackWidget
from jdxi_editor.ui.widgets.midi.utils import build_tick_to_seconds, get_first_channel
from picomidi.constant import Midi
from picomidi.message.type import MidoMetaMessageType, MidoMessageType


class MidiTrackViewer(QWidget):
    """
    MidiTrackViewer
    """

    mute_changed = Signal()  # track/channel mute or solo state changed
    track_velocity_changed = Signal()  # a track's velocity scale changed
    file_changed = Signal(object)  # the viewer now shows this mido.MidiFile
    trim_track_requested = Signal(int)  # Trim Track… chosen for this track

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        self.midi_file = None
        self.event_index = None
        self.ruler = TimeRulerWidget()
        self.midi_track_widgets = {}  # MidiTrackWidget()
        self.muted_tracks: set[int] = set()  # To track muted tracks
        self.solo_track: int | None = None
        self._pre_solo_muted_tracks: set[int] | None = None
        self.track_mute_buttons: dict[int, QPushButton] = {}
        self.track_solo_buttons: dict[int, QPushButton] = {}
        # track index -> note velocity factor during playback (absent = 1.0)
        self.track_velocity_scales: dict[int, float] = {}
        self.track_velocity_sliders: dict[int, TrackVelocitySlider] = {}
        self._draggable_rows = {}
        self._selected_track_index: int | None = None

        # To track muted channels
        self.muted_channels: set[int] = set()
        # Per-track editors for batch apply
        self._track_name_edits: dict[int, QLineEdit] = {}
        self.track_channel_spins: dict[int, MidiSpinBox] = {}
        self._track_part_labels: dict[int, QLabel] = {}
        self._track_icon_labels: dict[int, QLabel] = {}
        # Channel edits wait CHANNEL_EDIT_DELAY_MS so repeated clicks merge
        self._pending_channels: dict[int, int] = {}
        self._channel_edit_timer = QTimer(self)
        self._channel_edit_timer.setSingleShot(True)
        self._channel_edit_timer.timeout.connect(self.flush_pending_edits)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Scrollable content widget
        self.scroll_content = QWidget()
        scroll_layout = QVBoxLayout(self.scroll_content)
        scroll_layout.setSpacing(0)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        # scroll_layout.addWidget(self.ruler)
        ruler_container = QWidget()
        self._ruler_layout = QHBoxLayout(ruler_container)
        self._ruler_layout.setContentsMargins(0, 0, 0, 0)
        self._ruler_layout.setSpacing(0)

        # Width is matched to the track controls in _align_ruler_to_tracks()
        self._ruler_spacer = QWidget()
        self._ruler_spacer.setFixedWidth(self.get_track_controls_width())
        self._ruler_layout.addWidget(self._ruler_spacer)

        self._ruler_layout.addWidget(self.ruler, stretch=1)

        scroll_layout.addWidget(ruler_container)

        # Add Mute Buttons for channels 1-16
        self.mute_buttons = {}
        mute_layout = QHBoxLayout()
        mute_layout.addWidget(QLabel("Mute Channels:"))

        for ch in range(1, 17):
            btn = QPushButton(f"{ch}")
            btn.setCheckable(True)
            btn.setFixedWidth(30)
            btn.toggled.connect(
                lambda checked, c=ch: self.toggle_channel_mute(c, checked)
            )
            btn.setStyleSheet(
                JDXi.UI.MidiPlayer.sequencer_button_style(
                    True, checked_means_inactive=True
                )
            )
            self.mute_buttons[ch] = btn
            mute_layout.addWidget(btn)

        # scroll_layout.addLayout(mute_layout)

        # Scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.scroll_area.setWidget(self.scroll_content)

        # Add scroll area to main layout
        main_layout.addWidget(self.scroll_area, 1)

        # Track zoom slider
        self.track_zoom_slider = QSlider(Qt.Horizontal)
        self.track_zoom_slider.setRange(1, 100)
        self.track_zoom_slider.setValue(50)
        self.track_zoom_slider.valueChanged.connect(self.update_track_zoom)
        self.update_track_zoom(self.track_zoom_slider.value())

        # Add zoom slider to layout
        main_layout.addWidget(QLabel("Track Zoom"))
        main_layout.addWidget(self.track_zoom_slider)

        self.setLayout(main_layout)

    def clear(self):
        """Clear the MIDI track view and reset state."""
        # Clear MIDI data
        self.midi_file = None
        self.event_index = None

        # Unmute all channels
        for ch, btn in self.mute_buttons.items():
            if btn.isChecked():
                btn.setChecked(False)
        self.muted_channels.clear()
        self.muted_tracks.clear()
        self.solo_track = None
        self._pre_solo_muted_tracks = None
        self.track_mute_buttons.clear()
        self.track_solo_buttons.clear()
        self.track_velocity_scales.clear()
        self.track_velocity_sliders.clear()
        self._track_name_edits.clear()
        self.track_channel_spins.clear()
        self._track_part_labels.clear()
        self._track_icon_labels.clear()
        self._pending_channels.clear()
        self._draggable_rows.clear()

        # Remove track widgets
        for track_key, track_widget in self.midi_track_widgets.copy().items():
            track_widget.setParent(None)
            track_widget.deleteLater()
        self.midi_track_widgets.clear()

        # Remove layouts/items from the channel controls layout
        if hasattr(self, "channel_controls_vlayout"):
            layout = self.channel_controls_vlayout
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.setParent(None)
                    widget.deleteLater()
                elif item.layout():
                    self._clear_layout(item.layout())  # See helper below

        # Reset zoom slider to default
        self.track_zoom_slider.setValue(50)

        # Optional: force a redraw
        self.update()

    def _clear_layout(self, layout: QLayout):
        """
        _clear_layout

        :param layout:
        :return:
        Recursively clear a layout and its children.
        """
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def clear_old(self):
        """Clear the MIDI track view and reset state."""
        # Clear MIDI data
        self.midi_file = None
        self.event_index = None

        # Unmute all channels
        for ch, btn in self.mute_buttons.items():
            if btn.isChecked():
                btn.setChecked(False)
        self.muted_channels.clear()
        self.muted_tracks.clear()

        # Remove track widgets
        for track_key, track_widget in self.midi_track_widgets.copy().items():
            track_widget.setParent(None)
            track_widget.deleteLater()
        self.midi_track_widgets.clear()

        # Reset zoom slider to default
        self.track_zoom_slider.setValue(50)

    def fit_tracks_to_view(self) -> None:
        """Scale the timeline so the full MIDI file fits the visible viewer width."""
        if self.scroll_area is None:
            return

        viewport_width = self.scroll_area.viewport().width()
        if viewport_width <= 0:
            QTimer.singleShot(0, self.fit_tracks_to_view)
            return

        min_content_width = self.get_track_controls_width() + 200
        target_width = max(min_content_width, viewport_width)
        self.scroll_content.setFixedWidth(target_width)
        self.scroll_content.updateGeometry()
        self.scroll_area.horizontalScrollBar().setValue(0)

        slider_value = max(1, min(100, target_width // 80))
        self.track_zoom_slider.blockSignals(True)
        self.track_zoom_slider.setValue(slider_value)
        self.track_zoom_slider.blockSignals(False)

        for widget in self.midi_track_widgets.values():
            widget.cached_pixmap = None
            widget.cached_width = 0
            widget.update()
        self.ruler.update()
        QTimer.singleShot(0, self._align_ruler_to_tracks)

    def _align_ruler_to_tracks(self) -> None:
        """Line the ruler up exactly with the track timelines below it."""
        widget = next(iter(self.midi_track_widgets.values()), None)
        if widget is None or not widget.isVisible():
            return
        left = widget.mapTo(self.scroll_content, QPoint(0, 0)).x()
        right_gap = self.scroll_content.width() - (left + widget.width())
        self._ruler_spacer.setFixedWidth(max(0, left))
        self._ruler_layout.setContentsMargins(0, 0, max(0, right_gap), 0)

    def set_playhead(self, seconds: float | None) -> None:
        """Show the playback position on the ruler and every track (None hides it)."""
        self.ruler.set_playhead(seconds)
        length = self.midi_file.length if self.midi_file else 0
        norm = None if seconds is None or not length else seconds / length
        for widget in self.midi_track_widgets.values():
            widget.set_playhead(norm)

    def resizeEvent(self, event: QEvent) -> None:
        super().resizeEvent(event)
        if self.midi_file is not None:
            self.fit_tracks_to_view()
        else:
            self.update_track_zoom(self.track_zoom_slider.value())

    def update_track_zoom(self, width: int):
        """
        update_track_zoom

        :param width: int slider value (1–100) used to set content width
        :return: None
        """
        min_content_width = self.get_track_controls_width() + 200
        content_width = max(min_content_width, width * 80)
        if self.scroll_area is not None:
            viewport_width = self.scroll_area.viewport().width()
            if viewport_width > 0:
                content_width = max(content_width, viewport_width)
        self.scroll_content.setFixedWidth(content_width)
        self.scroll_content.updateGeometry()
        QTimer.singleShot(0, self._align_ruler_to_tracks)

    def toggle_channel_mute(self, channel: int, is_muted: bool) -> None:
        """
        Toggle mute state for a specific MIDI channel.

        :param channel: int MIDI channel (1-16)
        :param is_muted: bool is the channel muted?
        :return: None
        """
        if is_muted:
            self.muted_channels.add(channel)
        else:
            self.muted_channels.discard(channel)

        # Unmuted = accent border; muted = grey
        if channel in self.mute_buttons:
            self.mute_buttons[channel].setStyleSheet(
                JDXi.UI.MidiPlayer.sequencer_button_style(
                    not is_muted, checked_means_inactive=True
                )
            )

        # Notify all track widgets
        for widget in self.midi_track_widgets.values():
            widget.update_muted_channels(self.muted_channels)
        self.mute_changed.emit()

    def select_track(self, track_index: int) -> None:
        """Highlight the chosen track row and its note events."""
        self._selected_track_index = track_index
        for idx, row in self._draggable_rows.items():
            row.set_row_selected(idx == track_index)
        for idx, widget in self.midi_track_widgets.items():
            if hasattr(widget, "set_selected"):
                widget.set_selected(idx == track_index)

    def update_muted_channels(self, muted_channels: set[int]) -> None:
        """
        Called when the global mute state is updated.
        """
        self.muted_channels = muted_channels
        print(f"Muted channels updated: {self.muted_channels}")
        self.update()  # trigger repaint or UI change if needed

    def _apply_muted_tracks_to_widgets(self) -> None:
        """Push the current muted-tracks set to all track row widgets."""
        for track_index, widget in self.midi_track_widgets.items():
            widget.muted = track_index in self.muted_tracks
            widget.update_muted_tracks(self.muted_tracks)

    def _sync_track_mute_solo_buttons(self) -> None:
        """Keep per-track mute/solo buttons aligned with internal state."""
        for track_index, btn in self.track_mute_buttons.items():
            btn.blockSignals(True)
            btn.setChecked(track_index in self.muted_tracks)
            btn.blockSignals(False)
        for track_index, btn in self.track_solo_buttons.items():
            btn.blockSignals(True)
            btn.setChecked(self.solo_track == track_index)
            btn.blockSignals(False)

    def _clear_solo(self, *, restore_pre_solo: bool = True) -> None:
        """Exit solo mode and optionally restore pre-solo mute state."""
        self.solo_track = None
        if restore_pre_solo and self._pre_solo_muted_tracks is not None:
            self.muted_tracks = set(self._pre_solo_muted_tracks)
        self._pre_solo_muted_tracks = None
        self._apply_muted_tracks_to_widgets()
        self._sync_track_mute_solo_buttons()

    def toggle_track_solo(self, track_index: int, is_solo: bool) -> None:
        """
        Solo a track: mute all other tracks and unmute the soloed track.

        :param track_index: Index of the track to solo
        :param is_solo: Whether solo is active for this track
        """
        if not self.midi_file:
            return

        if is_solo:
            if self.solo_track is None:
                self._pre_solo_muted_tracks = set(self.muted_tracks)
            self.solo_track = track_index
            num_tracks = len(self.midi_file.tracks)
            self.muted_tracks = {t for t in range(num_tracks) if t != track_index}
        elif self.solo_track == track_index:
            self._clear_solo(restore_pre_solo=True)
            self.mute_changed.emit()
            return

        self._apply_muted_tracks_to_widgets()
        self._sync_track_mute_solo_buttons()
        self.mute_changed.emit()

    def toggle_track_mute(self, track: int, is_muted: bool) -> None:
        """
        Toggle mute state for a specific MIDI track.

        :param track: int track index (0-based)
        :param is_muted: bool is the track muted?
        :return: None
        """
        if self.solo_track is not None:
            self._clear_solo(restore_pre_solo=True)

        if is_muted:
            self.muted_tracks.add(track)
        else:
            self.muted_tracks.discard(track)

        self._apply_muted_tracks_to_widgets()
        print(f"Muted tracks updated: {self.muted_tracks}")
        self.mute_changed.emit()

    def set_track_velocity_scale(self, track: int, scale: float) -> None:
        """
        Scale a track's note velocities during playback.

        :param track: int track index (0-based)
        :param scale: float factor, 1.0 = velocities as in the file
        """
        if scale == 1.0:
            self.track_velocity_scales.pop(track, None)
        else:
            self.track_velocity_scales[track] = scale
        slider = self.track_velocity_sliders.get(track)
        if slider is not None and slider.scale() != scale:
            slider.blockSignals(True)
            slider.set_scale(scale)
            slider.blockSignals(False)
        self.track_velocity_changed.emit()

    def get_track_velocity_scales(self) -> dict[int, float]:
        return dict(self.track_velocity_scales)

    def update_muted_tracks(self, muted_tracks: set[int]) -> None:
        """
        Called when the global mute state is updated.
        """
        self.muted_tracks = muted_tracks
        print(f"Muted tracks updated: {self.muted_tracks}")
        self.update()  # trigger repaint or UI change if needed

    def delete_track(self, track_index: int) -> None:
        """
        Ask user to confirm and delete a specific MIDI track and its widget.

        :param track_index: int
        :return: None
        """
        if not (0 <= track_index < len(self.midi_file.tracks)):
            raise IndexError("Invalid track index")
        if len(self.midi_file.tracks) == 1:
            QMessageBox.information(
                self, "Delete Track", "A MIDI file needs at least one track."
            )
            return

        track = self.midi_file.tracks[track_index]
        track_name = track.name or f"Track {track_index + 1}"

        reply = QMessageBox.question(
            self,
            "Delete Track?",
            f"Are you sure you want to delete '{track_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        tracks = [t for i, t in enumerate(self.midi_file.tracks) if i != track_index]
        # new index -> old index (tracks after the deleted one move up)
        index_map = {
            new: (new if new < track_index else new + 1) for new in range(len(tracks))
        }
        self._replace_tracks(tracks, index_map)
        log.message(f"Deleted track {track_index + 1} ({track_name})")

    def clone_track(self, track_index: int) -> None:
        """
        Insert a copy of a track directly below it.

        :param track_index: int
        :return: None
        """
        if not (0 <= track_index < len(self.midi_file.tracks)):
            raise IndexError("Invalid track index")

        source = self.midi_file.tracks[track_index]
        copy = deepcopy(source)
        new_name = f"{source.name or f'Track {track_index + 1}'} (copy)"
        for msg in copy:
            if msg.type == MidoMetaMessageType.TRACK_NAME.value:
                msg.name = new_name
                break
        else:
            copy.insert(
                0,
                mido.MetaMessage(
                    MidoMetaMessageType.TRACK_NAME.value, name=new_name, time=0
                ),
            )

        tracks = list(self.midi_file.tracks)
        tracks.insert(track_index + 1, copy)
        # The copy (track_index + 1) starts with the source's mute state
        index_map = {
            new: (new if new <= track_index else new - 1) for new in range(len(tracks))
        }
        self._replace_tracks(tracks, index_map)
        log.message(f"Cloned track {track_index + 1} as '{new_name}'")

    def _replace_tracks(
        self, tracks: list[mido.MidiTrack], index_map: dict[int, int]
    ) -> None:
        """
        Show a new file made of *tracks*, keeping per-track mutes and velocity.

        :param tracks: Tracks for the new file, in order
        :param index_map: New track index -> index the track had before
        """
        old_muted = set(self.muted_tracks)
        old_scales = dict(self.track_velocity_scales)
        new_midi = mido.MidiFile(
            type=1 if len(tracks) > 1 else self.midi_file.type,
            ticks_per_beat=self.midi_file.ticks_per_beat,
        )
        new_midi.tracks.extend(tracks)
        # Solo ends; the tracks it muted stay muted
        self.solo_track = None
        self._pre_solo_muted_tracks = None
        self.muted_tracks = {
            new for new, old in index_map.items() if old in old_muted
        }
        self.track_velocity_scales = {
            new: old_scales[old] for new, old in index_map.items() if old in old_scales
        }
        self.set_midi_file(new_midi, keep_track_state=True)
        self.mute_changed.emit()

    def _show_track_menu(self, track_index: int, global_pos: QPoint) -> None:
        """Right-click menu for a track row."""
        if not self.midi_file or not (0 <= track_index < len(self.midi_file.tracks)):
            return
        menu = QMenu(self)
        clone_action = menu.addAction("Clone Track")
        trim_action = menu.addAction("Trim Track…")
        delete_action = menu.addAction("Delete Track…")
        chosen = menu.exec(global_pos)
        if chosen is clone_action:
            self.clone_track(track_index)
        elif chosen is trim_action:
            self.trim_track_requested.emit(track_index)
        elif chosen is delete_action:
            self.delete_track(track_index)

    # --- Edits in the track headers (applied immediately) ---------------------

    # Channel arrows clicked in quick succession become one change
    CHANNEL_EDIT_DELAY_MS = 300

    def _track_part(self, first_channel: int, has_channel: bool):
        """Part label and icon pixmap for a track on *first_channel* (1-16)."""
        mp = JDXi.UI.MidiPlayer
        if not has_channel:
            label, icon_name, color = "Tempo / Conductor", "mdi.metronome", mp.TEXT_SECONDARY
        else:
            label, icon_name, color = {
                1: ("Digital 1", "mdi.piano", "#B44646"),
                2: ("Digital 2", "mdi.piano", "#C88C3C"),
                3: ("Analog", "mdi.sine-wave", JDXi.UI.Style.ACCENT_ANALOG),
                10: ("Drums", "fa5s.drum", "#7850A0"),
            }.get(first_channel, ("MIDI", "mdi.piano", mp.TEXT_SECONDARY))
        pixmap = qta.icon(icon_name, color=color).pixmap(
            mp.TRACK_ICON_SIZE, mp.TRACK_ICON_SIZE
        )
        return label, pixmap

    def _on_channel_edited(self, track_index: int, display_channel: int) -> None:
        self._pending_channels[track_index] = display_channel + Midi.channel.DISPLAY_TO_BINARY
        self._channel_edit_timer.start(self.CHANNEL_EDIT_DELAY_MS)

    def flush_pending_edits(self) -> None:
        """Apply channel edits still waiting for the merge delay."""
        self._channel_edit_timer.stop()
        pending, self._pending_channels = self._pending_channels, {}
        if pending:
            self.set_track_channels(pending)

    def _on_name_edited(self, track_index: int, text: str) -> None:
        if not self.midi_file or track_index >= len(self.midi_file.tracks):
            return
        if text.strip() != (self.midi_file.tracks[track_index].name or "").strip():
            self.rename_track(track_index, text.strip())

    def set_track_channels(self, channels: dict[int, int]) -> None:
        """
        Move tracks to new channels (0-15), in place.

        Only the changed rows are refreshed (lane, icon, part label); the
        headers are not rebuilt, so the selector being edited keeps focus.
        """
        if not self.midi_file:
            return
        changed = {}
        for track_index, channel in channels.items():
            if not (0 <= channel <= 15) or not (
                0 <= track_index < len(self.midi_file.tracks)
            ):
                continue
            source = self.midi_file.tracks[track_index]
            if get_first_channel(source) == channel:
                continue
            track = mido.MidiTrack(
                msg.copy(channel=channel) if hasattr(msg, "channel") else msg.copy()
                for msg in source
            )
            changed[track_index] = track
        if changed:
            self._update_tracks_in_place(changed)
            log.message(f"Track channels changed: { {t + 1: c + 1 for t, c in channels.items()} }")

    def rename_track(self, track_index: int, new_name: str) -> None:
        """Rename a track in place."""
        if not (0 <= track_index < len(self.midi_file.tracks)):
            raise IndexError("Invalid track index")
        track = mido.MidiTrack(msg.copy() for msg in self.midi_file.tracks[track_index])
        self.set_track_name(track, new_name)
        self._update_tracks_in_place({track_index: track})

    def replace_track(self, track_index: int, track: mido.MidiTrack) -> None:
        """Show *track* in place of track *track_index* (an edit of that track)."""
        if not (0 <= track_index < len(self.midi_file.tracks)):
            raise IndexError("Invalid track index")
        self._update_tracks_in_place({track_index: track})

    def _update_tracks_in_place(self, changed: dict[int, mido.MidiTrack]) -> None:
        """New file with *changed* tracks replaced; refresh only those rows."""
        new_midi = mido.MidiFile(
            type=self.midi_file.type, ticks_per_beat=self.midi_file.ticks_per_beat
        )
        new_midi.tracks.extend(
            changed.get(i, track) for i, track in enumerate(self.midi_file.tracks)
        )
        self.midi_file = new_midi
        self.ruler.set_midi_file(new_midi)
        tick_to_seconds = build_tick_to_seconds(new_midi)
        for track_index, track in changed.items():
            widget = self.midi_track_widgets.get(track_index)
            if widget is not None:
                widget.tick_to_seconds = tick_to_seconds
                widget.set_track(track, new_midi.length, new_midi.ticks_per_beat)
            has_channel = any(hasattr(msg, "channel") for msg in track)
            first_channel = get_first_channel(track) + Midi.channel.BINARY_TO_DISPLAY
            part, pixmap = self._track_part(first_channel, has_channel)
            if track_index in self._track_part_labels:
                self._track_part_labels[track_index].setText(part)
            if track_index in self._track_icon_labels:
                self._track_icon_labels[track_index].setPixmap(pixmap)
            spin = self.track_channel_spins.get(track_index)
            if spin is not None and spin.value() != first_channel:
                spin.blockSignals(True)
                spin.setValue(first_channel)
                spin.blockSignals(False)
        self.file_changed.emit(new_midi)

    def change_track_name(self, track_index: int, new_name: str) -> None:
        """
        Change the name of a specific MIDI track.

        :param track_index: int
        :param new_name: str
        :return: None
        """
        if not (0 <= track_index < len(self.midi_file.tracks)):
            raise IndexError("Invalid track index")

        midi_file_copy = deepcopy(self.midi_file)  # Deep copy of the MIDI file
        track_copy = midi_file_copy.tracks[track_index]

        self.set_track_name(track_copy, new_name)
        log.message(f"Renamed track {track_index} to {new_name}")

        self.set_midi_file(midi_file_copy, keep_track_state=True)

    def set_track_name(self, track, new_name):
        for msg in track:
            if msg.type == "track_name":
                msg.name = new_name
                return track
        # If not found, insert it at the beginning
        track.insert(
            0,
            mido.MetaMessage(
                MidoMetaMessageType.TRACK_NAME.value, name=new_name, time=0
            ),
        )
        return track

    def change_track_channel(self, track_index: int, new_channel: int) -> None:
        """
        Change the MIDI channel of a specific track.

        :param track_index: int
        :param new_channel: int
        :return: None
        """
        if not (0 <= new_channel <= 15):
            raise ValueError("MIDI channel must be between 0 and 15")
        if not (0 <= track_index < len(self.midi_file.tracks)):
            raise IndexError("Invalid track index")

        old_channel = get_first_channel(self.midi_file.tracks[track_index])
        log.message(
            f"Changing track {track_index} channel from {old_channel} to {new_channel}"
        )

        tracks = []
        for i, t in enumerate(self.midi_file.tracks):
            new_track = mido.MidiTrack()
            for msg in t:
                msg_copy = msg.copy()
                # Only change channel for channel messages
                if i == track_index and hasattr(msg_copy, "channel"):
                    msg_copy.channel = new_channel
                new_track.append(msg_copy)
            tracks.append(new_track)

        new_channel_tested = get_first_channel(tracks[track_index])
        log.message(
            f"Changed track {track_index} channel from {old_channel} to {new_channel_tested}"
        )

        # Same tracks in the same order: mutes carry over
        self._replace_tracks(tracks, {i: i for i in range(len(tracks))})

    def make_apply_name(self, track_name: str, text_edit: QLineEdit) -> callable:
        """
        Create a slot for applying changes to the track channel.

        :param track_name: str Track name to modify
        :param text_edit: QLineEdit for selecting the name
        :return: callable function to apply changes
        """
        log.message(f"Track index: {track_name}, Text: {text_edit.text()}")
        return lambda: self.change_track_name(track_name, text_edit.text())

    def set_midi_file(self, midi_file: mido.MidiFile, keep_track_state: bool = False) -> None:
        """
        Set the MIDI file for the widget and create channel controls.

        :param midi_file:
        :param keep_track_state: keep track mutes, solo and velocity scales
            (an edit of the same tracks, in the same order); a new file starts
            unmuted at 100 %
        :return: None
        """
        track_count = len(midi_file.tracks)
        kept_muted = (
            {t for t in self.muted_tracks if t < track_count} if keep_track_state else set()
        )
        kept_solo = self.solo_track if keep_track_state else None
        if kept_solo is not None and kept_solo >= track_count:
            kept_solo = None
        kept_pre_solo = self._pre_solo_muted_tracks if kept_solo is not None else None
        kept_scales = (
            {t: v for t, v in self.track_velocity_scales.items() if t < track_count}
            if keep_track_state
            else {}
        )
        self.midi_file = midi_file
        self.ruler.set_midi_file(midi_file)

        # Clear existing selectors if reloading
        if not hasattr(self, "channel_controls_vlayout"):
            self.channel_controls_vlayout = QVBoxLayout()
            self.scroll_content.layout().addLayout(self.channel_controls_vlayout)
        else:
            self.clear_layout(self.channel_controls_vlayout)

        self.midi_track_widgets = {}
        self._draggable_rows = {}
        self.solo_track = kept_solo
        self._pre_solo_muted_tracks = kept_pre_solo
        self.muted_tracks = kept_muted
        self.track_velocity_scales = kept_scales
        self.track_velocity_sliders = {}
        # Rows are rebuilt: per-row widgets and edits of the old rows go
        self._channel_edit_timer.stop()
        self._pending_channels = {}
        self.track_channel_spins = {}
        self._track_name_edits = {}
        self._track_part_labels = {}
        self._track_icon_labels = {}
        self.track_mute_buttons = {}
        self.track_solo_buttons = {}
        tick_to_seconds = build_tick_to_seconds(midi_file)
        # Create each track widget and add it to the layout
        for i, track in enumerate(midi_file.tracks):
            hlayout = QHBoxLayout()
            first_channel = get_first_channel(track) + Midi.channel.BINARY_TO_DISPLAY
            # Optional: Get the track name to show in dialog
            track = self.midi_file.tracks[i]
            track_name = getattr(
                track, "name", f"Track {i + Midi.channel.BINARY_TO_DISPLAY}"
            )
            mp = JDXi.UI.MidiPlayer
            has_channel = any(hasattr(msg, "channel") for msg in track)
            has_notes = any(
                msg.type == MidoMessageType.NOTE_ON.value and msg.velocity > 0
                for msg in track
            )
            part, pixmap = self._track_part(first_channel, has_channel)

            # Header: two lines in a fixed-width column
            #   1  [icon] Name ........... [mute] [solo]
            #      [Ch 1] Digital 1 ...... [velocity]
            # Clone / Delete are in the right-click menu; edits apply at once
            header = QWidget()
            header.setFixedWidth(mp.TRACK_HEADER_WIDTH)
            header.setFixedHeight(mp.TRACK_HEIGHT)
            header_layout = QVBoxLayout(header)
            header_layout.setContentsMargins(4, 3, 4, 3)
            header_layout.setSpacing(2)
            top_row = QHBoxLayout()
            top_row.setSpacing(4)
            bottom_row = QHBoxLayout()
            bottom_row.setSpacing(4)
            header_layout.addLayout(top_row)
            header_layout.addLayout(bottom_row)
            control_size = JDXi.UI.Style.BUTTON_TRACK_WIDTH

            track_number_label = QLabel(f"{i + 1}")
            track_number_label.setFixedWidth(mp.TRACK_NUMBER_WIDTH)
            track_number_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            track_number_label.setStyleSheet(
                f"color: {mp.TEXT_SECONDARY}; font-size: {mp.FONT_TRACK_SECONDARY};"
            )
            top_row.addWidget(track_number_label)

            icon_label = QLabel()
            icon_label.setPixmap(pixmap)
            icon_label.setFixedWidth(mp.TRACK_ICON_SIZE)
            top_row.addWidget(icon_label)
            self._track_icon_labels[i] = icon_label

            track_name_line_edit = QLineEdit()
            track_name_line_edit.setText(track_name.strip())
            track_name_line_edit.setCursorPosition(0)  # show the start of long names
            track_name_line_edit.setPlaceholderText("Unnamed")
            track_name_line_edit.setToolTip("Track name (applied on Enter or when you click away)")
            track_name_line_edit.editingFinished.connect(
                lambda tr=i, le=track_name_line_edit: self._on_name_edited(tr, le.text())
            )
            track_name_line_edit.setStyleSheet(mp.track_name_stylesheet())
            track_name_line_edit.setAlignment(Qt.AlignLeft)
            top_row.addWidget(track_name_line_edit, 1)
            self._track_name_edits[i] = track_name_line_edit

            mute_icon = JDXi.UI.Icon.get_icon(
                JDXi.UI.Icon.MUTE, color=JDXi.UI.Style.FOREGROUND
            )
            mute_button = QPushButton()
            mute_button.setIcon(mute_icon)
            mute_button.setToolTip("Mute Track")
            mute_button.setFixedSize(control_size, control_size)
            mute_button.setCheckable(True)
            mute_button.setStyleSheet(mp.track_toggle_stylesheet(mp.ACCENT))
            mute_button.toggled.connect(
                lambda checked, tr=i: self.toggle_track_mute(tr, checked)
            )
            top_row.addWidget(mute_button)
            self.track_mute_buttons[i] = mute_button

            solo_icon = JDXi.UI.Icon.get_icon(
                JDXi.UI.Icon.SOLO,
                color=JDXi.UI.Style.FOREGROUND,
                fallback="mdi.headphones",
            )
            solo_button = QPushButton()
            solo_button.setIcon(solo_icon)
            solo_button.setToolTip("Solo Track (mute all other tracks)")
            solo_button.setFixedSize(control_size, control_size)
            solo_button.setCheckable(True)
            solo_button.setStyleSheet(mp.track_toggle_stylesheet(mp.SOLO))
            solo_button.toggled.connect(
                lambda checked, tr=i: self.toggle_track_solo(tr, checked)
            )
            top_row.addWidget(solo_button)
            self.track_solo_buttons[i] = solo_button

            # Second line, under the icon: the channel selector is the
            # channel display; tracks without channel data (tempo, markers)
            # have none
            bottom_row.addSpacing(mp.TRACK_NUMBER_WIDTH + 4)
            if has_channel:
                spin = MidiSpinBox()
                spin.setToolTip("MIDI channel of the track (changes apply immediately)")
                spin.setValue(first_channel)
                spin.valueChanged.connect(
                    lambda value, tr=i: self._on_channel_edited(tr, value)
                )
                spin.setFixedWidth(mp.TRACK_CHANNEL_WIDTH)
                spin.setFixedHeight(control_size)
                spin.setPrefix("Ch ")
                bottom_row.addWidget(spin)
                self.track_channel_spins[i] = spin
            secondary = QLabel(part)
            secondary.setStyleSheet(mp.track_secondary_stylesheet())
            bottom_row.addWidget(secondary, 1)
            self._track_part_labels[i] = secondary

            velocity_slider = TrackVelocitySlider()
            velocity_slider.set_scale(self.track_velocity_scales.get(i, 1.0))
            velocity_slider.setFixedWidth(JDXi.UI.Style.TRACK_VELOCITY_SLIDER_WIDTH)
            velocity_slider.setFixedHeight(control_size)
            velocity_slider.valueChanged.connect(
                lambda _, tr=i, sl=velocity_slider: self.set_track_velocity_scale(
                    tr, sl.scale()
                )
            )
            velocity_slider.setVisible(has_notes)
            bottom_row.addWidget(velocity_slider)
            self.track_velocity_sliders[i] = velocity_slider

            hlayout.addWidget(header)

            # Add the MidiTrackWidget for the specific track
            self.midi_track_widgets[i] = MidiTrackWidget(
                track=track,
                track_number=i,
                total_length=midi_file.length,
                ticks_per_beat=midi_file.ticks_per_beat,
                tick_to_seconds=tick_to_seconds,
            )
            hlayout.addWidget(self.midi_track_widgets[i])

            # Wrap the layout in a draggable row widget
            draggable_row = DraggableTrackRow(i, hlayout, self.scroll_content)
            # Rows keep their height and the list scrolls, rather than squeezing
            draggable_row.setFixedHeight(mp.TRACK_HEIGHT)
            draggable_row.track_moved.connect(self.move_track)
            draggable_row.track_clicked.connect(self.select_track)
            draggable_row.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            draggable_row.customContextMenuRequested.connect(
                lambda pos, tr=i, row=draggable_row: self._show_track_menu(
                    tr, row.mapToGlobal(pos)
                )
            )
            self._draggable_rows[i] = draggable_row
            self.channel_controls_vlayout.addWidget(draggable_row)

        self.channel_controls_vlayout.addStretch()
        self._apply_muted_tracks_to_widgets()
        self._sync_track_mute_solo_buttons()
        self.fit_tracks_to_view()
        self.file_changed.emit(midi_file)

    def get_track_controls_width(self) -> int:
        """
        Returns the estimated total width of all controls to the left of the MidiTrackWidget.
        """
        # Fixed widths from layout:
        # Apply, Mute, Solo, Delete, Clone track buttons, velocity slider
        # + label/spin controls
        return JDXi.UI.MidiPlayer.TRACK_HEADER_WIDTH + 10

    def clear_layout(self, layout: QLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())

    def refresh_track_list(self):
        """
        refresh_track_list

        :return:
        """
        self.update()

    # Channel (1-16) → JD-Xi preset number (e.g. 159 Picked Bass, 162 Piano, 1 JP8 Strings)
    _CHANNEL_PRESET_MAP = {
        1: 159,  # Picked Bass
        2: 162,  # JD Piano 1
        3: 1,    # JP8 Strings1 (Cheat Preset #1)
    }

    def apply_channel_presets(self) -> None:
        """Insert Bank Select and Program Change at the start of each track based on channel."""
        log.message(
            scope=self.__class__.__name__,
            message="apply_channel_presets (file update) called",
        )
        if not self.midi_file:
            log.message(
                scope=self.__class__.__name__,
                message="Early return: no midi_file",
            )
            return

        pc_map = JDXiPresetToneListDigital.PROGRAM_CHANGE
        new_midi = mido.MidiFile()
        new_midi.ticks_per_beat = self.midi_file.ticks_per_beat

        for i, track in enumerate(self.midi_file.tracks):
            desired_display_ch = (
                self.track_channel_spins.get(i).value()
                if i in self.track_channel_spins
                else None
            )
            if desired_display_ch is None:
                new_track = mido.MidiTrack()
                for msg in track:
                    new_track.append(msg.copy())
                new_midi.tracks.append(new_track)
                continue

            preset_num = self._CHANNEL_PRESET_MAP.get(desired_display_ch)
            channel = desired_display_ch + Midi.channel.DISPLAY_TO_BINARY
            if preset_num is None or preset_num not in pc_map:
                new_track = mido.MidiTrack()
                for msg in track:
                    msg_copy = msg.copy()
                    if hasattr(msg_copy, "channel"):
                        msg_copy.channel = channel
                    new_track.append(msg_copy)
                new_midi.tracks.append(new_track)
                continue

            spec = pc_map[preset_num]
            msb = spec["MSB"]
            lsb = spec["LSB"]
            pc = spec["PC"]

            msgs = [
                mido.Message(
                    MidoMessageType.CONTROL_CHANGE.value,
                    control=0,
                    value=msb,
                    channel=channel,
                    time=0,
                ),
                mido.Message(
                    MidoMessageType.CONTROL_CHANGE.value,
                    control=32,
                    value=lsb,
                    channel=channel,
                    time=0,
                ),
                mido.Message(
                    MidoMessageType.PROGRAM_CHANGE.value,
                    program=max(0, pc - 1),
                    channel=channel,
                    time=0,
                ),
            ]

            new_track = mido.MidiTrack()
            for m in msgs:
                new_track.append(m)
            for msg in track:
                msg_copy = msg.copy()
                if hasattr(msg_copy, "channel"):
                    msg_copy.channel = channel
                new_track.append(msg_copy)

            new_midi.tracks.append(new_track)

        log.parameter(
            scope=self.__class__.__name__,
            message="Tracks with presets inserted",
            parameter=len(new_midi.tracks),
        )
        self.set_midi_file(new_midi, keep_track_state=True)

    def get_muted_channels(self):
        return self.muted_channels

    def get_muted_tracks(self):
        return self.muted_tracks

    def move_track(self, from_index: int, to_index: int) -> None:
        """
        Move a track from one position to another in the MIDI file.

        :param from_index: Source track index
        :param to_index: Target track index
        """
        if not self.midi_file:
            return

        if from_index == to_index:
            return

        if not (0 <= from_index < len(self.midi_file.tracks)):
            log.warning(f"Invalid from_index: {from_index}")
            return

        if not (0 <= to_index < len(self.midi_file.tracks)):
            log.warning(f"Invalid to_index: {to_index}")
            return

        log.message(f"Moving track {from_index + 1} to position {to_index + 1}")

        # order[new index] = old index
        order = list(range(len(self.midi_file.tracks)))
        order.insert(to_index, order.pop(from_index))
        tracks = [self.midi_file.tracks[old] for old in order]
        self._replace_tracks(tracks, dict(enumerate(order)))

        log.message(f"Track moved successfully")
