"""
Midi Track Viewer
"""

import mido
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QSlider, QMessageBox

from jdxi_editor.jdxi.midi.constant import MidiConstant
from jdxi_editor.log.logger import Logger as log
from jdxi_editor.ui.widgets.midi.spin_box.spin_box import MidiSpinBox
from jdxi_editor.ui.widgets.midi.time_ruler import TimeRulerWidget
from jdxi_editor.ui.widgets.midi.track import MidiTrackWidget
from jdxi_editor.ui.widgets.midi.utils import get_first_channel


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
        self.muted_tracks = set()  # To track muted tracks

        # To track muted channels
        self.muted_channels: set[int] = set()

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Scrollable content widget
        self.scroll_content = QWidget()
        scroll_layout = QVBoxLayout(self.scroll_content)
        scroll_layout.setSpacing(0)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.addWidget(self.ruler)


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

    def update_muted_channels(self, muted_channels: set[int]) -> None:
        """
        Called when the global mute state is updated.
        """
        self.muted_channels = muted_channels
        self.update()  # trigger repaint or UI change if needed

    """
    def toggle_track_mute(self, track: int, is_muted: bool) -> None:
        ""
        Toggle mute state for a specific track.

        :param track: int - Track index (0-based)
        :param is_muted: bool - True to mute, False to unmute
        ""
        log.message(f"Toggling mute for track {track}: {'Muted' if is_muted else 'Unmuted'}")

        if is_muted:
            self.muted_channels.add(track)
        else:
            self.muted_channels.discard(track)

        # Optional: Immediately apply mute state (e.g., for live playback)
        self.apply_mute_state(track)"""

    """
    def apply_mute_state(self, track: int) -> None:
        if track in self.muted_channels:
            self.silence_track(track)
        else:
            self.unsilence_track(track)

    def silence_track(self, track: int) -> None:
        # Stop sending note-on messages or send all-notes-off
        self.midi_out.send_control_change(123, 0, channel=track)

    def unsilence_track(self, track: int) -> None:
        # Resume normal playback (nothing needed unless you pre-buffer notes)
        pass

    def play_next_event(self):
        ""Override or add the logic to handle muted channels.""
        if self.event_index >= len(self.midi_events):
            return

        tick, msg = self.midi_events[self.event_index]

        if hasattr(msg, "channel") and (msg.channel + 1) in self.muted_channels:
            return  # Skip muted channel
        else:
            self.send_midi_message(msg)  # Your MIDI playback logic

        self.event_index += 1"""

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
        track_name = getattr(track, 'name', f"Track {track_index + 1}")

        # Show confirmation dialog
        reply = QMessageBox.question(
            self,
            "Delete Track?",
            f"Are you sure you want to delete '{track_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            del self.midi_file.tracks[track_index]
            self.midi_track_widgets.pop(track_index)

            # Optional: update UI if needed
            self.refresh_track_list()

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
        log.message(f"Changing track {track_index} channel from {old_channel} to {new_channel}")

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
        log.message(f"Changed track {track_index} channel from {old_channel} to {new_channel_tested}")

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

    def set_midi_file(self, midi_file: mido.MidiFile) -> None:
        """
        Set the MIDI file for the widget and create channel controls.

        :param midi_file:
        :return: None
        """
        self.midi_file = midi_file
        self.ruler.set_midi_file(midi_file)

        # Clear existing selectors if reloading
        if hasattr(self, "channel_controls_layout"):
            old_layout = self.channel_controls_layout
            while old_layout.count():
                item = old_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            self.scroll_content.layout().removeItem(old_layout)
            del self.channel_controls_layout

        # else:
        self.channel_controls_layout = QVBoxLayout()
        self.scroll_content.layout().addLayout(self.channel_controls_layout)

        self.midi_track_widgets = {}
        # Create each track widget and add it to the layout
        for i, track in enumerate(midi_file.tracks):
            hlayout = QHBoxLayout()

            # Add QLabel for track number and channel
            label = QLabel(f"Track {i+1} Channel:")
            label.setFixedWidth(100)
            hlayout.addWidget(label)
            # Add QSpinBox for selecting the MIDI channel
            spin = MidiSpinBox()
            spin.setValue(get_first_channel(track) + MidiConstant.CHANNEL_BINARY_TO_DISPLAY)  # Offset for display
            spin.setFixedWidth(30)
            hlayout.addWidget(spin)

            # Add QPushButton for applying the changes
            apply_button = QPushButton("Apply")
            apply_button.setFixedWidth(30)
            apply_button.clicked.connect(self.make_apply_slot(i, spin))
            hlayout.addWidget(apply_button)

            mute_button = QPushButton("Mute")
            mute_button.setFixedWidth(30)
            mute_button.setCheckable(True)
            mute_button.clicked.connect(lambda _, tr=i: self.mute_track(tr))  # Send internal value (0–15)
            mute_button.toggled.connect(
                lambda checked, tr=i: self.toggle_track_mute(tr, checked)
            )
            # hlayout.addWidget(mute_button)

            mute_button = QPushButton("Delete")
            mute_button.setFixedWidth(30)
            mute_button.setCheckable(True)
            mute_button.clicked.connect(lambda _, tr=i: self.delete_track(tr))  # Send internal value (0–15)
            hlayout.addWidget(mute_button)

            # Add the MidiTrackWidget for the specific track
            self.midi_track_widgets[i] = MidiTrackWidget(track=track, track_number=i, total_length=midi_file.length)  # Initialize the dictionary
            hlayout.addWidget(self.midi_track_widgets[i])
            self.setStyleSheet("QLabel { width: 100px; }")  # Set background color for the layout
            self.channel_controls_layout.addLayout(hlayout)
            self.channel_controls_layout.addStretch()

    def refresh_track_list(self):
        """
        refresh_track_list

        :return:
        """
        self.update()

