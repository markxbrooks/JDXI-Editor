"""
TimeRulerWidget

Time axis above the track viewer. Shows the playback position, the loop
range and program-change markers, and is the place to seek (click/drag)
and to move or delete program changes (drag/right-click a marker handle).
"""

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
        self._loop_enabled = False
        # Interaction state
        self._dragging_marker: Optional[RulerMarker] = None
        self._drag_seconds: Optional[float] = None
        self._scrubbing = False

    # --- Data -----------------------------------------------------------------

    def set_midi_file(self, midi_file: mido.MidiFile) -> None:
        self.midi_file = midi_file
        self.midi_file_cached_total_length = self.midi_file.length
        self.update()

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
        self.setToolTip(
            "Double-click to change, drag to move, right-click to delete"
            if hovering
            else ""
        )

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

        self._paint_loop_region(painter, height)

        num_marks = int(duration) + 1
        spacing = width / duration if duration else width

        font = painter.font()
        font.setPointSize(8)
        painter.setFont(font)
        painter.setPen(QPen(Qt.white))

        for second in range(num_marks):
            x = int(second * spacing)
            if second % 10 == 0:
                # Draw major ticks every 10 seconds
                painter.drawLine(x, 0, x, height)
                painter.drawText(x + 2, height - 4, f"{second}s")
            elif spacing >= 4:
                painter.drawLine(x, height - 5, x, height)

        if duration > 0:
            for marker in self._markers:
                self._paint_marker(painter, marker, height)
            self._paint_playhead(painter, height)
        painter.end()

    def _paint_loop_region(self, painter: QPainter, height: int) -> None:
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

    def _paint_marker(self, painter: QPainter, marker: RulerMarker, height: int) -> None:
        dragging = marker is self._dragging_marker
        seconds = self._drag_seconds if dragging else marker.seconds
        x = self._x_for(seconds)
        color = (
            marker.color
            if isinstance(marker.color, QColor)
            else QColor(JDXi.UI.Style.ACCENT)
        )
        pen = QPen(color)
        pen.setWidth(2)
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
        if marker.label:
            painter.setPen(QPen(Qt.white))
            painter.drawText(x + HANDLE_WIDTH + 2, HANDLE_HEIGHT - 2, marker.label)

    def _paint_playhead(self, painter: QPainter, height: int) -> None:
        seconds = self._drag_seconds if self._scrubbing else self._playhead_seconds
        if seconds is None:
            return
        x = self._x_for(seconds)
        pen = QPen(QColor(JDXi.UI.Style.FOREGROUND))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(x, 0, x, height)
