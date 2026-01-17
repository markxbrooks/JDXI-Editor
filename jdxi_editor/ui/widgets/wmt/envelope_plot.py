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
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget

from jdxi_editor.ui.style import JDXiStyle
from picomidi.constant import Midi


def midi_value_to_float(value: int) -> float:
    """
    Convert MIDI value (0-127) to a float in the range [0.0, 1.0].

    :param value: int
    :return: float in range [0.0, 1.0]
    """
    return max(0.0, min(1.0, value / Midi.VALUE.MAX.SEVEN_BIT))


class WMTEnvPlot(QWidget):
    """
    A QWidget-based plot for displaying envelope curves,
    supporting both a modern velocity-style plot and
    a vintage LCD-style pitch envelope plot.
    """

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
        from jdxi_editor.ui.style.theme_manager import JDXiThemeManager

        JDXiThemeManager.apply_adsr_plot(self)
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

    def setEnabled(self, enabled):
        super().setEnabled(enabled)  # Ensure QWidget's default behavior is applied
        self.enabled = enabled

    def set_values(self, envelope: dict) -> None:
        """
        Update the envelope values and refresh the plot.

        :param envelope: dict
        :return: None
        """
        self.envelope = envelope
        self.update()

    def paintEvent(self, event):
        """Paint the plot in the style of an LCD"""
        painter = QPainter(self)
        try:
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
            painter.setFont(QFont("JD LCD Rounded", 10))

            # Envelope parameters
            fade_lower = max(
                self.envelope["fade_lower"] / 1000.0, 1.0
            )  # Fade lower in seconds
            range_lower = max(self.envelope["range_lower"] / 1000.0, 1.0)
            depth = self.envelope["depth"] / 2.0  # Depth in range [0.0, 0.5]

            range_upper = max(self.envelope["range_upper"] / 2000.0, 0.1)
            fade_upper = max(self.envelope["fade_upper"] / 2000.0, 0.5)
            sustain = 2.0  # Sustain in seconds

            fade_lower_period = range_lower - fade_lower
            fade_upper_period = fade_upper - range_upper

            fade_lower_samples = max(int(fade_lower * self.sample_rate), 1)
            fade_lower_period_samples = max(
                int(fade_lower_period * self.sample_rate), 1
            )
            fade_upper_samples = max(int(fade_upper * self.sample_rate), 1)
            initial_level = 0.0

            upper_fade = np.linspace(
                depth, initial_level, fade_upper_samples, endpoint=False
            )
            sustain_samples = int(
                self.sample_rate * (sustain + range_upper)
            )  # Sustain for 2 seconds
            sustain = np.full(sustain_samples, depth)
            baseline = np.full(fade_lower_samples, initial_level)
            lower_fade = np.linspace(
                initial_level, depth, fade_lower_period_samples, endpoint=False
            )
            envelope = np.concatenate([baseline, lower_fade, sustain, upper_fade])
            total_samples = len(envelope)
            total_time = 10  # seconds

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
            painter.drawLine(
                left_padding, top_padding, left_padding, top_padding + plot_h
            )  # Y-axis

            zero_y = top_padding + (y_max / (y_max - y_min)) * plot_h
            painter.drawLine(
                left_padding, zero_y, left_padding + plot_w, zero_y
            )  # X-axis at Y=0

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

            # Y-axis ticks and labels from +0.6 to -0.6
            for i in range(-3, 4):
                y_val = i * 0.2
                y = top_padding + ((y_max - y_val) / (y_max - y_min)) * plot_h
                painter.drawLine(left_padding - 5, y, left_padding, y)
                painter.drawText(left_padding - 40, y + 5, f"{y_val:.1f}")

            # Draw top title
            painter.setPen(QPen(QColor("orange")))
            painter.setFont(QFont("JD LCD Rounded", 16))
            painter.drawText(
                left_padding + plot_w / 2 - 40, top_padding / 2, "WMT Envelope"
            )

            # Draw X-axis label
            painter.setPen(QPen(QColor("white")))
            painter.drawText(
                left_padding + plot_w / 2 - 10, top_padding + plot_h + 35, "Time (s)"
            )

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
            for i in range(1, 7):
                x = left_padding + i * plot_w / 6
                painter.drawLine(x, top_padding, x, top_padding + plot_h)
            for i in range(1, 4):
                y_val = i * 0.2
                y = top_padding + ((y_max - y_val) / (y_max - y_min)) * plot_h
                painter.drawLine(left_padding, y, left_padding + plot_w, y)
                y_mirror = top_padding + ((y_max + y_val) / (y_max - y_min)) * plot_h
                painter.drawLine(
                    left_padding, y_mirror, left_padding + plot_w, y_mirror
                )

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

                # Draw debug points
                # if self.debug:
                #    painter.setPen(QPen(QColor(255, 0, 0), 4))
                #    for x, y in screen_points:
                #        painter.drawEllipse(int(x) - 2, int(y) - 2, 4, 4)
        finally:
            painter.end()


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication([])

    test_env = {
        "fade_lower": 200,
        "range_lower": 300,
        "depth": 0.7,
        "range_upper": 400,
        "fade_upper": 300,
    }

    plot = WMTEnvPlot(400, 200, test_env)
    plot.setStyleSheet("background-color: black;")
    plot.show()

    app.exec()
