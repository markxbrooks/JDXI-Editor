"""
ADSR Plot
==========

This module defines the `ADSRPlot` class, address QWidget subclass that visualizes an ADSR (Attack,
Decay, Sustain, Release) envelope using Matplotlib. The plot displays the envelope's progression
over time, with adjustable parameters for attack, decay, sustain, and release times, as well as
initial, peak, and sustain amplitudes.

The plot is rendered in address QWidget, and the background and text colors are customized for better
visibility, with the envelope plotted in orange on address dark gray background.

Classes:
--------
- `ADSRPlot`: A QWidget subclass that generates and displays an ADSR envelope plot.

Methods:
--------
- `__init__(self)`: Initializes the widget and sets up the figure and layout for the plot.
- `plot_envelope(self)`: Generates and plots the ADSR envelope based on the current envelope parameters.
- `set_values(self, envelope)`: Updates the envelope parameters and refreshes the plot.

Customization:
-------------
- The plot background is dark gray (`#333333`), with all plot elements (ticks, labels, title) in
  orange for better visibility against the dark background.
- The time is represented in seconds, and the amplitude in address range from 0 to 1.
"""

import numpy as np
from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QLinearGradient,
    QMouseEvent,
    QPainter,
    QPainterPath,
    QPaintEvent,
    QPen,
)
from PySide6.QtWidgets import QWidget

from decologr import Decologr as log
from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.ui.widgets.plot.base import BasePlotWidget


class ADSRPlot(BasePlotWidget):
    def __init__(
        self,
        width: int = 300,
        height: int = 300,
        envelope: dict = None,
        parent: QWidget = None,
    ):
        super().__init__(parent)
        """
        Initialize the ADSRPlot

        :param width: int
        :param height: int
        :param envelope: dict
        :param parent: QWidget
        """
        self.parent = parent
        # Default envelope parameters (times in ms)
        self.enabled = True
        self.envelope = envelope
        # Set address fixed size for the widget (or use layouts as needed)
        self.setMinimumSize(width, height)
        self.setMaximumHeight(height)
        self.setMaximumWidth(width)
        # Use dark gray background

        JDXi.UI.ThemeManager.apply_adsr_plot(self)
        # Sample rate for converting times to samples
        self.sample_rate = 256
        self.setMinimumHeight(150)
        self.attack_x = 0.1
        self.decay_x = 0.3
        self.sustain_level = 0.5
        self.release_x = 0.7
        self.dragging = None
        if hasattr(self.parent, "envelope_changed"):
            self.parent.envelope_changed.connect(self.set_values)
        if hasattr(self.parent, "pitchenvelope_changed"):
            self.parent.pitchenvelope_changed.connect(self.set_values)

    def paintEvent_experimental(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(QColor("#ffffff"), 2)
        painter.setPen(pen)

        w = self.width()
        h = self.height()

        # Define points
        p0 = QPointF(0, h)
        p1 = QPointF(self.attack_x * w, 0)
        p2 = QPointF(self.decay_x * w, (1 - self.sustain_level) * h)
        p3 = QPointF(self.release_x * w, (1 - self.sustain_level) * h)
        p4 = QPointF(w, h)

        # Draw lines
        painter.drawPolyline([p0, p1, p2, p3, p4])

        # Draw draggable points
        dot_pen = QPen(QColor("#ff6666"), 4)
        painter.setPen(dot_pen)
        painter.setBrush(QColor("#ffcccc"))
        for pt in [p1, p2, p3]:
            painter.drawEllipse(pt, 6, 6)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        pos = event.position()
        points = {
            "attack": QPointF(self.attack_x * self.width(), 0),
            "decay": QPointF(
                self.decay_x * self.width(), (1 - self.sustain_level) * self.height()
            ),
            "release": QPointF(
                self.release_x * self.width(), (1 - self.sustain_level) * self.height()
            ),
        }
        for name, pt in points.items():
            if (pt - pos).manhattanLength() < 15:
                self.dragging = name
                break

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.dragging:
            pos = event.position()
            if self.dragging == "attack":
                self.attack_x = max(0.01, min(pos.x() / self.width(), 1.0))
            elif self.dragging == "decay":
                self.decay_x = max(
                    self.attack_x + 0.01, min(pos.x() / self.width(), 1.0)
                )
            elif self.dragging == "release":
                self.release_x = max(
                    self.decay_x + 0.01, min(pos.x() / self.width(), 1.0)
                )

            self.point_moved.emit(self.dragging, pos.x() / self.width())
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.dragging = None

    def setEnabled(self, enabled: bool) -> None:
        super().setEnabled(enabled)  # Ensure QWidget's default behavior is applied
        self.enabled = enabled

    def set_values(self, envelope: dict) -> None:
        """Update envelope values and trigger address redraw.
        :param envelope: dict
        """
        self.envelope = envelope
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        """Paint the ADSR plot in the style of FilterPlot.
        :param event: QPaintEvent
        """
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.Antialiasing)
            self.draw_background(painter)

            axis_pen = self.set_pen(painter)

            envelope, total_samples, total_time = self.envelope_parameters()

            left_pad, plot_h, plot_w, top_pad = self.plot_dimensions()

            y_max, y_min = self.get_y_range()

            zero_y = self.draw_axes(axis_pen, left_pad, painter, plot_h, plot_w, top_pad, y_max, y_min, zero_at_bottom=True)

            self.draw_x_axis(left_pad, painter, plot_w, total_time, zero_y)

            self.draw_y_axis(left_pad, painter, plot_h, top_pad, y_max, y_min)

            self.draw_title(painter, "ADSR Envelope", left_pad, plot_w, top_pad)

            self.draw_x_axis_label(painter, "Time (s)", left_pad, plot_w, plot_h, top_pad)

            self.draw_y_axis_label(painter, "Amplitude", left_pad, plot_h, top_pad)

            # Background grid using base class method
            self.draw_grid(
                painter=painter,
                top_pad=top_pad,
                plot_h=plot_h,
                left_pad=left_pad,
                plot_w=plot_w,
                num_vertical_lines=6,
                num_horizontal_lines=5,
                y_min=y_min,
                y_max=y_max,
            )

            self.draw_envelope(envelope, left_pad, painter, plot_h, plot_w, top_pad, total_samples, total_time,
                               y_max, y_min, zero_y)
        finally:
            painter.end()

    def envelope_parameters(self):
        """Compute envelope segments in seconds"""
        attack_time = self.envelope["attack_time"] / 1000.0
        decay_time = self.envelope["decay_time"] / 1000.0
        release_time = self.envelope["release_time"] / 1000.0
        sustain_level = self.envelope["sustain_level"]
        peak_level = max(self.envelope["peak_level"] * 2, 0)
        initial_level = self.envelope["initial_level"]

        # Convert times to sample counts
        attack_samples = int(attack_time * self.sample_rate)
        decay_samples = int(decay_time * self.sample_rate)
        sustain_samples = int(self.sample_rate * 2)  # Fixed 2 seconds sustain
        release_samples = int(release_time * self.sample_rate)

        # Construct the ADSR envelope as one concatenated array
        # Normalized ADSR envelope (peak level = 1.0)
        attack = np.linspace(
            initial_level, peak_level, attack_samples, endpoint=False
        )  # Attack from initial to peak level
        decay = np.linspace(
            peak_level, sustain_level * peak_level, decay_samples, endpoint=False
        )  # Decay to sustain level
        sustain = np.full(
            sustain_samples, sustain_level * peak_level
        )  # Sustain level scaled by peak level
        release = np.linspace(
            sustain_level * peak_level, 0.0, release_samples
        )  # Release from sustain level to 0
        envelope = np.concatenate([attack, decay, sustain, release])

        total_samples = len(envelope)
        total_time = 5  # in seconds
        return envelope, total_samples, total_time

    def get_y_range(self):
        """Get Y range"""
        y_min, y_max = 0.0, 1.0
        return y_max, y_min

    def draw_x_axis(self, left_pad: int, painter: QPainter, plot_w: int, total_time: float, zero_y: float):
        """Draw X-axis ticks and labels"""
        font_metrics = painter.fontMetrics()
        num_ticks = 6
        for i in range(num_ticks + 1):
            x = left_pad + i * plot_w / num_ticks
            # Draw tick mark
            painter.drawLine(x, zero_y, x, zero_y + 5)
            # Draw label
            time_val = i * (total_time / num_ticks)
            label = f"{time_val:.1f}"
            label_width = font_metrics.horizontalAdvance(label)
            painter.drawText(
                x - label_width / 2, zero_y + 20, label
            )

    def draw_y_axis(self, left_pad: int, painter: QPainter, plot_h: int, top_pad: int, y_max: float, y_min: float):
        """Draw Y-axis ticks and labels"""
        font_metrics = painter.fontMetrics()
        for i in range(6):  # 0.0 to 1.0 in 0.2 steps
            y_val = i * 0.2
            y = top_pad + plot_h - (y_val * plot_h)
            painter.drawLine(left_pad - 5, y, left_pad, y)
            label = f"{y_val:.1f}"
            label_width = font_metrics.horizontalAdvance(label)
            painter.drawText(
                left_pad - 10 - label_width, y + font_metrics.ascent() / 2, label
            )

    def draw_envelope(self, envelope, left_pad: int, painter: QPainter, plot_h: int, plot_w: int,
                      top_pad: int, total_samples: int, total_time: float, y_max: float, y_min: float, zero_y: float):
        """Draw envelope plot"""
        if not self.enabled:
            return

        # Draw the envelope polyline last, on top of the grid
        # Create a list of points for the envelope polyline.
        points = []
        num_points = 500
        indices = np.linspace(0, total_samples - 1, num_points).astype(int)
        for i in indices:
            t = i / self.sample_rate  # time in seconds
            x = left_pad + (t / total_time) * plot_w
            y = top_pad + plot_h - (envelope[i] * plot_h)
            points.append((x, y))

        # Build the path for the envelope curve
        if points:
            path = QPainterPath()
            # Start from the left edge at zero line
            path.moveTo(left_pad, zero_y)
            # Move to first point of the curve
            path.lineTo(*points[0])
            # Draw through all curve points
            for pt in points[1:]:
                path.lineTo(*pt)
            # End at the right edge at zero line
            path.lineTo(left_pad + plot_w, zero_y)
            # Close back to start (this creates the closed area under the curve)
            path.closeSubpath()
            
            # Draw shaded fill under the curve
            self.draw_shaded_curve(
                painter=painter,
                path=path,
                top_pad=top_pad,
                plot_h=plot_h,
                zero_y=zero_y,
                left_pad=left_pad,
                plot_w=plot_w,
            )
            
            # Draw the envelope polyline on top (just the curve, not the closed path)
            curve_path = QPainterPath()
            curve_path.moveTo(*points[0])
            for pt in points[1:]:
                curve_path.lineTo(*pt)
            painter.setPen(QPen(QColor("orange"), 2))
            painter.drawPath(curve_path)
