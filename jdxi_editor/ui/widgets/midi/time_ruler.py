"""
TimeRulerWidget

Time axis above the track viewer. Shows the playback position, the loop
range and program-change markers, and is the place to seek (click/drag)
and to move or delete program changes (drag/right-click a marker handle).
"""

import bisect
from dataclasses import dataclass
from typing import Any, Optional

import mido
from PySide6.QtCore import QPoint, QPointF, Qt, Signal
from PySide6.QtGui import (
    QColor,
    QMouseEvent,
    QPainter,
    QPaintEvent,
    QPen,
    QPolygonF,
)
from PySide6.QtWidgets import QMenu, QWidget

from jdxi_editor.core.jdxi import JDXi

HANDLE_WIDTH = 10  # Flag-shaped marker handle, px
HANDLE_HEIGHT = 14
HANDLE_HIT_SLOP = 4  # Extra px around a handle that still grabs it
RULER_MIN_HEIGHT = 34
MIN_LABEL_SPACING = 28  # px between bar numbers; fewer bars are numbered when zoomed out
MIN_BEAT_SPACING = 6  # px between beat ticks before they are hidden
MARKER_GROUP_PX = 6  # markers closer than this share one flag and label


MAX_GRID_BARS = 2000  # beyond this the ruler shows seconds


@dataclass
class BarLine:
    """A bar on the ruler: where it starts, its number, and the time signature
    when one starts there (None otherwise)."""

    seconds: float
    bar: int
    signature: Optional[tuple[int, int]] = None


def _conductor(midi_file: mido.MidiFile) -> tuple[list, list, int]:
    """Tempo changes [(tick, µs per beat)], time signatures [(tick, num, den)] and
    the last tick of *midi_file*, from all its tracks (as the playback engine
    reads them: one entry per tick, the last one wins)."""
    tempos: dict[int, int] = {}
    signatures: dict[int, tuple[int, int]] = {}
    end = 0
    for track in midi_file.tracks:
        tick = 0
        for msg in track:
            tick += msg.time
            if msg.type == "set_tempo":
                tempos[tick] = msg.tempo
            elif msg.type == "time_signature":
                signatures[tick] = (msg.numerator, msg.denominator)
        end = max(end, tick)
    tempos.setdefault(0, 500_000)
    signatures.setdefault(0, (4, 4))
    return (sorted(tempos.items()), [(t, n, d) for t, (n, d) in sorted(signatures.items())], end)


def bar_grid(midi_file: mido.MidiFile) -> tuple[list[BarLine], list[float]]:
    """The bars and beats of *midi_file*, in seconds, following its time
    signatures and tempo changes.

    Bars are counted as the playback engine counts them (``bar_beat_at_tick``,
    the position shown in the player and «Snap to bars»): at a change of time
    signature a new bar starts, and an unfinished bar before it still counts.
    Returns ([], []) when the file has more than MAX_GRID_BARS bars.
    """
    tpb = midi_file.ticks_per_beat or 480
    tempos, signatures, end_tick = _conductor(midi_file)
    # seconds at each tempo change
    starts = [0.0]
    for (t0, tempo), (t1, _) in zip(tempos, tempos[1:]):
        starts.append(starts[-1] + mido.tick2second(t1 - t0, tpb, tempo))

    tempo_ticks = [t for t, _ in tempos]

    def seconds(tick: float) -> float:
        k = max(0, bisect.bisect_right(tempo_ticks, tick) - 1)
        return starts[k] + mido.tick2second(tick - tempos[k][0], tpb, tempos[k][1])

    bars: list[BarLine] = []
    beats: list[float] = []
    number = 1
    for k, (start, num, den) in enumerate(signatures):
        stop = signatures[k + 1][0] if k + 1 < len(signatures) else max(end_tick, start + 1)
        beat_ticks = tpb * 4 / den
        bar_ticks = beat_ticks * num
        tick = float(start)
        first = True
        while tick < stop - 1e-6:
            if len(bars) > MAX_GRID_BARS:
                return [], []
            bars.append(BarLine(seconds(tick), number, (num, den) if first else None))
            first = False
            bar_end = min(tick + bar_ticks, stop)
            beat = tick + beat_ticks
            while beat < bar_end - 1e-6:
                beats.append(seconds(beat))
                beat += beat_ticks
            number += 1
            tick += bar_ticks
    # the same signature again is not a change
    for line in bars[1:]:
        if line.signature is not None and line.signature == _signature_before(bars, line):
            line.signature = None
    if bars and bars[0].signature == (4, 4) and all(b.signature is None for b in bars[1:]):
        bars[0].signature = None  # plain 4/4 throughout: nothing to say
    return bars, beats


def _signature_before(bars: list[BarLine], line: BarLine) -> Optional[tuple[int, int]]:
    current = None
    for b in bars:
        if b is line:
            return current
        if b.signature is not None:
            current = b.signature
    return current


@dataclass
class RulerMarker:
    """A marker on the ruler. Markers with a key can be dragged and deleted."""

    seconds: float
    label: Optional[str] = None
    color: Optional[QColor] = None
    key: Any = None


class TimeRulerWidget(QWidget):
    """
    TimeRulerWidget

    Signals:
        seek_requested(float): user clicked/dragged to a time (seconds)
        marker_moved(object, float): marker *key* dragged to a new time
        marker_delete_requested(object): delete the marker with *key*
        marker_edit_requested(object): edit the marker with *key* (double-click)
    """

    seek_requested = Signal(float)
    marker_moved = Signal(object, float)
    marker_delete_requested = Signal(object)
    marker_edit_requested = Signal(object)

    def __init__(self, midi_file: mido.MidiFile = None, parent: QWidget = None):
        super().__init__(parent)
        self.midi_file_cached_total_length = None
        self.midi_file = midi_file
        self.setMinimumHeight(RULER_MIN_HEIGHT)
        self.setMaximumHeight(JDXi.UI.Style.MAX_RULER_HEIGHT)
        self.setMouseTracking(True)
        self._markers: list[RulerMarker] = []
        self._playhead_seconds: Optional[float] = None
        self._loop_range: Optional[tuple[float, float]] = None
        self._loop_marks: tuple[Optional[float], Optional[float]] = (None, None)
        self._loop_enabled = False
        # Interaction state
        self._dragging_marker: Optional[RulerMarker] = None
        self._drag_seconds: Optional[float] = None
        self._scrubbing = False
        self._grid: Optional[tuple[list[BarLine], list[float]]] = None

    # --- Data -----------------------------------------------------------------

    def set_midi_file(self, midi_file: mido.MidiFile, length: float | None = None) -> None:
        self.midi_file = midi_file
        # *length* when the caller knows it (mido's length reads the whole file)
        self.midi_file_cached_total_length = midi_file.length if length is None else length
        self._grid = None  # worked out again at the next paint
        self.update()

    def grid(self) -> tuple[list[BarLine], list[float]]:
        """The file's bars and beats (see bar_grid), worked out once per file."""
        if self._grid is None:
            try:
                self._grid = bar_grid(self.midi_file) if self.midi_file else ([], [])
            except Exception:  # an odd file: the ruler falls back to seconds
                self._grid = ([], [])
        return self._grid

    @property
    def duration(self) -> float:
        return self.midi_file_cached_total_length or 0.0

    def set_playhead(self, seconds: Optional[float]) -> None:
        """Show the playback position (None hides it)."""
        if seconds == self._playhead_seconds:
            return
        self._playhead_seconds = seconds
        self.update()

    def set_loop_region(
        self, loop_range: Optional[tuple[float, float]], enabled: bool
    ) -> None:
        """Show the A–B range (None = whole file) and whether looping is on."""
        self._loop_range = loop_range
        self._loop_enabled = enabled
        self.update()

    def set_loop_marks(self, a: Optional[float], b: Optional[float]) -> None:
        """The A and B points as they are set: one shows at once, before the
        other makes the range (A alone used to show nothing)."""
        self._loop_marks = (a, b)
        self.update()

    def add_marker(
        self,
        seconds: float,
        color: QColor | None = None,
        label: str | None = None,
        key: Any = None,
    ) -> None:
        """Add a time marker in seconds and repaint. Markers with a *key* are draggable."""
        try:
            seconds = max(0.0, float(seconds))
        except (TypeError, ValueError):
            seconds = 0.0
        self._markers.append(RulerMarker(seconds, label, color, key))
        self.update()

    def set_markers(self, markers: list[RulerMarker]) -> None:
        """Replace all markers."""
        self._markers = list(markers)
        self.update()

    def clear_markers(self) -> None:
        """Clear all time markers and repaint."""
        self._markers.clear()
        self.update()

    # --- Geometry -------------------------------------------------------------

    def _x_for(self, seconds: float) -> int:
        if self.duration <= 0:
            return 0
        return int(seconds / self.duration * self.width())

    def _seconds_for(self, x: float) -> float:
        if self.width() <= 0:
            return 0.0
        return max(0.0, min(self.duration, x / self.width() * self.duration))

    def _marker_at(self, pos: QPoint) -> Optional[RulerMarker]:
        """Draggable marker whose handle is under *pos*."""
        if pos.y() > HANDLE_HEIGHT + HANDLE_HIT_SLOP:
            return None
        for marker in reversed(self._markers):
            if marker.key is None:
                continue
            x = self._x_for(marker.seconds)
            if x - HANDLE_HIT_SLOP <= pos.x() <= x + HANDLE_WIDTH + HANDLE_HIT_SLOP:
                return marker
        return None

    # --- Mouse ----------------------------------------------------------------

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if not self.midi_file:
            return
        pos = event.position().toPoint()
        marker = self._marker_at(pos)
        if event.button() == Qt.MouseButton.RightButton:
            if marker is not None:
                self._show_marker_menu(marker, event.globalPosition().toPoint())
            return
        if event.button() != Qt.MouseButton.LeftButton:
            return
        if marker is not None:
            self._dragging_marker = marker
            self._drag_seconds = marker.seconds
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        else:
            self._scrubbing = True
            self._drag_seconds = self._seconds_for(pos.x())
        self.update()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pos = event.position().toPoint()
        if self._dragging_marker is not None or self._scrubbing:
            self._drag_seconds = self._seconds_for(pos.x())
            self.update()
            return
        hovering = self._marker_at(pos) is not None
        self.setCursor(
            Qt.CursorShape.OpenHandCursor if hovering else Qt.CursorShape.ArrowCursor
        )
        near = [m.label for m in self._markers_near(pos) if m.label]
        tip = "\n".join(near)
        if hovering:
            tip += ("\n\n" if tip else "") + (
                "Double-click to change, drag to move, right-click to delete"
            )
        self.setToolTip(tip)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        marker = (
            self._marker_at(event.position().toPoint())
            if event.button() == Qt.MouseButton.LeftButton
            else None
        )
        if marker is None:
            super().mouseDoubleClickEvent(event)  # Treated as a press: seek
            return
        # The first click of the pair started a (zero-distance) drag; drop it
        self._dragging_marker = None
        self._drag_seconds = None
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.update()
        self.marker_edit_requested.emit(marker.key)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            return
        seconds = self._drag_seconds
        if self._dragging_marker is not None and seconds is not None:
            marker = self._dragging_marker
            if abs(seconds - marker.seconds) > 1e-3:
                self.marker_moved.emit(marker.key, seconds)
        elif self._scrubbing and seconds is not None:
            self.seek_requested.emit(seconds)
        self._dragging_marker = None
        self._scrubbing = False
        self._drag_seconds = None
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.update()

    def _show_marker_menu(self, marker: RulerMarker, global_pos: QPoint) -> None:
        menu = QMenu(self)
        label = marker.label or "Program Change"
        delete_action = menu.addAction(f"Delete {label}")
        if menu.exec(global_pos) is delete_action:
            self.marker_delete_requested.emit(marker.key)

    # --- Painting -------------------------------------------------------------

    def paintEvent(self, event: QPaintEvent) -> None:
        if not self.midi_file:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        duration = self.duration
        width = self.width()
        height = self.height()
        mp = JDXi.UI.MidiPlayer

        self._paint_loop_region(painter, height)

        font = painter.font()
        font.setPointSize(int(mp.FONT_RULER.replace("px", "")) or 10)
        painter.setFont(font)

        if duration > 0:
            self._paint_bar_beat_grid(painter, width, height, duration)
            self._paint_markers(painter, height)
            self._paint_playhead(painter, height)
        painter.end()

    def _paint_bar_beat_grid(
        self, painter: QPainter, width: int, height: int, duration: float
    ) -> None:
        """Bars (numbered) and beats, with the file's time signatures and tempo
        changes; the time signature where it starts (when not 4/4 throughout).
        Seconds when the file has no usable bars."""
        mp = JDXi.UI.MidiPlayer
        bar_pen = QPen(QColor(mp.BORDER_HOVER))
        bar_pen.setWidth(1)
        label_pen = QPen(QColor(mp.TEXT_SECONDARY))
        minor_pen = QPen(QColor(mp.BORDER))
        bars, beats = self.grid()

        if not bars:
            spacing = width / duration
            for second in range(int(duration) + 1):
                x = int(second * spacing)
                if second % 10 == 0:
                    painter.setPen(bar_pen)
                    painter.drawLine(x, 0, x, height)
                    painter.setPen(label_pen)
                    painter.drawText(x + 2, height - 4, f"{second}s")
                elif spacing >= 4:
                    painter.setPen(bar_pen)
                    painter.drawLine(x, height - 5, x, height)
            return

        shown = [b for b in bars if b.seconds <= duration + 1e-6]
        bar_px = width / max(1, len(shown)) if shown else width
        label_every = self._label_interval(bar_px, painter, len(shown))
        if beats and width / (len(beats) + len(shown)) >= MIN_BEAT_SPACING:
            painter.setPen(minor_pen)
            for bt in beats:
                if bt > duration:
                    break
                bx = int(bt / duration * width)
                painter.drawLine(bx, height - 5, bx, height)
        for index, line in enumerate(shown):
            x = int(line.seconds / duration * width)
            text = f"{line.bar}"
            if line.signature is not None:
                text += f"  {line.signature[0]}/{line.signature[1]}"
            if index % label_every == 0 or line.signature is not None:
                painter.setPen(bar_pen)
                painter.drawLine(x, 0, x, height)
                painter.setPen(label_pen)
                painter.drawText(x + 3, height - 4, text)
            else:
                painter.setPen(minor_pen)
                painter.drawLine(x, height - 10, x, height)

    @staticmethod
    def _label_interval(bar_px: float, painter: QPainter, bar_count: float) -> int:
        """Number every 1, 2, 4, 8… bars so labels are MIN_LABEL_SPACING apart."""
        text_px = painter.fontMetrics().horizontalAdvance(str(int(bar_count) + 1)) + 6
        needed = max(MIN_LABEL_SPACING, text_px)
        interval = 1
        while bar_px * interval < needed and interval < 1024:
            interval *= 2
        return interval

    def _paint_loop_region(self, painter: QPainter, height: int) -> None:
        if self._loop_range is None:
            # a single point set so far: its line and letter
            for seconds, letter in zip(self._loop_marks, "AB"):
                if seconds is None:
                    continue
                x = self._x_for(seconds)
                painter.setPen(QPen(QColor(JDXi.UI.Style.ACCENT_ANALOG), 2))
                painter.drawLine(x, 0, x, height)
                painter.drawText(x + 3, height // 2 + 4, letter)
        if self._loop_range is None and not self._loop_enabled:
            return
        start, end = self._loop_range or (0.0, self.duration)
        x1, x2 = self._x_for(start), self._x_for(end)
        color = QColor(JDXi.UI.Style.ACCENT_ANALOG)
        color.setAlpha(90 if self._loop_enabled else 35)
        painter.fillRect(x1, 0, max(1, x2 - x1), height, color)
        if self._loop_range is not None:
            painter.setPen(QPen(QColor(JDXi.UI.Style.ACCENT_ANALOG), 2))
            painter.drawLine(x1, 0, x1, height)
            painter.drawLine(x2, 0, x2, height)
            painter.drawText(x1 + 3, height // 2 + 4, "A")
            painter.drawText(x2 - 10, height // 2 + 4, "B")

    def _marker_groups(self) -> list[list[RulerMarker]]:
        """Markers drawn within MARKER_GROUP_PX of each other, left to right."""
        def x_of(marker: RulerMarker) -> int:
            if marker is self._dragging_marker and self._drag_seconds is not None:
                return self._x_for(self._drag_seconds)
            return self._x_for(marker.seconds)

        groups: list[list[RulerMarker]] = []
        for marker in sorted(self._markers, key=x_of):
            if groups and x_of(marker) - x_of(groups[-1][0]) < MARKER_GROUP_PX:
                groups[-1].append(marker)
            else:
                groups.append([marker])
        return groups

    def _paint_markers(self, painter: QPainter, height: int) -> None:
        """One flag per group; a label only where it fits before the next one."""
        groups = self._marker_groups()
        for index, group in enumerate(groups):
            for marker in group:
                self._paint_marker(painter, marker, height, label=False)
            labels = [m.label for m in group if m.label]
            if not labels:
                continue
            text = labels[0] + (f" +{len(labels) - 1}" if len(labels) > 1 else "")
            x = self._x_for(group[0].seconds) + HANDLE_WIDTH + 2
            next_x = (
                self._x_for(groups[index + 1][0].seconds)
                if index + 1 < len(groups)
                else self.width()
            )
            metrics = painter.fontMetrics()
            if x + metrics.horizontalAdvance(text) >= next_x:
                text = f"+{len(labels) - 1}" if len(labels) > 1 else ""
                if not text or x + metrics.horizontalAdvance(text) >= next_x:
                    continue  # no room: the tooltip lists it
            painter.setPen(QPen(QColor(JDXi.UI.MidiPlayer.TEXT)))
            painter.drawText(x, HANDLE_HEIGHT - 2, text)

    def _markers_near(self, pos: QPoint) -> list[RulerMarker]:
        """Markers in the group under *pos* (for the tooltip)."""
        if pos.y() > HANDLE_HEIGHT + HANDLE_HIT_SLOP:
            return []
        for group in self._marker_groups():
            x = self._x_for(group[0].seconds)
            if x - HANDLE_HIT_SLOP <= pos.x() <= x + HANDLE_WIDTH + HANDLE_HIT_SLOP:
                return group
        return []

    def _paint_marker(
        self, painter: QPainter, marker: RulerMarker, height: int, label: bool = True
    ) -> None:
        dragging = marker is self._dragging_marker
        seconds = self._drag_seconds if dragging else marker.seconds
        x = self._x_for(seconds)
        color = (
            marker.color
            if isinstance(marker.color, QColor)
            else QColor(JDXi.UI.Style.ACCENT)
        )
        pen = QPen(color)
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawLine(x, 0, x, height)
        if marker.key is not None:
            # Flag handle: grab here to drag, right-click to delete
            flag = QPolygonF(
                [
                    QPointF(x, 0),
                    QPointF(x + HANDLE_WIDTH, HANDLE_HEIGHT / 2),
                    QPointF(x, HANDLE_HEIGHT),
                ]
            )
            fill = QColor(color)
            fill.setAlpha(255 if dragging else 200)
            painter.setBrush(fill)
            painter.drawPolygon(flag)
            painter.setBrush(Qt.BrushStyle.NoBrush)
        if label and marker.label:
            painter.setPen(QPen(QColor(JDXi.UI.MidiPlayer.TEXT)))
            painter.drawText(x + HANDLE_WIDTH + 2, HANDLE_HEIGHT - 2, marker.label)

    def _paint_playhead(self, painter: QPainter, height: int) -> None:
        seconds = self._drag_seconds if self._scrubbing else self._playhead_seconds
        if seconds is None:
            return
        x = self._x_for(seconds)
        pen = QPen(QColor(JDXi.UI.MidiPlayer.ACCENT))
        pen.setWidth(3)
        painter.setPen(pen)
        painter.drawLine(x, 0, x, height)
