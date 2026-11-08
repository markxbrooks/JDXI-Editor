"""
Playlist progress

Where playback is in a playlist: an LCD with the song number and name, the
song's own progress (elapsed, length and time left), a bar with a segment per
song (played, playing, still to come; click one to play it) and the next song.
"""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QEvent, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QLinearGradient, QMouseEvent, QPainter, QPen
from PySide6.QtWidgets import QLabel, QProgressBar, QToolTip, QWidget

from jdxi_editor.ui.common import JDXi, QVBoxLayout
from jdxi_editor.ui.editors.midi_player.utils import format_time
from jdxi_editor.ui.widgets.digital.title import DigitalTitle

SEGMENT_GAP = 3  # px between songs
SEGMENT_HEIGHT = 14
PLAYED_TOP = QColor("#ff1a1a")  # the red of JDXi.UI.Style.PROGRESS_BAR
PLAYED_BOTTOM = QColor("#660000")
UNPLAYED = QColor("#333333")
UNPLAYED_BORDER = QColor("#444444")
CURRENT_BORDER = QColor("#ff6a6a")


class PlaylistSegmentBar(QWidget):
    """A segment per song: played ones lit, the current one filling, the rest dark."""

    song_clicked = Signal(int)  # index of the song (0-based)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._titles: list[str] = []
        self._current: Optional[int] = None
        self._fraction = 0.0
        self.setMinimumHeight(SEGMENT_HEIGHT + 2)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def set_songs(self, titles: list[str]) -> None:
        self._titles = list(titles)
        self.update()

    def set_position(self, current: Optional[int], fraction: float = 0.0) -> None:
        """Song *current* is playing, *fraction* (0-1) through; None: none is."""
        self._current = current
        self._fraction = min(max(fraction, 0.0), 1.0)
        self.update()

    def _segment_rects(self) -> list[QRectF]:
        count = len(self._titles)
        if not count:
            return []
        width = (self.width() - 1 - SEGMENT_GAP * (count - 1)) / count
        top = (self.height() - SEGMENT_HEIGHT) / 2
        return [
            QRectF(i * (width + SEGMENT_GAP) + 0.5, top, max(width, 1.0), SEGMENT_HEIGHT)
            for i in range(count)
        ]

    def song_at(self, x: float) -> Optional[int]:
        for index, rect in enumerate(self._segment_rects()):
            if rect.left() - SEGMENT_GAP / 2 <= x <= rect.right() + SEGMENT_GAP / 2:
                return index
        return None

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        lit = QLinearGradient(0, 0, 0, self.height())
        lit.setColorAt(0, PLAYED_TOP)
        lit.setColorAt(1, PLAYED_BOTTOM)
        for index, rect in enumerate(self._segment_rects()):
            painter.setPen(QPen(UNPLAYED_BORDER, 1))
            painter.setBrush(UNPLAYED)
            painter.drawRoundedRect(rect, 3, 3)
            if self._current is None:
                continue
            if index < self._current:
                filled = rect
            elif index == self._current:
                filled = QRectF(rect)
                filled.setWidth(rect.width() * self._fraction)
            else:
                continue
            if filled.width() > 0:
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(lit)
                painter.drawRoundedRect(filled, 3, 3)
            if index == self._current:
                painter.setPen(QPen(CURRENT_BORDER, 1.5))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawRoundedRect(rect, 3, 3)
        painter.end()

    def event(self, event: QEvent) -> bool:
        if event.type() == QEvent.Type.ToolTip:
            index = self.song_at(event.pos().x())
            if index is None:
                QToolTip.hideText()
            else:
                QToolTip.showText(
                    event.globalPos(),
                    f"{index + 1}. {self._titles[index]}\nClick to play",
                    self,
                )
            return True
        return super().event(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            index = self.song_at(event.position().x())
            if index is not None:
                self.song_clicked.emit(index)
                return
        super().mousePressEvent(event)


class PlaylistProgressWidget(QWidget):
    """Now playing: song n of N, its progress, the playlist's progress, up next."""

    song_clicked = Signal(int)  # a song's segment was clicked (0-based)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._titles: list[str] = []
        self._current: Optional[int] = None
        self._duration = 0.0
        self._paused = False
        self._status = "Stopped"  # shown while no song is playing

        self.display = DigitalTitle("No song playing")
        self.song_bar = QProgressBar()
        self.song_bar.setRange(0, 1000)
        self.song_bar.setTextVisible(True)
        self.song_bar.setStyleSheet(JDXi.UI.Style.PROGRESS_BAR)
        self.segments = PlaylistSegmentBar()
        self.segments.song_clicked.connect(self.song_clicked)
        self.next_label = QLabel()
        self.next_label.setStyleSheet(JDXi.UI.Style.STYLE_FOREGROUND)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.display)
        layout.addWidget(self.song_bar)
        layout.addWidget(self.segments)
        layout.addWidget(self.next_label)
        self.show_stopped()

    # --- Playlist -------------------------------------------------------------

    def set_songs(self, titles: list[str]) -> None:
        """The playlist's songs (the rows with a MIDI file), in play order."""
        self._titles = list(titles)
        self.segments.set_songs(self._titles)
        if self._current is not None and self._current >= len(self._titles):
            self._current = None
        if self._current is None:
            self._show_idle(self._status)
        else:
            self._refresh()

    # --- Playback -------------------------------------------------------------

    def show_song(self, index: int, duration: float) -> None:
        """Song *index* (0-based) has started; it lasts *duration* seconds."""
        self._current = index
        self._duration = max(duration, 0.0)
        self._paused = False
        self.set_position(0.0)

    def set_current(self, index: int) -> None:
        """The playing song is now number *index* (0-based), e.g. after sorting."""
        self._current = index
        self._refresh()

    def set_position(self, seconds: float) -> None:
        """Playback position in the current song."""
        if self._current is None:
            return
        seconds = min(max(seconds, 0.0), self._duration)
        fraction = seconds / self._duration if self._duration else 0.0
        self.song_bar.setValue(int(fraction * self.song_bar.maximum()))
        self.song_bar.setFormat(
            f"{format_time(seconds)} / {format_time(self._duration)}"
            f"   -{format_time(self._duration - seconds)}"
        )
        self.segments.set_position(self._current, fraction)
        self._refresh()

    def set_paused(self, paused: bool) -> None:
        self._paused = paused
        self._refresh()

    def show_stopped(self) -> None:
        self._show_idle("Stopped")

    def show_finished(self) -> None:
        """The last song ended: every segment lit."""
        self._show_idle("Playlist finished")
        if self._titles:
            self.segments.set_position(len(self._titles) - 1, 1.0)

    def _show_idle(self, status: str) -> None:
        self._status = status
        self._current = None
        self._paused = False
        self.song_bar.setValue(0)
        self.song_bar.setFormat("")
        self.segments.set_position(None)
        count = len(self._titles)
        self.display.set_upper_display_text(
            f"{status} · {count} song{'' if count == 1 else 's'}"
        )
        self.display.setText("No song playing")
        self.next_label.setText(
            f"First: {self._titles[0]}" if self._titles else "No songs with a MIDI file"
        )

    # --- Text -----------------------------------------------------------------

    @property
    def current(self) -> Optional[int]:
        return self._current

    def _refresh(self) -> None:
        if self._current is None:
            return
        count = len(self._titles)
        state = "Paused" if self._paused else "Playing"
        self.display.set_upper_display_text(f"Song {self._current + 1} of {count} · {state}")
        self.display.setText(self._titles[self._current])
        following = self._current + 1
        self.next_label.setText(
            f"Up next: {self._titles[following]}" if following < count else "Last song"
        )
