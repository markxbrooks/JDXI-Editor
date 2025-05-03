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
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtCore import Qt, Signal, QPointF
from PySide6.QtWidgets import QVBoxLayout, QWidget
from PySide6.QtGui import QPainter, QPainterPath, QLinearGradient, QColor, QPen, QFont

from jdxi_editor.jdxi.style import JDXIStyle


class PitchEnvPlot(QWidget):
    def __init__(self,
                 width: int = 400,
                 height: int = 400,
                 envelope: dict = None,
                 parent: QWidget = None):
        super().__init__(parent)
        self.parent = parent
        # Default envelope parameters (times in ms)
        self.enabled = True
        self.envelope = envelope
        # Set address fixed size for the widget (or use layouts as needed)
        self.setMinimumSize(width, height)
        self.setMaximumHeight(height)
        self.setMaximumWidth(width)
        # Use dark gray background
        self.setStyleSheet(
            JDXIStyle.ADSR_PLOT
        )
        # Sample rate for converting times to samples
        self.sample_rate = 256
        self.setMinimumHeight(150)
        self.attack_x = 0.1
        self.decay_x = 0.3
        self.peak_level = 0.5
        self.release_x = 0.7
        self.dragging = None
        if hasattr(self.parent, "envelopeChanged"):
            self.parent.envelopeChanged.connect(self.set_values)
        if hasattr(self.parent, "pitchEnvelopeChanged"):
            self.parent.pitchEnvelopeChanged.connect(self.set_values)

    def set_values(self, envelope: dict):
        self.envelope = envelope
        self.update()

    def mousePressEvent(self, event):
        pos = event.position()
        points = {
            "attack": QPointF(self.attack_x * self.width(), 0),
            "decay": QPointF(self.decay_x * self.width(), (1 - self.peak_level) * self.height()),
            "release": QPointF(self.release_x * self.width(), (1 - self.peak_level) * self.height()),
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
                self.decay_x = max(self.attack_x + 0.01, min(pos.x() / self.width(), 1.0))
            elif self.dragging == "release":
                self.release_x = max(self.decay_x + 0.01, min(pos.x() / self.width(), 1.0))

            self.point_moved.emit(self.dragging, pos.x() / self.width())
            self.update()

    def mouseReleaseEvent(self, event):
        self.dragging = None

    def setEnabled(self, enabled):
        super().setEnabled(enabled)  # Ensure QWidget's default behavior is applied
        self.enabled = enabled

    def set_values(self, envelope):
        """Update envelope values and trigger address redraw."""
        self.envelope = envelope
        self.update()

    def paintEvent(self, event):
        """ Paint the plot in the style of an LCD """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Background gradient
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor("#321212"))
        gradient.setColorAt(0.3, QColor("#331111"))
        gradient.setColorAt(0.5, QColor("#551100"))
        gradient.setColorAt(0.7, QColor("#331111"))
        gradient.setColorAt(1.0, QColor("#111111"))
        painter.setBrush(gradient)
        painter.setPen(QPen(QColor("#000000"), 0))
        painter.drawRect(0, 0, self.width(), self.height())

        # Orange drawing pen
        pen = QPen(QColor("orange"))
        pen.setWidth(2)
        axis_pen = QPen(QColor("white"))
        painter.setRenderHint(QPainter.Antialiasing, False)
        painter.setPen(pen)
        painter.setFont(QFont("Consolas", 10))

        # Envelope parameters
        attack_time = self.envelope["attack_time"] / 1000.0
        decay_time = self.envelope["decay_time"] / 1000.0
        release_time = self.envelope["release_time"] / 1000.0
        sustain_level = self.envelope["sustain_level"]
        peak_level = self.envelope["peak_level"]
        initial_level = self.envelope["initial_level"]

        attack_samples = int(attack_time * self.sample_rate)
        decay_samples = int(decay_time * self.sample_rate)
        sustain_samples = int(self.sample_rate * 2)
        release_samples = int(release_time * self.sample_rate)

        attack = np.linspace(initial_level, peak_level, attack_samples, endpoint=False)
        decay = np.linspace(peak_level, peak_level, decay_samples, endpoint=False)
        sustain = np.full(sustain_samples, peak_level)
        release = np.linspace(peak_level, 0, release_samples)
        envelope = np.concatenate([attack, decay, sustain, release])
        total_samples = len(envelope)
        total_time = 5  # seconds

        # Plot area dimensions
        w = self.width()
        h = self.height()
        top_padding = 50
        bottom_padding = 80
        left_padding = 80
        right_padding = 50
        plot_w = w - left_padding - right_padding
        plot_h = h - top_padding - bottom_padding

        # Y range
        y_min = -0.6
        y_max = 0.6

        # Draw axes
        painter.setPen(axis_pen)
        painter.drawLine(left_padding, top_padding, left_padding, top_padding + plot_h)  # Y-axis

        zero_y = top_padding + (y_max / (y_max - y_min)) * plot_h
        painter.drawLine(left_padding, zero_y, left_padding + plot_w, zero_y)  # X-axis at Y=0

        # X-axis labels
        painter.drawText(left_padding, zero_y + 20, "0")
        painter.drawText(left_padding + plot_w - 10, zero_y + 20, "5")
        for i in range(1, 5):
            x = left_padding + i * plot_w / 5
            painter.drawLine(x, zero_y - 5, x, zero_y + 5)
            painter.drawText(x - 10, zero_y + 20, f"{i}")

        # Y-axis ticks and labels from +0.6 to -0.6
        for i in range(-3, 4):
            y_val = i * 0.2
            y = top_padding + ((y_max - y_val) / (y_max - y_min)) * plot_h
            painter.drawLine(left_padding - 5, y, left_padding, y)
            painter.drawText(left_padding - 40, y + 5, f"{y_val:.1f}")

        # Draw top title
        painter.setPen(QPen(QColor("orange")))
        painter.setFont(QFont("Consolas", 12))
        painter.drawText(left_padding + plot_w / 2 - 40, top_padding / 2, "Pitch Envelope")

        # Draw X-axis label
        painter.setPen(QPen(QColor("white")))
        painter.drawText(left_padding + plot_w / 2 - 10, top_padding + plot_h + 35, "Time (s)")

        # Y-axis label rotated
        painter.save()
        painter.translate(left_padding - 50, top_padding + plot_h / 2 + 25)
        painter.rotate(-90)
        painter.drawText(0, 0, "Pitch")
        painter.restore()

        # Background grid
        pen = QPen(Qt.GlobalColor.darkGray, 1)
        pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)
        for i in range(1, 5):
            x = left_padding + i * plot_w / 5
            painter.drawLine(x, top_padding, x, top_padding + plot_h)
        for i in range(1, 4):
            y_val = i * 0.2
            y = top_padding + ((y_max - y_val) / (y_max - y_min)) * plot_h
            painter.drawLine(left_padding, y, left_padding + plot_w, y)
            y_mirror = top_padding + ((y_max + y_val) / (y_max - y_min)) * plot_h
            painter.drawLine(left_padding, y_mirror, left_padding + plot_w, y_mirror)

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

