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
from typing import Any

import numpy as np
from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget
from numpy import ndarray, dtype, floating

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.ui.widgets.plot.base import BasePlotWidget


class PitchEnvPlot(BasePlotWidget):
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
        self.setMinimumHeight(150)
        self.attack_x = 0.1
        self.decay_x = 0.3
        self.peak_level = 0.5
        self.release_x = 0.7
        self.dragging = None
        if hasattr(self.parent, "envelope_changed"):
            self.parent.envelope_changed.connect(self.set_values)
        if hasattr(self.parent, "pitchenvelope_changed"):
            self.parent.pitchenvelope_changed.connect(self.set_values)

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

            left_padding, plot_h, plot_w, top_padding = self.plot_dimensions()

            y_max, y_min = self.get_y_range()

            zero_y = self.draw_axes(axis_pen, left_padding, painter, plot_h, plot_w, top_padding, y_max, y_min)

            self.draw_x_axis(left_padding, painter, plot_w, total_time, zero_y)

            self.draw_y_axis(left_padding, painter, plot_h, top_padding, y_max, y_min)

            self.draw_title(painter, "Pitch Envelope", left_padding, plot_w, top_padding)

            self.draw_x_axis_label(painter, "Time (s)", left_padding, plot_w, plot_h, top_padding)

            self.draw_y_axis_label(painter, "Pitch", left_padding, plot_h, top_padding)

            # Background grid using base class method
            # Pitch envelope has symmetric grid (positive and negative values)
            def y_callback(y_val):
                return top_padding + ((y_max - y_val) / (y_max - y_min)) * plot_h
            
            # Draw main grid lines (positive side: 0.2, 0.4, 0.6)
            self.draw_grid(
                painter=painter,
                top_pad=top_padding,
                plot_h=plot_h,
                left_pad=left_padding,
                plot_w=plot_w,
                num_vertical_lines=6,
                num_horizontal_lines=3,  # Only 3 lines for positive side (0.2, 0.4, 0.6)
                y_min=y_min,
                y_max=y_max,
                y_callback=y_callback,
            )

            self.draw_mirror_grid(left_padding, painter, plot_h, plot_w, top_padding, y_max, y_min)

            self.draw_envelope(envelope, left_padding, painter, plot_h, plot_w, top_padding, total_samples, total_time,
                               y_max, y_min)
        finally:
            painter.end()

    def draw_mirror_grid(self, left_padding: int, painter: QPainter, plot_h: int, plot_w: int, top_padding: int,
                         y_max: float, y_min: float):
        """Draw mirror grid lines for negative side"""
        grid_pen = QPen(Qt.GlobalColor.darkGray, 1, Qt.PenStyle.DashLine)
        painter.setPen(grid_pen)
        for i in range(1, 4):
            y_val = -i * 0.2  # Negative values: -0.2, -0.4, -0.6
            y = top_padding + ((y_max - y_val) / (y_max - y_min)) * plot_h
            painter.drawLine(left_padding, y, left_padding + plot_w, y)

    def draw_envelope(self, envelope: ndarray[Any, dtype[floating[Any]]], left_padding: int, painter: QPainter,
                      plot_h: int, plot_w: int, top_padding: int, total_samples: int, total_time: int, y_max: float,
                      y_min: float):
        # Draw envelope polyline
        if self.enabled:
            painter.setPen(QPen(QColor("orange")))
            points = []
            num_points = 500
            indices = np.linspace(0, total_samples - 1, num_points).astype(int)
            for i in indices:
                t = i / self.sample_rate
                x = left_padding + (t / total_time) * plot_w
                y_val = envelope[i]
                y = top_padding + ((y_max - y_val) / (y_max - y_min)) * plot_h
                points.append((x, y))

            if points:
                path = QPainterPath()
                path.moveTo(*points[0])
                for pt in points[1:]:
                    path.lineTo(*pt)
                painter.drawPath(path)

    def draw_y_axis(self, left_padding: int, painter: QPainter, plot_h: int, top_padding: int,
                    y_max: float, y_min: float):
        """Y-axis ticks and labels from +0.6 to -0.6"""
        for i in range(-3, 4):
            y_val = i * 0.2
            y = top_padding + ((y_max - y_val) / (y_max - y_min)) * plot_h
            painter.drawLine(left_padding - 5, y, left_padding, y)
            painter.drawText(left_padding - 40, y + 5, f"{y_val:.1f}")

    def draw_x_axis(self, left_padding: int, painter: QPainter, plot_w: int, total_time: int, zero_y: float):
        # X-axis labels
        # painter.drawText(left_padding, zero_y + 20, "0")
        # painter.drawText(left_padding + plot_w - 10, zero_y + 20, "5")
        # X-axis ticks for 0, 3, 6, 9, 12, 15
        num_ticks = 6
        for i in range(num_ticks + 1):
            x = left_padding + i * plot_w / num_ticks
            painter.drawLine(x, zero_y - 5, x, zero_y + 5)
            # label = f"{i * (total_time // num_ticks)}"
            label = f"{i * (total_time / num_ticks):.0f}"
            painter.drawText(x - 10, zero_y + 20, label)

    def get_y_range(self) -> tuple[float, float]:
        # Y range
        y_min = -0.6
        y_max = 0.6
        return y_max, y_min

    def plot_dimensions(self) -> tuple[int, int, int, int]:
        # Plot area dimensions - PitchEnvPlot uses different bottom padding
        return super().plot_dimensions(top_padding=50, bottom_padding=80, left_padding=80, right_padding=50)

    def envelope_parameters(self) -> tuple[ndarray[Any, dtype[floating[Any]]], int, int]:
        """Envelope parameters"""
        attack_time = self.envelope["attack_time"] / 1000.0
        decay_time = self.envelope["decay_time"] / 1000.0
        peak_level = self.envelope["peak_level"]
        initial_level = self.envelope["initial_level"]

        attack_samples = max(int(attack_time * self.sample_rate), 1)
        decay_samples = max(int(decay_time * self.sample_rate), 1)

        attack = np.linspace(
            initial_level, peak_level, attack_samples, endpoint=False
        )
        decay = np.linspace(
            peak_level, initial_level, decay_samples, endpoint=False
        )
        envelope = np.concatenate([attack, decay])
        total_samples = len(envelope)
        total_time = 10  # seconds
        return envelope, total_samples, total_time

