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
from decologr import Decologr as log
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

from jdxi_editor.jdxi.style import JDXiStyle


class ADSRPlot(QWidget):
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
        from jdxi_editor.jdxi.style.theme_manager import JDXiThemeManager

        JDXiThemeManager.apply_adsr_plot(self)
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
        """Paint the ADSR plot.
        :param event: QPaintEvent
        """
        with QPainter(self) as painter:
            # Draw background gradient
            gradient = QLinearGradient(0, 0, self.width(), self.height())
            gradient.setColorAt(0.0, QColor("#321212"))  # Darker edges
            gradient.setColorAt(0.3, QColor("#331111"))  # Gray transition
            gradient.setColorAt(0.5, QColor("#551100"))  # Orange glow center
            gradient.setColorAt(0.7, QColor("#331111"))  # Gray transition
            gradient.setColorAt(1.0, QColor("#111111"))  # Darker edges
            painter.setBrush(gradient)
            painter.setPen(QPen(QColor("#000000"), 0))  # no border
            painter.drawRect(0, 0, self.width(), self.height())

            # Use orange for drawing
            pen = QPen(QColor("orange"))
            axis_pen = QPen(QColor("white"))
            pen.setWidth(2)
            painter.setPen(QPen(Qt.PenStyle.SolidLine))
            painter.setPen(pen)
            painter.setFont(QFont("JD LCD Rounded", 10))

            # Compute envelope segments in seconds
            attack_time = self.envelope["attack_time"] / 1000.0
            decay_time = self.envelope["decay_time"] / 1000.0
            release_time = self.envelope["release_time"] / 1000.0
            sustain_level = self.envelope["sustain_level"]
            peak_level = max(self.envelope["peak_level"] * 2, 0)
            log.message(f"peak_level: {peak_level}")
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

            # envelope = np.concatenate([attack, decay, sustain, release])
            total_samples = len(envelope)
            total_time = 5  # in seconds

            # Prepare points for drawing
            w = self.width()
            h = self.height()
            top_padding = 50  # Custom top padding value
            right_padding = 50  # Custom right padding value
            bottom_padding = 80  # Bottom padding remains the same
            left_padding = 80  # Left padding remains the same

            plot_w = w - left_padding - right_padding
            plot_h = h - top_padding - bottom_padding

            # Optionally draw axis lines and labels
            painter.setPen(axis_pen)
            painter.drawLine(
                left_padding, top_padding, left_padding, top_padding + plot_h
            )  # Y-axis
            painter.drawLine(
                left_padding,
                top_padding + plot_h,
                left_padding + plot_w,
                top_padding + plot_h,
            )  # X-axis
            painter.drawText(left_padding, top_padding + plot_h + 20, "0")
            painter.drawText(left_padding + plot_w - 10, top_padding + plot_h + 20, "5")
            for i in range(1, 5):
                x = left_padding + i * plot_w / 5
                painter.drawLine(x, top_padding + plot_h, x, top_padding + plot_h + 5)
                painter.drawText(x - 10, top_padding + plot_h + 20, f"{i}")
            for i in range(1, 5):
                y = top_padding + i * plot_h / 5
                painter.drawLine(left_padding, y, left_padding - 5, y)
                painter.drawText(left_padding - 35, y + 5, f"{1 - i * 0.2:.1f}")
            painter.drawText(left_padding - 35, top_padding + 5, "1")
            painter.drawText(left_padding - 35, top_padding + plot_h, "0")

            # Draw the envelope label at the top center of the widget
            painter.setPen(QPen(QColor("orange")))
            painter.setFont(QFont("JD LCD Rounded", 16))
            painter.drawText(
                left_padding + plot_w / 2 - 40, top_padding / 2, "ADSR Envelope"
            )  # half way up top padding

            # Write legend label for x-axis at the bottom center of the widget
            painter.setPen(QPen(QColor("white")))
            painter.setFont(QFont("JD LCD Rounded", 16))
            painter.drawText(
                left_padding + plot_w / 2 - 10, top_padding + plot_h + 35, "Time (s)"
            )

            # Draw y-axis label rotated 90 degrees
            painter.save()
            painter.translate(left_padding - 50, top_padding + plot_h / 2 + 25)
            painter.rotate(-90)
            painter.drawText(0, 0, "Amplitude")
            painter.restore()

            # Draw background grid as dashed dark gray lines
            pen = QPen(Qt.GlobalColor.darkGray, 2)
            pen.setStyle(Qt.PenStyle.DashLine)
            pen.setWidth(1)
            painter.setPen(pen)
            for i in range(1, 5):
                x = left_padding + i * plot_w / 5
                painter.drawLine(x, top_padding, x, top_padding + plot_h)
            for i in range(1, 5):
                y = top_padding + i * plot_h / 5
                painter.drawLine(left_padding, y, left_padding + plot_w, y)

            if self.enabled:
                # Draw the envelope polyline last, on top of the grid
                # Create a list of points for the envelope polyline.
                painter.setPen(QPen(QColor("orange")))
                points = []
                num_points = 500
                indices = np.linspace(0, total_samples - 1, num_points).astype(int)
                for i in indices:
                    t = i / self.sample_rate  # time in seconds
                    x = left_padding + (t / total_time) * plot_w
                    y = top_padding + plot_h - (envelope[i] * plot_h)
                    points.append((x, y))

                # Draw the envelope polyline
                if points:
                    path = QPainterPath()
                    path.moveTo(*points[0])
                    for pt in points[1:]:
                        path.lineTo(*pt)
                    painter.drawPath(path)
