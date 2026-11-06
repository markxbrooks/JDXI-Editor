"""
Midi Track Widget
"""

from typing import Callable, Optional

import mido
from decologr import Decologr as log
from PySide6.QtCore import QRect, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPaintEvent, QPen, QPixmap

from jdxi_editor.ui.common import JDXi, QWidget
from jdxi_editor.ui.widgets.midi.colors import MIDI_CHANNEL_COLORS
from jdxi_editor.ui.widgets.midi.utils import (
    generate_track_colors,
    get_first_channel,
    ticks_to_seconds,
)
from picomidi.constant import Midi
from picomidi.message.type import MidoMessageType


class MidiTrackWidget(QWidget):
    """
    MidiTrackWidget
    """

    def __init__(
        self,
        track: mido.MidiTrack,
        track_number: int,
        total_length: float,
        ticks_per_beat: int | None = None,
        parent: QWidget = None,
        tick_to_seconds: Optional[Callable[[int], float]] = None,
    ):
        """
        Initialize the MidiTrackWidget.

        :param track: mido.MidiTrack the mido track data
        :param track_number: int The track number
        :param total_length: float The total length of the longest of the tracks in seconds
        :param ticks_per_beat: MIDI file ticks per beat
        :param parent: QWidget Parent widget
        :param tick_to_seconds: File-wide tick → seconds converter; without it
            only this track's own tempo events are used
        """
        super().__init__(parent)
        self.midi_file = None
        self.track = track
        self.track_number = track_number
        self.ticks_per_beat = ticks_per_beat or Midi.timing.TICKS_PER_BEAT
        self.color = generate_track_colors(track_number)
        self.muted = False
        self.total_length = total_length
        self.setMinimumHeight(JDXi.UI.MidiPlayer.TRACK_HEIGHT)
        self.track_data = None  # Dict: notes, label, channels, pitch_range
        self.muted_channels = set()  # Set of muted channels
        self.muted_tracks = set()  # Set of muted channels
        self.cached_pixmap = None
        self.cached_width = 0
        self.tick_to_seconds = tick_to_seconds
        self.playhead_norm: Optional[float] = None  # 0..1, None hides it
        self.selected = False  # Brighter note fill / outline when selected

        if track:
            self.set_track(track, total_length, self.ticks_per_beat)

    def set_selected(self, selected: bool) -> None:
        """Highlight this track's notes as selected."""
        if self.selected == selected:
            return
        self.selected = selected
        self.cached_pixmap = None
        self.update()

    def set_track(
        self,
        track: mido.MidiTrack,
        total_length: float,
        ticks_per_beat: int | None = None,
    ) -> None:
        """
        set_track

        :param track: mido.MidiTrack
        :param total_length: float total file length in seconds
        :param ticks_per_beat: MIDI file ticks per beat
        :return: None
        """
        if ticks_per_beat is None:
            ticks_per_beat = self.ticks_per_beat
        self.ticks_per_beat = ticks_per_beat
        self.track = track
        self.track_data = None
        if not track:
            return

        notes = []  # (start, end) as fractions of the file length, pitch, velocity
        channels = set()
        program_changes = []
        sounding: dict[tuple[int, int], list[tuple[float, int]]] = {}

        first_channel = get_first_channel(track)
        if first_channel is None:
            first_channel = 0

        def norm(seconds: float) -> float:
            return seconds / total_length if total_length else 0.0

        tempo = Midi.tempo.BPM_120_USEC
        abs_seconds = 0.0
        abs_tick = 0
        for msg in track:
            abs_tick += msg.time
            if self.tick_to_seconds is not None:
                abs_seconds = self.tick_to_seconds(abs_tick)
            else:
                abs_seconds += ticks_to_seconds(msg.time, tempo, ticks_per_beat)
            if msg.type == MidoMessageType.SET_TEMPO.value:
                tempo = msg.tempo
            if hasattr(msg, "channel"):
                channels.add(msg.channel)
            if msg.type == MidoMessageType.NOTE_ON.value and msg.velocity > 0:
                sounding.setdefault((msg.channel, msg.note), []).append(
                    (norm(abs_seconds), msg.velocity)
                )
            elif msg.type in (
                MidoMessageType.NOTE_OFF.value,
                MidoMessageType.NOTE_ON.value,
            ):
                started = sounding.get((msg.channel, msg.note))
                if started:
                    begin, velocity = started.pop(0)
                    notes.append((begin, norm(abs_seconds), msg.note, velocity))
            if msg.type == MidoMessageType.PROGRAM_CHANGE.value:
                program_changes.append(msg.program)
        # Notes never released last to the end of the track
        for (_, note), started in sounding.items():
            for begin, velocity in started:
                notes.append((begin, norm(abs_seconds), note, velocity))
        notes.sort()

        name = track.name.strip() if track.name else "Unnamed"
        label = f"{name} | Notes: {len(notes)}"
        if channels:
            label += f" | Channel: {first_channel + 1}"  # Display 1-based channel
        if program_changes:
            label += f" | Prog: {', '.join(map(str, program_changes))}"
        self.setToolTip(label)

        pitches = [pitch for _, _, pitch, _ in notes]
        self.track_data = {
            "notes": notes,
            "label": label,
            "channels": {first_channel},
            "pitch_range": (min(pitches), max(pitches)) if pitches else None,
        }
        self.cached_pixmap = None
        self.cached_width = 0
        self.update()

    def update_muted_tracks(self, muted_tracks: set[int]) -> None:
        """
        Called when the global mute state is updated.
        """
        self.muted_tracks = muted_tracks
        self.cached_pixmap = None  # mute state is drawn into the pixmap
        self.update()

    def _is_channel_muted(self, channel: int) -> bool:
        """*channel* is 0-15; muted_channels holds 1-16 as the mute buttons show."""
        return channel + Midi.channel.BINARY_TO_DISPLAY in self.muted_channels

    def update_muted_channels(self, muted_channels: set[int]) -> None:
        """
        Called when the global mute state is updated.
        """
        self.muted_channels = muted_channels
        self.cached_pixmap = None  # mute state is drawn into the pixmap
        self.update()

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
        x = self._playhead_x()
        if x is not None:
            # Playhead is the primary red signal on the timeline
            pen = QPen(QColor(JDXi.UI.MidiPlayer.ACCENT))
            pen.setWidth(3)
            painter.setPen(pen)
            painter.drawLine(x, 0, x, self.height())
        painter.end()

    def _playhead_x(self) -> Optional[int]:
        if self.playhead_norm is None:
            return None
        return int(self.playhead_norm * self.width())

    def set_playhead(self, norm: Optional[float]) -> None:
        """
        Show the playback position as a line.

        :param norm: Position as a fraction (0..1) of the file length; None hides it
        """
        old_x = self._playhead_x()
        self.playhead_norm = None if norm is None else max(0.0, min(1.0, norm))
        new_x = self._playhead_x()
        if old_x == new_x:
            return
        # Repaint only the columns the line leaves and enters
        for x in (old_x, new_x):
            if x is not None:
                self.update(QRect(x - 2, 0, 5, self.height()))

    # Smallest pitch span drawn (an octave), so a few notes are not stretched
    # over the whole lane height
    MIN_PITCH_SPAN = 12
    LANE_PADDING = 3

    def render_track_to_pixmap(self) -> QPixmap:
        """
        Draw the lane: a miniature piano roll in the track's channel colour.

        Each note is a bar from its start to its end, placed by pitch; a faint
        band in the same colour covers the stretch from the first note to the
        last. Tracks without notes (tempo, markers) are left empty.

        :return: QPixmap
        """
        width = self.width()
        height = self.height()
        pixmap = QPixmap(width, height)
        pixmap.fill(QColor(JDXi.UI.MidiPlayer.BACKGROUND))

        painter = QPainter(pixmap)
        painter.setPen(QPen(QColor(JDXi.UI.MidiPlayer.SURFACE_ALT)))
        painter.drawLine(0, height - 1, width, height - 1)  # row separator

        notes = self.track_data["notes"]
        channels = self.track_data["channels"]
        if not notes:
            painter.end()
            return pixmap
        muted = self.muted or any(
            self._is_channel_muted(channel) for channel in channels
        )
        channel = next(iter(channels))
        # Copy: the colour table is shared by every track
        base = QColor(MIDI_CHANNEL_COLORS.get(channel, QColor(100, 100, 255, 150)))

        band = QColor(base)
        band.setAlpha(18 if muted else 40)
        band_left = notes[0][0] * width
        band_right = max(end for _, end, _, _ in notes) * width
        band_rect = QRectF(band_left, 1, max(2.0, band_right - band_left), height - 3)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(band)
        painter.drawRoundedRect(band_rect, 3, 3)
        if self.selected:
            painter.setPen(QPen(QColor(JDXi.UI.MidiPlayer.TEXT), 1))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(band_rect, 3, 3)

        low, high = self.track_data["pitch_range"]
        span = max(high - low, self.MIN_PITCH_SPAN)
        low -= (span - (high - low)) / 2  # centre narrow ranges
        usable = height - 2 * self.LANE_PADDING
        note_height = max(2.0, min(4.0, usable / (span + 1)))

        painter.setPen(Qt.PenStyle.NoPen)
        for start, end, pitch, velocity in notes:
            x = start * width
            w = max(1.5, (end - start) * width)
            if x > width or x + w < 0:
                continue  # off screen
            y = self.LANE_PADDING + (1 - (pitch - low) / span) * (usable - note_height)
            color = QColor(base)
            if muted:
                color.setAlpha(60)
            else:
                # Louder notes are more opaque
                color.setAlpha(min(255, 110 + velocity))
                if self.selected:
                    color = color.lighter(130)
            painter.setBrush(color)
            painter.drawRect(QRectF(x, y, w, note_height))

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
                MidoMessageType.NOTE_ON.value,
                MidoMessageType.NOTE_OFF.value,
                MidoMessageType.CONTROL_CHANGE.value,
                MidoMessageType.PROGRAM_CHANGE.value,
                MidoMessageType.PITCH_WHEEL,
                MidoMessageType.AFTERTOUCH,
                MidoMessageType.POLYTOUCH,
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
