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
from PySide6.QtCore import Qt, QPointF
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPainterPath, QLinearGradient, QColor, QPen, QFont, QBrush

from jdxi_editor.jdxi.midi.constant import JDXiConstant
from jdxi_editor.jdxi.style import JDXiStyle


def generate_filter_plot(width: float,
                         slope: float,
                         sample_rate: int,
                         duration: float) -> np.ndarray:
    """Generates a filter envelope with a sustain plateau followed by a slope down to zero."""
    width = max(0.0, min(1.0, width))  # Clip to valid range
    total_samples = int(duration * sample_rate)
    slope_gradient = 0.5 - (slope * 0.25)
    print(f"slope: \t{slope}")
    print(f"slope_gradient: \t{slope_gradient}")
    # Define segments in samples
    period = max(1, sample_rate)  # Avoid divide-by-zero
    sustain_samples = int(period * width)
    slope_samples = int(period * slope_gradient)

    # At least 1 sample high or slope to avoid weird signals
    sustain_samples = max(1, sustain_samples)
    slope_samples = max(1, slope_samples)

    # Create the sustain plateau first
    sustain = np.full(sustain_samples, JDXiConstant.FILTER_PLOT_DEPTH, dtype=np.float32)

    # Now create slope descending to zero
    slope_vals = np.linspace(
        JDXiConstant.FILTER_PLOT_DEPTH, 0, slope_samples, endpoint=False, dtype=np.float32
    )

    # Combine together
    envelope = np.concatenate([sustain, slope_vals], axis=0)

    # Trim or pad to match total_samples
    if envelope.size > total_samples:
        envelope = envelope[:total_samples]
    elif envelope.size < total_samples:
        padding = np.zeros(total_samples - envelope.size, dtype=np.float32)
        envelope = np.concatenate([envelope, padding], axis=0)

    return envelope


class AnalogFilterPlot(QWidget):
    def __init__(
            self,
            width: int = JDXiStyle.ADSR_PLOT_WIDTH,
            height: int = JDXiStyle.ADSR_PLOT_HEIGHT,
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
        self.setStyleSheet(JDXiStyle.ADSR_PLOT)
        # Sample rate for converting times to samples
        self.sample_rate = 256
        self.setMinimumHeight(JDXiStyle.ADSR_PLOT_HEIGHT)
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

            # === Background ===
            gradient = QLinearGradient(0, 0, self.width(), self.height())
            gradient.setColorAt(0.0, QColor("#321212"))
            gradient.setColorAt(0.3, QColor("#331111"))
            gradient.setColorAt(0.5, QColor("#551100"))
            gradient.setColorAt(0.7, QColor("#331111"))
            gradient.setColorAt(1.0, QColor("#111111"))
            painter.setBrush(gradient)
            painter.setPen(QPen(QColor("#000000"), 0))
            painter.drawRect(0, 0, self.width(), self.height())

            # === Pens & Fonts ===
            orange_pen = QPen(QColor("orange"), 2)
            axis_pen = QPen(QColor("white"))
            grid_pen = QPen(Qt.GlobalColor.darkGray, 1, Qt.PenStyle.DashLine)
            painter.setFont(QFont("JD LCD Rounded", 10))
            font_metrics = painter.fontMetrics()

            # === Envelope Parameters ===
            # Pulse width envelope: rise and fall
            envelope = generate_filter_plot(width=self.envelope["cutoff_param"],
                                            slope=self.envelope["slope_param"],
                                            sample_rate=self.sample_rate,
                                            duration=self.envelope.get("duration", 1.0))
            total_samples = len(envelope)
            total_time = total_samples / self.sample_rate

            # === Plot Layout ===
            w, h = self.width(), self.height()
            top_pad, bottom_pad = 50, 50
            left_pad, right_pad = 80, 50
            plot_w = w - left_pad - right_pad
            plot_h = h - top_pad - bottom_pad

            y_min, y_max = -0.2, 1.2
            zero_y = top_pad + (y_max / (y_max - y_min)) * plot_h

            # === Axes ===
            painter.setPen(axis_pen)
            # Y-axis
            painter.drawLine(left_pad, top_pad, left_pad, top_pad + plot_h)
            # X-axis
            painter.drawLine(left_pad, zero_y, left_pad + plot_w, zero_y)

            # === X-axis Labels & Ticks ===
            num_ticks = 6
            for i in range(num_ticks + 1):
                x = left_pad + i * plot_w / num_ticks

            # === Y-axis Labels & Ticks ===
            for i in range(-1, 6):
                y_val = i * 0.2
                y = top_pad + ((y_max - y_val) / (y_max - y_min)) * plot_h
                painter.drawLine(left_pad - 5, y, left_pad, y)
                label = f"{y_val:.1f}"
                label_width = font_metrics.horizontalAdvance(label)
                painter.drawText(left_pad - 10 - label_width, y + font_metrics.ascent() / 2, label)

            # === Title ===
            painter.setPen(QPen(QColor("orange")))
            painter.setFont(QFont("JD LCD Rounded", 16))
            title = "Filter Cutoff"
            title_width = painter.fontMetrics().horizontalAdvance(title)
            painter.drawText(left_pad + (plot_w - title_width) / 2, top_pad / 2, title)

            # === X-axis Label ===
            painter.setPen(QPen(QColor("white")))
            painter.setFont(QFont("JD LCD Rounded", 10))
            x_label = "Frequency (Hz)"
            x_label_width = font_metrics.horizontalAdvance(x_label)
            painter.drawText(left_pad + (plot_w - x_label_width) / 2, top_pad + plot_h + 35, x_label)

            # === Y-axis Label (rotated) ===
            painter.save()
            y_label = "Voltage (V)"
            y_label_width = font_metrics.horizontalAdvance(y_label)
            painter.translate(left_pad - 50, top_pad + plot_h / 2 + y_label_width / 2)
            painter.rotate(-90)
            painter.drawText(0, 0, y_label)
            painter.restore()

            # === Grid Lines ===
            painter.setPen(grid_pen)
            for i in range(1, 7):
                x = left_pad + i * plot_w / 6
                painter.drawLine(x, top_pad, x, top_pad + plot_h)
            for i in range(1, 6):
                y_val = i * 0.2
                y = top_pad + ((y_max - y_val) / (y_max - y_min)) * plot_h
                y_mirror = top_pad + ((y_max + y_val) / (y_max - y_min)) * plot_h
                painter.drawLine(left_pad, y, left_pad + plot_w, y)
                # painter.drawLine(left_pad, y_mirror, left_pad + plot_w, y_mirror)

            # === Envelope Plot ===
            if self.enabled:
                painter.setPen(orange_pen)
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

                if points and self.enabled:
                    path = QPainterPath()
                    path.moveTo(points[0])
                    for pt in points[1:]:
                        path.lineTo(pt)  # For smoothing: use cubicTo
                    painter.drawPath(path)

                    # Now fill in to axes
                    path.lineTo(left_pad + plot_w, zero_y)
                    path.lineTo(left_pad, zero_y)
                    path.closeSubpath()

                    # Fill the path black first
                    painter.fillPath(path, gradient)
                    # redraw x-axis
                    painter.setPen(axis_pen)
                    painter.drawLine(left_pad, zero_y, left_pad + plot_w, zero_y)
                    # === X-axis Labels & Ticks ===
                    num_ticks = 6
                    for i in range(num_ticks + 1):
                        x = left_pad + i * plot_w / num_ticks

        finally:
            painter.end()
