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
from jdxi_editor.ui.widgets.plot.base import BasePlotWidget, PlotConfig, PlotContext


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
        self.set_dimensions(height, width)
        JDXi.UI.Theme.apply_adsr_plot(self)
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

    def draw_custom_ticks(self, ctx: PlotContext, config: PlotConfig) -> None:
        """Draw custom tick marks for PWMPlot."""
        # X-axis ticks are not shown in PWMPlot (omitted)

        # Y-axis ticks (from -0.2 to 1.0 in 0.2 steps)
        y_tick_values = [i * 0.2 for i in range(-1, 6)]
        y_tick_labels = [f"{y:.1f}" for y in y_tick_values]
        self.draw_y_axis_ticks(
            ctx,
            tick_values=y_tick_values,
            tick_labels=y_tick_labels,
            tick_length=5,
            label_offset=45,
            zero_at_bottom=False,
            config=config,
        )

    def draw_grid_hook(self, ctx: PlotContext, config: PlotConfig) -> None:
        """Draw grid for PWMPlot with custom Y callback."""

        def y_callback(y_val):
            return ctx.value_to_y(y_val, zero_at_bottom=False)

        self.draw_grid_ctx(
            ctx,
            num_vertical_lines=6,
            num_horizontal_lines=5,
            zero_at_bottom=False,
            y_callback=y_callback,
            config=config,
        )

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

    def get_plot_config(self) -> PlotConfig:
        """Get plot configuration with PWMPlot-specific settings."""
        return PlotConfig(
            top_padding=50,
            bottom_padding=50,
            left_padding=80,
            right_padding=50,
        )

    def get_y_range(self) -> tuple[float, float]:
        """Get Y range for PWMPlot (-0.2 to 1.2)."""
        return 1.2, -0.2

    def zero_at_bottom(self) -> bool:
        """PWMPlot does not have zero at bottom (uses y_max/y_min scaling)."""
        return False

    def get_title(self) -> str:
        """Get plot title."""
        return "Pulse Width Modulation"

    def get_x_label(self) -> str:
        """Get X-axis label."""
        return "Time (s)"

    def get_y_label(self) -> str:
        """Get Y-axis label."""
        return "Voltage (V)"

    def draw_data(self, ctx: PlotContext, config: PlotConfig) -> None:
        """Draw PWMPlot envelope data."""
        if not self.enabled:
            return

        envelope, _, total_time = self.envelope_parameters()

        # Draw curve using new helper method
        self.draw_curve_from_array(
            ctx,
            y_values=envelope,
            x_max=total_time,
            sample_rate=self.sample_rate,
            max_points=500,
            zero_at_bottom=False,
            config=config,
        )
