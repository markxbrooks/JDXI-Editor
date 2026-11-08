"""
Track Velocity Slider

A small slider on each MIDI player track row that scales the track's note
velocities during playback (10-200 %, 100 % = as in the file). Channel volume
is set by CC in the Program editor; this balances tracks, including tracks
that share a channel. Double-click resets to 100 %.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QSlider, QWidget


class TrackVelocitySlider(QSlider):
    """Horizontal slider in percent; scale() is the velocity factor."""

    MIN_PERCENT = 10
    MAX_PERCENT = 200
    DEFAULT_PERCENT = 100

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(Qt.Orientation.Horizontal, parent)
        self.setRange(self.MIN_PERCENT, self.MAX_PERCENT)
        self.setValue(self.DEFAULT_PERCENT)
        self.setPageStep(10)
        self.valueChanged.connect(self._update_tooltip)
        self._update_tooltip(self.value())

    def scale(self) -> float:
        return self.value() / 100.0

    def set_scale(self, scale: float) -> None:
        self.setValue(round(scale * 100))

    def _update_tooltip(self, percent: int) -> None:
        self.setToolTip(f"Track velocity {percent}% (double-click: 100%)")

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        self.setValue(self.DEFAULT_PERCENT)
        event.accept()
