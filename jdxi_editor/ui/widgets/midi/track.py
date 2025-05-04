
import mido
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QScrollArea,
    QSlider,
    QLabel,
    QHBoxLayout,
    QPushButton,
)
from PySide6.QtGui import QPainter, QColor, QPen, QPaintEvent
from PySide6.QtCore import Qt, QRectF

from jdxi_editor.log.message import log_message

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
CHANNEL_COLORS = {
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
    def __init__(self, midi_file: mido.MidiFile = None, parent: QWidget = None):
        super().__init__(parent)
        self.midi_file = None
        self.setMinimumHeight(400)
        self.track_data = []  # List of dicts: {rects: [...], label: str}
        if midi_file:
            self.set_midi_file(midi_file)
        self.muted_channels = set()  # Set of muted channels

    def set_midi_file(self, midi_file: mido.MidiFile) -> None:
        self.midi_file = midi_file
        self.track_data = []

        if not midi_file:
            return

        total_length = midi_file.length

        for i, track in enumerate(midi_file.tracks):
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

            label = f"Track {i+1} | {track.name} | Notes: {note_count}"
            if channels:
                label += f" | Channel(s): {', '.join(map(str, sorted(channels)))}"
            if program_changes:
                label += f" | Prog: {', '.join(map(str, program_changes))}"

            self.track_data.append(
                {"rects": rects, "label": label, "channels": channels}
            )

        self.update()

        json_safe_data = []
        for track in self.track_data:
            json_safe_data.append(
                {
                    "rects": track["rects"],
                    "label": track["label"],
                    "channels": list(
                        track["channels"]
                    ),  # sets aren't JSON serializable
                }
            )

        # with open("midi_track_data.json", "w") as f:
        #    json.dump(json_safe_data, f, indent=2)

    def toggle_channel_mute(self, channel: int, is_muted: bool) -> None:
        """Toggle the mute state for a channel.

        :param channel: int
        :param is_muted: bool
        """
        log_message(
            f"Track Widget Toggling mute for channel {channel}: {'Muted' if is_muted else 'Un-muted'}"
        )
        if is_muted:
            self.muted_channels.add(channel)
        else:
            self.muted_channels.discard(channel)

    def paintEventNew(self, event: QPaintEvent) -> None:
        if not self.track_data or not self.midi_file:
            return

        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.Antialiasing)

            track_height = 30  # Fixed track height as you requested
            widget_width = self.width()

            font = painter.font()
            font.setPointSize(8)
            painter.setFont(font)

            for i, data in enumerate(
                self.track_data[:1]
            ):  # Show only the first track for debugging
                spacing = int(track_height / 5)
                y = i * (track_height + spacing)
                rects = data["rects"]
                label = data["label"]
                channels = data["channels"]

                # Check if this track is muted
                muted = any(channel in self.muted_channels for channel in channels)

                # Draw background from start to end of track notes
                if rects:
                    times = [t[0] for t in rects]
                    start_x = min(times) * widget_width
                    end_x = max(times) * widget_width
                    track_rect = QRectF(start_x, y, end_x - start_x, int(track_height))
                    painter.setBrush(
                        QColor(50, 50, 50, 100) if muted else QColor(255, 255, 255, 50)
                    )  # Subtle background
                    painter.setPen(Qt.NoPen)
                    painter.drawRect(track_rect)

                # Draw notes
                painter.setPen(Qt.NoPen)
                for norm_time, channel in rects:
                    color = (
                        QColor(150, 150, 150) if muted else QColor(100, 100, 255, 150)
                    )  # Grey out muted tracks
                    painter.setBrush(color)
                    x = norm_time * widget_width
                    rect = QRectF(x, y, 4, int(track_height))
                    painter.drawRect(rect)

                # Draw label
                painter.setPen(QColor(200, 200, 200))
                painter.drawText(5, int(y + 15), label)
        finally:
            painter.end()

    def paintEvent(self, event: QPaintEvent) -> None:
        """Paint the MIDI track widget.

        :param event: QPaintEvent
        """
        if not self.track_data or not self.midi_file:
            return
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.Antialiasing)
            number_of_tracks = len(self.track_data)
            track_height = self.height() / number_of_tracks

            widget_width = self.width()

            font = painter.font()
            font.setPointSize(8)
            painter.setFont(font)

            for i, data in enumerate(self.track_data):
                y = i * track_height
                rects = data["rects"]
                label = data["label"]

                # Draw notes
                painter.setPen(Qt.NoPen)
                painter.setBrush(QColor(100, 100, 255, 150))
                for norm_time, channel in rects:
                    color = CHANNEL_COLORS.get(channel, QColor(100, 100, 255, 150))
                    # If the channel is muted, draw it in a different color
                    if channel in self.muted_channels:
                        color = QColor(150, 150, 150, 150)
                    # log_message(f"Drawing color {color} for channel {channel}")
                    painter.setBrush(color)
                    x = norm_time * widget_width
                    rect = QRectF(x, y, 4, int(track_height))
                    painter.drawRect(rect)

                # Draw label
                painter.setPen(QColor(200, 200, 200))
                painter.drawText(5, int(y + 15), label)
                # Draw grid lines
                painter.setPen(QPen(QColor(200, 200, 200), 1))
                painter.drawLine(0, y, widget_width, y)

            # Draw border
            painter.setPen(QPen(Qt.white, 1))
            painter.drawRect(self.rect().adjusted(0, 0, -1, -1))
        finally:
            painter.end()


class MidiTrackViewer(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.event_index = None
        self.ruler = TimeRulerWidget()
        self.tracks = MidiTrackWidget()

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
        scroll_layout.addWidget(self.tracks)

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

    def set_midi_file(self, midi_file):
        self.ruler.set_midi_file(midi_file)
        self.tracks.set_midi_file(midi_file)

    def toggle_channel_mute(self, channel, is_muted):
        """Add or remove the channel from muted set."""
        log_message(
            f"Toggling mute for channel {channel}: {'Muted' if is_muted else 'Unmuted'}"
        )
        if is_muted:
            self.muted_channels.add(channel)
            self.tracks.toggle_channel_mute(channel, True)
        else:
            self.muted_channels.discard(channel)

    def play_next_event(self):
        """Override or add the logic to handle muted channels."""
        if self.event_index >= len(self.midi_events):
            return

        tick, msg = self.midi_events[self.event_index]

        if hasattr(msg, "channel") and (msg.channel + 1) in self.muted_channels:
            return  # Skip muted channel
        else:
            self.send_midi_message(msg)  # Your MIDI playback logic

        self.event_index += 1
