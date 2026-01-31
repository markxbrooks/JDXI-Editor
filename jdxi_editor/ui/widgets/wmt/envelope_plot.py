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
from picomidi.constant import Midi
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.ui.widgets.plot.base import BasePlotWidget, PlotConfig, PlotContext


def midi_value_to_float(value: int) -> float:
    """
    Convert MIDI value (0-127) to a float in the range [0.0, 1.0].

    :param value: int
    :return: float in range [0.0, 1.0]
    """
    return max(0.0, min(1.0, value / Midi.VALUE.MAX.SEVEN_BIT))


class WMTEnvPlot(BasePlotWidget):
    """
    A QWidget-based plot for displaying envelope curves,
    supporting both a modern velocity-style plot and
    a vintage LCD-style pitch envelope plot.
    """

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

    def envelope_parameters(self):
        """Generate WMT envelope from parameters."""
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
        return envelope, total_samples, total_time

    def get_plot_config(self) -> PlotConfig:
        """Get plot configuration with WMT-specific settings."""
        return PlotConfig(
            top_padding=50,
            bottom_padding=80,
            left_padding=80,
            right_padding=50,
        )

    def get_y_range(self) -> tuple[float, float]:
        """Get Y range for WMT plot (-0.6 to 0.6)."""
        return 0.6, -0.6

    def zero_at_bottom(self) -> bool:
        """WMT plot does not have zero at bottom (uses y_max/y_min scaling)."""
        return False

    def get_title(self) -> str:
        """Get plot title."""
        return "WMT Envelope"

    def get_x_label(self) -> str:
        """Get X-axis label."""
        return "Time (s)"

    def get_y_label(self) -> str:
        """Get Y-axis label."""
        return "Pitch"

    def draw_custom_ticks(self, ctx: PlotContext, config: PlotConfig) -> None:
        """Draw custom tick marks for WMT plot."""
        _, _, total_time = self.envelope_parameters()

        # X-axis ticks (time: 0, 2, 4, 6, 8, 10)
        num_ticks = 6
        x_tick_values = [(i / num_ticks) * total_time for i in range(num_ticks + 1)]
        x_tick_labels = [f"{t:.0f}" for t in x_tick_values]
        self.draw_x_axis_ticks(
            ctx,
            tick_values=x_tick_values,
            tick_labels=x_tick_labels,
            tick_length=5,
            label_offset=20,
            position="zero",
            x_max=total_time,
            config=config,
        )

        # Y-axis ticks (from -0.6 to 0.6 in 0.2 steps)
        y_tick_values = [i * 0.2 for i in range(-3, 4)]
        y_tick_labels = [f"{y:.1f}" for y in y_tick_values]
        self.draw_y_axis_ticks(
            ctx,
            tick_values=y_tick_values,
            tick_labels=y_tick_labels,
            tick_length=5,
            label_offset=40,
            zero_at_bottom=False,
            config=config,
        )

    def draw_grid_hook(self, ctx: PlotContext, config: PlotConfig) -> None:
        """Draw grid for WMT plot with symmetric grid lines."""
        _, _, total_time = self.envelope_parameters()

        # Custom grid: vertical lines at tick positions, horizontal lines symmetric around zero
        num_ticks = 6
        x_ticks = [(i / num_ticks) * total_time for i in range(1, num_ticks + 1)]
        
        # Horizontal grid lines: symmetric around zero (positive and negative)
        y_ticks = []
        for i in range(1, 4):
            y_ticks.append(i * 0.2)  # Positive
            y_ticks.append(-i * 0.2)  # Negative

        self.draw_grid_ctx(
            ctx,
            x_ticks=x_ticks,
            y_ticks=y_ticks,
            x_max=total_time,
            zero_at_bottom=False,
            config=config,
        )

    def draw_data(self, ctx: PlotContext, config: PlotConfig) -> None:
        """Draw WMT envelope data."""
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
