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
from PySide6.QtGui import (
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
)
from PySide6.QtWidgets import QWidget

from jdxi_editor.core.jdxi import JDXi


def generate_filter_plot(
    width: float,
    slope: float,
    sample_rate: int,
    duration: float,
    filter_mode: str = "lpf",
) -> np.ndarray:
    """
    Generates a filter frequency response plot based on filter mode.

    :param width: Cutoff frequency position (0.0-1.0)
    :param slope: Filter slope (0.0-1.0)
    :param sample_rate: Sample rate for the plot
    :param duration: Duration of the plot
    :param filter_mode: Filter mode - "lpf", "hpf", "bpf", "bypass"
    :return: numpy array representing the frequency response
    """
    width = max(0.0, min(1.0, width))  # Clip to valid range
    total_samples = int(duration * sample_rate)

    # Normalize filter_mode to lowercase
    filter_mode = filter_mode.lower() if filter_mode else "lpf"

    if filter_mode == "bypass":
        # Bypass: flat line at full amplitude
        envelope = np.full(
            total_samples, JDXi.UI.Constants.FILTER_PLOT_DEPTH, dtype=np.float32
        )
        return envelope

    # Calculate slope steepness based on slope parameter
    slope_gradient = 0.5 - (slope * 0.25)

    # Define segments in samples
    period = max(1, sample_rate)  # Avoid divide-by-zero
    cutoff_samples = int(period * width)
    transition_samples = int(period * slope_gradient)

    # At least 1 sample to avoid weird signals
    cutoff_samples = max(1, cutoff_samples)
    transition_samples = max(1, transition_samples)

    if filter_mode == "lpf":
        # Low-pass filter: full amplitude up to cutoff, then rolloff
        # Create the passband (full amplitude up to cutoff)
        passband = np.full(
            cutoff_samples, JDXi.UI.Constants.FILTER_PLOT_DEPTH, dtype=np.float32
        )

        # Create transition rolloff
        rolloff = np.linspace(
            JDXi.UI.Constants.FILTER_PLOT_DEPTH,
            0,
            transition_samples,
            endpoint=False,
            dtype=np.float32,
        )

        # Combine together
        envelope = np.concatenate([passband, rolloff], axis=0)

    elif filter_mode == "hpf":
        # High-pass filter: rolloff up to cutoff, then full amplitude
        # Create transition rolloff from 0 to cutoff
        rolloff = np.linspace(
            0,
            JDXi.UI.Constants.FILTER_PLOT_DEPTH,
            cutoff_samples,
            endpoint=False,
            dtype=np.float32,
        )

        # Create the passband (full amplitude after cutoff)
        passband = np.full(
            transition_samples, JDXi.UI.Constants.FILTER_PLOT_DEPTH, dtype=np.float32
        )

        # Combine together
        envelope = np.concatenate([rolloff, passband], axis=0)

    elif filter_mode == "bpf":
        # Band-pass filter: rolloff, passband, rolloff
        # Low rolloff (before passband)
        low_rolloff_samples = int(cutoff_samples * 0.3)
        low_rolloff = np.linspace(
            0,
            JDXi.UI.Constants.FILTER_PLOT_DEPTH,
            low_rolloff_samples,
            endpoint=False,
            dtype=np.float32,
        )

        # Passband (middle section)
        passband_samples = int(cutoff_samples * 0.4)
        passband = np.full(
            passband_samples, JDXi.UI.Constants.FILTER_PLOT_DEPTH, dtype=np.float32
        )

        # High rolloff (after passband)
        high_rolloff_samples = int(transition_samples * 0.5)
        high_rolloff = np.linspace(
            JDXi.UI.Constants.FILTER_PLOT_DEPTH,
            0,
            high_rolloff_samples,
            endpoint=False,
            dtype=np.float32,
        )

        # Combine together
        envelope = np.concatenate([low_rolloff, passband, high_rolloff], axis=0)

    else:
        # Default to LPF if unknown mode
        passband = np.full(
            cutoff_samples, JDXi.UI.Constants.FILTER_PLOT_DEPTH, dtype=np.float32
        )
        rolloff = np.linspace(
            JDXi.UI.Constants.FILTER_PLOT_DEPTH,
            0,
            transition_samples,
            endpoint=False,
            dtype=np.float32,
        )
        envelope = np.concatenate([passband, rolloff], axis=0)

    # Trim or pad to match total_samples
    if envelope.size > total_samples:
        envelope = envelope[:total_samples]
    elif envelope.size < total_samples:
        padding = np.zeros(total_samples - envelope.size, dtype=np.float32)
        envelope = np.concatenate([envelope, padding], axis=0)

    return envelope


class FilterPlot(QWidget):
    def __init__(
        self,
        width: int = JDXi.UI.Style.ADSR_PLOT_WIDTH,
        height: int = JDXi.UI.Style.ADSR_PLOT_HEIGHT,
        envelope: dict = None,
        parent: QWidget = None,
        filter_mode: str = "lpf",
    ):
        super().__init__(parent)
        self.point_moved = None
        self.parent = parent
        # Default envelope parameters (times in ms)
        self.enabled = True
        self.envelope = envelope
        self.filter_mode = filter_mode  # Store filter mode
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

    def set_filter_mode(self, filter_mode: str) -> None:
        """
        Update filter mode and trigger redraw

        :param filter_mode: str - Filter mode ("lpf", "hpf", "bpf", "bypass")
        :return: None
        """
        self.filter_mode = filter_mode.lower() if filter_mode else "lpf"
        self.update()

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
            # Generate filter frequency response based on filter mode
            envelope = generate_filter_plot(
                width=self.envelope["cutoff_param"],
                slope=self.envelope["slope_param"],
                sample_rate=self.sample_rate,
                duration=self.envelope.get("duration", 1.0),
                filter_mode=self.filter_mode,
            )
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
                painter.drawText(
                    left_pad - 10 - label_width, y + font_metrics.ascent() / 2, label
                )
            # === Title ===
            painter.setPen(QPen(QColor("orange")))
            painter.setFont(QFont("JD LCD Rounded", 16))
            # Update title based on filter mode
            filter_mode_upper = self.filter_mode.upper() if self.filter_mode else "LPF"
            if filter_mode_upper == "BYPASS":
                title = "Filter Bypass"
            elif filter_mode_upper == "HPF":
                title = "HPF Cutoff"
            elif filter_mode_upper == "BPF":
                title = "BPF Cutoff"
            else:
                title = "LPF Cutoff"
            title_width = painter.fontMetrics().horizontalAdvance(title)
            painter.drawText(left_pad + (plot_w - title_width) / 2, top_pad / 2, title)

            # === X-axis Label ===
            painter.setPen(QPen(QColor("white")))
            painter.setFont(QFont("JD LCD Rounded", 10))
            x_label = "Frequency (Hz)"
            x_label_width = font_metrics.horizontalAdvance(x_label)
            painter.drawText(
                left_pad + (plot_w - x_label_width) / 2, top_pad + plot_h + 35, x_label
            )

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
                samples_per_pixel = max(1, int(total_samples / plot_w))

                # --- Build fill path (upper envelope only) ---
                fill_path = QPainterPath()
                first_point = True

                for px in range(int(plot_w)):
                    start = px * samples_per_pixel
                    end = min(start + samples_per_pixel, total_samples)
                    if start >= end:
                        continue

                    ymax = max(envelope[start:end])

                    x = left_pad + px
                    y = top_pad + ((y_max - ymax) / (y_max - y_min)) * plot_h

                    if first_point:
                        fill_path.moveTo(x, y)
                        first_point = False
                    else:
                        fill_path.lineTo(x, y)

                # Close path to zero line
                fill_path.lineTo(left_pad + plot_w, zero_y)
                fill_path.lineTo(left_pad, zero_y)
                fill_path.closeSubpath()

                # --- Fill under curve (subtle LCD style) ---
                fill_gradient = QLinearGradient(0, top_pad, 0, top_pad + plot_h)
                fill_gradient.setColorAt(0.0, QColor(255, 160, 40, 60))
                fill_gradient.setColorAt(1.0, QColor(255, 160, 40, 10))

                painter.fillPath(fill_path, fill_gradient)

                # --- Draw envelope strokes on top ---
                pen = QPen(QColor("orange"), 1)
                pen.setCapStyle(Qt.FlatCap)
                pen.setCosmetic(True)
                painter.setPen(pen)

                for px in range(int(plot_w)):
                    start = px * samples_per_pixel
                    end = min(start + samples_per_pixel, total_samples)
                    if start >= end:
                        continue

                    segment = envelope[start:end]
                    ymin = min(segment)
                    ymax = max(segment)

                    x = left_pad + px
                    y1 = top_pad + ((y_max - ymax) / (y_max - y_min)) * plot_h
                    y2 = top_pad + ((y_max - ymin) / (y_max - y_min)) * plot_h

                    painter.drawLine(QPointF(x, y1), QPointF(x, y2))

        finally:
            painter.end()
