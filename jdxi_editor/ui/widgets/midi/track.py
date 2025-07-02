"""
Midi Track Widget
"""

import mido
from PySide6.QtWidgets import (
    QWidget,
)
from PySide6.QtGui import QPainter, QColor, QPaintEvent, QPixmap
from PySide6.QtCore import QRectF

from jdxi_editor.jdxi.style import JDXiStyle
from jdxi_editor.log.logger import Logger as log
from jdxi_editor.ui.widgets.midi.colors import MIDI_CHANNEL_COLORS
from jdxi_editor.ui.widgets.midi.utils import generate_track_colors, get_first_channel


class MidiTrackWidget(QWidget):
    """
    MidiTrackWidget
    """
    def __init__(self,
                 track: mido.MidiTrack,
                 track_number: int,
                 total_length: float,
                 parent: QWidget = None):
        """
        Initialize the MidiTrackWidget.

        :param track: mido.MidiTrack the mido track data
        :param track_number: int The track number
        :param total_length: float The total length of the longest of the tracks in seconds
        :param parent: QWidget Parent widget
        """
        super().__init__(parent)
        self.midi_file = None
        self.note_width = 400
        self.track = track
        self.track_number = track_number
        self.color = generate_track_colors(track_number)
        self.muted = False
        self.total_length = total_length
        self.setMinimumHeight(JDXiStyle.TRACK_HEIGHT_MINIMUM)  # Adjust as needed
        self.track_data = None  # Dict: {rects: [...], label: str, channels: set}
        self.muted_channels = set()  # Set of muted channels
        self.muted_tracks = set()  # Set of muted channels
        self.cached_pixmap = None
        self.cached_width = 0

        if track:
            self.set_track(track, total_length)

    def set_track(self, track: mido.MidiTrack, total_length: float) -> None:
        """
        set_track

        :param track: mido.MidiTrack
        :param total_length: float
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

        # Find the first channel in the track
        first_channel = None
        for msg in track:
            if hasattr(msg, "channel"):
                first_channel = msg.channel
                break
        if first_channel is None:
            first_channel = 0  # fallback if no channel found

        for msg in track:
            abs_time += msg.time
            if hasattr(msg, "channel"):
                channels.add(msg.channel)
            if msg.type == "note_on" and msg.velocity > 0:
                note_count += 1
                norm_time = abs_time / total_length if total_length else 0
                # Use first_channel for all notes
                rects.append(
                    (norm_time, first_channel)
                )
            if msg.type == "program_change":
                program_changes.append(msg.program)

        label = f"Track | {track.name if track.name else 'Unnamed'} | Notes: {note_count}"
        if channels:
            label += f" | Channel: {first_channel + 1}"  # Display 1-based channel
        if program_changes:
            label += f" | Prog: {', '.join(map(str, program_changes))}"

        self.track_data = {"rects": rects, "label": label, "channels": {first_channel}}
        self.cached_pixmap = None
        self.cached_width = 0
        self.update()
        # log.message(f"rects: {rects}")

    def update_muted_tracks(self, muted_tracks: set[int]) -> None:
        """
        Called when the global mute state is updated.
        """
        self.muted_tracks = muted_tracks
        self.update()  # trigger repaint or UI change if needed

    def update_muted_channels(self, muted_channels: set[int]) -> None:
        """
        Called when the global mute state is updated.
        """
        self.muted_channels = muted_channels
        self.update()  # trigger repaint or UI change if needed

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        paintEvent with caching and optimization
        """
        if not self.track_data:
            return

        if self.cached_pixmap is None or self.cached_width != self.width():
            self.cached_pixmap = self.render_track_to_pixmap()
            self.cached_width = self.width()

        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.cached_pixmap)
        painter.end()

    def paintEventOld(self, event: QPaintEvent) -> None:
        """
        paintEvent

        :param event: QPaintEvent
        :return: None
        """
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
                    max_time = max(times)  # Use the last time in the list
                    scale = widget_width / max_time
                    start_x = min(times) * scale
                    end_x = max(times) * scale
                    # Adjust the end_x to ensure it doesn't go beyond the widget width
                    if end_x - start_x < self.note_width:
                        end_x = start_x + self.note_width
                    track_rect = QRectF(start_x, y, end_x - start_x, int(track_height))
                    channel = get_first_channel(self.track)
                    bg_color = generate_track_colors(16)[int(self.track_number) % 16]
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
                color = MIDI_CHANNEL_COLORS.get(channel, QColor(100, 100, 255, 150))
                if channel in self.muted_channels:
                    color.setAlpha(100)
                painter.setBrush(color)
                painter.drawRect(QRectF(x, y, self.note_width, height))

            # Draw label
            painter.setPen(QColor(200, 200, 200))
            painter.drawText(5, int(y + 15), label)

        finally:
            painter.end()

    def render_track_to_pixmap(self) -> QPixmap:
        """
        render_track_to_pixmap

        :return: QPixmap
        """
        width = self.width()
        height = self.height()
        pixmap = QPixmap(width, height)
        pixmap.fill(self.palette().window().color())

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        font = painter.font()
        font.setPointSize(8)
        painter.setFont(font)

        y = 0
        rects = self.track_data["rects"]
        label = self.track_data["label"]
        channels = self.track_data["channels"]
        muted = any(channel in self.muted_channels for channel in channels)

        # Compute scale based on last timestamp
        times = [t[0] for t in rects]
        if not times:
            return pixmap

        max_time = max(times)
        scale = width / max_time if max_time else 1.0

        # Background track bar
        start_x = min(times) * scale
        end_x = max(times) * scale
        if end_x - start_x < self.note_width:
            end_x = start_x + self.note_width
        track_rect = QRectF(start_x, y, end_x - start_x, height)

        channel = get_first_channel(self.track)
        bg_color = generate_track_colors(16)[int(self.track_number) % 16]
        if muted:
            bg_color.setAlpha(50)
        painter.setBrush(bg_color)
        painter.drawRect(track_rect)

        # Notes
        for norm_time, channel in rects:
            x = norm_time * scale
            if x + self.note_width < 0 or x > width:
                continue  # Skip offscreen
            color = MIDI_CHANNEL_COLORS.get(channel, QColor(100, 100, 255, 150))
            if channel in self.muted_channels:
                color.setAlpha(100)
            painter.setBrush(color)
            painter.drawRect(QRectF(x, y, self.note_width, height))

        # Label
        painter.setPen(QColor(200, 200, 200))
        painter.drawText(5, int(y + 15), label)

        painter.end()
        return pixmap

    def change_track_channel(self, track_index: int, new_channel: int) -> None:
        """
        change_track_channel

        :param track_index: int
        :param new_channel: int
        :return: None
        """
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

    def set_midi_file(self, new_midi: mido.MidiFile):
        """
        set_midi_file
        
        :param new_midi: mido.MidiFile
        :return: None
        """
        self.midi_file = new_midi
