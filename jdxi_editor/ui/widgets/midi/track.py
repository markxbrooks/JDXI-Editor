import mido
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QScrollArea,
    QSlider,
    QLabel,
    QHBoxLayout,
    QPushButton, QSpinBox,
)
from PySide6.QtGui import QPainter, QColor, QPen, QPaintEvent
from PySide6.QtCore import Qt, QRectF

from jdxi_editor.jdxi.midi.constant import MidiConstant
from jdxi_editor.log.logger import Logger as log

RAINBOW_COLORS = [
    QColor(255, 0, 0, 150),  # Pure Red
    QColor(0, 255, 0, 150),  # Pure Green
    QColor(0, 0, 255, 150),  # Pure Blue
    QColor(255, 255, 0, 150),  # Yellow
    QColor(255, 0, 255, 150),  # Magenta
    QColor(0, 255, 255, 150),  # Cyan
    QColor(255, 255, 255, 150),  # White
]

# Create a channel-to-color mapping
CHANNEL_COLORS_OLD = {
    0: QColor(255, 0, 0, 150),  # Red - Channel 1
    1: QColor(255, 127, 0, 150),  # Orange - Channel 2
    2: QColor(255, 255, 0, 150),  # Yellow - Channel 3
    3: QColor(0, 255, 0, 150),  # Green - Channel 4
    4: QColor(0, 0, 255, 150),  # Blue - Channel 5
    5: QColor(75, 0, 130, 150),  # Indigo - Channel 6
    6: QColor(148, 0, 211, 150),  # Violet - Channel 7
    7: QColor(255, 192, 203, 150),  # Pink - Channel 8
    8: QColor(255, 165, 0, 150),  # Orange-Red - Channel 9
    9: QColor(128, 0, 128, 150),  # Purple - Channel 10 (Drums)
    10: QColor(0, 255, 255, 150),  # Cyan - Channel 11
    11: QColor(255, 215, 0, 150),  # Gold - Channel 12
    12: QColor(192, 192, 192, 150),  # Silver - Channel 13
    13: QColor(0, 128, 0, 150),  # Dark Green - Channel 14
    14: QColor(128, 0, 0, 150),  # Maroon - Channel 15
    15: QColor(0, 128, 128, 150),  # Teal - Channel 16
}

CHANNEL_COLORS = {
    0: QColor(255, 0, 0, 120),    # Red
    1: QColor(255, 128, 0, 120),  # Orange
    2: QColor(255, 255, 0, 120),  # Yellow
    3: QColor(0, 255, 0, 120),    # Green
    4: QColor(0, 255, 255, 120),  # Cyan
    5: QColor(0, 128, 255, 120),  # Sky Blue
    6: QColor(0, 0, 255, 120),    # Blue
    7: QColor(128, 0, 255, 120),  # Purple
    8: QColor(255, 0, 255, 120),  # Magenta
    9: QColor(160, 32, 240, 120), # Deep Purple
    10: QColor(128, 128, 128, 120), # Gray
    11: QColor(0, 100, 0, 120),   # Dark Green
    12: QColor(139, 69, 19, 120), # Brown
    13: QColor(255, 20, 147, 120),# Pink
    14: QColor(70, 130, 180, 120),# Steel Blue
    15: QColor(210, 105, 30, 120) # Chocolate
}


def extract_notes_with_absolute_time(
    track: mido.MidiTrack, tempo: int, ticks_per_beat: int
) -> list:
    """Extract notes with absolute time from a MIDI track.

    :param track: mido.MidiTrack
    :param tempo: int
    :param ticks_per_beat: int
    """
    notes = []
    current_time = 0
    for msg in track:
        current_time += msg.time
        if msg.type == "note_on":
            abs_time = mido.tick2second(current_time, ticks_per_beat, tempo)
            notes.append((abs_time, msg))
    return notes


class MidiSpinBox(QSpinBox):
    """
    Custom QSpinBox to display MIDI channels as 1-16,
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(1, 16)  # Display range is 1–16

    def valueFromText(self, text: str) -> int:
        # Convert displayed value (1–16) to internal value (0–15)
        return int(text)

    def textFromValue(self, value: int) -> str:
        # Convert internal value (0–15) to displayed value (1–16)
        return str(value)


class TimeRulerWidget(QWidget):
    def __init__(self, midi_file: mido.MidiFile = None, parent: QWidget = None):
        super().__init__(parent)
        self.midi_file = midi_file
        self.setMinimumHeight(20)

    def set_midi_file(self, midi_file: mido.MidiFile) -> None:
        self.midi_file = midi_file
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        if not self.midi_file:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        duration = self.midi_file.length
        width = self.width()
        height = self.height()

        num_marks = int(duration) + 1
        spacing = width / duration if duration else width

        font = painter.font()
        font.setPointSize(8)
        painter.setFont(font)
        painter.setPen(QPen(Qt.white))

        for second in range(num_marks):
            if second % 10 == 0:
                # Draw major ticks every 10 seconds
                x = int(second * spacing)
                painter.drawLine(x, 0, x, height)
                painter.drawText(x + 2, height - 4, f"{second}s")


class MidiTrackWidget(QWidget):
    def __init__(self, track: mido.MidiTrack, total_length: float, parent: QWidget = None):
        super().__init__(parent)
        self.note_width = 400
        self.track = track
        self.muted = False
        self.total_length = total_length
        self.setMinimumHeight(50)  # Adjust as needed
        self.track_data = None  # Dict: {rects: [...], label: str, channels: set}
        self.muted_channels = set()  # Set of muted channels

        if track:
            self.set_track(track, total_length)

    def set_track(self, track: mido.MidiTrack, total_length: float) -> None:
        """
        Set the MIDI track and extract relevant data.
        :param track: mido.MidiTrack Track to be displayed
        :param total_length: float track length in seconds
        :return: None
        """
        self.track = track
        self.track_data = None

        if not track:
            return

        abs_time = 0
        rects = []
        channels = set()
        note_count = 0
        program_changes = []

        for msg in track:
            abs_time += msg.time
            if hasattr(msg, "channel"):
                channels.add(msg.channel)
            if msg.type == "note_on" and msg.velocity > 0:
                note_count += 1
                norm_time = abs_time / total_length if total_length else 0
                # Store both time and channel for each note
                rects.append(
                    (norm_time, msg.channel if hasattr(msg, "channel") else 0)
                )
            if msg.type == "program_change":
                program_changes.append(msg.program)

        label = f"Track | {track.name if track.name else 'Unnamed'} | Notes: {note_count}"
        if channels:
            channel = get_first_channel(track)
            label += f" | Channel: {channel + 1}"  # Display as 1-16
        if program_changes:
            label += f" | Prog: {', '.join(map(str, program_changes))}"

        self.track_data = {"rects": rects, "label": label, "channels": channels}
        self.update()
        log.message(f"rects: {rects}")

    def paintEvent(self, event: QPaintEvent) -> None:
        if not self.track_data:
            return

        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.Antialiasing)

            # Clear background
            painter.fillRect(self.rect(), self.palette().window())

            track_height = self.height()
            widget_width = self.width()

            font = painter.font()
            font.setPointSize(8)
            painter.setFont(font)

            data = self.track_data
            y = 0
            rects = data["rects"]
            label = data["label"]
            channels = data["channels"]
            muted = any(channel in self.muted_channels for channel in channels)

            # Draw background for note range
            if rects:
                try:
                    times = [t[0] for t in rects]
                    start_x = min(times) * widget_width
                    end_x = max(times) * widget_width
                    if end_x - start_x < self.note_width:
                        end_x = start_x + self.note_width
                    track_rect = QRectF(start_x, y, end_x - start_x, int(track_height))
                    channel = get_first_channel(self.track)
                    bg_color = CHANNEL_COLORS.get(int(channel), QColor(100, 100, 255, 150))
                    if muted:
                        bg_color.setAlpha(50)
                    painter.setBrush(bg_color)
                    painter.drawRect(track_rect)
                except Exception as e:
                    log.error(f"Error drawing track background: {e}")

            # Draw notes
            for norm_time, channel in rects:
                x = norm_time * widget_width
                height = track_height
                color = CHANNEL_COLORS.get(channel, QColor(100, 100, 255, 150))
                if channel in self.muted_channels:
                    color.setAlpha(100)
                painter.setBrush(color)
                painter.drawRect(QRectF(x, y, self.note_width, height))

            # Draw label
            painter.setPen(QColor(200, 200, 200))
            painter.drawText(5, int(y + 15), label)

        finally:
            painter.end()

    def paintEventOld(self, event: QPaintEvent) -> None:
        """
        Paint the MIDI track widget.
        :param event: QPaintEvent
        :return: None
        """
        if not self.track_data:
            return

        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.Antialiasing)
            track_height = self.height()
            widget_width = self.width()

            font = painter.font()
            font.setPointSize(8)
            painter.setFont(font)

            data = self.track_data
            y = 0  # Single track, no need for different y positions
            rects = data["rects"]
            label = data["label"]
            channels = data["channels"]

            # Check if this track is muted
            muted = any(channel in self.muted_channels for channel in channels)

            # Draw background from start to end of track notes
            if rects:
                try:
                    times = [t[0] for t in rects]
                    start_x = min(times) * widget_width
                    end_x = max(times) * widget_width
                    track_rect = QRectF(start_x, y, end_x - start_x, int(track_height))
                    channel = get_first_channel(self.track)
                    # channel = self.track[0].channel_prefix if hasattr(self.track[0], "channel_prefix") else 0
                    log.message(f"Track 'self.track' first channel: '{channel}'")
                    bg_color = CHANNEL_COLORS.get(int(channel), QColor(100, 100, 255, 150))
                    log.message(f"bg_color '{bg_color}'")
                    if muted:
                        bg_color.setAlpha(50)
                    painter.setBrush(bg_color)
                    painter.drawRect(track_rect)
                except Exception as e:
                    log.error(f"Error drawing track background: {e}")
            # Draw notes
            for norm_time, channel in rects:
                x = norm_time * widget_width
                height = track_height
                color = CHANNEL_COLORS.get(channel, QColor(100, 100, 255, 150))
                if channel in self.muted_channels:
                    color.setAlpha(100)
                painter.setBrush(color)
                painter.drawRect(QRectF(x, y, self.note_width, height))
            # Draw label
            painter.setPen(QColor(200, 200, 200))
            painter.drawText(5, int(y + 15), label)

        finally:
            painter.end()

    def change_track_channel(self, track_index: int, new_channel: int) -> None:
        if not (0 <= new_channel <= 15):
            raise ValueError("MIDI channel must be between 0 and 15")
        if not (0 <= track_index < len(self.midi_file.tracks)):
            raise IndexError("Invalid track index")

        track = self.midi_file.tracks[track_index]
        for msg in track:
            if msg.type in [
                "note_on", "note_off", "control_change", "program_change",
                "pitchwheel", "aftertouch", "polytouch"
            ]:
                msg.channel = new_channel

        # Force reset by creating a new MidiFile with modified tracks
        new_midi = mido.MidiFile()
        new_midi.ticks_per_beat = self.midi_file.ticks_per_beat
        for t in self.midi_file.tracks:
            new_midi.tracks.append(mido.MidiTrack(t))  # Shallow copy is okay here

        self.set_midi_file(new_midi)


def get_first_channel(track) -> int:
    """
    Get the first channel from a MIDI track.
    :param track: mido.MidiTrack
    :return: int
    """
    for msg in track:
        if msg.type in {"note_on", "note_off", "control_change", "program_change"} and hasattr(msg, "channel"):
            return msg.channel
    return 0  # default fallback


class MidiTrackViewer(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.midi_file = None
        self.event_index = None
        self.ruler = TimeRulerWidget()
        self.midi_track_widgets = {}  # MidiTrackWidget()
        self.muted_tracks = set()  # To track muted tracks

        # To track muted channels
        self.muted_channels = set()

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
        # scroll_layout.addWidget(self.tracks)

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

    def update_track_zoom(self, width):
        self.scroll_content.setFixedWidth(width * 80)

    #def set_midi_file(self, midi_file):
    #    self.ruler.set_midi_file(midi_file)
    #    self.tracks.set_midi_file(midi_file)

    def toggle_channel_mute(self, channel, is_muted):
        """Add or remove the channel from muted set."""
        log.message(
            f"Toggling mute for channel {channel}: {'Muted' if is_muted else 'Unmuted'}"
        )
        if is_muted:
            self.muted_channels.add(channel)
            # self.tracks.toggle_channel_mute(channel, True)
        else:
            self.muted_channels.discard(channel)

    def toggle_track_mute(self, track, is_muted):
        """Add or remove the channel from muted set."""
        log.message(
            f"Toggling mute for track {track}: {'Muted' if is_muted else 'Unmuted'}"
        )
        if is_muted:
            self.muted_channels.add(track)
            # self.tracks.toggle_channel_mute(channel, True)
        else:
            self.muted_channels.discard(track)

        self.event_index += 1
        
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
            spin.setFixedWidth(50)
            hlayout.addWidget(spin)
        
            # Add QPushButton for applying the changes
            apply_button = QPushButton("Apply")
            apply_button.setFixedWidth(50)
            apply_button.clicked.connect(self.make_apply_slot(i, spin))
            # apply_button.clicked.connect(lambda _, tr=i, sp=spin: self.change_track_channel(tr, sp.value() -  MidiConstant.CHANNEL_DISPLAY_TO_BINARY))  # Send internal value (0–15)
            hlayout.addWidget(apply_button)

            mute_button = QPushButton("Mute")
            mute_button.setFixedWidth(50)
            mute_button.setCheckable(True)
            mute_button.clicked.connect(lambda _, tr=i: self.mute_track(tr))  # Send internal value (0–15)
            mute_button.toggled.connect(
                lambda checked, tr=i: self.toggle_track_mute(tr, checked)
            )
            hlayout.addWidget(mute_button)

            # Add the MidiTrackWidget for the specific track
            self.midi_track_widgets[i] = MidiTrackWidget(track=track, total_length=midi_file.length)  # Initialize the dictionary
            hlayout.addWidget(self.midi_track_widgets[i])
            self.setStyleSheet("QLabel { width: 100px; }")  # Set background color for the layout
            self.channel_controls_layout.addLayout(hlayout)
