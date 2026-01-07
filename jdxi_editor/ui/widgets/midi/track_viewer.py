"""
Midi Track Viewer
"""

from copy import deepcopy

import mido
import qtawesome as qta
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.jdxi.style import JDXiStyle
from jdxi_editor.log.logger import Logger as log
from jdxi_editor.ui.widgets.midi.spin_box.spin_box import MidiSpinBox
from jdxi_editor.ui.widgets.midi.time_ruler import TimeRulerWidget
from jdxi_editor.ui.widgets.midi.track import MidiTrackWidget
from jdxi_editor.ui.widgets.midi.utils import get_first_channel
from picomidi.constant import MidiConstant


class MidiTrackViewer(QWidget):
    """
    MidiTrackViewer
    """

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.midi_file = None
        self.event_index = None
        self.ruler = TimeRulerWidget()
        self.midi_track_widgets = {}  # MidiTrackWidget()
        self.muted_tracks: set[int] = set()  # To track muted tracks

        # To track muted channels
        self.muted_channels: set[int] = set()
        # Per-track editors for batch apply
        self._track_name_edits: dict[int, QLineEdit] = {}
        self._track_channel_spins: dict[int, MidiSpinBox] = {}

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
        ruler_layout = QHBoxLayout(ruler_container)
        ruler_layout.setContentsMargins(0, 0, 0, 0)
        ruler_layout.setSpacing(0)

        left_spacer = QWidget()
        left_spacer.setFixedWidth(
            self.get_track_controls_width()
        )  # same width as controls
        ruler_layout.addWidget(left_spacer)

        ruler_layout.addWidget(self.ruler, stretch=1)

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
                "QPushButton:checked { background-color: #cc0000; color: white; }"
            )
            self.mute_buttons[ch] = btn
            mute_layout.addWidget(btn)

        scroll_layout.addLayout(mute_layout)

        # Scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setWidget(self.scroll_content)

        # Add scroll area to main layout
        main_layout.addWidget(scroll_area)

        # Track zoom slider
        self.track_zoom_slider = QSlider(Qt.Horizontal)
        self.track_zoom_slider.setRange(1, 100)
        self.track_zoom_slider.setValue(50)
        self.track_zoom_slider.valueChanged.connect(self.update_track_zoom)

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
        self._track_name_edits.clear()
        self._track_channel_spins.clear()

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

    def update_track_zoom(self, width: int):
        """
        update_track_zoom

        :param width: int
        :return: None
        """
        self.scroll_content.setFixedWidth(width * 80)

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

        # Notify all track widgets
        for widget in self.midi_track_widgets.values():
            widget.update_muted_channels(self.muted_channels)
        print(f"Muted channels updated: {self.muted_channels}")

    def update_muted_channels(self, muted_channels: set[int]) -> None:
        """
        Called when the global mute state is updated.
        """
        self.muted_channels = muted_channels
        print(f"Muted channels updated: {self.muted_channels}")
        self.update()  # trigger repaint or UI change if needed

    def toggle_track_mute(self, track: int, is_muted: bool) -> None:
        """
        Toggle mute state for a specific MIDI track.

        :param track: int MIDI channel (1-16)
        :param is_muted: bool is the channel muted?
        :return: None
        """
        if is_muted:
            self.muted_tracks.add(track)
        else:
            self.muted_tracks.discard(track)

        # Notify all track widgets
        for widget in self.midi_track_widgets.values():
            widget.update_muted_tracks(self.muted_tracks)
        print(f"Muted tracks updated: {self.muted_tracks}")

    def update_muted_tracks(self, muted_tracks: set[int]) -> None:
        """
        Called when the global mute state is updated.
        """
        self.muted_tracks = muted_tracks
        print(f"Muted tracks updated: {self.muted_tracks}")
        self.update()  # trigger repaint or UI change if needed

    def mute_track(self, track_index: int) -> None:
        """
        Mute a specific track

        :param track_index: int
        :return: None
        """
        if not (0 <= track_index < len(self.midi_file.tracks)):
            raise IndexError("Invalid track index")

        track_widget = self.midi_track_widgets[track_index]
        track_widget.muted = not track_widget.muted
        self.toggle_track_mute(track_index, track_widget.muted)

    def delete_track(self, track_index: int) -> None:
        """
        Ask user to confirm and delete a specific MIDI track and its widget.

        :param track_index: int
        :return: None
        """
        if not (0 <= track_index < len(self.midi_file.tracks)):
            raise IndexError("Invalid track index")

        # Optional: Get the track name to show in dialog
        track = self.midi_file.tracks[track_index]
        track_name = getattr(track, "name", f"Track {track_index + 1}")

        # Show confirmation dialog
        reply = QMessageBox.question(
            self,
            "Delete Track?",
            f"Are you sure you want to delete '{track_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            del self.midi_file.tracks[track_index]
            self.midi_track_widgets.pop(track_index)

            # Optional: update UI if needed
            self.refresh_track_list()

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

        self.set_midi_file(midi_file_copy)  # Replace with modified file

    def set_track_name(self, track, new_name):
        for msg in track:
            if msg.type == "track_name":
                msg.name = new_name
        # If not found, insert it at the beginning
        track.insert(0, mido.MetaMessage("track_name", name=new_name, time=0))
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

        new_midi = mido.MidiFile()
        new_midi.ticks_per_beat = self.midi_file.ticks_per_beat

        for i, t in enumerate(self.midi_file.tracks):
            new_track = mido.MidiTrack()
            for msg in t:
                msg_copy = msg.copy()
                # Only change channel for channel messages
                if i == track_index and hasattr(msg_copy, "channel"):
                    msg_copy.channel = new_channel
                new_track.append(msg_copy)
            new_midi.tracks.append(new_track)

        new_channel_tested = get_first_channel(new_midi.tracks[track_index])
        log.message(
            f"Changed track {track_index} channel from {old_channel} to {new_channel_tested}"
        )

        self.set_midi_file(new_midi)

    def make_apply_slot(self, track_index: int, spin_box: MidiSpinBox) -> callable:
        """
        Create a slot for applying changes to the track channel.

        :param track_index: int Track index to modify
        :param spin_box: MidiSpinBox Spin box for selecting the channel
        :return: callable function to apply changes
        """
        log.message(f"Track index: {track_index}, Spin box value: {spin_box.value()}")
        return lambda: self.change_track_channel(
            track_index, spin_box.value() + MidiConstant.CHANNEL_DISPLAY_TO_BINARY
        )

    def make_apply_name(self, track_name: str, text_edit: QLineEdit) -> callable:
        """
        Create a slot for applying changes to the track channel.

        :param track_name: str Track name to modify
        :param text_edit: QLineEdit for selecting the name
        :return: callable function to apply changes
        """
        log.message(f"Track index: {track_name}, Text: {text_edit.text()}")
        return lambda: self.change_track_name(track_name, text_edit.text())

    def set_midi_file(self, midi_file: mido.MidiFile) -> None:
        """
        Set the MIDI file for the widget and create channel controls.

        :param midi_file:
        :return: None
        """
        self.midi_file = midi_file
        self.ruler.set_midi_file(midi_file)

        # Clear existing selectors if reloading
        if not hasattr(self, "channel_controls_vlayout"):
            self.channel_controls_vlayout = QVBoxLayout()
            self.scroll_content.layout().addLayout(self.channel_controls_vlayout)
        else:
            self.clear_layout(self.channel_controls_vlayout)

        self.midi_track_widgets = {}
        # Create each track widget and add it to the layout
        for i, track in enumerate(midi_file.tracks):
            hlayout = QHBoxLayout()
            first_channel = (
                get_first_channel(track) + MidiConstant.CHANNEL_BINARY_TO_DISPLAY
            )
            # Optional: Get the track name to show in dialog
            track = self.midi_file.tracks[i]
            track_name = getattr(
                track, "name", f"Track {i + MidiConstant.CHANNEL_BINARY_TO_DISPLAY}"
            )
            icon_names = {
                10: "fa5s.drum",
            }
            colors = {3: JDXiStyle.ACCENT_ANALOG}
            color = colors.get(
                first_channel, JDXiStyle.ACCENT
            )  # Default color if not specified
            icon_name = icon_names.get(
                first_channel,
                "mdi.piano",
            )  # Default icon if not specified
            # Add QLabel for track number and channel
            pixmap = qta.icon(icon_name, color=color).pixmap(
                JDXiStyle.TRACK_ICON_PIXMAP_SIZE, JDXiStyle.TRACK_ICON_PIXMAP_SIZE
            )

            track_number_label = QLabel(f"{i + 1}")
            track_number_label.setFixedWidth(JDXiStyle.TRACK_BUTTON_WIDTH)
            hlayout.addWidget(track_number_label)

            icon_label = QLabel()
            icon_label.setPixmap(pixmap)
            icon_label.setFixedWidth(
                JDXiStyle.TRACK_ICON_PIXMAP_SIZE
            )  # Add some padding
            hlayout.addWidget(icon_label)

            label_vlayout = QVBoxLayout()
            label_vlayout.setContentsMargins(0, 0, 0, 0)
            label_vlayout.setSpacing(0)
            hlayout.addLayout(label_vlayout)
            line_label_row = QHBoxLayout()
            label_vlayout.addLayout(line_label_row)

            # Add QLineEdit for track label
            track_name_line_edit = QLineEdit()
            track_name_line_edit.setText(track_name)
            track_name_line_edit.setFixedWidth(JDXiStyle.TRACK_LABEL_WIDTH)
            track_name_line_edit.setToolTip("Track Name")
            track_name_line_edit.setStyleSheet(
                "QLineEdit { background-color: transparent; border: none; }"
            )
            track_name_line_edit.setAlignment(Qt.AlignLeft)
            temp_row = QHBoxLayout()
            line_label_row.addLayout(temp_row)
            # temp_row.addWidget(track_number_label)
            temp_row.addWidget(track_name_line_edit)
            # temp_row.addWidget(track_channel_label)
            self._track_name_edits[i] = track_name_line_edit

            # Add QSpinBox for selecting the MIDI channel
            spin = MidiSpinBox()
            spin.setToolTip(
                "Select MIDI Channel for Track, then click 'Apply' to save changes"
            )
            spin.setValue(first_channel)  # Offset for display
            spin.setFixedWidth(JDXiStyle.TRACK_SPINBOX_WIDTH)
            spin.setPrefix("Ch")
            line_label_row.addWidget(spin)
            self._track_channel_spins[i] = spin

            button_hlayout = QHBoxLayout()
            label_vlayout.addLayout(button_hlayout)

            apply_icon = qta.icon("fa5.save", color=JDXiStyle.FOREGROUND)
            apply_button = QPushButton()
            apply_button.setIcon(apply_icon)
            apply_button.setToolTip("Apply changes to Track Channel")
            apply_button.setFixedWidth(JDXiStyle.TRACK_SPINBOX_WIDTH)
            apply_button.clicked.connect(self.make_apply_slot(i, spin))
            # apply_button.clicked.connect(self.make_apply_name(i, track_name_line_edit))
            apply_button.clicked.connect(
                lambda _, tr=i, le=track_name_line_edit: self.change_track_name(
                    tr, le.text()
                )
            )
            """
            apply_button.clicked.connect(lambda _, tr=i, le=track_name_line_edit, sp=spin: (
            self.change_track_name(tr, le.text()),
            self.change_channel(tr, sp.value())
            ))
            """
            button_hlayout.addWidget(apply_button)

            mute_icon = qta.icon("msc.mute", color=JDXiStyle.FOREGROUND)
            mute_button = QPushButton()
            mute_button.setIcon(mute_icon)
            mute_button.setToolTip("Mute Track")
            mute_button.setFixedWidth(JDXiStyle.TRACK_BUTTON_WIDTH)
            mute_button.setCheckable(True)
            mute_button.clicked.connect(
                lambda _, tr=i: self.mute_track(tr)
            )  # Send internal value (0–15)
            mute_button.toggled.connect(
                lambda checked, tr=i: self.toggle_track_mute(tr, checked)
            )
            button_hlayout.addWidget(mute_button)

            delete_icon = qta.icon(
                "mdi.delete-empty-outline", color=JDXiStyle.FOREGROUND
            )
            delete_button = QPushButton()
            delete_button.setIcon(delete_icon)
            delete_button.setToolTip("Delete Track")
            delete_button.setFixedWidth(JDXiStyle.TRACK_BUTTON_WIDTH)
            delete_button.setCheckable(True)
            delete_button.clicked.connect(
                lambda _, tr=i: self.delete_track(tr)
            )  # Send internal value (0–15)
            button_hlayout.addWidget(delete_button)

            # Add the MidiTrackWidget for the specific track
            self.midi_track_widgets[i] = MidiTrackWidget(
                track=track, track_number=i, total_length=midi_file.length
            )  # Initialize the dictionary
            hlayout.addWidget(self.midi_track_widgets[i])

            self.channel_controls_vlayout.addLayout(hlayout)

        # Global Apply button
        apply_all_layout = QHBoxLayout()
        apply_all_layout.addStretch()
        apply_all_btn = QPushButton("Apply All Track Changes")
        apply_all_btn.setToolTip("Apply all Track Name and MIDI Channel changes")
        apply_all_btn.clicked.connect(self.apply_all_track_changes)
        apply_all_layout.addWidget(apply_all_btn)
        self.channel_controls_vlayout.addLayout(apply_all_layout)

        self.channel_controls_vlayout.addStretch()

    def get_track_controls_width(self) -> int:
        """
        Returns the estimated total width of all controls to the left of the MidiTrackWidget.
        """
        # Fixed widths from layout:
        # QLabels: JDXiStyle.ICON_PIXMAP_SIZE, JDXiStyle.TRACK_LABEL_WIDTH , QSpinBox: JDXiStyle.TRACK_MUTE_BUTTON_WIDTH, Apply: JDXiStyle.TRACK_MUTE_BUTTON_WIDTH, Mute: JDXiStyle.TRACK_MUTE_BUTTON_WIDTH, Delete: JDXiStyle.TRACK_MUTE_BUTTON_WIDTH + margins (~10)
        return (
            JDXiStyle.ICON_PIXMAP_SIZE
            + JDXiStyle.TRACK_LABEL_WIDTH
            + (JDXiStyle.TRACK_BUTTON_WIDTH * 4)
            + 10
        )  # = 2JDXiStyle.TRACK_MUTE_BUTTON_WIDTH

    def clear_layout(self, layout: QLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())

    def refresh_track_list(self):
        """
        refresh_track_list

        :return:
        """
        self.update()

    def apply_all_track_changes(self) -> None:
        """Apply all Track Name and Channel changes in one operation."""
        if not self.midi_file:
            return

        # Build a new MIDI file with updated channels
        new_midi = mido.MidiFile()
        new_midi.ticks_per_beat = self.midi_file.ticks_per_beat

        for i, t in enumerate(self.midi_file.tracks):
            desired_display_channel = (
                self._track_channel_spins.get(i).value()
                if i in self._track_channel_spins
                else None
            )
            desired_channel = (
                None
                if desired_display_channel is None
                else desired_display_channel + MidiConstant.CHANNEL_DISPLAY_TO_BINARY
            )
            new_track = mido.MidiTrack()

            for msg in t:
                msg_copy = msg.copy()
                if desired_channel is not None and hasattr(msg_copy, "channel"):
                    msg_copy.channel = desired_channel
                new_track.append(msg_copy)

            # Set or update track name
            new_name = (
                self._track_name_edits.get(i).text()
                if i in self._track_name_edits
                else None
            )
            if new_name:
                # Remove existing track_name meta to avoid duplicates
                filtered = [
                    m
                    for m in new_track
                    if not (m.is_meta and getattr(m, "type", "") == "track_name")
                ]
                new_track.clear()
                # Insert a track_name at the very beginning
                new_track.append(mido.MetaMessage("track_name", name=new_name, time=0))
                for m in filtered:
                    new_track.append(m)

            new_midi.tracks.append(new_track)

        self.set_midi_file(new_midi)

    def get_muted_channels(self):
        return self.muted_channels

    def get_muted_tracks(self):
        return self.muted_tracks
