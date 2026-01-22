"""
Pitch Envelope Plot
===================

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
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.ui.widgets.plot.base import BasePlotWidget


def generate_square_wave(
    width: float, mod_depth: float, sample_rate: int, duration: float
) -> np.ndarray:
    """Generates a square wave with a given duty cycle (width ∈ [0, 1])."""
    width = max(0.0, min(1.0, width))  # Clip to valid range
    total_samples = int(duration * sample_rate)

    # Define the period in samples (e.g., 10 Hz wave → 100 ms period)
    period = max(1, sample_rate // 10)  # Avoid divide-by-zero
    high_samples = int(period * width)
    low_samples = period - high_samples

    # At least 1 sample high and low to keep wave visually meaningful
    high_samples = max(1, high_samples)
    low_samples = max(1, low_samples)

    cycle = np.concatenate(
        [
            np.ones(high_samples, dtype=np.float32),
            np.zeros(low_samples, dtype=np.float32),
        ]
    )
    num_cycles = total_samples // len(cycle) + 1
    wave = np.tile(cycle, num_cycles)
    return wave[:total_samples] * mod_depth


class PWMPlot(BasePlotWidget):
    def __init__(
        self,
        width: int = JDXi.UI.Style.ADSR_PLOT_WIDTH,
        height: int = JDXi.UI.Style.ADSR_PLOT_HEIGHT,
        envelope: dict = None,
        parent: QWidget = None,
    ):
        super().__init__(parent)
        self.point_moved = None
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
        self.setMinimumHeight(JDXi.UI.Style.ADSR_PLOT_HEIGHT)
        self.attack_x = 0.1
        self.decay_x = 0.3
        self.peak_level = 0.5
        self.release_x = 0.7
        self.dragging = None
        if hasattr(self.parent, "envelope_changed"):
            self.parent.envelope_changed.connect(self.set_values)
        if hasattr(self.parent, "pulse_width_changed"):
            self.parent.pulse_width_changed.connect(self.set_values)
        if hasattr(self.parent, "mod_depth_changed"):
            self.parent.mod_depth_changed.connect(self.set_values)

    def set_values(self, envelope: dict) -> None:
        """
        Update envelope values and trigger address redraw

        :param envelope: dict
        :return: None
        """
        self.envelope = envelope
        self.update()

    def mousePressEvent(self, event):
        pos = event.position()
        points = {
            "attack": QPointF(self.attack_x * self.width(), 0),
            "decay": QPointF(
                self.decay_x * self.width(), (1 - self.peak_level) * self.height()
            ),
            "release": QPointF(
                self.release_x * self.width(), (1 - self.peak_level) * self.height()
            ),
        }
        for name, pt in points.items():
            if (pt - pos).manhattanLength() < 15:
                self.dragging = name
                break

    def mouseMoveEvent(self, event):
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

    def mouseReleaseEvent(self, event):
        self.dragging = None

    def setEnabled(self, enabled):
        super().setEnabled(enabled)  # Ensure QWidget's default behavior is applied
        self.enabled = enabled

    def paintEvent(self, event):
        """Paint the plot in the style of an LCD"""
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.Antialiasing)
            self.draw_background(painter)

            axis_pen = self.set_pen(painter)

            envelope, total_samples, total_time = self.envelope_parameters()

            left_pad, plot_h, plot_w, top_pad = self.plot_dimensions()

            y_max, y_min = self.get_y_range()

            zero_y = self.draw_axes(axis_pen, left_pad, painter, plot_h, plot_w, top_pad, y_max, y_min)

            self.draw_x_axis(left_pad, painter, plot_w, total_time, zero_y)

            self.draw_y_axis(left_pad, painter, plot_h, top_pad, y_max, y_min)

            self.draw_title(painter, "Pulse Width Modulation", left_pad, plot_w, top_pad)

            self.draw_x_axis_label(painter, "Time (s)", left_pad, plot_w, plot_h, top_pad)

            self.draw_y_axis_label(painter, "Voltage (V)", left_pad, plot_h, top_pad)

            # Background grid using base class method
            def y_callback(y_val):
                return top_pad + ((y_max - y_val) / (y_max - y_min)) * plot_h
            
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
                y_callback=y_callback,
            )

            self.draw_envelope(envelope, left_pad, painter, plot_h, plot_w, top_pad, total_samples, total_time,
                               y_max, y_min)
        finally:
            painter.end()

    def envelope_parameters(self):
        """Generate pulse width envelope"""
        envelope = generate_square_wave(
            width=self.envelope["pulse_width"],
            mod_depth=self.envelope["mod_depth"],
            sample_rate=self.sample_rate,
            duration=self.envelope.get("duration", 1.0),
        )
        total_samples = len(envelope)
        total_time = total_samples / self.sample_rate
        return envelope, total_samples, total_time

    def get_y_range(self):
        """Get Y range"""
        y_min, y_max = -0.2, 1.2
        return y_max, y_min

    def draw_x_axis(self, left_pad: int, painter: QPainter, plot_w: int, total_time: float, zero_y: float):
        """Draw X-axis ticks and labels"""
        # X-axis ticks and labels are not shown in PWMPlot (commented out)
        num_ticks = 6
        for i in range(num_ticks + 1):
            x = left_pad + i * plot_w / num_ticks
            # Tick marks and labels are omitted

    def draw_y_axis(self, left_pad: int, painter: QPainter, plot_h: int, top_pad: int, y_max: float, y_min: float):
        """Draw Y-axis ticks and labels"""
        font_metrics = painter.fontMetrics()
        for i in range(-1, 6):
            y_val = i * 0.2
            y = top_pad + ((y_max - y_val) / (y_max - y_min)) * plot_h
            painter.drawLine(left_pad - 5, y, left_pad, y)
            label = f"{y_val:.1f}"
            label_width = font_metrics.horizontalAdvance(label)
            painter.drawText(
                left_pad - 10 - label_width, y + font_metrics.ascent() / 2, label
            )

    def draw_envelope(self, envelope, left_pad: int, painter: QPainter, plot_h: int, plot_w: int,
                      top_pad: int, total_samples: int, total_time: float, y_max: float, y_min: float):
        """Draw envelope plot"""
        if not self.enabled:
            return

        painter.setPen(QPen(QColor("orange"), 2))
        points = []
        num_points = 500
        indices = np.linspace(0, total_samples - 1, num_points).astype(int)

        for i in indices:
            if i >= len(envelope):
                continue
            t = i / self.sample_rate
            x = left_pad + (t / total_time) * plot_w
            y_val = envelope[i]
            y = top_pad + ((y_max - y_val) / (y_max - y_min)) * plot_h
            points.append(QPointF(x, y))

        if points:
            path = QPainterPath()
            path.moveTo(points[0])
            for pt in points[1:]:
                path.lineTo(pt)  # For smoothing: use cubicTo
            painter.drawPath(path)
